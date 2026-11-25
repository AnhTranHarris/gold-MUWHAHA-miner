#ifndef HG5_RESEARCH_ACCOUNT_MQH
#define HG5_RESEARCH_ACCOUNT_MQH
#include "HG5StateCodec.mqh"
#include "HG5StatePrimitives.mqh"
// A port of account_stream_stage4.py, strictly a modeled account kernel.
// No order APIs, no broker fill assumptions promoted to live execution.
class HG5ResearchAccount {
private:
 double state[12],lev;long st[17],counts[100],profit[100],first[100],gate[3];
 long active,px,ent,entms,aw,dt,last,w,p,d,j,now;int u,s,bid,ask,cap;bool clock,enabled,busy,ready;
 void Mark(const double eq,const double margin){state[2]=MathMin(state[2],eq);state[1]=MathMax(state[1],eq);double dd=state[1]-eq;state[4]=MathMax(state[4],dd);state[5]=MathMax(state[5],state[1]>0?dd/state[1]:0.0);state[9]=MathMin(state[9],eq-margin);state[10]=MathMin(state[10],eq/margin*100);state[11]=MathMax(state[11],margin);if(eq<=0)st[11]=1;}
 long Net(const int extra) const {return ((long)s*((s>0?bid:ask)-px)-1-extra)*u;}
public:
 HG5ResearchAccount(){ZeroFields();Reset(500.0,false,10,false,10000.0);}
 bool Reset(const double leverage,const bool ladder,const int maxunits,const bool useclock,const double initial){
  ready=false;if(!MathIsValidNumber(leverage)||leverage<=0||!MathIsValidNumber(initial)||initial<0||maxunits<1||maxunits>100)return false;
  lev=leverage;enabled=ladder;cap=maxunits;clock=useclock;for(int k=0;k<12;k++)state[k]=0;state[0]=initial;state[1]=initial;state[2]=initial;state[3]=initial;state[6]=initial;state[9]=1e99;state[10]=1e99;
  for(int k=0;k<17;k++)st[k]=0;for(int k=0;k<100;k++){counts[k]=0;profit[k]=0;first[k]=0;}for(int k=0;k<3;k++)gate[k]=0;
  active=-1;px=0;u=0;s=0;ent=-1;entms=0;aw=-1;dt=-1;last=-1;w=-1;p=0;d=0;j=-1;now=0;bid=0;ask=0;busy=false;ready=true;return true;
 }
 bool Ready() const {return ready;}
 // Call once per chronological quote, then each eligible proposal, then each decision at this quote.
 long BeginQuote(const long ordinal,const long ms,const int b,const int a,const HG5Window &windows[],const int nw){
  if(!ready||ordinal!=j+1||ms<0||(j>=0&&ms<now)||b<=0||a<b||nw<0||nw>ArraySize(windows)||(clock&&active>=0&&(aw<0||aw>=nw))){ready=false;return -2;}
  j=ordinal;now=ms;bid=b;ask=a;w=HG5WindowIndex(now,windows,nw);busy=(active>=0);if(!busy)return -1;
  bool due=dt>=0&&now>dt,force=clock&&now>windows[aw].flatten_ms,ending=due||force;double margin=(double)px*u/lev;double eq=state[0]+Net(ending?1:0);Mark(eq,margin);bool stop=eq<=0.5*margin&&!ending;if(!ending&&!stop)return -1;
  long net=Net(1);state[0]+=net;double bal=state[0];state[3]=MathMin(state[3],bal);state[1]=MathMax(state[1],bal);state[6]=MathMax(state[6],bal);state[7]=MathMax(state[7],state[6]-bal);state[8]=MathMax(state[8],state[6]>0?(state[6]-bal)/state[6]:0.0);
  last=j;long closed=active;if(force&&!due)gate[1]++;if(clock&&!stop&&now>=windows[aw].close_ms)gate[2]++;st[1]++;counts[u-1]++;profit[u-1]+=net;if(first[u-1]==0)first[u-1]=entms;if(u>st[12])st[12]=u;if(st[13]>0&&u<st[13])st[14]++;st[13]=u;if(net<st[15])st[15]=net;if(net>st[16])st[16]=net;if(stop)st[9]++;if(net>0){st[2]++;st[5]+=net;}else if(net<0){st[3]++;st[6]+=net;}else st[4]++;
  active=-1;dt=-1;return closed;
 }
 void Proposal(const long id,const long t,const int side,const HG5Window &windows[]){
  if(!ready||id!=p||t>=now||(side!=1&&side!=-1)){ready=false;return;}
  p++;if(clock&&(w<0||t<windows[w].open_ms||t>=windows[w].block_ms||now>=windows[w].block_ms)){gate[0]++;return;}
  st[0]++;if(active>=0||busy||j<=last){st[7]++;return;}if(state[0]<=0){st[10]++;return;}
  u=HG5LotUnits((long)state[0],enabled,cap);s=side;px=(s>0?ask:bid);double margin=(double)px*u/lev;double eq=state[0]+Net(0);
  if(eq<margin){st[8]++;last=j;return;}active=id;ent=j;entms=now;aw=w;dt=-1;Mark(eq,margin);
 }
 void Decision(const long id){if(!ready||id<0){ready=false;return;}if(active==id&&dt<0)dt=now;d++;}
 bool Snapshot(double &v[],long &k[]) const {
  if(!ready||ArrayResize(v,12)!=12||ArrayResize(k,331)!=331)return false;
  for(int i=0;i<12;i++)v[i]=state[i];for(int i=0;i<17;i++)k[i]=st[i];for(int i=0;i<100;i++){k[17+i]=counts[i];k[117+i]=profit[i];k[217+i]=first[i];}for(int i=0;i<3;i++)k[317+i]=gate[i];k[320]=active;k[321]=px;k[322]=u;k[323]=s;k[324]=ent;k[325]=aw;k[326]=dt;k[327]=p;k[328]=d;k[329]=last;k[330]=w;return true;
 }

public:
 void ZeroFields(){for(int i=0;i<12;i++){state[i]=0;}{lev=0;}for(int i=0;i<17;i++){st[i]=0;}for(int i=0;i<100;i++){counts[i]=0;}for(int i=0;i<100;i++){profit[i]=0;}for(int i=0;i<100;i++){first[i]=0;}for(int i=0;i<3;i++){gate[i]=0;}{active=0;}{px=0;}{ent=0;}{entms=0;}{aw=0;}{dt=0;}{last=0;}{w=0;}{p=0;}{d=0;}{j=0;}{now=0;}{u=0;}{s=0;}{bid=0;}{ask=0;}{cap=0;}{clock=0;}{enabled=0;}{busy=0;}{ready=0;}}
 bool StateFields(HG5StateCodec &codec){for(int i=0;i<12;i++){if(!codec.F64(state[i]))return false;}{if(!codec.F64(lev))return false;}for(int i=0;i<17;i++){if(!codec.I64(st[i]))return false;}for(int i=0;i<100;i++){if(!codec.I64(counts[i]))return false;}for(int i=0;i<100;i++){if(!codec.I64(profit[i]))return false;}for(int i=0;i<100;i++){if(!codec.I64(first[i]))return false;}for(int i=0;i<3;i++){if(!codec.I64(gate[i]))return false;}{if(!codec.I64(active))return false;}{if(!codec.I64(px))return false;}{if(!codec.I64(ent))return false;}{if(!codec.I64(entms))return false;}{if(!codec.I64(aw))return false;}{if(!codec.I64(dt))return false;}{if(!codec.I64(last))return false;}{if(!codec.I64(w))return false;}{if(!codec.I64(p))return false;}{if(!codec.I64(d))return false;}{if(!codec.I64(j))return false;}{if(!codec.I64(now))return false;}{if(!codec.I32(u))return false;}{if(!codec.I32(s))return false;}{if(!codec.I32(bid))return false;}{if(!codec.I32(ask))return false;}{if(!codec.I32(cap))return false;}{if(!codec.Flag(clock))return false;}{if(!codec.Flag(enabled))return false;}{if(!codec.Flag(busy))return false;}{if(!codec.Flag(ready))return false;}return true;}
};
#endif
