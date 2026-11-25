#ifndef HG6_ACTUAL_HOLDING_MQH
#define HG6_ACTUAL_HOLDING_MQH
#include "HG5HoldController.mqh"
// SECTION H1: derived actual-fill HOLD event; formula body generated from HG5Hold.
// Only age anchor is changed. Market observations are never manufactured.
struct HG6ActualHold {
long fill_ms;
int e;int s;int px;float due;float v;int peak;int trough;int pk;int tk;int old;int anchor;int turn;int sign;double travel;double noise;double ema;double under;double above;long last;bool first;bool done;float floor;
void Init(const HG5Quote &q[],int e_,int s_,float h_,float v_){peak=-1000000;trough=1000000;old=0;anchor=0;turn=0;sign=0;travel=0;noise=0;ema=100;under=0;above=0;first=true;done=false;floor=-1e9f;e=e_;s=s_;px=s>0?q[e].ask:q[e].bid;due=HG5MaxF(0.f,h_-.008f);v=v_;pk=e;tk=e;last=q[e].ms-2000;}
bool Step(const HG5Quote &q[],int j,float &f[]){if(done)return false;bool emit=false;long age_ms=q[j].ms-fill_ms;float age=age_ms*.001f;int mark=s*((s>0?q[j].bid:q[j].ask)-px)-2;int spread=q[j].ask-q[j].bid; if(j>e){int ch=mark-old,sg=(ch>0)-(ch<0);double dt=q[j].ms-q[j-1].ms;travel+=HG5AbsI(ch);noise=.82*noise+.18*HG5AbsI(ch);if(dt>0)ema=.85*ema+.15*HG5MinD(2000.,dt);under+=dt*(old<0);above+=dt*(old>0);if(sg&&sign&&sg!=sign)turn++;if(sg)sign=sg;}old=mark;if(mark>peak){peak=mark;pk=j;}if(mark<trough){trough=mark;tk=j;}
 bool close=HG5AbsF(age-due)<=.25f;bool guard=age>=29.995f;bool crossing=age>=due&&first;bool move=q[j].ms-last>=2000&&HG5AbsI(mark-anchor)>=30;bool periodic=q[j].ms-last>=3000; if(close||guard||crossing||move||periodic||j==e){emit=true;{ f[0]=age;f[1]=mark;f[2]=peak;f[3]=trough;f[4]=peak-mark;f[5]=mark-trough;f[6]=(q[j].ms-q[pk].ms)*.001f;f[7]=(q[j].ms-q[tk].ms)*.001f;f[8]=noise;f[9]=ema;f[10]=spread;f[11]=travel;f[12]=mark/(travel+1);f[13]=under/(age_ms+1);f[14]=above/(age_ms+1);f[15]=turn;f[16]=j-e+1;f[17]=s;f[18]=due-age;f[19]=v-mark;f[20]=v;f[21]=due;f[22]=s*((s>0?q[j].bid:q[j].ask)-(s>0?q[HG5MaxI(e,j-3)].bid:q[HG5MaxI(e,j-3)].ask));f[23]=s*((s>0?q[j].bid:q[j].ask)-(s>0?q[HG5MaxI(e,j-8)].bid:q[HG5MaxI(e,j-8)].ask));}last=q[j].ms;anchor=mark;}if(crossing)first=false;done=guard;return emit;}

