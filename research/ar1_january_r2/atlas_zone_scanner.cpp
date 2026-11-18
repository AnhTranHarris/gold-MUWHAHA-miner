// Read-only January Coinexx TickLogger window scanner. R9 fixed entry/exit NEVER altered.
// Surrounding intervals outside the R9 holding window are market context, NEVER intratrade P&L.
#include <zlib.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>
#include <algorithm>
#include <limits>
using ll=long long;
struct Interval{int aid,row,bin; std::string group,kind;ll lo,hi;ll count=0,first=0,last=0;double bid0=0,bid1=0,ask0=0,ask1=0,m0=0,m1=0,minmid=1e20,maxmid=-1e20,spread_sum=0,max_spread=0,abs_change=0,max_jump=0,last_mid=0;};
static int cents(const char* p){int neg=(*p=='-');if(neg)++p;int whole=0;while(*p>='0'&&*p<='9')whole=whole*10+(*p++-'0');int v=whole*100;if(*p=='.'){++p;v+=10*(*p++-'0');if(*p>='0'&&*p<='9')v+=*p-'0';}return neg?-v:v;}
int main(int argc,char**argv){
 if(argc<5){fprintf(stderr,"usage: bin intervals.csv output.csv tickfiles...\n");return 2;}
 std::ifstream in(argv[1]);std::string line;std::getline(in,line);std::vector<Interval>v;
 while(std::getline(in,line)){std::istringstream ss(line);std::string a[7];bool ok=true;for(auto &s:a){if(!std::getline(ss,s,',')){ok=false;break;}}if(!ok)continue;Interval t;t.aid=std::stoi(a[0]);t.row=std::stoi(a[1]);t.group=a[2];t.kind=a[3];t.bin=std::stoi(a[4]);t.lo=std::stoll(a[5]);t.hi=std::stoll(a[6]);v.push_back(t);}
 std::sort(v.begin(),v.end(),[](auto&a,auto&b){if(a.lo==b.lo)return a.hi<b.hi;return a.lo<b.lo;});
 std::vector<int>active;size_t idx=0;ll ticks=0,backward=0,lastms=-1;char buf[2048];
 for(int i=3;i<argc;i++){gzFile f=gzopen(argv[i],"rb");if(!f){fprintf(stderr,"missing %s\n",argv[i]);return 4;}gzbuffer(f,1<<20);ll before=ticks;
 while(gzgets(f,buf,sizeof(buf))){if(strncmp(buf,"REAL,",5))continue;char *p=buf+5;ll ms=strtoll(p,&p,10);p=strchr(p,',');if(!p)continue;p=strchr(p+1,',');if(!p)continue;int bid=cents(p+1);p=strchr(p+1,',');if(!p)continue;int ask=cents(p+1);if(bid<=0||ask<=0)continue;
 if(lastms>=0&&ms<lastms){backward++;continue;}lastms=ms;ticks++;
 while(idx<v.size()&&v[idx].lo<=ms){active.push_back((int)idx);idx++;}
 active.erase(std::remove_if(active.begin(),active.end(),[&](int j){return v[j].hi<=ms;}),active.end());
 const double mid=(bid+ask)*.5,spread=ask-bid;
 for(int j:active){auto &r=v[j];r.count++;if(r.count==1){r.first=ms;r.bid0=bid;r.ask0=ask;r.m0=mid;r.last_mid=mid;}else{double jump=fabs(mid-r.last_mid);r.abs_change+=jump;r.max_jump=std::max(r.max_jump,jump);}r.last=ms;r.bid1=bid;r.ask1=ask;r.m1=mid;r.last_mid=mid;r.minmid=std::min(r.minmid,mid);r.maxmid=std::max(r.maxmid,mid);r.spread_sum+=spread;r.max_spread=std::max(r.max_spread,spread);}
 }
 gzclose(f);fprintf(stderr,"scan %s quotes=%lld cumulative=%lld\n",argv[i],ticks-before,ticks);
 }
 FILE*o=fopen(argv[2],"w");if(!o)return 3;
 fprintf(o,"anchor_id,source_row,group,anchor_kind,bin_index,start_ms,end_ms,quote_count,first_tick_ms,last_tick_ms,first_bid_USD,last_bid_USD,first_ask_USD,last_ask_USD,first_mid_USD,last_mid_USD,mid_range_USD,mid_change_USD,mid_abs_travel_USD,max_mid_jump_USD,mean_spread_USD,max_spread_USD\n");
 for(auto&r:v){double k=.01;fprintf(o,"%d,%d,%s,%s,%d,%lld,%lld,%lld,%lld,%lld,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n",r.aid,r.row,r.group.c_str(),r.kind.c_str(),r.bin,r.lo,r.hi,r.count,r.first,r.last,r.bid0*k,r.bid1*k,r.ask0*k,r.ask1*k,r.m0*k,r.m1*k,r.count?(r.maxmid-r.minmid)*k:0,(r.m1-r.m0)*k,r.abs_change*k,r.max_jump*k,r.count?r.spread_sum/r.count*k:0,r.max_spread*k);}
 fclose(o);fprintf(stderr,"DONE ticks=%lld intervals=%zu backward=%lld\n",ticks,v.size(),backward);return backward?5:0;
}
