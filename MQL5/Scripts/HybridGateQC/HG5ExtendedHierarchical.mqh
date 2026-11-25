#ifndef HG5_EXTENDED_HIERARCHICAL
#define HG5_EXTENDED_HIERARCHICAL
#include "HG5StateCodec.mqh"
#include "HG5StructuralAdaptive.mqh"
struct HG5Market73{long ms,ordinal;float x[73];
 void ZeroFields(){{ms=0;}{ordinal=0;}for(int i=0;i<73;i++){x[i]=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(ms))return false;}{if(!codec.I64(ordinal))return false;}for(int i=0;i<73;i++){if(!codec.F32(x[i]))return false;}return true;}
};
bool HG5JoinProxy(const HG5Market137 &m,const long ord,const float &proxy[],HG5Market73 &o){if(m.ordinal!=ord||ArraySize(proxy)!=36)return false;o.ms=m.ms;o.ordinal=m.ordinal;for(int i=0;i<37;i++)o.x[i]=m.x[HG5_C[i]];for(int i=0;i<36;i++)o.x[37+i]=proxy[i];return true;}
struct HG5Anchor73{long id,t;int side;float x[73],extra[5],mn,mx;int mode,config;
 void ZeroFields(){{id=0;}{t=0;}{side=0;}for(int i=0;i<73;i++){x[i]=0;}for(int i=0;i<5;i++){extra[i]=0;}{mn=0;}{mx=0;}{mode=0;}{config=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(id))return false;}{if(!codec.I64(t))return false;}{if(!codec.I32(side))return false;}for(int i=0;i<73;i++){if(!codec.F32(x[i]))return false;}for(int i=0;i<5;i++){if(!codec.F32(extra[i]))return false;}{if(!codec.F32(mn))return false;}{if(!codec.F32(mx))return false;}{if(!codec.I32(mode))return false;}{if(!codec.I32(config))return false;}return true;}
};
bool HG5AddReserve(HG5ReserveEvent &o[],const HG5ReserveEvent &r){int n=ArraySize(o);if(ArrayResize(o,n+1)!=n+1)return false;o[n]=r;return true;}
// Source-exact reservation source selection, one retained anchor. Current snapshot cannot anchor itself.
class HG5AnchorHistory{
 HG5Market73 snap;HG5ReserveEvent prev;bool have_snap,have_prev;long n;
public:
 HG5AnchorHistory(){ZeroFields();have_snap=have_prev=false;n=0;snap.ms=prev.t=-1000000000000000000;}
 bool Parent(const HG5ReserveEvent &p,HG5Anchor73 &a,bool &eligible){long t=p.t,id=n++,dt=t-snap.ms;eligible=have_snap&&dt>0&&dt<=2000&&snap.ms/60000==t/60000&&t/1000%60<=15&&!p.replaced&&(!have_prev||prev.t/60000!=t/60000);a.id=id;a.t=t;a.side=p.side;a.mn=a.mx=0.f;a.mode=-1;a.config=-1;if(eligible){for(int i=0;i<73;i++)a.x[i]=snap.x[i];a.extra[0]=(float)p.side;a.extra[1]=(float)(t/1000%60);a.extra[2]=(float)dt;a.extra[3]=have_prev?(float)MathMin(120000.,(double)(t-prev.t)):120000.f;a.extra[4]=have_prev?(float)prev.side:0.f;}prev=p;have_prev=true;return true;}
 void Snapshot(const HG5Market73 &m){snap=m;have_snap=true;}

public:
 void ZeroFields(){{snap.ZeroFields();}{prev.ZeroFields();}{have_snap=0;}{have_prev=0;}{n=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!snap.StateFields(codec))return false;}{if(!prev.StateFields(codec))return false;}{if(!codec.Flag(have_snap))return false;}{if(!codec.Flag(have_prev))return false;}{if(!codec.I64(n))return false;}return true;}
};
void HG5PathBounds(HG5Anchor73 &a,const HG5Market73 &m){float d=(float)a.side*(m.x[13]-a.x[13]);a.mn=(float)MathMin(a.mn,d);a.mx=(float)MathMax(a.mx,d);}
void HG5V25R(const HG5Anchor73 &a,float &x[]){for(int i=0;i<37;i++)x[i]=a.x[i];for(int i=0;i<5;i++)x[37+i]=a.extra[i];for(int i=0;i<36;i++)x[42+i]=a.x[37+i];}
void HG5V26R(const HG5Anchor73 &a,float &x[]){for(int i=0;i<73;i++)x[i]=a.x[i];for(int i=0;i<5;i++)x[73+i]=a.extra[i];x[78]=0;}
bool HG5V25Select(const HG5LateBank &b,HG5Anchor73 &a,bool &reserve){
 reserve=false;float x[];if(ArrayResize(x,43)!=43)return false;for(int i=0;i<37;i++)x[i]=a.x[i];for(int i=0;i<5;i++)x[37+i]=a.extra[i];x[42]=2.f;float g,l;if(!b.Score(31,x,g)||!b.Score(32,x,l))return false;
 if(g>=.2f&&l<=.2f){reserve=true;a.mode=0;a.config=2;return true;}
 if(ArrayResize(x,79)!=79)return false;HG5V25R(a,x);x[78]=0.f;if(!b.Score(35,x,g)||!b.Score(36,x,l))return false;
 if(g>=.2f&&l<=.2f){reserve=true;a.mode=1;a.config=0;return true;}
 if(ArrayResize(x,78)!=78)return false;float ag,al;if(!b.Score(37,x,ag)||!b.Score(38,x,al))return false;if(ArrayResize(x,83)!=83)return false;x[78]=ag;x[79]=al;int best=-1;float quality=-1e9f;float xx[];if(ArrayResize(xx,81)!=81)return false;
 for(int k=0;k<3;k++){for(int i=0;i<80;i++)xx[i]=x[i];xx[80]=(float)k;if(!b.Score(39,xx,g)||!b.Score(40,xx,l))return false;x[80]=g;x[81]=l;x[82]=(float)k;float w15,w30;if(!b.Score(41,x,w15)||!b.Score(42,x,w30))return false;float wr=(float)MathMax(w15,w30),q=g-.5f*l-.5f*wr;if(g>=.2f&&l<=.07f&&wr<=.05f&&(best<0||q>quality)){best=k;quality=q;}}
 if(best>=0){reserve=true;a.mode=2;a.config=best;}return true;
}
bool HG5V25Release(const HG5LateBank &b,HG5Anchor73 &a,const HG5Market73 &m,HG5ReleaseChoice &choice){long d=m.ms-a.t;if(d<=0||d>24000||m.ms/60000!=a.t/60000)return true;HG5PathBounds(a,m);if(d<9000)return true;float x[];if(ArrayResize(x,a.mode==0?90:166)!=(a.mode==0?90:166))return false;for(int i=0;i<37;i++)x[i]=a.x[i];for(int i=0;i<5;i++)x[37+i]=a.extra[i];for(int i=0;i<37;i++)x[42+i]=m.x[i];float rel=(float)a.side*(m.x[13]-a.x[13]);x[79]=(float)d;x[82]=rel;x[83]=-a.mn;x[84]=a.mx;x[85]=rel-a.mn;
 for(int k=0;k<2;k++){int side=k==0?1:-1;float s=(float)side;x[80]=s;x[81]=side==a.side?1.f:0.f;x[86]=s*m.x[21];x[87]=s*m.x[22];x[88]=s*m.x[23];x[89]=s*(m.x[18]+m.x[19]+m.x[20]);if(a.mode!=0){for(int i=0;i<36;i++){x[90+i]=a.x[37+i];x[126+i]=m.x[37+i];}x[162]=s*(m.x[40]+m.x[41])*.5f;x[163]=s*(m.x[40]+m.x[41]-m.x[64]-m.x[65])*.5f;x[164]=(rel-a.mn)/(float)MathMax(5.f,a.mx-a.mn);x[165]=m.x[43]/(float)MathMax(1.f,m.x[44]);}
  bool allowed=false;double gf=0,lc=0;int maxms=0;bool same=false;if(a.mode==1){allowed=side==a.side&&rel<=-5.f&&-a.mn>=20.f&&rel-a.mn>=5.f;gf=.10;lc=.40;maxms=24000;}else{double gains[3]={.15,.25,.10},losses[3]={.30,.35,.40};int horizon[3]={16000,24000,22000};gf=gains[a.config];lc=losses[a.config];maxms=horizon[a.config];same=a.config!=1;allowed=!same||side==a.side;}if(!allowed||d>maxms)continue;float g,l;if(!b.Score(a.mode==0?29:33,x,g)||!b.Score(a.mode==0?30:34,x,l))return false;if((double)g>=gf&&(double)l<=lc)HG5ChooseRelease(choice,side,g,l,true);
 }return true;
}
class HG5V25Router{
 HG5AnchorHistory history;HG5Reservation router;HG5Anchor73 anchor;bool valid,have_anchor;long last_group;
public:
 HG5V25Router(){ZeroFields();router.Reset(24000);valid=true;have_anchor=false;last_group=-1;}
 bool Route(const HG5LateBank &b,long t,const HG5Market73 &market[],const HG5ReserveEvent &parents[],HG5ReserveEvent &o[]){ArrayResize(o,0);if(!valid||t<=last_group)return false;valid=false;last_group=t;router.Cutoff(t);long state[];if(!router.State(state))return false;have_anchor=state[1]!=0;for(int i=0;i<ArraySize(parents);i++){if(parents[i].t!=t)return false;HG5Anchor73 a;bool eligible=false,reserve=false;if(!history.Parent(parents[i],a,eligible))return false;if(eligible&&!HG5V25Select(b,a,reserve))return false;HG5ReserveEvent out;if(router.Parent(t,a.id,a.side,reserve,out)&&!HG5AddReserve(o,out))return false;if(!router.State(state))return false;have_anchor=state[1]!=0;if(have_anchor)anchor=a;}
 for(int i=0;i<ArraySize(market);i++){if(market[i].ms!=t)return false;if(have_anchor){HG5ReleaseChoice choice;choice.present=false;choice.side=0;choice.utility=0;if(!HG5V25Release(b,anchor,market[i],choice))return false;if(choice.present){HG5ReserveEvent out;if(router.Release(t,anchor.id,choice.side,out)&&!HG5AddReserve(o,out))return false;if(!router.State(state))return false;have_anchor=state[1]!=0;}}history.Snapshot(market[i]);}valid=true;return true;}

public:
 void ZeroFields(){{anchor.ZeroFields();}{valid=0;}{have_anchor=0;}{last_group=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!history.StateFields(codec))return false;}{if(!router.StateFields(codec))return false;}{if(!anchor.StateFields(codec))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.Flag(have_anchor))return false;}{if(!codec.I64(last_group))return false;}return true;}
};
// V26-HS original selected rc/dc/sc/mc configurations; no fitting or new policy.
bool HG5V26Select(const HG5LateBank &b,HG5Anchor73 &a,bool &reserve){reserve=false;float x[];if(ArrayResize(x,80)!=80)return false;HG5V26R(a,x);float g,l,w,quality=-1e9f;int best=-1;for(int k=0;k<5;k++){x[79]=(float)k;if(!b.Score(52,x,g)||!b.Score(53,x,l)||!b.Score(54,x,w))return false;float q=g-.5f*l-.5f*w;if(g>=.2f&&l<=.2f&&w<=.1f&&(best<0||q>quality)){best=k;quality=q;}}if(best>=0){reserve=true;a.config=best;return true;}
 if(ArrayResize(x,79)!=79)return false;float og,ol,ow;if(!b.Score(55,x,og)||!b.Score(56,x,ol)||!b.Score(57,x,ow))return false;if(ArrayResize(x,83)!=83)return false;x[80]=og;x[81]=ol;x[82]=ow;for(int k=0;k<3;k++){x[79]=(float)k;if(!b.Score(58,x,g)||!b.Score(59,x,l)||!b.Score(60,x,w))return false;float q=g-.5f*l-.5f*w;if(g>=.15f&&l<=.03f&&w<=.15f&&(best<0||q>quality)){best=k;quality=q;}}if(best>=0){reserve=true;a.config=best;}return true;}
