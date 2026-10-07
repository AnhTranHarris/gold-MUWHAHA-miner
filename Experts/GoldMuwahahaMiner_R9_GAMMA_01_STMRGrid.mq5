#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "9.40"
#property strict
#property description "Gold MUWHAHA R9 GAMMA-01 STMR Grid: exact R9 HybridGate core plus Jan-Jul session/timeframe grid sleeve."

#include <Trade/Trade.mqh>
CTrade trade;
CTrade gridTrade;

/*
===============================================================================
 R9 GAMMA-01 STMR GRID — MAINTENANCE / PROVENANCE MAP
===============================================================================
 BASE CODE AUTHORITY
   Branch: carson/r9-gamma-00-baseline
   EA: Experts/GoldMuwahahaMiner_R9_HybridGate.mq5
   Base EA blob SHA: 7eecb5f1947017a01ce85b2520725de54749e523

 GRID RESEARCH AUTHORITY
   Candidate: STMR_XMONTH_SUBPHASE_001
   Research branch: delta-A-alpha-stmr-janjul-stress-20261006
   Authoritative stress journal: 0028_DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_JANJUL_STRESS_003.json
   Clean-room Jan-Jul comparator: +$829.71 / PF 1.2967425592 / 2,675 trades
   Authoritative January research floor remains STMR_SLEEVE_PHASE_001 +$877.78.

 DESIGN INTENT
   This file is CUMULATIVE: the original R9 HybridGate core remains available and
   independently switchable, while the STMR grid runs as an isolated second
   magic-number sleeve on the same XAUUSD tick stream.

 A/B CERTIFICATION MODES
   Core only : InpCoreEnabled=true,  InpGridEnabled=false
   Grid only : InpCoreEnabled=false, InpGridEnabled=true
   Combined  : InpCoreEnabled=true,  InpGridEnabled=true   [default]

 EDIT MAP — SEARCH THESE TAGS BEFORE CHANGING BEHAVIOR
   [CORE-00] Original R9 HybridGate logic. Keep behavior-identical.
   [GRID-01] Fixed UTC session translation / test envelope.
   [GRID-02] Completed H4/H1/M15/M5 EMA(8/21) state engine.
   [GRID-03] Session-local lattice / sleeve-local first-touch genealogy.
   [GRID-04] Sleeve classifier / funded sleeve list / subphase gates.
   [GRID-05] TP/SL + 300-second lifecycle.
   [GRID-06] Grid ticket execution / fill-relative stop anchoring.
   [GRID-07] Decision logger / Python-to-MT5 reconciliation.
   [INTEGRATION] Core/grid initialization, isolation, and call order.

 IMPORTANT
   Do not "fix" Python/MT5 differences by tuning this EA first. Diagnose clock,
   timeframe state, lattice, sleeve, then broker execution. Scientific changes
   to GRID-02..GRID-05 require a fresh Python replay before promotion.
===============================================================================
*/

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


input group "GAMMA-01 cumulative integration"
input bool   InpCoreEnabled              = true;
input bool   InpGridEnabled              = true;
input ulong  InpGridMagic                = 5593001;
input int    InpGridDeviationPoints      = 20;
input bool   InpGridRequireHedging       = true;

input group "STMR grid certification envelope"
input datetime InpGridWarmupStartUtc     = D'2026.01.01 00:00:00';
input datetime InpGridEntryStartUtc      = D'2026.01.05 00:00:00';
input datetime InpGridEntryEndUtc        = D'2026.08.01 00:00:00'; // do not test August

input group "STMR grid parity diagnostics"
input bool InpGridDecisionLoggerEnabled  = true;
input bool InpGridFlushDecisionLogOften  = false;

string EA_TAG = "GM_R9_HYBRID";
string GRID_TAG = "GM_R9_GAMMA_STMR";

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

bool OpenTrade(const int side,const MqlTick &tick)
{
   const double volume=NormalizeVolume(InpLots);
   const double brokerMin=InpRespectBrokerStops?BrokerStopsDistance()+TickSize():0.0;
   const double sd=MathMax(HunterDistance(InpStopLossPips),brokerMin);
   double sl=0.0;bool sent=false;
   ResetLastError();
   if(side>0){ sl=NormalizePrice(tick.bid-sd);sent=trade.Buy(volume,_Symbol,0.0,sl,0.0,EA_TAG+" BUY"); }
   else{ sl=NormalizePrice(tick.ask+sd);sent=trade.Sell(volume,_Symbol,0.0,sl,0.0,EA_TAG+" SELL"); }
   if(!sent || !ResultAccepted()){ LogTradeFailure(side>0?"BUY":"SELL");return false; }
   g_positionOpenedAt=tick.time;g_pendingMode=0;
   if(InpVerbose) PrintFormat("%s: %s entry minute=%s rearm=%d",EA_TAG,side>0?"BUY":"SELL",TimeToString(g_cycleMinute,TIME_DATE|TIME_MINUTES),g_rearms);
   return true;
}

