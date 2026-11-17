// MICRO180-RB1: exact source-ordinal Coinexx REAL TickLogger -> strictly causal
// first-quote-of-second snapshots. Read-only; NO R9 target, label, exit or P&L
// fields are accepted by this executable. Derived feature stream goes to stdout.
// GPL? No external source reused. C++17 + system zlib only.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
#include <unordered_set>
#include <fstream>
#include <vector>
#include <zlib.h>
using namespace std;
struct Second {long long s=-1;double bid=0,ask=0,mid=0,hi=0,lo=0;unsigned n=0;};
struct Bar {long long m=-1;double o=0,h=0,l=0,c=0,sum=0;unsigned n=0;};
struct Market {
 array<Second,2048> secs{}; deque<Bar> bars;
 Second forming; Bar minute_bar;
 long long current_second=-1,current_minute=-1,lastms=-1,lastoutput=-1;
 double lastbid=0,lastask=0,anchor5=0,anchor15=0,minute_anchor=0;
 double cached_di_spread=0,cached_adx=0;
 long long bucket5=-1,bucket15=-1; unsigned long long rows=0;
 void reset(){secs.fill(Second{});bars.clear();forming=Second{};minute_bar=Bar{};current_second=current_minute=lastms=-1;bucket5=bucket15=-1;cached_adx=cached_di_spread=0;}
 void advance(long long ms,double bid,double ask){
  long long sec=ms/1000, minute=ms/60000;
  double mid=(bid+ask)*.5;
  if(current_second>=0 && (sec<current_second || sec-current_second>120)) reset();
  if(current_second>=0 && sec!=current_second){secs[current_second%secs.size()]=forming;forming=Second{};}
  if(current_minute>=0 && minute!=current_minute){
   if(minute==current_minute+1){bars.push_back(minute_bar);if(bars.size()>360)bars.pop_front();refresh_di_adx();}
   else bars.clear();
   minute_bar=Bar{};
  }
  current_second=sec; current_minute=minute;
  if(bucket5!=sec/5){bucket5=sec/5;anchor5=mid;}
  if(bucket15!=sec/15){bucket15=sec/15;anchor15=mid;}
  if(minute_bar.n==0){minute_anchor=mid;minute_bar={minute,mid,mid,mid,mid,mid,1};}
  else {minute_bar.h=max(minute_bar.h,mid);minute_bar.l=min(minute_bar.l,mid);minute_bar.c=mid;minute_bar.sum+=mid;minute_bar.n++;}
  if(forming.n==0)forming={sec,bid,ask,mid,mid,mid,1};
  else {forming.bid=bid;forming.ask=ask;forming.mid=mid;forming.hi=max(forming.hi,mid);forming.lo=min(forming.lo,mid);forming.n++;}
  lastbid=bid;lastask=ask;lastms=ms;rows++;
 }
 const Second *sback(long long sec,int n)const {
  const long long target=sec-n;
  // Exact earlier seconds preferred; accept only 3 seconds of missing quotes.
  for(int d=0;d<4;d++){long long t=target-d;if(t<0)break;const Second &x=secs[t%secs.size()];if(x.s==t)return &x;}
  return nullptr;
 }
 double at(long long sec,int n,int kind=0)const {
  auto p=sback(sec,n);if(!p)return numeric_limits<double>::quiet_NaN();
  return kind==1?p->bid:kind==2?p->ask:p->mid;
 }
 // Completed-M1 Wilder DM/DI14 and ADX14 (no incomplete current bar).
 void refresh_di_adx(){
  const int n=14;if(bars.size()<n+1){cached_di_spread=cached_adx=0;return;}
  double tr=0,plus=0,minus=0,adx=0;vector<double> dxx;dxx.reserve(bars.size());
  for(int i=1;i<int(bars.size());i++){
   const auto &b=bars[i],&p=bars[i-1];
   double up=b.h-p.h,down=p.l-b.l;
   double pd=(up>down&&up>0)?up:0;
   double md=(down>up&&down>0)?down:0;
   double tt=max({b.h-b.l,abs(b.h-p.c),abs(b.l-p.c)});
   if(i<=n){tr+=tt;plus+=pd;minus+=md;}
   else {tr=tr-tr/n+tt;plus=plus-plus/n+pd;minus=minus-minus/n+md;}
   if(i>=n){
    double pdi=100*plus/max(1e-9,tr),mdi=100*minus/max(1e-9,tr);
    cached_di_spread=(pdi-mdi)/100.;
    dxx.push_back(100*abs(pdi-mdi)/max(1e-9,pdi+mdi));
   }
  }
  if(dxx.size()>=size_t(n)){
   for(int i=0;i<n;i++){adx+=dxx[i];}adx/=n;
   for(int i=n;i<int(dxx.size());i++)adx=(adx*(n-1)+dxx[i])/n;
   cached_adx=adx/100.;
  }else cached_adx=0;
 }
 double ema(int n)const {if(bars.empty())return 0;double x=bars.front().c,a=2./(n+1);for(const auto &b:bars)x=a*b.c+(1-a)*x;return x;}
 double qvwap(int n)const {if(int(bars.size())<n)return 0;double sum=0,count=0;for(int i=int(bars.size())-n;i<int(bars.size());i++){sum+=bars[i].sum;count+=bars[i].n;}return sum/max(1.,count);}
 double range(int n)const {if(int(bars.size())<n)return 0;double total=0;for(int i=int(bars.size())-n;i<int(bars.size());i++)total+=bars[i].h-bars[i].l;return total/n;}
 double atr1(int n=14)const {if(int(bars.size())<n+1)return 0;double sum=0;for(int i=int(bars.size())-n;i<int(bars.size());i++){
  auto &b=bars[i];double prev=bars[i-1].c;sum+=max({b.h-b.l,abs(b.h-prev),abs(b.l-prev)});
 }return sum/n;}
 double atr5()const { // 14 COMPLETED 5m bars constructed exclusively from completed M1 bars.
  if(bars.size()<76)return 0;
  vector<Bar> m5; m5.reserve(17);Bar g{}; int mcount=0;
  for(const auto &b:bars){
   if(b.m%5==0){g=b;mcount=1;}
   else if(mcount>0 && b.m==g.m+mcount){
    g.h=max(g.h,b.h);g.l=min(g.l,b.l);g.c=b.c;g.sum+=b.sum;g.n+=b.n;mcount++;
   } else {g=Bar{};mcount=0;}
   if(mcount==5){m5.push_back(g);g=Bar{};mcount=0;}
  }
  if(m5.size()<15)return 0;
  double sum=0;for(int i=int(m5.size())-14;i<int(m5.size());i++){
   const auto &b=m5[i];double prev=m5[i-1].c;sum+=max({b.h-b.l,abs(b.h-prev),abs(b.l-prev)});
  }return sum/14.;
 }
 double efficiency(long long sec,int n,int step,double now)const {double travel=0,last=now;for(int k=step;k<=n;k+=step){auto x=at(sec,k);if(!isfinite(x))return 0;travel+=abs(last-x);last=x;}return (now-last)/max(.01,travel);}
 double rv(long long sec,int n,int step,double now)const {double sum=0,last=now;int count=0;for(int k=step;k<=n;k+=step){auto x=at(sec,k);if(!isfinite(x))break;sum+=(last-x)*(last-x);last=x;count++;}return count?sqrt(sum/count):0;}
 double quote_count(long long sec,int n)const{double c=0;for(int k=1;k<=n;k++){const Second &v=secs[(sec-k)%secs.size()];if(v.s==sec-k)c+=v.n;}return c;}
 bool features(long long ms,double bid,double ask,vector<double>&v){
  long long sec=ms/1000;double mid=(bid+ask)*.5;
  // From completed bars only. Initial cold/warmup minutes are explicitly unscored.
  if(bars.size()<22)return false;
  double r5=at(sec,5),r15=at(sec,15),r60=at(sec,60),r180=at(sec,180),r300=at(sec,300);
  if(!isfinite(r5)||!isfinite(r15)||!isfinite(r60)||!isfinite(r180)||!isfinite(r300))return false;
  double atrm1=max(.05,atr1()),atrm5=atr5(),atr=max(.1,atrm5>0?atrm5:atrm1);
  double highs15=-1e99, lows15=1e99, highs30=-1e99,lows30=1e99,asklo15=1e99,asklo30=1e99;
  double bidhi15=-1e99,bidhi30=-1e99;
  for(int k=1;k<=30;k++){const Second &q=secs[(sec-k)%secs.size()];if(q.s!=sec-k)continue;
   if(k<=15){bidhi15=max(bidhi15,q.bid);asklo15=min(asklo15,q.ask);highs15=max(highs15,q.mid);lows15=min(lows15,q.mid);}
   bidhi30=max(bidhi30,q.bid);asklo30=min(asklo30,q.ask);highs30=max(highs30,q.mid);lows30=min(lows30,q.mid);
  }
  if(bidhi15<-1e50||bidhi30<-1e50||asklo15>1e50||asklo30>1e50)return false;
  double s1=efficiency(sec,10,1,mid),s1travel=0,prev=mid;int turns=0;double prevmove=0;
  for(int k=1;k<=10;k++){double x=at(sec,k);if(!isfinite(x))break;double move=prev-x;s1travel+=abs(move);if(prevmove*move<0)turns++;prevmove=move;prev=x;}
  double high3=-1e99,low3=1e99,high5=-1e99,low5=1e99;
  for(int k=1;k<=5;k++){const Bar &b=bars[bars.size()-k];high5=max(high5,b.h);low5=min(low5,b.l);if(k<=3){high3=max(high3,b.h);low3=min(low3,b.l);}}
  double sr60=rv(sec,60,5,mid),sr300=rv(sec,300,15,mid);
  double cnt5=quote_count(sec,5),cnt60=quote_count(sec,60);
  double spread=ask-bid,spread_prev=lastask-lastbid;
  double completed15=at(sec,15),completed30=at(sec,30);
  // All output values reflect only prices at or before this current first tick.
  v={
   double(sec%60),double((ms/3600000)%24),
   atrm1,atrm5,atr,
   spread,spread/max(.01,spread_prev),
   (mid-r5)/atr,(mid-r15)/atr,(mid-r60)/atr,(mid-r180)/atr,(mid-r300)/atr,
   efficiency(sec,10,1,mid),efficiency(sec,60,5,mid),efficiency(sec,180,15,mid),
   sr60/atr,sr300/atr,sr60/max(.01,sr300),
   cnt5/max(1.,cnt60/12.),cnt5,cnt60,
   (mid-qvwap(1))/atr,(mid-qvwap(3))/atr,(mid-qvwap(5))/atr,
   (mid-ema(3))/atr,(ema(3)-ema(8))/atr,(ema(8)-ema(21))/atr,
   (mid-bars.back().c)/atr,(mid-bars.back().o)/atr,
   (mid-high3)/atr,(mid-low3)/atr,(mid-high5)/atr,(mid-low5)/atr,
   range(1)/max(.01,range(5)),
   (mid-anchor5)/atr,(mid-anchor15)/atr,(mid-minute_anchor)/atr,
   (bid-bidhi15)/atr,(bid-bidhi30)/atr,(asklo15-ask)/atr,(asklo30-ask)/atr,
   (mid-completed15)/atr,(mid-completed30)/atr,
   s1,s1travel/atr,double(turns),
   atrm5/max(.01,atrm1),cached_di_spread,cached_adx,double(minute_bar.n),
   (mid-(highs15+lows15)*.5)/atr,(mid-(highs30+lows30)*.5)/atr,
   (mid-(high5+low5)*.5)/atr
  };
  for(double x:v)if(!isfinite(x))return false;
  return true;
 }
};
// No use of logger's future-derived R9 state, gate_open, entry/exit events,
// ATR, S1, synthetic quote marks, volume_real or family outcome.
static bool parse(const char *ln,long long &ms,double &bid,double &ask){
 if(strncmp(ln,"REAL,",5))return false;
 const char *p=ln+5;char *ep=nullptr;
 ms=strtoll(p,&ep,10);if(!ep||*ep!=',')return false;
 p=ep+1;const char *comma=strchr(p,',');if(!comma)return false;
 p=comma+1;bid=strtod(p,&ep);if(!ep||*ep!=',')return false;
 p=ep+1;ask=strtod(p,&ep);if(!ep||(*ep!=','&&*ep!='\n'))return false;
 return ms>0&&bid>0&&ask>=bid;
}
static const char *NAMES="phase,hour,atr_m1,atr_m5,atr_used,spread,spread_shock,ret5,ret15,ret60,ret180,ret300,eff10,eff60,eff180,rv60,rv300,rv_ratio,quote_intensity,quote_count5,quote_count60,vwap1,vwap3,vwap5,ema3_dist,ema3_8,ema8_21,lastbar_close,lastbar_open,channel3_hi,channel3_lo,channel5_hi,channel5_lo,contraction,basket5,basket15,minute_disp,buy_break15,buy_break30,sell_break15,sell_break30,disp15,disp30,s1_eff,s1_travel,s1_turns,atr_ratio,di_spread14,adx14,minute_quote_count,band15,band30,band5";
int main(int argc,char**argv){
 if(argc<2){cerr<<"usage: causal_quote_engine [--only-seconds positive_teacher_seconds.txt] original_REAL_daily_file.csv.gz [...]\n";return 2;}
 int firstarg=1;bool filter=false;unordered_set<long long> allowed;
 if(string(argv[1])=="--only-seconds"){
  if(argc<4){cerr<<"missing time list or source files\n";return 2;}
  ifstream fi(argv[2]);if(!fi){cerr<<"cannot read training time list\n";return 2;}
  long long s;while(fi>>s)allowed.insert(s);
  firstarg=3;filter=true;
 }
 cout<<"time_msc,second,minute,bid,ask,"<<NAMES<<"\n";
 cout<<fixed<<setprecision(7);Market h;long long prevms=-1;unsigned long long ok=0,candidates=0;
 char ln[8192];
 for(int k=firstarg;k<argc;k++){
  gzFile g=gzopen(argv[k],"rb");if(!g){cerr<<"error: cannot open source "<<argv[k]<<"\n";return 3;}
  while(gzgets(g,ln,sizeof(ln))){long long ms;double bid,ask;if(!parse(ln,ms,bid,ask))continue;
   if(prevms>=0&&ms<prevms){cerr<<"error: non-monotonic source tick time\n";gzclose(g);return 4;}
   prevms=ms;ok++;long long sec=ms/1000;
   if(h.current_second!=sec){
    h.advance(ms,bid,ask); // commits prior completed second and bar; updates only current observed tick
    vector<double> v;
    if((!filter||allowed.count(sec))&&h.features(ms,bid,ask,v)){
     cout<<ms<<','<<sec<<','<<ms/60000<<','<<bid<<','<<ask;
     for(double x:v)cout<<','<<x;
     cout<<'\n';candidates++;
    }
   }else h.advance(ms,bid,ask);
  }
  if(!gzeof(g)){cerr<<"error: incomplete gzip or corrupt source "<<argv[k]<<"\n";gzclose(g);return 5;}
  gzclose(g);
 }
 cerr<<"source_real_rows="<<ok<<" causal_second_snapshots="<<candidates<<"\n";
}
