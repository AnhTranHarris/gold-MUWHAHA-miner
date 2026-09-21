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

void InitializeTradeRuntime(const ENUM_GMM_SLEEVE sleeve,const int eventSide,const bool isP3Flip,const MqlTick &tick)
{
   g_activeSleeve=sleeve;
   g_positionOpenedAt=tick.time;
   g_tradeCycleMinute=g_cycleMinute;
   g_lastEventSide=eventSide;
   g_tradeHarvestArmed=false;
   g_tradeRunner=false;
   g_tradeP3Flip=isP3Flip;
   g_tradeMFE=0.0;
   g_tradeMAE=0.0;
   double atr=0.0;
   g_entryAtr=(GetCompletedAtr(atr)?atr:0.0);
}

bool OpenR9Trade(const int side,const MqlTick &tick)
{
   const double volume=NormalizeVolume(InpLots);
   const double brokerMin=InpRespectBrokerStops?BrokerStopsDistance()+TickSize():0.0;
   const double sd=MathMax(HunterDistance(InpStopLossPips),brokerMin);
   double sl=0.0;bool sent=false;
   ResetLastError();
   if(side>0){ sl=NormalizePrice(tick.bid-sd);sent=trade.Buy(volume,_Symbol,0.0,sl,0.0,EA_TAG+" R9"); }
   else{ sl=NormalizePrice(tick.ask+sd);sent=trade.Sell(volume,_Symbol,0.0,sl,0.0,EA_TAG+" R9"); }
   if(!sent || !ResultAccepted()){ LogTradeFailure(side>0?"R9 BUY":"R9 SELL");return false; }
   InitializeTradeRuntime(GMM_SLEEVE_R9,side,false,tick);
   g_pendingMode=0;
   return true;
}

bool OpenHftTrade(const int tradeSide,const int eventSide,const ENUM_GMM_SLEEVE sleeve,const bool isP3Flip,const MqlTick &tick,const string label)
{
   const double volume=NormalizeVolume(InpLots);
   const double brokerMin=InpRespectBrokerStops?BrokerStopsDistance()+TickSize():0.0;
   const double sd=MathMax(InpP1EmergencyStopPrice,brokerMin);
   double sl=0.0;bool sent=false;
   ResetLastError();
   if(tradeSide>0){ sl=NormalizePrice(tick.bid-sd);sent=trade.Buy(volume,_Symbol,0.0,sl,0.0,EA_TAG+" "+label); }
   else{ sl=NormalizePrice(tick.ask+sd);sent=trade.Sell(volume,_Symbol,0.0,sl,0.0,EA_TAG+" "+label); }
   if(!sent || !ResultAccepted()){ LogTradeFailure(label);return false; }
   InitializeTradeRuntime(sleeve,eventSide,isP3Flip,tick);
   g_lastPositionType=(tradeSide>0?POSITION_TYPE_BUY:POSITION_TYPE_SELL);
   g_pendingMode=0;
   if(InpVerbose) PrintFormat("%s: %s ENTRY tradeSide=%d eventSide=%d",EA_TAG,label,tradeSide,eventSide);
   return true;
}

bool OpenP5Trade(const int side,const ENUM_GMM_SLEEVE sleeve,const double atr,const MqlTick &tick)
{
   const double volume=NormalizeVolume(InpLots);
   const double brokerMin=InpRespectBrokerStops?BrokerStopsDistance()+TickSize():0.0;
   const double sd=MathMax(atr*InpP5StopAtr,brokerMin);
   const string label=(sleeve==GMM_SLEEVE_P5_H4?"P5_H4":"P5_H1");
   double sl=0.0;bool sent=false;
   ResetLastError();
   if(side>0){ sl=NormalizePrice(tick.bid-sd);sent=trade.Buy(volume,_Symbol,0.0,sl,0.0,EA_TAG+" "+label); }
   else{ sl=NormalizePrice(tick.ask+sd);sent=trade.Sell(volume,_Symbol,0.0,sl,0.0,EA_TAG+" "+label); }
   if(!sent || !ResultAccepted()){ LogTradeFailure(label);return false; }
   InitializeTradeRuntime(sleeve,0,false,tick);
   g_entryAtr=atr;
   g_lastPositionType=(side>0?POSITION_TYPE_BUY:POSITION_TYPE_SELL);
   g_pendingMode=0;
   if(InpVerbose) PrintFormat("%s: %s ENTRY side=%d ATR=%.3f",EA_TAG,label,side,atr);
   return true;
}

