#ifndef HG5_STATE_PRIMITIVES_MQH
#define HG5_STATE_PRIMITIVES_MQH
#include "HG5StateCodec.mqh"
// Offline candidate. Source-exact valid-input arithmetic; never sends orders.
// Host tests use 64-bit long. Actual MetaEditor compilation is pending.
struct HG5Window { long open_ms,block_ms,flatten_ms,close_ms; 
 void ZeroFields(){{open_ms=0;}{block_ms=0;}{flatten_ms=0;}{close_ms=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(open_ms))return false;}{if(!codec.I64(block_ms))return false;}{if(!codec.I64(flatten_ms))return false;}{if(!codec.I64(close_ms))return false;}return true;}
};
enum HG5ClockAction { HG5_BLOCK=0,HG5_TRADE=1,HG5_FLATTEN=2,HG5_DRAIN=3,HG5_DRAIN_CANCEL_PENDING=4 };
int HG5WindowIndex(const long now,const HG5Window &windows[],const int n){
 if(n<0||n>ArraySize(windows))return -1;int lo=0,hi=n;while(lo<hi){int m=lo+(hi-lo)/2;if(windows[m].open_ms<=now)lo=m+1;else hi=m;}return lo-1;
}
int HG5Clock(const long now,const bool position,const bool pending,const bool broker_open,const bool clock_valid,const bool enabled,const bool overdue,const HG5Window &windows[],const int n){
 if(overdue||!clock_valid||n<0||n>ArraySize(windows))return position||pending?HG5_FLATTEN:HG5_BLOCK;
 if(!enabled)return broker_open?HG5_TRADE:HG5_BLOCK;
 int i=HG5WindowIndex(now,windows,n);
 if(i<0||now>=windows[i].close_ms||now>=windows[i].flatten_ms)return position||pending?HG5_FLATTEN:HG5_BLOCK;
 if(now>=windows[i].block_ms)return pending?HG5_DRAIN_CANCEL_PENDING:HG5_DRAIN;
 return broker_open?HG5_TRADE:HG5_BLOCK;
}
int HG5LotUnits(const long balance,const bool enabled,const int cap){
 if(cap<1||cap>100)return -1; // invalid configuration, not an executable volume
 if(balance<=0)return 0;if(!enabled)return 1;
 long n=1+balance/500000;return (int)(n<cap?n:cap);
}
struct HG5Bar { long key; double o,h,l,c; long n; 
 void ZeroFields(){{key=0;}{o=0;}{h=0;}{l=0;}{c=0;}{n=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(key))return false;}{if(!codec.F64(o))return false;}{if(!codec.F64(h))return false;}{if(!codec.F64(l))return false;}{if(!codec.F64(c))return false;}{if(!codec.I64(n))return false;}return true;}
};
struct HG5Series { HG5Bar cur; HG5Bar hist[3]; 
 void ZeroFields(){{cur.ZeroFields();}for(int i=0;i<3;i++){hist[i].ZeroFields();}}
 bool StateFields(HG5StateCodec &codec){{if(!cur.StateFields(codec))return false;}for(int i=0;i<3;i++){if(!hist[i].StateFields(codec))return false;}return true;}
};
class HG5CandleState {
private:
 HG5Series a[6];long last_ms,count;int horizons[6];
 void ClearBar(HG5Bar &b){b.key=-1;b.o=0;b.h=0;b.l=0;b.c=0;b.n=0;}
 void PushBar(HG5Series &s,const long k,const double v){
  if(s.cur.key!=k){if(s.cur.n){s.hist[2]=s.hist[1];s.hist[1]=s.hist[0];s.hist[0]=s.cur;}s.cur.key=k;s.cur.o=v;s.cur.h=v;s.cur.l=v;s.cur.c=v;s.cur.n=1;}
  else{s.cur.h=MathMax(s.cur.h,v);s.cur.l=MathMin(s.cur.l,v);s.cur.c=v;s.cur.n++;}
 }
public:
 HG5CandleState(){ZeroFields();Reset();}
 void Reset(){last_ms=0;count=0;horizons[0]=1000;horizons[1]=5000;horizons[2]=15000;horizons[3]=60000;horizons[4]=300000;horizons[5]=900000;for(int k=0;k<6;k++){ClearBar(a[k].cur);for(int j=0;j<3;j++)ClearBar(a[k].hist[j]);}}
 bool Push(const long ms,const int bid,const int ask){if(ms<0||bid<=0||ask<bid||(count>0&&ms<last_ms))return false;double v=((double)bid+(double)ask)*0.5;for(int k=0;k<6;k++)PushBar(a[k],ms/horizons[k],v);last_ms=ms;count++;return true;}
 long Count() const {return count;}
 long LastMs() const {return last_ms;}
 bool Snapshot(const int side,float &out[],float &raw[]) const {
  if(count<=0||(side!=1&&side!=-1)||ArrayResize(out,72)!=72||ArrayResize(raw,42)!=42)return false;
  for(int k=0;k<6;k++){
   HG5Bar b=a[k].cur,p=a[k].hist[0],r=a[k].hist[2];double atr=0;int nc=0;
   for(int j=0;j<3;j++){HG5Bar u=a[k].hist[j];if(u.n){double pc=u.o;if(j<2&&a[k].hist[j+1].n)pc=a[k].hist[j+1].c;atr+=MathMax(MathMax(u.h-u.l,MathAbs(u.h-pc)),MathAbs(u.l-pc));nc++;}}
   atr=nc?atr/nc:b.h-b.l;double rng=b.h-b.l,den=atr+1;int i=12*k;
   out[i]=(float)(side*(b.c-b.o)/den);out[i+1]=(float)(rng/den);out[i+2]=(float)((side>0?b.c-b.l:b.h-b.c)/(rng+1));
   out[i+3]=(float)((side>0?b.h-MathMax(b.o,b.c):MathMin(b.o,b.c)-b.l)/den);out[i+4]=(float)((side>0?MathMin(b.o,b.c)-b.l:b.h-MathMax(b.o,b.c))/den);
   out[i+5]=(float)(p.n?side*(p.c-p.o)/den:0);out[i+6]=(float)(p.n?(p.h-p.l)/den:0);out[i+7]=(float)(r.n?side*(b.c-r.c)/den:0);
   out[i+8]=(float)atr;out[i+9]=(float)b.n;out[i+10]=(float)(last_ms%horizons[k])/(float)horizons[k];out[i+11]=(float)(p.n?side*(b.c-p.c)/den:0);
   int j=k*7;raw[j]=(float)b.o;raw[j+1]=(float)b.h;raw[j+2]=(float)b.l;raw[j+3]=(float)b.c;raw[j+4]=(float)b.n;raw[j+5]=(float)atr;raw[j+6]=(float)(p.n?p.c:b.o);
  }return true;
 }

public:
 void ZeroFields(){for(int i=0;i<6;i++){a[i].ZeroFields();}{last_ms=0;}{count=0;}for(int i=0;i<6;i++){horizons[i]=0;}}
 bool StateFields(HG5StateCodec &codec){for(int i=0;i<6;i++){if(!a[i].StateFields(codec))return false;}{if(!codec.I64(last_ms))return false;}{if(!codec.I64(count))return false;}for(int i=0;i<6;i++){if(!codec.I32(horizons[i]))return false;}return true;}
};
struct HG5ReserveEvent { long t,id; int side; bool replaced; 
 void ZeroFields(){{t=0;}{id=0;}{side=0;}{replaced=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(t))return false;}{if(!codec.I64(id))return false;}{if(!codec.I32(side))return false;}{if(!codec.Flag(replaced))return false;}return true;}
};
// One pending anchor. The caller presents parent events first at each timestamp,
// then release candidates grouped by anchor id; HG5ReleaseChoice reduces scores.
struct HG5ReleaseChoice { bool present; int side; double utility; 
 void ZeroFields(){{present=0;}{side=0;}{utility=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.Flag(present))return false;}{if(!codec.I32(side))return false;}{if(!codec.F64(utility))return false;}return true;}
};
void HG5ChooseRelease(HG5ReleaseChoice &c,const int side,const double gain,const double loss,const bool float32_scores){if(gain>=0&&loss<=1){double u=float32_scores?(double)(float)(gain-loss):gain-loss;if(!c.present||u>c.utility){c.present=true;c.side=side;c.utility=u;}}}
class HG5Reservation {
private:
 long h,minute,last,pt,pid,res,released,expired,blocked;int used,ps;bool pending;
 void Expire(){if(pending){pending=false;expired++;}}
 void CheckTime(const long t){if(pending&&(t>pt+h||t/60000!=pt/60000))Expire();}
public:
 HG5Reservation(){ZeroFields();Reset(24000);}
 void Reset(const long horizon){h=horizon;minute=-1;last=-1000000000000000000;pt=0;pid=0;ps=0;used=0;res=0;released=0;expired=0;blocked=0;pending=false;}
 bool Parent(const long t,const long id,const int side,const bool anchor,HG5ReserveEvent &out){
  CheckTime(t);Expire();long m=t/60000;if(minute!=m){minute=m;used=0;}
  if(anchor&&used==0){pending=true;pt=t;pid=id;ps=side;res++;return false;}
  if(used>=2||(last>=0&&last/60000==m&&t-last<3000)){blocked++;return false;}
  used++;last=t;out.t=t;out.id=id;out.side=side;out.replaced=false;return true;
 }
 bool Release(const long t,const long id,const int side,HG5ReserveEvent &out){
  CheckTime(t);if(!pending||pid!=id)return false;long m=t/60000;
  if(minute==m&&(used>=2||t-last<3000))return false;
  if(minute!=m){minute=m;used=0;}out.t=t;out.id=id;out.side=side;out.replaced=(t!=pt||side!=ps);pending=false;released++;used++;last=t;return true;
 }
 void Cutoff(const long t){CheckTime(t);}
 bool State(long &v[]) const {if(ArrayResize(v,12)!=12)return false;v[0]=h;v[1]=pending?1:0;v[2]=pending?pid:-1;v[3]=pending?pt:-1;v[4]=pending?ps:0;v[5]=minute;v[6]=used;v[7]=last;v[8]=res;v[9]=released;v[10]=expired;v[11]=blocked;return true;}

public:
 void ZeroFields(){{h=0;}{minute=0;}{last=0;}{pt=0;}{pid=0;}{res=0;}{released=0;}{expired=0;}{blocked=0;}{used=0;}{ps=0;}{pending=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(h))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(last))return false;}{if(!codec.I64(pt))return false;}{if(!codec.I64(pid))return false;}{if(!codec.I64(res))return false;}{if(!codec.I64(released))return false;}{if(!codec.I64(expired))return false;}{if(!codec.I64(blocked))return false;}{if(!codec.I32(used))return false;}{if(!codec.I32(ps))return false;}{if(!codec.Flag(pending))return false;}return true;}
};
#endif
