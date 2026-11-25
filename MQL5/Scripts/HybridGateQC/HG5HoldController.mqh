#ifndef HG5_HOLD_CONTROLLER_MQH
#define HG5_HOLD_CONTROLLER_MQH
#include "HG5StateCodec.mqh"
#include "HG5HoldEvents.mqh"
#include "HG5ConditionalPartition.mqh"
#include "HG5PackedCore.mqh"
// All 27 selected holding models in the frozen binding order (NOT archive order after the loaded-only head).
class HG5HoldingBank {
private:
 HG5PackedCore models[27]; bool loaded[27];
public:
 HG5HoldingBank(){for(int i=0;i<27;i++)loaded[i]=false;}
 bool Load(const int id,const uchar &bytes[]){
  int dims[27]={136,136,138,138,140,140,142,142,216,216,218,218,220,220,222,222,210,92,92,98,116,116,116,123,60,133,133};
  if(id<0||id>=27)return false;loaded[id]=false;
  if(!models[id].LoadBytes(bytes)||models[id].Features()!=dims[id]||models[id].Outputs()!=1)return false;
  loaded[id]=true;return true;
 }
 bool Ready() const {for(int i=0;i<27;i++)if(!loaded[i])return false;return true;}
 bool Score(const int id,const float &x[],const int n,double &score) const {
  if(id<0||id>=27||!loaded[id]||n!=models[id].Features()||ArraySize(x)<n)return false;
  float a[];double y[];if(ArrayResize(a,n)!=n)return false;for(int k=0;k<n;k++)a[k]=x[k];
  if(!models[id].Predict(a,y)||ArraySize(y)!=1)return false;score=y[0];return MathIsValidNumber(score);
 }
};
bool HG5HoldingPriors(const HG5HoldingBank &bank,const float &rx[],const float &c[],float &h4,float &v4,float &h5){
 if(ArraySize(rx)!=136||ArraySize(c)!=72||!bank.Ready())return false;
 float x[],f5[],p[8];if(ArrayResize(x,224)!=224||ArrayResize(f5,210)!=210)return false;
 for(int i=0;i<136;i++)x[i]=rx[i];double u,w;float h,v;
 if(!bank.Score(0,x,136,u)||!bank.Score(1,x,136,w))return false;h=(float)u;v=(float)w;x[136]=p[0]=h;x[137]=p[1]=v;
 for(int k=1;k<=3;k++){if(!bank.Score(2*k,x,136+2*k,u)||!bank.Score(2*k+1,x,136+2*k,w))return false;h=HG5MinF(30.f,HG5MaxF(0.f,h+(float)u));v=v+(float)w;x[136+2*k]=p[2*k]=h;x[137+2*k]=p[2*k+1]=v;}
 for(int i=0;i<72;i++)x[136+i]=c[i];for(int i=0;i<8;i++)x[208+i]=p[i];
 for(int k=0;k<4;k++){if(!bank.Score(8+2*k,x,216+2*k,u)||!bank.Score(9+2*k,x,216+2*k,w))return false;h=HG5MinF(30.f,HG5MaxF(0.f,h+(float)u));v=v+(float)w;if(k<3){x[216+2*k]=h;x[217+2*k]=v;}}
 h4=h;v4=v;for(int i=0;i<208;i++)f5[i]=x[i];f5[208]=h;f5[209]=v;if(!bank.Score(16,f5,210,u))return false;h5=h+(float)u*.001f;return MathIsValidNumber(h5)&&MathIsValidNumber(v4);
}
float HG5NonnegativeExp(double x){return (float)HG5MaxD(0.,MathExpm1(x));}
int HG5HoldAction(const HG5HoldingBank &bank,HG5Hold &st,const float &f[],const float &c[]){
 if(ArraySize(f)!=24||ArraySize(c)!=72)return -1;
 float x[],xs[];if(ArrayResize(x,98)!=98||ArrayResize(xs,92)!=92)return -1;for(int i=0;i<24;i++)x[i]=f[i];for(int i=0;i<72;i++)x[24+i]=c[i];int k=0;for(int i=0;i<18;i++)xs[k++]=x[i];xs[k++]=x[22];xs[k++]=x[23];for(int i=24;i<96;i++)xs[k++]=x[i];
 double u,w;if(!bank.Score(17,xs,92,u)||!bank.Score(18,xs,92,w))return -1;float g=HG5NonnegativeExp(u),r=HG5NonnegativeExp(w);x[96]=g;x[97]=r;if(!bank.Score(19,x,98,u))return -1;float prob=(float)u,m=f[1],peak=f[2],slack=8.f;float dist=HG5MaxF(HG5MaxF(2.f,1.5f*f[8]),HG5MaxF(.2f*f[10],(g+slack)/(1.f+r/(g+25.f))));if(peak>HG5MaxF(5.f,f[10]*.25f))st.floor=HG5MaxF(st.floor,peak-dist);bool conf=prob>=.8f;int why=0;if(conf&&peak>0&&m<=st.floor&&r>=g)why=3;else if(conf&&m>=0&&g<=slack&&r>=g)why=2;else if(conf&&m<0&&r>=g+slack&&g<=slack)why=4;if(!why&&(f[18]<=0.f||f[0]>=29.995f))why=1;return why;
}
int HG5RenewAction(const HG5HoldingBank &bank,HG5Renew &st,const float &f[],const float &c[],const int kind){
 if(ArraySize(f)!=48||ArraySize(c)!=72)return -1;
 float x[],xs[];if(ArrayResize(x,123)!=123||ArrayResize(xs,116)!=116)return -1;for(int i=0;i<48;i++)x[i]=f[i];for(int i=0;i<72;i++)x[48+i]=c[i];int k=0;for(int i=0;i<42;i++)xs[k++]=x[i];for(int i=46;i<120;i++)xs[k++]=x[i];
 double u,w,z;if(!bank.Score(20,xs,116,u)||!bank.Score(21,xs,116,w)||!bank.Score(22,xs,116,z))return -1;float premium=(float)u,gain=HG5NonnegativeExp(w),risk=HG5NonnegativeExp(z);x[120]=premium;x[121]=gain;x[122]=risk;if(!bank.Score(23,x,123,u))return -1;float prob=(float)u,slack=15.f,m=f[1],peak=f[2];float dist=HG5MaxF(HG5MaxF(2.f,1.2f*f[8]),HG5MaxF(.2f*f[9],(gain+slack)/(1.f+risk/(gain+25.f))));if(peak>HG5MaxF(5.f,f[9]*.25f))st.floor=HG5MaxF(st.floor,peak-dist);float edge=m+premium;bool conf=prob>=.8f,near_value=edge>=f[43]-slack;int why=0;if(conf&&peak>0&&edge<=st.floor&&risk>=gain)why=3;else if(conf&&m>=0&&near_value&&gain<=slack&&risk>=gain)why=2;else if(conf&&m<0&&risk>=gain+slack&&gain<=slack)why=4;else if(conf&&near_value&&gain<=slack)why=6;if(!why&&f[44]<=0)why=1;if(!why&&(kind&4))why=5;return why;
}
int HG5HazardAction(const HG5HoldingBank &bank,const float &f[],const float &c[]){
 if(ArraySize(f)!=60||ArraySize(c)!=72)return -1;double u,w;if(!bank.Score(24,f,60,u))return -1;float sc=(float)u;if(sc<.45f)return 0;
 float x[];if(ArrayResize(x,133)!=133)return -1;for(int i=0;i<60;i++)x[i]=f[i];for(int i=0;i<72;i++)x[60+i]=c[i];x[132]=sc;if(!bank.Score(25,x,133,u)||!bank.Score(26,x,133,w))return -1;float p=(float)u,r=HG5MaxF(0.f,(float)MathExpm1((double)(float)w));return HG5Partition(x,p,r);
}
int HG5Release(const int ra,const int rb,const int rc){if(ra<0||rb<0||rc<0)return -1;int release=ra;bool sa=ra>1&&ra!=5,sb=rb>1&&rb!=5;if(rb&&(!ra||(sb&&!sa)))release=rb+10;if(rc&&(!release||release%10==1))release=26;return release;}
// Path is a modeled decision lifecycle. No orders. All indices local to retained tape.
// Result -1 error, 0 active, 1 newly decided, 2 filled strictly later, 3 already complete.
class HG5HoldingPath {
private:
 HG5Hold h;HG5Renew r;HG5Hazard a;int e,s,next;bool ready,complete;long dms;
public:
 int decision,exit,why,net;float h4,v4,h5;long observations;
 HG5HoldingPath(){ZeroFields();ready=false;complete=false;}
 bool Init(const HG5HoldingBank &bank,const HG5Quote &q[],const int j,const int side,const long base,const float &candles[]){
  ready=false;complete=false;decision=-1;exit=-1;why=0;net=0;observations=0;dms=-1;if(j<=0||j>=ArraySize(q)||(side!=1&&side!=-1))return false;
  float rx[];if(!HG5RXFeatures(q,j+1,j,side,j-1,base,rx)||!HG5HoldingPriors(bank,rx,candles,h4,v4,h5))return false;
  e=j;s=side;next=j;h.Init(q,j,s,h5,v4);r.Init(q,j,s,h5,v4);a.Init(q,j,s,30.f,v4);ready=true;return true;
 }
 int Step(const HG5HoldingBank &bank,const HG5Quote &q[],const int j,const float &candles[]){
  if(!ready)return -1;if(complete)return 3;if(j!=next||j>=ArraySize(q)||j<e||q[j].ms<q[j-1].ms||q[j].bid<=0||q[j].ask<q[j].bid||ArraySize(candles)!=72){ready=false;return -1;}next++;
  if(decision>=0){if(q[j].ms>dms){exit=j;net=HG5Mark(q,j,s,h.px);complete=true;return 2;}return 0;}
  float f[],g[],z[];if(ArrayResize(f,24)!=24||ArrayResize(g,48)!=48||ArrayResize(z,60)!=60){ready=false;return -1;}
  int kind=0,k2=0;bool ea=h.Step(q,j,f),eb=r.Step(q,j,g,kind),ec=a.Step(q,j,z,k2);int ra=ea?HG5HoldAction(bank,h,f,candles):0,rb=eb?HG5RenewAction(bank,r,g,candles,kind):0,rc=ec?HG5HazardAction(bank,z,candles):0;observations+=(int)ea+(int)eb+(int)ec;int release=HG5Release(ra,rb,rc);if(release<0){ready=false;return -1;}if(release){decision=j;dms=q[j].ms;why=release;return 1;}return 0;
 }
 // A ring shift may never retire the entry while the path remains pending.
 bool Shift(const int n){if(!ready||complete||n<0||n>e)return false;e-=n;next-=n;if(decision>=0)decision-=n;h.e-=n;h.pk-=n;h.tk-=n;r.e-=n;r.pk-=n;r.lk-=n;a.e-=n;a.pk-=n;a.lk-=n;for(int i=0;i<4;i++){r.w[i]-=n;a.w[i]-=n;}return true;}

public:
 void ZeroFields(){{h.ZeroFields();}{r.ZeroFields();}{a.ZeroFields();}{e=0;}{s=0;}{next=0;}{ready=0;}{complete=0;}{dms=0;}{decision=0;}{exit=0;}{why=0;}{net=0;}{h4=0;}{v4=0;}{h5=0;}{observations=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!h.StateFields(codec))return false;}{if(!r.StateFields(codec))return false;}{if(!a.StateFields(codec))return false;}{if(!codec.I32(e))return false;}{if(!codec.I32(s))return false;}{if(!codec.I32(next))return false;}{if(!codec.Flag(ready))return false;}{if(!codec.Flag(complete))return false;}{if(!codec.I64(dms))return false;}{if(!codec.I32(decision))return false;}{if(!codec.I32(exit))return false;}{if(!codec.I32(why))return false;}{if(!codec.I32(net))return false;}{if(!codec.F32(h4))return false;}{if(!codec.F32(v4))return false;}{if(!codec.F32(h5))return false;}{if(!codec.I64(observations))return false;}return true;}
};
#endif