 void ZeroFields(){fill_ms=0;{e=0;}{s=0;}{px=0;}{due=0;}{v=0;}{peak=0;}{trough=0;}{pk=0;}{tk=0;}{old=0;}{anchor=0;}{turn=0;}{sign=0;}{travel=0;}{noise=0;}{ema=0;}{under=0;}{above=0;}{last=0;}{first=0;}{done=0;}{floor=0;}}
 bool StateFields(HG5StateCodec &codec){if(!codec.I64(fill_ms))return false;{if(!codec.I32(e))return false;}{if(!codec.I32(s))return false;}{if(!codec.I32(px))return false;}{if(!codec.F32(due))return false;}{if(!codec.F32(v))return false;}{if(!codec.I32(peak))return false;}{if(!codec.I32(trough))return false;}{if(!codec.I32(pk))return false;}{if(!codec.I32(tk))return false;}{if(!codec.I32(old))return false;}{if(!codec.I32(anchor))return false;}{if(!codec.I32(turn))return false;}{if(!codec.I32(sign))return false;}{if(!codec.F64(travel))return false;}{if(!codec.F64(noise))return false;}{if(!codec.F64(ema))return false;}{if(!codec.F64(under))return false;}{if(!codec.F64(above))return false;}{if(!codec.I64(last))return false;}{if(!codec.Flag(first))return false;}{if(!codec.Flag(done))return false;}{if(!codec.F32(floor))return false;}return true;}
};
int HG6ActualHoldAction(const HG5HoldingBank &bank,HG6ActualHold &st,const float &f[],const float &c[]){
 if(ArraySize(f)!=24||ArraySize(c)!=72)return -1;
 float x[],xs[];if(ArrayResize(x,98)!=98||ArrayResize(xs,92)!=92)return -1;for(int i=0;i<24;i++)x[i]=f[i];for(int i=0;i<72;i++)x[24+i]=c[i];int k=0;for(int i=0;i<18;i++)xs[k++]=x[i];xs[k++]=x[22];xs[k++]=x[23];for(int i=24;i<96;i++)xs[k++]=x[i];
 double u,w;if(!bank.Score(17,xs,92,u)||!bank.Score(18,xs,92,w))return -1;float g=HG5NonnegativeExp(u),r=HG5NonnegativeExp(w);x[96]=g;x[97]=r;if(!bank.Score(19,x,98,u))return -1;float prob=(float)u,m=f[1],peak=f[2],slack=8.f;float dist=HG5MaxF(HG5MaxF(2.f,1.5f*f[8]),HG5MaxF(.2f*f[10],(g+slack)/(1.f+r/(g+25.f))));if(peak>HG5MaxF(5.f,f[10]*.25f))st.floor=HG5MaxF(st.floor,peak-dist);bool conf=prob>=.8f;int why=0;if(conf&&peak>0&&m<=st.floor&&r>=g)why=3;else if(conf&&m>=0&&g<=slack&&r>=g)why=2;else if(conf&&m<0&&r>=g+slack&&g<=slack)why=4;if(!why&&(f[18]<=0.f||f[0]>=29.995f))why=1;return why;
}
// SECTION H2: separate broker-confirmed path. No modeled close is a broker fill.
class HG6ActualHoldingPath {
 HG6ActualHold h; HG5Renew r; HG5Hazard a; int e,s,next;
 bool ready; long confirmed_ms; int confirmed_px,why;
 float h4,v4,h5;
 public:
 HG6ActualHoldingPath(){Reset();}
 void Reset(){h.ZeroFields();r.ZeroFields();a.ZeroFields();e=s=next=0;ready=false;confirmed_ms=0;confirmed_px=why=0;h4=v4=h5=0;}
 // The prior anchor is the last unambiguous observation at or before the fill.
 // The first holding observation is at or after fill; no future candle enters priors.
 bool InitAsOf(const HG5HoldingBank &bank,const HG5Quote &q[],int n,int anchor,int j,int side,long base,const float &candles[],long fill_ms,int fill_px){
  Reset();if(anchor<=0||j<anchor||j>anchor+1||j>=n||n>ArraySize(q)||(side!=1&&side!=-1)||fill_px<=0||q[anchor].ms>fill_ms||q[j].ms<fill_ms)return false;
  if(j==anchor&&q[j].ms!=fill_ms)return false;
  if(j!=anchor&&q[j].ms<=fill_ms)return false;
  float rx[];if(!HG5RXFeatures(q,anchor+1,anchor,side,anchor-1,base,rx)||!HG5HoldingPriors(bank,rx,candles,h4,v4,h5))return false;
  e=j;s=side;next=j;confirmed_ms=fill_ms;confirmed_px=fill_px;
  h.Init(q,j,s,h5,v4);r.Init(q,j,s,h5,v4);a.Init(q,j,s,30.f,v4);
  h.px=fill_px;h.fill_ms=fill_ms;h.last=fill_ms-2000;r.px=fill_px;r.t0=fill_ms;r.last=fill_ms-1000;a.px=fill_px;a.t0=fill_ms;a.last=fill_ms-1000;
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