void UpdateExcursion(const MqlTick &tick,const ENUM_POSITION_TYPE type,const double openPrice)
{
   const double favorable=(type==POSITION_TYPE_BUY?(tick.bid-openPrice):(openPrice-tick.ask));
   const double adverse=(type==POSITION_TYPE_BUY?(openPrice-tick.bid):(tick.ask-openPrice));
   if(favorable>g_tradeMFE) g_tradeMFE=favorable;
   if(adverse>g_tradeMAE) g_tradeMAE=adverse;
}

int RouteP1Event(const int eventSide,double &alignedRet1,double &range1,int &ticks1,string &label)
{
   alignedRet1=0.0;range1=0.0;ticks1=0;label="ABSTAIN";
   if(g_microCount<1) return 0;
   const int idx=RingIndexFromNewest(0);
   const MicroBar bar=g_micro[idx];
   alignedRet1=(bar.close-bar.open)*(double)eventSide;
   range1=bar.high-bar.low;
   ticks1=bar.ticks;
   if(alignedRet1<=InpP1ContinueMaxAligned && range1+1e-12>=InpP1MinCompletedS1Range)
   {
      label="P1_CONT";
      return eventSide;
   }
   if(alignedRet1>=InpP1FadeMinAligned && ticks1>=InpP1MinFadeTicks)
   {
      label="P1_FADE";
      return -eventSide;
   }
   return 0;
}

bool P4Qualifies(const double eff10,double &atrRatio)
{
   atrRatio=1.0;
   if(!InpUseP4Rotation) return false;
   double atr=0.0;
   if(!GetAtrRatio(atrRatio,atr)) return false;
   return (atrRatio<=InpP4MaxAtrRatio+1e-12 && eff10<=InpP4MaxEfficiency+1e-12);
}

bool ShouldPromoteP2Runner(const int tradeSide,double &flow,double &eff,double &disp,double &structural)
{
   flow=0.0;eff=0.0;disp=0.0;structural=-1.0;
   if(!InpUseP2Runner || g_activeSleeve!=GMM_SLEEVE_P1) return false;
   if(!RecentPathForSide(tradeSide,InpP2LookbackSeconds,disp,eff,flow)) return false;
   structural=StructuralAgreementForSide(tradeSide);
   if(structural<=InpP2MinStructuralScore) return false;
   if(flow+1e-12<InpP2MinDirectionalFlow) return false;
   if(eff+1e-12<InpP2MinPathEfficiency) return false;
   if(disp+1e-12<InpP2MinAlignedDispPrice) return false;
   return true;
}

bool P3FailedIgnition(const int tradeSide,const datetime now,double &atr,double &disp,double &eff,double &flow)
{
   atr=0.0;disp=0.0;eff=0.0;flow=0.0;
   if(!InpUseP3FailedIgnition || g_tradeP3Flip || g_tradeHarvestArmed || g_tradeRunner || g_positionOpenedAt<=0) return false;
   const int age=(int)(now-g_positionOpenedAt);
   if(age<InpP3EvaluateAfterSeconds || g_tradeMFE+1e-12>=InpP3MaxMFEToFail) return false;
   if(!GetCompletedAtr(atr) || atr<=0.0) return false;
   if(g_tradeMAE+1e-12<InpP3MinMAEAtr*atr) return false;
   if(!RecentPathForSide(tradeSide,InpP3AdverseLookbackSeconds,disp,eff,flow)) return false;
   if(disp>-InpP3MinAdverseDispAtr*atr+1e-12) return false;
   if(eff+1e-12<InpP3MinAdverseEfficiency) return false;
   if(flow>InpP3MaxAlignedTickFlow+1e-12) return false;
   return true;
}

