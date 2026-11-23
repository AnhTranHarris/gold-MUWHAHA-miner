// Research-only R9 HybridGate v1.90 REAL-tick chronological replay.
// Independent C++17 translation of the pinned Python causal state machine.
// Original raw Coinexx ticks are read-only; synthetic book timestamps are NOT engine inputs.
// No broker execution, commission, margin, financing, queue or partial-fill model is implied.
#include <zlib.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <deque>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using i64 = int64_t;
struct Tick { i64 ms, bid, ask, ordinal; i64 sec() const {return ms/1000;} };
struct Sbar { i64 sec, h, l, c; };
struct Config {
 int gap=30, stop=30, trail=3, activation=10, hold=30, rearm=3, vel=10, range=10, minvel=15, minrange=50, maxturn=9, spread=25, atr_period=14, router=0;
 double eff=0.7, atr_multiplier=1.0;
 bool no_atr=false,no_trail=false;
};
struct Stats {
 i64 ticks=0,same_ms=0, entries=0, stopped=0, timed=0, targeted=0, rearmed=0, trails=0, gate_spread=0, gate_no_atr=0, gate_low_atr=0, gate_s1=0, positive=0, negative=0, flat=0;
 i64 net_c=0; i64 first=0,last=0;
};
static i64 rounded(double v){return (i64)std::llround(v*100.);}
static bool parse(const char* row,Tick& t){
 char *p=nullptr; errno=0;i64 sec=std::strtoll(row,&p,10);if(errno || *p!=',')return false;
 i64 ms=std::strtoll(p+1,&p,10);if(errno || *p!=',')return false;
 double bid=std::strtod(p+1,&p);if(errno || *p!=',')return false;
 double ask=std::strtod(p+1,&p);if(errno || *p!=',')return false;
 if(sec!=ms/1000 || !std::isfinite(bid) || !std::isfinite(ask) || bid<=0 || ask<bid)return false;
 t.ms=ms;t.bid=rounded(bid);t.ask=rounded(ask);return t.bid>0 && t.ask>=t.bid;
}
static int weekday(int year,int month,int day){ // Sakamoto; 0 is Sunday
 static const int offsets[]={0,3,2,5,0,3,5,1,4,6,2,4}; if(month<3) --year;
 return (year+year/4-year/100+year/400+offsets[month-1]+day)%7;
}
static bool leap(int y){return (y%400==0)||(y%4==0 && y%100!=0);}
static int last_sunday(int y,int m){int len=(m==2?(leap(y)?29:28):(m==4||m==6||m==9||m==11?30:31));return len-weekday(y,m,len);}
static int nth_sunday(int y,int m,int n){return 1+(7-weekday(y,m,1))%7+7*(n-1);}
static i64 stamp_utc(int y,int mo,int day,int hr){
 std::tm q{};q.tm_year=y-1900;q.tm_mon=mo-1;q.tm_mday=day;q.tm_hour=hr;
 return (i64)timegm(&q);
}
static int source_session(i64 minute){
 std::time_t u=std::time_t(minute);std::tm g{};gmtime_r(&u,&g);int y=g.tm_year+1900;
 bool london_dst=(minute>=stamp_utc(y,3,last_sunday(y,3),1)&&minute<stamp_utc(y,10,last_sunday(y,10),1));
 bool ny_dst=(minute>=stamp_utc(y,3,nth_sunday(y,3,2),7)&&minute<stamp_utc(y,11,nth_sunday(y,11,1),6));
 int lond=(g.tm_hour*60+g.tm_min+(london_dst?60:0))%1440;
 int ny=(g.tm_hour*60+g.tm_min+(ny_dst?-240:-300)+1440)%1440;
 bool l=lond>=8*60 && lond<16*60+30;
 bool n=ny>=8*60 && ny<17*60;
 return l&&n?2:l?1:n?3:0;
}
struct Atr {
 i64 bucket=-1, high=0,low=0,close=0,previous_close=-1;
 int completed=0,seed_n=0,period=14;double seed_sum=0, atr=-1;
 explicit Atr(int n):period(n){}
 void update(const Tick&t){i64 k=(t.sec()/300)*300;
  if(bucket==-1){bucket=k; high=low=close=t.bid;return;}
  if(k==bucket){high=std::max(high,t.bid);low=std::min(low,t.bid);close=t.bid;return;}
  if(previous_close>=0){i64 tr=std::max<i64>({high-low,std::llabs(high-previous_close),std::llabs(low-previous_close)});
   if(atr<0){seed_sum+=tr;++seed_n;if(seed_n==period)atr=seed_sum/period;}
   else atr=(atr*(period-1)+tr)/period;
  }
  ++completed;previous_close=close;bucket=k;high=low=close=t.bid;
 }
 bool ready() const {return atr>=0 && completed>=period+2;}
};
struct Pos {int side=0; i64 enter_ms=0,enter_s=0,ord=0,entry=0,sl=0,initial_sl=0;int rearm_number=0;};
struct Anchor {int row=0,side=0,leg=0; i64 start=0;double booked=0;};
struct Snapshot {Anchor ref; i64 first_ms=0,last_ms=0;int quote_count=0,first_flags=0,any_flags=0,last_flags=0;double atr_u=-1,atr_min_u=-1;int spread_u=-1,bar_dist_u=0,second_age=-1;int original_gate_candidates=0, executable_candidates=0,blocked_occupancy=0,blocked_rearm=0;double s1_disp_c=0,s1_eff=0,s1_range_c=0;int s1_turns=0;};
static std::vector<Anchor> load_anchors(const std::string& path){
 std::vector<Anchor> out;std::ifstream f(path);if(!f)throw std::runtime_error("cannot read anchor manifest");
 std::string line;if(!std::getline(f,line))throw std::runtime_error("empty anchor manifest");
 if(line.rfind("row,role,side,entry_sec,exit_sec,",0)!=0)throw std::runtime_error("unrecognized anchor manifest");
 while(std::getline(f,line)) {std::stringstream ss(line);std::string c;std::vector<std::string> x;
  while(std::getline(ss,c,',')) {x.push_back(c);if(x.size()>=7)break;}
  if(x.size()<7)throw std::runtime_error("bad anchor line");
  Anchor a; a.row=std::stoi(x[0]);a.side=x[2]=="BUY"?1:x[2]=="SELL"?-1:0;
  if(!a.side)throw std::runtime_error("bad anchor side");
  a.start=std::stoll(x[3]);a.booked=std::stod(x[5]);a.leg=std::stoi(x[6]);
  if(!out.empty() && a.start<=out.back().start)throw std::runtime_error("unsorted/duplicate anchor second");
  out.push_back(a);
 }
 return out;
}

