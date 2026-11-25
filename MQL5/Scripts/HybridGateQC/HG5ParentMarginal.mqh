#ifndef HG5_PARENT_MARGINAL
#define HG5_PARENT_MARGINAL
#include "HG5StateCodec.mqh"
#include "HG5EarlyRouting.mqh"
#include "HG5V22Math.mqh"
struct HG5ParentSignal{long ms;int side,source;float confidence;
 void ZeroFields(){{ms=0;}{side=0;}{source=0;}{confidence=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(ms))return false;}{if(!codec.I32(side))return false;}{if(!codec.I32(source))return false;}{if(!codec.F32(confidence))return false;}return true;}
};
struct HG5V20Context{long ms;float x[37],pulse,p0[2],p1[2],a0,a1,c0,c1;
 void ZeroFields(){{ms=0;}for(int i=0;i<37;i++){x[i]=0;}{pulse=0;}for(int i=0;i<2;i++){p0[i]=0;}for(int i=0;i<2;i++){p1[i]=0;}{a0=0;}{a1=0;}{c0=0;}{c1=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(ms))return false;}for(int i=0;i<37;i++){if(!codec.F32(x[i]))return false;}{if(!codec.F32(pulse))return false;}for(int i=0;i<2;i++){if(!codec.F32(p0[i]))return false;}for(int i=0;i<2;i++){if(!codec.F32(p1[i]))return false;}{if(!codec.F32(a0))return false;}{if(!codec.F32(a1))return false;}{if(!codec.F32(c0))return false;}{if(!codec.F32(c1))return false;}return true;}
};
class HG5MiddleBank{
 HG5PackedCore m[8];bool loaded[8];
public:
 HG5MiddleBank(){for(int i=0;i<8;i++)loaded[i]=false;}
 bool Load(int i,const uchar &bytes[]){int dim[8]={37,37,37,37,45,62,62,77},out[8]={3,3,1,1,1,3,3,3};if(i<0||i>=8)return false;loaded[i]=false;loaded[i]=m[i].LoadBytes(bytes)&&m[i].Features()==dim[i]&&m[i].Outputs()==out[i];return loaded[i];}
 bool Ready()const{for(int i=0;i<8;i++)if(!loaded[i])return false;return true;}
 bool Score(int i,const float &x[],double &y[])const{return i>=0&&i<8&&loaded[i]&&m[i].Predict(x,y);}
};
float HG5Missing(){HGFloatBits b;b.u=0x7fc00000;return b.f;}
float HG5Sign(float x){return x>0?1.f:x<0?-1.f:0.f;}
bool HG5AddParent(HG5ParentSignal &o[],long t,int s,int src,float cf){int n=ArraySize(o);if(ArrayResize(o,n+1)!=n+1)return false;o[n].ms=t;o[n].side=s;o[n].source=src;o[n].confidence=cf;return true;}
class HG5V20Router{
 HG5V20Context prev;bool ready,valid;long minute,last,last_group;int used;
 bool Confidence(const HG5MiddleBank &bank,const HG5V20Context &c,int role,int src,long age,int sd,bool good,float &score){
  float x[];double y[];if(ArrayResize(x,45)!=45)return false;float nan=HG5Missing();for(int i=0;i<37;i++)x[i]=good?c.x[i]:nan;float p=c.p0[0],q=c.p0[1],a=c.a0;if(role){p=c.p1[0];q=c.p1[1];a=c.a1;}x[37]=(float)role;x[38]=(float)src;x[39]=(float)age;x[40]=good?(float)MathMax(p,q):nan;x[41]=good?a:nan;x[42]=good?(float)MathAbs(p-q):nan;x[43]=good?(p>=q?1.f:-1.f):nan;x[44]=good?c.pulse*(float)sd:0.f;if(!bank.Score(4,x,y))return false;score=(float)y[0];return true;
 }
 bool Context(const HG5MiddleBank &bank,const HG5EarlyRow &row,HG5V20Context &c){
  if(row.width!=37)return false;float x[];double y[];if(ArrayResize(x,37)!=37)return false;c.ms=row.ms;for(int i=0;i<37;i++)x[i]=c.x[i]=(float)row.x[i];c.pulse=x[4];if(!bank.Score(0,x,y))return false;c.p0[0]=(float)y[1];c.p0[1]=(float)y[2];if(!bank.Score(1,x,y))return false;c.p1[0]=(float)y[1];c.p1[1]=(float)y[2];if(!bank.Score(2,x,y))return false;c.a0=(float)y[0];if(!bank.Score(3,x,y))return false;c.a1=(float)y[0];return Confidence(bank,c,0,0,0,c.p0[0]>=c.p0[1]?1:-1,true,c.c0)&&Confidence(bank,c,1,0,0,c.p1[0]>=c.p1[1]?1:-1,true,c.c1);
 }
 void Advance(long t){long m=t/60000;if(m!=minute){minute=m;used=0;last=-1000000000000000000;}}
public:
 HG5V20Router(){ZeroFields();Reset();}
 void Reset(){ready=false;valid=true;minute=-1;last=-1000000000000000000;last_group=-1;used=0;prev.ms=-1000000000000000000;prev.pulse=prev.a0=prev.a1=prev.c0=prev.c1=0;for(int i=0;i<2;i++){prev.p0[i]=0;prev.p1[i]=0;}for(int i=0;i<37;i++)prev.x[i]=0;}
 bool Route(const HG5MiddleBank &bank,long t,const HG5EarlyRow &rows[],const HG5EarlySignal &fallback[],HG5ParentSignal &o[],HG5V20Context &ctx[]){
  ArrayResize(o,0);ArrayResize(ctx,0);if(!valid||t<=last_group||!bank.Ready())return false;valid=false;last_group=t;Advance(t);int phase=(int)(t/1000%60);
  for(int i=0;i<ArraySize(rows);i++){if(rows[i].ms!=t||!Context(bank,rows[i],prev))return false;ready=true;int n=ArraySize(ctx);if(ArrayResize(ctx,n+1)!=n+1)return false;ctx[n]=prev;if(used>=2||t-last<3000)continue;float p=used?prev.p1[0]:prev.p0[0],q=used?prev.p1[1]:prev.p0[1],a=used?prev.a1:prev.a0,c=used?prev.c1:prev.c0;if(phase>=(used?30:14)&&MathMax(p,q)>=(used?.50:.56)&&(double)a>=.04&&(double)c>=.08){if(!HG5AddParent(o,t,p>=q?1:-1,0,c))return false;used++;last=t;}}
  for(int i=0;i<ArraySize(fallback);i++){if(fallback[i].ms!=t)return false;if(used>=2||t-last<3000||fallback[i].rank!=used)continue;long age=t-prev.ms;bool good=ready&&age>=0&&age<=10000&&t/60000==prev.ms/60000;float cf;if(!Confidence(bank,prev,used,1,good?age:10000,fallback[i].side,good,cf))return false;if((double)cf>=.08){if(!HG5AddParent(o,t,fallback[i].side,1,cf))return false;used++;last=t;}}
  valid=true;return true;
 }

public:
 void ZeroFields(){{prev.ZeroFields();}{ready=0;}{valid=0;}{minute=0;}{last=0;}{last_group=0;}{used=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!prev.StateFields(codec))return false;}{if(!codec.Flag(ready))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(last))return false;}{if(!codec.I64(last_group))return false;}{if(!codec.I32(used))return false;}return true;}
};
struct HG5MarginalContext{long ms,ordinal;float x[62],wide[2],tight[2];bool keep;
 void ZeroFields(){{ms=0;}{ordinal=0;}for(int i=0;i<62;i++){x[i]=0;}for(int i=0;i<2;i++){wide[i]=0;}for(int i=0;i<2;i++){tight[i]=0;}{keep=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(ms))return false;}{if(!codec.I64(ordinal))return false;}for(int i=0;i<62;i++){if(!codec.F32(x[i]))return false;}for(int i=0;i<2;i++){if(!codec.F32(wide[i]))return false;}for(int i=0;i<2;i++){if(!codec.F32(tight[i]))return false;}{if(!codec.Flag(keep))return false;}return true;}
};
struct HG5MarginalChoice{int side;float quality;
 void ZeroFields(){{side=0;}{quality=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I32(side))return false;}{if(!codec.F32(quality))return false;}return true;}
};
class HG5V22Router{
 HG5ParentSignal prev;long minute,last,last_group,parent_minute;int used,added,lastside,parent_seen,parent_count;bool valid,have_parent;
 void Advance(long t){long m=t/60000;if(m!=minute){minute=m;used=added=lastside=parent_seen=0;last=-1000000000000000000;}}
 bool Make(const HG5MiddleBank &bank,const HG5EarlyRow &row,HG5MarginalContext &c,HG5MarginalChoice &choices[]){
  if(row.width!=45||row.x[37]!=1)return false;c.ms=row.ms;c.ordinal=row.ordinal;float x[];double y[];if(ArrayResize(x,62)!=62)return false;for(int i=0;i<45;i++)x[i]=(float)row.x[i];long t=row.ms;bool good=have_parent&&parent_minute==t/60000&&parent_count>0;float sd=good?(float)prev.side:0.f,age=good?(float)((t-prev.ms)/1000.):9999.f,sp=x[11],vol=(float)MathMax(5.f,x[33]+sp),rng=(float)MathMax(1.f,x[9]),pulse=x[4],s1=x[13],s5=x[14],q5=x[20];
  x[45]=(float)(good?parent_count:0);x[46]=age;x[47]=sd;x[48]=good?prev.confidence:HG5Missing();x[49]=good?(float)prev.source:-1.f;x[50]=x[12]-x[39];x[51]=x[43]/rng;x[52]=HG5NpTanh((pulse*s1+x[10]*.25f)/vol);x[53]=HG5NpTanh((x[19]-q5/5.f)/(3.f+(float)MathSqrt(MathMax(0.f,q5))));x[54]=x[8]/vol;x[55]=HG5Sign(s1)*HG5Sign(s5);x[56]=pulse*HG5NpExp(-x[5]/8.f);x[57]=HG5NpTanh((s1-s5/5.f)/vol);x[58]=sd*HG5Sign(s1);x[59]=sd*pulse;x[60]=have_parent?(float)prev.side:0.f;x[61]=have_parent?(float)MathMin(9999.,(t-prev.ms)/1000.):9999.f;
  for(int i=0;i<62;i++)c.x[i]=x[i];if(!bank.Score(5,x,y))return false;c.wide[0]=(float)y[1];c.wide[1]=(float)y[2];if(!bank.Score(6,x,y))return false;c.tight[0]=(float)y[1];c.tight[1]=(float)y[2];c.keep=MathMax(c.wide[0],c.wide[1])>=.08f||MathMax(c.tight[0],c.tight[1])>=.025f;if(!c.keep)return true;
  float j[2];for(int k=0;k<2;k++)j[k]=(float)MathSqrt(MathMax(0.f,c.wide[k]*c.tight[k]));if(ArrayResize(x,77)!=77)return false;
  for(int k=0;k<2;k++){int side=k==0?1:-1;float sf=(float)side;if(j[k]<.15f||c.wide[k]<.18f||x[0]<3||x[0]>27||x[45]>1||age<3||(sd==sf&&age<5))continue;x[62]=c.wide[0];x[63]=c.wide[1];x[64]=c.tight[0];x[65]=c.tight[1];x[66]=sf;x[67]=c.wide[k];x[68]=c.tight[k];x[69]=j[k];x[70]=j[k]-j[1-k];x[71]=sf*x[8];x[72]=sf*x[13];x[73]=sf*x[14];x[74]=sf*x[24];x[75]=sf*x[4];x[76]=sf*x[47];if(!bank.Score(7,x,y))return false;float gain=(float)y[1],risk=(float)y[2];if(risk>.015f||gain<.15f)continue;int n=ArraySize(choices);if(ArrayResize(choices,n+1)!=n+1)return false;choices[n].side=side;choices[n].quality=gain;}
  return true;
 }
public:
 HG5V22Router(){ZeroFields();Reset();}
 void Reset(){valid=true;have_parent=false;minute=parent_minute=last_group=-1;last=-1000000000000000000;used=added=lastside=parent_seen=parent_count=0;prev.ms=-1000000000000000000;prev.side=0;prev.source=-1;prev.confidence=HG5Missing();}
 bool Route(const HG5MiddleBank &bank,long t,const HG5EarlyRow &rows[],const HG5ParentSignal &parents[],HG5ParentSignal &o[],HG5MarginalContext &ctx[]){
  ArrayResize(o,0);ArrayResize(ctx,0);if(!valid||t<=last_group||!bank.Ready())return false;valid=false;last_group=t;Advance(t);int ph=(int)(t/1000%60);for(int i=0;i<ArraySize(parents);i++){if(parents[i].ms!=t)return false;if(parent_minute!=minute){parent_minute=minute;parent_count=0;}parent_count++;prev=parents[i];have_parent=true;parent_seen++;if(used>=2||t-last<3000)continue;if(!HG5AddParent(o,t,prev.side,0,0))return false;used++;last=t;lastside=prev.side;}
  HG5MarginalChoice choices[];ArrayResize(choices,0);for(int i=0;i<ArraySize(rows);i++){if(rows[i].ms!=t||rows[i].width!=45)return false;if(rows[i].x[37]!=1)continue;HG5MarginalContext c;if(!Make(bank,rows[i],c,choices))return false;int n=ArraySize(ctx);if(ArrayResize(ctx,n+1)!=n+1)return false;ctx[n]=c;}
  // At most one marginal addition per minute; source sorting chooses highest gain, BUY first on exact tie.
  int best=-1;for(int i=0;i<ArraySize(choices);i++){int s=choices[i].side;float q=choices[i].quality;if(added||used>=2||ph<3||ph>27||t-last<3000||(double)q<.45||(s==lastside&&t-last<5000))continue;if(best<0||q>choices[best].quality||(q==choices[best].quality&&s>choices[best].side))best=i;}
  if(best>=0){if(!HG5AddParent(o,t,choices[best].side,1,choices[best].quality))return false;added=1;used++;last=t;lastside=choices[best].side;}
  valid=true;return true;
 }

public:
 void ZeroFields(){{prev.ZeroFields();}{minute=0;}{last=0;}{last_group=0;}{parent_minute=0;}{used=0;}{added=0;}{lastside=0;}{parent_seen=0;}{parent_count=0;}{valid=0;}{have_parent=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!prev.StateFields(codec))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(last))return false;}{if(!codec.I64(last_group))return false;}{if(!codec.I64(parent_minute))return false;}{if(!codec.I32(used))return false;}{if(!codec.I32(added))return false;}{if(!codec.I32(lastside))return false;}{if(!codec.I32(parent_seen))return false;}{if(!codec.I32(parent_count))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.Flag(have_parent))return false;}return true;}
};
#endif
