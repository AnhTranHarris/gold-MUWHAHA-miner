"""Build a clean standalone demo/Strategy Tester EA from immutable v2.06 and 88 packed models.
No training, market history, third-party libraries or compile-time resource files.
Python 3.11+ standard library; native compiler certification remains separate.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, re, struct, tempfile, zipfile, zlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

PARENT = '699da4f68239b8029a9e61e272e650f90c365de5'
EA = 'MQL5/Experts/HybridGateV1/GoldMuwahahaMiner_HybridGateV1.mq5'
ENG = 'engineering/hybridgate_v1/'
WIDTHS = (2, 1, 4, 4, 8, 8)
COUNT = 88
MAX = 67108864
CHUNK = 8192 # chars, divisible by four, below MQL5 literal limit
ZIP_SHA = '076c12a01b7f17561438186521156f009aeff379306e6747e3343f61be2c1ec0'
BUILD_ID = 'HG8-monolith-699da4f68239b8029a9e61e272e650f90c365de5-v1'

LOADER = r'''
// Single-source model payload codec. Byte-plane permutation is reversible; no numeric conversion.
#define HG8_BUILD_ID "HG8-monolith-699da4f68239b8029a9e61e272e650f90c365de5-v1"
uint HG8U32(const uchar &b[],const int p){
 uint v=0;for(int k=0;k<4;k++)v|=((uint)b[p+k])<<(8*k);return v;
}
bool HG8RestorePacked(const uchar &x[],const int raw_len,uchar &out[]){
 ArrayFree(out);int len=ArraySize(x);
 if(len!=raw_len||len<32||len>67108864||x[0]!=72||x[1]!=71||x[2]!=53||x[3]!=80||HG8U32(x,4)!=1)return false;
 uint trees=HG8U32(x,16);if(trees<1||trees>100000||32+(long)trees*4>len)return false;
 int nt=(int)trees;long nodes=0;
 for(int t=0;t<nt;t++){uint n=HG8U32(x,32+4*t);if(n>65535)return false;nodes+=(long)n;}
 if(32+(long)nt*12+27*nodes!=len)return false;
 int width[6]={2,1,4,4,8,8};int total[6],base[6],used[6];
 ArrayInitialize(used,0);int start=32+4*nt;
 for(int k=0;k<6;k++){
  total[k]=(int)(nodes+(k==5?nt:0));base[k]=start;start+=total[k]*width[k];
 }
 if(start!=len||ArrayResize(out,len)!=len)return false;
 if(ArrayCopy(out,x,0,0,32)!=32)return false;int pos=32;
 for(int t=0;t<nt;t++){
  int n=(int)HG8U32(x,32+4*t);if(ArrayCopy(out,x,pos,32+4*t,4)!=4)return false;pos+=4;
  for(int k=0;k<6;k++){
   int count=n+(k==5?1:0),w=width[k];
   if(used[k]+count>total[k]||pos+(long)count*w>len)return false;
   for(int b=0;b<w;b++){
    int from=base[k]+b*total[k]+used[k];
    for(int j=0;j<count;j++)out[pos+j*w+b]=x[from+j];
   }
   used[k]+=count;pos+=count*w;
  }
 }
 if(pos!=len)return false;for(int k=0;k<6;k++)if(used[k]!=total[k])return false;
 return true;
}
bool HG8Decode(const string &blocks[],const int packed_len,const int raw_len,const string expected,uchar &out[]){
 ArrayFree(out);if(packed_len<=0||packed_len>67108864||raw_len<32||raw_len>67108864)return false;
 uchar packed[],ascii[],piece[],dummy[],shuffled[],digest[];
 if(ArrayResize(packed,packed_len)!=packed_len)return false;int pos=0;
 for(int i=0;i<ArraySize(blocks);i++){
  int sl=StringLen(blocks[i]);if(sl<=0||sl>8192||sl%4!=0)return false;
  ArrayFree(ascii);ArrayFree(piece);
  if(StringToCharArray(blocks[i],ascii,0,-1,CP_UTF8)!=sl+1||ArrayResize(ascii,sl)!=sl)return false;
  int n=CryptDecode(CRYPT_BASE64,ascii,dummy,piece);
  if(n<=0||ArraySize(piece)!=n||n>packed_len-pos||ArrayCopy(packed,piece,pos,0,n)!=n)return false;pos+=n;
 }
 if(pos!=packed_len)return false;
 ArrayFree(ascii);ArrayFree(piece);
 ResetLastError();int got=CryptDecode(CRYPT_ARCH_ZIP,packed,dummy,shuffled);ArrayFree(packed);
 if(got!=raw_len||ArraySize(shuffled)!=raw_len){PrintFormat("HG8 decompress failed, expected=%d got=%d error=%d",raw_len,got,GetLastError());return false;}
 if(!HG8RestorePacked(shuffled,raw_len,out)){ArrayFree(out);return false;}ArrayFree(shuffled);
 if(CryptEncode(CRYPT_HASH_SHA256,out,dummy,digest)!=32){ArrayFree(out);return false;}
 string hex="";for(int i=0;i<32;i++)hex+=StringFormat("%02x",(uint)digest[i]);
 if(hex!=expected){ArrayFree(out);return false;}
 return true;
}
'''

def require(ok, message):
    if not ok: raise RuntimeError(message)

def sha(b): return hashlib.sha256(b).hexdigest()
def file_sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def once(s,a,b):
    require(s.count(a)==1,'unmatched source anchor: '+a)
    return s.replace(a,b,1)
def array(s,name):
    m=re.search(r'string '+name+r'\[\]=\{([^}]+)\};',s)
    require(m is not None,'missing manifest '+name)
    return json.loads('['+m.group(1)+']')

def shuffle(b):
    require(32<=len(b)<=MAX and b[:8]==b'HG5P\x01\x00\x00\x00','invalid model header')
    nt=struct.unpack_from('<I',b,16)[0]; require(1<=nt<=100000,'invalid tree count')
    p=32;counts=bytearray();fields=[bytearray() for _ in WIDTHS]
    for _ in range(nt):
        require(p+4<=len(b),'truncated count');n=struct.unpack_from('<I',b,p)[0];require(n<=65535,'invalid tree size')
        counts.extend(b[p:p+4]);p+=4
        for i,w in enumerate(WIDTHS):
            k=(n+(i==5))*w;require(p+k<=len(b),'truncated tree field');fields[i].extend(b[p:p+k]);p+=k
    require(p==len(b),'unexpected trailing model bytes')
    return b[:32]+bytes(counts)+b''.join(bytes(f[j::w]) for f,w in zip(fields,WIDTHS) for j in range(w))

def unshuffle(x):
    nt=struct.unpack_from('<I',x,16)[0];counts=struct.unpack_from('<'+'I'*nt,x,32);nodes=sum(counts);p=32+4*nt
    require(len(x)==32+12*nt+27*nodes,'shuffled length')
    fields=[]
    for i,w in enumerate(WIDTHS):
        n=nodes+(nt if i==5 else 0);f=bytearray(n*w)
        for j in range(w): f[j::w]=x[p:p+n];p+=n
        fields.append(f)
    require(p==len(x),'plane length');out=bytearray(x[:32]);used=[0]*6
    for t,n in enumerate(counts):
        out.extend(x[32+4*t:36+4*t])
        for i,w in enumerate(WIDTHS):
            k=(n+(i==5))*w;out.extend(fields[i][used[i]:used[i]+k]);used[i]+=k
    return bytes(out)

def pack_model(task):
    archive,index,name,digest=task
    with zipfile.ZipFile(archive) as z: b=z.read('model_bank/'+name+'.hg5p')
    require(sha(b)==digest,'model bytes mismatch '+name)
    compressed=zlib.compress(shuffle(b),6)
    encoded=base64.b64encode(compressed).decode('ascii')
    blocks=[encoded[i:i+CHUNK] for i in range(0,len(encoded),CHUNK)]
    restored=unshuffle(zlib.decompress(b''.join(base64.b64decode(c,validate=True) for c in blocks)))
    require(restored==b and sha(restored)==digest,'roundtrip mismatch '+name)
    s=f'\n// Model {index}: {name}, original SHA256 {digest}\nbool HG8Model{index:03d}(const string expected,uchar &out[]){{\n string blocks[]={{\n'
    s+=',\n'.join('  "'+c+'"' for c in blocks)+'\n };\n'
    s+=f' return HG8Decode(blocks,{len(compressed)},{len(b)},expected,out);\n}}\n'
    return s, {'index':index,'name':name,'sha256':digest,'raw_bytes':len(b),'compressed_bytes':len(compressed),'chunks':len(blocks),'roundtrip':'PASS'}

def build(root,archive,controller,out,jobs):
    eng=root/ENG
    qc=json.loads((eng/'QC_INSTALL_MANIFEST.json').read_text());native=json.loads((eng/'NATIVE_SOURCE_MANIFEST.json').read_text());pins={**{k:v for k,v in qc.items() if k.startswith('MQL5/Scripts/')},**native};headers={Path(k).name:k for k in pins if k.endswith('.mqh')}
    for name,digest in pins.items(): require(file_sha(root/name)==digest,'source pin mismatch '+name)
    require(len(pins)==39,'source pin count')
    manifest=(root/headers['HG5QCManifest.mqh']).read_text(encoding='utf-8')
    ids,hashes=array(manifest,'HG_ID'),array(manifest,'HG_MODEL_SHA')
    require(len(ids)==len(hashes)==len(set(ids))==COUNT,'model manifest count')
    for name,digest in zip(ids,hashes):require(qc.get('MQL5/Files/HG5QC/'+name+'.hg5p')==digest,'model pin '+name)
    models=list(zip(ids,hashes))
    seen=[];edits={}
    def normalize_types(name,s):
     orig=s
     if name in ('HG5HoldEvents.mqh','HG6ActualHolding.mqh'):
      s=re.sub(r'\bf\[([^\]\n]+)\]=([^;\n]+);',lambda m:'f['+m[1]+']=(float)('+m[2]+');',s)
      s=s.replace('double dt=q[j].ms-q[j-1].ms;','double dt=(double)(q[j].ms-q[j-1].ms);')
      s=s.replace('if(sg&&sign&&sg!=sign)','if(sg!=0&&sign!=0&&sg!=sign)').replace('if(sg)sign=sg;','if(sg!=0)sign=sg;')
      s=s.replace('if(sg&&prevsign&&sg!=prevsign)','if(sg!=0&&prevsign!=0&&sg!=prevsign)').replace('if(sg)prevsign=sg;','if(sg!=0)prevsign=sg;')
     if name=='HG5HoldController.mqh':s=s.replace('if(!why&&(kind&4))','if(why==0&&(kind&4)!=0)')
     if s!=orig:edits[name]={'original_sha256':sha(orig.encode()),'typed_sha256':sha(s.encode())}
     return s
    pat=re.compile(r'^\s*#include\s+"([^"\n]+)"\s*$',re.M)
    def expand(name):
     if name in seen:return '// Previously inlined: '+name+'\n'
     assert name in headers,name;seen.append(name);s=(root/headers[name]).read_text();s=normalize_types(name,s)
     return '\n// BEGIN '+name+' SOURCE_SHA256 '+pins[headers[name]]+'\n'+pat.sub(lambda m:expand(m[1]),s)+'\n// END '+name+'\n'
    license='\n'.join('// '+l for l in (eng/'NUMPY_LICENSE.txt').read_text().splitlines())
    pre='// Gold MUWHAHA Miner | clean demo execution architecture | frozen HybridGate V1\n// Native compile and demo-forward test not yet performed. Real-money execution forbidden.\n#property strict\n#property version "3.00"\n#property description "HybridGate V1 standalone demo and Strategy Tester EA"\n'+license+'\n'
    for n in ['HG6Core.mqh','HG5QCManifest.mqh','HG6Calendar.mqh','HG6Feed.mqh','HG6Storage.mqh']:pre+=expand(n)
    s=(root/headers['HG6Terminal.mqh']).read_text();pre+='\n// Frozen session helper\n'+s[s.index('bool HG6TradeSession('):s.index('bool HG6ClockMapping(')]
    s=(root/headers['HG6Broker.mqh']).read_text();pre+='\n// Frozen broker fact helpers, no legacy order controller\n'+s[s.index('struct HG6Exposure '):s.index('// SECTION B1B:')]

    require(not out.exists() and not out.is_symlink(),'destination exists')
    require(file_sha(archive)==ZIP_SHA,'original packed archive mismatch')
    runtime=controller.read_text(encoding='utf-8')
    require('HG9Pump' not in runtime and 'HG6Broker ' not in runtime,'legacy controller reference')
    out.parent.mkdir(parents=True,exist_ok=True)
    tasks=[(str(archive),i,n,h) for i,(n,h) in enumerate(models)]
    results=[]
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',newline='\n',dir=out.parent,prefix='.hg10-',delete=False) as f:
        tmp=Path(f.name)
        try:
            f.write(pre);f.write(LOADER[1:])
            with ProcessPoolExecutor(max_workers=jobs) as pool:
                for i,(s,r) in enumerate(pool.map(pack_model,tasks)):
                    f.write(s);results.append(r);print(f'Verified {i+1}/88',flush=True)
            f.write('\nbool HG8ReadModel(const int index,const string expected,uchar &out[]){\n switch(index){\n')
            for i in range(COUNT): f.write(f'  case {i}: return HG8Model{i:03d}(expected,out);\n')
            f.write('  default: ArrayFree(out);return false;\n }\n}\n\n');f.write(runtime);f.flush();os.fsync(f.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True);raise
    try:
        text=tmp.read_text(encoding='utf-8')
        require(not re.search(r'^\s*#\s*(?:include|resource|import)\b|^\s*#property\s+tester_file\b',text,re.M),'external compile directive')
        require(text.count('int OnInit(){')==1 and 'class HG6Broker' not in text,'unexpected EA lifecycle')
        segs=list(re.finditer(r'bool HG8Model(\d{3})\(const string expected,uchar &out\[\]\)\{\n string blocks\[\]=\{\n(.*?)\n \};\n return HG8Decode\(blocks,(\d+),(\d+),expected,out\);\n\}',text,re.S))
        require(len(segs)==COUNT,'model payload readback count')
        for i,m in enumerate(segs):
            packed=b''.join(base64.b64decode(x,validate=True) for x in re.findall(r'"([A-Za-z0-9+/=]+)"',m[2]))
            raw=unshuffle(zlib.decompress(packed));require(int(m[1])==i and len(packed)==int(m[3]) and len(raw)==int(m[4]) and sha(raw)==models[i][1],'model readback '+str(i))
        require(not out.exists() and not out.is_symlink(),'destination appeared');os.replace(tmp,out)
    finally:tmp.unlink(missing_ok=True)
    return {'status':'SOURCE_ASSEMBLY_PASS_NATIVE_NOT_RUN','source_parent':PARENT,'source_sha256':file_sha(out),'bytes':out.stat().st_size,'archive_sha256':ZIP_SHA,'source_pins_verified':len(pins),'models_verified':len(results),'headers':seen,'assignment_boundary_type_changes':edits,'controller_sha256':file_sha(controller),'model_roundtrips':results,'native_compile':'NOT_RUN','native_demo':'NOT_RUN'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument('--archive',type=Path,required=True);p.add_argument('--controller',type=Path,default=Path(__file__).with_name('DemoController.mq5'));p.add_argument('--out',type=Path,required=True);p.add_argument('--jobs',type=int,default=4);p.add_argument('--receipt',type=Path);a=p.parse_args();require(1<=a.jobs<=8,'jobs out of range');r=build(a.root.resolve(),a.archive.resolve(),a.controller.resolve(),a.out.absolute(),a.jobs);result=json.dumps(r,indent=2);print(result);
    if a.receipt:a.receipt.write_text(result+'\n',encoding='utf-8')
if __name__=='__main__':main()
