#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "1.92"
#property strict
#property description "Gold MUWHAHA R9 LOGGER: trading logic identical to R9, plus per-tick tester instrumentation."

#include <Trade/Trade.mqh>
CTrade trade;

enum ENUM_GMM_SESSION
{
   GMM_SESSION_OFF = 0,
   GMM_SESSION_LONDON = 1,
   GMM_SESSION_OVERLAP = 2,
   GMM_SESSION_NEWYORK = 3
};

input group "R9 R5-style execution geometry"
input double InpLots                   = 0.01;
input int    InpGapPips                = 30;   // total bracket width = 0.30 at HunterPipPrice=0.01
input int    InpStopLossPips           = 30;
input bool   InpTrailingEnabled        = true;
input int    InpTrailPips              = 3;
input int    InpTrailActivationPips    = 10;
input int    InpMaxHoldSeconds         = 30;
input int    InpMaxSameMinuteRearms    = 3;
input ulong  InpMagic                  = 5559;

input group "R9 causal S1 quality gate"
input int    InpVelocityLookbackSec    = 10;
input int    InpMinVelocityPips        = 15;
input double InpMinDirectionalEff      = 0.70;
input int    InpRangeLookbackSec       = 10;
input int    InpMinRangePips           = 50;
input int    InpMaxTurns               = 9;

input group "R9 strategic regime gate"
input bool            InpUseRegimeGate     = true;
input ENUM_TIMEFRAMES InpAtrTimeframe      = PERIOD_M5;
input int             InpAtrPeriod         = 14;
input int             InpMaxSpreadPoints   = 25;
input bool            InpFailClosedOnNoATR = true;

input group "R9 session-adaptive ATR"
input bool   InpUseSessionAdaptiveAtr = true;
input int    InpQuoteUtcOffsetMinutes = 0;
input double InpAtrLondonPrice        = 2.00;
input double InpAtrOverlapPrice       = 1.75;
input double InpAtrNewYorkPrice       = 1.75;
input double InpAtrOffSessionPrice    = 2.50;

input group "Price normalization"
input double InpHunterPipPrice       = 0.01;
input bool   InpRespectBrokerStops   = true;

input group "Execution"
input int    InpDeviationPoints      = 20;
input bool   InpVerbose              = true;

input group "R9 tick logger"
input bool   InpTickLoggerEnabled    = true;
input string InpRunLabel             = "SYNTH"; // set SYNTH or REAL before each tester run
input bool   InpLogEveryTick         = true;

string EA_TAG = "GM_R9_LOGGER";

int      g_tickFile = INVALID_HANDLE;
string   g_tickFileName = "";
string   g_loggerEvent = "NONE";
double   g_loggerMFE = 0.0;
double   g_loggerMAE = 0.0;


#define MICRO_CAPACITY 128
struct MicroBar
{
   datetime second;
   double open;
   double high;
   double low;
   double close;
};
MicroBar g_micro[MICRO_CAPACITY];
int g_microHead=0;
int g_microCount=0;

bool g_bucketReady=false;
datetime g_bucketSecond=0;
double g_bucketOpen=0.0,g_bucketHigh=0.0,g_bucketLow=0.0,g_bucketClose=0.0;

datetime g_cycleMinute=0;
double g_cycleBuy=0.0,g_cycleSell=0.0;
int g_pendingMode=0; // 2 both, 1 buy only, -1 sell only, 0 none
int g_rearms=0;

bool g_hadPosition=false;
ENUM_POSITION_TYPE g_lastPositionType=POSITION_TYPE_BUY;
datetime g_positionOpenedAt=0;

int g_atrHandle=INVALID_HANDLE;
datetime g_lastGateLogBar=0;

void Log(const string text)
{
   if(InpVerbose) Print(EA_TAG, ": ", text);
}

int DigitsForSymbol(){ return (int)SymbolInfoInteger(_Symbol,SYMBOL_DIGITS); }

double TickSize()
{
   double v=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   if(v<=0.0) v=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   return v;
}

