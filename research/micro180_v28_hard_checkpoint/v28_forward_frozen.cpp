// Causal historical quote prefix extractor -- original REAL TickLogger only.
// Every source quote updates rolling state; only positive mapped-entry events get
// feature rows. No non-positive trade or quote is ever a labelled training row.
#include <bits/stdc++.h>
using namespace std;
struct Target {long long ms;int leg,side,price; char family; long long teacher;string month;};
struct Bar {long long minute; double o,h,l,c,sum;int n;};
struct Sec {long long s=-1;double mid=0;};
struct History{
 long long prevs=-1,prevmin=-1;double prevmid=0;
 array<Sec,1024> sec{};
 deque<Bar> bars;
 Bar active{};
 double lastbid=0,lastask=0;
 void update(long long ms,double mid,double bid,double ask){
  auto s=ms/1000,m=ms/60000;
  if(prevmin!=m){
   if(prevmin>=0){if(m==prevmin+1) {bars.push_back(active);if(bars.size()>32)bars.pop_front();}
    else {bars.clear();sec.fill(Sec{});}}
   active={m,mid,mid,mid,mid,mid,1};prevmin=m;
  }else{active.h=max(active.h,mid);active.l=min(active.l,mid);active.c=mid;active.sum+=mid;active.n++;}
  if(prevs!=-1 && s!=prevs)sec[prevs%1024]={prevs,prevmid};
  prevs=s;prevmid=mid;lastbid=bid;lastask=ask;
 }
 double past(long long s,int seconds) const {
  long long t=s-seconds;
  for(int k=0;k<4;k++) {long long z=t-k;const auto &v=sec[z%1024];if(v.s==z) return v.mid;}
  return nan("");
 }
 bool features(long long ms,double mid,int side,double atr,
               double cycle_buy,double cycle_sell,double source_s1,double s1eff,double s1range,int s1turns,
               vector<double>& out) const{
  if(bars.size()<21)return false;long long s=ms/1000;double p5=past(s,5),p15=past(s,15),p60=past(s,60),p180=past(s,180),p300=past(s,300);
  if(!isfinite(p5)||!isfinite(p15)||!isfinite(p60)||!isfinite(p180)||!isfinite(p300))return false;
  atr=max(0.5,atr); // ATR is from completed M5 logger (as-of quote)
  auto dir=[&](double x){return side*x/atr;};
  auto returnn=[&](int n){return side*(mid-past(s,n))/atr;};
  // strictly completed M1 bars, quote-count-weighted mid/VWAP proxy
  auto vwap=[&](int n){double z=0;long long cnt=0;for(int i=(int)bars.size()-n;i<(int)bars.size();i++){z+=bars[i].sum;cnt+=bars[i].n;}return z/max(1LL,cnt);};
  auto sma=[&](int n){double z=0;for(int i=(int)bars.size()-n;i<(int)bars.size();i++)z+=bars[i].c;return z/n;};
  auto ema=[&](int n){double v=bars.front().c;double a=2./(n+1);for(const auto &b:bars)v=a*b.c+(1-a)*v;return v;};
  auto eff=[&](int n,int step){double sum=0,last=mid;for(int i=step;i<=n;i+=step){double x=past(s,i);if(!isfinite(x))return 0.;sum+=abs(last-x);last=x;}return side*(mid-last)/max(0.01,sum);};
  auto rv=[&](int n,int step){double sum=0,last=mid;int count=0;for(int i=step;i<=n;i+=step){double x=past(s,i);if(!isfinite(x))break;sum+=(last-x)*(last-x);last=x;count++;}return count>0?sqrt(sum/count):0.;};
  auto channel=[&](int n){double hi=-1e10,lo=1e10;for(int i=(int)bars.size()-n;i<(int)bars.size();i++){hi=max(hi,bars[i].h);lo=min(lo,bars[i].l);}return side>0?(mid-hi)/atr:(lo-mid)/atr;};
  auto tr=[&](int n){double sum=0;for(int i=(int)bars.size()-n;i<(int)bars.size();i++){const auto& b=bars[i];double pc=bars[i-1].c;sum+=max({b.h-b.l,abs(b.h-pc),abs(b.l-pc)});}return sum/n;};
  double m1mid=sma(1), m3mid=sma(3),m5mid=sma(5),ema3=ema(3),ema8=ema(8),ema21=ema(21);
  double qrv60=rv(60,5),qrv300=rv(300,15);
  double spread=lastask-lastbid;
  double margin=side>0?lastask-cycle_buy:cycle_sell-lastbid;
  double r60=returnn(60),r180=returnn(180),r300=returnn(300);
  double range5=0;for(int i=(int)bars.size()-5;i<(int)bars.size();i++)range5+=bars[i].h-bars[i].l;
  double lastRange=bars.back().h-bars.back().l;
  double rvRatio=qrv60/max(.01,qrv300);
  double trendNested=r60*r300;
  out={double((ms/1000)%60),double((ms/3600000)%24),double(side),
       returnn(5),returnn(15),r60,r180,r300,
       eff(60,5),eff(180,15),eff(300,15),
       dir(mid-vwap(1)),dir(mid-vwap(3)),dir(mid-vwap(5)),
       dir(mid-sma(3)),dir(mid-sma(5)),dir(mid-ema3),dir(ema3-ema8),dir(ema8-ema21),
       channel(1),channel(3),channel(5),
       qrv60/atr,qrv300/atr,rvRatio,
       lastRange/max(.01,range5/5),tr(5)/max(.01,tr(14)),
       dir(mid-active.o),dir(mid-active.h),dir(mid-active.l),
       margin/atr,spread/atr,side*source_s1/atr,s1eff,s1range/atr,double(s1turns),
       double(active.n)/max(1,int(bars.back().n)),trendNested};
  for(double x:out)if(!isfinite(x))return false;
  return true;
 }
};
// Executable teacher-free entry-intent replay. Loads ONLY frozen positive-entry
// manifold and original REAL quote files. NO teacher labels, profit, or exits.
struct Prototype {array<double,25> center{},width{};double threshold=0;int count=0;};
struct Candidate {string role,state;int side=0;double score=-1e9,density=0,threshold=0;bool qualified=false;};
struct FrozenPositivePolicy {
 array<double,25> median{},scale{};
 unordered_map<string,vector<Prototype>> proto;
 unordered_map<string,array<double,60>> phases;
 unordered_map<string,double> role_prior;
 unordered_map<string,array<double,24>> rate;
 unordered_map<string,double> phase_min;
 static string key(const string&role,int side,const string&state){return role+"|"+to_string(side)+"|"+state;}
 bool load(string path){
  ifstream f(path);if(!f)return false;string line;
  while(getline(f,line)){
   istringstream in(line);string typ;in>>typ;
   if(typ=="CENTER")for(double &x:median)in>>x;
   else if(typ=="SCALE")for(double &x:scale)in>>x;
   else if(typ=="PHASEMIN") {string r;int side;double val;in>>r>>side>>val;phase_min[key(r,side,"")]=val;}
   else if(typ=="RATE") {string r;int h;double v;in>>r>>h>>v;rate[r][h]=v;}
   else if(typ=="PRIOR") {string name;double p;in>>name>>p;role_prior[name]=p;}
   else if(typ=="G") {string role,state;int side;Prototype p;in>>role>>side>>state>>p.count>>p.threshold;
    for(double &x:p.center)in>>x;for(double &x:p.width)in>>x;proto[key(role,side,state)].push_back(p);
   }else if(typ=="P"){string role;int side;in>>role>>side;array<double,60> probs{};for(double &x:probs)in>>x;phases[key(role,side,"")]=probs;}
  }
  return !proto.empty();
 }
 bool phase_qualified(const string &r,int side,int sec)const{
    const string k=key(r,side,"");auto it=phases.find(k);
    if(it==phases.end())return false;
    auto z=phase_min.find(k);if(z==phase_min.end())return true;
    return it->second[sec%60]+1e-10>=z->second;
 }
 string state(const vector<double>&v)const{
  double r1=v[5],r3=v[6],r5=v[7],e5=v[10],br=v[20],rv=v[24],cr=v[25];
  if(br>=.01||(br>-.08&&rv>.82&&cr>1.22))return "breakout";
  if(r1*r5<0&&abs(r1)>.12&&abs(r5)>.09)return "reversal";
  if(r1*r3>0&&r3*r5>0&&abs(e5)>.30)return "nested_trend";
  if(abs(e5)>.16&&abs(r5)>.22)return "trend";
  if(abs(e5)<.13&&abs(r5)<.15&&rv<.68)return "consolidation";
  return "transition";
 }
 static double normalcdf(double z){return .5*erfc(-z/sqrt(2.));}
 double hit(const vector<double>&v,double atr)const{
  atr=max(.1,atr);int sec=int(v[0]);double gap=max(0.,.15-atr*v[27]);if(!gap)return 1.;
  double T=max(1,60-sec);double drift=atr*(.55*v[5]/60+.30*v[6]/180+.15*v[7]/300);
  double sigma=max(.005,atr*v[22]/sqrt(5.));double den=max(1e-9,sigma*sqrt(T));
  double z=exp(max(-60.,min(60.,2*drift*gap/(sigma*sigma))));
  return max(0.,min(1.,normalcdf((drift*T-gap)/den)+z*normalcdf((-drift*T-gap)/den)));
 }
 Candidate score(const vector<double>&v,const string&role,int side,double atr)const {
  static const int ix[]={3,4,5,6,7,8,9,10,11,12,13,17,18,20,21,22,24,25,26,27,30,31,32,33,36};
  static const set<int> fast={0,1,2,5,8,19,20,15,22,23,24};
  Candidate c;c.role=role;c.side=side;c.state=state(v);
  string k=key(role,side,c.state);auto it=proto.find(k);
  if(it==proto.end()) {k=key(role,side,"ANY");it=proto.find(k);}
  if(it==proto.end())return c;
  array<double,25> x{};for(int i=0;i<25;i++)x[i]=max(-8.,min(8.,(v[ix[i]]-median[i])/max(.03,scale[i])));
  double w=(c.state=="breakout"||c.state=="reversal")?.72:
           (c.state=="trend"||c.state=="nested_trend")?.40:.50;
  for(const auto&p:it->second){double df=0,ds=0;int nf=0,ns=0;
   for(int i=0;i<25;i++){
    double delta=max(-8.,min(8.,(x[i]-p.center[i])/max(.45,p.width[i])));
    if(fast.count(i)){df+=log1p(delta*delta);nf++;}
    else {ds+=log1p(delta*delta);ns++;}
   }
   double den=-(w*df/nf+(1-w)*ds/ns);
   if(den>c.density||c.score==-1e9){c.density=den;c.threshold=p.threshold;}
  }
  int sec=int(v[0]);auto ph=phases.find(key(role,side,""));double pp=ph==phases.end()?1./60:ph->second[sec];
  c.score=c.density+.12*log(max(.00001,pp)*60.)+.10*log(max(.01,hit(v,atr)))+.8*log(max(1e-5,role_prior.count(role)?role_prior.at(role):.01));
  c.qualified=c.density>=c.threshold;
  return c;
 }
};
int main(int argc,char**argv){
 if(argc<4){cerr<<"use: v28_forward_frozen FROZEN_JULY_WEIGHTS.tsv intents.tsv rawREAL_part08 [...part10]\n";return 2;}
 FrozenPositivePolicy p;int activeMonth=0;
 if(!p.load(argv[1])){cerr<<"frozen July policy unavailable\n";return 6;}
 ofstream o(argv[2]);o<<"ms\tminute\tleg\tside\trole\tstate\tscore\tprice_u\tconditional_on_flat\n";
 string cmd="cat";for(int i=3;i<argc;i++)cmd+=" '"+string(argv[i])+"'";cmd+=" | gzip -dc";
 FILE* src=popen(cmd.c_str(),"r");if(!src){cerr<<"source failure";return 4;}
 char line[2048];History h;long long curminute=-1,prevsec=-1;bool havefirst=false,havesecond=false;
 unordered_map<string,double> tokens;
 string firstrole;int firstside=0,firstsec=0;unsigned long long rows=0,intents=0;long long lastDay=-1;
 while(fgets(line,sizeof(line),src)){
  if(line[0]!='R'||strncmp(line,"REAL,",5))continue;
  char *fields[22]{};fields[0]=line;char*cursor=line;
  for(int i=0;i<5;i++){char*v=strchr(cursor,',');if(!v)break;*v=0;fields[i+1]=v+1;cursor=v+1;}
  if(!fields[5])continue;
  long long ms=atoll(fields[1]);double bid=atof(fields[3]),ask=atof(fields[4]),mid=(bid+ask)/2.;
  // Frozen checkpoint progresses Jan, Jan+Feb, ..., Jan+Jul. No model fitting.
  const long long day=ms/86400000LL;
  if(day!=lastDay){
    lastDay=day;
    time_t wall=time_t(ms/1000);tm utc{};gmtime_r(&wall,&utc);
    int requestedMonth=utc.tm_mon+1;
    if(utc.tm_year+1900!=2026 || requestedMonth<7 || requestedMonth>9){
      cerr<<"outside pre-August warmup and August-September 2026 source scope\n";return 7;
    }
    if(requestedMonth!=activeMonth){
      // Monthly trading-intensity counters reset, but the *identical* final
      // Jan-Jul policy remains loaded. Jul is warmup only, no entries.
      tokens.clear();activeMonth=requestedMonth;
      cerr<<"forward_month="<<activeMonth<<" july_policy_frozen="<<argv[1]<<"\n";
    }
  }
  long long sec=ms/1000,minute=ms/60000;int ss=int(sec%60);
  // Parse signal state on the first REAL quote of a new second only.
  bool eval=sec!=prevsec && ((ss<=17&&!havefirst)||(ss>=18&&ss<=44&&!havefirst)||
                           (ss>=18&&ss<=54&&havefirst&&!havesecond&&firstrole[0]!='A'));
  double cb=0,cs=0,s1=0,ef=0,rg=0,atr=0;int turns=0;
  if(eval){for(int i=6;i<=21;i++){char*v=strchr(cursor,',');if(!v)break;*v=0;fields[i]=v+1;cursor=v+1;}
   if(fields[20]){cb=atof(fields[12]);cs=atof(fields[13]);s1=atof(fields[16]);ef=atof(fields[17]);rg=atof(fields[18]);turns=atoi(fields[19]);atr=atof(fields[20]);}
   else eval=false;
  }
  h.update(ms,mid,bid,ask);rows++;
  // July quotes warm up rolling features only. The frozen policy is NEVER
  // evaluated until August 1. This is a true later-period entry replay.
  if(activeMonth==7) {prevsec=sec;continue;}
  if(minute!=curminute){
   curminute=minute;havefirst=false;havesecond=false;firstrole="";firstside=0;firstsec=0;
   int hour=int((ms/3600000)%24);
   for(const auto &pr:p.rate)tokens[pr.first]=min(3.,tokens[pr.first]+pr.second[hour]);
  }
  if(sec==prevsec)continue;
  prevsec=sec;
  if(!eval)continue;
  Candidate best;vector<double> f;
  if(!havefirst){
   const vector<string>roles=(ss<18)?vector<string>{"A_EARLY","B_FIRST","C_FIRST","D_FIRST"}:vector<string>{"A_LATE"};
   for(int side:{-1,1}){
    vector<string>eligible; eligible.reserve(roles.size());
    for(const auto&r:roles) if(tokens[r]>=1.0 && p.phase_qualified(r,side,ss)) eligible.push_back(r);
    if(eligible.empty())continue; // exact short-circuit: does not affect any emitted signal
    if(!h.features(ms,mid,side,atr,cb,cs,s1,ef,rg,turns,f))continue;
    for(const auto&r:eligible){Candidate c=p.score(f,r,side,atr);
      if(c.density>=c.threshold && c.score>best.score)best=c;
    }
   }
  }else if(firstrole[0]!='A' && ss>=max(18,firstsec+7)&&ss<=54){
    const string rr=firstrole.substr(0,1)+"_SECOND";
    if(tokens[rr]>=1.0 && p.phase_qualified(rr,-firstside,ss) &&
       h.features(ms,mid,-firstside,atr,cb,cs,s1,ef,rg,turns,f)){
      Candidate c=p.score(f,rr,-firstside,atr);
      if(c.density>=c.threshold)best=c;
    }
  }
  if(best.score<-1e8)continue;
  int leg=havefirst?2:1;bool requires_flat=leg==2;int price=int(round((best.side>0?ask:bid)*100.));
  o<<ms<<'\t'<<minute<<'\t'<<leg<<'\t'<<best.side<<'\t'<<best.role<<'\t'<<best.state<<'\t'<<fixed<<setprecision(6)<<best.score<<'\t'<<price<<'\t'<<int(requires_flat)<<'\n';
  intents++;tokens[best.role]=max(0.,tokens[best.role]-1.0);
  if(!havefirst){havefirst=true;firstrole=best.role;firstside=best.side;firstsec=ss;}
  else havesecond=true;
 }
 int rc=pclose(src);cerr<<"real_ticks="<<rows<<" independent_entry_intents="<<intents<<" process_rc="<<rc<<"\n";return rc?5:0;
}