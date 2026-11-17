//+------------------------------------------------------------------+
//| MICRO180 V28 HARD CHECKPOINT: JULY-FINAL ENTRY INTENT EA         |
//| Frozen C++ replay is behavioral source; NO automatic trade orders|
//| All 2,658 Jan-Jul experts loaded from byte-preserved TSV.        |
//| R9-Coinexx positive-cycle labels NEVER supplied to this EA.     |
//+------------------------------------------------------------------+
#property strict
#property version "28.11"
#property description "FROZEN V28 Jan-Jul dual-basket entry shadow. No order routing."

input string InpFrozenV28Weights="MICRO180_Jan_through_07_merged_weights.tsv";
input int InpCompletedM5ATRPeriod=14;
input bool InpLogEntryIntents=true;
input bool InpWriteIntentTSV=true;
input string InpIntentFilename="MICRO180_V28_MT5_ENTRY_INTENTS.tsv";
input bool InpRequireFull2658=true;
// Independent frozen C++ policy SHA256; this string is a deployment check,
// NOT an in-terminal SHA calculation. Verify the TSV with scripts/check_weights.py.
const string FROZEN_JULY_WEIGHTS_SHA256="92719ae1edd78c91e63f151da7d2f3607c7d5f42119b07613b8b20a7cce3997b";

#define NROLE 8
#define NFEAT 25
#define MAX_PROTOS 8192
#define SEC_RING 1024
#define MIN_RING 32
const string ROLE_NAMES[NROLE]={"A_EARLY","A_LATE","B_FIRST","C_FIRST","D_FIRST","B_SECOND","C_SECOND","D_SECOND"};
const int FEATURE_MAP[NFEAT]={3,4,5,6,7,8,9,10,11,12,13,17,18,20,21,22,24,25,26,27,30,31,32,33,36};

struct V28Proto {int role;int side;string state;double threshold;double center[NFEAT];double width[NFEAT];};
struct V28Minute {long minute;double o,h,l,c,sum;int n;};
struct V28Second {long second;double mid,bid,hi,lo;};
V28Proto gProto[MAX_PROTOS];int gProtoN=0;
double gMedian[NFEAT],gScale[NFEAT],gPhase[NROLE][2][60],gPhaseMin[NROLE][2],gRate[NROLE][24],gToken[NROLE],gPrior[NROLE];
V28Minute gMinutes[MIN_RING];int gMinuteHead=0,gMinuteCount=0;
V28Second gSecond[SEC_RING];long gActiveMinute=-1,gActiveSecond=-1;
V28Minute gActive;double gLastMid=0,gLastBid=0,gSecHigh=0,gSecLow=0;
double gOpenCycleMid=0;int gAtrHandle=INVALID_HANDLE;
long gPolicyMinute=-1;bool gHaveFirst=false,gHaveSecond=false;
int gModelCalendarMonth=-1,gIntentFile=INVALID_HANDLE;
int gFirstRole=-1,gFirstSide=0,gFirstSecond=0;

int RoleID(const string s){for(int i=0;i<NROLE;i++)if(ROLE_NAMES[i]==s)return i;return -1;}
int SideID(const int s){return s>0?1:0;}
double Clip(const double x,const double a,const double b){return MathMax(a,MathMin(b,x));}
V28Minute GetBarAgo(const int n){return gMinutes[(gMinuteHead-n+MIN_RING)%MIN_RING];}
void StoreMinute(){gMinutes[gMinuteHead]=gActive;gMinuteHead=(gMinuteHead+1)%MIN_RING;gMinuteCount=MathMin(MIN_RING,gMinuteCount+1);}
void ResetSecondHistory(){for(int i=0;i<SEC_RING;i++)gSecond[i].second=-1;}

