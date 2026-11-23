// Offline upper-bound teacher: original R9 fixed trade IDs and side are ground truth only for analysis.
// Select best *order-respecting* BUY-Ask→Bid or SELL-Bid→Ask pair within ±w seconds
// of each original SYNTH entry/exit. HINDSIGHT OPTIMISTIC, NOT a causal trading strategy.
#include <zlib.h>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
using I=int64_t;
struct Quote {I ord=0,ms=0,bid=0,ask=0;};
struct Row {I entry=0,exit=0;int side=0,leg=0;double booked=0.;std::vector<Quote>en,ex;};
struct Window {I begin=0,end=0;size_t ref=0;bool entry=false;};
static std::vector<Row> manifest(const std::string& file){std::ifstream f(file);if(!f)throw std::runtime_error("missing original manifest");std::string line;if(!getline(f,line)||line.rfind("row,role,side,entry_sec,exit_sec,",0)!=0)throw std::runtime_error("manifest header");std::vector<Row> r;while(getline(f,line)){
 size_t a=line.find(','),b=line.find(',',a+1),c=line.find(',',b+1);const std::string side=line.substr(b+1,c-b-1);a=c;b=line.find(',',a+1);I entry=std::stoll(line.substr(a+1,b-a-1));a=b;b=line.find(',',a+1);I exit=std::stoll(line.substr(a+1,b-a-1));a=b;b=line.find(',',a+1);double booked=std::stod(line.substr(a+1,b-a-1));a=b;b=line.find(',',a+1);int leg=std::stoi(line.substr(a+1,b-a-1));r.push_back(Row{entry,exit,side=="BUY"?1:-1,leg,booked,{},{}});
 }return r;}
static Quote parse(const char*s,I ordinal){char*p=nullptr;I sec=strtoll(s,&p,10);if(*p!=',')throw std::runtime_error("bad second");I ms=strtoll(p+1,&p,10);if(*p!=',')throw std::runtime_error("bad millis");I bid=llround(strtod(p+1,&p)*100.);if(*p!=',')throw std::runtime_error("bad bid");I ask=llround(strtod(p+1,&p)*100.);if(sec!=ms/1000 || bid<=0 || ask<bid)throw std::runtime_error("bad quote");return {ordinal,ms,bid,ask};}
int main(int argc,char **argv){try{
 if(argc!=5)throw std::runtime_error("usage: manifest.csv orig_ticks.gz tolerance_seconds out.csv");
 auto rows=manifest(argv[1]);int w=std::stoi(argv[3]);if(w<0||w>10)throw std::runtime_error("tolerance out of range");
 std::vector<Window> windows;windows.reserve(rows.size()*2);for(size_t i=0;i<rows.size();i++){windows.push_back({rows[i].entry-w,rows[i].entry+w,i,true});windows.push_back({rows[i].exit-w,rows[i].exit+w,i,false});}
 std::sort(windows.begin(),windows.end(),[](const Window&a,const Window&b){return a.begin<b.begin || (a.begin==b.begin&&a.end<b.end);});
 gzFile f=gzopen(argv[2],"rb");if(!f)throw std::runtime_error("source raw unreadable");char line[2048];if(!gzgets(f,line,sizeof line)||strncmp(line,"time,time_msc,bid,ask,",22))throw std::runtime_error("source header mismatch");std::vector<size_t> active;size_t n=0;I ordinal=0,prevms=-1,samems=0;
 while(gzgets(f,line,sizeof line)){if(!strchr(line,'\n'))throw std::runtime_error("truncated original row");Quote t=parse(line,++ordinal);if(t.ms<prevms)throw std::runtime_error("raw not ordered");if(t.ms==prevms)++samems;prevms=t.ms;I sec=t.ms/1000;
  while(n<windows.size()&&windows[n].begin<=sec)active.push_back(n++);
  size_t keep=0;for(size_t wi:active){const auto &p=windows[wi];if(p.end<sec)continue;
   if(p.entry)rows[p.ref].en.push_back(t);else rows[p.ref].ex.push_back(t);
   active[keep++]=wi;
  }active.resize(keep);
 }
 if(gzclose(f)!=Z_OK)throw std::runtime_error("source gzip CRC error");
 std::ofstream o(argv[4]);if(!o)throw std::runtime_error("cannot write teacher");o<<"row,leg,side,entry_ref_sec,exit_ref_sec,original_booked_net_usd,source_entry_quotes,source_exit_quotes,order_respecting,teacher_entry_ord,teacher_entry_ms,teacher_entry_bid_c,teacher_entry_ask_c,teacher_exit_ord,teacher_exit_ms,teacher_exit_bid_c,teacher_exit_ask_c,teacher_best_net_c,teacher_positive_after_20c\n";
 I eligible=0,positive=0,after20=0,protectedwin=0,winpositive=0,missing=0,notordered=0;int best=std::numeric_limits<int>::min();
 for(size_t row=0;row<rows.size();++row){const auto &r=rows[row];I nentry=I(r.en.size()),nexit=I(r.ex.size());
  bool has=false;Quote bestEntry{},bestExit{},tracker{};I bestNet=std::numeric_limits<I>::min();bool trackerReady=false;size_t j=0;
  for(const Quote &q:r.ex){while(j<r.en.size() && r.en[j].ord<q.ord){const Quote &e=r.en[j++];if(!trackerReady || (r.side>0?e.ask<tracker.ask:e.bid>tracker.bid)){tracker=e;trackerReady=true;}}
   if(!trackerReady)continue;
   I profit=r.side>0?q.bid-tracker.ask:tracker.bid-q.ask;
   if(!has || profit>bestNet){has=true;bestNet=profit;bestEntry=tracker;bestExit=q;}
  }
  if(r.booked>0)++protectedwin;
  if(has){++eligible;if(bestNet>0){++positive;if(r.booked>0)++winpositive;}if(bestNet>20)++after20;best=std::max(best,int(bestNet));}
  else if(!nentry||!nexit)++missing;else ++notordered;
  o<<row+1<<','<<r.leg<<','<<r.side<<','<<r.entry<<','<<r.exit<<','<<r.booked<<','<<nentry<<','<<nexit<<','<<(has?1:0)<<','<<bestEntry.ord<<','<<bestEntry.ms<<','<<bestEntry.bid<<','<<bestEntry.ask<<','<<bestExit.ord<<','<<bestExit.ms<<','<<bestExit.bid<<','<<bestExit.ask<<','<<(has?bestNet:0)<<','<<(has&&bestNet>20?1:0)<<'\n';
 }
 std::cerr<<"{\"source_ticks\":"<<ordinal<<",\"same_millisecond_neighbors\":"<<samems<<",\"reference_rows\":"<<rows.size()<<",\"tolerance_sec\":"<<w<<",\"ordered_pair_coverage\":"<<eligible<<",\"oracle_positive\":"<<positive<<",\"oracle_positive_after20c\":"<<after20<<",\"original_synth_positive\":"<<protectedwin<<",\"original_synth_winners_oracle_positive\":"<<winpositive<<",\"missing_quote_window\":"<<missing<<",\"no_ordered_pair\":"<<notordered<<",\"optimistic_only\":true}\n";
 return 0;
 }catch(const std::exception&ex){std::cerr<<"ERROR "<<ex.what()<<'\n';return 1;}}