double NormalizePrice(const double price)
{
   const double tick=TickSize();
   if(tick<=0.0) return NormalizeDouble(price,DigitsForSymbol());
   return NormalizeDouble(MathRound(price/tick)*tick,DigitsForSymbol());
}

double NormalizeVolume(const double requested)
{
   const double mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   const double mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   const double st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   double v=MathMax(mn,MathMin(mx,requested));
   if(st>0.0) v=mn+MathRound((v-mn)/st)*st;
   return NormalizeDouble(MathMax(mn,MathMin(mx,v)),8);
}

double HunterDistance(const int pips){ return (double)pips*InpHunterPipPrice; }

double BrokerStopsDistance()
{
   const long stops=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL);
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   return (double)MathMax((long)0,stops)*point;
}

bool ResultAccepted()
{
   const uint c=trade.ResultRetcode();
   return (c==TRADE_RETCODE_DONE || c==TRADE_RETCODE_PLACED || c==TRADE_RETCODE_DONE_PARTIAL || c==TRADE_RETCODE_NO_CHANGES);
}

void LogTradeFailure(const string action)
{
   PrintFormat("%s: %s failed; retcode=%u (%s), lastError=%d",EA_TAG,action,trade.ResultRetcode(),trade.ResultRetcodeDescription(),GetLastError());
}

int DaysInMonth(const int year,const int month)
{
   if(month==2){ const bool leap=((year%400)==0 || ((year%4)==0 && (year%100)!=0)); return leap?29:28; }
   if(month==4 || month==6 || month==9 || month==11) return 30;
   return 31;
}

int DayOfWeekUtc(const int year,const int month,const int day)
{
   MqlDateTime v={}; v.year=year;v.mon=month;v.day=day;v.hour=12;
   const datetime s=StructToTime(v); MqlDateTime r={}; if(!TimeToStruct(s,r)) return -1; return r.day_of_week;
}

int NthSunday(const int year,const int month,const int nth)
{
   const int fd=DayOfWeekUtc(year,month,1); if(fd<0) return 0;
   const int first=1+((7-fd)%7); return first+(nth-1)*7;
}

int LastSunday(const int year,const int month)
{
   const int ld=DaysInMonth(year,month); const int dow=DayOfWeekUtc(year,month,ld); if(dow<0) return 0; return ld-dow;
}

datetime MakeUtc(const int year,const int month,const int day,const int hour,const int minute=0)
{
   MqlDateTime v={};v.year=year;v.mon=month;v.day=day;v.hour=hour;v.min=minute;return StructToTime(v);
}

bool IsLondonDstUtc(const datetime utc)
{
   MqlDateTime n={};if(!TimeToStruct(utc,n)) return false;
   return (utc>=MakeUtc(n.year,3,LastSunday(n.year,3),1,0) && utc<MakeUtc(n.year,10,LastSunday(n.year,10),1,0));
}

bool IsNewYorkDstUtc(const datetime utc)
{
   MqlDateTime n={};if(!TimeToStruct(utc,n)) return false;
   return (utc>=MakeUtc(n.year,3,NthSunday(n.year,3,2),7,0) && utc<MakeUtc(n.year,11,NthSunday(n.year,11,1),6,0));
}

int LocalMinuteOfDay(const datetime utc,const int offsetMinutes)
{
   MqlDateTime v={}; if(!TimeToStruct(utc+(datetime)(offsetMinutes*60),v)) return -1; return v.hour*60+v.min;
}

ENUM_GMM_SESSION CurrentSession()
{
   const datetime quote=TimeCurrent();
   const datetime utc=quote-(datetime)(InpQuoteUtcOffsetMinutes*60);
   const int lo=IsLondonDstUtc(utc)?60:0;
   const int no=IsNewYorkDstUtc(utc)?-240:-300;
   const int lm=LocalMinuteOfDay(utc,lo), nm=LocalMinuteOfDay(utc,no);
   const bool l=(lm>=8*60 && lm<16*60+30);
   const bool n=(nm>=8*60 && nm<17*60);
   if(l&&n) return GMM_SESSION_OVERLAP;
   if(l) return GMM_SESSION_LONDON;
   if(n) return GMM_SESSION_NEWYORK;
   return GMM_SESSION_OFF;
}