class R9 {
 Config c;Stats& st;std::ostream& trades;
 i64 bucket_second=-1,bucket_hi=0,bucket_lo=0,bucket_cl=0;
 std::deque<Sbar> seconds;
 Atr atr;
 i64 minute=0,cycle_buy=0,cycle_sell=0;
 i64 minute_open_bid=0,minute_last_bid=0,completed_m1_disp=0;
 bool seen_upper=false,seen_lower=false;
 int routed_cont=0,routed_reject=0;
 int pending=0, rearms=0,last_position_side=1;
 bool had_position=false,has_position=false,last_close_negative=false;
 Pos pos;
 double current_atr_min=250;
 std::vector<Anchor> reference; size_t ref_idx=0; std::ostream* diag=nullptr; Snapshot snap;
 void flush_snapshot(){
  if(!diag || !snap.ref.row)return;
  const Snapshot& q=snap;
  *diag<<q.ref.row<<','<<q.ref.start<<','<<q.ref.side<<','<<q.ref.leg<<','<<std::fixed<<std::setprecision(2)<<q.ref.booked<<','<<q.first_ms<<','<<q.last_ms<<','<<q.quote_count<<','<<q.first_flags<<','<<q.any_flags<<','<<q.last_flags<<','<<q.atr_u<<','<<q.atr_min_u<<','<<q.spread_u<<','<<q.bar_dist_u<<','<<q.second_age<<','<<q.original_gate_candidates<<','<<q.executable_candidates<<','<<q.blocked_occupancy<<','<<q.blocked_rearm<<','<<q.s1_disp_c<<','<<std::setprecision(12)<<q.s1_eff<<','<<std::setprecision(2)<<q.s1_range_c<<','<<q.s1_turns<<'\n';
  snap=Snapshot{};
 }
 void observe(const Tick&t){
  if(!diag)return;
  while(ref_idx<reference.size() && reference[ref_idx].start<t.sec()){
   if(snap.ref.row==0) snap.ref=reference[ref_idx];
   flush_snapshot(); ++ref_idx;
  }
  if(ref_idx>=reference.size() || reference[ref_idx].start!=t.sec())return;
  if(!snap.ref.row)snap.ref=reference[ref_idx];
  const bool s1=quality(snap.ref.side);
  if(snap.quote_count==0 && (int)seconds.size()>=std::max(c.vel,c.range)+1){
    int n=(int)seconds.size(),start=n-c.vel;
    i64 disp=seconds.back().c-seconds[start].c,travel=0;
    int prior=0,turns=0;
    for(int k=start+1;k<n;++k){i64 d=seconds[k].c-seconds[k-1].c;travel+=std::llabs(d);int sg=d>0?1:d<0?-1:0;
      if(sg){if(prior&&sg!=prior)++turns;prior=sg;}}
    i64 hi=std::numeric_limits<i64>::min(),lo=std::numeric_limits<i64>::max();
    for(int k=n-c.range;k<n;++k){hi=std::max(hi,seconds[k].h);lo=std::min(lo,seconds[k].l);}
    snap.s1_disp_c=double(disp);snap.s1_eff=std::fabs(double(disp))/(double(travel)+1e-9);snap.s1_range_c=double(hi-lo);snap.s1_turns=turns;
  }
  const bool spread_pass=(t.ask-t.bid<=c.spread || c.no_atr);
  const bool atr_ready=atr.ready();
  const bool atr_pass=atr_ready && (atr.atr+1e-12 >= current_atr_min*c.atr_multiplier);
  const bool bracket=snap.ref.side>0?t.ask>=cycle_buy:t.bid<=cycle_sell;
  const bool pend_ok=pending==2 || pending==snap.ref.side;
  const bool slot_free=!has_position && !had_position;
  const bool fully=s1 && spread_pass && (c.no_atr || atr_pass) && bracket;
  const bool executive=fully && pend_ok && slot_free;
  int flags=1;
  if(atr_ready)flags|=2;
  if(atr_pass)flags|=4;
  if(spread_pass)flags|=8;
  if(bracket)flags|=16;
  if(s1)flags|=32;
  if(fully)flags|=64;
  if(has_position)flags|=128;
  if(had_position)flags|=256;
  if(pend_ok)flags|=512;
  if(executive)flags|=1024;
  if(slot_free)flags|=2048;
  if(snap.quote_count==0){snap.first_ms=t.ms;snap.first_flags=flags;snap.atr_u=atr.atr;snap.atr_min_u=current_atr_min;
   snap.spread_u=int(t.ask-t.bid);snap.bar_dist_u=int(snap.ref.side>0?t.ask-cycle_buy:cycle_sell-t.bid);
   snap.second_age=seconds.empty()?-1:int(t.sec()-seconds.back().sec);
  }
  ++snap.quote_count;snap.last_ms=t.ms;snap.any_flags|=flags;snap.last_flags=flags;
  if(fully){++snap.original_gate_candidates;if(!slot_free)++snap.blocked_occupancy;else if(!pend_ok)++snap.blocked_rearm;}
  if(executive)++snap.executable_candidates;
 }

