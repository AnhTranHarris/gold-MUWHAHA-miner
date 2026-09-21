#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "1.95"
#property strict
#property description "Gold MUWHAHA R9 MOD P1-P5: R9 HybridGate chassis with causal P1 harvester, P2 runner, P3 failed-ignition reversal, P4 rotation, and P5 structural trend."

#include <Trade/Trade.mqh>
CTrade trade;

enum ENUM_GMM_SESSION
{
   GMM_SESSION_OFF = 0,
   GMM_SESSION_LONDON = 1,
   GMM_SESSION_OVERLAP = 2,
   GMM_SESSION_NEWYORK = 3
};

enum ENUM_GMM_SLEEVE
{
   GMM_SLEEVE_R9 = 0,
   GMM_SLEEVE_P1 = 1,
   GMM_SLEEVE_P3_FLIP = 3,
   GMM_SLEEVE_P4 = 4,
   GMM_SLEEVE_P5_H1 = 51,
   GMM_SLEEVE_P5_H4 = 54
};

input group "R9 baseline execution geometry"
input double InpLots                   = 0.01;
input int    InpGapPips                = 30;
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

input group "P1 Pullback/Reacceleration Harvester"
input bool   InpUseP1Harvester             = true;
input double InpP1ContinueMaxAligned       = -0.255;
input double InpP1FadeMinAligned           = 0.275;
input double InpP1MinCompletedS1Range      = 0.285;
input int    InpP1MinFadeTicks             = 5;
input double InpP1EmergencyStopPrice       = 5.00;
input double InpP1HarvestActivationPrice   = 0.01;
input double InpP1HarvestTrailPrice        = 0.01;
input int    InpP1MaxHoldSeconds           = 30;

input group "P2 Expansion/Persistence Runner"
input bool   InpUseP2Runner                 = true;
input int    InpP2LookbackSeconds           = 10;
input double InpP2MinDirectionalFlow        = 0.30;
input double InpP2MinPathEfficiency         = 0.70;
input double InpP2MinAlignedDispPrice       = 0.01;
input double InpP2MinStructuralScore        = 0.00;
input double InpP2RunnerTrailAtr            = 1.00;
input int    InpP2RunnerMaxHoldSeconds      = 120;

input group "P3 Failed-Ignition Reversal"
input bool   InpUseP3FailedIgnition         = true;
input bool   InpP3FlipAfterExit             = true;
input int    InpP3EvaluateAfterSeconds      = 15;
input double InpP3MaxMFEToFail              = 0.01;
input double InpP3MinMAEAtr                 = 2.00;
input int    InpP3AdverseLookbackSeconds    = 5;
input double InpP3MinAdverseEfficiency      = 0.70;
input double InpP3MinAdverseDispAtr         = 0.15;
input double InpP3MaxAlignedTickFlow        = -0.30;

input group "P4 Low-Volatility Rotation"
input bool   InpUseP4Rotation               = true;
input int    InpP4AtrBaselineBars           = 20;
input double InpP4MaxAtrRatio               = 1.05;
input double InpP4MaxEfficiency             = 0.78;

input group "P5 H1/H4 Structural Trend"
input bool   InpUseP5Structural             = true;
input int    InpP5H1BreakoutBars            = 5;
input int    InpP5H4BreakoutBars            = 6;
input int    InpP5AtrBaselineBars           = 20;
input double InpP5H1MaxVolRatio             = 1.20;
input double InpP5H4MaxVolRatio             = 2.00;
input double InpP5StopAtr                   = 1.50;
input double InpP5ActivationAtr             = 0.25;
input double InpP5TrailAtr                  = 1.00;
input int    InpP5H1MaxHoldSeconds          = 43200;
input int    InpP5H4MaxHoldSeconds          = 86400;

input group "Price normalization"
input double InpHunterPipPrice       = 0.01;
input bool   InpRespectBrokerStops   = true;

input group "Execution and QC"
input int    InpDeviationPoints      = 20;
input bool   InpRequireXAUUSD        = true;
input bool   InpVerbose              = true;

string EA_TAG = "GM_R9MOD_P1P5";

#define MICRO_CAPACITY 4096
struct MicroBar
{
   datetime second;
   double open;
   double high;
   double low;
   double close;
   int ticks;
   int upTicks;
   int downTicks;
};
MicroBar g_micro[MICRO_CAPACITY];
int g_microHead=0;
int g_microCount=0;

bool g_bucketReady=false;
datetime g_bucketSecond=0;
double g_bucketOpen=0.0,g_bucketHigh=0.0,g_bucketLow=0.0,g_bucketClose=0.0,g_bucketPrevBid=0.0;
int g_bucketTicks=0,g_bucketUpTicks=0,g_bucketDownTicks=0;

datetime g_cycleMinute=0;
double g_cycleBuy=0.0,g_cycleSell=0.0;
int g_pendingMode=0;
int g_rearms=0;

bool g_hadPosition=false;
ENUM_POSITION_TYPE g_lastPositionType=POSITION_TYPE_BUY;
datetime g_positionOpenedAt=0;
datetime g_tradeCycleMinute=0;
int g_lastEventSide=0;
ENUM_GMM_SLEEVE g_activeSleeve=GMM_SLEEVE_R9;
bool g_tradeHarvestArmed=false;
bool g_tradeRunner=false;
bool g_tradeP3Flip=false;
double g_tradeMFE=0.0;
double g_tradeMAE=0.0;
double g_entryAtr=0.0;

int g_atrHandle=INVALID_HANDLE;
int g_p5H1AtrHandle=INVALID_HANDLE;
int g_p5H4AtrHandle=INVALID_HANDLE;
datetime g_lastGateLogBar=0;
datetime g_lastP5H1Bar=0;
datetime g_lastP5H4Bar=0;

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