double SessionAtrMinimum(const ENUM_GMM_SESSION s)
{
   if(!InpUseSessionAdaptiveAtr) return InpAtrLondonPrice;
   if(s==GMM_SESSION_OVERLAP) return InpAtrOverlapPrice;
   if(s==GMM_SESSION_NEWYORK) return InpAtrNewYorkPrice;
   if(s==GMM_SESSION_LONDON) return InpAtrLondonPrice;
   return InpAtrOffSessionPrice;
}

bool GetCompletedAtr(double &atr)
{
   atr=0.0;
   if(!InpUseRegimeGate) return true;
   if(g_atrHandle==INVALID_HANDLE || BarsCalculated(g_atrHandle)<InpAtrPeriod+2) return false;
   double b[1]; ResetLastError();
   if(CopyBuffer(g_atrHandle,0,1,1,b)!=1 || !MathIsValidNumber(b[0]) || b[0]<=0.0) return false;
   atr=b[0]; return true;
}

bool GateAllowsEntry(const MqlTick &tick)
{
   if(!InpUseRegimeGate) return true;
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(point<=0.0 || tick.ask<=0.0 || tick.bid<=0.0) return false;
   const double sp=(tick.ask-tick.bid)/point;
   if(InpMaxSpreadPoints>0 && sp>(double)InpMaxSpreadPoints+1e-9) return false;
   double atr=0.0; const bool have=GetCompletedAtr(atr);
   if(!have) return !InpFailClosedOnNoATR;
   const double mn=SessionAtrMinimum(CurrentSession());
   if(mn>0.0 && atr+1e-12<mn)
   {
      const datetime bar=iTime(_Symbol,PERIOD_M1,0);
      if(InpVerbose && bar!=g_lastGateLogBar){ PrintFormat("%s: gate CLOSED ATR=%.5f min=%.5f spread=%.1f",EA_TAG,atr,mn,sp);g_lastGateLogBar=bar; }
      return false;
   }
   return true;
}

void PushCompletedSecond(const datetime sec,const double o,const double h,const double l,const double c)
{
   g_micro[g_microHead].second=sec;g_micro[g_microHead].open=o;g_micro[g_microHead].high=h;g_micro[g_microHead].low=l;g_micro[g_microHead].close=c;
   g_microHead=(g_microHead+1)%MICRO_CAPACITY;if(g_microCount<MICRO_CAPACITY) g_microCount++;
}

int RingIndexFromNewest(const int offset)
{
   int idx=g_microHead-1-offset;while(idx<0) idx+=MICRO_CAPACITY;return idx%MICRO_CAPACITY;
}

void UpdateSecondBucket(const MqlTick &tick)
{
   const datetime sec=tick.time;
   if(!g_bucketReady)
   {
      g_bucketReady=true;g_bucketSecond=sec;g_bucketOpen=tick.bid;g_bucketHigh=tick.bid;g_bucketLow=tick.bid;g_bucketClose=tick.bid;return;
   }
   if(sec!=g_bucketSecond)
   {
      PushCompletedSecond(g_bucketSecond,g_bucketOpen,g_bucketHigh,g_bucketLow,g_bucketClose);
      g_bucketSecond=sec;g_bucketOpen=tick.bid;g_bucketHigh=tick.bid;g_bucketLow=tick.bid;g_bucketClose=tick.bid;return;
   }
   if(tick.bid>g_bucketHigh) g_bucketHigh=tick.bid;
   if(tick.bid<g_bucketLow) g_bucketLow=tick.bid;
   g_bucketClose=tick.bid;
}

