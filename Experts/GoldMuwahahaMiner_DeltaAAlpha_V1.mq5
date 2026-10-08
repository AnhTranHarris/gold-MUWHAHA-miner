#property copyright "AnhTranHarris / Delta-A-alpha Vertical Grid System V1"
#property version   "1.03"
#property strict
#property description "Delta-A-alpha V1: tick-rooted vertical grid spine with session lattice and first-touch event genealogy."

#include <Trade/Trade.mqh>
CTrade g_trade;

/*
===============================================================================
 DELTA-A-ALPHA — VERTICAL GRID SYSTEM V1
 MT5 IMPLEMENTATION 001 — ARCHITECTURE SHELL
===============================================================================
 PERMANENT ORDER
 [V1-00] ordered tick / clock normalization
 [V1-10] session-specific grid geometry
 [V1-20] completed H4/H1/M15/M5 structure
 [V1-30] London/overlap/NY hourly harvesting + separate Asia geometry
 [V1-40] Watchdog / regime renewal
 [V1-50] trend-within-trend native routing
 [V1-60] wrong-direction recovery
 [V1-70] portfolio heat / capital governor
 [V1-80] deterministic diagnostics

This first engineering unit establishes interfaces, clock/state ownership,
orchestration order and diagnostics. It intentionally opens no trades.
Profit-bearing mechanics are ported layer-by-layer in later units and must
match the frozen Python research before execution is enabled.
===============================================================================
*/

enum DAA_V1_SESSION
{
   DAA_SESSION_ASIA=0,
   DAA_SESSION_LONDON_OPEN=1,
   DAA_SESSION_LONDON=2,
   DAA_SESSION_OVERLAP=3,
   DAA_SESSION_NEW_YORK=4,
   DAA_SESSION_LATE_NY=5,
   DAA_SESSION_ROLLOVER=6
};

enum DAA_V1_TREND
{
   DAA_TREND_DOWN=-1,
   DAA_TREND_FLAT=0,
   DAA_TREND_UP=1
};

enum DAA_V1_RISK_STATE
{
   DAA_RISK_OBSERVE_ONLY=0,
   DAA_RISK_OPEN_NEW=1,
   DAA_RISK_REDUCE_ONLY=2
};

enum DAA_V1_CLOCK_MODE
{
   DAA_CLOCK_COINEXX_AUTO=0,
   DAA_CLOCK_FIXED_OFFSET=1,
   DAA_CLOCK_RAW_TESTER=2
};

enum DAA_V1_CYCLE_REASON
{
   DAA_CYCLE_INIT=0,
   DAA_CYCLE_SESSION_HANDOFF=1,
   DAA_CYCLE_GEOMETRY_CHANGE=2,
   DAA_CYCLE_MAX_AGE=3
};

input group "V1 identity / safety"
input double InpLots=0.01;
input ulong  InpMagic=761001;
input bool   InpExecutionEnabled=false; // remains false until parity units pass
input int    InpGlobalMaxPositions=620;

input group "V1 historical clock"
input DAA_V1_CLOCK_MODE InpClockMode=DAA_CLOCK_COINEXX_AUTO;
input int InpFixedQuoteUtcOffsetMinutes=120;

input group "V1 completed MTF"
input int InpFastEmaPeriod=8;
input int InpSlowEmaPeriod=21;

input group "V1 session grid / genealogy"
input int InpMaxCycleAgeMinutes=720;
input int InpMaxTouchKeys=8192;
input int InpMaxEventRecords=8192;

input group "V1 Watchdog / renewal"
input int    InpWatchdogGoodStreak=4;
input int    InpWatchdogGoodHoldSeconds=60;
input int    InpWatchdogMaxCells=4096;
input double InpWatchdogRenewalGap=1.19;
input double InpWatchdogLastSubphaseGap=1.10;
input int    InpWatchdogMaxRenewalLayer=30;

input group "V1 diagnostics"
input bool InpDiagnostics=true;
input bool InpVerbose=true;
input string InpDiagnosticPrefix="DAA_V1_VERTICAL_GRID";

struct DAAV1Context
{
   long utc_ms;
   double bid;
   double ask;
   DAA_V1_SESSION session;
   double session_gap;
   bool cycle_restarted;
   int cycle_restart_reason;
   long cycle_generation;
   bool event_created;
   bool event_duplicate;
   ulong event_id;
   int grid_from_cell;
   int grid_to_cell;
   int grid_landing_cell;
   int crossing_direction;
   double grid_boundary;
   bool route_valid;
   string route_id;
   int route_direction;
   double route_tp;
   double route_sl;
   int route_horizon_seconds;
   int route_hour_utc;
   int route_subphase_10m;
   bool watchdog_candidate;
   int watchdog_cell_index;
   bool watchdog_scout;
   bool watchdog_parent_admitted;
   bool watchdog_gate;
   int watchdog_streak;
   double watchdog_renewal_gap;
   int watchdog_max_layer;
   int h4;
   int h1;
   int m15;
   int m5;
   bool mtf_ready;
   bool high_volume_session;
   bool asia_geometry;
   bool watchdog_ready;
   bool native_route_ready;
   bool recovery_ready;
   DAA_V1_RISK_STATE risk_state;
   int open_positions;
};

struct DAAV1GridCycle
{
   bool initialized;
   bool active;
   long generation;
   long start_utc_ms;
   long last_utc_ms;
   DAA_V1_SESSION session;
   double anchor_mid;
   double gap;
   int last_cell;
};