void ManagePosition(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   if(g_positionOpenedAt>0 && (tick.time-g_positionOpenedAt)>=InpMaxHoldSeconds)
   {
      ResetLastError();if(!trade.PositionClose(ticket) || !ResultAccepted()) LogTradeFailure("max-hold close");return;
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
   ResetLastError();if(!trade.PositionModify(ticket,cand,0.0) || !ResultAccepted()) LogTradeFailure("trail modify");
}

void StartMinuteCycle(const MqlTick &tick)
{
   const datetime m=(datetime)((long)tick.time-((long)tick.time%60));
   if(m==g_cycleMinute) return;
   g_cycleMinute=m;g_rearms=0;g_pendingMode=2;
   const double mid=(tick.ask+tick.bid)*0.5;
   const double half=HunterDistance(InpGapPips)*0.5;
   g_cycleBuy=NormalizePrice(mid+half);g_cycleSell=NormalizePrice(mid-half);
}

void ArmOppositeAfterExit()
{
   if(g_rearms>=InpMaxSameMinuteRearms){ g_pendingMode=0;return; }
   g_rearms++;
   g_pendingMode=(g_lastPositionType==POSITION_TYPE_SELL)?1:-1;
}

void ProcessEntries(const MqlTick &tick)
{
   if(g_pendingMode==0) return;
   if(!GateAllowsEntry(tick)) return;

   int side=0;
   if((g_pendingMode==2 || g_pendingMode==1) && tick.ask>=g_cycleBuy) side=1;
   else if((g_pendingMode==2 || g_pendingMode==-1) && tick.bid<=g_cycleSell) side=-1;
   if(side==0) return;

   double disp,eff,rng;int turns;
   if(!S1QualityForSide(side,disp,eff,rng,turns)) return;
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


// ============================================================================
// [GRID-01..07] STMR_XMONTH_SUBPHASE_001 SIDE-CAR MODULE
// ============================================================================
// -------------------------------
// Frozen research constants.
// -------------------------------
#define STMR_SLEEVE_COUNT 12
#define STMR_SEEN_KEYS 32768
#define STMR_SEEN_TOTAL (STMR_SLEEVE_COUNT*STMR_SEEN_KEYS)
#define STMR_KEY_OFFSET 16384

const long STMR_DAY_MS = 86400000;
const long STMR_MAX_HOLD_MS = 300000;
const double STMR_LOTS = 0.01;
const int STMR_MAX_POSITIONS = 3;
const double STMR_RAW_SCALE = 1000.0; // 1 raw unit = $0.001

// session codes: 0 Asia, 1 LondonOpen, 2 London, 3 Overlap, 4 NY, 5 LateNY, 6 Rollover
int g_gapRaw[7] = {750,0,1000,750,1500,500,0};

// sleeve order matches Python artifact.
string g_sleeveName[STMR_SLEEVE_COUNT] =
{
   "ASIA_LOWER_TAKEOVER",
   "ASIA_M15_DIVERGE_M5_RECLAIM",
   "LONDON_M5_TAKEOVER",
   "LONDON_M5_RECLAIM",
   "OVERLAP_LOWER_TAKEOVER",
   "OVERLAP_ALIGNED_COUNTERCROSS",
   "NY_LOWER_TRANSFER",
   "NY_LOWER_COUNTERCROSS",
   "LATE_ALIGNED_MOMENTUM",
   "LATE_MACRO_SPLIT_TRANSFER",
   "LATE_M5_REJECTION",
   "LATE_LOWER_TAKEOVER"
};

// Price-distance raw units.  Only funded sleeves are executable.
int g_tpRaw[STMR_SLEEVE_COUNT] = {4000,4000,4000,3000,4000,3000,4000,2500,4000,4000,4000,2500};
int g_slRaw[STMR_SLEEVE_COUNT] = {1000,1500,750,750,1500,750,1500,1500,1500,1500,1500,1250};

// Flattened semantic sleeve-local first-touch memory.  Cleared at every session transition.
uchar g_seen[STMR_SEEN_TOTAL];

// -------------------------------
// [EDIT-02] Custom completed-bar EMA engine.
// Uses tick Bid closes and UTC epoch buckets to match Python bar_states_span().
// -------------------------------
struct TfState
{
   long tf_ms;
   long bucket;
   bool have_bucket;
   long close_raw;
   bool ema_ready;
   double ema8;
   double ema21;
   int state; // -1,0,+1 for the most recently COMPLETED observed bucket
};

TfState g_h4, g_h1, g_m15, g_m5;

// -------------------------------
// [EDIT-03] Session-local lattice state.
// -------------------------------
int  g_session = -1;
long g_anchorRaw = 0;
long g_prevCell = 0;
long g_crossingId = 0;

// Diagnostics.
long g_crossings = 0;
long g_fundedCrossings = 0;
long g_entriesAttempted = 0;
long g_entriesOpened = 0;
long g_seenBlocks = 0;
long g_directionBlocks = 0;
long g_phaseBlocks = 0;
long g_capSkips = 0;
long g_orderFailures = 0;
long g_ageCloseAttempts = 0;
long g_sleeveAttempts[STMR_SLEEVE_COUNT];
long g_sleeveOpened[STMR_SLEEVE_COUNT];

int g_logFile = INVALID_HANDLE;
long g_logRows = 0;



/* [GRID-06] CTrade result isolation: never read the R9 core CTrade retcode here. */
bool GridResultAccepted()
{
   const uint c=gridTrade.ResultRetcode();
   return (c==TRADE_RETCODE_DONE || c==TRADE_RETCODE_PLACED ||
           c==TRADE_RETCODE_DONE_PARTIAL || c==TRADE_RETCODE_NO_CHANGES);
}

void GridLogTradeFailure(const string action)
{
   PrintFormat("%s: %s failed; retcode=%u (%s), lastError=%d",
               GRID_TAG,action,gridTrade.ResultRetcode(),
               gridTrade.ResultRetcodeDescription(),GetLastError());
}

long PriceToRaw(const double price)
{
   return (long)MathRound(price*STMR_RAW_SCALE);
}

double RawDistanceToPrice(const int raw)
{
   return ((double)raw)/STMR_RAW_SCALE;
}

long FloorDiv(const long numerator,const int denominator)
{
   if(denominator<=0) return 0;
   if(numerator>=0) return numerator/(long)denominator;
   return -(((-numerator)+(long)denominator-1)/(long)denominator);
}

long ToUtcMs(const long server_ms)
{
   return server_ms-(long)InpQuoteUtcOffsetMinutes*60000L;
}

long WarmupStartMs(){ return (long)InpGridWarmupStartUtc*1000L; }
long EntryStartMs(){ return (long)InpGridEntryStartUtc*1000L; }
long EntryEndMs(){ return (long)InpGridEntryEndUtc*1000L; }

string SessionName(const int s)
{
   switch(s)
   {
      case 0:return "ASIA";
      case 1:return "LONDON_OPEN";
      case 2:return "LONDON";
      case 3:return "OVERLAP";
      case 4:return "NEW_YORK";
      case 5:return "LATE_NY";
      case 6:return "ROLLOVER";
   }
   return "UNKNOWN";
}

// -------------------------------
// [EDIT-01] Fixed UTC session clock from the frozen Python clean-room child.
// -------------------------------
int SessionCodeFixed(const long utc_ms)
{
   long tod=utc_ms%STMR_DAY_MS;
   if(tod<0) tod+=STMR_DAY_MS;
   if(tod>=23L*3600000L || tod<7L*3600000L) return 0;
   if(tod<9L*3600000L) return 1;
   if(tod<13L*3600000L+30L*60000L) return 2;
   if(tod<16L*3600000L) return 3;
   if(tod<20L*3600000L) return 4;
   if(tod<22L*3600000L) return 5;
   return 6;
}

int MinuteOfDayUtc(const long utc_ms)
{
   long tod=utc_ms%STMR_DAY_MS;
   if(tod<0) tod+=STMR_DAY_MS;
   return (int)(tod/60000L);
}

void InitTf(TfState &s,const long tf_ms)
{
   s.tf_ms=tf_ms;
   s.bucket=0;
   s.have_bucket=false;
   s.close_raw=0;
   s.ema_ready=false;
   s.ema8=0.0;
   s.ema21=0.0;
   s.state=0;
}

void ApplyCompletedClose(TfState &s,const long close_raw)
{
   const double c=(double)close_raw;
   if(!s.ema_ready)
   {
      // Python seeds EMA8 and EMA21 with the first observed completed bar close.
      s.ema8=c;
      s.ema21=c;
      s.ema_ready=true;
      s.state=0;
      return;
   }

   const double a8=2.0/9.0;
   const double a21=2.0/22.0;
   s.ema8=a8*c+(1.0-a8)*s.ema8;
   s.ema21=a21*c+(1.0-a21)*s.ema21;
   if(s.ema8>s.ema21) s.state=1;
   else if(s.ema8<s.ema21) s.state=-1;
   else s.state=0;
}

void UpdateTf(TfState &s,const long utc_ms,const long bid_raw)
{
   const long bucket=utc_ms/s.tf_ms;
   if(!s.have_bucket)
   {
      s.bucket=bucket;
      s.close_raw=bid_raw;
      s.have_bucket=true;
      return;
   }

   if(bucket==s.bucket)
   {
      s.close_raw=bid_raw;
      return;
   }

   if(bucket>s.bucket)
   {
      const long completed_open_ms=s.bucket*s.tf_ms;
      if(completed_open_ms>=WarmupStartMs()) ApplyCompletedClose(s,s.close_raw);
      // Missing clock buckets are intentionally NOT synthesized.  Python only
      // advances EMA over buckets that actually contain ticks.
      s.bucket=bucket;
      s.close_raw=bid_raw;
      return;
   }

   // Defensive only: tester tick time should never move backward.
   PrintFormat("%s: WARNING backward TF bucket tf=%I64d old=%I64d new=%I64d",
               GRID_TAG,s.tf_ms,s.bucket,bucket);
}

void UpdateAllTimeframes(const long utc_ms,const long bid_raw)
{
   UpdateTf(g_h4, utc_ms,bid_raw);
   UpdateTf(g_h1, utc_ms,bid_raw);
   UpdateTf(g_m15,utc_ms,bid_raw);
   UpdateTf(g_m5, utc_ms,bid_raw);
}

// -------------------------------
// [EDIT-04] Sleeve state classifier.  Mirrors stmr_janjul.sleeve_state().
// -------------------------------
bool DetermineSleeve(const int s,const int h4,const int h1,const int m15,const int m5,
                     int &sleeve,int &expected_direction)
{
   sleeve=-1;
   expected_direction=0;
   const bool macro=(h4!=0 && h4==h1);

   if(s==0)
   {
      if(macro && m15==m5 && m15==-h1){ sleeve=0; expected_direction=m5; return true; }
      if(macro && m15==-h1 && m5==h1){ sleeve=1; expected_direction=m5; return true; }
   }
   else if(s==2)
   {
      if(macro && m15==h1 && m5==-h1){ sleeve=2; expected_direction=m5; return true; }
      if(macro && m15==-h1 && m5==h1){ sleeve=3; expected_direction=m5; return true; }
   }
   else if(s==3)
   {
      if(macro && m15==m5 && m15==-h1){ sleeve=4; expected_direction=m5; return true; }
      if(macro && m15==m5 && m15==h1){ sleeve=5; expected_direction=-m5; return true; }
   }
   else if(s==4)
   {
      if(h4!=0 && h1!=0 && h4!=h1)
      {
         if(m15!=0 && m5==-m15){ sleeve=6; expected_direction=m5; return true; }
         if(m15==m5 && m15!=0){ sleeve=7; expected_direction=-m5; return true; }
      }
   }
   else if(s==5)
   {
      if(h4==h1 && h1==m15 && m15==m5 && h4!=0){ sleeve=8; expected_direction=m5; return true; }
      if(h4!=0 && h1!=0 && h4!=h1 && m15!=0 && m5==-m15){ sleeve=9; expected_direction=m5; return true; }
      if(macro && m15==h1 && m5==-h1){ sleeve=10; expected_direction=-m5; return true; }
      if(macro && m15==m5 && m15==-h1){ sleeve=11; expected_direction=m5; return true; }
   }
   return false;
}

bool IsFundedSleeve(const int sleeve)
{
   return (sleeve==0 || sleeve==2 || sleeve==4 || sleeve==8 || sleeve==9 || sleeve==11);
}

bool SleevePhaseAllowed(const int sleeve,const long utc_ms)
{
   const int minute=MinuteOfDayUtc(utc_ms);
   // Accepted January gates retained.
   if(sleeve==0) return (minute>=1380);            // 23:00-24:00
   if(sleeve==2) return (minute>=660 && minute<720); // 11:00-12:00
   // Cross-month Stress-003 subphases.
   if(sleeve==4) return (minute>=900 && minute<960); // 15:00-16:00
   if(sleeve==11) return (minute>=1260 && minute<1320); // 21:00-22:00
   return true;
}

int SeenIndex(const int sleeve,const long key)
{
   if(sleeve<0 || sleeve>=STMR_SLEEVE_COUNT) return -1;
   if(key<0 || key>=STMR_SEEN_KEYS) return -1;
   return sleeve*STMR_SEEN_KEYS+(int)key;
}

void ResetSessionLattice(const int new_session,const long mid_raw)
{
   g_session=new_session;
   g_anchorRaw=mid_raw;
   g_prevCell=0;
   ArrayInitialize(g_seen,0);
   if(InpVerbose)
      PrintFormat("%s: session reset -> %s anchorRaw=%I64d",GRID_TAG,SessionName(new_session),mid_raw);
}

// -------------------------------
// Position utilities / [EDIT-05] lifecycle.
// -------------------------------
int OurPositionCount()
{
   int n=0;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong ticket=PositionGetTicket(i);
      if(ticket==0) continue;
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpGridMagic) continue;
      n++;
   }
   return n;
}

