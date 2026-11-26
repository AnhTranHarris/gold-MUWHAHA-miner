"""Reproduce the v2.09 normal-tester single MQ5 from immutable v2.06 and 88 packed models.
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

# Entire rebuilt tester controller, including unchanged reusable transaction routines.
RUNTIME = r"""
// HG9 — independent normal Strategy Tester controller; original research and reconciliation retained.
#define HG9_BUILD_ID "HG9-normal-tester-699da4f68239b8029a9e61e272e650f90c365de5-v1"
input group "Trading"
input ulong InpMagic=6202601;
input bool InpLotLadder=false;
input int InpLadderCapUnits=10;
input group "Historical broker clock (fixed offset from UTC)"
input int InpSourceUtcOffsetMinutes=0;
input bool InpWeeklyClock=false;
input bool InpUseTradingClock=true;
input group "Tester transport"
input int InpQuoteCapacity=262144;
input int InpMaxGroupsPerPump=4096;
input int InpMaxQuoteAgeMs=2000;
input int InpDeviationPoints=10;
input int InpCheckpointSeconds=15;
const bool InpEmergencyCloseAuthorized=true; // simulation only
HG6Core g_core;HG6Cursor g_cursor;HG6Store g_store;HG6Broker g_broker;HG6Telemetry g_log;HG6Readiness g_ops;
HG5Window g_windows[];MqlTick g_raw[HG6_TICK_BATCH];HG5Quote g_group[];
HG5StageEvent g_stage[];HG5Proposal g_proposals[];HG5PathEvent g_paths[];HG5AccountEvent g_accounts[];
string g_scope="";int g_lock=INVALID_HANDLE;bool g_initialized=false,g_fatal=false,g_caught_up=false,g_dirty=false,g_overdue=false,g_trade_dirty=true;
long g_applied_seq=0,g_external_applied=0;
ulong g_save_count=0,g_save_total_us=0,g_save_max_us=0,g_save_max_bytes=0,g_pump_max_us=0,g_copy_max_us=0;
long g_last_flat_ms=-1,g_mailbox=0,g_seen_proposals=0,g_suppressed_proposals=0;ulong g_saved_us=0,g_last_service=0,g_last_copy_us=0;
bool g_tester=false,g_execute=false,g_origin_verified=false;ulong g_trade_first_us=0;long g_dispatched=0,g_gate_blocked=0;
void HG6Fault(string why){if(!g_fatal)Print("HG6 FAIL CLOSED: ",why);g_fatal=true;g_ops.Quarantine();
 // Persist rescue even if already flat; a fatal model failure is not reset by a restart.
 if(g_execute&&!g_broker.EnterRescue())Print("HG6: durable quarantine unavailable; operator reconciliation required");
}
// ============================================================================
// SECTION 03 — snapshot identity, explicit field encoding, verified two-slot recovery.
// ============================================================================
bool HG6Save(){
 if(!g_initialized||g_fatal||!g_store.Healthy())return false;ulong begin=GetMicrosecondCount();uchar core[],cursor[],all[];HG5StateCodec c;int version=4;
 if(!g_core.ExportState(core)||!c.BeginWrite()||!c.I32(version)||!g_cursor.Transfer(c)||!c.I64(g_applied_seq)||!c.I64(g_external_applied)||!c.I64(g_last_flat_ms)||!c.Flag(g_overdue)||!c.Flag(g_origin_verified)||!c.Finish(cursor))return false;
 int a=ArraySize(cursor),b=ArraySize(core);if(a<=0||b<=0||a+b+16>HG6_MAX_ENVELOPE-96||ArrayResize(all,a+b+16)!=a+b+16)return false;
 HG6Put64(all,0,a);HG6Put64(all,8,b);if(ArrayCopy(all,cursor,16,0,a)!=a||ArrayCopy(all,core,16+a,0,b)!=b||!g_store.Save(all))return false;
 g_saved_us=GetMicrosecondCount();ulong elapsed=g_saved_us-begin;g_save_count++;g_save_total_us+=elapsed;if(elapsed>g_save_max_us)g_save_max_us=elapsed;if((ulong)ArraySize(all)>g_save_max_bytes)g_save_max_bytes=(ulong)ArraySize(all);g_dirty=false;return true;
}
// ============================================================================
// SECTION 04 — actual execution reconciliation, never the modeled account ledger.
// ============================================================================
bool HG6RecordFlat(long pos){
 // Establish an observable confirmation epoch BEFORE mutating the core. If quote
 // retrieval fails, the server clock is still a conservative cooldown boundary.
 MqlTick t;HG5Quote q;long observed=0;datetime server=TimeTradeServer();
 if(server>0)observed=(long)server*1000;
 if(SymbolInfoTick(_Symbol,t)&&HG6Normalize(t,q)&&t.time_msc>observed)observed=t.time_msc;
 if(observed<=0)return false;
 if(g_core.ActualState()!=0&&!g_core.ConfirmFlat(pos))return false;
 if(observed>g_last_flat_ms)g_last_flat_ms=observed;g_overdue=false;g_dirty=true;return true;
}
bool HG6Reconcile(HG6Exposure &x){
 if(!HG6ExposureRead(_Symbol,InpMagic,x)||x.foreign||x.ambiguous){x.ambiguous=true;g_ops.Disarm();return false;}
 if(g_broker.Outstanding()){
  if(!g_broker.Reconcile(x)||!g_broker.Resolved())return false;
  // Replay an unresolved outcome only if its sequence is not already in the verified core checkpoint.
  long seq=g_broker.Sequence();if(!g_broker.CheckLink(g_applied_seq,g_store.Generation())){HG6Fault("transaction watermark mismatch");return false;}
  bool intent_flat=g_broker.IntentAlreadyFlat();long flat_pos=intent_flat?g_broker.PositionId():0;
  if(g_applied_seq!=seq||(intent_flat&&g_external_applied!=flat_pos)){
  if(intent_flat){if(x.ticket||x.pending||!HG6RecordFlat(flat_pos))return false;g_external_applied=flat_pos;}
  else if(g_broker.Filled()&&g_broker.IntentKind()==1){
   if(!x.ticket)return false;
   if(g_core.ActualState()==0){
    bool ok=x.anchor_ok?g_core.BindActual((long)x.identifier,x.time_ms,x.side,x.price_cents,x.units):g_core.BindUnmodeled((long)x.identifier,x.time_ms,x.side,x.units);
    if(!ok&&g_core.ActualState()!=3){HG6Fault("cannot bind confirmed position identity");return false;}
    if(g_core.ActualState()==3){g_ops.Disarm();g_log.Event("ACTUAL_ANCHOR_QUARANTINE",x.time_ms,(long)x.identifier,0,0,0);g_overdue=true;}
   }else if(g_core.ActualId()!=(long)x.identifier||g_core.ActualMs()!=x.time_ms||g_core.ActualSide()!=x.side||g_core.ActualUnits()!=x.units||(g_core.ActualState()!=3&&(!x.anchor_ok||g_core.ActualPx()!=x.price_cents))){HG6Fault("actual fill identity mismatch");return false;}
  }else if(g_broker.Filled()&&g_broker.IntentKind()==2){
   long pos=g_broker.PositionId();if(x.ticket){if((long)x.identifier!=pos||!g_core.ReduceActual(pos,x.units))return false;g_overdue=true;}
   else if(!HG6RecordFlat(pos))return false;
  }
  g_applied_seq=seq;g_dirty=true;if(!HG6Save()){HG6Fault("reconciliation checkpoint failed");return false;}
  }
  if(!g_broker.ReleaseApplied(g_applied_seq,g_store.Generation())){HG6Fault("reconciliation journal release failed");return false;}
 }
 if(x.pending)return false;
 if(x.ticket){if(g_core.ActualState()==0||g_core.ActualId()!=(long)x.identifier||g_core.ActualSide()!=x.side||g_core.ActualMs()!=x.time_ms||g_core.ActualUnits()!=x.units||(g_core.ActualState()!=3&&(!x.anchor_ok||g_core.ActualPx()!=x.price_cents)))return false;}
 else if(g_core.ActualState()!=0){long pos=g_core.ActualId();if(!g_broker.ExternalFlat(pos)||!HG6RecordFlat(pos)){g_ops.Disarm();return false;}g_external_applied=pos;if(!HG6Save()){HG6Fault("external flat checkpoint failed");return false;}}
 if(g_broker.ExternalPending()!=0){long pos=g_broker.ExternalPending();if(x.ticket||x.pending||g_core.ActualState()!=0||g_external_applied!=pos||!g_broker.ReleaseExternal(pos,g_applied_seq,g_store.Generation())){HG6Fault("external flat commit mismatch");return false;}}
 else if(!x.ticket&&g_broker.ActiveLedgerPosition()!=0){g_ops.Disarm();return false;}
 if(!x.ticket&&!x.pending&&g_overdue){g_overdue=false;g_dirty=true;if(!HG6Save()){HG6Fault("flat-state persistence failed");return false;}}
 g_trade_dirty=false;g_mailbox=0;g_trade_first_us=0;return g_broker.Ready();
}
// ============================================================================
// SECTION 05 — clock, account risk and actual-exposure protection.
// ============================================================================
int HG6Action(long source_ms,const HG6Exposure &x,bool mapped,bool session){return HG5Clock(source_ms,x.ticket!=0,x.pending,session,mapped,InpUseTradingClock,g_overdue,g_windows,ArraySize(g_windows));}
// Clock and safety evaluation is independent of tick availability. The frozen
// clock policy is unchanged. No quote is synthesized for a market close.
bool HG6MaybeClose(const HG6Exposure &x,const MqlTick &latest,int clock_action,bool reconciled,bool quote_ready=true,bool session_open=true){
 datetime server=TimeTradeServer();long now=server>0?(long)server*1000:0;
 if(quote_ready&&latest.time_msc>now)now=latest.time_msc;
 bool age_due=x.ticket!=0&&now>0&&now-x.time_ms>=30000;
 HG6AccountFacts facts;bool risk=x.ticket!=0&&HG6ReadAccount(facts)&&HG6AccountUrgent(facts);
 bool urgent=clock_action==HG5_FLATTEN||age_due||g_overdue||g_core.ActualState()==3||risk;
 if((x.ticket||x.pending)&&urgent){if(!g_overdue){g_overdue=true;g_dirty=true;}g_ops.Disarm();}
 if(x.pending&&(clock_action==HG5_DRAIN_CANCEL_PENDING||urgent)){
  g_ops.Disarm();
  if(g_execute&&InpEmergencyCloseAuthorized&&!x.foreign&&!x.ambiguous)g_broker.CancelPending(x);
  return true;
 }
 if(x.ticket==0)return false;
 int reason=g_core.ActualReason();if(!urgent&&reason<=0)return false;
 // No market submission from unavailable/stale quote or known closed session.
 // Leave overdue latched; timer will retry only after fresh observable evidence.
 bool market_ready=quote_ready&&now>=latest.time_msc&&now-latest.time_msc<=InpMaxQuoteAgeMs&&session_open;
 if(!market_ready||!g_execute||(!reconciled&&!(urgent&&g_broker.Ready()&&g_broker.ActiveLedgerPosition()==(long)x.identifier))||g_broker.Outstanding()||x.foreign||x.ambiguous||x.pending||(!InpEmergencyCloseAuthorized&&urgent&&reason<=0)){
  g_log.Event("CLOSE_BLOCKED",now,(long)x.identifier,reason,(long)urgent,clock_action);return true;
 }
 if(!HG6Save()){HG6Fault("cannot persist close intent context");return true;}
 if(!g_broker.Submit(2,g_core.ActualId(),-x.side,x.units,latest,x,(ulong)InpDeviationPoints))g_ops.Disarm();return true;
}
// Fatal-state protection never evaluates the failed model or creates an entry.
// Only a known owned position in the explicitly authorized simulated tester may be closed.
void HG6RiskOnly(){
 HG6Exposure x;MqlTick t;HG5Quote q;if(!HG6ExposureRead(_Symbol,InpMagic,x)||x.foreign||x.ambiguous)return;
 if(!g_execute||!InpEmergencyCloseAuthorized||!g_broker.EnterRescue())return;
 if(!x.ticket&&!x.pending&&!g_broker.Outstanding()&&g_broker.ActiveLedgerPosition()==0&&g_broker.ExternalPending()==0)return;
 Comment("HG6 QUARANTINE: owned exposure detected; entries disabled");
 if(g_broker.Outstanding()){bool resolved=g_broker.Reconcile(x)&&g_broker.Resolved();if(x.pending){g_broker.CancelPending(x);return;}if(!resolved||!g_broker.ReleaseRescue())return;}
 if(x.pending)return;
 if(!x.ticket&&g_broker.ActiveLedgerPosition()!=0){g_broker.ExternalFlat(g_broker.ActiveLedgerPosition());return;}
 if(!x.ticket&&g_broker.ExternalPending()!=0){g_broker.ReleaseExternalRescue();return;}
 datetime server=TimeTradeServer();
 if(x.ticket&&g_broker.Ready()&&g_broker.ActiveLedgerPosition()==(long)x.identifier&&SymbolInfoTick(_Symbol,t)&&HG6Normalize(t,q)&&HG6TradeSession(_Symbol,server)&&server>0&&(long)server*1000-t.time_msc<=InpMaxQuoteAgeMs)g_broker.Submit(2,(long)x.identifier,-x.side,x.units,t,x,(ulong)InpDeviationPoints);
}
// New tester-only orchestrator. No exact reference quote, external history or manual execution arming.
long hg9_ticks=0,hg9_history_wait=0,hg9_stale=0,hg9_clock=0,hg9_busy=0,hg9_account=0,hg9_order_reject=0,hg9_ready=0,hg9_last_report=0;
bool hg9_models_ready=false;
void HG9Report(string phase){
 PrintFormat("HG9 %s ticks=%I64d quotes=%I64d proposals=%I64d stale=%I64d busy=%I64d clock=%I64d account=%I64d readiness=%I64d order_reject=%I64d sends=%I64d closed=%I64d net=%.8f history_wait=%I64d fatal=%d",phase,hg9_ticks,g_cursor.Ordinal(),g_seen_proposals,hg9_stale,hg9_busy,hg9_clock,hg9_account,hg9_ready,hg9_order_reject,g_dispatched,g_broker.ClosedPositions(),g_broker.ActualNet(),hg9_history_wait,(int)g_fatal);
}
int HG9InitFail(string why){Print("HG9 INITIALIZATION FAILED: ",why," error=",GetLastError());return INIT_FAILED;}
bool HG9FreshRun(const MqlTick &first){
 if(!g_cursor.Init(first.time_msc)){Print("HG9 cursor init failed");return false;}
 string key=AccountInfoString(ACCOUNT_SERVER)+"|"+IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN))+"|"+_Symbol+"|"+IntegerToString((long)InpMagic)+"|"+IntegerToString(first.time_msc)+"|"+HG9_BUILD_ID;
 uchar id[],intent_id[],digest[];if(!HG6TextDigest(key,digest))return false;
 string prefix="HG9_"+HG6Hex(digest);bool found=false;
 for(int i=0;i<10000;i++){
  string name=prefix+"_"+IntegerToString(i);
  if(!FileIsExist(name+"_state.genesis")&&!FileIsExist(name+"_state.0.bin")&&!FileIsExist(name+"_state.1.bin")&&!FileIsExist(name+"_intent.genesis")&&!FileIsExist(name+"_intent.0.bin")&&!FileIsExist(name+"_intent.1.bin")&&!FileIsExist(name+"_events.0.csv")){g_scope=name;found=true;break;}
 }
 if(!found||!HG6TextDigest(g_scope+"|core",id)||!HG6TextDigest(g_scope+"|intent",intent_id))return false;
 if(!g_store.Init(g_scope+"_state",id)||!g_log.Open(g_scope+"_events"))return false;
 uchar empty[];if(g_store.Load(empty)!=0||!g_broker.Init(_Symbol,InpMagic,g_scope+"_intent",intent_id,true)||!g_broker.CheckLink(0,g_store.Generation()))return false;
 HG6Exposure x;if(!HG6ExposureRead(_Symbol,InpMagic,x)||x.ticket||x.pending||x.foreign||x.ambiguous)return false;
 HG5OpsLimits lim;lim.max_quote_age_ms=InpMaxQuoteAgeMs;lim.max_queue_us=1;lim.max_service_us=1;lim.max_trade_lag_ms=InpMaxQuoteAgeMs;lim.max_queue=HG6_TICK_BATCH;lim.max_active=1;lim.max_mailbox=1024;
 if(!g_ops.Init(lim))return false;
 g_initialized=true;g_origin_verified=true;g_saved_us=GetMicrosecondCount();
 PrintFormat("HG9 START first_ms=%I64d bid=%.2f ask=%.2f offset_minutes=%d scope=%s",first.time_msc,first.bid,first.ask,InpSourceUtcOffsetMinutes,g_scope);
 return true;
}
bool HG9Entry(const HG5Proposal &p,const MqlTick &latest,const HG6Exposure &x,bool mapped,bool session,bool reconciled,long now){
 if(!reconciled||!g_broker.Ready()||g_broker.Outstanding()||x.ticket||x.pending||x.foreign||x.ambiguous||g_core.ActualState()!=0||p.t<=g_last_flat_ms){hg9_busy++;return false;}
 if(HG6Action(p.t,x,mapped,session)!=HG5_TRADE||HG6Action(now,x,mapped,session)!=HG5_TRADE){hg9_clock++;return false;}
 // CPU and disk wall time are not simulated market latency. Preserve chronological quote age and account/ownership gates.
 HG5OpsSample s;s.now_us=(long)GetMicrosecondCount();s.quote_age_ms=now-latest.time_msc;s.queue_us=0;s.service_us=0;s.trade_lag_ms=0;s.queue=0;s.active=0;s.mailbox=(int)g_mailbox;
 s.connected=true;s.calendar_ok=mapped;s.identity_ok=HG6BrokerSpec(_Symbol);s.history_ok=true;s.reconciled=reconciled&&!g_trade_dirty;s.storage_ok=g_store.Healthy()&&g_broker.IntegrityHealthy()&&g_broker.CheckLink(g_applied_seq,g_store.Generation());
 if(!g_ops.Arm(s,g_execute&&!g_fatal&&!g_overdue)){hg9_ready++;return false;}
 HG6AccountFacts facts;if(!HG6ReadAccount(facts)||!HG6AdmissionAccount(facts)||facts.balance>9e13){hg9_account++;return false;}
 int units=HG5LotUnits((long)MathRound(facts.balance*100.0),InpLotLadder,InpLadderCapUnits);if(units<=0||!HG6VolumeAllowed(_Symbol,(double)units/100.0)){hg9_account++;return false;}
 if(!HG6Save()){HG6Fault("entry checkpoint");return false;}
 if(!g_broker.Submit(1,p.id,p.side,units,latest,x,(ulong)InpDeviationPoints,0)){hg9_order_reject++;if(hg9_order_reject<=10||hg9_order_reject%100==0)PrintFormat("HG9 order not acknowledged id=%I64d side=%d error=%d outstanding=%d",p.id,p.side,GetLastError(),(int)g_broker.Outstanding());g_ops.Disarm();return false;}
 g_dispatched++;return true;
}
void HG9Pump(){
 if(!hg9_models_ready)return;
 if(g_fatal){if(g_initialized)HG6RiskOnly();return;}
 MqlTick latest={};HG5Quote normalized;
 if(!SymbolInfoTick(_Symbol,latest)||!HG6Normalize(latest,normalized)){hg9_history_wait++;if(hg9_history_wait<=3)Print("HG9 waiting for valid cents-grid bid/ask");return;}
 if(!g_initialized&&!HG9FreshRun(latest)){HG6Fault("tester run initialization");return;}
 ulong started=GetMicrosecondCount();HG6Exposure x;bool reconciled=HG6Reconcile(x);if(g_fatal)return;
 datetime server=TimeCurrent();long now=(long)server*1000;if(now<latest.time_msc)now=latest.time_msc;
 bool mapped=ArraySize(g_windows)>0&&now>=g_windows[0].open_ms&&now<g_windows[ArraySize(g_windows)-1].close_ms;
 bool session=HG6TradeSession(_Symbol,server);
 bool close_requested=HG6MaybeClose(x,latest,HG6Action(now,x,mapped,session),reconciled,true,session);
 if(g_fatal)return;
 if(g_cursor.Last()>latest.time_msc){HG6Fault("terminal time regression");return;}
 ulong copy_start=GetMicrosecondCount();ResetLastError();int n=CopyTicks(_Symbol,g_raw,COPY_TICKS_ALL,(ulong)g_cursor.From(),HG6_TICK_BATCH);int err=GetLastError();g_last_copy_us=GetMicrosecondCount()-copy_start;if(g_last_copy_us>g_copy_max_us)g_copy_max_us=g_last_copy_us;
 if(n<0||n>ArraySize(g_raw)||err!=0){hg9_history_wait++;g_caught_up=false;g_ops.Disarm();if(hg9_history_wait<=5||hg9_history_wait%1000==0)PrintFormat("HG9 history wait n=%d err=%d",n,err);return;}
 while(n>0&&g_raw[n-1].time_msc>latest.time_msc)n--;
 int first=0,status=g_cursor.ClassifyBatch(g_raw,n,first);if(status<0){HG6Fault("quote overlap/order/grid integrity");return;}
 if(status==0){hg9_history_wait++;g_caught_up=false;return;}
 int lo=first,count=0;g_caught_up=false;
 while(lo<n&&count<InpMaxGroupsPerPump){
  int end=g_cursor.NextEnd(g_raw,n,lo);if(end<0){HG6Fault("same-ms group capacity/order");return;}if(end==0)break;
  if(!g_cursor.Group(g_raw,lo,end,g_group)||!g_core.StepGroup(g_group,g_stage,g_proposals,g_paths,g_accounts)||!g_cursor.Commit(g_raw,lo,end)){HG6Fault("frozen core/feed commit");return;}
  g_dirty=true;count++;lo=end;
  bool fresh=n<HG6_TICK_BATCH&&g_raw[n-1].time_msc==latest.time_msc&&g_raw[lo].time_msc==latest.time_msc;
  if(g_core.ActualReason()>0&&!close_requested)close_requested=HG6MaybeClose(x,latest,HG6Action(now,x,mapped,session),reconciled,true,session);
  int proposals=ArraySize(g_proposals);g_seen_proposals+=proposals;
  if(proposals>0){
   for(int j=0;j<proposals;j++)if(!g_log.Event("PROPOSAL",g_proposals[j].t,g_proposals[j].id,g_proposals[j].side,g_proposals[j].origin,g_cursor.Ordinal())){HG6Fault("proposal telemetry");return;}
   if(!fresh||latest.time_msc-g_proposals[0].t>InpMaxQuoteAgeMs||g_proposals[0].t>=latest.time_msc){hg9_stale+=proposals;g_suppressed_proposals+=proposals;}
   else if(close_requested){hg9_busy+=proposals;g_suppressed_proposals+=proposals;}
   else {if(proposals>1){hg9_stale+=proposals-1;g_suppressed_proposals+=proposals-1;}if(!HG9Entry(g_proposals[0],latest,x,mapped,session,reconciled,now))g_gate_blocked++;}
  }
  if(g_fatal)return;
 }
 g_caught_up=n>0&&n<HG6_TICK_BATCH&&lo<n&&g_raw[lo].time_msc==latest.time_msc&&g_raw[n-1].time_msc==latest.time_msc;
 if(!g_caught_up||g_trade_dirty)g_ops.Disarm();
 if(g_dirty&&GetMicrosecondCount()-g_saved_us>=(ulong)InpCheckpointSeconds*1000000&&!HG6Save()){HG6Fault("periodic checkpoint");return;}
 g_last_service=GetMicrosecondCount()-started;if(g_last_service>g_pump_max_us)g_pump_max_us=g_last_service;
 if(hg9_ticks-hg9_last_report>=10000){HG9Report("PROGRESS");hg9_last_report=hg9_ticks;}
}
int OnInit(){
 g_tester=MQLInfoInteger(MQL_TESTER)!=0;
 if(!g_tester){Print("HG9 Strategy Tester build: demo/live execution intentionally unavailable");return INIT_FAILED;}
 g_execute=true;
 if(InpMagic==0||InpLadderCapUnits<1||InpLadderCapUnits>100||InpQuoteCapacity<32768||InpQuoteCapacity>262144||InpMaxGroupsPerPump<1||InpMaxGroupsPerPump>4096||InpMaxQuoteAgeMs<1||InpDeviationPoints<0||InpCheckpointSeconds<1||InpSourceUtcOffsetMinutes< -840||InpSourceUtcOffsetMinutes>840)return HG9InitFail("invalid inputs");
 if(StringFind(_Symbol,"XAUUSD")<0||!HG6BrokerSpec(_Symbol))return HG9InitFail("requires XAUUSD, USD account, 100 oz contract and cents tick grid");
 if(AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)return HG9InitFail("requires hedging account");
 if(!HG6FokAllowed(_Symbol))return HG9InitFail("requires FOK execution support");
 if(!HG6VolumeAllowed(_Symbol,0.01))return HG9InitFail("0.01 lot unsupported");
 if(!HG6Windows(InpWeeklyClock,InpSourceUtcOffsetMinutes,g_windows))return HG9InitFail("frozen calendar");
 if(ArraySize(HG_ID)!=88||ArraySize(HG_MODEL_SHA)!=88)return HG9InitFail("model manifest count");
 Print("HG9 LOADING 88 embedded models; default simulated order execution ACTIVE");
 uchar bytes[];for(int i=0;i<88;i++){if(IsStopped()||!HG8ReadModel(i,HG_MODEL_SHA[i],bytes)||!g_core.Load(i,bytes)){PrintFormat("HG9 MODEL FAILURE index=%d name=%s error=%d",i,HG_ID[i],GetLastError());return HG9InitFail("embedded model decode/hash/shape");}ArrayFree(bytes);if((i+1)%11==0)PrintFormat("HG9 models verified %d/88",i+1);}
 if(!g_core.Start(g_windows,InpQuoteCapacity))return HG9InitFail("core startup");
 hg9_models_ready=true;Print("HG9 READY: 88/88 models verified; waiting for first tester tick. Calendar 2026-2028; fixed source clock offset in Inputs.");return INIT_SUCCEEDED;
}
void OnTick(){hg9_ticks++;HG9Pump();}
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result){g_trade_dirty=true;if(g_mailbox<1025)g_mailbox++;if(g_mailbox>1024)g_ops.Disarm();}
void OnDeinit(const int reason){if(g_initialized&&g_dirty&&!g_fatal&&!HG6Save())Print("HG9 final checkpoint failed");HG9Report("FINAL");if(!hg9_models_ready)Print("HG9 did not complete initialization");else if(!g_initialized)Print("HG9 no usable tick received");else if(g_seen_proposals==0)Print("HG9 no strategy proposals; inspect tick count, date and cold-start history");else if(g_dispatched==0)Print("HG9 proposals existed but no order acknowledged; inspect gate counters and broker journal");g_log.Close();PrintFormat("HG9 deinit reason=%d; no implied liquidation",reason);}
"""
EXPECTED = '97b28887bf81ca79dbbbb403d38418dbc761b294f00756c8c3a4cb83d22ae715'
def build(root,archive,out,jobs):
    require(not out.exists() and not out.is_symlink(),'destination already exists')
    require(file_sha(archive)==ZIP_SHA,'frozen archive hash mismatch')
    flat,models,headers=source_closure(root)
    before,_=flat.split('// HG8_MODEL_PAYLOAD_INSERTION')
    before=before.replace('"2.08"','"2.09"').replace('HybridGate V1 single-file source candidate; demo/live execution locked','HybridGate V1 standalone Strategy Tester; demo/live locked')
    out.parent.mkdir(parents=True,exist_ok=True)
    tasks=[(str(archive),i,n,h) for i,(n,h) in enumerate(models)]
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',newline='\n',dir=out.parent,prefix='.hg9-',delete=False) as f:
        tmp=Path(f.name)
        try:
            f.write(before);f.write(LOADER[1:])
            with ProcessPoolExecutor(max_workers=jobs) as pool:
                for i,(s,r) in enumerate(pool.map(pack_model,tasks)):
                    f.write(s);print(f'Verified model {i+1}/{COUNT}',flush=True)
            f.write('\nbool HG8ReadModel(const int index,const string expected,uchar &out[]){\n switch(index){\n')
            for i in range(COUNT): f.write(f'  case {i}: return HG8Model{i:03d}(expected,out);\n')
            f.write('  default: ArrayFree(out);return false;\n }\n}\n\n');f.write(RUNTIME);f.flush();os.fsync(f.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True);raise
    try:
        require(file_sha(tmp)==EXPECTED,'generated source is not the verified v2.09 artifact')
        require(not out.exists() and not out.is_symlink(),'destination appeared');os.replace(tmp,out)
    finally:tmp.unlink(missing_ok=True)
    return {'status':'REPRODUCED_VERIFIED_V209_SOURCE','sha256':file_sha(out),'source_bytes':out.stat().st_size,'models':88,'native_compile':'NOT_RUN','native_strategy_tester':'NOT_RUN'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--jobs',type=int,default=4);a=p.parse_args();require(1<=a.jobs<=8,'jobs out of range');r=build(a.root.resolve(),a.archive.resolve(),a.out.absolute(),a.jobs);print(json.dumps(r,indent=2))
if __name__=='__main__':main()