int ModifyTrailingStop(const ulong ticket,const ENUM_POSITION_TYPE type,const MqlTick &tick,const double trailDistance,const double currentSL)
{
   const double broker=InpRespectBrokerStops?BrokerStopsDistance():0.0;
   const double ts=TickSize();
   double cand=0.0;
   if(type==POSITION_TYPE_BUY)
   {
      cand=NormalizePrice(tick.bid-trailDistance);
      cand=MathMin(cand,NormalizePrice(tick.bid-broker-ts));
      if(cand<=0.0 || cand<=currentSL+ts*0.5) return 0;
   }
   else
   {
      cand=NormalizePrice(tick.ask+trailDistance);
      cand=MathMax(cand,NormalizePrice(tick.ask+broker+ts));
      if(cand<=0.0 || (currentSL>0.0 && cand>=currentSL-ts*0.5)) return 0;
   }
   ResetLastError();
   if(!trade.PositionModify(ticket,cand,0.0) || !ResultAccepted())
   {
      LogTradeFailure("trail modify");
      return -1;
   }
   return 1;
}

void ManageR9Position(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   if(g_positionOpenedAt>0 && (tick.time-g_positionOpenedAt)>=InpMaxHoldSeconds)
   {
      ResetLastError();if(!trade.PositionClose(ticket) || !ResultAccepted()) LogTradeFailure("R9 max-hold close");return;
   }
   if(!InpTrailingEnabled || InpTrailPips<=0) return;
   const double activation=HunterDistance(InpTrailActivationPips);
   const double favorable=(type==POSITION_TYPE_BUY?(tick.bid-openPrice):(openPrice-tick.ask));
   if(favorable<activation) return;
   ModifyTrailingStop(ticket,type,tick,HunterDistance(InpTrailPips),currentSL);
}

void ManageP5Position(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   const int maxHold=(g_activeSleeve==GMM_SLEEVE_P5_H4?InpP5H4MaxHoldSeconds:InpP5H1MaxHoldSeconds);
   if(g_positionOpenedAt>0 && (tick.time-g_positionOpenedAt)>=maxHold)
   {
      ResetLastError();if(!trade.PositionClose(ticket) || !ResultAccepted()) LogTradeFailure("P5 max-hold close");return;
   }
   if(g_entryAtr<=0.0) return;
   const double favorable=(type==POSITION_TYPE_BUY?(tick.bid-openPrice):(openPrice-tick.ask));
   if(favorable+1e-12<g_entryAtr*InpP5ActivationAtr) return;
   if(ModifyTrailingStop(ticket,type,tick,g_entryAtr*InpP5TrailAtr,currentSL)>0) g_tradeHarvestArmed=true;
}

void ManageHftPosition(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   const int tradeSide=(type==POSITION_TYPE_BUY?1:-1);
   double atr=0.0,p3Disp=0.0,p3Eff=0.0,p3Flow=0.0;
   if(P3FailedIgnition(tradeSide,tick.time,atr,p3Disp,p3Eff,p3Flow))
   {
      const int oldEventSide=g_lastEventSide;
      const int age=(int)(tick.time-g_positionOpenedAt);
      ResetLastError();
      if(!trade.PositionClose(ticket) || !ResultAccepted())
      {
         LogTradeFailure("P3 failed-ignition close");
         return;
      }
      if(InpVerbose)
         PrintFormat("%s: P3_FAILED_EXIT side=%d MFE=%.3f MAE=%.3f ATR=%.3f disp=%.3f eff=%.3f flow=%.3f age=%d",
                     EA_TAG,tradeSide,g_tradeMFE,g_tradeMAE,atr,p3Disp,p3Eff,p3Flow,age);
      if(InpP3FlipAfterExit)
      {
         MqlTick fresh;
         if(SymbolInfoTick(_Symbol,fresh) && fresh.bid>0.0 && fresh.ask>0.0)
            OpenHftTrade(-tradeSide,-oldEventSide,GMM_SLEEVE_P3_FLIP,true,fresh,"P3_FLIP");
      }
      return;
   }

   const int maxHold=(g_tradeRunner?InpP2RunnerMaxHoldSeconds:InpP1MaxHoldSeconds);
   if(g_positionOpenedAt>0 && (tick.time-g_positionOpenedAt)>=maxHold)
   {
      ResetLastError();if(!trade.PositionClose(ticket) || !ResultAccepted()) LogTradeFailure("HFT max-hold close");return;
   }

   const double favorable=(type==POSITION_TYPE_BUY?(tick.bid-openPrice):(openPrice-tick.ask));
   if(g_tradeRunner)
   {
      double runnerAtr=(g_entryAtr>0.0?g_entryAtr:0.0);
      if(runnerAtr<=0.0) GetCompletedAtr(runnerAtr);
      if(runnerAtr>0.0) ModifyTrailingStop(ticket,type,tick,runnerAtr*InpP2RunnerTrailAtr,currentSL);
      return;
   }

   if(favorable+1e-12<InpP1HarvestActivationPrice) return;

   if(g_activeSleeve==GMM_SLEEVE_P1 && InpUseP2Runner)
   {
      double flow=0.0,eff=0.0,disp=0.0,structural=0.0;
      if(ShouldPromoteP2Runner(tradeSide,flow,eff,disp,structural))
      {
         g_tradeRunner=true;
         double runnerAtr=(g_entryAtr>0.0?g_entryAtr:0.0);
         if(runnerAtr<=0.0) GetCompletedAtr(runnerAtr);
         if(InpVerbose)
            PrintFormat("%s: P2_RUNNER_PROMOTE side=%d flow=%.3f eff=%.3f disp=%.3f structural=%.2f ATR=%.3f",
                        EA_TAG,tradeSide,flow,eff,disp,structural,runnerAtr);
         if(runnerAtr>0.0) ModifyTrailingStop(ticket,type,tick,runnerAtr*InpP2RunnerTrailAtr,currentSL);
         return;
      }
   }

   if(ModifyTrailingStop(ticket,type,tick,InpP1HarvestTrailPrice,currentSL)>0) g_tradeHarvestArmed=true;
}