bool FindNewestOurPosition(ulong &ticket,double &open_price)
{
   ticket=0;
   open_price=0.0;
   long best_time=-1;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong t=PositionGetTicket(i);
      if(t==0) continue;
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpGridMagic) continue;
      const long tm=(long)PositionGetInteger(POSITION_TIME_MSC);
      if(tm>=best_time)
      {
         best_time=tm;
         ticket=t;
         open_price=PositionGetDouble(POSITION_PRICE_OPEN);
      }
   }
   return (ticket!=0);
}

void ManageAgeExits(const MqlTick &tick)
{
   // Broker-native SL/TP exits are processed by MT5.  We only implement the
   // Python hard maximum age = 300 seconds.
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong ticket=PositionGetTicket(i);
      if(ticket==0) continue;
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpGridMagic) continue;
      const long opened=(long)PositionGetInteger(POSITION_TIME_MSC);
      if(opened>0 && tick.time_msc-opened>=STMR_MAX_HOLD_MS)
      {
         g_ageCloseAttempts++;
         ResetLastError();
         if(!gridTrade.PositionClose(ticket) || !GridResultAccepted()) GridLogTradeFailure("300s age close");
      }
   }
}

bool StopsRespectBroker(const int direction,const MqlTick &tick,const double sl,const double tp)
{
   const long stops_points=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL);
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(stops_points<=0 || point<=0.0) return true;
   const double min_dist=(double)stops_points*point;
   if(direction>0)
      return ((tick.bid-sl)+1e-12>=min_dist && (tp-tick.ask)+1e-12>=min_dist);
   return ((sl-tick.ask)+1e-12>=min_dist && (tick.bid-tp)+1e-12>=min_dist);
}

