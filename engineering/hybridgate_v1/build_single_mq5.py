"""Create ONE self-contained MQ5 from the immutable v2.06 source and 88 packed models.
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

def source_closure(root):
    qc=json.loads((root/(ENG+'QC_INSTALL_MANIFEST.json')).read_text())
    native=json.loads((root/(ENG+'NATIVE_SOURCE_MANIFEST.json')).read_text())
    pins={**{k:v for k,v in qc.items() if k.startswith('MQL5/Scripts/')},**native}
    require(len(pins)==39,'unexpected source count')
    for name,digest in pins.items(): require(file_sha(root/name)==digest,'source pin mismatch: '+name)
    headers={Path(k).name:k for k in pins if k.endswith('.mqh')}
    require(len(headers)==sum(k.endswith('.mqh') for k in pins),'ambiguous header basename')
    manifest=(root/headers['HG5QCManifest.mqh']).read_text(encoding='utf-8')
    ids,hashes=array(manifest,'HG_ID'),array(manifest,'HG_MODEL_SHA')
    require(len(ids)==len(hashes)==len(set(ids))==COUNT,'model order/count')
    for n,h in zip(ids,hashes): require(qc.get('MQL5/Files/HG5QC/'+n+'.hg5p')==h,'model manifest mismatch '+n)
    ea=(root/EA).read_text(encoding='utf-8')
    decl=re.findall(r'^#property tester_file "HG5QC\\\\([^"]+)\.hg5p"$',ea,re.M)
    require(decl==ids,'original tester declaration order mismatch')
    ea,n=re.subn(r'^#property tester_file .*\n','',ea,flags=re.M)
    require(n==COUNT,'tester declaration count')
    ea=once(ea,'// SECTION 00 — exact tester asset declarations; native transfer still requires QC.','// SECTION 00 — monolithic MQ5; all original fitted model bytes contained in this file; native QC pending.')
    ea=once(ea,'#property version   "2.06"','#property version   "2.08"')
    ea=once(ea,'#property description "Human Approved HybridGate V1 — tester-only integration candidate; demo/live execution locked"','#property description "HybridGate V1 single-file source candidate; demo/live execution locked"')
    ea=once(ea,'#include <HybridGateV1/HG5FileAdapter.mqh>\n','')
    ea=once(ea,r'HG5ReadVerified("HG5QC\\"+HG_ID[i]+".hg5p",HG_MODEL_SHA[i],67108864,bytes)','HG8ReadModel(i,HG_MODEL_SHA[i],bytes)')
    ea=once(ea,'g_scope="HybridGateV1_"+HG6Hex(lock_id)+"_"+InpRunId+(g_tester?"_TEST":"_OBS");','g_scope="HybridGateV1_"+HG6Hex(lock_id)+"_"+InpRunId+(g_tester?"_TEST_MONO":"_OBS_MONO");')
    require(ea.count('HG6_BUILD_ID')==2,'identity anchors')
    ea=ea.replace('HG6_BUILD_ID','HG8_BUILD_ID')
    # Loader insertion point is after the native headers and before EA inputs.
    ea=once(ea,'#include <HybridGateV1/HG6BuildIdentity.mqh>','// HG8_MODEL_PAYLOAD_INSERTION')
    pattern=re.compile(r'^\s*#include\s+(?:"([^"\n]+)"|<HybridGateV1/([^>\n]+)>)\s*$',re.M)
    seen=set();ordered=[]
    def expand(t):
        def include(m):
            name=m.group(1) or m.group(2)
            require(name in headers,'unresolved include '+name)
            if name in seen: return '// Previously inlined: '+name+'\n'
            seen.add(name);ordered.append(name)
            p=headers[name];s=(root/p).read_text(encoding='utf-8')
            # Existing modules use unconditional includes within their header guard.
            require(not re.search(r'^\s*#(?:if|ifdef|elif|else)\b',s,re.M),'conditional include requires review '+name)
            return '\n// BEGIN EXACT FROZEN HEADER '+p+' SHA256 '+pins[p]+'\n'+expand(s)+'\n// END EXACT FROZEN HEADER '+p+'\n'
        return pattern.sub(include,t)
    flat=expand(ea)
    require(not re.search(r'^\s*#\s*(?:include|resource|import)\b|^\s*#property\s+tester_file\b',flat,re.M),'external compile directive remained')
    require('HG5ReadVerified(' not in flat,'runtime model-file reader remained')
    require(flat.count('// HG8_MODEL_PAYLOAD_INSERTION')==1,'payload anchor')
    require('g_execute=InpRequestTesterExecution&&g_tester&&HG6_TESTER_EXECUTION_ENABLED==1;' in flat,'tester release lock changed')
    require('#define HG6_EXECUTION_RELEASED 0' in flat,'demo/live release lock changed')
    license=(root/(ENG+'NUMPY_LICENSE.txt')).read_text(encoding='utf-8')
    license='\n'.join('// '+l for l in license.splitlines())
    flat='// Full Human Approved HybridGate V1 source; parent '+PARENT+'\n// Native compile NOT_RUN; all execution gates remain unchanged.\n'+license+'\n'+flat
    return flat, list(zip(ids,hashes)), ordered

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

def build(root,archive,out,jobs):
    require(not out.exists() and not out.is_symlink(),'destination already exists')
    require(file_sha(archive)==ZIP_SHA,'frozen archive hash mismatch')
    flat,models,headers=source_closure(root)
    before,after=flat.split('// HG8_MODEL_PAYLOAD_INSERTION')
    out.parent.mkdir(parents=True,exist_ok=True);receipt=[]
    tasks=[(str(archive),i,n,h) for i,(n,h) in enumerate(models)]
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',newline='\n',dir=out.parent,prefix='.hg8-',delete=False) as f:
        tmp=Path(f.name)
        try:
            f.write(before);f.write(LOADER)
            if jobs>1:
                with ProcessPoolExecutor(max_workers=jobs) as pool:
                    for i,(s,r) in enumerate(pool.map(pack_model,tasks)):
                        f.write(s);receipt.append(r);print(f'Verified model {i+1}/{COUNT}',flush=True)
            else:
                for i,task in enumerate(tasks):
                    s,r=pack_model(task);f.write(s);receipt.append(r);print(f'Verified model {i+1}/{COUNT}',flush=True)
            f.write('\nbool HG8ReadModel(const int index,const string expected,uchar &out[]){\n switch(index){\n')
            for i in range(COUNT):f.write(f'  case {i}: return HG8Model{i:03d}(expected,out);\n')
            f.write('  default: ArrayFree(out);return false;\n }\n}\n');f.write(after);f.flush();os.fsync(f.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True);raise
    try:
        # Read back the final file itself, not just the generation buffer.
        actual=tmp.read_text(encoding='utf-8');require(not re.search(r'^\s*#\s*(?:include|resource|import)\b|^\s*#property\s+tester_file\b',actual,re.M),'external dependency directive in final file')
        segments=list(re.finditer(r'bool HG8Model(\d{3})\(const string expected,uchar &out\[\]\)\{\n string blocks\[\]=\{\n(.*?)\n \};\n return HG8Decode\(blocks,(\d+),(\d+),expected,out\);\n\}',actual,re.S))
        require(len(segments)==COUNT,'readback model count')
        for i,m in enumerate(segments):
            require(int(m.group(1))==i,'readback order');chunks=re.findall(r'"([A-Za-z0-9+/=]+)"',m.group(2));require(len(chunks)==receipt[i]['chunks'] and max(map(len,chunks))<=CHUNK,'readback chunks')
            c=b''.join(base64.b64decode(s,validate=True) for s in chunks);require(len(c)==int(m.group(3)),'readback packed length')
            b=unshuffle(zlib.decompress(c));require(len(b)==int(m.group(4)) and sha(b)==models[i][1],'readback model mismatch')
        require(len(re.findall(r'^  case \d+: return HG8Model\d{3}\(expected,out\);$',actual,re.M))==COUNT,'dispatch count')
        require(not out.exists() and not out.is_symlink(),'destination appeared');os.replace(tmp,out)
    finally:tmp.unlink(missing_ok=True)
    return {'status':'SINGLE_MQ5_SOURCE_ASSEMBLY_PASS_NATIVE_COMPILE_NOT_RUN','parent':PARENT,'sha256':file_sha(out),'source_bytes':out.stat().st_size,'models':COUNT,'raw_model_bytes':sum(r['raw_bytes'] for r in receipt),'compressed_model_bytes':sum(r['compressed_bytes'] for r in receipt),'inlined_headers':headers,'source_pin_count':39,'external_compile_directives':0,'native_compile':'NOT_RUN','model_roundtrips':receipt}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--jobs',type=int,default=4);a=p.parse_args();require(1<=a.jobs<=8,'jobs out of range');r=build(a.root.resolve(),a.archive.resolve(),a.out.absolute(),a.jobs);print(json.dumps(r,indent=2))
if __name__=='__main__':main()
