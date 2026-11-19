// Atlas-directed causal completed-microbar Heikin-Ashi and confirmed-swing Fibonacci features.
// 1s/5s/15s/30s windows selected from January R9 observed median 18s holding duration.
// Read-only original Coinexx REAL TickLogger. Never use R9 SYNTH intraday price action.
// Emit one snapshot BEFORE each original R9 entry tick, never the quote at/after entry.
#include <zlib.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <limits>
using ll=long long;
struct Event{int row;ll ms;int side;};
struct Quote{ll ms;double mid,spread;};
struct Bar{ll bucket,end;double o,h,l,c,ha_o,ha_c,atr;int dir;double wick;int run;};
struct Factory{
 int s;ll curr=-1,last_end=-1;double o,h,l,c,ha_op=0,ha_cl=0,atr=0,prev_close=0;
 std::vector<Bar>v;int last_pivot_dir=0,pivot_previous_dir=0;double last_pivot_price=0,pivot_previous_price=0;int last_pivot_idx=-1;
 int pivots=0,run=0;double range_sum=0;int ntr=0;
 explicit Factory(int p):s(p){v.reserve(600000/(p>1?p:1));}
 void finalbar(){
  if(curr<0)return;ll end=(curr+1)*(ll)s*1000;
  double tr=(v.empty()?h-l:std::max({h-l,std::fabs(h-prev_close),std::fabs(l-prev_close)}));
  ++ntr;range_sum+=tr;atr=(ntr==1?tr:(ntr<14?range_sum/ntr:(atr*13+tr)/14));
  double ha_close=(o+h+l+c)*.25;
  double ha_open=(v.empty()||end-v.back().end>6LL*3600000LL)?(o+c)*.5:(v.back().ha_o+v.back().ha_c)*.5;
  double ha_high=std::max({h,ha_open,ha_close}),ha_low=std::min({l,ha_open,ha_close});
  int dir=ha_close>ha_open?1:ha_close<ha_open?-1:0;
  run=(v.empty()||v.back().dir!=dir||end-v.back().end>6LL*3600000LL)?1:run+1;
  double wick=((ha_high-std::max(ha_open,ha_close))-(std::min(ha_open,ha_close)-ha_low))/std::max(.01,ha_high-ha_low);
  v.push_back({curr,end,o,h,l,c,ha_open,ha_close,atr,dir,wick,run});
  int j=(int)v.size()-1,k=j-2;
  if(k>=3){
    bool high=v[k].h>=v[k-1].h&&v[k].h>=v[k-2].h&&v[k].h>=v[k-3].h&&v[k].h>v[k+1].h&&v[k].h>v[k+2].h;
    bool low=v[k].l<=v[k-1].l&&v[k].l<=v[k-2].l&&v[k].l<=v[k-3].l&&v[k].l<v[k+1].l&&v[k].l<v[k+2].l;
    if(high&&low){if(std::fabs(v[k].h-v[k-1].c)>std::fabs(v[k-1].c-v[k].l))low=false;else high=false;}
    if(high||low){
      int typ=high?1:-1;double price=high?v[k].h:v[k].l;
      if(last_pivot_dir==typ){if((typ==1&&price>last_pivot_price)||(typ==-1&&price<last_pivot_price)){last_pivot_price=price;last_pivot_idx=k;}}
      else if(last_pivot_dir==0||std::fabs(price-last_pivot_price)>=.55*atr){
        pivot_previous_dir=last_pivot_dir;pivot_previous_price=last_pivot_price;last_pivot_dir=typ;last_pivot_price=price;last_pivot_idx=k;++pivots;
      }
    }
  }
  prev_close=c;last_end=end;
 }
 void advance(ll ms){
  if(curr>=0&&(curr+1)*(ll)s*1000<=ms){finalbar();curr=-1;}
 }
 void add(ll ms,double mid){
  advance(ms);ll b=ms/((ll)s*1000);
  if(curr!=b){curr=b;o=h=l=c=mid;}
  else{h=std::max(h,mid);l=std::min(l,mid);c=mid;}
 }
 std::string snapshot(ll ms,int side){
  advance(ms);
  if(v.empty())return ",,,,,,,,,,,,,,,";
  const Bar &b=v.back(); int N=(int)v.size();
  double flip=0;int flips=0,np=0;for(int i=std::max(1,N-7);i<N;i++){if(v[i].end-v[i-1].end<=6LL*3600000LL){flips+=(v[i].dir!=v[i-1].dir);np++;}}
  double fib=std::numeric_limits<double>::quiet_NaN(),swingdir=fib,amp=fib,nearest=fib,piv_age=fib;
  if(pivots>=2&&last_pivot_dir!=pivot_previous_dir&&pivot_previous_dir!=0){
    double dist=last_pivot_price-pivot_previous_price;amp=std::fabs(dist);swingdir=(dist>0?1:-1)*side;
    fib=(dist>0?(last_pivot_price-b.c): (b.c-last_pivot_price))/std::max(.01,amp);
    const double levels[]={0.236,0.382,.5,.618,.786,1.,1.272,1.618};
    double delta=1e20;for(double r:levels)delta=std::min(delta,std::fabs(fib-r));
    nearest=delta*amp/std::max(.01,b.atr);piv_age=(last_pivot_idx>=0)?(b.end-v[last_pivot_idx].end)/(1000.*s):0;
  }
  // Field counts are exactly 16, empty fields preserve missing states.
  char buf[640];auto clean=[](double x){return std::isfinite(x)?x:-999999.;};
  std::snprintf(buf,sizeof(buf),",%.3f,%.4f,%.6f,%.6f,%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.3f,%d,%d", (ms-b.end)/1000.,b.atr, (b.ha_c-b.ha_o)/std::max(.01,b.atr)*side,b.wick*side,b.dir*side,b.run,np?((double)flips/np):-1.,clean(fib),clean(swingdir),clean(amp/std::max(.01,b.atr)),clean(nearest),clean(piv_age), (double)(b.ha_c-b.ha_o), pivots,(int)v.size());
  return std::string(buf);
 }
};
static int cents(const char* p){int neg=(*p=='-');if(neg)++p;int whole=0;while(*p>='0'&&*p<='9')whole=whole*10+(*p++-'0');int v=whole*100;if(*p=='.'){++p;v+=10*(*p++-'0');if(*p>='0'&&*p<='9')v+=*p-'0';}return neg?-v:v;}
int main(int argc,char**argv){
 if(argc<5){std::cerr<<"Usage: entries.csv out.csv daily_gzs...\n";return 2;}
 std::ifstream in(argv[1]);std::string line;getline(in,line);std::vector<Event>events;
 while(getline(in,line)){std::istringstream ss(line);std::string a,b,c;getline(ss,a,',');getline(ss,b,',');getline(ss,c,',');if(a.empty()||b.empty())continue;events.push_back({atoi(a.c_str()),atoll(b.c_str()),atoi(c.c_str())});}
 if(events.size()!=27980){std::cerr<<"bad entry count "<<events.size()<<"\n";return 3;}
 auto cmp=[](const Event&a,const Event&b){return a.ms<b.ms;};if(!std::is_sorted(events.begin(),events.end(),cmp)){std::cerr<<"events unsorted\n";return 4;}
 std::ofstream out(argv[2]);out<<std::setprecision(12);out<<"source_row,entry_ms";
 for(std::string n:{"quotes10","quotes60","mean_spread60_USD","disp10_USD","disp60_USD","travel10_USD","travel60_USD","max_jump10_USD","quote_staleness_ms"})out<<","<<n;
 for(int s:{1,5,15,30}){
  std::string k="micro"+std::to_string(s)+"s";
  for(std::string nm:{"lastbar_age_s","atr","ha_body_atr_side","ha_wick_side","ha_dir_side","ha_run","ha_flip7","fib_retrace","fib_dir_side","fib_amp_atr","fib_level_dist_atr","fib_pivot_age","ha_raw_body","fib_pivot_count","closed_bar_count"})out<<","<<k<<"_"<<nm;
 }out<<"\n";
 Factory b1(1),b5(5),b15(15),b30(30);std::deque<Quote> recent;size_t idx=0;long long ticknum=0,prev_ms=-1,backwards=0;
 char buf[2048];
 auto output_event=[&](const Event&e){
    while(!recent.empty() && recent.front().ms <e.ms-60000)recent.pop_front();
    ll q10=0,q60=0;double sumspread=0,first10=0,last10=0,travel10=0,first60=0,last60=0,travel60=0,maxjump10=0;
    bool seen10=false,seen60=false;
    for(const Quote&q:recent){if(q.ms>=e.ms)continue;
      if(q.ms>=e.ms-60000){q60++;sumspread+=q.spread;
        if(!seen60){first60=q.mid;last60=q.mid;seen60=true;}else{travel60+=fabs(q.mid-last60);last60=q.mid;}}
      if(q.ms>=e.ms-10000){q10++;
        if(!seen10){first10=q.mid;last10=q.mid;seen10=true;}else{double delta=fabs(q.mid-last10);travel10+=delta;maxjump10=std::max(maxjump10,delta);last10=q.mid;}}
    }
    const ll age=recent.empty()?-1:(e.ms-recent.back().ms);
    out<<e.row<<","<<e.ms<<","<<q10<<","<<q60<<","<<(q60?sumspread/q60:0.)/100.<<","<<(last10-first10)/100.<<","<<(last60-first60)/100.<<","<<travel10/100.<<","<<travel60/100.<<","<<maxjump10/100.<<","<<age;
    out<<b1.snapshot(e.ms,e.side)<<b5.snapshot(e.ms,e.side)<<b15.snapshot(e.ms,e.side)<<b30.snapshot(e.ms,e.side)<<"\n";
 };
 for(int j=3;j<argc;j++){
  gzFile f=gzopen(argv[j],"rb");if(!f){std::cerr<<"missing file "<<argv[j]<<"\n";return 5;}gzbuffer(f,1<<20);long long prior=ticknum;
  while(gzgets(f,buf,sizeof(buf))){
    if(strncmp(buf,"REAL,",5))continue;
    char*p=buf+5;ll ms=strtoll(p,&p,10);p=strchr(p,',');if(!p)continue;p=strchr(p+1,',');if(!p)continue;int bid=cents(p+1);p=strchr(p+1,',');if(!p)continue;int ask=cents(p+1);
    if(ms<prev_ms){++backwards;continue;}prev_ms=ms;
    while(idx<events.size()&&events[idx].ms<=ms)output_event(events[idx++]);
    const double mid=(bid+ask)*.5;
    recent.push_back({ms,mid,(double)(ask-bid)});
    while(!recent.empty() && recent.front().ms<ms-60000)recent.pop_front();
    b1.add(ms,mid*.01);b5.add(ms,mid*.01);b15.add(ms,mid*.01);b30.add(ms,mid*.01);++ticknum;
  }
  gzclose(f);std::cerr<<"SOURCE "<<argv[j]<<" scanned="<<ticknum-prior<<"\n";
 }
 while(idx<events.size())output_event(events[idx++]);
 std::cerr<<"CERT entries="<<idx<<" quotes="<<ticknum<<" reversals="<<backwards<<" barcounts="<<b1.v.size()<<","<<b5.v.size()<<","<<b15.v.size()<<","<<b30.v.size()<<"\n";
 if(backwards||ticknum!=7699274||idx!=27980)return 8;
 return 0;
}