bool LoadPositiveModel(){
 int f=FileOpen(InpFrozenV28Weights,FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
 if(f==INVALID_HANDLE){PrintFormat("V28: missing frozen model Common\\Files\\%s",InpFrozenV28Weights);return false;}
 while(!FileIsEnding(f)){
  string line=FileReadString(f);if(line=="")continue;
  string a[];int n=StringSplit(line,' ',a);if(n<2)continue;
  if(a[0]=="CENTER" && n>=NFEAT+1){for(int j=0;j<NFEAT;j++)gMedian[j]=StringToDouble(a[j+1]);}
  else if(a[0]=="SCALE" && n>=NFEAT+1){for(int j=0;j<NFEAT;j++)gScale[j]=StringToDouble(a[j+1]);}
  else if(a[0]=="PRIOR" && n>=3){int r=RoleID(a[1]);if(r>=0)gPrior[r]=StringToDouble(a[2]);}
  else if(a[0]=="RATE" && n>=4){int r=RoleID(a[1]),h=(int)StringToInteger(a[2]);if(r>=0&&h>=0&&h<24)gRate[r][h]=StringToDouble(a[3]);}
  else if(a[0]=="PHASEMIN" && n>=4){int r=RoleID(a[1]),side=SideID((int)StringToInteger(a[2]));if(r>=0)gPhaseMin[r][side]=StringToDouble(a[3]);}
  else if(a[0]=="P" && n>=63){int r=RoleID(a[1]),side=SideID((int)StringToInteger(a[2]));if(r>=0)for(int j=0;j<60;j++)gPhase[r][side][j]=StringToDouble(a[j+3]);}
  else if(a[0]=="G" && n>=56){
   if(gProtoN>=MAX_PROTOS){Print("V28: prototype capacity too small");FileClose(f);return false;}
   int r=RoleID(a[1]);if(r<0)continue;
   int k=gProtoN++;gProto[k].role=r;gProto[k].side=(int)StringToInteger(a[2]);
   gProto[k].state=a[3];gProto[k].threshold=StringToDouble(a[5]);
   for(int j=0;j<NFEAT;j++){gProto[k].center[j]=StringToDouble(a[j+6]);gProto[k].width[j]=StringToDouble(a[j+31]);}
  }
 }
 FileClose(f);
 PrintFormat("V28 hard checkpoint: experts=%d weights_sha256_expected=%s",gProtoN,FROZEN_JULY_WEIGHTS_SHA256);
 if(InpRequireFull2658 && gProtoN!=2658){Print("FROZEN V28: expected all 2658 experts");return false;}
 return gProtoN>0;
}

void UpdateQuote(const MqlTick &tick){
 long ms=tick.time_msc,minute=ms/60000,second=ms/1000;
 double mid=(tick.bid+tick.ask)*.5;
 if(minute!=gActiveMinute){
  if(gActiveMinute>=0){
   if(minute==gActiveMinute+1)StoreMinute();
   else {gMinuteHead=0;gMinuteCount=0;ResetSecondHistory();}
  }
  gActiveMinute=minute;gOpenCycleMid=mid;
  gActive.minute=minute;gActive.o=mid;gActive.h=mid;gActive.l=mid;gActive.c=mid;gActive.sum=mid;gActive.n=1;
 }else{
  gActive.h=MathMax(gActive.h,mid);gActive.l=MathMin(gActive.l,mid);
  gActive.c=mid;gActive.sum+=mid;gActive.n++;
 }
 if(gActiveSecond!=-1 && second!=gActiveSecond){
  int idx=(int)(gActiveSecond%SEC_RING);
  gSecond[idx].second=gActiveSecond;gSecond[idx].mid=gLastMid;gSecond[idx].bid=gLastBid;
  gSecond[idx].hi=gSecHigh;gSecond[idx].lo=gSecLow;
  gSecHigh=tick.bid;gSecLow=tick.bid;
 }else if(gActiveSecond==-1){gSecHigh=tick.bid;gSecLow=tick.bid;}
 gSecHigh=MathMax(gSecHigh,tick.bid);gSecLow=MathMin(gSecLow,tick.bid);
 gActiveSecond=second;gLastMid=mid;gLastBid=tick.bid;
}

double PastMid(const long s,const int age){
 long t=s-age;for(int k=0;k<4;k++){
  long z=t-k;int i=(int)(z%SEC_RING);if(i>=0&&gSecond[i].second==z)return gSecond[i].mid;
 }return EMPTY_VALUE;
}
double BarVWAP(const int n){double sum=0;int cnt=0;for(int i=1;i<=n;i++){V28Minute b=GetBarAgo(i);sum+=b.sum;cnt+=b.n;}return sum/MathMax(1,cnt);}
double BarSMA(const int n){double sum=0;for(int i=1;i<=n;i++)sum+=GetBarAgo(i).c;return sum/n;}
double BarEMA(const int n){double a=2./(n+1),v=GetBarAgo(gMinuteCount).c;
 for(int i=gMinuteCount-1;i>=1;i--)v=a*GetBarAgo(i).c+(1-a)*v;return v;}
double BarTR(const int n){double z=0;for(int i=n;i>=1;i--){V28Minute b=GetBarAgo(i),old=GetBarAgo(i+1);
 z+=MathMax(b.h-b.l,MathMax(MathAbs(b.h-old.c),MathAbs(b.l-old.c)));}return z/n;}
double Efficiency(const long s,const int n,const int step,const double mid,const int side){
 double sum=0,old=mid,latest=mid;
 for(int i=step;i<=n;i+=step){double x=PastMid(s,i);if(x==EMPTY_VALUE)return 0.; // frozen C++ returns zero efficiency on an internal gap
  sum+=MathAbs(old-x);old=x;latest=x;}
 return side*(mid-latest)/MathMax(.01,sum);
}
double RV(const long s,const int n,const int step,const double mid){double sum=0,old=mid;int cnt=0;
 for(int i=step;i<=n;i+=step){double x=PastMid(s,i);if(x==EMPTY_VALUE)break;
  sum+=(old-x)*(old-x);old=x;cnt++;}return cnt>0?MathSqrt(sum/cnt):0.;}
void S1Diagnostic(const long s,double &d,double &e,double &rng,int &turns){
 d=0;e=0;rng=0;turns=0;double first=0,last=0,travel=0,hi=-DBL_MAX,lo=DBL_MAX;int prevSign=0;
 for(int age=10;age>=1;age--){long t=s-age;int idx=(int)(t%SEC_RING);if(idx<0 || gSecond[idx].second!=t)continue;
  V28Second bar=gSecond[idx];hi=MathMax(hi,bar.hi);lo=MathMin(lo,bar.lo);
  if(first==0)first=bar.bid;
  if(last!=0){double dx=bar.bid-last;travel+=MathAbs(dx);int sign=dx>0?1:dx<0?-1:0;
   if(sign!=0){if(prevSign!=0 && prevSign!=sign)turns++;prevSign=sign;}}
  last=bar.bid;
 }
 d=last-first;e=MathAbs(d)/MathMax(1e-9,travel);rng=hi>-DBL_MAX/2?hi-lo:0;
}
bool Features(const MqlTick &q,int side,double atr,double &v[]){
 if(gMinuteCount<21)return false;
 long s=q.time_msc/1000;double mid=(q.bid+q.ask)*.5;
 double p5=PastMid(s,5),p15=PastMid(s,15),p60=PastMid(s,60),p180=PastMid(s,180),p300=PastMid(s,300);
 if(p5==EMPTY_VALUE||p15==EMPTY_VALUE||p60==EMPTY_VALUE||p180==EMPTY_VALUE||p300==EMPTY_VALUE)return false;
 atr=MathMax(.5,atr);ArrayResize(v,38);ArrayInitialize(v,0.);
 double r5=side*(mid-p5)/atr,r15=side*(mid-p15)/atr,r60=side*(mid-p60)/atr;
 double r180=side*(mid-p180)/atr,r300=side*(mid-p300)/atr;
 double eff60=Efficiency(s,60,5,mid,side),eff180=Efficiency(s,180,15,mid,side),eff300=Efficiency(s,300,15,mid,side);
 // C++ reference represents missing internal path samples as zero efficiency;
 // the five explicit lookback endpoints above still must exist.
 double vv1=BarVWAP(1),vv3=BarVWAP(3),vv5=BarVWAP(5),sma3=BarSMA(3),sma5=BarSMA(5);
 double ema3=BarEMA(3),ema8=BarEMA(8),ema21=BarEMA(21);
 double hi1=GetBarAgo(1).h,lo1=GetBarAgo(1).l,hi3=-DBL_MAX,lo3=DBL_MAX,hi5=-DBL_MAX,lo5=DBL_MAX;
 double range5=0;
 for(int i=1;i<=5;i++){
  V28Minute b=GetBarAgo(i);hi5=MathMax(hi5,b.h);lo5=MathMin(lo5,b.l);range5+=b.h-b.l;
  if(i<=3){hi3=MathMax(hi3,b.h);lo3=MathMin(lo3,b.l);}}
 double qrv60=RV(s,60,5,mid),qrv300=RV(s,300,15,mid);
 double disp,eff,rng;int turns;S1Diagnostic(s,disp,eff,rng,turns);
 v[0]=(double)(s%60);v[1]=(double)((s/3600)%24);v[2]=side;
 v[3]=r5;v[4]=r15;v[5]=r60;v[6]=r180;v[7]=r300;
 v[8]=eff60;v[9]=eff180;v[10]=eff300;
 v[11]=side*(mid-vv1)/atr;v[12]=side*(mid-vv3)/atr;v[13]=side*(mid-vv5)/atr;
 v[14]=side*(mid-sma3)/atr;v[15]=side*(mid-sma5)/atr;
 v[16]=side*(mid-ema3)/atr;v[17]=side*(ema3-ema8)/atr;v[18]=side*(ema8-ema21)/atr;
 v[19]=side>0?(mid-hi1)/atr:(lo1-mid)/atr;
 v[20]=side>0?(mid-hi3)/atr:(lo3-mid)/atr;
 v[21]=side>0?(mid-hi5)/atr:(lo5-mid)/atr;
 v[22]=qrv60/atr;v[23]=qrv300/atr;v[24]=qrv60/MathMax(.01,qrv300);
 V28Minute last=GetBarAgo(1);v[25]=(last.h-last.l)/MathMax(.01,range5/5.);
 v[26]=BarTR(5)/MathMax(.01,BarTR(14));v[27]=side*(mid-gActive.o)/atr;
 v[28]=side*(mid-gActive.h)/atr;v[29]=side*(mid-gActive.l)/atr;
 v[30]=(side>0?q.ask-(gOpenCycleMid+.15):(gOpenCycleMid-.15)-q.bid)/atr;
 v[31]=(q.ask-q.bid)/atr;v[32]=side*disp/atr;v[33]=eff;
 v[34]=rng/atr;v[35]=turns;v[36]=(double)gActive.n/MathMax(1,last.n);v[37]=r60*r300;
 return true;
}
string StateName(const double &v[]){double r1=v[5],r3=v[6],r5=v[7],e=v[10],br=v[20],rv=v[24],cr=v[25];
 if(br>=.01||(br>-.08&&rv>.82&&cr>1.22))return "breakout";
 if(r1*r5<0&&MathAbs(r1)>.12&&MathAbs(r5)>.09)return "reversal";
 if(r1*r3>0&&r3*r5>0&&MathAbs(e)>.30)return "nested_trend";
 if(MathAbs(e)>.16&&MathAbs(r5)>.22)return "trend";
 if(MathAbs(e)<.13&&MathAbs(r5)<.15&&rv<.68)return "consolidation";
 return "transition";
}
double NormCDF(const double z){ // Standard normal CDF, stable polynomial approximation
 double az=MathAbs(z),t=1./(1.+.2316419*az);
 double poly=t*(.319381530+t*(-.356563782+t*(1.781477937+t*(-1.821255978+t*1.330274429))));
 double cc=1.-.398942280401*MathExp(-.5*az*az)*poly;
 return z>=0?cc:1.-cc;
}
double HitProbability(const double &v[],double atr){
 atr=MathMax(.1,atr);double gap=MathMax(0.,.15-atr*v[27]);if(gap<=0)return 1.;
 double T=MathMax(1.,60.-v[0]);double drift=atr*(.55*v[5]/60.+.30*v[6]/180.+.15*v[7]/300.);
 double sigma=MathMax(.005,atr*v[22]/MathSqrt(5.)),den=MathMax(1e-9,sigma*MathSqrt(T));
 return Clip(NormCDF((drift*T-gap)/den)+MathExp(Clip(2*drift*gap/(sigma*sigma),-60.,60.))*NormCDF((-drift*T-gap)/den),0.,1.);
}
bool ScoreRole(const double &v[],double atr,const int role,const int side,double &score,string &state){
 int sidx=SideID(side),second=(int)v[0];state=StateName(v);
 if(gPhase[role][sidx][second]+1e-10<gPhaseMin[role][sidx])return false;
 double z[NFEAT];for(int i=0;i<NFEAT;i++)z[i]=Clip((v[FEATURE_MAP[i]]-gMedian[i])/MathMax(.03,gScale[i]),-8.,8.);
 bool found=false;double best=-DBL_MAX,bestThresh=0;
 double fastWeight=(state=="breakout"||state=="reversal")?.72:((state=="trend"||state=="nested_trend")?.40:.50);
 bool hasState=false;
 for(int k=0;k<gProtoN;k++)if(gProto[k].role==role && gProto[k].side==side && gProto[k].state==state){hasState=true;break;}
 for(int k=0;k<gProtoN;k++){
  if(gProto[k].role!=role||gProto[k].side!=side)continue;
  if(gProto[k].state!=(hasState?state:"ANY"))continue;
  double fast=0,slow=0;int nf=0,ns=0;
  for(int i=0;i<NFEAT;i++){
   double dx=Clip((z[i]-gProto[k].center[i])/MathMax(.45,gProto[k].width[i]),-8,8);
   bool isFast=(i==0||i==1||i==2||i==5||i==8||i==15||i==19||i==20||i==22||i==23||i==24);
   if(isFast){fast+=MathLog(1.+dx*dx);nf++;}else{slow+=MathLog(1.+dx*dx);ns++;}
  }
  double density=-(fastWeight*fast/nf+(1.-fastWeight)*slow/ns);
  // SOURCE-EXACT C++ V28 QUIRK: reference Candidate.score remains -1e9
  // during its prototype loop, so EVERY candidate overwrites the previous.
  // The LAST matching expert wins. Do NOT "fix" this into max-density:
  // doing so alters the frozen human-approved V28 entry behavior.
  found=true;best=density;bestThresh=gProto[k].threshold;
 }
 if(!found)return false; // Fail closed for unavailable state (no universal family policy).
 if(best<bestThresh)return false; // Positive-anchor thresholds only; model abstention is not precision certification.
 score=best+.12*MathLog(MathMax(.00001,gPhase[role][sidx][second])*60.)
       +.10*MathLog(MathMax(.01,HitProbability(v,atr)))
       +.8*MathLog(MathMax(.00001,gPrior[role]));
 return true;
}

int OnInit(){
 ResetSecondHistory();gAtrHandle=iATR(_Symbol,PERIOD_M5,InpCompletedM5ATRPeriod);
 if(gAtrHandle==INVALID_HANDLE)return INIT_FAILED;
 if(!LoadPositiveModel())return INIT_FAILED;
 if(InpWriteIntentTSV){
  gIntentFile=FileOpen(InpIntentFilename,FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
  if(gIntentFile==INVALID_HANDLE){Print("Cannot create intent trace in Common\\Files; err=",GetLastError());return INIT_FAILED;}
  FileWriteString(gIntentFile,"ms\tminute\tleg\tside\trole\tstate\tscore\tprice_u\tconditional_on_flat\r\n");
  FileFlush(gIntentFile);
 }
 Print("MICRO180 V28 FROZEN ENTRY SHADOW loaded; no order, hold, exit or cash logic.");
 return INIT_SUCCEEDED;
}
void OnDeinit(const int reason){
 if(gIntentFile!=INVALID_HANDLE){FileFlush(gIntentFile);FileClose(gIntentFile);}
 if(gAtrHandle!=INVALID_HANDLE)IndicatorRelease(gAtrHandle);
}
void OnTick(){
 MqlTick q;if(!SymbolInfoTick(_Symbol,q)||q.time_msc<=0)return;
 long sec=q.time_msc/1000,minute=q.time_msc/60000;
 // The accepted C++ forward replay resets only token budgets when entering
 // August and September; it preserves rolling structural history.
 MqlDateTime dt;TimeToStruct((datetime)sec,dt);
 int monthKey=dt.year*12+dt.mon;
 if(gModelCalendarMonth!=monthKey){
  for(int r=0;r<NROLE;r++)gToken[r]=0.;
  gModelCalendarMonth=monthKey;
 }
 bool newSec=(sec!=gActiveSecond),newMinute=(minute!=gPolicyMinute);
 int sourceSecond=(int)(sec%60);
 // Source-exact ordering: the C++ replay determines whether to evaluate
 // a quote BEFORE resetting the minute's first/second basket state.
 bool evalBeforeMinuteReset=(newSec &&
  ((!gHaveFirst && sourceSecond<=44) ||
   (gHaveFirst && !gHaveSecond && gFirstRole>=2 && gFirstRole<=4
       && sourceSecond>=18 && sourceSecond<=54)));
 UpdateQuote(q);
 if(newMinute){
  gPolicyMinute=minute;gHaveFirst=false;gHaveSecond=false;gFirstRole=-1;gFirstSide=0;gFirstSecond=0;
  int h=(int)((sec/3600)%24);
  for(int r=0;r<NROLE;r++)gToken[r]=MathMin(3.,gToken[r]+gRate[r][h]);
 }
 if(!evalBeforeMinuteReset)return;
 int s=sourceSecond;
 if(!gHaveFirst && s>44)return;
 if(gHaveFirst && (gFirstRole<0||gFirstRole<=1||gHaveSecond||s<MathMax(18,gFirstSecond+7)||s>54))return;
 double b[];if(CopyBuffer(gAtrHandle,0,1,1,b)!=1||b[0]<=0)return;
 double atr=b[0],best=-DBL_MAX;int selected=-1,selectedSide=0;string selectedState="";
 for(int side=-1;side<=1;side+=2){
  if(gHaveFirst&&side!=-gFirstSide)continue;
  double feat[];if(!Features(q,side,atr,feat))continue;
  for(int r=0;r<NROLE;r++){
   if(!gHaveFirst){if(s<18){if(r==1||r>=5)continue;}
                    else{if(s>44||r!=1)continue;}}
   else {if(r!=gFirstRole+3)continue;} // B_FIRST=2→B_SECOND=5; C=3→6; D=4→7
   if(gToken[r]<1.)continue;
   double score;string state;
   if(ScoreRole(feat,atr,r,side,score,state)&&score>best){best=score;selected=r;selectedSide=side;selectedState=state;}
  }
 }
 if(selected<0)return;
 gToken[selected]=MathMax(0.,gToken[selected]-1.);
 int leg=gHaveFirst?2:1;double entry=selectedSide>0?q.ask:q.bid;
 if(leg==1){gHaveFirst=true;gFirstRole=selected;gFirstSide=selectedSide;gFirstSecond=s;}
 else gHaveSecond=true;
 if(gIntentFile!=INVALID_HANDLE){
  int price_u=(int)MathRound(entry*100.);
  string out=StringFormat("%I64d\t%I64d\t%d\t%d\t%s\t%s\t%.6f\t%d\t%d\r\n",
              q.time_msc,minute,leg,selectedSide,ROLE_NAMES[selected],selectedState,best,price_u,(leg==2?1:0));
  FileWriteString(gIntentFile,out);
 }
 if(InpLogEntryIntents)
  PrintFormat("MICRO180_V28_ENTRY_INTENT ms=%I64d minute=%I64d leg=%d side=%s family_head=%s regime=%s real_quote=%.2f score=%.4f conditional_on_external_flat=%d",
              q.time_msc,minute,leg,selectedSide>0?"BUY":"SELL",ROLE_NAMES[selected],selectedState,entry,best,(leg==2));
}