void ManagePosition(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   UpdateExcursion(tick,type,openPrice);
   if(g_activeSleeve==GMM_SLEEVE_R9){ ManageR9Position(tick,ticket,type,openPrice,currentSL); return; }
   if(g_activeSleeve==GMM_SLEEVE_P5_H1 || g_activeSleeve==GMM_SLEEVE_P5_H4){ ManageP5Position(tick,ticket,type,openPrice,currentSL); return; }
   ManageHftPosition(tick,ticket,type,openPrice,currentSL);
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

   int eventSide=0;
   if((g_pendingMode==2 || g_pendingMode==1) && tick.ask>=g_cycleBuy) eventSide=1;
   else if((g_pendingMode==2 || g_pendingMode==-1) && tick.bid<=g_cycleSell) eventSide=-1;
   if(eventSide==0) return;

   double disp10=0.0,eff10=0.0,rng10=0.0;int turns10=0;
   if(!S1QualityForSide(eventSide,disp10,eff10,rng10,turns10)) return;

   if(!InpUseP1Harvester)
   {
      OpenR9Trade(eventSide,tick);
      return;
   }

   double alignedRet1=0.0,range1=0.0;int ticks1=0;string p1Label="ABSTAIN";
   const int p1Side=RouteP1Event(eventSide,alignedRet1,range1,ticks1,p1Label);
   if(p1Side!=0)
   {
      OpenHftTrade(p1Side,eventSide,GMM_SLEEVE_P1,false,tick,p1Label);
      return;
   }

   double atrRatio=1.0;
   if(P4Qualifies(eff10,atrRatio))
   {
      OpenHftTrade(-eventSide,eventSide,GMM_SLEEVE_P4,false,tick,"P4_ROT");
      if(InpVerbose) PrintFormat("%s: P4_ROTATION eventSide=%d eff10=%.3f atrRatio=%.3f",EA_TAG,eventSide,eff10,atrRatio);
      return;
   }

   if(InpVerbose)
      PrintFormat("%s: ABSTAIN eventSide=%d ret1=%.3f range1=%.3f ticks1=%d disp10=%.3f eff10=%.3f range10=%.3f turns10=%d",
                  EA_TAG,eventSide,alignedRet1,range1,ticks1,disp10,eff10,rng10,turns10);
   g_pendingMode=0;
}