struct DAAV1TouchKey
{
   int cell;
   int direction;
};

struct DAAV1GridEventRecord
{
   ulong event_id;
   long cycle_generation;
   long birth_utc_ms;
   DAA_V1_SESSION session;
   int from_cell;
   int to_cell;
   int landing_cell;
   int direction;
   double boundary;
   int h4;
   int h1;
   int m15;
   int m5;
   string route_id;
   int route_direction;
   double route_tp;
   double route_sl;
   int route_horizon_seconds;
   int route_hour_utc;
   int route_subphase_10m;
   bool watchdog_candidate;
   int watchdog_cell_index;
   bool watchdog_scout;
   bool watchdog_parent_admitted;
   bool watchdog_gate;
   int watchdog_streak;
   double watchdog_renewal_gap;
   int watchdog_max_layer;
};

struct DAAV1WatchdogCell
{
   long day_key;
   int ny_hour;
   int ny_bin10;
   int h4;
   int h1;
   int m15;
   int m5;
   int direction;
   int realized_good_streak;
   bool gate;
   int unlocks;
   int relocks;
   int parents_seen;
   int parents_admitted;
};

DAAV1GridCycle g_grid_cycle={};
DAAV1TouchKey g_touch_keys[];
DAAV1GridEventRecord g_event_records[];
DAAV1WatchdogCell g_watchdog_cells[];
ulong g_event_sequence=0;
long g_watchdog_day_key=-1;

int g_h4_fast=INVALID_HANDLE, g_h4_slow=INVALID_HANDLE;
int g_h1_fast=INVALID_HANDLE, g_h1_slow=INVALID_HANDLE;
int g_m15_fast=INVALID_HANDLE, g_m15_slow=INVALID_HANDLE;
int g_m5_fast=INVALID_HANDLE, g_m5_slow=INVALID_HANDLE;
int g_diag=INVALID_HANDLE;
int g_last_clock_offset=99999;

void V1Log(const string s)
{
   if(InpVerbose) Print("DAA_V1: ",s);
}

int DaysInMonth(const int year,const int month)
{
   if(month==2){ const bool leap=((year%400)==0 || ((year%4)==0 && (year%100)!=0)); return leap?29:28; }
   if(month==4 || month==6 || month==9 || month==11) return 30;
   return 31;
}

int DayOfWeekUtc(const int year,const int month,const int day)
{
   MqlDateTime v={}; v.year=year; v.mon=month; v.day=day; v.hour=12;
   const datetime s=StructToTime(v); MqlDateTime r={};
   if(!TimeToStruct(s,r)) return -1;
   return r.day_of_week;
}

int NthSunday(const int year,const int month,const int nth)
{
   const int fd=DayOfWeekUtc(year,month,1);
   if(fd<0) return 0;
   const int first=1+((7-fd)%7);
   return first+(nth-1)*7;
}

datetime MakeUtc(const int year,const int month,const int day,const int hour,const int minute=0)
{
   MqlDateTime v={};
   v.year=year; v.mon=month; v.day=day; v.hour=hour; v.min=minute;
   return StructToTime(v);
}

// [V1-00] Coinexx historical server -> UTC mapping used by the validated clock-fix lineage.
int CoinexxOffsetMinutes(const long server_ms)
{
   const datetime server_time=(datetime)(server_ms/1000L);
   MqlDateTime d={};
   if(!TimeToStruct(server_time,d)) return 120;
   const datetime dst_start_server=MakeUtc(d.year,3,NthSunday(d.year,3,2),9,0);
   const datetime dst_end_server=MakeUtc(d.year,11,NthSunday(d.year,11,1),9,0);
   return (server_time>=dst_start_server && server_time<dst_end_server)?180:120;
}

long TickToUtcMs(const long server_ms)
{
   int offset=0;
   if(InpClockMode==DAA_CLOCK_COINEXX_AUTO) offset=CoinexxOffsetMinutes(server_ms);
   else if(InpClockMode==DAA_CLOCK_FIXED_OFFSET) offset=InpFixedQuoteUtcOffsetMinutes;
   else offset=0;

   if(offset!=g_last_clock_offset)
   {
      V1Log(StringFormat("clock offset=%d min mode=%d",offset,(int)InpClockMode));
      g_last_clock_offset=offset;
   }
   return server_ms-(long)offset*60000L;
}

int UtcMinuteOfDay(const long utc_ms)
{
   const datetime s=(datetime)(utc_ms/1000L);
   MqlDateTime d={};
   if(!TimeToStruct(s,d)) return -1;
   return d.hour*60+d.min;
}

DAA_V1_SESSION SessionFromUtc(const long utc_ms)
{
   const int m=UtcMinuteOfDay(utc_ms);
   if(m<0) return DAA_SESSION_ROLLOVER;
   if(m>=23*60 || m<7*60) return DAA_SESSION_ASIA;
   if(m<9*60) return DAA_SESSION_LONDON_OPEN;
   if(m<13*60+30) return DAA_SESSION_LONDON;
   if(m<16*60) return DAA_SESSION_OVERLAP;
   if(m<20*60) return DAA_SESSION_NEW_YORK;
   if(m<22*60) return DAA_SESSION_LATE_NY;
   return DAA_SESSION_ROLLOVER;
}

