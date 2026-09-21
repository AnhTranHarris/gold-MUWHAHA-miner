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
   if(g_atrHandle==INVALID_HANDLE || BarsCalculated(g_atrHandle)<InpAtrPeriod+2) return false;
   double b[1]; ResetLastError();
   if(CopyBuffer(g_atrHandle,0,1,1,b)!=1 || !MathIsValidNumber(b[0]) || b[0]<=0.0) return false;
   atr=b[0]; return true;
}

bool GetAtrRatio(double &ratio,double &atr)
{
   ratio=1.0; atr=0.0;
   if(!GetCompletedAtr(atr)) return false;
   const int n=MathMax(InpP4AtrBaselineBars,5);
   double hist[]; ArrayResize(hist,n);
   if(CopyBuffer(g_atrHandle,0,2,n,hist)!=n) return false;
   double mean=0.0;
   for(int i=0;i<n;i++)
   {
      if(!MathIsValidNumber(hist[i]) || hist[i]<=0.0) return false;
      mean+=hist[i];
   }
   mean/=(double)n;
   if(mean<=0.0) return false;
   ratio=atr/mean;
   return MathIsValidNumber(ratio) && ratio>0.0;
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

void PushCompletedSecond(const datetime sec,const double o,const double h,const double l,const double c,const int ticks,const int upTicks,const int downTicks)
{
   g_micro[g_microHead].second=sec;
   g_micro[g_microHead].open=o;
   g_micro[g_microHead].high=h;
   g_micro[g_microHead].low=l;
   g_micro[g_microHead].close=c;
   g_micro[g_microHead].ticks=ticks;
   g_micro[g_microHead].upTicks=upTicks;
   g_micro[g_microHead].downTicks=downTicks;
   g_microHead=(g_microHead+1)%MICRO_CAPACITY;
   if(g_microCount<MICRO_CAPACITY) g_microCount++;
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
      g_bucketReady=true;g_bucketSecond=sec;
      g_bucketOpen=tick.bid;g_bucketHigh=tick.bid;g_bucketLow=tick.bid;g_bucketClose=tick.bid;g_bucketPrevBid=tick.bid;
      g_bucketTicks=1;g_bucketUpTicks=0;g_bucketDownTicks=0;return;
   }
   if(sec!=g_bucketSecond)
   {
      PushCompletedSecond(g_bucketSecond,g_bucketOpen,g_bucketHigh,g_bucketLow,g_bucketClose,g_bucketTicks,g_bucketUpTicks,g_bucketDownTicks);
      g_bucketSecond=sec;g_bucketOpen=tick.bid;g_bucketHigh=tick.bid;g_bucketLow=tick.bid;g_bucketClose=tick.bid;g_bucketPrevBid=tick.bid;
      g_bucketTicks=1;g_bucketUpTicks=0;g_bucketDownTicks=0;return;
   }
   if(tick.bid>g_bucketPrevBid) g_bucketUpTicks++;
   else if(tick.bid<g_bucketPrevBid) g_bucketDownTicks++;
   g_bucketTicks++;
   if(tick.bid>g_bucketHigh) g_bucketHigh=tick.bid;
   if(tick.bid<g_bucketLow) g_bucketLow=tick.bid;
   g_bucketClose=tick.bid;
   g_bucketPrevBid=tick.bid;
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

bool RecentPathForSide(const int side,const int seconds,double &alignedDisp,double &eff,double &alignedFlow)
{
   alignedDisp=0.0;eff=0.0;alignedFlow=0.0;
   if(seconds<2 || g_microCount<seconds) return false;
   const int oldest=RingIndexFromNewest(seconds-1);
   double prev=g_micro[oldest].open;
   const double start=prev;
   double travel=0.0;
   long up=0,down=0;
   for(int off=seconds-1;off>=0;--off)
   {
      const int idx=RingIndexFromNewest(off);
      const double v=g_micro[idx].close;
      travel+=MathAbs(v-prev);
      prev=v;
      up+=g_micro[idx].upTicks;
      down+=g_micro[idx].downTicks;
   }
   const double rawDisp=prev-start;
   alignedDisp=rawDisp*(double)side;
   eff=MathAbs(rawDisp)/(travel+1e-9);
   const long directional=up+down;
   if(directional>0) alignedFlow=((double)(up-down)/(double)directional)*(double)side;
   return true;
}

bool CompletedBarDirection(const ENUM_TIMEFRAMES tf,const int side,double &score)
{
   score=0.0;
   MqlRates r[]; ArraySetAsSeries(r,true); ArrayResize(r,1);
   if(CopyRates(_Symbol,tf,1,1,r)!=1) return false;
   const double d=r[0].close-r[0].open;
   if(d>0.0) score=(double)side;
   else if(d<0.0) score=-(double)side;
   return true;
}

double StructuralAgreementForSide(const int side)
{
   double a=0.0,b=0.0;
   const bool ha=CompletedBarDirection(PERIOD_M1,side,a);
   const bool hb=CompletedBarDirection(PERIOD_M5,side,b);
   if(!ha && !hb) return -1.0;
   if(ha && hb) return (a+b)*0.5;
   return ha?a:b;
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

void ResetTradeRuntime()
{
   g_positionOpenedAt=0;
   g_tradeCycleMinute=0;
   g_lastEventSide=0;
   g_activeSleeve=GMM_SLEEVE_R9;
   g_tradeHarvestArmed=false;
   g_tradeRunner=false;
   g_tradeP3Flip=false;
   g_tradeMFE=0.0;
   g_tradeMAE=0.0;
   g_entryAtr=0.0;
}
