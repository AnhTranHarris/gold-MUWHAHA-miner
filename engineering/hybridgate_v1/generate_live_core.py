"""Generate live adapter variant from pinned Stage5 sources, never edit the frozen files."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
# works in the repo layout or local staging layout; explicit source path optional
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'MQL5/Scripts/HybridGateQC'
OUT=ROOT/'MQL5/Include/HybridGateV1';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
PINS=json.loads((Path(__file__).resolve().parent/'QC_INSTALL_MANIFEST.json').read_text())
def load(name):
 p=SRC/name
 assert sha(p)==PINS['MQL5/Scripts/HybridGateQC/'+name], 'frozen source mismatch '+name
 return p.read_text()
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
# Actual holding uses frozen feature math with explicit confirmed price and age.
# Reference HG5 classes are not changed. Mapping is a new live-only engineering policy.
s=load('HG5HoldEvents.mqh'); h=s[s.index('struct HG5Hold {'):s.index('struct HG5Renew {')].rstrip()
h=once(h,'struct HG5Hold {','struct HG6ActualHold {\nlong fill_ms;')
h=once(h,'long age_ms=q[j].ms-q[e].ms;','long age_ms=q[j].ms-fill_ms;')
h=once(h,'void ZeroFields(){','void ZeroFields(){fill_ms=0;')
h=once(h,'bool StateFields(HG5StateCodec &codec){','bool StateFields(HG5StateCodec &codec){if(!codec.I64(fill_ms))return false;')
s=load('HG5HoldController.mqh'); act=s[s.index('int HG5HoldAction('):s.index('int HG5RenewAction(')].rstrip().replace('HG5HoldAction','HG6ActualHoldAction').replace('HG5Hold &st','HG6ActualHold &st')
p='''#ifndef HG6_ACTUAL_HOLDING_MQH
#define HG6_ACTUAL_HOLDING_MQH
#include "HG5HoldController.mqh"
// SECTION H1: derived actual-fill HOLD event; formula body generated from HG5Hold.
// Only age anchor is changed. Market observations are never manufactured.
'''+h+'\n'+act+'''
// SECTION H2: separate broker-confirmed path. No modeled close is a broker fill.
class HG6ActualHoldingPath {
 HG6ActualHold h; HG5Renew r; HG5Hazard a; int e,s,next;
 bool ready; long confirmed_ms; int confirmed_px,why;
 float h4,v4,h5;
 public:
 HG6ActualHoldingPath(){Reset();}
 void Reset(){h.ZeroFields();r.ZeroFields();a.ZeroFields();e=s=next=0;ready=false;confirmed_ms=0;confirmed_px=why=0;h4=v4=h5=0;}
 bool Init(const HG5HoldingBank &bank,const HG5Quote &q[],int j,int side,long base,const float &candles[],long fill_ms,int fill_px){
  Reset();if(j<=0||j>=ArraySize(q)||(side!=1&&side!=-1)||fill_px<=0||fill_ms<=q[j-1].ms||fill_ms>q[j].ms)return false;
  float rx[];if(!HG5RXFeatures(q,j+1,j,side,j-1,base,rx)||!HG5HoldingPriors(bank,rx,candles,h4,v4,h5))return false;
  e=j;s=side;next=j;confirmed_ms=fill_ms;confirmed_px=fill_px;
  h.Init(q,j,s,h5,v4);r.Init(q,j,s,h5,v4);a.Init(q,j,s,30.f,v4);
  h.px=fill_px;h.fill_ms=fill_ms;r.px=fill_px;r.t0=fill_ms;a.px=fill_px;a.t0=fill_ms;
  ready=true;return true;
 }
 int Step(const HG5HoldingBank &bank,const HG5Quote &q[],int j,const float &candles[]){
  if(!ready||j!=next||j<e||j>=ArraySize(q)||q[j].ms<confirmed_ms||ArraySize(candles)!=72)return -1;
  next++;if(why)return why;float f[],g[],z[];if(ArrayResize(f,24)!=24||ArrayResize(g,48)!=48||ArrayResize(z,60)!=60)return -1;
  int kind=0,k2=0;bool ea=h.Step(q,j,f),eb=r.Step(q,j,g,kind),ec=a.Step(q,j,z,k2);
  int ra=ea?HG6ActualHoldAction(bank,h,f,candles):0,rb=eb?HG5RenewAction(bank,r,g,candles,kind):0,rc=ec?HG5HazardAction(bank,z,candles):0;
  why=HG5Release(ra,rb,rc);return why;
 }
 bool Shift(int n){if(!ready||n<0||n>e)return false;e-=n;next-=n;h.e-=n;h.pk-=n;h.tk-=n;r.e-=n;r.pk-=n;r.lk-=n;a.e-=n;a.pk-=n;a.lk-=n;for(int i=0;i<4;i++){r.w[i]-=n;a.w[i]-=n;}return true;}
 int EntryLocal()const{return e;}
 int Reason()const{return why;}
 bool Ready()const{return ready;}
 bool Validate(int n,int side,int px,long ms)const{return ready&&e>=0&&e<n&&next==n&&s==side&&confirmed_px==px&&confirmed_ms==ms&&why>=0&&h.px==px&&r.px==px&&a.px==px&&h.fill_ms==ms&&r.t0==ms&&a.t0==ms;}
 bool StateFields(HG5StateCodec &c){return h.StateFields(c)&&r.StateFields(c)&&a.StateFields(c)&&c.I32(e)&&c.I32(s)&&c.I32(next)&&c.Flag(ready)&&c.I64(confirmed_ms)&&c.I32(confirmed_px)&&c.I32(why)&&c.F32(h4)&&c.F32(v4)&&c.F32(h5);}
};
#endif
'''
(OUT/'HG6ActualHolding.mqh').write_text(p)
s=load('HG5Core.mqh').replace('HG5_CORE_MQH','HG6_CORE_MQH').replace('class HG5Core{','class HG6Core{').replace(' HG5Core(){',' HG6Core(){')
s=once(s,'#include "HG5StateCodec.mqh"\n#include "HG5StateCodec.mqh"','#include "HG5StateCodec.mqh"\n#include "HG6ActualHolding.mqh"')
s=once(s,' long base,last_group,next_id,groups,observations;bool valid,started,loaded[88];',''' long base,last_group,next_id,groups,observations;bool valid,started,loaded[88];
 // SECTION L1: separate actual broker path; does not affect ancestral shadow decisions.
 HG6ActualHoldingPath actual; int actual_state,actual_side,actual_px,actual_units;long actual_ms,actual_id;
 bool ActualQuote(const HG5Quote &tick,int j){
  if(actual_state==0)return true;
  if(actual_state==1&&tick.ms<actual_ms)return true;
  float c[],raw[];if(!candles.Snapshot(actual_side,c,raw))return false;
  if(actual_state==1){if(!actual.Init(hold,q,j,actual_side,base,c,actual_ms,actual_px))return false;actual_state=2;}
  return actual.Step(hold,q,j,c)>=0;
 }''')
s=once(s,'if(drop<=0||n-drop+count>cap)return false;','if(actual_state==2&&actual.EntryLocal()<drop)drop=actual.EntryLocal();if(drop<=0||n-drop+count>cap)return false;if(actual_state==2&&!actual.Shift(drop))return false;')
s=once(s,'if(!candles.Push(tick.ms,tick.bid,tick.ask))return false;','if(!candles.Push(tick.ms,tick.bid,tick.ask)||!ActualQuote(tick,j))return false;')
s=once(s,' HG6Core(){valid=false;started=false;',' HG6Core(){actual_state=actual_side=actual_px=actual_units=0;actual_ms=0;actual_id=-1;valid=false;started=false;')
s=once(s,' bool Snapshot(int k,double &v[],long &z[])const',''' // SECTION L2: actual fill binding. A fill already behind committed history is ambiguous.
 bool BindActual(long id,long ms,int side,int cents,int units){if(!valid||!started||actual_state!=0||id<0||ms<=last_group||(side!=1&&side!=-1)||cents<=0||units<=0||units>100)return false;actual_id=id;actual_ms=ms;actual_side=side;actual_px=cents;actual_units=units;actual_state=1;return true;}
 bool ConfirmFlat(long id){if(actual_state==0||id!=actual_id)return false;actual.Reset();actual_state=actual_side=actual_px=actual_units=0;actual_ms=0;actual_id=-1;return true;}
 int ActualState()const{return actual_state;}
 int ActualReason()const{return actual_state==2?actual.Reason():0;}
 long ActualId()const{return actual_id;}
 long ActualMs()const{return actual_ms;}
 int ActualSide()const{return actual_side;}
 int ActualPx()const{return actual_px;}
 int ActualUnits()const{return actual_units;}
 long LastGroup()const{return last_group;}
 bool Snapshot(int k,double &v[],long &z[])const''')
s=once(s,'int version=1,savedcap=cap,savednw=nw;if(!c.I32(version)||version!=1','int version=2,savedcap=cap,savednw=nw;if(!c.I32(version)||version!=2')
s=once(s,'  return true;\n }\n bool ExportState','''  if(!c.I32(actual_state)||!c.I32(actual_side)||!c.I32(actual_px)||!c.I32(actual_units)||!c.I64(actual_ms)||!c.I64(actual_id)||!actual.StateFields(c))return false;
  if(actual_state<0||actual_state>2||(actual_state==0&&(actual_id!=-1||actual.Ready()))||(actual_state>0&&(actual_id<0||actual_ms<0||actual_px<=0||actual_units<=0||actual_units>100||(actual_side!=1&&actual_side!=-1)))||(actual_state==1&&(actual_ms<=last_group||actual.Ready()))||(actual_state==2&&(!actual.Validate(n,actual_side,actual_px,actual_ms)||actual_ms>last_group)))return false;
  return true;
 }
 bool ExportState''')
(OUT/'HG6Core.mqh').write_text(s.replace('// Version 1 payload.','// Version 2 payload.'))
print('generated live holding + core variant; original unchanged')
