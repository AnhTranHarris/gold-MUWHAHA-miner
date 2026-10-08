#property copyright "AnhTranHarris / Delta-A-alpha Vertical Grid System V1"
#property version   "1.00"
#property strict
#property description "Delta-A-alpha V1 architecture shell: tick-rooted vertical grid spine with deterministic layer diagnostics."

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

// [V1-30] Interface boundary for hourly high-volume harvesting.
// Profit-bearing cadence/grid genealogy is ported in the next implementation units.
void ApplyHourlyHarvest(DAAV1Context &c)
{
   if(!c.mtf_ready) return;
   if(c.high_volume_session)
   {
      // Observe-only shell: session/hour/subphase and completed MTF state are now available.
   }
   if(c.asia_geometry)
   {
      // Asia remains a separate geometry family by contract.
   }
}

// [V1-40] Watchdog/regime renewal interface.
void ApplyWatchdogRegime(DAAV1Context &c)
{
   c.watchdog_ready=c.mtf_ready && c.session==DAA_SESSION_NEW_YORK;
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
   RefreshCompletedMTF(c);                      // V1-20
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
   if(InpGlobalMaxPositions<1 || InpFastEmaPeriod<1 || InpSlowEmaPeriod<=InpFastEmaPeriod)
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
         FileWrite(g_diag,"utc_ms","bid","ask","session","session_gap","h4","h1","m15","m5",
                   "mtf_ready","high_volume","asia_geometry","watchdog_ready","native_ready",
                   "recovery_ready","risk_state","open_positions");
      }
   }

   V1Log("MT5 IMPLEMENTATION 001 initialized: architecture shell / observe-only");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   ReleaseOne(g_h4_fast); ReleaseOne(g_h4_slow);
   ReleaseOne(g_h1_fast); ReleaseOne(g_h1_slow);
   ReleaseOne(g_m15_fast); ReleaseOne(g_m15_slow);
   ReleaseOne(g_m5_fast); ReleaseOne(g_m5_slow);
   if(g_diag!=INVALID_HANDLE){ FileClose(g_diag); g_diag=INVALID_HANDLE; }
   V1Log(StringFormat("deinit reason=%d",reason));
}

void OnTick()
{
   MqlTick tick={};
   if(!SymbolInfoTick(_Symbol,tick)) return;
   if(tick.bid<=0.0 || tick.ask<=0.0 || tick.ask<tick.bid) return;
   OrchestrateV1(tick);
}