string SessionName(const DAA_V1_SESSION s)
{
   if(s==DAA_SESSION_ASIA) return "ASIA";
   if(s==DAA_SESSION_LONDON_OPEN) return "LONDON_OPEN";
   if(s==DAA_SESSION_LONDON) return "LONDON";
   if(s==DAA_SESSION_OVERLAP) return "OVERLAP";
   if(s==DAA_SESSION_NEW_YORK) return "NEW_YORK";
   if(s==DAA_SESSION_LATE_NY) return "LATE_NY";
   return "ROLLOVER";
}

// [V1-10] Session geometry is a primary layer, not an optional filter.
void ApplySessionGeometry(DAAV1Context &c)
{
   c.asia_geometry=false;
   c.high_volume_session=false;
   if(c.session==DAA_SESSION_ASIA)
   {
      c.session_gap=0.75;
      c.asia_geometry=true;
   }
   else if(c.session==DAA_SESSION_LONDON)
   {
      c.session_gap=1.00;
      c.high_volume_session=true;
   }
   else if(c.session==DAA_SESSION_OVERLAP)
   {
      c.session_gap=0.75;
      c.high_volume_session=true;
   }
   else if(c.session==DAA_SESSION_NEW_YORK)
   {
      c.session_gap=1.50;
      c.high_volume_session=true;
   }
   else if(c.session==DAA_SESSION_LATE_NY)
   {
      c.session_gap=0.50;
   }
   else
      c.session_gap=0.0; // London-open and rollover observe-only in the base geometry.
}


void ResetTouchMemory()
{
   ArrayResize(g_touch_keys,0);
}

void ResetGenealogyMemory()
{
   ArrayResize(g_event_records,0);
}

void ResetEventContext(DAAV1Context &c)
{
   c.cycle_restarted=false;
   c.cycle_restart_reason=-1;
   c.cycle_generation=g_grid_cycle.generation;
   c.event_created=false;
   c.event_duplicate=false;
   c.event_id=0;
   c.grid_from_cell=0;
   c.grid_to_cell=0;
   c.grid_landing_cell=0;
   c.crossing_direction=0;
   c.grid_boundary=0.0;
   c.route_valid=false;
   c.route_id="NONE";
   c.route_direction=0;
   c.route_tp=0.0;
   c.route_sl=0.0;
   c.route_horizon_seconds=0;
   c.route_hour_utc=-1;
   c.route_subphase_10m=-1;
   c.watchdog_ready=false;
   c.watchdog_candidate=false;
   c.watchdog_cell_index=-1;
   c.watchdog_scout=false;
   c.watchdog_parent_admitted=false;
   c.watchdog_gate=false;
   c.watchdog_streak=0;
   c.watchdog_renewal_gap=0.0;
   c.watchdog_max_layer=InpWatchdogMaxRenewalLayer;
}

void RestartGridCycle(DAAV1Context &c,const DAA_V1_CYCLE_REASON reason)
{
   g_grid_cycle.initialized=true;
   g_grid_cycle.active=(c.session_gap>0.0);
   g_grid_cycle.generation++;
   g_grid_cycle.start_utc_ms=c.utc_ms;
   g_grid_cycle.last_utc_ms=c.utc_ms;
   g_grid_cycle.session=c.session;
   g_grid_cycle.anchor_mid=(c.bid+c.ask)*0.5;
   g_grid_cycle.gap=c.session_gap;
   g_grid_cycle.last_cell=0;
   ResetTouchMemory();
   ResetGenealogyMemory();

   c.cycle_restarted=true;
   c.cycle_restart_reason=(int)reason;
   c.cycle_generation=g_grid_cycle.generation;

   if(InpVerbose)
      PrintFormat("DAA_V1: cycle restart gen=%I64d reason=%d session=%s anchor=%.5f gap=%.5f active=%d",
                  g_grid_cycle.generation,(int)reason,SessionName(c.session),
                  g_grid_cycle.anchor_mid,g_grid_cycle.gap,(int)g_grid_cycle.active);
}

// [V1-11] Finite session-local ownership.
// A session handoff, geometry change, or maximum cycle age creates a new cycle
// and clears first-touch ownership. London-open/rollover remain observe-only.
void UpdateSessionGridCycle(DAAV1Context &c)
{
   ResetEventContext(c);

   bool restart=false;
   DAA_V1_CYCLE_REASON reason=DAA_CYCLE_INIT;

   if(!g_grid_cycle.initialized)
   {
      restart=true;
      reason=DAA_CYCLE_INIT;
   }
   else if(g_grid_cycle.session!=c.session)
   {
      restart=true;
      reason=DAA_CYCLE_SESSION_HANDOFF;
   }
   else if(MathAbs(g_grid_cycle.gap-c.session_gap)>1e-12)
   {
      restart=true;
      reason=DAA_CYCLE_GEOMETRY_CHANGE;
   }
   else if(InpMaxCycleAgeMinutes>0)
   {
      const long max_age=(long)InpMaxCycleAgeMinutes*60000L;
      if(c.utc_ms-g_grid_cycle.start_utc_ms>=max_age)
      {
         restart=true;
         reason=DAA_CYCLE_MAX_AGE;
      }
   }

   if(restart) RestartGridCycle(c,reason);
   else
   {
      g_grid_cycle.last_utc_ms=c.utc_ms;
      c.cycle_generation=g_grid_cycle.generation;
   }
}

int GridCellIndex(const double mid)
{
   if(!g_grid_cycle.active || g_grid_cycle.gap<=0.0) return 0;
   const double rel=(mid-g_grid_cycle.anchor_mid)/g_grid_cycle.gap;
   return (int)MathFloor(rel);
}