 void close(const Tick&t,int reason){
  i64 exit=t.bid;if(pos.side<0)exit=t.ask;
  i64 net=(exit-pos.entry)*pos.side;
  if(net>0)++st.positive;else if(net<0)++st.negative;else ++st.flat;
  st.net_c+=net;last_close_negative=(net<0);
  if(reason==1)++st.stopped;else if(reason==3)++st.targeted;else ++st.timed;
  trades<<pos.ord<<','<<pos.enter_ms<<','<<pos.side<<','<<pos.entry<<','<<pos.initial_sl<<','<<t.ordinal<<','<<t.ms<<','<<exit<<','<<(reason==1?"stop":reason==3?"target":"timeout")<<','<<net<<','<<pos.rearm_number<<'\n';
  has_position=false;
 }
 void update_sec(const Tick&t){i64 s=t.sec();
  if(bucket_second<0){bucket_second=s;bucket_hi=bucket_lo=bucket_cl=t.bid;return;}
  if(s==bucket_second){bucket_hi=std::max(bucket_hi,t.bid);bucket_lo=std::min(bucket_lo,t.bid);bucket_cl=t.bid;return;}
  seconds.push_back(Sbar{bucket_second,bucket_hi,bucket_lo,bucket_cl});if(seconds.size()>128)seconds.pop_front();
  bucket_second=s;bucket_hi=bucket_lo=bucket_cl=t.bid;
 }
 bool quality(int side) const{
  int need=std::max(c.vel,c.range)+1;
  if((int)seconds.size()<need)return false;
  int n=(int)seconds.size(),start=n-c.vel;
  i64 disp=seconds.back().c-seconds[start].c;
  i64 travel=0;int prior_sign=0,turns=0;
  for(int j=start+1;j<n;++j){i64 delta=seconds[j].c-seconds[j-1].c;travel+=std::llabs(delta);int sg=delta>0?1:delta<0?-1:0;
   if(sg){if(prior_sign&&sg!=prior_sign)++turns;prior_sign=sg;}}
  double eff=std::fabs(double(disp))/(double(travel)+1e-9);
  i64 h=std::numeric_limits<i64>::min(),l=std::numeric_limits<i64>::max();
  for(int j=n-c.range;j<n;++j){h=std::max(h,seconds[j].h);l=std::min(l,seconds[j].l);}
  return eff+1e-12>=c.eff && turns<=c.maxturn && h-l>=c.minrange && (side>0?disp>=c.minvel:disp<=-c.minvel);
 }
 bool gate(const Tick&t){
  if(c.no_atr)return true;
  if(c.spread>0 && t.ask-t.bid>c.spread){++st.gate_spread;return false;}
  if(!atr.ready()){++st.gate_no_atr;return false;}
  if(atr.atr+1e-12<current_atr_min*c.atr_multiplier){++st.gate_low_atr;return false;}
  return true;
 }
 void cycle(const Tick&t){i64 m=t.sec()-t.sec()%60;
  if(m==minute){minute_last_bid=t.bid;return;}
  if(minute!=0)completed_m1_disp=minute_last_bid-minute_open_bid;
  minute=m;minute_open_bid=minute_last_bid=t.bid;seen_upper=false;seen_lower=false;rearms=0;pending=2;
  cycle_buy=(t.bid+t.ask+c.gap+1)/2;
  cycle_sell=(t.bid+t.ask-c.gap+1)/2;
  int s=source_session(minute);current_atr_min=s==2||s==3?175:s==1?200:250;
 }
 void manage(const Tick&t){
  if(c.router){
   i64 profit=(pos.side>0?t.bid-pos.entry:pos.entry-t.ask);
   i64 target=c.router==1?85:75;
   if(profit>=target){close(t,3);return;}
  }
  if(t.sec()-pos.enter_s>=c.hold){close(t,2);return;}
  if(c.no_trail || c.trail<=0)return;
  i64 trail=std::max((c.router?25:c.trail),1);
  if(pos.side>0 && t.bid-pos.entry>=(c.router?55:c.activation)){
   i64 cand=t.bid-trail; cand=std::min(cand,t.bid-1);
   if(double(cand)>double(pos.sl)+.5){pos.sl=cand;++st.trails;}
  } else if(pos.side<0 && pos.entry-t.ask>=(c.router?55:c.activation)){
   i64 cand=t.ask+trail; cand=std::max(cand,t.ask+1);
   if(double(cand)<double(pos.sl)-.5){pos.sl=cand;++st.trails;}
  }
 }
 public:
 explicit R9(Config conf,Stats& stats,std::ostream&os,std::vector<Anchor> anchors={},std::ostream* diagout=nullptr):c(conf),st(stats),trades(os),atr(conf.atr_period),reference(std::move(anchors)),diag(diagout){
  if(diag)*diag<<"row,entry_sec,side,leg,original_booked_net_usd,first_quote_ms,last_quote_ms,quote_count,first_flags,any_flags,last_flags,first_atr_cents,session_atr_min_cents,first_spread_cents,first_bracket_touch_margin_cents,age_last_completed_second_s,signal_candidate_tick_count,executable_candidate_tick_count,blocked_by_occupancy_tick_count,blocked_by_rearm_tick_count,s1_disp_cents,s1_efficiency,s1_range_cents,s1_turns\n";
 }
 void flush_remaining(){while(ref_idx<reference.size()){if(!snap.ref.row)snap.ref=reference[ref_idx];flush_snapshot();++ref_idx;}}