void HG5Press(const HG5Market73 &m,int side,float &p0,float &p1,float &p2){p0=(float)side*(m.x[40]+m.x[41])/2.f;p1=(float)side*(m.x[52]+m.x[53])/2.f;p2=(float)side*(m.x[64]+m.x[65])/2.f;}
bool HG5V26Release(const HG5LateBank &b,HG5Anchor73 &a,const HG5Market73 &m,HG5ReleaseChoice &choice){long d=m.ms-a.t;if(d<=0||d>24000||m.ms/60000!=a.t/60000)return true;HG5PathBounds(a,m);if(d<9000)return true;float x[];if(ArrayResize(x,166)!=166)return false;HG5V26R(a,x);for(int i=0;i<73;i++)x[79+i]=m.x[i];float rel=(float)a.side*(m.x[13]-a.x[13]);x[152]=(float)d;x[155]=rel;x[156]=-a.mn;x[157]=a.mx;x[158]=rel-a.mn;
 double gf[5]={.45,.35,.55,.45,.35},lc[5]={.25,.35,.20,.25,.35},wc[5]={.25,.35,.20,.25,.35};int horizon[5]={16000,24000,24000,20000,24000};for(int k=0;k<2;k++){int side=k==0?1:-1;if(d>horizon[a.config]||(side==a.side)!=(a.config>=3))continue;float s=(float)side,p0,p1,p2;HG5Press(m,side,p0,p1,p2);x[153]=s;x[154]=side==a.side?1.f:0.f;x[159]=(side==a.side?rel-a.mn:a.mx-rel)/(float)MathMax(5.f,a.mx-a.mn);x[160]=p0;x[161]=p1;x[162]=p2;x[163]=p0-p2;x[164]=s*(m.x[18]-m.x[20]);x[165]=m.x[43]/(float)MathMax(1.f,m.x[44]);float g,l,w;if(!b.Score(43,x,g)||!b.Score(44,x,l)||!b.Score(45,x,w))return false;if((double)g>=gf[a.config]&&(double)l<=lc[a.config]&&(double)w<=wc[a.config])HG5ChooseRelease(choice,side,g-.5f*w,l,true);}
 return true;}