bool P5Signal(const ENUM_TIMEFRAMES tf,const int breakoutBars,const double maxVolRatio,const int atrHandle,datetime &lastProcessedBar,int &side,double &atr)
{
   side=0;atr=0.0;
   const datetime currentBar=iTime(_Symbol,tf,0);
   if(currentBar<=0 || currentBar==lastProcessedBar) return false;
   lastProcessedBar=currentBar;
   if(breakoutBars<2 || atrHandle==INVALID_HANDLE) return false;

   MqlRates rates[]; ArraySetAsSeries(rates,true);
   const int need=breakoutBars+2;
   if(CopyRates(_Symbol,tf,1,need,rates)!=need) return false;
   double priorHigh=-DBL_MAX,priorLow=DBL_MAX;
   for(int i=1;i<=breakoutBars;i++)
   {
      if(rates[i].high>priorHigh) priorHigh=rates[i].high;
      if(rates[i].low<priorLow) priorLow=rates[i].low;
   }

   double currentAtr[1];
   if(CopyBuffer(atrHandle,0,1,1,currentAtr)!=1 || !MathIsValidNumber(currentAtr[0]) || currentAtr[0]<=0.0) return false;
   atr=currentAtr[0];
   const int n=MathMax(InpP5AtrBaselineBars,5);
   double hist[]; ArrayResize(hist,n);
   if(CopyBuffer(atrHandle,0,2,n,hist)!=n) return false;
   double mean=0.0;
   for(int i=0;i<n;i++)
   {
      if(!MathIsValidNumber(hist[i]) || hist[i]<=0.0) return false;
      mean+=hist[i];
   }
   mean/=(double)n;
   if(mean<=0.0 || atr/mean>maxVolRatio) return false;

   const double close1=rates[0].close;
   if(close1>priorHigh) side=1;
   else if(close1<priorLow) side=-1;
   return side!=0;
}

bool ProcessP5Structural(const MqlTick &tick)
{
   if(!InpUseP5Structural) return false;
   int side=0;double atr=0.0;
   if(P5Signal(PERIOD_H4,InpP5H4BreakoutBars,InpP5H4MaxVolRatio,g_p5H4AtrHandle,g_lastP5H4Bar,side,atr))
      return OpenP5Trade(side,GMM_SLEEVE_P5_H4,atr,tick);
   if(P5Signal(PERIOD_H1,InpP5H1BreakoutBars,InpP5H1MaxVolRatio,g_p5H1AtrHandle,g_lastP5H1Bar,side,atr))
      return OpenP5Trade(side,GMM_SLEEVE_P5_H1,atr,tick);
   return false;
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
      ManagePosition(tick,ticket,type,openPrice,currentSL);
      return;
   }

   if(g_hadPosition)
   {
      const ENUM_GMM_SLEEVE closedSleeve=g_activeSleeve;
      g_hadPosition=false;
      const datetime tradeMinute=g_tradeCycleMinute;
      ResetTradeRuntime();
      const datetime nowMinute=(datetime)((long)tick.time-((long)tick.time%60));
      if(closedSleeve!=GMM_SLEEVE_P5_H1 && closedSleeve!=GMM_SLEEVE_P5_H4 && nowMinute==tradeMinute && nowMinute==g_cycleMinute)
         ArmOppositeAfterExit();
      else if(closedSleeve==GMM_SLEEVE_P5_H1 || closedSleeve==GMM_SLEEVE_P5_H4)
         g_pendingMode=0;
      return;
   }

   ProcessEntries(tick);
   ulong checkTicket;ENUM_POSITION_TYPE checkType;double checkOpen,checkSL;
   if(!FindOurPosition(checkTicket,checkType,checkOpen,checkSL)) ProcessP5Structural(tick);
}

