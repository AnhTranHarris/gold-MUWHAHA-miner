#property copyright "AnhTranHarris / clean-room Delta-A-alpha MT5 certification port"
#property version   "9.31"
#property strict
#property description "R9 STMR XMonth 001: Jan-Jul session/timeframe clean-room MT5 certification build."

#include <Trade/Trade.mqh>
CTrade trade;

/*
===============================================================================
 CARSON MAINTENANCE MAP — READ BEFORE EDITING
===============================================================================
 Scientific source:
   STMR_XMONTH_SUBPHASE_001
   research/delta_a_alpha/state_journal/0028_..._JANJUL_STRESS_003.json

 This EA is a BROKER CERTIFICATION PORT, not a new research optimization.
 It deliberately uses Coinexx/MT5 native Bid/Ask, fills, spread, commission,
 stop execution and slippage.  Therefore dollar P/L is not expected to be
 bit-identical to the Dukascopy DUKAS_COINEXX_LIKE_P75 Python surface.

 DO NOT silently change the frozen behavior below.  If a change is needed:
   [EDIT-01] session clock / UTC offset plumbing
   [EDIT-02] custom completed-bar EMA engine
   [EDIT-03] session-local lattice and first-touch genealogy
   [EDIT-04] sleeve classifier / funded sleeve list
   [EDIT-05] TP/SL/300-second lifecycle
   [EDIT-06] broker execution / ticket handling
   [EDIT-07] diagnostic event logger

 Any scientific change to [EDIT-02]..[EDIT-05] should be re-certified in the
 Python ordered-tick harness before becoming an MT5 research candidate.

 Frozen research behavior in this build:
   * XAUUSD only
   * fixed physical 0.01 lot
   * hedging account required (max 3 simultaneous positions)
   * no Martingale / no loss-dependent sizing
   * fixed UTC session windows
   * H4/H1/M15/M5 EMA(8/21), completed custom bars only
   * session-local lattice reset
   * semantic sleeve-local first-touch genealogy
   * one landing-cell crossing event per ordered tick
   * no timer rearm / no generic recross rearm
   * funded sleeves: 0,2,4,8,9,11 only
   * ASIA_LOWER_TAKEOVER: 23:00-00:00 UTC
   * LONDON_M5_TAKEOVER: 11:00-12:00 UTC
   * OVERLAP_LOWER_TAKEOVER: 15:00-16:00 UTC
   * LATE_LOWER_TAKEOVER: 21:00-22:00 UTC
   * fixed TP/SL per sleeve, hard age exit at 300 seconds

 Python clean-room comparator (Jan-Jul 2026):
   net +829.71, PF 1.29674, trades 2675, expected payoff +0.31017
   monthly: +641.58 / +43.95 / +4.55 / -34.51 / -19.89 / +213.13 / -19.10

 Authoritative January floor remains STMR_SLEEVE_PHASE_001 +877.78 and is NOT
 replaced by this clean-room MT5 port.
===============================================================================
*/

// -------------------------------
// User-adjustable CERTIFICATION plumbing only.  Research geometry is compiled.
// -------------------------------
input group "Certification clock / test envelope"
input int      InpQuoteUtcOffsetMinutes = 0; // server quote time = UTC + this offset
input datetime InpWarmupStartUtc        = D'2026.01.01 00:00:00';
input datetime InpEntryStartUtc         = D'2026.01.05 00:00:00';
input datetime InpEntryEndUtc           = D'2026.08.01 00:00:00'; // August stays sealed/no entries

input group "Execution plumbing"
input ulong InpMagic               = 5593001;
input int   InpDeviationPoints     = 20;
input bool  InpRequireHedging      = true;
input bool  InpVerbose             = true;

input group "Parity diagnostics"
input bool InpDecisionLoggerEnabled = true;
input bool InpFlushDecisionLogOften = false;

string EA_TAG = "GM_R9_STMR_XM01";

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

// -------------------------------
// Utility / broker plumbing.
// -------------------------------
void Log(const string text)
{
   if(InpVerbose) Print(EA_TAG, ": ", text);
}

