#ifndef HG5_EARLY_ROUTING
#define HG5_EARLY_ROUTING
#include "HG5StateCodec.mqh"
#include "HG5EarlyObservers.mqh"
#include "HG5EarlyMaps.mqh"
#include "HG5PackedCore.mqh"
// Source-exact V14/V15F/V16/V17B decisions. Caller closes same-ms group before Route.
// No live orders. Rows are emitted by the corresponding frozen quote observers.
struct HG5EarlySignal{long ms;int side,rank,source;
 void ZeroFields(){{ms=0;}{side=0;}{rank=0;}{source=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(ms))return false;}{if(!codec.I32(side))return false;}{if(!codec.I32(rank))return false;}{if(!codec.I32(source))return false;}return true;}
};
class HG5EarlyBank{
 HG5PackedCore m[11];bool loaded[11];
public:
 HG5EarlyBank(){for(int i=0;i<11;i++)loaded[i]=false;}
 bool Load(int i,const uchar &bytes[]){int dim[11]={20,20,27,27,33,33,30,30,33,33,33},out[11]={3,3,1,1,1,1,3,3,1,3,3};if(i<0||i>=11)return false;loaded[i]=false;loaded[i]=m[i].LoadBytes(bytes)&&m[i].Features()==dim[i]&&m[i].Outputs()==out[i];return loaded[i];}
 bool Ready()const{for(int i=0;i<11;i++)if(!loaded[i])return false;return true;}
 bool Score(int i,const float &x[],double &y[])const{return i>=0&&i<11&&loaded[i]&&m[i].Predict(x,y);}
};
bool HG5MapEarly(const HG5EarlyRow &r,const HG5EarlyRow &grid,const int &idx[],const int n,int side,int rank,double a,double b,float &x[]){
 if(ArrayResize(x,n)!=n)return false;for(int i=0;i<n;i++){int k=idx[i];double v=0;if(k>=100){if(k-100>=grid.width)return false;v=grid.x[k-100];}else if(k>=0){if(k>=r.width)return false;v=r.x[k];}else if(k==-1)v=(r.ms/3600000)%24;else if(k==-2)v=(r.ms/86400000+3)%7;else if(k==-3)v=side;else if(k==-4)v=rank;else if(k==-5)v=a;else if(k==-6)v=b;else return false;x[i]=(float)v;}return true;
}
// Preserve stable source order on ties, phase-first V14; V16/V17 own source before fallback.
class HG5EarlyRouter{
 HG5EarlyRow grid;bool grid_ready,valid;long minute16,minute17,last17,last_group;bool seen0,seen1;int count17;
 bool Add(HG5EarlySignal &dst[],long t,int side,int rank,int source){int n=ArraySize(dst);if(ArrayResize(dst,n+1)!=n+1)return false;dst[n].ms=t;dst[n].side=side;dst[n].rank=rank;dst[n].source=source;return true;}
 bool Role16(long t,int role,float prob,int source){long m=t/60000;if(m!=minute16){minute16=m;seen0=seen1=false;}if((role==0&&seen0)||(role==1&&seen1)||(source==0&&(double)prob<.45))return false;if(role==0)seen0=true;else seen1=true;return true;}
 bool Role17(long t,int source,int fallback_rank,int &rank){long m=t/60000;if(m!=minute17){minute17=m;count17=0;last17=-1000000000000000000;}if(count17>=2||(count17==1&&t-last17<3000))return false;if(source==1&&count17==1&&fallback_rank!=1)return false;rank=count17;return true;}
public:
 HG5EarlyRouter(){ZeroFields();Reset();}
 void Reset(){grid_ready=false;valid=true;grid.width=0;minute16=minute17=-1;last17=-1000000000000000000;last_group=-1;seen0=seen1=false;count17=0;}
 bool Route(const HG5EarlyBank &bank,const long t,const HG5EarlyRow &a[],const HG5EarlyRow &g[],const HG5EarlyRow &b[],const HG5EarlyRow &c[],HG5EarlySignal &o14[],HG5EarlySignal &o15[],HG5EarlySignal &o16[],HG5EarlySignal &o17[]){
  ArrayResize(o14,0);ArrayResize(o15,0);ArrayResize(o16,0);ArrayResize(o17,0);if(!valid||t<=last_group||!bank.Ready())return false;valid=false;last_group=t;
  for(int i=0;i<ArraySize(g);i++){if(g[i].ms!=t||g[i].width!=28)return false;grid=g[i];grid_ready=true;}
  float x[];double y[],z[];
  for(int role=0;role<2;role++)for(int i=0;i<ArraySize(a);i++){
   if(a[i].ms!=t||a[i].width!=19||a[i].kind<0||a[i].kind>1)return false;if(a[i].kind!=role)continue;
   if(!HG5MapEarly(a[i],grid,HG5_MAP_V14,20,0,role,0,0,x)||!bank.Score(role,x,y))return false;
   double p=MathMax(1e-9,MathMin(1.-1e-9,1.-y[0])),score=MathLog(p/(1.-p))-(role==0?2.2:-.15)*MathLog(MathMax(a[i].x[3],100.)/500.);
   if(score<(role==0?.4962051736357207:-.35373151534483405))continue;int sd=(y[1]>=y[2]?1:-1);if(!Add(o14,t,sd,role,0))return false;
   if(!grid_ready||t-grid.ms<0||t-grid.ms>6000||!HG5MapEarly(grid,grid,HG5_MAP_V15_HAZARD,27,0,0,0,0,x)||!bank.Score(2,x,y)||!bank.Score(3,x,z))return false;
   double p1=y[0],p2=z[0];if(!HG5MapEarly(a[i],grid,HG5_MAP_V15_SIDE,33,sd,role,p1,p2,x)||!bank.Score(4+role,x,y)||!Add(o15,t,y[0]>=.5?1:-1,role,0))return false;
  }
  for(int i=0;i<ArraySize(b);i++){
   if(b[i].ms!=t||b[i].width!=31)return false;int role=(int)b[i].x[0];if(role<0||role>1)return false;if(!HG5MapEarly(b[i],grid,HG5_MAP_V16,30,0,role,0,0,x)||!bank.Score(6+role,x,y))return false;float pb=(float)y[1],ps=(float)y[2];
   if(!Role16(t,role,(float)MathMax(pb,ps),0))continue;if(!HG5MapEarly(b[i],grid,HG5_MAP_V16_SIDE,33,0,role,pb,ps,x)||!bank.Score(8,x,y)||!Add(o16,t,y[0]>=.5?1:-1,role,0))return false;
  }
  for(int i=0;i<ArraySize(o15);i++)if(Role16(t,o15[i].rank,1.f,1)&&!Add(o16,t,o15[i].side,o15[i].rank,1))return false;
  for(int i=0;i<ArraySize(c);i++){
   if(c[i].ms!=t||c[i].width!=33)return false;int rank=0;if(!Role17(t,0,0,rank))continue;if(!HG5MapEarly(c[i],grid,HG5_MAP_V17,33,0,rank,0,0,x)||!bank.Score(9+rank,x,y))return false;float pb=(float)y[1],ps=(float)y[2];if(MathMax(pb,ps)<(rank==0?.82:.84))continue;if(!Add(o17,t,pb>=ps?1:-1,rank,0))return false;count17++;last17=t;
  }
  for(int i=0;i<ArraySize(o16);i++){int rank=0;if(Role17(t,1,o16[i].rank,rank)){if(!Add(o17,t,o16[i].side,rank,1))return false;count17++;last17=t;}}
  valid=true;return true;
 }

public:
 void ZeroFields(){{grid.ZeroFields();}{grid_ready=0;}{valid=0;}{minute16=0;}{minute17=0;}{last17=0;}{last_group=0;}{seen0=0;}{seen1=0;}{count17=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!grid.StateFields(codec))return false;}{if(!codec.Flag(grid_ready))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.I64(minute16))return false;}{if(!codec.I64(minute17))return false;}{if(!codec.I64(last17))return false;}{if(!codec.I64(last_group))return false;}{if(!codec.Flag(seen0))return false;}{if(!codec.Flag(seen1))return false;}{if(!codec.I32(count17))return false;}return true;}
};
#endif