bool S1QualityForSide(const int side,double &disp,double &eff,double &range10,int &turns)
{
   disp=0.0;eff=0.0;range10=0.0;turns=0;
   const int need=MathMax(InpVelocityLookbackSec,InpRangeLookbackSec)+1;
   if(g_microCount<need) return false;

   const int oldest=RingIndexFromNewest(InpVelocityLookbackSec-1);
   double prev=g_micro[oldest].close;
   const double start=prev;
   double travel=0.0;
   double prevSign=0.0;

   for(int off=InpVelocityLookbackSec-2;off>=0;--off)
   {
      const int idx=RingIndexFromNewest(off);
      const double v=g_micro[idx].close;
      const double d=v-prev;
      travel+=MathAbs(d);
      const double s=(d>0.0?1.0:(d<0.0?-1.0:0.0));
      if(s!=0.0)
      {
         if(prevSign!=0.0 && s!=prevSign) turns++;
         prevSign=s;
      }
      prev=v;
   }
   const int newest=RingIndexFromNewest(0);
   disp=g_micro[newest].close-start;
   eff=MathAbs(disp)/(travel+1e-9);

   double hi=-DBL_MAX,lo=DBL_MAX;
   for(int off=0;off<InpRangeLookbackSec;++off)
   {
      const int idx=RingIndexFromNewest(off);
      if(g_micro[idx].high>hi) hi=g_micro[idx].high;
      if(g_micro[idx].low<lo) lo=g_micro[idx].low;
   }
   range10=hi-lo;

   if(eff+1e-12<InpMinDirectionalEff) return false;
   if(turns>InpMaxTurns) return false;
   if(range10+1e-12<HunterDistance(InpMinRangePips)) return false;
   const double minv=HunterDistance(InpMinVelocityPips);
   if(side>0 && disp+1e-12<minv) return false;
   if(side<0 && disp-1e-12>-minv) return false;
   return true;
}

bool FindOurPosition(ulong &ticket,ENUM_POSITION_TYPE &type,double &openPrice,double &stopLoss)
{
   ticket=0;openPrice=0.0;stopLoss=0.0;type=POSITION_TYPE_BUY;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong t=PositionGetTicket(i);if(t==0) continue;
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
      ticket=t;type=(ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);openPrice=PositionGetDouble(POSITION_PRICE_OPEN);stopLoss=PositionGetDouble(POSITION_SL);return true;
   }
   return false;
}

string SafeRunLabel()
{
   string x=InpRunLabel;
   StringReplace(x," ","_");
   StringReplace(x,"/","_");
   StringReplace(x,"\\","_");
   StringReplace(x,":","_");
   if(StringLen(x)==0) x="RUN";
   return x;
}