bool TouchAlreadyOwned(const int cell,const int direction)
{
   const int n=ArraySize(g_touch_keys);
   for(int i=0;i<n;i++)
      if(g_touch_keys[i].cell==cell && g_touch_keys[i].direction==direction)
         return true;
   return false;
}

bool RegisterTouchOwnership(const int cell,const int direction)
{
   if(TouchAlreadyOwned(cell,direction)) return false;
   const int n=ArraySize(g_touch_keys);
   if(n>=InpMaxTouchKeys)
   {
      V1Log("touch-memory capacity reached; new event ownership suppressed until cycle restart");
      return false;
   }
   if(ArrayResize(g_touch_keys,n+1)!=n+1) return false;
   g_touch_keys[n].cell=cell;
   g_touch_keys[n].direction=direction;
   return true;
}

bool RecordGenealogyEvent(const DAAV1Context &c)
{
   const int n=ArraySize(g_event_records);
   if(n>=InpMaxEventRecords)
   {
      V1Log("event-genealogy capacity reached; event remains diagnostic-only until cycle restart");
      return false;
   }
   if(ArrayResize(g_event_records,n+1)!=n+1) return false;

   g_event_records[n].event_id=c.event_id;
   g_event_records[n].cycle_generation=c.cycle_generation;
   g_event_records[n].birth_utc_ms=c.utc_ms;
   g_event_records[n].session=c.session;
   g_event_records[n].from_cell=c.grid_from_cell;
   g_event_records[n].to_cell=c.grid_to_cell;
   g_event_records[n].landing_cell=c.grid_landing_cell;
   g_event_records[n].direction=c.crossing_direction;
   g_event_records[n].boundary=c.grid_boundary;
   g_event_records[n].h4=c.h4;
   g_event_records[n].h1=c.h1;
   g_event_records[n].m15=c.m15;
   g_event_records[n].m5=c.m5;
   g_event_records[n].route_id="NONE";
   g_event_records[n].route_direction=0;
   g_event_records[n].route_tp=0.0;
   g_event_records[n].route_sl=0.0;
   g_event_records[n].route_horizon_seconds=0;
   g_event_records[n].route_hour_utc=-1;
   g_event_records[n].route_subphase_10m=-1;
   g_event_records[n].watchdog_candidate=false;
   g_event_records[n].watchdog_cell_index=-1;
   g_event_records[n].watchdog_scout=false;
   g_event_records[n].watchdog_parent_admitted=false;
   g_event_records[n].watchdog_gate=false;
   g_event_records[n].watchdog_streak=0;
   g_event_records[n].watchdog_renewal_gap=0.0;
   g_event_records[n].watchdog_max_layer=InpWatchdogMaxRenewalLayer;
   return true;
}

int ActiveCycleEventCount()
{
   return ArraySize(g_event_records);
}

// [V1-12] One session-grid event maximum per market tick.
// If a tick jumps several cells, the event represents the FIRST crossed boundary;
// deeper skipped cells are not manufactured retroactively.
void ManufactureFirstTouchEvent(DAAV1Context &c)
{
   if(!g_grid_cycle.initialized || !g_grid_cycle.active || g_grid_cycle.gap<=0.0) return;

   const double mid=(c.bid+c.ask)*0.5;
   const int landing=GridCellIndex(mid);
   const int prior=g_grid_cycle.last_cell;
   if(landing==prior) return;

   const int direction=(landing>prior)?1:-1;
   const int target=prior+direction;
   const double boundary=(direction>0)
      ? g_grid_cycle.anchor_mid+(double)target*g_grid_cycle.gap
      : g_grid_cycle.anchor_mid+(double)prior*g_grid_cycle.gap;

   // The observed market state advances to the landing cell even if the first
   // boundary was already owned. This prevents replaying skipped boundaries.
   g_grid_cycle.last_cell=landing;

   c.grid_from_cell=prior;
   c.grid_to_cell=target;
   c.grid_landing_cell=landing;
   c.crossing_direction=direction;
   c.grid_boundary=boundary;

   if(TouchAlreadyOwned(target,direction))
   {
      c.event_duplicate=true;
      return;
   }
   if(!RegisterTouchOwnership(target,direction)) return;

   g_event_sequence++;
   c.event_created=true;
   c.event_id=g_event_sequence;

   // Snapshot the original completed MTF/session context at birth. Higher layers
   // consume this record rather than recomputing historical ownership later.
   RecordGenealogyEvent(c);
}

bool ReadCompletedEmaTrend(const int fast_handle,const int slow_handle,int &trend)
{
   trend=DAA_TREND_FLAT;
   if(fast_handle==INVALID_HANDLE || slow_handle==INVALID_HANDLE) return false;
   if(BarsCalculated(fast_handle)<InpSlowEmaPeriod+2 || BarsCalculated(slow_handle)<InpSlowEmaPeriod+2) return false;
   double f[1],s[1];
   if(CopyBuffer(fast_handle,0,1,1,f)!=1) return false;
   if(CopyBuffer(slow_handle,0,1,1,s)!=1) return false;
   if(!MathIsValidNumber(f[0]) || !MathIsValidNumber(s[0])) return false;
   const double eps=SymbolInfoDouble(_Symbol,SYMBOL_POINT)*0.1;
   if(f[0]>s[0]+eps) trend=DAA_TREND_UP;
   else if(f[0]<s[0]-eps) trend=DAA_TREND_DOWN;
   else trend=DAA_TREND_FLAT;
   return true;
}

