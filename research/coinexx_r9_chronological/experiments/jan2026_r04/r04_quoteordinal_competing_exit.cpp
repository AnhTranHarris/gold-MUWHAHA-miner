// R04 research-only: source-ordered Coinexx chronological replay, actual R9 0.01-lot 2 US-cent roundtrip fee.
// Frozen original book is NEVER read. Original R03 January fitted direction hazard provides as-of second scores.
// Counterfactual fills are on observed quote-side prices; stop execution latency/slippage NOT modelled.
#include <zlib.h>
#include <algorithm>
#include <array>
#include <cstdint>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
using I=std::int64_t;
struct Q{I sec=0,ms=0,bid=0,ask=0,ord=0;};
static I ci(const char*&p){char*e=nullptr;I v=strtoll(p,&e,10);if(e==p||(*e!=','&&*e!='\n'&&*e!='\r'&&*e!='\0'))throw std::runtime_error("csv integer");p=e+(*e==',');return v;}
static double cd(const char*&p){char*e=nullptr;double v=strtod(p,&e);if(e==p||(*e!=','&&*e!='\n'&&*e!='\r'&&*e!='\0'))throw std::runtime_error("csv decimal");p=e+(*e==',');return v;}
static Q quote(const char*s){const char*p=s;Q q;q.sec=ci(p);q.ms=ci(p);q.bid=llround(cd(p)*100);q.ask=llround(cd(p)*100);if(q.sec!=q.ms/1000||q.bid<=0||q.ask<q.bid)throw std::runtime_error("quote validation");return q;}
struct Sig{I sec=0,ms=0,bid=0,ask=0,phase=0,spread=0;double fb=0,fs=0,sb=0,ss=0;};
static Sig signal(const char*s){const char*p=s;Sig a;a.sec=ci(p);a.ms=ci(p);a.bid=ci(p);a.ask=ci(p);a.phase=ci(p);a.spread=ci(p);a.fb=cd(p);a.fs=cd(p);a.sb=cd(p);a.ss=cd(p);return a;}
struct Config {double f=.24,s=.23;int fee=2,spread=80,hardstop=30,hold=30,mode=1,second=1,opp=1;};
struct Pos{bool active=false;int side=0,leg=0;I ms=0,sec=0,ord=0,entry=0,best=std::numeric_limits<I>::min(),worst=std::numeric_limits<I>::max(),lastMark=0,prevMark=0,last_ms=0;double rollAbs=0,rollSigned=0;I qcount=0;};
int main(int argc,char**argv){try{
 if(argc<4)throw std::runtime_error("usage raw.gz preds.gz output.csv --mode=N --hardstop=N --hold=N --fee=N");
 Config c;for(int i=4;i<argc;i++){std::string a=argv[i];auto j=a.find('=');if(j==std::string::npos||a.substr(0,2)!="--")throw std::runtime_error("invalid option");auto k=a.substr(2,j-2);double v=std::stod(a.substr(j+1));if(k=="mode")c.mode=int(v);else if(k=="hardstop")c.hardstop=int(v);else if(k=="hold")c.hold=int(v);else if(k=="fee")c.fee=int(v);else if(k=="spread")c.spread=int(v);else if(k=="f")c.f=v;else if(k=="s")c.s=v;else if(k=="second")c.second=int(v);else if(k=="opp")c.opp=int(v);else throw std::runtime_error("unknown option "+k);}
 if(c.mode<0||c.mode>3||c.f<0||c.f>1||c.s<0||c.s>1||c.hardstop<=0||c.hold<=0||c.fee<0)throw std::runtime_error("configuration bounds");
 gzFile raw=gzopen(argv[1],"rb"),pred=gzopen(argv[2],"rb");if(!raw||!pred)throw std::runtime_error("original source or scores unreadable");
 char line[2048],ss[2048];if(!gzgets(raw,line,sizeof line)||std::strncmp(line,"time,time_msc,bid,ask,",22))throw std::runtime_error("source header mismatch");
 if(!gzgets(pred,ss,sizeof ss)||std::strncmp(ss,"sec,ms,bid_c,",13))throw std::runtime_error("score header mismatch");
 bool have=bool(gzgets(pred,ss,sizeof ss));Sig sig;if(have)sig=signal(ss);
 std::ofstream out(argv[3]);if(!out)throw std::runtime_error("output open");
 out<<"entry_ordinal,entry_time_msc,side,entry_price_cents,exit_ordinal,exit_time_msc,exit_price_cents,reason,net_quote_cents,net_cash_cents,leg,minute_id,peak_quote_cents,trough_quote_cents,quotes_held\n";
 I priorMs=-1,priorExitOrd=0,minute=-1,all=0,same=0,signals=0,complete=0,netSum=0,netWin=0,grossWin=0,loss=0,realizedRecoveries=0,stops=0,targets=0,phases=0,timeouts=0,orphan=0,noncausal=0;
 int first=0,second=0,firstSide=0;Pos p;
 while(gzgets(raw,line,sizeof line)){
  if(!std::strchr(line,'\n'))throw std::runtime_error("invalid raw line");
  Q q=quote(line);if(q.ms<priorMs)throw std::runtime_error("original tick order broken");if(q.ms==priorMs)++same;priorMs=q.ms;q.ord=++all;
  I m=q.sec/60;if(m!=minute){minute=m;first=0;second=0;firstSide=0;}
  if(p.active){
    I closeprice=p.side>0?q.bid:q.ask,mark=p.side*(closeprice-p.entry),spread=q.ask-q.bid,net=mark-c.fee;
    const I prev=p.lastMark;I delta=(p.qcount?mark-prev:0);p.rollAbs=.875*p.rollAbs+.125*std::abs(double(delta));p.rollSigned=.875*p.rollSigned+.125*double(delta);
    ++p.qcount;p.best=std::max(p.best,mark);p.worst=std::min(p.worst,mark);
    const I maxed=p.best,drawdown=maxed-mark,age=q.sec-p.sec;I sched=42;if(p.leg==1){const int ep=int(p.sec%60);sched=ep<=2?5:ep<=10?16:42;}
    int reason=0;const bool normal_phase=(q.sec/60==p.sec/60 && q.sec%60>=sched);
    // Three pre-registered, different, observable competing-exit mechanisms:
    // 1: profit first passage with quote-ordinal confirmed pullback; no synthetic path samples.
    // 2: original minute-phase paired with positive fee-adjusted quote and trailing source-path exhaustion.
    // 3: dynamic competing pressure: spread-normalized peak giveback + sign of smoothed recent quote renewal.
    if(mark<=-c.hardstop)reason=1;
    else if(c.mode==0){if(net>0)reason=2;}
    else if(c.mode==1){if(net>0 && p.qcount>1 && delta<0 && maxed>=spread+c.fee && drawdown>=std::max<I>(1,spread/3))reason=2;}
    else if(c.mode==2){if(normal_phase && net>0)reason=4;else if(net>0 && p.qcount>2 && maxed>=spread+c.fee && drawdown>=spread)reason=2;}
    else if(c.mode==3){const double pressure=p.rollAbs>0?(p.rollSigned/p.rollAbs):0.;const I refuge=std::max<I>(1,spread/2);
      if(net>0 && p.qcount>2 && maxed>=spread+c.fee && drawdown>=refuge && pressure<0)reason=2;
      else if(normal_phase && net>0 && pressure<0)reason=4;
    }
    if(!reason && age>=c.hold)reason=3;
    if(reason){++complete;netSum+=net;if(net>0)++netWin;else ++loss;if(mark>0)++grossWin;
      if(reason==1)++stops;else if(reason==2)++targets;else if(reason==4)++phases;else ++timeouts;
      out<<p.ord<<','<<p.ms<<','<<p.side<<','<<p.entry<<','<<q.ord<<','<<q.ms<<','<<closeprice<<','<<(reason==1?"source_stop":reason==2?"favorable_quote":reason==4?"phase_favorable":"timeout")<<','<<mark<<','<<net<<','<<p.leg<<','<<p.sec/60<<','<<p.best<<','<<p.worst<<','<<p.qcount<<'\n';
      if(p.leg==2)++realizedRecoveries;
      p.active=false;priorExitOrd=q.ord;
    } else {p.lastMark=mark;p.last_ms=q.ms;}
  }
  while(have&&sig.ms<q.ms){++orphan;have=bool(gzgets(pred,ss,sizeof ss));if(have)sig=signal(ss);}
  if(!have||sig.ms!=q.ms)continue;
  if(sig.bid!=q.bid||sig.ask!=q.ask)throw std::runtime_error("source-asof feature mismatch");
  ++signals;
  if(!p.active && q.ord>priorExitOrd && sig.spread<=c.spread){
   int side=0,leg=0;double f=std::max(sig.fb,sig.fs),s=std::max(sig.sb,sig.ss);
   if(!first&&sig.phase<=33&&f>=c.f){side=sig.fb>=sig.fs?1:-1;leg=1;}
   else if(c.second && first && !second && sig.phase>=15 && sig.phase<=46 && s>=c.s){side=sig.sb>=sig.ss?1:-1;leg=2;if(c.opp&&side==firstSide)side=0;}
   if(side){p=Pos{};p.active=true;p.side=side;p.leg=leg;p.ms=q.ms;p.sec=q.sec;p.ord=q.ord;p.entry=side>0?q.ask:q.bid;
    if(leg==1){first=1;firstSide=side;}else second=1;
   }
  }
  have=bool(gzgets(pred,ss,sizeof ss));if(have)sig=signal(ss);
 }
 if(p.active)++noncausal;
 if(gzclose(raw)!=Z_OK||gzclose(pred)!=Z_OK)throw std::runtime_error("source CRC failure");
 std::cerr<<"{\"source_ticks\":"<<all<<",\"same_ms\":"<<same<<",\"signal_seconds\":"<<signals<<",\"trades\":"<<complete<<",\"fee_positive\":"<<netWin<<",\"gross_positive\":"<<grossWin<<",\"negative_or_zero_fee\":"<<loss<<",\"cash_cents\":"<<netSum<<",\"entry_fee_roundtrip_cents\":"<<c.fee<<",\"stop\":"<<stops<<",\"favorable\":"<<targets<<",\"phase\":"<<phases<<",\"timeout\":"<<timeouts<<",\"unknown\":"<<noncausal<<",\"orphan\":"<<orphan<<"}\n";
 return 0;
 }catch(const std::exception&ex){std::cerr<<"FATAL "<<ex.what()<<'\n';return 1;}}