struct HG5DiscoveryChoice{int side;float g,l,w;double quality;bool eligible;
 void ZeroFields(){{side=0;}{g=0;}{l=0;}{w=0;}{quality=0;}{eligible=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I32(side))return false;}{if(!codec.F32(g))return false;}{if(!codec.F32(l))return false;}{if(!codec.F32(w))return false;}{if(!codec.F64(quality))return false;}{if(!codec.Flag(eligible))return false;}return true;}
};
class HG5DiscoverGate{
 long minute,last;int used;
public:
 HG5DiscoverGate(){ZeroFields();minute=-1;last=-1000000000000000000;used=0;}
 bool Route(long t,const HG5ReserveEvent &parents[],const HG5DiscoveryChoice &choices[],HG5ReserveEvent &o[]){ArrayResize(o,0);if(t/60000!=minute){minute=t/60000;last=-1000000000000000000;used=0;}for(int i=0;i<ArraySize(parents);i++){if(used>=2||t-last<3000)continue;if(!HG5AddReserve(o,parents[i]))return false;used++;last=t;}if(used)return true;int best=-1;for(int i=0;i<ArraySize(choices);i++){if(!choices[i].eligible)continue;if(best<0||choices[i].quality>choices[best].quality)best=i;}if(best>=0){HG5ReserveEvent out;out.t=t;out.id=-1;out.side=choices[best].side;out.replaced=false;if(!HG5AddReserve(o,out))return false;used++;last=t;}return true;}

public:
 void ZeroFields(){{minute=0;}{last=0;}{used=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(minute))return false;}{if(!codec.I64(last))return false;}{if(!codec.I32(used))return false;}return true;}
};
class HG5V26Router{
 HG5AnchorHistory history;HG5Reservation router;HG5Anchor73 anchor;HG5DiscoverGate discovery,meta;bool valid,have_anchor,have_shadow;long last_group,hm,first[2];int count[2];float mx[2],util[2];HG5ReserveEvent shadow;
 bool Discover(const HG5LateBank &b,const HG5Market73 &m,HG5DiscoveryChoice &d[],HG5DiscoveryChoice &md[]){long t=m.ms;int ph=(int)(t/1000%60);if(ph<3||ph>24||(have_shadow&&shadow.t/60000==t/60000))return true;float F0[],F1[];if(ArrayResize(F0,87)!=87||ArrayResize(F1,87)!=87)return false;float s0[3],s1[3];bool mask[2];if(t/60000!=hm){hm=t/60000;for(int k=0;k<2;k++){count[k]=0;mx[k]=util[k]=0;first[k]=-1;}}
 for(int k=0;k<2;k++){int side=k==0?1:-1;float s=(float)side;float x[];if(ArrayResize(x,87)!=87)return false;for(int i=0;i<73;i++)x[i]=m.x[i];x[73]=s;x[74]=s*m.x[13];x[75]=s*m.x[6];x[76]=s*m.x[7];x[77]=s*m.x[18];x[78]=s*m.x[19];x[79]=s*m.x[20];HG5Press(m,side,x[80],x[81],x[82]);x[83]=x[80]-x[82];x[84]=m.x[43]/(float)MathMax(1.f,m.x[44]);x[85]=have_shadow?(float)MathMin(120000.,(double)(t-shadow.t)):120000.f;x[86]=have_shadow?(float)shadow.side:0.f;float g,l,w;if(!b.Score(46,x,g)||!b.Score(47,x,l)||!b.Score(48,x,w))return false;d[k].side=side;d[k].g=g;d[k].l=l;d[k].w=w;d[k].quality=(double)g-.5*(double)l-.5*(double)w;d[k].eligible=g>=.95f&&l<=.015f&&w<=.03f;mask[k]=g>=.65f&&l<=.10f&&w<=.10f;if(k==0){for(int j=0;j<87;j++)F0[j]=x[j];s0[0]=g;s0[1]=l;s0[2]=w;}else{for(int j=0;j<87;j++)F1[j]=x[j];s1[0]=g;s1[1]=l;s1[2]=w;}}
 for(int k=0;k<2;k++){int side=k==0?1:-1,di=side>0?1:0;md[k].eligible=false;md[k].side=side;if(!mask[k])continue;float x[];if(ArrayResize(x,98)!=98)return false;for(int j=0;j<87;j++)x[j]=k==0?F0[j]:F1[j];for(int j=0;j<3;j++){x[87+j]=k==0?s0[j]:s1[j];x[90+j]=k==0?s1[j]:s0[j];}x[93]=(float)count[di];x[94]=mx[di];x[95]=util[di];x[96]=first[di]<0?0.f:(float)(t-first[di]);x[97]=x[87]-mx[di];count[di]++;mx[di]=(float)MathMax(mx[di],x[87]);util[di]=(float)MathMax(util[di],(double)x[87]-.5*(double)x[88]-.5*(double)x[89]);if(first[di]<0)first[di]=t;float g,l,w;if(!b.Score(49,x,g)||!b.Score(50,x,l)||!b.Score(51,x,w))return false;md[k].g=g;md[k].l=l;md[k].w=w;md[k].quality=(double)g-.5*(double)l-.5*(double)w;md[k].eligible=g>=.75f&&l<=.05f&&w<=.05f;}return true;
 }
public:
 HG5V26Router(){ZeroFields();router.Reset(24000);valid=true;have_anchor=have_shadow=false;last_group=hm=-1;shadow.t=-1000000000000000000;for(int k=0;k<2;k++){count[k]=0;mx[k]=util[k]=0;first[k]=-1;}}
 bool Route(const HG5LateBank &b,long t,const HG5Market73 &market[],const HG5ReserveEvent &parents[],HG5ReserveEvent &o[]){ArrayResize(o,0);if(!valid||t<=last_group)return false;valid=false;last_group=t;router.Cutoff(t);long state[];if(!router.State(state))return false;have_anchor=state[1]!=0;HG5ReserveEvent res[];for(int i=0;i<ArraySize(parents);i++){if(parents[i].t!=t)return false;HG5Anchor73 a;bool eligible=false,reserve=false;if(!history.Parent(parents[i],a,eligible))return false;if(eligible&&!HG5V26Select(b,a,reserve))return false;HG5ReserveEvent out;if(router.Parent(t,a.id,a.side,reserve,out)&&!HG5AddReserve(res,out))return false;if(!router.State(state))return false;have_anchor=state[1]!=0;if(have_anchor)anchor=a;shadow=parents[i];have_shadow=true;}
 HG5DiscoveryChoice d[],md[];if(ArrayResize(d,2)!=2||ArrayResize(md,2)!=2)return false;for(int k=0;k<2;k++){d[k].eligible=false;md[k].eligible=false;}if(ArraySize(market)>1)return false;for(int i=0;i<ArraySize(market);i++){if(market[i].ms!=t)return false;if(have_anchor){HG5ReleaseChoice choice;choice.present=false;choice.side=0;choice.utility=0;if(!HG5V26Release(b,anchor,market[i],choice))return false;if(choice.present){HG5ReserveEvent out;if(router.Release(t,anchor.id,choice.side,out)&&!HG5AddReserve(res,out))return false;if(!router.State(state))return false;have_anchor=state[1]!=0;}}history.Snapshot(market[i]);if(!Discover(b,market[i],d,md))return false;}
 HG5ReserveEvent p[];if(!discovery.Route(t,res,d,p)||!meta.Route(t,p,md,o))return false;valid=true;return true;}

public:
 void ZeroFields(){{anchor.ZeroFields();}{valid=0;}{have_anchor=0;}{have_shadow=0;}{last_group=0;}{hm=0;}for(int i=0;i<2;i++){first[i]=0;}for(int i=0;i<2;i++){count[i]=0;}for(int i=0;i<2;i++){mx[i]=0;}for(int i=0;i<2;i++){util[i]=0;}{shadow.ZeroFields();}}
 bool StateFields(HG5StateCodec &codec){{if(!history.StateFields(codec))return false;}{if(!router.StateFields(codec))return false;}{if(!anchor.StateFields(codec))return false;}{if(!discovery.StateFields(codec))return false;}{if(!meta.StateFields(codec))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.Flag(have_anchor))return false;}{if(!codec.Flag(have_shadow))return false;}{if(!codec.I64(last_group))return false;}{if(!codec.I64(hm))return false;}for(int i=0;i<2;i++){if(!codec.I64(first[i]))return false;}for(int i=0;i<2;i++){if(!codec.I32(count[i]))return false;}for(int i=0;i<2;i++){if(!codec.F32(mx[i]))return false;}for(int i=0;i<2;i++){if(!codec.F32(util[i]))return false;}{if(!shadow.StateFields(codec))return false;}return true;}
};
#endif