bool OpenTickLogger()
{
   if(!InpTickLoggerEnabled) return true;
   MqlDateTime now={};
   TimeToStruct(TimeLocal(),now);
   const string mode=(bool)MQLInfoInteger(MQL_TESTER)?"TESTER":"LIVE";
   const string stamp=StringFormat("%04d%02d%02d_%02d%02d%02d",now.year,now.mon,now.day,now.hour,now.min,now.sec);
   g_tickFileName="GoldMuwahaha_R9_TickLog_"+SafeRunLabel()+"_"+mode+"_"+stamp+".csv";
   ResetLastError();
   g_tickFile=FileOpen(g_tickFileName,FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
   if(g_tickFile==INVALID_HANDLE)
   {
      PrintFormat("%s: logger FileOpen failed file=%s error=%d",EA_TAG,g_tickFileName,GetLastError());
      return false;
   }
   FileWrite(g_tickFile,
      "run_label","time_msc","time","bid","ask","last","tick_volume","volume_real","flags","spread",
      "minute_start","minute_second","cycle_buy","cycle_sell","pending_mode","rearm_number",
      "s1_disp","s1_eff","s1_range","s1_turns","atr","session","gate_open",
      "position_open","position_side","entry_price","mfe","mae","current_sl","trail_armed","event");
   FileFlush(g_tickFile);
   PrintFormat("%s: tick logger enabled -> %s\\Files\\%s",EA_TAG,TerminalInfoString(TERMINAL_COMMONDATA_PATH),g_tickFileName);
   return true;
}

void CloseTickLogger()
{
   if(g_tickFile!=INVALID_HANDLE)
   {
      FileFlush(g_tickFile);
      FileClose(g_tickFile);
      g_tickFile=INVALID_HANDLE;
   }
}

void UpdateLoggerExcursion(const MqlTick &tick,const bool havePos,const ENUM_POSITION_TYPE type,const double openPrice)
{
   if(!havePos)
   {
      g_loggerMFE=0.0;
      g_loggerMAE=0.0;
      return;
   }

   double favorable=0.0,adverse=0.0;
   if(type==POSITION_TYPE_BUY)
   {
      favorable=tick.bid-openPrice;
      adverse=openPrice-tick.bid;
   }
   else
   {
      favorable=openPrice-tick.ask;
      adverse=tick.ask-openPrice;
   }
   if(favorable>g_loggerMFE) g_loggerMFE=favorable;
   if(adverse>g_loggerMAE) g_loggerMAE=adverse;
}

void LogTickState(const MqlTick &tick)
{
   if(!InpTickLoggerEnabled || !InpLogEveryTick || g_tickFile==INVALID_HANDLE) return;

   double disp=0.0,eff=0.0,rng=0.0; int turns=0;
   S1QualityForSide(1,disp,eff,rng,turns);

   double atr=0.0;
   const bool haveAtr=GetCompletedAtr(atr);
   const ENUM_GMM_SESSION session=CurrentSession();
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   const double spread=(point>0.0?(tick.ask-tick.bid)/point:0.0);
   bool gateOpen=true;
   if(InpUseRegimeGate)
   {
      gateOpen=haveAtr || !InpFailClosedOnNoATR;
      if(gateOpen && InpMaxSpreadPoints>0 && spread>(double)InpMaxSpreadPoints+1e-9) gateOpen=false;
      if(gateOpen && haveAtr)
      {
         const double mn=SessionAtrMinimum(session);
         if(mn>0.0 && atr+1e-12<mn) gateOpen=false;
      }
   }

   ulong ticket=0; ENUM_POSITION_TYPE ptype=POSITION_TYPE_BUY; double openPrice=0.0,sl=0.0;
   const bool havePos=FindOurPosition(ticket,ptype,openPrice,sl);
   UpdateLoggerExcursion(tick,havePos,ptype,openPrice);

   const int minuteSecond=(int)((long)tick.time%60);
   bool trailArmed=false;
   if(havePos && InpTrailingEnabled)
   {
      const double activation=HunterDistance(MathMax(0,InpTrailActivationPips));
      trailArmed=(ptype==POSITION_TYPE_BUY ? (tick.bid-openPrice)>=activation : (openPrice-tick.ask)>=activation);
   }

   FileWrite(g_tickFile,
      SafeRunLabel(),
      (long)tick.time_msc,
      TimeToString(tick.time,TIME_DATE|TIME_SECONDS),
      DoubleToString(tick.bid,_Digits),
      DoubleToString(tick.ask,_Digits),
      DoubleToString(tick.last,_Digits),
      (long)tick.volume,
      DoubleToString(tick.volume_real,8),
      (uint)tick.flags,
      DoubleToString(spread,3),
      TimeToString(g_cycleMinute,TIME_DATE|TIME_MINUTES),
      minuteSecond,
      DoubleToString(g_cycleBuy,_Digits),
      DoubleToString(g_cycleSell,_Digits),
      g_pendingMode,
      g_rearms,
      DoubleToString(disp,6),
      DoubleToString(eff,6),
      DoubleToString(rng,6),
      turns,
      DoubleToString(atr,6),
      (int)session,
      (gateOpen?1:0),
      (havePos?1:0),
      (havePos?(ptype==POSITION_TYPE_BUY?1:-1):0),
      DoubleToString(openPrice,_Digits),
      DoubleToString(g_loggerMFE,6),
      DoubleToString(g_loggerMAE,6),
      DoubleToString(sl,_Digits),
      (trailArmed?1:0),
      g_loggerEvent);

   if(g_loggerEvent!="NONE") FileFlush(g_tickFile);
}

bool OpenTrade(const int side,const MqlTick &tick)
{
   const double volume=NormalizeVolume(InpLots);
   const double brokerMin=InpRespectBrokerStops?BrokerStopsDistance()+TickSize():0.0;
   const double sd=MathMax(HunterDistance(InpStopLossPips),brokerMin);
   double sl=0.0;bool sent=false;
   ResetLastError();
   if(side>0){ sl=NormalizePrice(tick.bid-sd);sent=trade.Buy(volume,_Symbol,0.0,sl,0.0,EA_TAG+" BUY"); }
   else{ sl=NormalizePrice(tick.ask+sd);sent=trade.Sell(volume,_Symbol,0.0,sl,0.0,EA_TAG+" SELL"); }
   if(!sent || !ResultAccepted()){ LogTradeFailure(side>0?"BUY":"SELL");g_loggerEvent=(side>0?"ENTRY_BUY_FAIL":"ENTRY_SELL_FAIL");return false; }
   g_positionOpenedAt=tick.time;g_pendingMode=0;g_loggerMFE=0.0;g_loggerMAE=0.0;
   g_loggerEvent=(side>0?"ENTRY_BUY":"ENTRY_SELL");
   if(InpVerbose) PrintFormat("%s: %s entry minute=%s rearm=%d",EA_TAG,side>0?"BUY":"SELL",TimeToString(g_cycleMinute,TIME_DATE|TIME_MINUTES),g_rearms);
   return true;
}

void ManagePosition(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   if(g_positionOpenedAt>0 && (tick.time-g_positionOpenedAt)>=InpMaxHoldSeconds)
   {
      ResetLastError();
      if(!trade.PositionClose(ticket) || !ResultAccepted()) LogTradeFailure("max-hold close");
      else g_loggerEvent="EXIT_MAX_HOLD";
      return;
   }
   if(!InpTrailingEnabled || InpTrailPips<=0) return;
   const double trail=HunterDistance(InpTrailPips);
   const double activation=HunterDistance(InpTrailActivationPips);
   const double broker=InpRespectBrokerStops?BrokerStopsDistance():0.0;
   const double ts=TickSize();double cand=0.0;
   if(type==POSITION_TYPE_BUY)
   {
      if((tick.bid-openPrice)<activation) return;
      cand=NormalizePrice(tick.bid-trail);
      cand=MathMin(cand,NormalizePrice(tick.bid-broker-ts));
      if(cand<=0.0 || cand<=currentSL+ts*0.5) return;
   }
   else
   {
      if((openPrice-tick.ask)<activation) return;
      cand=NormalizePrice(tick.ask+trail);
      cand=MathMax(cand,NormalizePrice(tick.ask+broker+ts));
      if(cand<=0.0 || (currentSL>0.0 && cand>=currentSL-ts*0.5)) return;
   }
   ResetLastError();
   if(!trade.PositionModify(ticket,cand,0.0) || !ResultAccepted()) LogTradeFailure("trail modify");
   else g_loggerEvent="TRAIL_MOVE";
}

void StartMinuteCycle(const MqlTick &tick)
{
   const datetime m=(datetime)((long)tick.time-((long)tick.time%60));
   if(m==g_cycleMinute) return;
   g_cycleMinute=m;g_rearms=0;g_pendingMode=2;g_loggerEvent="MINUTE_START";
   const double mid=(tick.ask+tick.bid)*0.5;
   const double half=HunterDistance(InpGapPips)*0.5;
   g_cycleBuy=NormalizePrice(mid+half);g_cycleSell=NormalizePrice(mid-half);
}

void ArmOppositeAfterExit()
{
   if(g_rearms>=InpMaxSameMinuteRearms){ g_pendingMode=0;return; }
   g_rearms++;
   g_pendingMode=(g_lastPositionType==POSITION_TYPE_SELL)?1:-1;
   g_loggerEvent="REARM";
}

void ProcessEntries(const MqlTick &tick)
{
   if(g_pendingMode==0) return;
   if(!GateAllowsEntry(tick)) return;

   int side=0;
   if((g_pendingMode==2 || g_pendingMode==1) && tick.ask>=g_cycleBuy) side=1;
   else if((g_pendingMode==2 || g_pendingMode==-1) && tick.bid<=g_cycleSell) side=-1;
   if(side==0) return;

   g_loggerEvent=(side>0?"BRACKET_CROSS_BUY":"BRACKET_CROSS_SELL");
   double disp,eff,rng;int turns;
   if(!S1QualityForSide(side,disp,eff,rng,turns))
   {
      g_loggerEvent=(side>0?"QUALITY_REJECT_BUY":"QUALITY_REJECT_SELL");
      return;
   }
   g_loggerEvent=(side>0?"QUALITY_ACCEPT_BUY":"QUALITY_ACCEPT_SELL");
   if(InpVerbose) PrintFormat("%s: qualified side=%d disp=%.3f eff=%.3f range=%.3f turns=%d",EA_TAG,side,disp,eff,rng,turns);
   OpenTrade(side,tick);
}

void Reconcile(const MqlTick &tick)
{
   UpdateSecondBucket(tick);
   StartMinuteCycle(tick);

   ulong ticket;ENUM_POSITION_TYPE type;double openPrice,currentSL;
   const bool have=FindOurPosition(ticket,type,openPrice,currentSL);
   if(have)
   {
      g_hadPosition=true;g_lastPositionType=type;
      if(g_positionOpenedAt<=0) g_positionOpenedAt=(datetime)PositionGetInteger(POSITION_TIME);
      ManagePosition(tick,ticket,type,openPrice,currentSL);return;
   }

   if(g_hadPosition)
   {
      g_hadPosition=false;g_positionOpenedAt=0;
      const datetime nowMinute=(datetime)((long)tick.time-((long)tick.time%60));
      if(nowMinute==g_cycleMinute) ArmOppositeAfterExit(); else g_pendingMode=0;
      return;
   }
   ProcessEntries(tick);
}

int OnInit()
{
   if(InpLots<=0.0 || InpGapPips<=0 || InpStopLossPips<=0 || InpTrailPips<0 || InpTrailActivationPips<0 ||
      InpMaxHoldSeconds<=0 || InpMaxSameMinuteRearms<0 || InpVelocityLookbackSec<2 || InpRangeLookbackSec<2 ||
      InpVelocityLookbackSec>=MICRO_CAPACITY || InpRangeLookbackSec>=MICRO_CAPACITY || InpMinVelocityPips<0 ||
      InpMinDirectionalEff<0.0 || InpMinDirectionalEff>1.0 || InpMinRangePips<0 || InpMaxTurns<0 ||
      InpHunterPipPrice<=0.0 || InpAtrPeriod<=0 || InpMaxSpreadPoints<0)
   {
      Print(EA_TAG,": invalid inputs");return INIT_PARAMETERS_INCORRECT;
   }
   trade.SetExpertMagicNumber(InpMagic);trade.SetDeviationInPoints(InpDeviationPoints);trade.SetAsyncMode(false);
   if(!trade.SetTypeFillingBySymbol(_Symbol)) Log("warning: unable to derive filling mode");
   if(InpUseRegimeGate)
   {
      g_atrHandle=iATR(_Symbol,InpAtrTimeframe,InpAtrPeriod);
      if(g_atrHandle==INVALID_HANDLE){ PrintFormat("%s: ATR handle failed lastError=%d",EA_TAG,GetLastError());return INIT_FAILED; }
   }
   if(!OpenTickLogger()) return INIT_FAILED;
   PrintFormat("%s initialized gap=%d stop=%d trail=%d act=%d velLB=%d minVel=%d eff=%.2f range=%d maxHold=%d rearms=%d",
               EA_TAG,InpGapPips,InpStopLossPips,InpTrailPips,InpTrailActivationPips,InpVelocityLookbackSec,InpMinVelocityPips,InpMinDirectionalEff,InpMinRangePips,InpMaxHoldSeconds,InpMaxSameMinuteRearms);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   CloseTickLogger();
   if(g_atrHandle!=INVALID_HANDLE){ IndicatorRelease(g_atrHandle);g_atrHandle=INVALID_HANDLE; }
   Log(StringFormat("deinit reason=%d",reason));
}

void OnTick()
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol,tick) || tick.bid<=0.0 || tick.ask<=0.0) return;
   g_loggerEvent="NONE";
   Reconcile(tick);
   LogTickState(tick);
}