 void on_tick(const Tick&t){
  // The server-side SL is assessed BEFORE the EA receives this quote.
  if(has_position && ((pos.side>0 && t.bid<=pos.sl)||(pos.side<0 && t.ask>=pos.sl)))close(t,1);
  update_sec(t);atr.update(t);cycle(t);observe(t);
  // Update breakout flags ONLY after observation so no same-tick path look-ahead.
  if(t.ask>=cycle_buy)seen_upper=true;
  if(t.bid<=cycle_sell)seen_lower=true;
  if(has_position){had_position=true;last_position_side=pos.side;manage(t);return;}
  if(had_position){had_position=false;
   if(t.sec()-t.sec()%60==minute){if((c.router==3 && !last_close_negative)||rearms>=c.rearm)pending=0;
    else{++rearms;pending=last_position_side<0?1:-1;++st.rearmed;}}
   else pending=0;
   return;
  }
  if(!pending || !gate(t))return;
  int side=0;
  if(c.router==0){
   if((pending==2||pending==1) && t.ask>=cycle_buy)side=1;
   else if((pending==2||pending==-1) && t.bid<=cycle_sell)side=-1;
   if(!side)return;
   if(!quality(side)){++st.gate_s1;return;}
  }else if(c.router==1||c.router==3){
   // CONT: prior completed M1 directional displacement plus completed last-5-second bid trend.
   if(seconds.size()<7)return;
   i64 displacement=seconds.back().c-seconds[seconds.size()-5].c;
   i64 travel=0;for(size_t i=seconds.size()-4;i<seconds.size();++i)travel+=std::llabs(seconds[i].c-seconds[i-1].c);
   double efficiency=std::fabs(double(displacement))/(double(travel)+1e-9);
   if((pending==2||pending==1)&&t.ask>=cycle_buy && displacement>=20 && completed_m1_disp>=20 && efficiency>=0.55)side=1;
   else if((pending==2||pending==-1)&&t.bid<=cycle_sell && displacement<=-20 && completed_m1_disp<=-20 && efficiency>=0.55)side=-1;
   if(!side && c.router==3 && std::llabs(completed_m1_disp)<20){
    const i64 mid=(cycle_buy+cycle_sell)/2;
    i64 rev=seconds.back().c-seconds[seconds.size()-4].c;
    if(seen_lower && t.bid>=mid+10 && rev>=15 && (pending==2||pending==1))side=1;
    else if(seen_upper && t.ask<=mid-10 && rev<=-15 && (pending==2||pending==-1))side=-1;
   }
   if(!side)return;
   // In hybrid conditional recovery, a second leg requires a previous REAL losing exit
   // and three completed observed seconds of confirmation in its proposed direction.
   if(c.router==3 && rearms>0){
    i64 rev=seconds.back().c-seconds[seconds.size()-4].c;
    if(!last_close_negative || rev*side<15)return;
   }
   ++routed_cont;
  }else{
   // REJECT: only after genuine crossed minute bracket and causal return to opposite side of minute midpoint.
   if(seconds.size()<5)return;
   i64 dis=seconds.back().c-seconds[seconds.size()-4].c;
   const i64 mid=(cycle_buy+cycle_sell)/2;
   if(seen_lower && t.bid>=mid+10 && dis>=15 && (pending==2||pending==1))side=1;
   else if(seen_upper && t.ask<=mid-10 && dis<=-15 && (pending==2||pending==-1))side=-1;
   if(!side)return;
   ++routed_reject;
  }
  i64 sd=std::max((c.router?75:c.stop),1);
  pos=Pos{side,t.ms,t.sec(),t.ordinal,side>0?t.ask:t.bid,side>0?t.bid-sd:t.ask+sd,side>0?t.bid-sd:t.ask+sd,rearms};
  has_position=true;pending=0;++st.entries;
 }
};
int main(int argc,char**argv){try{
 if(argc<3){std::cerr<<"Usage: r9_real_replay MONTH_TICKS.csv.gz TRADES.csv [--spread=N --vel=N --range=N --minvel=N --minrange=N --eff=0.7 --hold=N --stop=N --trail=N --activation=N --rearm=N --atr_multiplier=1.0 --no_atr --no_trail]\n";return 2;}
 std::string diagnostic_manifest,diagnostic_output; Config c;for(int i=3;i<argc;++i){std::string arg=argv[i];if(arg=="--no_atr")c.no_atr=true;else if(arg=="--no_trail")c.no_trail=true;else{
 auto p=arg.find('=');if(p==std::string::npos || arg.substr(0,2)!="--")throw std::runtime_error("bad option "+arg);
 std::string n=arg.substr(2,p-2),v=arg.substr(p+1);
 if(n=="diagnostic_manifest"){diagnostic_manifest=v;continue;}
 if(n=="diagnostic_output"){diagnostic_output=v;continue;}
 double d=std::stod(v);int z=(int)d;
 if(n=="router")c.router=z;else if(n=="gap")c.gap=z;else if(n=="spread")c.spread=z;else if(n=="vel")c.vel=z;else if(n=="range")c.range=z;else if(n=="minvel")c.minvel=z;else if(n=="minrange")c.minrange=z;else if(n=="eff")c.eff=d;else if(n=="hold")c.hold=z;else if(n=="stop")c.stop=z;else if(n=="trail")c.trail=z;else if(n=="activation")c.activation=z;else if(n=="rearm")c.rearm=z;else if(n=="atr_multiplier")c.atr_multiplier=d;else throw std::runtime_error("unknown option "+n);
 }}
 if(c.vel<2 || c.range<2 || std::max(c.vel,c.range)>=128 || c.gap<1 || c.hold<1 || c.stop<1 || c.trail<0 || c.activation<0 || c.rearm<0 || c.eff<0 || c.eff>1 || c.router<0 || c.router>3)throw std::runtime_error("invalid config");
 gzFile f=gzopen(argv[1],"rb");if(!f)throw std::runtime_error("cannot read raw month");
 char line[2048];if(!gzgets(f,line,sizeof(line)))throw std::runtime_error("empty source");
 if(std::strcmp(line,"time,time_msc,bid,ask,last,volume,volume_real,flags\n") && std::strcmp(line,"time,time_msc,bid,ask,last,volume,volume_real,flags\r\n"))throw std::runtime_error("unexpected source header");
 std::ofstream trades(argv[2]);if(!trades)throw std::runtime_error("cannot create result");trades<<"entry_ordinal,entry_time_msc,side,entry_price_cents,initial_sl_cents,exit_ordinal,exit_time_msc,exit_price_cents,reason,net_quote_cents,rearm_number\n";
 std::ofstream diagnosis;std::vector<Anchor> anchors;
 if(!diagnostic_manifest.empty()){
  if(diagnostic_output.empty())throw std::runtime_error("missing --diagnostic_output");
  anchors=load_anchors(diagnostic_manifest);diagnosis.open(diagnostic_output);if(!diagnosis)throw std::runtime_error("cannot open diag output");
 }
 Stats st;R9 engine(c,st,trades,std::move(anchors),diagnosis.is_open()?&diagnosis:nullptr);i64 previous=-1;
 while(gzgets(f,line,sizeof(line))){if(!std::strchr(line,'\n'))throw std::runtime_error("oversized/truncated csv row");Tick t;
  if(!parse(line,t))throw std::runtime_error("invalid tick row "+std::to_string(st.ticks+1));
  if(previous>t.ms)throw std::runtime_error("reverse tick order at "+std::to_string(st.ticks+1));
  if(t.ms==previous){++st.same_ms;}
  previous=t.ms;t.ordinal=++st.ticks;
  if(!st.first){st.first=t.ms;}
  st.last=t.ms;engine.on_tick(t);
 }
 engine.flush_remaining();
 if(gzclose(f)!=Z_OK)throw std::runtime_error("corrupt gzip");
 std::cerr<<"{\"ticks\":"<<st.ticks<<",\"same_ms\":"<<st.same_ms<<",\"first\":"<<st.first<<",\"last\":"<<st.last
  <<",\"entries\":"<<st.entries<<",\"stop\":"<<st.stopped<<",\"timeout\":"<<st.timed<<",\"target\":"<<st.targeted
  <<",\"positive\":"<<st.positive<<",\"negative\":"<<st.negative<<",\"flat\":"<<st.flat<<",\"net_quote_cents\":"<<st.net_c
  <<",\"rearmed\":"<<st.rearmed<<",\"trail_updates\":"<<st.trails<<",\"gate_spread\":"<<st.gate_spread<<",\"gate_no_atr\":"<<st.gate_no_atr
  <<",\"gate_low_atr\":"<<st.gate_low_atr<<",\"gate_s1\":"<<st.gate_s1<<"}\n";
 return 0;
 }catch(const std::exception&ex){std::cerr<<"FATAL: "<<ex.what()<<"\n";return 1;}}