// [V1-20] Completed H4/H1/M15/M5 only. No unfinished-bar state.
void RefreshCompletedMTF(DAAV1Context &c)
{
   int h4=0,h1=0,m15=0,m5=0;
   const bool ok=
      ReadCompletedEmaTrend(g_h4_fast,g_h4_slow,h4) &&
      ReadCompletedEmaTrend(g_h1_fast,g_h1_slow,h1) &&
      ReadCompletedEmaTrend(g_m15_fast,g_m15_slow,m15) &&
      ReadCompletedEmaTrend(g_m5_fast,g_m5_slow,m5);
   c.h4=h4; c.h1=h1; c.m15=m15; c.m5=m5; c.mtf_ready=ok;
}

int UtcHour(const long utc_ms)
{
   const int m=UtcMinuteOfDay(utc_ms);
   return (m<0)?-1:(m/60);
}

int UtcSubphase10m(const long utc_ms)
{
   const int m=UtcMinuteOfDay(utc_ms);
   return (m<0)?-1:((m%60)/10);
}

void SetRoute(DAAV1Context &c,const string route_id,const int direction,
              const double tp,const double sl,const int horizon_seconds)
{
   c.route_valid=true;
   c.route_id=route_id;
   c.route_direction=direction;
   c.route_tp=tp;
   c.route_sl=sl;
   c.route_horizon_seconds=horizon_seconds;
   c.route_hour_utc=UtcHour(c.utc_ms);
   c.route_subphase_10m=UtcSubphase10m(c.utc_ms);
}

void AttachRouteToLatestEvent(const DAAV1Context &c)
{
   if(!c.event_created || !c.route_valid) return;
   const int n=ArraySize(g_event_records);
   if(n<=0) return;
   if(g_event_records[n-1].event_id!=c.event_id) return;
   g_event_records[n-1].route_id=c.route_id;
   g_event_records[n-1].route_direction=c.route_direction;
   g_event_records[n-1].route_tp=c.route_tp;
   g_event_records[n-1].route_sl=c.route_sl;
   g_event_records[n-1].route_horizon_seconds=c.route_horizon_seconds;
   g_event_records[n-1].route_hour_utc=c.route_hour_utc;
   g_event_records[n-1].route_subphase_10m=c.route_subphase_10m;
}

// [V1-30] Session/MTF route proposal layer.
// This consumes ONLY the event birth tick and completed H4/H1/M15/M5 state.
// It creates an observe-only proposal; no physical order authority exists yet.
void ApplyHourlyHarvest(DAAV1Context &c)
{
   if(!c.event_created || !c.mtf_ready) return;
   if(c.session==DAA_SESSION_LONDON_OPEN || c.session==DAA_SESSION_ROLLOVER) return;

   const int d=c.crossing_direction;
   if(d==0) return;
   const bool macro=(c.h4!=0 && c.h4==c.h1);
   const int hour=UtcHour(c.utc_ms);

   if(c.session==DAA_SESSION_ASIA)
   {
      // Separate Asia geometry family. Historical BUILD-02 evidence retained a
      // targeted 23:00-00:00 gate for the lower-takeover sleeve.
      if(macro && c.m15==c.m5 && c.m15==-c.h1 && d==c.m5 && hour==23)
         SetRoute(c,"ASIA_LOWER_TAKEOVER",d,4.00,1.00,300);
      else if(macro && c.m15==-c.h1 && c.m5==c.h1 && d==c.m5)
         SetRoute(c,"ASIA_M15_DIVERGE_M5_RECLAIM",d,4.00,1.50,300);
   }
   else if(c.session==DAA_SESSION_LONDON)
   {
      // London high-volume harvesting remains hourly-aware. The 11 UTC gate
      // is the durable BUILD-02 takeover specialization; reclaim remains broad.
      if(macro && c.m15==c.h1 && c.m5==-c.h1 && d==c.m5 && hour==11)
         SetRoute(c,"LONDON_M5_TAKEOVER",d,4.00,0.75,300);
      else if(macro && c.m15==-c.h1 && c.m5==c.h1 && d==c.m5)
         SetRoute(c,"LONDON_M5_RECLAIM",d,3.00,0.75,300);
   }
   else if(c.session==DAA_SESSION_OVERLAP)
   {
      if(macro && c.m15==c.m5 && c.m15==-c.h1 && d==c.m5)
         SetRoute(c,"OVERLAP_LOWER_TAKEOVER",d,4.00,1.50,300);
      else if(macro && c.m15==c.m5 && c.m15==c.h1 && d==-c.m5)
         SetRoute(c,"OVERLAP_ALIGNED_COUNTERCROSS",d,3.00,0.75,300);
   }
   else if(c.session==DAA_SESSION_NEW_YORK)
   {
      if(c.h4!=0 && c.h1!=0 && c.h4!=c.h1 && c.m15!=0 && c.m5==-c.m15 && d==c.m5)
         SetRoute(c,"NY_LOWER_TRANSFER",d,4.00,1.50,300);
      else if(c.h4!=0 && c.h1!=0 && c.h4!=c.h1 && c.m15==c.m5 && c.m15!=0 && d==-c.m5)
         SetRoute(c,"NY_LOWER_COUNTERCROSS",d,2.50,1.50,300);
   }
   else if(c.session==DAA_SESSION_LATE_NY)
   {
      if(c.h4==c.h1 && c.h1==c.m15 && c.m15==c.m5 && c.h4!=0 && d==c.m5)
         SetRoute(c,"LATE_ALIGNED_MOMENTUM",d,4.00,1.50,300);
      else if(c.h4!=0 && c.h1!=0 && c.h4!=c.h1 && c.m15!=0 && c.m5==-c.m15 && d==c.m5)
         SetRoute(c,"LATE_MACRO_SPLIT_TRANSFER",d,4.00,1.50,300);
      else if(macro && c.m15==c.h1 && c.m5==-c.h1 && d==-c.m5)
         SetRoute(c,"LATE_M5_REJECTION",d,4.00,1.50,300);
      else if(macro && c.m15==c.m5 && c.m15==-c.h1 && d==c.m5)
         SetRoute(c,"LATE_LOWER_TAKEOVER",d,2.50,1.25,300);
   }

   AttachRouteToLatestEvent(c);
}