// -------------------------------
// [EDIT-07] Compact decision/event logger for Python<->MT5 forensic matching.
// -------------------------------
string SafeStamp(const datetime t)
{
   MqlDateTime v={};
   TimeToStruct(t,v);
   return StringFormat("%04d%02d%02d_%02d%02d%02d",v.year,v.mon,v.day,v.hour,v.min,v.sec);
}

void OpenDecisionLog()
{
   if(!InpGridDecisionLoggerEnabled) return;
   const string mode=(MQLInfoInteger(MQL_TESTER)?"TESTER":"LIVE");
   const string name="GoldMuwahaha_R9_GAMMA01_STMR_"+mode+"_"+SafeStamp(TimeCurrent())+".csv";
   ResetLastError();
   g_logFile=FileOpen(name,FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI,',');
   if(g_logFile==INVALID_HANDLE)
   {
      PrintFormat("%s: decision log open failed name=%s lastError=%d",GRID_TAG,name,GetLastError());
      return;
   }
   FileWrite(g_logFile,
      "event_id","server_time_msc","utc_time_msc","session","h4","h1","m15","m5",
      "sleeve","sleeve_name","direction","expected","cell","key","anchor_raw","mid_raw",
      "bid","ask","seen_before","phase_ok","open_positions","action");
   FileFlush(g_logFile);
   PrintFormat("%s: decision log -> Common\Files\%s",GRID_TAG,name);
}

