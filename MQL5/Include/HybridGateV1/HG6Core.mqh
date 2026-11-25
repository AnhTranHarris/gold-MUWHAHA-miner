#ifndef HG6_CORE_MQH
#define HG6_CORE_MQH
#include "HG5StateCodec.mqh"
#include "HG6ActualHolding.mqh"
#include "HG5ExtendedHierarchical.mqh"
#include "HG5HoldController.mqh"
#include "HG5ResearchAccount.mqh"
#define HG5_MAX_ACTIVE 1024
struct HG5Proposal{long id,t,origin;int side;
 void ZeroFields(){{id=0;}{t=0;}{origin=0;}{side=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(id))return false;}{if(!codec.I64(t))return false;}{if(!codec.I64(origin))return false;}{if(!codec.I32(side))return false;}return true;}
};
struct HG5StageEvent{int stage;long ms;int side;long rank,source;float confidence;
 void ZeroFields(){{stage=0;}{ms=0;}{side=0;}{rank=0;}{source=0;}{confidence=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I32(stage))return false;}{if(!codec.I64(ms))return false;}{if(!codec.I32(side))return false;}{if(!codec.I64(rank))return false;}{if(!codec.I64(source))return false;}{if(!codec.F32(confidence))return false;}return true;}
};
struct HG5PathEvent{long id,ordinal;int kind,why,net;float h4,v4,h5;
 void ZeroFields(){{id=0;}{ordinal=0;}{kind=0;}{why=0;}{net=0;}{h4=0;}{v4=0;}{h5=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(id))return false;}{if(!codec.I64(ordinal))return false;}{if(!codec.I32(kind))return false;}{if(!codec.I32(why))return false;}{if(!codec.I32(net))return false;}{if(!codec.F32(h4))return false;}{if(!codec.F32(v4))return false;}{if(!codec.F32(h5))return false;}return true;}
};
struct HG5AccountEvent{long id,ordinal;int account,kind;
 void ZeroFields(){{id=0;}{ordinal=0;}{account=0;}{kind=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(id))return false;}{if(!codec.I64(ordinal))return false;}{if(!codec.I32(account))return false;}{if(!codec.I32(kind))return false;}return true;}
};
// Portable modeled trading core. A complete strictly ordered same-ms quote group is the unit of commitment.
// Never uses historical tables, training datasets, broker APIs or Python. A failed group invalidates the core.
class HG6Core{
 HG5EarlyBank early;HG5MiddleBank middle;HG5LateBank late;HG5HoldingBank hold;
 HG5PhaseObserver v14,v15;HG5V16 v16;HG5V17 v17;HG5V19 v19;HG5V22 v22;HG5StructuralObserver structural;HG5ProxyObserver proxy;
 HG5EarlyRouter r17;HG5V20Router r20;HG5V22Router r22;HG5V23Router r23;HG5V24Router r24;HG5V25Router r25;HG5V26Router r26;
 HG5CandleState candles;HG5ResearchAccount book[12];HG5Window windows[];HG5Quote q[];int n,cap,nw,peak,na,nfree,active_slots[HG5_MAX_ACTIVE],free_slots[HG5_MAX_ACTIVE],entry_local[HG5_MAX_ACTIVE];long path_id[HG5_MAX_ACTIVE];int path_side[HG5_MAX_ACTIVE];HG5HoldingPath paths[HG5_MAX_ACTIVE];HG5Proposal pending[];
 long base,last_group,next_id,groups,observations;bool valid,started,loaded[88];
 // SECTION L1: separate actual broker path; does not affect ancestral shadow decisions.
 HG6ActualHoldingPath actual; int actual_state,actual_side,actual_px,actual_units;long actual_ms,actual_id;
 bool ActualQuote(const HG5Quote &tick,int j){
  if(actual_state==0)return true;
  if(actual_state==1&&tick.ms<actual_ms)return true;
  float c[],raw[];if(!candles.Snapshot(actual_side,c,raw))return false;
  if(actual_state==1){if(!actual.Init(hold,q,j,actual_side,base,c,actual_ms,actual_px))return false;actual_state=2;}
  return actual.Step(hold,q,j,c)>=0;
 }
 bool Stage(HG5StageEvent &o[],int st,long t,int sd,long rank,long src,float confidence=0){int k=ArraySize(o);if(ArrayResize(o,k+1)!=k+1)return false;o[k].stage=st;o[k].ms=t;o[k].side=sd;o[k].rank=rank;o[k].source=src;o[k].confidence=confidence;return true;}
 bool Path(HG5PathEvent &o[],int slot,int kind,long j){int k=ArraySize(o);if(ArrayResize(o,k+1)!=k+1)return false;o[k].id=path_id[slot];o[k].ordinal=j;o[k].kind=kind;o[k].why=paths[slot].why;o[k].net=paths[slot].net;o[k].h4=paths[slot].h4;o[k].v4=paths[slot].v4;o[k].h5=paths[slot].h5;return true;}
 bool Acct(HG5AccountEvent &o[],int k,long id,long j,int kind){int i=ArraySize(o);if(ArrayResize(o,i+1)!=i+1)return false;o[i].account=k;o[i].id=id;o[i].ordinal=j;o[i].kind=kind;return true;}
 bool Room(int count){if(count<1||count>cap)return false;if(n+count<=cap)return true;int drop=HG5Prev(q,n-1,q[n-1].ms-900000);if(drop>n-257)drop=n-257;for(int i=0;i<na;i++)if(entry_local[active_slots[i]]<drop)drop=entry_local[active_slots[i]];if(actual_state==2&&actual.EntryLocal()<drop)drop=actual.EntryLocal();if(drop<=0||n-drop+count>cap)return false;if(actual_state==2&&!actual.Shift(drop))return false;for(int i=0;i<na;i++){int k=active_slots[i];if(!paths[k].Shift(drop))return false;entry_local[k]-=drop;}for(int i=0;i<n-drop;i++)q[i]=q[i+drop];n-=drop;base+=drop;return true;}
 bool Observe(const HG5Quote &tick,HG5EarlyRow &a[],HG5EarlyRow &g[],HG5EarlyRow &b[],HG5EarlyRow &c[],HG5EarlyRow &d[],HG5EarlyRow &e[],float &S[],long &so,float &P[],long &po){
  HG5EarlyRow x;int i;
  if(!v14.Push(tick,x))return false;if(x.width){i=ArraySize(a);if(ArrayResize(a,i+1)!=i+1)return false;a[i]=x;}
  if(!v15.Push(tick,x))return false;if(x.width){i=ArraySize(g);if(ArrayResize(g,i+1)!=i+1)return false;g[i]=x;}
  if(!v16.Push(tick,x))return false;if(x.width){i=ArraySize(b);if(ArrayResize(b,i+1)!=i+1)return false;b[i]=x;}
  if(!v17.Push(tick,x))return false;if(x.width){i=ArraySize(c);if(ArrayResize(c,i+1)!=i+1)return false;c[i]=x;}
  if(!v19.Push(tick,x))return false;if(x.width){i=ArraySize(d);if(ArrayResize(d,i+1)!=i+1)return false;d[i]=x;}
  if(!v22.Push(tick,x))return false;if(x.width){i=ArraySize(e);if(ArrayResize(e,i+1)!=i+1)return false;e[i]=x;}
  bool emit=false;if(!structural.Push(tick,emit,S))return false;if(emit)so=structural.Ordinal();if(!proxy.Push(tick,emit,P))return false;if(emit)po=proxy.Ordinal();return true;
 }
 bool ProcessQuote(const HG5Quote &tick,HG5PathEvent &path_out[],HG5AccountEvent &acct_out[]){
  int j=n++;q[j]=tick;long ord=base+j;float c[],raw[];for(int k=0;k<12;k++){long closed=book[k].BeginQuote(ord,tick.ms,tick.bid,tick.ask,windows,nw);if(closed==-2)return false;if(closed>=0&&!Acct(acct_out,k,closed,ord,1))return false;}
  if(!candles.Push(tick.ms,tick.bid,tick.ask)||!ActualQuote(tick,j))return false;
  for(int i=0;i<ArraySize(pending);i++){HG5Proposal p=pending[i];if(p.t>=tick.ms||na>=HG5_MAX_ACTIVE||nfree<=0)return false;int slot=free_slots[--nfree];if(!candles.Snapshot(p.side,c,raw)||!paths[slot].Init(hold,q,j,p.side,base,c))return false;path_id[slot]=p.id;path_side[slot]=p.side;entry_local[slot]=j;active_slots[na++]=slot;if(!Path(path_out,slot,0,ord))return false;for(int k=0;k<12;k++){book[k].Proposal(p.id,p.t,p.side,windows);if(!book[k].Ready())return false;}}
  ArrayResize(pending,0);
  for(int i=0;i<na;){int slot=active_slots[i];if(!candles.Snapshot(path_side[slot],c,raw))return false;int z=paths[slot].Step(hold,q,j,c);if(z<0||z>2)return false;if(z==1){if(!Path(path_out,slot,1,ord))return false;for(int k=0;k<12;k++)book[k].Decision(path_id[slot]);}if(z==2){if(!Path(path_out,slot,2,ord))return false;observations+=paths[slot].observations;active_slots[i]=active_slots[--na];free_slots[nfree++]=slot;continue;}i++;}return true;
 }
public:
 HG6Core(){actual_state=actual_side=actual_px=actual_units=0;actual_ms=0;actual_id=-1;valid=false;started=false;for(int i=0;i<88;i++)loaded[i]=false;}
 bool Load(int id,const uchar &bytes[]){if(started||id<0||id>=88)return false;bool ok=id<11?early.Load(id,bytes):id<19?middle.Load(id-11,bytes):id<61?late.Load(id,bytes):hold.Load(id-61,bytes);loaded[id]=ok;return ok;}
 bool Start(const HG5Window &clock[],int capacity=262144){if(started||capacity<257||capacity>262144)return false;for(int i=0;i<88;i++)if(!loaded[i])return false;nw=ArraySize(clock);if(nw<=0||ArrayResize(windows,nw)!=nw||ArrayResize(q,capacity)!=capacity)return false;for(int i=0;i<nw;i++){HG5Window w=clock[i];if(w.open_ms<0||w.open_ms>w.block_ms||w.block_ms>w.flatten_ms||w.flatten_ms>w.close_ms||(i&&w.open_ms<windows[i-1].open_ms))return false;windows[i]=w;}
  int k=0;for(int l=0;l<2;l++)for(int size=0;size<3;size++)for(int on=0;on<2;on++)if(!book[k++].Reset(l?50.:500.,size>0,size==2?100:10,on!=0,10000.))return false;v15.Reset(true);cap=capacity;n=na=peak=0;nfree=HG5_MAX_ACTIVE;for(int i=0;i<nfree;i++)free_slots[i]=nfree-1-i;base=next_id=groups=observations=0;last_group=-1;ArrayResize(pending,0);started=valid=true;return true;}
 bool StepGroup(const HG5Quote &group[],HG5StageEvent &st[],HG5Proposal &intents[],HG5PathEvent &pa[],HG5AccountEvent &ac[]){
  ArrayResize(st,0);ArrayResize(intents,0);ArrayResize(pa,0);ArrayResize(ac,0);if(!valid||!started)return false;valid=false;int count=ArraySize(group);if(count<=0)return false;long t=group[0].ms;if(t<=last_group)return false;for(int i=0;i<count;i++)if(group[i].ms!=t||group[i].bid<=0||group[i].ask<group[i].bid)return false;if(!Room(count))return false;
  HG5EarlyRow a[],g[],b[],c[],d[],e[];float S[],P[];long so=-1,po=-1;
  for(int i=0;i<count;i++)if(!ProcessQuote(group[i],pa,ac)||!Observe(group[i],a,g,b,c,d,e,S,so,P,po))return false;if(n>peak)peak=n;
  HG5EarlySignal o14[],o15[],o16[],o17[];HG5ParentSignal o20[],o22[],o23[];HG5V20Context ctx20[];HG5MarginalContext ctx22[];HG5Market137 market[];HG5Market73 market25[];HG5ReserveEvent o24[],o25[],o26[];
  if(!r17.Route(early,t,a,g,b,c,o14,o15,o16,o17)||!r20.Route(middle,t,d,o17,o20,ctx20)||!r22.Route(middle,t,e,o20,o22,ctx22)||!r23.Route(late,t,ctx20,ctx22,S,so,o22,o23,market)||!r24.Route(late,t,market,o23,o24))return false;
  if(ArrayResize(market25,ArraySize(market))!=ArraySize(market))return false;for(int i=0;i<ArraySize(market);i++)if(!HG5JoinProxy(market[i],po,P,market25[i]))return false;if(!r25.Route(late,t,market25,o24,o25)||!r26.Route(late,t,market25,o25,o26))return false;
  for(int i=0;i<ArraySize(o14);i++)if(!Stage(st,0,t,o14[i].side,o14[i].rank,0))return false;for(int i=0;i<ArraySize(o15);i++)if(!Stage(st,1,t,o15[i].side,o15[i].rank,0))return false;for(int i=0;i<ArraySize(o16);i++)if(!Stage(st,2,t,o16[i].side,o16[i].rank,o16[i].source))return false;for(int i=0;i<ArraySize(o17);i++)if(!Stage(st,3,t,o17[i].side,o17[i].rank,o17[i].source))return false;
  for(int i=0;i<ArraySize(o20);i++)if(!Stage(st,4,t,o20[i].side,0,o20[i].source,o20[i].confidence))return false;for(int i=0;i<ArraySize(o22);i++)if(!Stage(st,5,t,o22[i].side,0,o22[i].source))return false;for(int i=0;i<ArraySize(o23);i++)if(!Stage(st,6,t,o23[i].side,0,o23[i].source))return false;
  for(int i=0;i<ArraySize(o24);i++)if(!Stage(st,7,t,o24[i].side,o24[i].id,(long)o24[i].replaced))return false;for(int i=0;i<ArraySize(o25);i++)if(!Stage(st,8,t,o25[i].side,o25[i].id,(long)o25[i].replaced))return false;for(int i=0;i<ArraySize(o26);i++){if(!Stage(st,9,t,o26[i].side,o26[i].id,0))return false;int k=ArraySize(pending);if(ArrayResize(pending,k+1)!=k+1||ArrayResize(intents,k+1)!=k+1)return false;HG5Proposal p;p.id=next_id++;p.t=t;p.side=o26[i].side;p.origin=o26[i].id;pending[k]=p;intents[k]=p;}
  last_group=t;groups++;valid=true;return true;
 }
 // SECTION L2: actual fill binding. A fill already behind committed history is ambiguous.
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
 bool Snapshot(int k,double &v[],long &z[])const{return valid&&k>=0&&k<12&&book[k].Snapshot(v,z);}
 bool Stats(long &z[])const{if(!valid||ArrayResize(z,8)!=8)return false;z[0]=base+n;z[1]=base;z[2]=peak;z[3]=na;z[4]=ArraySize(pending);z[5]=next_id;z[6]=groups;z[7]=observations;for(int i=0;i<na;i++)z[7]+=paths[active_slots[i]].observations;return true;}
 // Version 2 payload. Caller must validate a SHA-256 sealed envelope and model/config manifest
 // BEFORE Restore. Restore only into fresh Start() state. Never use a failed restore.
 bool Transfer(HG5StateCodec &c){
  int version=2,savedcap=cap,savednw=nw;if(!c.I32(version)||version!=2||!c.I32(savedcap)||savedcap!=cap||!c.I32(savednw)||savednw!=nw)return false;
  if(!c.I32(n)||!c.I32(peak)||!c.I32(na)||!c.I32(nfree)||!c.I64(base)||!c.I64(last_group)||!c.I64(next_id)||!c.I64(groups)||!c.I64(observations))return false;
  if(n<0||n>cap||peak<n||peak>cap||na<0||na>HG5_MAX_ACTIVE||nfree!=HG5_MAX_ACTIVE-na||base<0||next_id<0||groups<0||observations<0||(n==0&&last_group!=-1))return false;
  for(int i=0;i<nw;i++){HG5Window w=windows[i];if(!w.StateFields(c)||w.open_ms!=windows[i].open_ms||w.block_ms!=windows[i].block_ms||w.flatten_ms!=windows[i].flatten_ms||w.close_ms!=windows[i].close_ms)return false;}
  for(int i=0;i<n;i++){if(!q[i].StateFields(c)||q[i].ms<0||q[i].bid<=0||q[i].ask<q[i].bid||(i&&q[i].ms<q[i-1].ms))return false;}if(n&&q[n-1].ms!=last_group)return false;
  if(!v14.StateFields(c)||!v15.StateFields(c)||!v16.StateFields(c)||!v17.StateFields(c)||!v19.StateFields(c)||!v22.StateFields(c)||!structural.StateFields(c)||!proxy.StateFields(c)||!r17.StateFields(c)||!r20.StateFields(c)||!r22.StateFields(c)||!r23.StateFields(c)||!r24.StateFields(c)||!r25.StateFields(c)||!r26.StateFields(c)||!candles.StateFields(c))return false;
  for(int i=0;i<12;i++)if(!book[i].StateFields(c)||!book[i].Ready())return false;
  bool seen[HG5_MAX_ACTIVE];for(int i=0;i<HG5_MAX_ACTIVE;i++)seen[i]=false;
  for(int i=0;i<na;i++){if(!c.I32(active_slots[i]))return false;int k=active_slots[i];if(k<0||k>=HG5_MAX_ACTIVE||seen[k])return false;seen[k]=true;if(!c.I32(entry_local[k])||!c.I64(path_id[k])||!c.I32(path_side[k])||!paths[k].StateFields(c))return false;if(entry_local[k]<0||entry_local[k]>=n||path_id[k]<0||path_id[k]>=next_id||(path_side[k]!=1&&path_side[k]!=-1))return false;}
  for(int i=0;i<nfree;i++){if(!c.I32(free_slots[i]))return false;int k=free_slots[i];if(k<0||k>=HG5_MAX_ACTIVE||seen[k])return false;seen[k]=true;}
  int np=ArraySize(pending);if(!c.I32(np)||np<0||np>HG5_MAX_ACTIVE)return false;if(c.Reading()&&ArrayResize(pending,np)!=np)return false;for(int i=0;i<np;i++)if(!pending[i].StateFields(c)||pending[i].id<0||pending[i].id>=next_id||pending[i].t!=last_group||(pending[i].side!=1&&pending[i].side!=-1))return false;
  if(!c.I32(actual_state)||!c.I32(actual_side)||!c.I32(actual_px)||!c.I32(actual_units)||!c.I64(actual_ms)||!c.I64(actual_id)||!actual.StateFields(c))return false;
  if(actual_state<0||actual_state>2||(actual_state==0&&(actual_id!=-1||actual.Ready()))||(actual_state>0&&(actual_id<0||actual_ms<0||actual_px<=0||actual_units<=0||actual_units>100||(actual_side!=1&&actual_side!=-1)))||(actual_state==1&&(actual_ms<=last_group||actual.Ready()))||(actual_state==2&&(!actual.Validate(n,actual_side,actual_px,actual_ms)||actual_ms>last_group)))return false;
  return true;
 }
 bool ExportState(uchar &out[]){if(!valid||!started)return false;HG5StateCodec c;return c.BeginWrite()&&Transfer(c)&&c.Finish(out);}
 bool RestoreState(const uchar &in[]){if(!valid||!started||groups!=0||n!=0)return false;valid=false;HG5StateCodec c;if(!c.BeginRead(in)||!Transfer(c)||!c.Done())return false;valid=true;return true;}
};
#endif