bool IsNewYorkDstUtcMs(const long utc_ms)
{
   const datetime utc=(datetime)(utc_ms/1000L);
   MqlDateTime d={};
   if(!TimeToStruct(utc,d)) return false;
   const datetime start=MakeUtc(d.year,3,NthSunday(d.year,3,2),7,0);
   const datetime end=MakeUtc(d.year,11,NthSunday(d.year,11,1),6,0);
   return utc>=start && utc<end;
}

int NewYorkLocalMinuteOfDay(const long utc_ms)
{
   const int offset=IsNewYorkDstUtcMs(utc_ms)?-240:-300;
   long mins=(utc_ms/60000L)+(long)offset;
   int out=(int)(mins%1440L);
   if(out<0) out+=1440;
   return out;
}

void ResetWatchdogDaily(const long day_key)
{
   ArrayResize(g_watchdog_cells,0);
   g_watchdog_day_key=day_key;
}

int FindWatchdogCell(const DAAV1Context &c,const int ny_hour,const int ny_bin10,const bool create)
{
   const long day_key=c.utc_ms/86400000L;
   if(g_watchdog_day_key!=day_key) ResetWatchdogDaily(day_key);

   const int n=ArraySize(g_watchdog_cells);
   for(int i=0;i<n;i++)
   {
      if(g_watchdog_cells[i].day_key==day_key &&
         g_watchdog_cells[i].ny_hour==ny_hour &&
         g_watchdog_cells[i].ny_bin10==ny_bin10 &&
         g_watchdog_cells[i].h4==c.h4 &&
         g_watchdog_cells[i].h1==c.h1 &&
         g_watchdog_cells[i].m15==c.m15 &&
         g_watchdog_cells[i].m5==c.m5 &&
         g_watchdog_cells[i].direction==c.crossing_direction)
         return i;
   }

   if(!create || n>=InpWatchdogMaxCells) return -1;
   if(ArrayResize(g_watchdog_cells,n+1)!=n+1) return -1;

   g_watchdog_cells[n].day_key=day_key;
   g_watchdog_cells[n].ny_hour=ny_hour;
   g_watchdog_cells[n].ny_bin10=ny_bin10;
   g_watchdog_cells[n].h4=c.h4;
   g_watchdog_cells[n].h1=c.h1;
   g_watchdog_cells[n].m15=c.m15;
   g_watchdog_cells[n].m5=c.m5;
   g_watchdog_cells[n].direction=c.crossing_direction;
   g_watchdog_cells[n].realized_good_streak=0;
   g_watchdog_cells[n].gate=false;
   g_watchdog_cells[n].unlocks=0;
   g_watchdog_cells[n].relocks=0;
   g_watchdog_cells[n].parents_seen=0;
   g_watchdog_cells[n].parents_admitted=0;
   return n;
}

double WatchdogRenewalGapForBin(const int ny_bin10)
{
   return (ny_bin10==5)?InpWatchdogLastSubphaseGap:InpWatchdogRenewalGap;
}

// Later lifecycle units call this only after a renewal child has actually exited.
bool RecordWatchdogRealizedOutcome(const int cell_index,const double pnl,const int hold_seconds)
{
   if(cell_index<0 || cell_index>=ArraySize(g_watchdog_cells)) return false;
   DAAV1WatchdogCell old=g_watchdog_cells[cell_index];

   const bool good=(pnl>0.0 && hold_seconds<=InpWatchdogGoodHoldSeconds);
   if(good) g_watchdog_cells[cell_index].realized_good_streak++;
   else g_watchdog_cells[cell_index].realized_good_streak=0;

   g_watchdog_cells[cell_index].gate=
      (g_watchdog_cells[cell_index].realized_good_streak>=InpWatchdogGoodStreak);

   if(g_watchdog_cells[cell_index].gate && !old.gate)
      g_watchdog_cells[cell_index].unlocks++;
   if(old.gate && !g_watchdog_cells[cell_index].gate)
      g_watchdog_cells[cell_index].relocks++;
   return true;
}

void AttachWatchdogToLatestEvent(const DAAV1Context &c)
{
   if(!c.event_created || !c.watchdog_candidate) return;
   const int n=ArraySize(g_event_records);
   if(n<=0 || g_event_records[n-1].event_id!=c.event_id) return;

   g_event_records[n-1].watchdog_candidate=c.watchdog_candidate;
   g_event_records[n-1].watchdog_cell_index=c.watchdog_cell_index;
   g_event_records[n-1].watchdog_scout=c.watchdog_scout;
   g_event_records[n-1].watchdog_parent_admitted=c.watchdog_parent_admitted;
   g_event_records[n-1].watchdog_gate=c.watchdog_gate;
   g_event_records[n-1].watchdog_streak=c.watchdog_streak;
   g_event_records[n-1].watchdog_renewal_gap=c.watchdog_renewal_gap;
   g_event_records[n-1].watchdog_max_layer=c.watchdog_max_layer;
}