void DecisionLog(const MqlTick &tick,const long utc_ms,const int s,const int sleeve,
                 const int direction,const int expected,const long cell,const long key,
                 const long mid_raw,const bool seen_before,const bool phase_ok,
                 const int open_positions,const string action)
{
   if(g_logFile==INVALID_HANDLE) return;
   const string nm=(sleeve>=0 && sleeve<STMR_SLEEVE_COUNT)?g_sleeveName[sleeve]:"NONE";
   FileWrite(g_logFile,
      g_crossingId,tick.time_msc,utc_ms,SessionName(s),g_h4.state,g_h1.state,g_m15.state,g_m5.state,
      sleeve,nm,direction,expected,cell,key,g_anchorRaw,mid_raw,
      DoubleToString(tick.bid,DigitsForSymbol()),DoubleToString(tick.ask,DigitsForSymbol()),
      (seen_before?1:0),(phase_ok?1:0),open_positions,action);
   g_logRows++;
   if(InpGridFlushDecisionLogOften || (g_logRows%250)==0) FileFlush(g_logFile);
}

// -------------------------------
// [EDIT-06] Broker-native market execution.
// -------------------------------
bool OpenSleeveTrade(const int sleeve,const int direction,const MqlTick &tick)
{
   g_entriesAttempted++;
   g_sleeveAttempts[sleeve]++;

   const double distance_sl=RawDistanceToPrice(g_slRaw[sleeve]);
   const double distance_tp=RawDistanceToPrice(g_tpRaw[sleeve]);
   const double quoted_entry=(direction>0?tick.ask:tick.bid);
   double sl=(direction>0?quoted_entry-distance_sl:quoted_entry+distance_sl);
   double tp=(direction>0?quoted_entry+distance_tp:quoted_entry-distance_tp);
   sl=NormalizePrice(sl);
   tp=NormalizePrice(tp);

   if(!StopsRespectBroker(direction,tick,sl,tp))
   {
      g_orderFailures++;
      PrintFormat("%s: skip %s — broker stop-distance constraint sl=%.5f tp=%.5f",
                  GRID_TAG,g_sleeveName[sleeve],sl,tp);
      return false;
   }

   const string comment=StringFormat("STMR E%I64d S%d",g_crossingId,sleeve);
   ResetLastError();
   bool sent=false;
   if(direction>0) sent=gridTrade.Buy(STMR_LOTS,_Symbol,0.0,sl,tp,comment);
   else sent=gridTrade.Sell(STMR_LOTS,_Symbol,0.0,sl,tp,comment);

   if(!sent || !GridResultAccepted())
   {
      g_orderFailures++;
      GridLogTradeFailure(direction>0?"BUY":"SELL");
      return false;
   }

   // Re-anchor SL/TP to the actual broker-confirmed position fill.  This keeps
   // geometry exact even if Coinexx fills away from the triggering quote.
   ulong ticket=0;
   double fill=0.0;
   if(FindNewestOurPosition(ticket,fill))
   {
      const double exact_sl=NormalizePrice(direction>0?fill-distance_sl:fill+distance_sl);
      const double exact_tp=NormalizePrice(direction>0?fill+distance_tp:fill-distance_tp);
      if(MathAbs(exact_sl-sl)>TickSize()*0.25 || MathAbs(exact_tp-tp)>TickSize()*0.25)
      {
         ResetLastError();
         if(!gridTrade.PositionModify(ticket,exact_sl,exact_tp) || !GridResultAccepted())
         {
            GridLogTradeFailure("fill-relative SL/TP modify");
            // Fail closed: an unfaithful lifecycle is worse than a skipped gridTrade.
            ResetLastError();
            if(!gridTrade.PositionClose(ticket) || !GridResultAccepted()) GridLogTradeFailure("cleanup after SL/TP modify failure");
            g_orderFailures++;
            return false;
         }
      }
   }

   g_entriesOpened++;
   g_sleeveOpened[sleeve]++;
   return true;
}

