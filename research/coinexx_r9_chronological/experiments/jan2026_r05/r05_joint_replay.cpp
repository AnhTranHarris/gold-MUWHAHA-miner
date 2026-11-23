// Gold MUWHAHA R05 January-only research, independent Coinexx REAL quote-order execution.
// Frozen R9 SYNTH reference is NEVER opened. Only prior/current source quote, trained trees
// and frozen January R03 entry scores are consulted. Original 0.01 lot: $0.02 full-trade fee.
#include <zlib.h>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
using I=std::int64_t;
struct Quote {I sec=0,ms=0,bid=0,ask=0,ord=0;};
static I readInt(const char*&p){char*end=nullptr;I val=std::strtoll(p,&end,10);if(p==end||(*end && *end!=','&&*end!='\n'&&*end!='\r'))throw std::runtime_error("bad integer CSV");p=end+(*end==',');return val;}
static double readDouble(const char*&p){char*end=nullptr;double val=std::strtod(p,&end);if(p==end||!std::isfinite(val)||(*end && *end!=','&&*end!='\n'&&*end!='\r'))throw std::runtime_error("bad double CSV");p=end+(*end==',');return val;}
static Quote parse_quote(const char*s){const char*p=s;Quote q;q.sec=readInt(p);q.ms=readInt(p);q.bid=std::llround(readDouble(p)*100);q.ask=std::llround(readDouble(p)*100);if(q.ms/1000!=q.sec||q.bid<=0||q.ask<q.bid)throw std::runtime_error("source raw format");return q;}
struct Signal {I sec=0,ms=0,bid=0,ask=0,phase=0,spread=0;double fb=0,fs=0,sb=0,ss=0;};
static Signal parse_signal(const char*s){const char*p=s;Signal a;a.sec=readInt(p);a.ms=readInt(p);a.bid=readInt(p);a.ask=readInt(p);a.phase=readInt(p);a.spread=readInt(p);a.fb=readDouble(p);a.fs=readDouble(p);a.sb=readDouble(p);a.ss=readDouble(p);return a;}
struct Feature {std::array<double,37> x{};I sec()const{return (I)x[0];}I ms()const{return (I)x[1];}I bid()const{return (I)x[2];}I ask()const{return (I)x[3];}};
static Feature parse_feat(const char*s){Feature z;const char*p=s;for(int k=0;k<37;k++)z.x[k]=readDouble(p);return z;}
struct Node {int field=-1,left=-1,right=-1;double threshold=0,value=0;bool default_left=true;};
struct Forest {std::vector<std::vector<Node>> trees;int feature_count=0;
 explicit Forest(std::string path){std::ifstream f(path);if(!f)throw std::runtime_error("forest unavailable "+path);std::string head;int version,n;f>>head>>version>>feature_count>>n;if(head!="R05FOREST"||version!=1||feature_count<20||n<1)throw std::runtime_error("invalid forest header");std::string feature;for(int i=0;i<feature_count;i++)f>>feature;for(int i=0;i<n;i++){int cnt;f>>cnt;if(cnt<1||cnt>300)throw std::runtime_error("invalid tree size");std::vector<Node> tree(cnt);for(Node&v:tree){int d;f>>v.field>>v.threshold>>v.left>>v.right>>v.value>>d;v.default_left=d!=0;}trees.push_back(std::move(tree));}if(!f)throw std::runtime_error("forest truncated");}
 double score(const double*x) const {double s=0;for(const auto&t:trees){int n=0;for(int i=0;i<100;i++){const Node&v=t[n];if(v.field<0){s+=v.value;break;}const double a=x[v.field];n=std::isnan(a)?(v.default_left?v.left:v.right):(a<=v.threshold?v.left:v.right);if(n<0||n>=(int)t.size())throw std::runtime_error("bad tree pointer");}}if(s>40)return 1;if(s<-40)return 0;return 1.0/(1+std::exp(-s));}
};
struct Config {double f=.24,s=.23,e=.40,r=.4,passcut=.60;int spread=80,stop=180,hold=30,mode=0,target=56,force_second=0,only_early_rearm=0,fee=2;std::string passage;};
struct Position {bool active=false;int side=0,leg=0;I entryms=0,entrysec=0,entryord=0,entry=0,peak=std::numeric_limits<I>::min(),trough=std::numeric_limits<I>::max(),best_bid=0;double enter_score=0,cached_exit=0,cached_passage=.5;I lastmark=0;bool mark_seen=false;};
struct First {bool finished=false;I minute=0,exit_sec=0,exit_ord=0;int side=0,entry_phase=0,exit_phase=0,age=0;I net=0;};
struct Stats {I ticks=0,same=0,feature_seconds=0,scores=0,positions=0,positive=0,positive_gross=0,negative=0,netcash=0,firsts=0,seconds=0,recovered=0,timeout=0,stopped=0,hazard=0,firstpass=0,missing=0,feat_miss=0;};
static void exit_feature(double *v,const Feature&f,const Position&p,I mark){const auto&x=f.x;
 const double d=double(p.side*mark-p.side*p.entry); int i=0;
 for(double w:{double(f.sec()-p.entrysec),double(p.entrysec%60),double(p.side),double(p.leg),d,double(p.peak),double(p.trough),double(p.peak)-d,x[7],x[8],x[4],x[6],x[9],x[10],x[11],x[12],x[13],x[14],x[15],x[16],x[17],x[18],x[19],x[20],x[21],x[22],x[23],x[24],x[26],x[27],x[31],x[32],x[33],x[34],x[35],x[36]})v[i++]=w;
 if(i!=36)throw std::runtime_error("exit feature count");
}
static void rearm_feature(double *v,const Feature&f,const First&a){const auto&x=f.x;int i=0;
 for(double w:{double(f.sec()-a.exit_sec),double(a.side),double(a.exit_phase),double(a.age),double(a.net+2),x[4],x[7],x[8],x[6],x[9],x[10],x[11],x[12],x[13],x[14],x[15],x[16],x[17],x[18],x[19],x[20],x[21],x[22],x[23],x[24],x[26],x[27],x[31],x[32],x[33],x[34],x[35],x[36]})v[i++]=w;
 if(i!=33)throw std::runtime_error("rearm feature count");
}
int main(int argc,char**argv){try{
 if(argc<7)throw std::runtime_error("Usage: RAW_TICKS.gz R03_FEATURES.gz R03_ENTRY_SCORES.gz R05_EXIT_FOREST R05_REARM_FOREST TRADES.csv [--f=.24 --s=.23 --e=.40 --r=.4 --mode=0 --stop=180 --hold=30 --spread=80 --target=56]");
 Config c;for(int i=7;i<argc;i++){std::string a=argv[i];auto p=a.find('=');if(p==std::string::npos||a.substr(0,2)!="--")throw std::runtime_error("invalid flag");std::string k=a.substr(2,p-2);if(k=="passage"){c.passage=a.substr(p+1);continue;}double d=std::stod(a.substr(p+1));if(k=="f")c.f=d;else if(k=="s")c.s=d;else if(k=="e")c.e=d;else if(k=="r")c.r=d;else if(k=="mode")c.mode=int(d);else if(k=="stop")c.stop=int(d);else if(k=="hold")c.hold=int(d);else if(k=="target")c.target=int(d);else if(k=="spread")c.spread=int(d);else if(k=="force_second")c.force_second=int(d);else if(k=="only_early_rearm")c.only_early_rearm=int(d);else if(k=="passcut")c.passcut=d;else throw std::runtime_error("unknown flag "+k);}
 if(c.f<0||c.f>1||c.s<0||c.s>1||c.e<0||c.e>1||c.r<0||c.r>1||c.stop<=0||c.hold<=0||c.mode<0||c.mode>11)throw std::runtime_error("invalid params");
 Forest exitmodel(argv[4]),rearmmodel(argv[5]);std::unique_ptr<Forest> passage;if(!c.passage.empty())passage=std::make_unique<Forest>(c.passage);if(((c.mode>=5&&c.mode<=7)||c.mode>=10)&&!passage)throw std::runtime_error("passage forest required for this mode");if(exitmodel.feature_count!=36||rearmmodel.feature_count!=33)throw std::runtime_error("forest feature signature differs");
 gzFile raw=gzopen(argv[1],"rb"),feat=gzopen(argv[2],"rb"),pred=gzopen(argv[3],"rb");if(!raw||!feat||!pred)throw std::runtime_error("source input missing");
 char qline[2048],fline[4096],sline[2048];if(!gzgets(raw,qline,sizeof qline)||std::strncmp(qline,"time,time_msc,bid,ask,",22))throw std::runtime_error("raw header");
 if(!gzgets(feat,fline,sizeof fline)||std::strncmp(fline,"sec,ms,bid_c,ask_c,",19))throw std::runtime_error("feature header");
 if(!gzgets(pred,sline,sizeof sline)||std::strncmp(sline,"sec,ms,bid_c,",13))throw std::runtime_error("score header");
 bool has_feat=bool(gzgets(feat,fline,sizeof fline)),has_signal=bool(gzgets(pred,sline,sizeof sline));Feature z{};Signal sig{};if(has_feat)z=parse_feat(fline);if(has_signal)sig=parse_signal(sline);
 std::ofstream out(argv[6]);if(!out)throw std::runtime_error("write ledger");out<<"entry_ordinal,entry_time_msc,side,entry_price_cents,exit_ordinal,exit_time_msc,exit_price_cents,reason,net_quote_cents,net_cash_cents,leg,minute_id,exit_hazard,entry_hazard,elapsed_seconds,rearm_hazard\n";
 Stats st;Position pos;First prevfirst;I lastms=-1,minute=-1,firsttaken=0,secondtaken=0,lastcloseord=-1;int firstside=0;double second_likelihood=0;
 while(gzgets(raw,qline,sizeof qline)){
  if(!std::strchr(qline,'\n'))throw std::runtime_error("oversized quote row");
  Quote q=parse_quote(qline);if(lastms>q.ms)throw std::runtime_error("non-monotone raw tick");if(lastms==q.ms)++st.same;lastms=q.ms;q.ord=++st.ticks;
  I m=q.sec/60;if(m!=minute){minute=m;firsttaken=0;secondtaken=0;firstside=0;prevfirst=First{};}
  const bool feature_tick=has_feat&&z.ms()==q.ms&&z.sec()==q.sec;
  if(feature_tick){if(z.bid()!=q.bid||z.ask()!=q.ask)throw std::runtime_error("wrong original source quote in MTF feature");++st.feature_seconds;}
  // Stops checked on EVERY original quote BEFORE any new position decision.
  double currentexit=0;I closebid=0,liqnet=0;int reason=0;
  if(pos.active){closebid=pos.side>0?q.bid:q.ask;liqnet=pos.side*(closebid-pos.entry);pos.peak=std::max(pos.peak,liqnet);pos.trough=std::min(pos.trough,liqnet);
   if(liqnet<=-c.stop)reason=1;
   else if(feature_tick && q.sec>pos.entrysec){double fv[36]{};exit_feature(fv,z,pos,closebid);currentexit=exitmodel.score(fv);pos.cached_exit=currentexit;if(passage)pos.cached_passage=passage->score(fv);
    if(c.mode==0&&currentexit>=c.e)reason=2;
    else if(c.mode==1&&currentexit>=c.e&&liqnet>c.fee)reason=2;
    else if(c.mode==2&&((currentexit>=c.e&&liqnet>c.fee)||(liqnet>=c.target&&currentexit>=0.1)))reason=2;
    else if(c.mode==3&&((currentexit>=c.e&&liqnet>c.fee)||(liqnet>=c.target)))reason=2;
    else if(c.mode==4&&((currentexit>=c.e&&liqnet>c.fee)||(pos.peak-liqnet>=std::max<I>(5,q.ask-q.bid)&&pos.peak>=c.target&&liqnet>c.fee)))reason=2;
    else if(c.mode>=5&&c.mode<=7){
     const double improve=passage->score(fv);
     if(c.mode==5){
       if(liqnet>c.fee&&currentexit>=c.e&&improve<c.passcut)reason=2;
       else if(liqnet>=c.target&&improve<.72)reason=2;
       else if(liqnet< -65&&improve<.30)reason=5;
     }else if(c.mode==6){
       if(liqnet>c.fee&&(improve<c.passcut||currentexit>=c.e))reason=2;
       else if(liqnet< -65&&improve<.28)reason=5;
     }else if(c.mode==7){
       if(liqnet>c.fee&&((currentexit>=c.e&&improve<.80)||(liqnet>=c.target&&improve<.78)))reason=2;
       else if(liqnet< -85&&improve<.18)reason=5;
     }
    }
   }
   if(!reason && c.mode>=8 && q.ord>pos.entryord && liqnet>c.fee){
     const int phase=int(q.sec%60);
     const int planned=pos.leg==2?42:(pos.entrysec%60<=2?5:pos.entrysec%60<=10?16:42);
     const bool near_phase=(q.sec/60==pos.entrysec/60 && phase>=planned-2 && phase<=planned+3);
     if(c.mode==8)reason=2; // first favorable observed REAL quote, never lookahead.
     else if(c.mode==9 && near_phase && (pos.cached_exit>=c.e||liqnet>=c.target))reason=2;
     else if(c.mode==10 && (pos.cached_exit>=c.e || pos.cached_passage<c.passcut))reason=2;
     else if(c.mode==11 && ((near_phase && pos.cached_exit>=c.e*.6)||(pos.peak>=c.target && pos.lastmark>liqnet)))reason=2;
   }
   if(!reason&&q.sec-pos.entrysec>=c.hold)reason=3;
   if(!reason){pos.lastmark=liqnet;pos.mark_seen=true;}
   if(reason){I cash=liqnet-c.fee;++st.positions;st.netcash+=cash;if(cash>0)++st.positive;else ++st.negative;if(liqnet>0)++st.positive_gross;
    if(reason==1||reason==5)++st.stopped;else if(reason==2)++st.hazard;else ++st.timeout;
    if(pos.leg==1){prevfirst.finished=true;prevfirst.minute=pos.entrysec/60;prevfirst.exit_sec=q.sec;prevfirst.exit_ord=q.ord;prevfirst.side=pos.side;prevfirst.exit_phase=int(q.sec%60);prevfirst.entry_phase=int(pos.entrysec%60);prevfirst.age=int(q.sec-pos.entrysec);prevfirst.net=cash;}
    if(pos.leg==2&&cash>0&&prevfirst.finished&&prevfirst.net<0&&cash+prevfirst.net>0)++st.recovered;
    out<<pos.entryord<<','<<pos.entryms<<','<<pos.side<<','<<pos.entry<<','<<q.ord<<','<<q.ms<<','<<closebid<<','<<(reason==1?"adverse_stop":reason==5?"competing_bad":reason==2?"learned_exit":"timeout")<<','<<liqnet<<','<<cash<<','<<pos.leg<<','<<pos.entrysec/60<<','<<std::setprecision(7)<<currentexit<<','<<pos.enter_score<<','<<q.sec-pos.entrysec<<','<<second_likelihood<<'\n';
    pos.active=false;lastcloseord=q.ord;
   }
  }
  const bool signal_tick=has_signal&&sig.ms==q.ms&&sig.sec==q.sec;
  if(signal_tick){if(sig.bid!=q.bid||sig.ask!=q.ask)throw std::runtime_error("wrong original source quote in entry model");++st.scores;}
  // The first/same-minute second entry depends on LIVE inventory and first close, not original trade labels.
  if(feature_tick && signal_tick && !pos.active && q.ord>lastcloseord && sig.spread<=c.spread){
   int side=0,leg=0;double score=0;
   if(!firsttaken && sig.phase<=33){score=std::max(sig.fb,sig.fs);if(score>=c.f){side=sig.fb>=sig.fs?1:-1;leg=1;}}
   else if(firsttaken&&!secondtaken && prevfirst.finished && prevfirst.minute==minute && (!c.only_early_rearm||prevfirst.entry_phase<=10) && q.sec>prevfirst.exit_sec && sig.phase>=15 && sig.phase<=47){
    double fv[33]{};rearm_feature(fv,z,prevfirst);second_likelihood=rearmmodel.score(fv);score=std::max(sig.sb,sig.ss);
    if(score>=c.s&&(second_likelihood>=c.r||c.force_second)){side=sig.sb>=sig.ss?1:-1;leg=2;if(side==firstside)side=0;}
   }
   if(side!=0){pos=Position{};pos.active=true;pos.side=side;pos.leg=leg;pos.entryms=q.ms;pos.entrysec=q.sec;pos.entryord=q.ord;pos.entry=side>0?q.ask:q.bid;pos.peak=pos.trough=-(q.ask-q.bid);pos.lastmark=pos.peak;pos.mark_seen=true;pos.enter_score=score;
    if(leg==1){firsttaken=1;firstside=side;++st.firsts;second_likelihood=0;}else{secondtaken=1;++st.seconds;}
   }
  }
  if(feature_tick){has_feat=bool(gzgets(feat,fline,sizeof fline));if(has_feat)z=parse_feat(fline);}
  if(signal_tick){has_signal=bool(gzgets(pred,sline,sizeof sline));if(has_signal)sig=parse_signal(sline);}
  if(has_feat&&z.ms()<q.ms){++st.feat_miss;throw std::runtime_error("feature stream desynced source");}
  if(has_signal&&sig.ms<q.ms){++st.missing;throw std::runtime_error("score stream desynced source");}
 }
 if(pos.active)++st.missing;
 if(gzclose(raw)!=Z_OK||gzclose(feat)!=Z_OK||gzclose(pred)!=Z_OK)throw std::runtime_error("gzip CRC corruption");
 std::cerr<<"{\"source_ticks\":"<<st.ticks<<",\"same_ms\":"<<st.same<<",\"feature_seconds\":"<<st.feature_seconds<<",\"entry_score_seconds\":"<<st.scores<<",\"firsts\":"<<st.firsts<<",\"seconds\":"<<st.seconds<<",\"trades\":"<<st.positions<<",\"fee_positive\":"<<st.positive<<",\"fee_nonpositive\":"<<st.negative<<",\"quote_positive\":"<<st.positive_gross<<",\"cash_net_cents\":"<<st.netcash<<",\"simulated_positive_recoveries\":"<<st.recovered<<",\"stopped\":"<<st.stopped<<",\"exit_hazard\":"<<st.hazard<<",\"timeout\":"<<st.timeout<<",\"missing\":"<<st.missing<<"}\n";
 return 0;
 }catch(const std::exception&e){std::cerr<<"FATAL "<<e.what()<<'\n';return 1;}
}