// [V1-40] Frozen Watchdog-119 campaign admission semantics.
// The first parent in a causal day/hour/10m/MTF/direction cell scouts.
// Later parents are admitted only after four already-realized profitable
// renewal outcomes with <=60 s holds. Any losing/slow realized outcome relocks.
void ApplyWatchdogRegime(DAAV1Context &c)
{
   if(!c.event_created || !c.mtf_ready) return;

   const int ny_min=NewYorkLocalMinuteOfDay(c.utc_ms);
   const int ny_hour=ny_min/60;
   const int ny_bin10=(ny_min%60)/10;
   const bool macro=(c.h4!=0 && c.h4==c.h1 && c.crossing_direction==c.h4);

   // Watchdog-119 parent discovery window: New York local 12:00-13:59.
   if(!macro || ny_hour<12 || ny_hour>13) return;

   const int idx=FindWatchdogCell(c,ny_hour,ny_bin10,true);
   if(idx<0) return;

   c.watchdog_ready=true;
   c.watchdog_candidate=true;
   c.watchdog_cell_index=idx;
   c.watchdog_renewal_gap=WatchdogRenewalGapForBin(ny_bin10);
   c.watchdog_max_layer=InpWatchdogMaxRenewalLayer;

   const bool first=(g_watchdog_cells[idx].parents_seen==0);
   g_watchdog_cells[idx].parents_seen++;

   c.watchdog_scout=first;
   c.watchdog_gate=g_watchdog_cells[idx].gate;
   c.watchdog_streak=g_watchdog_cells[idx].realized_good_streak;
   c.watchdog_parent_admitted=(first || g_watchdog_cells[idx].gate);
   if(c.watchdog_parent_admitted) g_watchdog_cells[idx].parents_admitted++;

   AttachWatchdogToLatestEvent(c);
}

// [V1-50] Trend-within-trend routing interface.
void ApplyTrendWithinTrend(DAAV1Context &c)
{
   c.native_route_ready=false;
   if(!c.mtf_ready) return;
   const bool macro=(c.h4!=0 && c.h4==c.h1);
   const bool lower=(c.m15!=0 && c.m5!=0);
   c.native_route_ready=(macro && lower);
}

// [V1-60] Wrong-direction recovery interface.
// It remains disabled until failed-ignition/reclaim parity logic is ported.
void ApplyWrongDirectionRecovery(DAAV1Context &c)
{
   c.recovery_ready=false;
}

int CountV1Positions()
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

// [V1-70] Account-level physical risk authority.
void ApplyCapitalGovernor(DAAV1Context &c)
{
   c.open_positions=CountV1Positions();
   if(!InpExecutionEnabled) c.risk_state=DAA_RISK_OBSERVE_ONLY;
   else if(c.open_positions>=InpGlobalMaxPositions) c.risk_state=DAA_RISK_REDUCE_ONLY;
   else c.risk_state=DAA_RISK_OPEN_NEW;
}

void WriteDiagnostic(const DAAV1Context &c)
{
   if(!InpDiagnostics || g_diag==INVALID_HANDLE) return;
   FileWrite(g_diag,
      (long)c.utc_ms,
      DoubleToString(c.bid,_Digits),
      DoubleToString(c.ask,_Digits),
      SessionName(c.session),
      DoubleToString(c.session_gap,2),
      c.cycle_restarted?1:0,
      c.cycle_restart_reason,
      c.cycle_generation,
      ActiveCycleEventCount(),
      c.event_created?1:0,
      c.event_duplicate?1:0,
      c.event_id,
      c.grid_from_cell,
      c.grid_to_cell,
      c.grid_landing_cell,
      c.crossing_direction,
      DoubleToString(c.grid_boundary,_Digits),
      c.route_valid?1:0,
      c.route_id,
      c.route_direction,
      DoubleToString(c.route_tp,2),
      DoubleToString(c.route_sl,2),
      c.route_horizon_seconds,
      c.route_hour_utc,
      c.route_subphase_10m,
      c.watchdog_candidate?1:0,
      c.watchdog_cell_index,
      c.watchdog_scout?1:0,
      c.watchdog_parent_admitted?1:0,
      c.watchdog_gate?1:0,
      c.watchdog_streak,
      DoubleToString(c.watchdog_renewal_gap,2),
      c.watchdog_max_layer,
      c.h4,c.h1,c.m15,c.m5,
      c.mtf_ready?1:0,
      c.high_volume_session?1:0,
      c.asia_geometry?1:0,
      c.watchdog_ready?1:0,
      c.native_route_ready?1:0,
      c.recovery_ready?1:0,
      (int)c.risk_state,
      c.open_positions
   );
}

// The source-order of these calls is a static QA contract.
void OrchestrateV1(const MqlTick &tick)
{
   DAAV1Context c={};
   c.utc_ms=TickToUtcMs(tick.time_msc);         // V1-00
   c.bid=tick.bid; c.ask=tick.ask;
   c.session=SessionFromUtc(c.utc_ms);
   ApplySessionGeometry(c);                     // V1-10
   UpdateSessionGridCycle(c);                   // V1-11
   RefreshCompletedMTF(c);                      // V1-20
   ManufactureFirstTouchEvent(c);               // V1-12 birth snapshot has completed MTF state
   ApplyHourlyHarvest(c);                       // V1-30
   ApplyWatchdogRegime(c);                      // V1-40
   ApplyTrendWithinTrend(c);                    // V1-50
   ApplyWrongDirectionRecovery(c);              // V1-60
   ApplyCapitalGovernor(c);                     // V1-70
   WriteDiagnostic(c);                          // V1-80

   // IMPLEMENTATION-001 intentionally has no order-send path.
   // InpExecutionEnabled alone cannot create risk until later parity-certified units add proposals.
}