// -------------------------------
// Main crossing engine.
// -------------------------------
void ProcessCrossing(const MqlTick &tick,const long utc_ms,const long mid_raw)
{
   const int s=SessionCodeFixed(utc_ms);
   if(s!=g_session)
   {
      ResetSessionLattice(s,mid_raw);
      return; // Python also emits no crossing on the session-reset tick.
   }

   const int gap=g_gapRaw[s];
   if(gap<=0) return;

   const long cell=FloorDiv(mid_raw-g_anchorRaw,gap);
   if(cell==g_prevCell) return;

   g_crossingId++;
   g_crossings++;
   const int direction=(cell>g_prevCell?1:-1);

   int sleeve=-1,expected=0;
   const bool have_sleeve=DetermineSleeve(s,g_h4.state,g_h1.state,g_m15.state,g_m5.state,sleeve,expected);
   const long key_cell=(direction>0?cell:g_prevCell);
   const long key=key_cell+STMR_KEY_OFFSET;

   if(have_sleeve && IsFundedSleeve(sleeve) && key>=0 && key<STMR_SEEN_KEYS)
   {
      g_fundedCrossings++;
      const int si=SeenIndex(sleeve,key);
      const bool seen_before=(si>=0 && g_seen[si]!=0);
      const bool phase_ok=SleevePhaseAllowed(sleeve,utc_ms);
      const int open_positions=OurPositionCount();

      string action="MARK_ONLY";
      if(seen_before)
      {
         g_seenBlocks++;
         action="SEEN_BLOCK";
      }
      else if(direction!=expected)
      {
         g_directionBlocks++;
         action="DIRECTION_BLOCK";
      }
      else if(!phase_ok)
      {
         g_phaseBlocks++;
         action="PHASE_BLOCK";
      }
      else if(utc_ms<EntryStartMs() || utc_ms>=EntryEndMs())
      {
         action="OUTSIDE_ENTRY_WINDOW";
      }
      else if(open_positions>=STMR_MAX_POSITIONS)
      {
         g_capSkips++;
         action="CAP_SKIP";
      }
      else
      {
         const bool ok=OpenSleeveTrade(sleeve,direction,tick);
         action=(ok?"ENTRY_OPENED":"ENTRY_FAILED");
      }

      // IMPORTANT parity rule: once a funded sleeve sees this semantic cell,
      // mark it regardless of direction/phase/order outcome.  The Python
      // clean-room simulator does the same and never timer-rearms the cell.
      if(si>=0) g_seen[si]=1;
      DecisionLog(tick,utc_ms,s,sleeve,direction,expected,cell,key,mid_raw,
                  seen_before,phase_ok,open_positions,action);
   }

   // IMPORTANT: exactly one landing-cell crossing decision per ordered tick.
   // We do NOT loop through every skipped cell in a large tick jump.
   g_prevCell=cell;
}


