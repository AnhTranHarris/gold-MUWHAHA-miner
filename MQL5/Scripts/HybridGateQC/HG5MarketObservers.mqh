#ifndef HG5_MARKET_OBSERVERS_MQH
#define HG5_MARKET_OBSERVERS_MQH
#include "HG5StateCodec.mqh"
#include "HG5RX136.mqh"
// Frozen Stage4 structural/proxy observers. One quote at a time, no file I/O or order API.
// Output emitted at first quote of each second with phase <=29, ordinal starts at 1.
struct HG5StructSec {long sec;double o,h,l,c,travel,up,down;int n;
 void ZeroFields(){{sec=0;}{o=0;}{h=0;}{l=0;}{c=0;}{travel=0;}{up=0;}{down=0;}{n=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(sec))return false;}{if(!codec.F64(o))return false;}{if(!codec.F64(h))return false;}{if(!codec.F64(l))return false;}{if(!codec.F64(c))return false;}{if(!codec.F64(travel))return false;}{if(!codec.F64(up))return false;}{if(!codec.F64(down))return false;}{if(!codec.I32(n))return false;}return true;}
};
struct HG5DC {double ext,hi,lo,origin;int dir;long flip;
 void ZeroFields(){{ext=0;}{hi=0;}{lo=0;}{origin=0;}{dir=0;}{flip=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.F64(ext))return false;}{if(!codec.F64(hi))return false;}{if(!codec.F64(lo))return false;}{if(!codec.F64(origin))return false;}{if(!codec.I32(dir))return false;}{if(!codec.I64(flip))return false;}return true;}
};
class HG5StructuralObserver {
private:
 long n,last,oldsec,minute,hlast,llast;double prev,prevbid,prevask,mo,mh,ml,ph,pl,pc,mt;
 double ema[4],eabs[4],esigned[4],taus[4],thr[4];HG5DC dc[4];HG5StructSec hist[64],cur;bool valid;
 void ClearSec(HG5StructSec &b){b.sec=-1;b.o=0;b.h=0;b.l=0;b.c=0;b.travel=0;b.up=0;b.down=0;b.n=0;}
 void ResetDC(HG5DC &d){d.ext=0;d.hi=0;d.lo=0;d.origin=0;d.dir=0;d.flip=-1;}
 void PushDC(HG5DC &d,double x,long t,double q){if(d.flip<0){d.ext=d.hi=d.lo=d.origin=x;d.flip=t;return;}if(!d.dir){d.hi=MathMax(d.hi,x);d.lo=MathMin(d.lo,x);if(x-d.lo>=q){d.dir=1;d.ext=x;d.origin=d.lo;d.flip=t;}else if(d.hi-x>=q){d.dir=-1;d.ext=x;d.origin=d.hi;d.flip=t;}}else if(d.dir>0){d.ext=MathMax(d.ext,x);if(d.ext-x>=q){d.origin=d.ext;d.ext=x;d.dir=-1;d.flip=t;}}else{d.ext=MathMin(d.ext,x);if(x-d.ext>=q){d.origin=d.ext;d.ext=x;d.dir=1;d.flip=t;}}}
 void Add(float &a[],int &k,double x){a[k++]=(float)x;}
public:
 HG5StructuralObserver(){ZeroFields();Reset();}
 void Reset(){n=0;last=-1;oldsec=-1;minute=-1;hlast=-1;llast=-1;prev=0;prevbid=0;prevask=0;mo=0;mh=0;ml=0;ph=0;pl=0;pc=0;mt=0;valid=true;taus[0]=500;taus[1]=2000;taus[2]=8000;taus[3]=30000;thr[0]=8;thr[1]=20;thr[2]=50;thr[3]=100;for(int j=0;j<4;j++){ema[j]=0;eabs[j]=0;esigned[j]=0;ResetDC(dc[j]);}for(int j=0;j<64;j++)ClearSec(hist[j]);ClearSec(cur);}
 long Ordinal()const{return n;}
 bool Push(const HG5Quote &t,bool &emitted,float &a[]){
  emitted=false;if(!valid||t.ms<0||t.bid<=0||t.ask<t.bid||t.ms<last){valid=false;return false;}++n;double x=HG5Mid(t),dx=last<0?0:x-prev;long dt=last<0?0:t.ms-last,sec=t.ms/1000,mn=sec/60;bool fresh=sec!=oldsec;
  if(last<0||dt>60000){for(int j=0;j<4;j++){ema[j]=x;eabs[j]=esigned[j]=0;ResetDC(dc[j]);}for(int j=0;j<64;j++)ClearSec(hist[j]);ClearSec(cur);dx=0;}
  if(mn!=minute){if(minute>=0){ph=mh;pl=ml;pc=prev;}else ph=pl=pc=x;minute=mn;mo=mh=ml=x;hlast=llast=t.ms;mt=0;}else{if(x>mh){mh=x;hlast=t.ms;}if(x<ml){ml=x;llast=t.ms;}mt+=MathAbs(dx);}
  for(int j=0;j<4;j++){double alpha=-MathExpm1(-(dt>1?dt:1)/taus[j]);ema[j]+=alpha*(x-ema[j]);eabs[j]=(1-alpha)*eabs[j]+alpha*MathAbs(dx);esigned[j]=(1-alpha)*esigned[j]+alpha*dx;PushDC(dc[j],x,t.ms,thr[j]);}
  if(fresh){if(cur.sec>=0)hist[cur.sec%64]=cur;ClearSec(cur);cur.sec=sec;cur.o=cur.h=cur.l=cur.c=x;cur.n=1;}else{cur.h=MathMax(cur.h,x);cur.l=MathMin(cur.l,x);cur.c=x;cur.travel+=MathAbs(dx);cur.up+=MathMax(0.,dx);cur.down+=MathMax(0.,-dx);cur.n++;}
  if(fresh&&sec%60<=29){if(ArrayResize(a,64)!=64){valid=false;return false;}int k=0;Add(a,k,x-mo);Add(a,k,mh-x);Add(a,k,x-ml);Add(a,k,(t.ms-hlast)/1000.);Add(a,k,(t.ms-llast)/1000.);Add(a,k,(x-mo)/MathMax(1.,mt));Add(a,k,x-ph);Add(a,k,x-pl);Add(a,k,x-pc);Add(a,k,ph-pl);Add(a,k,last<0?0:t.bid-prevbid);Add(a,k,last<0?0:t.ask-prevask);
   for(int j=0;j<4;j++){Add(a,k,x-ema[j]);Add(a,k,esigned[j]/MathMax(.01,eabs[j]));}for(int j=0;j<4;j++){Add(a,k,dc[j].dir);Add(a,k,dc[j].dir*(x-dc[j].origin));Add(a,k,dc[j].dir*(dc[j].ext-x));Add(a,k,MathMin(120.,(t.ms-dc[j].flip)/1000.));}
   int horizons[4]={2,5,10,20};for(int i=0;i<4;i++){int w=horizons[i];double h=x,l=x,tr=0,up=0,dn=0,old=x;int cnt=0;for(int j=1;j<=w;j++){HG5StructSec b=hist[(sec-j+64)%64];if(b.sec!=sec-j)continue;h=MathMax(h,b.h);l=MathMin(l,b.l);tr+=b.travel;up+=b.up;dn+=b.down;old=b.o;cnt+=b.n;}Add(a,k,x-old);Add(a,k,h-x);Add(a,k,x-l);Add(a,k,(up-dn)/MathMax(1.,up+dn));Add(a,k,(x-old)/MathMax(1.,tr));Add(a,k,cnt);}for(int j=k;j<64;j++)a[j]=0.f;if(k!=60){valid=false;return false;}emitted=true;}
  prev=x;prevbid=t.bid;prevask=t.ask;last=t.ms;oldsec=sec;return true;
 }

public:
 void ZeroFields(){{n=0;}{last=0;}{oldsec=0;}{minute=0;}{hlast=0;}{llast=0;}{prev=0;}{prevbid=0;}{prevask=0;}{mo=0;}{mh=0;}{ml=0;}{ph=0;}{pl=0;}{pc=0;}{mt=0;}for(int i=0;i<4;i++){ema[i]=0;}for(int i=0;i<4;i++){eabs[i]=0;}for(int i=0;i<4;i++){esigned[i]=0;}for(int i=0;i<4;i++){taus[i]=0;}for(int i=0;i<4;i++){thr[i]=0;}for(int i=0;i<4;i++){dc[i].ZeroFields();}for(int i=0;i<64;i++){hist[i].ZeroFields();}{cur.ZeroFields();}{valid=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(n))return false;}{if(!codec.I64(last))return false;}{if(!codec.I64(oldsec))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(hlast))return false;}{if(!codec.I64(llast))return false;}{if(!codec.F64(prev))return false;}{if(!codec.F64(prevbid))return false;}{if(!codec.F64(prevask))return false;}{if(!codec.F64(mo))return false;}{if(!codec.F64(mh))return false;}{if(!codec.F64(ml))return false;}{if(!codec.F64(ph))return false;}{if(!codec.F64(pl))return false;}{if(!codec.F64(pc))return false;}{if(!codec.F64(mt))return false;}for(int i=0;i<4;i++){if(!codec.F64(ema[i]))return false;}for(int i=0;i<4;i++){if(!codec.F64(eabs[i]))return false;}for(int i=0;i<4;i++){if(!codec.F64(esigned[i]))return false;}for(int i=0;i<4;i++){if(!codec.F64(taus[i]))return false;}for(int i=0;i<4;i++){if(!codec.F64(thr[i]))return false;}for(int i=0;i<4;i++){if(!dc[i].StateFields(codec))return false;}for(int i=0;i<64;i++){if(!hist[i].StateFields(codec))return false;}{if(!cur.StateFields(codec))return false;}{if(!codec.Flag(valid))return false;}return true;}
};
struct HG5ProxySec {long s;double o,c,h,l,rv,bp,travel,db,da,ab,aa,sp,sp2,dt,dt2;int n,sync,chg;
 void ZeroFields(){{s=0;}{o=0;}{c=0;}{h=0;}{l=0;}{rv=0;}{bp=0;}{travel=0;}{db=0;}{da=0;}{ab=0;}{aa=0;}{sp=0;}{sp2=0;}{dt=0;}{dt2=0;}{n=0;}{sync=0;}{chg=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(s))return false;}{if(!codec.F64(o))return false;}{if(!codec.F64(c))return false;}{if(!codec.F64(h))return false;}{if(!codec.F64(l))return false;}{if(!codec.F64(rv))return false;}{if(!codec.F64(bp))return false;}{if(!codec.F64(travel))return false;}{if(!codec.F64(db))return false;}{if(!codec.F64(da))return false;}{if(!codec.F64(ab))return false;}{if(!codec.F64(aa))return false;}{if(!codec.F64(sp))return false;}{if(!codec.F64(sp2))return false;}{if(!codec.F64(dt))return false;}{if(!codec.F64(dt2))return false;}{if(!codec.I32(n))return false;}{if(!codec.I32(sync))return false;}{if(!codec.I32(chg))return false;}return true;}
};
class HG5ProxyObserver {
private:
 long n,last,oldsec;double pb,pa,prevabs;HG5ProxySec cur,hist[64];bool valid;
 void Clear(HG5ProxySec &b){b.s=-1;b.o=b.c=b.h=b.l=b.rv=b.bp=b.travel=b.db=b.da=b.ab=b.aa=b.sp=b.sp2=b.dt=b.dt2=0;b.n=b.sync=b.chg=0;}
 void Add(float &a[],int &k,double x){a[k++]=(float)x;}
public:
 HG5ProxyObserver(){ZeroFields();Reset();}
 void Reset(){n=0;last=-1;oldsec=-1;pb=pa=prevabs=0;valid=true;Clear(cur);for(int j=0;j<64;j++)Clear(hist[j]);}
 long Ordinal()const{return n;}
 bool Push(const HG5Quote &t,bool &emitted,float &a[]){
  emitted=false;if(!valid||t.ms<0||t.bid<=0||t.ask<t.bid||t.ms<last){valid=false;return false;}++n;double x=HG5Mid(t),sp=t.ask-t.bid;long sec=t.ms/1000;bool fresh=sec!=oldsec;double db=last<0?0:t.bid-pb,da=last<0?0:t.ask-pa,dx=(db+da)*.5,dt=last<0?0:t.ms-last;
  if(last<0||dt>60000){for(int j=0;j<64;j++)Clear(hist[j]);Clear(cur);db=da=dx=dt=prevabs=0;}
  if(fresh){if(cur.s>=0)hist[cur.s%64]=cur;Clear(cur);cur.s=sec;cur.o=cur.c=cur.h=cur.l=x;}
  cur.c=x;cur.h=MathMax(cur.h,x);cur.l=MathMin(cur.l,x);cur.rv+=dx*dx;cur.bp+=MathAbs(dx)*prevabs;cur.travel+=MathAbs(dx);cur.db+=db;cur.da+=da;cur.ab+=MathAbs(db);cur.aa+=MathAbs(da);cur.sp+=sp;cur.sp2+=sp*sp;cur.dt+=dt;cur.dt2+=dt*dt;cur.sync+=(int)(db*da>0);cur.chg+=(int)(db!=0||da!=0);cur.n++;
  if(fresh&&sec%60<=29){if(ArrayResize(a,36)!=36){valid=false;return false;}int k=0;int horizons[3]={4,10,20};for(int i=0;i<3;i++){int w=horizons[i];HG5ProxySec z=cur;double hi=x,lo=x,first=x,rv=0,bpv=0,pr=dx;int count=0;for(int j=1;j<=w;j++){HG5ProxySec b=hist[(sec-j+64)%64];if(b.s!=sec-j)continue;++count;hi=MathMax(hi,b.h);lo=MathMin(lo,b.l);first=b.o;double r=b.c-b.o;rv+=r*r;bpv+=MathAbs(pr*r);pr=r;z.rv+=b.rv;z.bp+=b.bp;z.travel+=b.travel;z.db+=b.db;z.da+=b.da;z.ab+=b.ab;z.aa+=b.aa;z.sp+=b.sp;z.sp2+=b.sp2;z.dt+=b.dt;z.dt2+=b.dt2;z.sync+=b.sync;z.chg+=b.chg;z.n+=b.n;}
   double mean=z.sp/MathMax(1,z.n),md=z.dt/MathMax(1,z.n),range=MathMax(1.,hi-lo);Add(a,k,(x-first)/MathSqrt(MathMax(1.,z.rv)));Add(a,k,(x-lo)/range);Add(a,k,(x-first)/MathMax(1.,z.travel));Add(a,k,z.db/MathMax(1.,z.ab));Add(a,k,z.da/MathMax(1.,z.aa));Add(a,k,(double)z.sync/MathMax(1,z.chg));Add(a,k,sp-mean);Add(a,k,MathSqrt(MathMax(0.,z.sp2/MathMax(1,z.n)-mean*mean)));Add(a,k,MathSqrt(MathMax(0.,z.dt2/MathMax(1,z.n)-md*md))/MathMax(1.,md));Add(a,k,MathMax(0.,(z.rv-1.57079632679*z.bp)/MathMax(1.,z.rv)));Add(a,k,MathMax(0.,(rv-1.57079632679*bpv)/MathMax(1.,rv)));Add(a,k,count);}if(k!=36){valid=false;return false;}emitted=true;}
  pb=t.bid;pa=t.ask;prevabs=MathAbs(dx);last=t.ms;oldsec=sec;return true;
 }

public:
 void ZeroFields(){{n=0;}{last=0;}{oldsec=0;}{pb=0;}{pa=0;}{prevabs=0;}{cur.ZeroFields();}for(int i=0;i<64;i++){hist[i].ZeroFields();}{valid=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(n))return false;}{if(!codec.I64(last))return false;}{if(!codec.I64(oldsec))return false;}{if(!codec.F64(pb))return false;}{if(!codec.F64(pa))return false;}{if(!codec.F64(prevabs))return false;}{if(!cur.StateFields(codec))return false;}for(int i=0;i<64;i++){if(!hist[i].StateFields(codec))return false;}{if(!codec.Flag(valid))return false;}return true;}
};
#endif