bool InitMtfHandles()
{
   g_h4_fast=iMA(_Symbol,PERIOD_H4,InpFastEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_h4_slow=iMA(_Symbol,PERIOD_H4,InpSlowEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_h1_fast=iMA(_Symbol,PERIOD_H1,InpFastEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_h1_slow=iMA(_Symbol,PERIOD_H1,InpSlowEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_m15_fast=iMA(_Symbol,PERIOD_M15,InpFastEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_m15_slow=iMA(_Symbol,PERIOD_M15,InpSlowEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_m5_fast=iMA(_Symbol,PERIOD_M5,InpFastEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_m5_slow=iMA(_Symbol,PERIOD_M5,InpSlowEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   return g_h4_fast!=INVALID_HANDLE && g_h4_slow!=INVALID_HANDLE &&
          g_h1_fast!=INVALID_HANDLE && g_h1_slow!=INVALID_HANDLE &&
          g_m15_fast!=INVALID_HANDLE && g_m15_slow!=INVALID_HANDLE &&
          g_m5_fast!=INVALID_HANDLE && g_m5_slow!=INVALID_HANDLE;
}

void ReleaseOne(int &h)
{
   if(h!=INVALID_HANDLE){ IndicatorRelease(h); h=INVALID_HANDLE; }
}

int OnInit()
{
   if(_Symbol!="XAUUSD") V1Log("warning: V1 is designed for XAUUSD");
   if(MathAbs(InpLots-0.01)>1e-12)
   {
      Print("DAA_V1: V1 requires fixed 0.01 lot");
      return INIT_PARAMETERS_INCORRECT;
   }
   if(InpGlobalMaxPositions<1 || InpFastEmaPeriod<1 || InpSlowEmaPeriod<=InpFastEmaPeriod ||
      InpMaxCycleAgeMinutes<1 || InpMaxTouchKeys<16 || InpMaxEventRecords<16 ||
      InpWatchdogGoodStreak<1 || InpWatchdogGoodHoldSeconds<1 || InpWatchdogMaxCells<16 ||
      InpWatchdogRenewalGap<=0.0 || InpWatchdogLastSubphaseGap<=0.0 || InpWatchdogMaxRenewalLayer<1)
      return INIT_PARAMETERS_INCORRECT;
   if(InpClockMode==DAA_CLOCK_FIXED_OFFSET &&
      (InpFixedQuoteUtcOffsetMinutes<-840 || InpFixedQuoteUtcOffsetMinutes>840))
      return INIT_PARAMETERS_INCORRECT;

   if(!InitMtfHandles())
   {
      Print("DAA_V1: failed to create completed-MTF EMA handles");
      return INIT_FAILED;
   }

   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetAsyncMode(false);

   if(InpDiagnostics)
   {
      const string fn=InpDiagnosticPrefix+"_"+_Symbol+".csv";
      g_diag=FileOpen(fn,FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
      if(g_diag!=INVALID_HANDLE)
      {
         FileWrite(g_diag,"utc_ms","bid","ask","session","session_gap",
                   "cycle_restarted","cycle_restart_reason","cycle_generation","active_cycle_events",
                   "event_created","event_duplicate","event_id",
                   "grid_from_cell","grid_to_cell","grid_landing_cell","crossing_direction","grid_boundary",
                   "route_valid","route_id","route_direction","route_tp","route_sl","route_horizon_seconds",
                   "route_hour_utc","route_subphase_10m",
                   "watchdog_candidate","watchdog_cell_index","watchdog_scout","watchdog_parent_admitted",
                   "watchdog_gate","watchdog_streak","watchdog_renewal_gap","watchdog_max_layer",
                   "h4","h1","m15","m5","mtf_ready","high_volume","asia_geometry","watchdog_ready","native_ready",
                   "recovery_ready","risk_state","open_positions");
      }
   }

   ResetTouchMemory();
   ResetGenealogyMemory();
   g_grid_cycle.initialized=false;
   g_grid_cycle.generation=0;
   g_event_sequence=0;
   ArrayResize(g_watchdog_cells,0);
   g_watchdog_day_key=-1;

   V1Log("MT5 IMPLEMENTATION 004 initialized: Watchdog campaign admission + renewal geometry / observe-only");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   ReleaseOne(g_h4_fast); ReleaseOne(g_h4_slow);
   ReleaseOne(g_h1_fast); ReleaseOne(g_h1_slow);
   ReleaseOne(g_m15_fast); ReleaseOne(g_m15_slow);
   ReleaseOne(g_m5_fast); ReleaseOne(g_m5_slow);
   if(g_diag!=INVALID_HANDLE){ FileClose(g_diag); g_diag=INVALID_HANDLE; }
   ResetTouchMemory();
   ResetGenealogyMemory();
   ArrayResize(g_watchdog_cells,0);
   V1Log(StringFormat("deinit reason=%d",reason));
}

void OnTick()
{
   MqlTick tick={};
   if(!SymbolInfoTick(_Symbol,tick)) return;
   if(tick.bid<=0.0 || tick.ask<=0.0 || tick.ask<tick.bid) return;
   OrchestrateV1(tick);
}