int OnInit()
{
   if(InpLots<=0.0 || InpGapPips<=0 || InpStopLossPips<=0 || InpTrailPips<0 || InpTrailActivationPips<0 ||
      InpMaxHoldSeconds<=0 || InpMaxSameMinuteRearms<0 || InpVelocityLookbackSec<2 || InpRangeLookbackSec<2 ||
      InpVelocityLookbackSec>=MICRO_CAPACITY || InpRangeLookbackSec>=MICRO_CAPACITY || InpMinVelocityPips<0 ||
      InpMinDirectionalEff<0.0 || InpMinDirectionalEff>1.0 || InpMinRangePips<0 || InpMaxTurns<0 ||
      InpHunterPipPrice<=0.0 || InpAtrPeriod<=0 || InpMaxSpreadPoints<0 ||
      InpP1EmergencyStopPrice<=0.0 || InpP1HarvestActivationPrice<0.0 || InpP1HarvestTrailPrice<=0.0 || InpP1MaxHoldSeconds<=0 ||
      InpP2LookbackSeconds<2 || InpP2LookbackSeconds>=MICRO_CAPACITY || InpP2MinDirectionalFlow<0.0 || InpP2MinDirectionalFlow>1.0 ||
      InpP2MinPathEfficiency<0.0 || InpP2MinPathEfficiency>1.0 || InpP2RunnerTrailAtr<=0.0 || InpP2RunnerMaxHoldSeconds<=0 ||
      InpP3EvaluateAfterSeconds<1 || InpP3MaxMFEToFail<0.0 || InpP3MinMAEAtr<=0.0 || InpP3AdverseLookbackSeconds<2 ||
      InpP3AdverseLookbackSeconds>=MICRO_CAPACITY || InpP3MinAdverseEfficiency<0.0 || InpP3MinAdverseEfficiency>1.0 ||
      InpP3MaxAlignedTickFlow<-1.0 || InpP3MaxAlignedTickFlow>0.0 || InpP4AtrBaselineBars<5 || InpP4MaxAtrRatio<=0.0 ||
      InpP4MaxEfficiency<0.0 || InpP4MaxEfficiency>1.0 || InpP5H1BreakoutBars<2 || InpP5H4BreakoutBars<2 ||
      InpP5AtrBaselineBars<5 || InpP5StopAtr<=0.0 || InpP5ActivationAtr<0.0 || InpP5TrailAtr<=0.0 ||
      InpP5H1MaxHoldSeconds<=0 || InpP5H4MaxHoldSeconds<=0)
   {
      Print(EA_TAG,": invalid inputs");return INIT_PARAMETERS_INCORRECT;
   }
   if(InpRequireXAUUSD && StringFind(_Symbol,"XAUUSD")<0)
   {
      PrintFormat("%s: symbol guard rejected %s; expected XAUUSD",EA_TAG,_Symbol);return INIT_FAILED;
   }

   trade.SetExpertMagicNumber(InpMagic);trade.SetDeviationInPoints(InpDeviationPoints);trade.SetAsyncMode(false);
   if(!trade.SetTypeFillingBySymbol(_Symbol)) Log("warning: unable to derive filling mode");

   const bool needM5Atr=(InpUseRegimeGate || InpUseP2Runner || InpUseP3FailedIgnition || InpUseP4Rotation);
   if(needM5Atr)
   {
      g_atrHandle=iATR(_Symbol,InpAtrTimeframe,InpAtrPeriod);
      if(g_atrHandle==INVALID_HANDLE){ PrintFormat("%s: M5 ATR handle failed lastError=%d",EA_TAG,GetLastError());return INIT_FAILED; }
   }
   if(InpUseP5Structural)
   {
      g_p5H1AtrHandle=iATR(_Symbol,PERIOD_H1,14);
      g_p5H4AtrHandle=iATR(_Symbol,PERIOD_H4,14);
      if(g_p5H1AtrHandle==INVALID_HANDLE || g_p5H4AtrHandle==INVALID_HANDLE)
      {
         PrintFormat("%s: P5 ATR handle failed lastError=%d",EA_TAG,GetLastError());return INIT_FAILED;
      }
   }

   PrintFormat("%s initialized P1=%s P2=%s P3=%s P4=%s P5=%s magic=%I64u",
               EA_TAG,(InpUseP1Harvester?"ON":"OFF"),(InpUseP2Runner?"ON":"OFF"),(InpUseP3FailedIgnition?"ON":"OFF"),
               (InpUseP4Rotation?"ON":"OFF"),(InpUseP5Structural?"ON":"OFF"),InpMagic);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_atrHandle!=INVALID_HANDLE){ IndicatorRelease(g_atrHandle);g_atrHandle=INVALID_HANDLE; }
   if(g_p5H1AtrHandle!=INVALID_HANDLE){ IndicatorRelease(g_p5H1AtrHandle);g_p5H1AtrHandle=INVALID_HANDLE; }
   if(g_p5H4AtrHandle!=INVALID_HANDLE){ IndicatorRelease(g_p5H4AtrHandle);g_p5H4AtrHandle=INVALID_HANDLE; }
   Log(StringFormat("deinit reason=%d",reason));
}

void OnTick()
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol,tick) || tick.bid<=0.0 || tick.ask<=0.0) return;
   Reconcile(tick);
}