bool ResultAccepted()
{
   const uint c=trade.ResultRetcode();
   return (c==TRADE_RETCODE_DONE || c==TRADE_RETCODE_PLACED ||
           c==TRADE_RETCODE_DONE_PARTIAL || c==TRADE_RETCODE_NO_CHANGES);
}

void LogTradeFailure(const string action)
{
   PrintFormat("%s: %s failed; retcode=%u (%s), lastError=%d",
               EA_TAG,action,trade.ResultRetcode(),trade.ResultRetcodeDescription(),GetLastError());
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

long WarmupStartMs(){ return (long)InpWarmupStartUtc*1000L; }
long EntryStartMs(){ return (long)InpEntryStartUtc*1000L; }
long EntryEndMs(){ return (long)InpEntryEndUtc*1000L; }

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
               EA_TAG,s.tf_ms,s.bucket,bucket);
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
      PrintFormat("%s: session reset -> %s anchorRaw=%I64d",EA_TAG,SessionName(new_session),mid_raw);
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
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
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
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
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
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
      const long opened=(long)PositionGetInteger(POSITION_TIME_MSC);
      if(opened>0 && tick.time_msc-opened>=STMR_MAX_HOLD_MS)
      {
         g_ageCloseAttempts++;
         ResetLastError();
         if(!trade.PositionClose(ticket) || !ResultAccepted()) LogTradeFailure("300s age close");
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
   if(!InpDecisionLoggerEnabled) return;
   const string mode=(MQLInfoInteger(MQL_TESTER)?"TESTER":"LIVE");
   const string name="GoldMuwahaha_R9_STMR_XM01_"+mode+"_"+SafeStamp(TimeCurrent())+".csv";
   ResetLastError();
   g_logFile=FileOpen(name,FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI,',');
   if(g_logFile==INVALID_HANDLE)
   {
      PrintFormat("%s: decision log open failed name=%s lastError=%d",EA_TAG,name,GetLastError());
      return;
   }
   FileWrite(g_logFile,
      "event_id","server_time_msc","utc_time_msc","session","h4","h1","m15","m5",
      "sleeve","sleeve_name","direction","expected","cell","key","anchor_raw","mid_raw",
      "bid","ask","seen_before","phase_ok","open_positions","action");
   FileFlush(g_logFile);
   PrintFormat("%s: decision log -> Common\Files\%s",EA_TAG,name);
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
   if(InpFlushDecisionLogOften || (g_logRows%250)==0) FileFlush(g_logFile);
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
                  EA_TAG,g_sleeveName[sleeve],sl,tp);
      return false;
   }

   const string comment=StringFormat("STMR E%I64d S%d",g_crossingId,sleeve);
   ResetLastError();
   bool sent=false;
   if(direction>0) sent=trade.Buy(STMR_LOTS,_Symbol,0.0,sl,tp,comment);
   else sent=trade.Sell(STMR_LOTS,_Symbol,0.0,sl,tp,comment);

   if(!sent || !ResultAccepted())
   {
      g_orderFailures++;
      LogTradeFailure(direction>0?"BUY":"SELL");
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
         if(!trade.PositionModify(ticket,exact_sl,exact_tp) || !ResultAccepted())
         {
            LogTradeFailure("fill-relative SL/TP modify");
            // Fail closed: an unfaithful lifecycle is worse than a skipped trade.
            ResetLastError();
            if(!trade.PositionClose(ticket) || !ResultAccepted()) LogTradeFailure("cleanup after SL/TP modify failure");
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

int OnInit()
{
   if(_Symbol!="XAUUSD")
   {
      PrintFormat("%s: certification build requires XAUUSD, got %s",EA_TAG,_Symbol);
      return INIT_PARAMETERS_INCORRECT;
   }
   if(InpQuoteUtcOffsetMinutes<-840 || InpQuoteUtcOffsetMinutes>840 ||
      InpWarmupStartUtc>=InpEntryStartUtc || InpEntryStartUtc>=InpEntryEndUtc)
   {
      Print(EA_TAG,": invalid certification clock inputs");
      return INIT_PARAMETERS_INCORRECT;
   }
   if(InpMagic==0)
   {
      Print(EA_TAG,": magic number must be nonzero");
      return INIT_PARAMETERS_INCORRECT;
   }

   const ENUM_ACCOUNT_MARGIN_MODE margin_mode=(ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(InpRequireHedging && margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
   {
      PrintFormat("%s: hedging account required for 3-position parity; ACCOUNT_MARGIN_MODE=%d",EA_TAG,(int)margin_mode);
      return INIT_FAILED;
   }

   const double lot=NormalizeVolume(STMR_LOTS);
   if(MathAbs(lot-STMR_LOTS)>1e-9)
   {
      PrintFormat("%s: broker cannot represent frozen 0.01 lot exactly; normalized=%.8f",EA_TAG,lot);
      return INIT_FAILED;
   }

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPoints);
   trade.SetAsyncMode(false);
   trade.SetMarginMode();
   if(!trade.SetTypeFillingBySymbol(_Symbol)) Log("warning: unable to derive symbol filling mode");

   InitTf(g_h4, 4L*3600000L);
   InitTf(g_h1, 3600000L);
   InitTf(g_m15,15L*60000L);
   InitTf(g_m5, 5L*60000L);
   ArrayInitialize(g_seen,0);
   ArrayInitialize(g_sleeveAttempts,0);
   ArrayInitialize(g_sleeveOpened,0);
   OpenDecisionLog();

   PrintFormat("%s initialized version=9.31 magic=%I64u quoteUtcOffsetMin=%d lots=%.2f maxPos=%d warmup=%s entryStart=%s entryEnd=%s",
               EA_TAG,InpMagic,InpQuoteUtcOffsetMinutes,STMR_LOTS,STMR_MAX_POSITIONS,
               TimeToString(InpWarmupStartUtc,TIME_DATE|TIME_MINUTES),
               TimeToString(InpEntryStartUtc,TIME_DATE|TIME_MINUTES),
               TimeToString(InpEntryEndUtc,TIME_DATE|TIME_MINUTES));
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_logFile!=INVALID_HANDLE)
   {
      FileFlush(g_logFile);
      FileClose(g_logFile);
      g_logFile=INVALID_HANDLE;
   }

   PrintFormat("%s summary reason=%d crossings=%I64d funded=%I64d attempts=%I64d opened=%I64d seenBlock=%I64d dirBlock=%I64d phaseBlock=%I64d capSkip=%I64d orderFail=%I64d ageCloseAttempts=%I64d",
               EA_TAG,reason,g_crossings,g_fundedCrossings,g_entriesAttempted,g_entriesOpened,
               g_seenBlocks,g_directionBlocks,g_phaseBlocks,g_capSkips,g_orderFailures,g_ageCloseAttempts);
   for(int s=0;s<STMR_SLEEVE_COUNT;s++)
   {
      if(g_sleeveAttempts[s]>0 || g_sleeveOpened[s]>0)
         PrintFormat("%s sleeve[%d]=%s attempts=%I64d opened=%I64d",EA_TAG,s,g_sleeveName[s],g_sleeveAttempts[s],g_sleeveOpened[s]);
   }
}

void OnTick()
{
   MqlTick tick={};
   if(!SymbolInfoTick(_Symbol,tick) || tick.bid<=0.0 || tick.ask<=0.0 || tick.ask<tick.bid) return;

   const long utc_ms=ToUtcMs(tick.time_msc);
   if(utc_ms<WarmupStartMs()) return;

   const long bid_raw=PriceToRaw(tick.bid);
   const long ask_raw=PriceToRaw(tick.ask);
   const long mid_raw=(ask_raw+bid_raw)/2L;

   // Causal order mirrors Python: completed-bar state first, then exits, then
   // session/lattice crossing decision on the current ordered tick.
   UpdateAllTimeframes(utc_ms,bid_raw);
   ManageAgeExits(tick);
   ProcessCrossing(tick,utc_ms,mid_raw);
}
