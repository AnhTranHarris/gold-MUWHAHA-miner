// R04 research-only in-sample continuation: original R03 source-faithful replay plus causal entry admission meta-probability.
// Source-documented original R9 0.01 lot USD 0.02 roundtrip fee is applied in post-hoc cash accounting. No invented $0.20 fee.
// Predicted scores are derived from the *current/past* quote in source order; no original trade ledger read.
// Quote-side fill proxy at each observed original Bid/Ask, no slippage, no commission, no margin claims.
#include <zlib.h>
#include <cstdint>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <fstream>
#include <stdexcept>
#include <string>
#include <iostream>
#include <algorithm>
using I=std::int64_t;
struct Quote{I sec=0,ms=0,bid=0,ask=0,ordinal=0;};
static I cint(const char*&p){char*e=nullptr;I v=strtoll(p,&e,10);if(e==p||(*e!=','&&*e!='\n'&&*e!='\r'&&*e!='\0'))throw std::runtime_error("CSV integer");p=e+(*e==',');return v;}
static double cdouble(const char*&p){char*e=nullptr;double v=strtod(p,&e);if(e==p||(*e!=','&&*e!='\n'&&*e!='\r'&&*e!='\0'))throw std::runtime_error("CSV decimal");p=e+(*e==',');return v;}
static Quote parse_quote(const char*s){const char*p=s;Quote q;q.sec=cint(p);q.ms=cint(p);q.bid=llround(cdouble(p)*100);q.ask=llround(cdouble(p)*100);if(q.sec!=q.ms/1000||q.bid<=0||q.ask<q.bid)throw std::runtime_error("raw quote row mismatch");return q;}
struct Signal{I sec=0,ms=0,bid=0,ask=0,phase=0,spread=0;double fb=0,fs=0,sb=0,ss=0,risk1=0,risk2=0;};
static Signal parse_signal(const char *s){const char*p=s;Signal r;r.sec=cint(p);r.ms=cint(p);r.bid=cint(p);r.ask=cint(p);r.phase=cint(p);r.spread=cint(p);r.fb=cdouble(p);r.fs=cdouble(p);r.sb=cdouble(p);r.ss=cdouble(p);r.risk1=cdouble(p);r.risk2=cdouble(p);return r;}
struct Config {double meta=0,f=.65,s=.60;int spread=60,pt=15,sl=180,hold=30,second=1,clock=0;bool opp=true;};
struct Position{bool open=false;int side=0,leg=0;I ms=0,sec=0,ordinal=0,entry=0,sl=0;};
struct Stats{I quotes=0,same=0,signals=0,trades=0,wins=0,loss=0,flat=0,recovery=0,netsum=0,stops=0,targets=0,timeout=0,unknown=0;};
int main(int argc,char**argv){try{
 if(argc<4)throw std::runtime_error("usage: raw.gz predicted_scores.gz trades.csv [--f=.65 --s=.6 --spread=60 --pt=15 --sl=180 --hold=30 --second=1 --opp=1]");
 Config c;for(int i=4;i<argc;++i){const std::string a=argv[i];auto p=a.find('=');if(p==std::string::npos||a.substr(0,2)!="--")throw std::runtime_error("bad flag");auto key=a.substr(2,p-2);double v=std::stod(a.substr(p+1));if(key=="meta")c.meta=v;else if(key=="f")c.f=v;else if(key=="s")c.s=v;else if(key=="spread")c.spread=int(v);else if(key=="pt")c.pt=int(v);else if(key=="sl")c.sl=int(v);else if(key=="hold")c.hold=int(v);else if(key=="second")c.second=int(v);else if(key=="clock")c.clock=int(v);else if(key=="opp")c.opp=(v!=0);else throw std::runtime_error("unknown option");}
 if(c.f<0||c.f>1||c.meta<0||c.meta>1||c.s<0||c.s>1||c.pt<=0||c.sl<=0||c.hold<=0)throw std::runtime_error("config range");
 gzFile raw=gzopen(argv[1],"rb"),pred=gzopen(argv[2],"rb");if(!raw||!pred)throw std::runtime_error("cannot open inputs");
 std::ofstream book(argv[3]);if(!book)throw std::runtime_error("cannot output");
 book<<"entry_ordinal,entry_time_msc,side,entry_price_cents,exit_ordinal,exit_time_msc,exit_price_cents,reason,net_quote_cents,leg,minute_id\n";
 char line[2048],signalLine[2048];if(!gzgets(raw,line,sizeof line)||std::strncmp(line,"time,time_msc,bid,ask,",22)!=0)throw std::runtime_error("bad raw header");
 if(!gzgets(pred,signalLine,sizeof signalLine)||std::strncmp(signalLine,"sec,ms,bid_c,",13)!=0)throw std::runtime_error("bad score header");
 Signal signal{};bool have=bool(gzgets(pred,signalLine,sizeof signalLine));if(have)signal=parse_signal(signalLine);
 Stats st;Position p;I lastms=-1,minute=-1,previous_exit_ord=-1;int first_taken=0,second_taken=0,first_side=0;bool first_loss=false;
 while(gzgets(raw,line,sizeof line)){
   if(!strchr(line,'\n'))throw std::runtime_error("raw truncated");
   Quote q=parse_quote(line);if(lastms>q.ms)throw std::runtime_error("raw nonmonotonic");if(lastms==q.ms)++st.same;lastms=q.ms;q.ordinal=++st.quotes;
   I m=q.sec/60; if(minute!=m){minute=m;first_taken=0;second_taken=0;first_side=0;first_loss=false;}
   if(p.open){
      I mark=p.side>0?q.bid:q.ask;I net=p.side*(mark-p.entry);
      int reason=0;
      if(net<=-c.sl)reason=1;
      else if(c.clock==0 && net>=c.pt)reason=2;
      else if(c.clock!=0){
       int scheduled=42;
       if(p.leg==1){int ep=int(p.sec%60);scheduled=ep<=2?5:ep<=10?16:42;}
       // This schedule is trained only from historical January phase patterns,
       // but the trade engine does not reference any original trade/exit labels.
       const bool same_min=q.sec/60==p.sec/60;
       const int phase=int(q.sec%60);
       if(c.clock==1){
         if(same_min && phase>=scheduled && q.sec>p.sec)reason=4;
       }else if(c.clock==2){
         if(same_min && phase>=scheduled-1 && phase<=scheduled+3 && net>=c.pt)reason=4;
         else if((!same_min || phase>scheduled+3) && net>=c.pt)reason=2;
       }else if(c.clock==3){
         if(same_min && phase>=scheduled-2 && net>=c.pt)reason=4;
       }else if(c.clock==4){
         if(same_min && phase>=scheduled-2 && net>=0)reason=4;
         else if((!same_min || phase>scheduled+2) && net>=c.pt)reason=2;
       }
       if(!reason && q.sec-p.sec>=c.hold)reason=3;
      }else if(q.sec-p.sec>=c.hold)reason=3;
      if(reason){st.trades++;if(net>0)st.wins++;else if(net<0)st.loss++;else st.flat++;st.netsum+=net;
       if(reason==1)st.stops++;else if(reason==2)st.targets++;else st.timeout++;
       book<<p.ordinal<<','<<p.ms<<','<<p.side<<','<<p.entry<<','<<q.ordinal<<','<<q.ms<<','<<mark<<','<<(reason==1?"stop":reason==2?"target":reason==4?"phase_clock":"timeout")<<','<<net<<','<<p.leg<<','<<p.sec/60<<'\n';
       first_loss=p.leg==1 && net<0; if(p.leg==2)++st.recovery;p.open=false;previous_exit_ord=q.ordinal;
      }
   }
   // Every signal originates at the first quote of the exact source second. No lookahead, no interpolation.
   while(have&&signal.ms<q.ms){++st.unknown;have=bool(gzgets(pred,signalLine,sizeof signalLine));if(have)signal=parse_signal(signalLine);}
   if(!have||signal.ms!=q.ms)continue;
   if(signal.bid!=q.bid||signal.ask!=q.ask)throw std::runtime_error("Causal score quote mismatch");
   ++st.signals;
   if(!p.open&&q.ordinal>previous_exit_ord&&signal.spread<=c.spread){
     int side=0,leg=0;
     const double f=std::max(signal.fb,signal.fs),s=std::max(signal.sb,signal.ss);
     if(!first_taken && signal.phase<=33 && f>=c.f && signal.risk1>=c.meta){side=signal.fb>=signal.fs?1:-1;leg=1;}
     else if(c.second && first_taken && !second_taken && signal.phase>=15 && signal.phase<=46 && s>=c.s && signal.risk2>=c.meta && (c.second!=2||first_loss)){
       side=signal.sb>=signal.ss?1:-1;leg=2;if(c.opp&&side==first_side)side=0;
     }
     if(side){p.open=true;p.side=side;p.leg=leg;p.ms=q.ms;p.sec=q.sec;p.ordinal=q.ordinal;p.entry=side>0?q.ask:q.bid;
       if(leg==1){first_taken=1;first_side=side;}else second_taken=1;
     }
   }
   have=bool(gzgets(pred,signalLine,sizeof signalLine));if(have)signal=parse_signal(signalLine);
 }
 if(p.open)++st.unknown;
 if(gzclose(raw)!=Z_OK||gzclose(pred)!=Z_OK)throw std::runtime_error("gzip checksum");
 std::cerr<<"{\"source_ticks\":"<<st.quotes<<",\"same_ms\":"<<st.same<<",\"candidate_signal_seconds\":"<<st.signals<<",\"trades\":"<<st.trades<<",\"positive\":"<<st.wins<<",\"negative\":"<<st.loss<<",\"flat\":"<<st.flat<<",\"recovery\":"<<st.recovery<<",\"net_quote_cents\":"<<st.netsum<<",\"stops\":"<<st.stops<<",\"targets\":"<<st.targets<<",\"timeouts\":"<<st.timeout<<",\"unknown\":"<<st.unknown<<"}\n";
 return 0;
 }catch(const std::exception &ex){std::cerr<<"ERROR: "<<ex.what()<<'\n';return 1;}}