/* [INTEGRATION] Initialize only the STMR sidecar. */
int GridInit()
{
   if(_Symbol!="XAUUSD")
   {
      PrintFormat("%s: STMR grid requires XAUUSD, got %s",GRID_TAG,_Symbol);
      return INIT_PARAMETERS_INCORRECT;
   }
   if(InpQuoteUtcOffsetMinutes<-840 || InpQuoteUtcOffsetMinutes>840 ||
      InpGridWarmupStartUtc>=InpGridEntryStartUtc || InpGridEntryStartUtc>=InpGridEntryEndUtc)
   {
      Print(GRID_TAG,": invalid grid clock/test-envelope inputs");
      return INIT_PARAMETERS_INCORRECT;
   }
   if(InpGridMagic==0 || (InpCoreEnabled && InpGridMagic==InpMagic))
   {
      Print(GRID_TAG,": grid magic must be nonzero and different from the R9 core magic");
      return INIT_PARAMETERS_INCORRECT;
   }

   const ENUM_ACCOUNT_MARGIN_MODE margin_mode=(ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(InpGridRequireHedging && margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
   {
      PrintFormat("%s: hedging account required for three-position grid parity; ACCOUNT_MARGIN_MODE=%d",
                  GRID_TAG,(int)margin_mode);
      return INIT_FAILED;
   }

   const double lot=NormalizeVolume(STMR_LOTS);
   if(MathAbs(lot-STMR_LOTS)>1e-9)
   {
      PrintFormat("%s: broker cannot represent frozen 0.01 grid lot exactly; normalized=%.8f",
                  GRID_TAG,lot);
      return INIT_FAILED;
   }

   gridTrade.SetExpertMagicNumber(InpGridMagic);
   gridTrade.SetDeviationInPoints(InpGridDeviationPoints);
   gridTrade.SetAsyncMode(false);
   gridTrade.SetMarginMode();
   if(!gridTrade.SetTypeFillingBySymbol(_Symbol))
      Print(GRID_TAG,": warning: unable to derive symbol filling mode");

   InitTf(g_h4, 4L*3600000L);
   InitTf(g_h1, 3600000L);
   InitTf(g_m15,15L*60000L);
   InitTf(g_m5, 5L*60000L);
   ArrayInitialize(g_seen,0);
   ArrayInitialize(g_sleeveAttempts,0);
   ArrayInitialize(g_sleeveOpened,0);
   OpenDecisionLog();

   PrintFormat("%s initialized gridMagic=%I64u quoteUtcOffsetMin=%d lots=%.2f maxGridPos=%d warmup=%s entryStart=%s entryEnd=%s",
               GRID_TAG,InpGridMagic,InpQuoteUtcOffsetMinutes,STMR_LOTS,STMR_MAX_POSITIONS,
               TimeToString(InpGridWarmupStartUtc,TIME_DATE|TIME_MINUTES),
               TimeToString(InpGridEntryStartUtc,TIME_DATE|TIME_MINUTES),
               TimeToString(InpGridEntryEndUtc,TIME_DATE|TIME_MINUTES));
   return INIT_SUCCEEDED;
}

void GridDeinit(const int reason)
{
   if(g_logFile!=INVALID_HANDLE)
   {
      FileFlush(g_logFile);
      FileClose(g_logFile);
      g_logFile=INVALID_HANDLE;
   }

   PrintFormat("%s summary reason=%d crossings=%I64d funded=%I64d attempts=%I64d opened=%I64d seenBlock=%I64d dirBlock=%I64d phaseBlock=%I64d capSkip=%I64d orderFail=%I64d ageCloseAttempts=%I64d",
               GRID_TAG,reason,g_crossings,g_fundedCrossings,g_entriesAttempted,g_entriesOpened,
               g_seenBlocks,g_directionBlocks,g_phaseBlocks,g_capSkips,g_orderFailures,g_ageCloseAttempts);
   for(int s=0;s<STMR_SLEEVE_COUNT;s++)
   {
      if(g_sleeveAttempts[s]>0 || g_sleeveOpened[s]>0)
         PrintFormat("%s sleeve[%d]=%s attempts=%I64d opened=%I64d",
                     GRID_TAG,s,g_sleeveName[s],g_sleeveAttempts[s],g_sleeveOpened[s]);
   }
}

void GridReconcile(const MqlTick &tick)
{
   const long utc_ms=ToUtcMs(tick.time_msc);
   if(utc_ms<WarmupStartMs()) return;

   const long bid_raw=PriceToRaw(tick.bid);
   const long ask_raw=PriceToRaw(tick.ask);
   const long mid_raw=(ask_raw+bid_raw)/2L;

   // Frozen causal order: completed-bar state -> existing grid exits -> crossing.
   UpdateAllTimeframes(utc_ms,bid_raw);
   ManageAgeExits(tick);
   ProcessCrossing(tick,utc_ms,mid_raw);
}


int OnInit()
{
   if(!InpCoreEnabled && !InpGridEnabled)
   {
      Print("GM_R9_GAMMA_STMR: both core and grid are disabled");
      return INIT_PARAMETERS_INCORRECT;
   }

   // [CORE-00] Exact R9 HybridGate initialization, conditionalized only for A/B testing.
   if(InpCoreEnabled)
   {
      if(InpLots<=0.0 || InpGapPips<=0 || InpStopLossPips<=0 || InpTrailPips<0 || InpTrailActivationPips<0 ||
         InpMaxHoldSeconds<=0 || InpMaxSameMinuteRearms<0 || InpVelocityLookbackSec<2 || InpRangeLookbackSec<2 ||
         InpVelocityLookbackSec>=MICRO_CAPACITY || InpRangeLookbackSec>=MICRO_CAPACITY || InpMinVelocityPips<0 ||
         InpMinDirectionalEff<0.0 || InpMinDirectionalEff>1.0 || InpMinRangePips<0 || InpMaxTurns<0 ||
         InpHunterPipPrice<=0.0 || InpAtrPeriod<=0 || InpMaxSpreadPoints<0)
      {
         Print(EA_TAG,": invalid inputs");
         return INIT_PARAMETERS_INCORRECT;
      }
      trade.SetExpertMagicNumber(InpMagic);
      trade.SetDeviationInPoints(InpDeviationPoints);
      trade.SetAsyncMode(false);
      trade.SetMarginMode();
      if(!trade.SetTypeFillingBySymbol(_Symbol)) Log("warning: unable to derive filling mode");
      if(InpUseRegimeGate)
      {
         g_atrHandle=iATR(_Symbol,InpAtrTimeframe,InpAtrPeriod);
         if(g_atrHandle==INVALID_HANDLE)
         {
            PrintFormat("%s: ATR handle failed lastError=%d",EA_TAG,GetLastError());
            return INIT_FAILED;
         }
      }
      PrintFormat("%s initialized gap=%d stop=%d trail=%d act=%d velLB=%d minVel=%d eff=%.2f range=%d maxHold=%d rearms=%d",
                  EA_TAG,InpGapPips,InpStopLossPips,InpTrailPips,InpTrailActivationPips,
                  InpVelocityLookbackSec,InpMinVelocityPips,InpMinDirectionalEff,
                  InpMinRangePips,InpMaxHoldSeconds,InpMaxSameMinuteRearms);
   }

   if(InpGridEnabled)
   {
      const int grid_init=GridInit();
      if(grid_init!=INIT_SUCCEEDED)
      {
         if(g_atrHandle!=INVALID_HANDLE)
         {
            IndicatorRelease(g_atrHandle);
            g_atrHandle=INVALID_HANDLE;
         }
         return grid_init;
      }
   }

   PrintFormat("GM_R9_GAMMA_STMR: integration ready core=%s grid=%s coreMagic=%I64u gridMagic=%I64u",
               (InpCoreEnabled?"ON":"OFF"),(InpGridEnabled?"ON":"OFF"),InpMagic,InpGridMagic);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(InpGridEnabled) GridDeinit(reason);
   if(g_atrHandle!=INVALID_HANDLE)
   {
      IndicatorRelease(g_atrHandle);
      g_atrHandle=INVALID_HANDLE;
   }
   Log(StringFormat("deinit reason=%d",reason));
}

void OnTick()
{
   MqlTick tick={};
   if(!SymbolInfoTick(_Symbol,tick) || tick.bid<=0.0 || tick.ask<=0.0 || tick.ask<tick.bid) return;

   // [INTEGRATION] Preserve R9 core priority on each tick; STMR is isolated by magic.
   if(InpCoreEnabled) Reconcile(tick);
   if(InpGridEnabled) GridReconcile(tick);
}
