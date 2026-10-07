/*
===============================================================================
 R9 GAMMA-01 STMR GRID — COINEXX HISTORICAL CLOCK FIX
===============================================================================
 ROOT CAUSE FIXED HERE
 ---------------------
 The original GAMMA-01 STMR port treated MT5 Strategy Tester tick timestamps as
 UTC because InpQuoteUtcOffsetMinutes defaulted to 0.  MetaTrader Strategy Tester
 timestamps are the historical quote/server-time domain, not recoverable GMT.
 Coinexx uses a New-York-close style server clock (UTC+2 standard / UTC+3 DST).

 That error shifted every fixed-UTC STMR session and, critically, shifted the H4
 completed-bar bucket alignment.  A Python fault-injection replay using the same
 +2/+3 mistaken clock reproduced the MT5 trade-count pattern almost exactly.

 This wrapper deliberately preserves the exact already-audited GAMMA-01 source
 and overrides ONLY the grid time-normalization path.  R9 core behavior remains
 unchanged.

 EDIT MAP
 --------
 [CLOCKFIX-01] historical Coinexx server->UTC conversion
 [CLOCKFIX-02] corrected GridReconcile
 [CLOCKFIX-03] integration entrypoints

 DO NOT edit the included GAMMA-01 source from this file.  Future scientific
 session/timeframe changes still belong in the Python ordered-tick lineage first.
===============================================================================
*/

// Rename the original program entrypoints/time path while textually including
// the exact GAMMA-01 implementation.  This avoids copying or silently drifting
// the 1,200+ line audited source.
#define OnInit          Gamma01_LegacyOnInit
#define OnDeinit        Gamma01_LegacyOnDeinit
#define OnTick          Gamma01_LegacyOnTick
#define GridReconcile   Gamma01_LegacyGridReconcile
#define ToUtcMs         Gamma01_LegacyToUtcMs
#include "GoldMuwahahaMiner_R9_GAMMA_01_STMRGrid.mq5"
#undef ToUtcMs
#undef GridReconcile
#undef OnTick
#undef OnDeinit
#undef OnInit

// [CLOCKFIX-01] Grid-only clock mode.  The R9 core still uses the legacy
// InpQuoteUtcOffsetMinutes input exactly as before.
enum ENUM_STMR_GRID_CLOCK_MODE
{
   STMR_GRID_CLOCK_COINEXX_AUTO = 0, // UTC+2 standard, UTC+3 during US DST
   STMR_GRID_CLOCK_FIXED_OFFSET = 1, // manual diagnostic mode
   STMR_GRID_CLOCK_RAW_TESTER   = 2  // forensic reproduction of invalid v1
};

input group "STMR grid clock normalization — CLOCKFIX"
input ENUM_STMR_GRID_CLOCK_MODE InpGridClockMode = STMR_GRID_CLOCK_COINEXX_AUTO;
input int InpGridFixedQuoteUtcOffsetMinutes = 120;

// Coinexx historical convention used for this 2026 certification campaign:
// standard UTC+2; US/New-York DST UTC+3.  The switch is represented in SERVER
// calendar time.  The market is closed during the Sunday transition interval,
// so 09:00 server is an unambiguous boundary for historical trading ticks.
int GridCoinexxOffsetMinutes(const long server_ms)
{
   const datetime server_time=(datetime)(server_ms/1000L);
   MqlDateTime d={};
   if(!TimeToStruct(server_time,d))
      return 120;

   const int start_day=NthSunday(d.year,3,2); // second Sunday in March
   const int end_day=NthSunday(d.year,11,1);  // first Sunday in November
   const datetime dst_start_server=MakeUtc(d.year,3,start_day,9,0);
   const datetime dst_end_server=MakeUtc(d.year,11,end_day,9,0);

   return (server_time>=dst_start_server && server_time<dst_end_server) ? 180 : 120;
}

long GridToUtcMs(const long server_ms)
{
   int offset_min=0;
   if(InpGridClockMode==STMR_GRID_CLOCK_COINEXX_AUTO)
      offset_min=GridCoinexxOffsetMinutes(server_ms);
   else if(InpGridClockMode==STMR_GRID_CLOCK_FIXED_OFFSET)
      offset_min=InpGridFixedQuoteUtcOffsetMinutes;
   else
      offset_min=0;

   return server_ms-(long)offset_min*60000L;
}

string GridClockModeName()
{
   if(InpGridClockMode==STMR_GRID_CLOCK_COINEXX_AUTO) return "COINEXX_AUTO_UTC+2/+3";
   if(InpGridClockMode==STMR_GRID_CLOCK_FIXED_OFFSET) return "FIXED_OFFSET";
   return "RAW_TESTER_TIME_INVALID_V1_REPRO";
}

// [CLOCKFIX-02] Exact legacy grid reconcile order with one intentional change:
// server tick milliseconds are normalized to UTC before timeframe/session work.
void GridReconcile(const MqlTick &tick)
{
   const long utc_ms=GridToUtcMs(tick.time_msc);
   if(utc_ms<WarmupStartMs()) return;

   const long bid_raw=PriceToRaw(tick.bid);
   const long ask_raw=PriceToRaw(tick.ask);
   const long mid_raw=(ask_raw+bid_raw)/2L;

   UpdateAllTimeframes(utc_ms,bid_raw);
   ManageAgeExits(tick);
   ProcessCrossing(tick,utc_ms,mid_raw);
}

// [CLOCKFIX-03] Preserve legacy initialization and deinitialization; override
// only tick orchestration so the corrected grid reconcile is used.
int OnInit()
{
   const int rc=Gamma01_LegacyOnInit();
   if(rc!=INIT_SUCCEEDED)
      return rc;

   if(InpGridEnabled)
   {
      if(InpGridClockMode==STMR_GRID_CLOCK_FIXED_OFFSET &&
         (InpGridFixedQuoteUtcOffsetMinutes<-840 || InpGridFixedQuoteUtcOffsetMinutes>840))
      {
         Print("GM_R9_GAMMA_STMR: invalid fixed grid UTC offset");
         return INIT_PARAMETERS_INCORRECT;
      }

      PrintFormat("GM_R9_GAMMA_STMR CLOCKFIX active mode=%s fixedOffsetMin=%d; coreQuoteOffsetMin=%d",
                  GridClockModeName(),InpGridFixedQuoteUtcOffsetMinutes,InpQuoteUtcOffsetMinutes);
   }
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   Gamma01_LegacyOnDeinit(reason);
}

void OnTick()
{
   MqlTick tick={};
   if(!SymbolInfoTick(_Symbol,tick) || tick.bid<=0.0 || tick.ask<=0.0 || tick.ask<tick.bid)
      return;

   // Exact GAMMA ordering: R9 core first, corrected STMR grid second.
   if(InpCoreEnabled) Reconcile(tick);
   if(InpGridEnabled) GridReconcile(tick);
}
