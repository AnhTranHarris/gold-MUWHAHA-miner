#ifndef HG5_STRUCTURAL_ADAPTIVE
#define HG5_STRUCTURAL_ADAPTIVE
#include "HG5StateCodec.mqh"
#include "HG5ParentMarginal.mqh"
#include "HG5MarketObservers.mqh"
#include "HG5LateMaps.mqh"
#include "HG5StatePrimitives.mqh"
class HG5LateBank{
 HG5PackedCore m[42];bool loaded[42];
public:
 HG5LateBank(){for(int i=0;i<42;i++)loaded[i]=false;}
 bool Load(int id,const uchar &bytes[]){int dims[42]={164,164,170,170,58,58,124,124,61,61,90,90,43,43,166,166,79,79,78,78,81,81,83,83,166,166,166,87,87,87,98,98,98,80,80,80,79,79,79,83,83,83};int i=id-19;if(i<0||i>=42)return false;loaded[i]=false;loaded[i]=m[i].LoadBytes(bytes)&&m[i].Features()==dims[i]&&m[i].Outputs()==1;return loaded[i];}
 bool Score(int id,const float &x[],float &v)const{int i=id-19;double y[];if(i<0||i>=42||!loaded[i]||!m[i].Predict(x,y))return false;v=(float)y[0];return true;}
};
struct HG5Market137{long ms,ordinal;float x[137];
 void ZeroFields(){{ms=0;}{ordinal=0;}for(int i=0;i<137;i++){x[i]=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(ms))return false;}{if(!codec.I64(ordinal))return false;}for(int i=0;i<137;i++){if(!codec.F32(x[i]))return false;}return true;}
};
bool HG5Actions(const HG5Market137 &m,int side,float &x[],int n){if((side!=1&&side!=-1)||(n!=164&&n!=170)||ArrayResize(x,n)!=n)return false;float sd=(float)side;for(int i=0;i<137;i++)x[i]=m.x[i];x[137]=sd;for(int i=0;i<19;i++)x[138+i]=sd*m.x[HG5_SIDE[i]];int k=side==1?0:1;x[157]=m.x[128+k];x[158]=m.x[130+k];x[159]=m.x[133+k];x[160]=sd*(m.x[133]-m.x[134]);x[161]=sd*m.x[27];x[162]=sd*m.x[4];x[163]=m.x[side==1?64:63];return true;}
class HG5V23Router{
 HG5ParentSignal prev;HG5V20Context context;HG5Market137 snap;bool have_prev,have_context,have_snap,valid;long pminute,minute,last,last_group;int pc,used,added,lastside;
 void Market(const HG5MarginalContext &c,const float &structure[],HG5Market137 &m){long t=c.ms;m.ms=t;m.ordinal=c.ordinal;for(int i=0;i<62;i++)m.x[i]=c.x[i];for(int i=0;i<60;i++)m.x[62+i]=structure[i];bool good=have_prev&&pminute==t/60000;float nan=HG5Missing();m.x[122]=good?(float)pc:0.f;m.x[123]=good?(float)((t-prev.ms)/1000.):9999.f;m.x[124]=good?(float)prev.side:0.f;m.x[125]=good?(float)prev.source:-1.f;m.x[126]=have_prev?(float)MathMin(9999.,(t-prev.ms)/1000.):9999.f;m.x[127]=have_prev?(float)prev.side:0.f;for(int k=0;k<2;k++){m.x[128+k]=c.keep?c.wide[k]:nan;m.x[130+k]=c.keep?c.tight[k]:nan;}long dt=t-context.ms;bool ok=have_context&&dt>=0&&dt<=10000&&t/60000==context.ms/60000;for(int i=132;i<137;i++)m.x[i]=nan;if(ok){bool role=c.x[45]>0;m.x[132]=(float)(dt/1000.);m.x[133]=role?context.p1[0]:context.p0[0];m.x[134]=role?context.p1[1]:context.p0[1];m.x[135]=role?context.a1:context.a0;m.x[136]=role?context.c1:context.c0;}}
public:
 HG5V23Router(){ZeroFields();have_prev=have_context=have_snap=false;valid=true;pminute=minute=last_group=-1;last=-1000000000000000000;pc=used=added=lastside=0;context.ms=prev.ms=snap.ms=-1000000000000000000;}
 bool Route(const HG5LateBank &bank,long t,const HG5V20Context &c20[],const HG5MarginalContext &c22[],const float &structure[],const long struct_ordinal,const HG5ParentSignal &parents[],HG5ParentSignal &o[],HG5Market137 &markets[]){
  ArrayResize(o,0);ArrayResize(markets,0);if(!valid||t<=last_group)return false;valid=false;last_group=t;long mn=t/60000;int ph=(int)(t/1000%60);if(mn!=minute){minute=mn;used=added=lastside=0;last=-1000000000000000000;}
  for(int i=0;i<ArraySize(c20);i++){if(c20[i].ms!=t)return false;context=c20[i];have_context=true;}float x[];float gain,loss;
  // Parent flip uses strictly prior snapshot, and unflipped V22 shadow history.
  for(int i=0;i<ArraySize(parents);i++){if(parents[i].ms!=t)return false;int side=parents[i].side;bool prior=have_prev&&pminute==mn;int rank=prior?pc:0;long dt=t-snap.ms;if(have_snap&&dt>0&&dt<=2000&&snap.ms/60000==mn&&ph<=29){if(!HG5Actions(snap,-side,x,170))return false;x[164]=(float)side;x[165]=(float)parents[i].source;x[166]=(float)dt;x[167]=(float)rank;x[168]=prior?(float)(t-prev.ms):99999.f;x[169]=prior?(float)prev.side:0.f;if(!bank.Score(21,x,gain)||!bank.Score(22,x,loss))return false;if(gain>=.45f&&loss<=.40f)side=-side;}
   if(!prior){pminute=mn;pc=0;}pc++;prev=parents[i];have_prev=true;if(used>=2||t-last<3000)continue;if(!HG5AddParent(o,t,side,0,0))return false;used++;last=t;lastside=side;
  }
  int best=0;float quality=0;for(int i=0;i<ArraySize(c22);i++){if(c22[i].ms!=t||c22[i].ordinal!=struct_ordinal||ArraySize(structure)<60)return false;HG5Market137 m;Market(c22[i],structure,m);int k=ArraySize(markets);if(ArrayResize(markets,k+1)!=k+1)return false;markets[k]=m;for(int j=0;j<2;j++){int side=j==0?1:-1;if(m.x[0]<3||m.x[0]>27||m.x[122]>=2||m.x[123]<3||(m.x[124]==side&&m.x[123]<5))continue;if(added||used>=2||ph<3||ph>27||t-last<3000||(side==lastside&&t-last<5000))continue;if(!HG5Actions(m,side,x,164)||!bank.Score(19,x,gain))return false;if(gain<.75f)continue;if(!bank.Score(20,x,loss))return false;if(loss>.003f)continue;if(best==0||gain>quality||(gain==quality&&side>best)){best=side;quality=gain;}}snap=m;have_snap=true;}
  if(best){if(!HG5AddParent(o,t,best,1,quality))return false;used++;added=1;last=t;lastside=best;}valid=true;return true;
 }

public:
 void ZeroFields(){{prev.ZeroFields();}{context.ZeroFields();}{snap.ZeroFields();}{have_prev=0;}{have_context=0;}{have_snap=0;}{valid=0;}{pminute=0;}{minute=0;}{last=0;}{last_group=0;}{pc=0;}{used=0;}{added=0;}{lastside=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!prev.StateFields(codec))return false;}{if(!context.StateFields(codec))return false;}{if(!snap.StateFields(codec))return false;}{if(!codec.Flag(have_prev))return false;}{if(!codec.Flag(have_context))return false;}{if(!codec.Flag(have_snap))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.I64(pminute))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(last))return false;}{if(!codec.I64(last_group))return false;}{if(!codec.I32(pc))return false;}{if(!codec.I32(used))return false;}{if(!codec.I32(added))return false;}{if(!codec.I32(lastside))return false;}return true;}
};
class HG5V24Router{
 HG5Reservation router;HG5Market137 snap;bool have_snap,have_prev,valid,has_anchor;HG5ParentSignal prev;long last_group,n,anchor_id,anchor_t;int anchor_side,anchor_config;float anchor[58];
 bool Select(const HG5LateBank &bank,const HG5ParentSignal &p,const long id,bool &reserve){reserve=false;long t=p.ms;long dt=t-snap.ms;if(!have_snap||dt<=0||dt>2000||snap.ms/60000!=t/60000||t/1000%60>24||(have_prev&&prev.ms/60000==t/60000))return true;float x[];if(ArrayResize(x,58)!=58)return false;for(int i=0;i<52;i++)x[i]=snap.x[HG5_COL[i]];x[52]=(float)p.side;x[53]=(float)(t/1000%60);x[54]=(float)p.source;x[55]=(float)dt;x[56]=have_prev?(float)MathMin(120000.,(double)(t-prev.ms)):120000.f;x[57]=have_prev?(float)prev.side:0.f;float rg,rl;if(!bank.Score(23,x,rg)||!bank.Score(24,x,rl))return false;float r[58];for(int i=0;i<58;i++)r[i]=x[i];if(ArrayResize(x,61)!=61)return false;x[58]=rg;x[59]=rl;float g[3],l[3];for(int j=0;j<3;j++){x[60]=(float)j;if(!bank.Score(27,x,g[j])||!bank.Score(28,x,l[j]))return false;}int best=-1;if(g[1]>=.35f&&l[1]<=.20f)best=1;else for(int j=0;j<3;j++){if(j==1||g[j]<.2f||l[j]>.1f)continue;if(best<0||g[j]-.5f*l[j]>g[best]-.5f*l[best])best=j;}if(best>=0){reserve=true;anchor_id=id;anchor_t=t;anchor_side=p.side;anchor_config=best;for(int i=0;i<58;i++)anchor[i]=r[i];}return true;}
 bool ReleaseScore(const HG5LateBank &bank,const HG5Market137 &m,HG5ReleaseChoice &c){long t=m.ms,delay=t-anchor_t;if(delay<1000||delay>8000||t/60000!=anchor_t/60000||delay>(anchor_config==2?5000:8000))return true;float x[];if(ArrayResize(x,124)!=124)return false;for(int i=0;i<58;i++)x[i]=anchor[i];for(int i=0;i<52;i++)x[58+i]=m.x[HG5_COL[i]];for(int i=0;i<11;i++)x[110+i]=x[58+HG5_DI[i]]-x[HG5_DI[i]];x[121]=(float)delay;double gf[3]={.25,.35,.45},lc[3]={.20,.25,.30};for(int k=0;k<2;k++){int s=k==0?1:-1;x[122]=(float)s;x[123]=s==anchor_side?1.f:0.f;float g,l;if(!bank.Score(25,x,g)||!bank.Score(26,x,l))return false;if((double)g>=gf[anchor_config]&&(double)l<=lc[anchor_config])HG5ChooseRelease(c,s,g,l,true);}return true;}
 bool Add(HG5ReserveEvent &o[],const HG5ReserveEvent &r){int n0=ArraySize(o);if(ArrayResize(o,n0+1)!=n0+1)return false;o[n0]=r;return true;}
public:
 HG5V24Router(){ZeroFields();router.Reset(8000);have_snap=have_prev=has_anchor=false;valid=true;last_group=-1;n=0;anchor_id=-1;anchor_t=-1;anchor_side=anchor_config=0;snap.ms=prev.ms=-1000000000000000000;}
 bool Route(const HG5LateBank &bank,long t,const HG5Market137 &markets[],const HG5ParentSignal &parents[],HG5ReserveEvent &o[]){ArrayResize(o,0);if(!valid||t<=last_group)return false;valid=false;last_group=t;router.Cutoff(t);long state[];if(!router.State(state))return false;has_anchor=state[1]!=0;for(int i=0;i<ArraySize(parents);i++){if(parents[i].ms!=t)return false;long id=n++;bool reserve=false;if(!Select(bank,parents[i],id,reserve))return false;HG5ReserveEvent e;if(router.Parent(t,id,parents[i].side,reserve,e)&&!Add(o,e))return false;if(!router.State(state))return false;has_anchor=state[1]!=0;prev=parents[i];have_prev=true;}
  for(int i=0;i<ArraySize(markets);i++){if(markets[i].ms!=t)return false;if(has_anchor){HG5ReleaseChoice c;c.present=false;c.utility=0;c.side=0;if(!ReleaseScore(bank,markets[i],c))return false;if(c.present){HG5ReserveEvent e;if(router.Release(t,anchor_id,c.side,e)&&!Add(o,e))return false;if(!router.State(state))return false;has_anchor=state[1]!=0;}}snap=markets[i];have_snap=true;}valid=true;return true;}

public:
 void ZeroFields(){{snap.ZeroFields();}{have_snap=0;}{have_prev=0;}{valid=0;}{has_anchor=0;}{prev.ZeroFields();}{last_group=0;}{n=0;}{anchor_id=0;}{anchor_t=0;}{anchor_side=0;}{anchor_config=0;}for(int i=0;i<58;i++){anchor[i]=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!router.StateFields(codec))return false;}{if(!snap.StateFields(codec))return false;}{if(!codec.Flag(have_snap))return false;}{if(!codec.Flag(have_prev))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.Flag(has_anchor))return false;}{if(!prev.StateFields(codec))return false;}{if(!codec.I64(last_group))return false;}{if(!codec.I64(n))return false;}{if(!codec.I64(anchor_id))return false;}{if(!codec.I64(anchor_t))return false;}{if(!codec.I32(anchor_side))return false;}{if(!codec.I32(anchor_config))return false;}for(int i=0;i<58;i++){if(!codec.F32(anchor[i]))return false;}return true;}
};
#endif
