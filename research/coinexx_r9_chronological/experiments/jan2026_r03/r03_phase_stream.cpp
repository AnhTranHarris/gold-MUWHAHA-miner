// R03 phase-aware first-observed-quote-per-second features; no historical labels are read.
// Single source-order scan. The quote in the row is currently observable. All historical bars are completed.
#include <zlib.h>
#include <deque>
#include <string>
#include <fstream>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <cstdio>
#include <iostream>
using I=int64_t;
struct T { I sec,ms,bid,ask; };
static T parse(char*line){T t;char*p=nullptr;t.sec=strtoll(line,&p,10);if(*p!=',')throw std::runtime_error("sec");t.ms=strtoll(p+1,&p,10);if(*p!=',')throw std::runtime_error("ms");t.bid=llround(strtod(p+1,&p)*100);if(*p!=',')throw std::runtime_error("bid");t.ask=llround(strtod(p+1,&p)*100);if(t.sec!=t.ms/1000||t.ask<t.bid||t.bid<=0)throw std::runtime_error("bad source quote");return t;}
struct Bar {I time=0,op=0,hi=0,lo=0,cl=0,n=0;};
struct TF {I dur;Bar cur{},last{};bool ready=false,opened=false;double atr=-1,seed=0;I prior=0;int nseed=0;TF(I d):dur(d){}
 void feed(T t){I start=t.sec/dur*dur;if(!opened){cur={start,t.bid,t.bid,t.bid,t.bid,1};opened=true;return;}
 if(start!=cur.time){last=cur;ready=true;double tr=prior?std::max({double(cur.hi-cur.lo),std::abs(double(cur.hi-prior)),std::abs(double(cur.lo-prior))}):double(cur.hi-cur.lo);
   if(atr<0){seed+=tr;if(++nseed>=14)atr=seed/14.;}else atr=(atr*13.+tr)/14.;prior=cur.cl;cur={start,t.bid,t.bid,t.bid,t.bid,1};return;}
 cur.hi=std::max(cur.hi,t.bid);cur.lo=std::min(cur.lo,t.bid);cur.cl=t.bid;++cur.n;}
};
struct S{I sec,bid,hi,lo,quotes;};
int main(int argc,char**argv){try{if(argc!=3)throw std::runtime_error("in.gz out.gz");gzFile in=gzopen(argv[1],"rb"),out=gzopen(argv[2],"wb1");if(!in||!out)throw std::runtime_error("open");
 const char* header="sec,ms,bid_c,ask_c,phase,minute,hour,spread_c,gap_ms,minute_disp,minute_range,minute_ticks,m1_disp,m5_disp,m15_disp,h1_disp,m5_atr,m15_atr,h1_atr,ret1,ret5,ret10,ret20,ret30,ret60,ret300,eff10,eff30,eff60,range10,range60,quotes10,quotes60,quote_imbalance10,m5_position,m15_position,h1_position\n";
 if(gzputs(out,header)<0)throw std::runtime_error("gzip header");
 char s[2048];if(!gzgets(in,s,sizeof s)||std::strncmp(s,"time,time_msc,bid,ask,",22))throw std::runtime_error("source header");
 TF m1(60),m5(300),m15(900),h1(3600);std::deque<S> history;S cur{};bool active=false;I ord=0,lastms=-1,rows=0,samems=0;
 auto prior=[&](I sec,I delay)->I {I target=sec-delay;for(auto it=history.rbegin();it!=history.rend();++it)if(it->sec<=target)return it->bid;return 0;};
 while(gzgets(in,s,sizeof s)){if(!strchr(s,'\n'))throw std::runtime_error("bad line");T t=parse(s);if(lastms>t.ms)throw std::runtime_error("nonmonotonic");if(lastms==t.ms)++samems;I lag=lastms<0?0:t.ms-lastms;++ord;
 if(active&&t.sec==cur.sec){cur.bid=t.bid;cur.hi=std::max(cur.hi,t.bid);cur.lo=std::min(cur.lo,t.bid);++cur.quotes;
 m1.feed(t);m5.feed(t);m15.feed(t);h1.feed(t);lastms=t.ms;continue;}
 if(active){history.push_back(cur);while(!history.empty()&&history.front().sec<t.sec-301)history.pop_front();}
 cur={t.sec,t.bid,t.bid,t.bid,1};active=true;m1.feed(t);m5.feed(t);m15.feed(t);h1.feed(t);
 double travel10=0,travel30=0,travel60=0;I high10=0,low10=0,high60=0,low60=0,n10=0,n60=0,up10=0,down10=0;
 I prev=0;
 for(auto it=history.rbegin();it!=history.rend();++it){I age=t.sec-it->sec;if(age>60)break;
  if(age<=10){high10=std::max(high10,it->hi);low10=low10?std::min(low10,it->lo):it->lo;n10+=it->quotes;}
  high60=std::max(high60,it->hi);low60=low60?std::min(low60,it->lo):it->lo;n60+=it->quotes;
  if(prev){const double d=double(prev-it->bid);if(age<=10){travel10+=fabs(d);if(d>0)++up10;else if(d<0)++down10;}if(age<=30)travel30+=fabs(d);travel60+=fabs(d);}prev=it->bid;
 }
 I c1=prior(t.sec,1),c5=prior(t.sec,5),c10=prior(t.sec,10),c20=prior(t.sec,20),c30=prior(t.sec,30),c60=prior(t.sec,60),c300=prior(t.sec,300);
 const auto r=[&](I old)->I{return old?t.bid-old:0;};
 const double e10=travel10?std::abs(double(r(c10)))/travel10:0,e30=travel30?std::abs(double(r(c30)))/travel30:0,e60=travel60?std::abs(double(r(c60)))/travel60:0;
 const double loc5=m5.ready?double(t.bid-m5.last.cl):0,loc15=m15.ready?double(t.bid-m15.last.cl):0,loch1=h1.ready?double(t.bid-h1.last.cl):0;
 char line[1024];int n=snprintf(line,sizeof line,"%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%.4f,%.4f,%.4f,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%.5f,%.5f,%.5f,%lld,%lld,%lld,%lld,%.5f,%.4f,%.4f,%.4f\n",
 (long long)t.sec,(long long)t.ms,(long long)t.bid,(long long)t.ask,(long long)(t.sec%60),(long long)((t.sec/60)%60),(long long)((t.sec/3600)%24),(long long)(t.ask-t.bid),(long long)lag,
 (long long)(t.bid-m1.cur.op),(long long)(m1.cur.hi-m1.cur.lo),(long long)m1.cur.n,
 (long long)(m1.ready?m1.last.cl-m1.last.op:0),(long long)(m5.ready?m5.last.cl-m5.last.op:0),(long long)(m15.ready?m15.last.cl-m15.last.op:0),(long long)(h1.ready?h1.last.cl-h1.last.op:0),
 m5.atr,m15.atr,h1.atr,(long long)r(c1),(long long)r(c5),(long long)r(c10),(long long)r(c20),(long long)r(c30),(long long)r(c60),(long long)r(c300),
 e10,e30,e60,(long long)(high10?high10-low10:0),(long long)(high60?high60-low60:0),(long long)n10,(long long)n60,
 (up10+down10)?double(up10-down10)/double(up10+down10):0.,loc5,loc15,loch1);
 if(n<=0||n>=int(sizeof line)||gzwrite(out,line,unsigned(n))!=n)throw std::runtime_error("gzip write");
 ++rows;lastms=t.ms;
 }
 if(gzclose(in)!=Z_OK||gzclose(out)!=Z_OK)throw std::runtime_error("gzip corruption");
 std::cerr<<"{\"ticks\":"<<ord<<",\"same_ms\":"<<samems<<",\"seconds\":"<<rows<<"}\n";
 return 0;}catch(const std::exception&ex){std::cerr<<"ERROR "<<ex.what()<<'\n';return 1;}}
