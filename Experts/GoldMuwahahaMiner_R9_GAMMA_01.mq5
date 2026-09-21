#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "1.91"
#property strict
#property description "Gold MUWHAHA R9 GAMMA-01: exact R9 core plus causal H1 Donchian/ATR structural persistence sleeve."

#include <Trade/Trade.mqh>
CTrade trade;
CTrade structuralTrade;

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

input group "R9 GAMMA-01 research A/B controls"
input bool   InpCoreEnabled                 = true;

input group "R9 GAMMA-01 H1 structural persistence sleeve"
input bool   InpStructuralEnabled           = true;
input double InpStructuralLots              = 0.01;
input ulong  InpStructuralMagic             = 5560;
input int    InpStructuralDonchianBars       = 4;
input int    InpStructuralAtrBars            = 14;
input double InpStructuralStopATR            = 2.0;
input double InpStructuralTrailATR           = 2.0;
input double InpStructuralMinBalance         = 1000.0;
input bool   InpStructuralAllowConcurrentCore= true;

string EA_TAG = "GM_R9_GAMMA01";
string STRUCT_TAG = "GM_G01_H1_STRUCT";

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

bool g_structLevelsReady=false;
datetime g_structH1Start=0;
double g_structUpper=0.0;
double g_structLower=0.0;
double g_structAtr=0.0;
double g_structPrevMid=0.0;
bool g_structHadPosition=false;
double g_structHighWater=0.0;
double g_structLowWater=0.0;

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

bool StructuralResultAccepted()
{
   const uint c=structuralTrade.ResultRetcode();
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

bool FindStructuralPosition(ulong &ticket,ENUM_POSITION_TYPE &type,double &openPrice,double &stopLoss)
{
   ticket=0;openPrice=0.0;stopLoss=0.0;type=POSITION_TYPE_BUY;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong t=PositionGetTicket(i);if(t==0) continue;
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpStructuralMagic) continue;
      ticket=t;
      type=(ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      openPrice=PositionGetDouble(POSITION_PRICE_OPEN);
      stopLoss=PositionGetDouble(POSITION_SL);
      return true;
   }
   return false;
}

bool ComputeStructuralLevels(double &upper,double &lower,double &atr)
{
   upper=-DBL_MAX;lower=DBL_MAX;atr=0.0;
   if(InpStructuralDonchianBars<1 || InpStructuralAtrBars<1) return false;
   const int need=MathMax(InpStructuralDonchianBars,InpStructuralAtrBars)+2;
   if(Bars(_Symbol,PERIOD_H1)<need) return false;

   for(int sh=1;sh<=InpStructuralDonchianBars;++sh)
   {
      const double h=iHigh(_Symbol,PERIOD_H1,sh);
      const double l=iLow(_Symbol,PERIOD_H1,sh);
      if(h<=0.0 || l<=0.0) return false;
      if(h>upper) upper=h;
      if(l<lower) lower=l;
   }

   double sumTR=0.0;
   for(int sh=1;sh<=InpStructuralAtrBars;++sh)
   {
      const double h=iHigh(_Symbol,PERIOD_H1,sh);
      const double l=iLow(_Symbol,PERIOD_H1,sh);
      const double pc=iClose(_Symbol,PERIOD_H1,sh+1);
      if(h<=0.0 || l<=0.0 || pc<=0.0) return false;
      const double tr=MathMax(h-l,MathMax(MathAbs(h-pc),MathAbs(l-pc)));
      sumTR+=tr;
   }
   atr=sumTR/(double)InpStructuralAtrBars;
   return (upper>lower && atr>0.0 && MathIsValidNumber(atr));
}

void RefreshStructuralLevels()
{
   if(!InpStructuralEnabled) return;
   const datetime h1=iTime(_Symbol,PERIOD_H1,0);
   if(h1<=0) return;
   if(g_structLevelsReady && h1==g_structH1Start) return;

   double u,l,a;
   if(!ComputeStructuralLevels(u,l,a))
   {
      g_structLevelsReady=false;
      return;
   }

   g_structH1Start=h1;
   g_structUpper=u;
   g_structLower=l;
   g_structAtr=a;
   g_structLevelsReady=true;

   if(InpVerbose)
      PrintFormat("%s: H1 state upper=%.5f lower=%.5f ATR%d=%.5f",
                  STRUCT_TAG,g_structUpper,g_structLower,InpStructuralAtrBars,g_structAtr);
}

bool CorePositionExists()
{
   ulong ticket;ENUM_POSITION_TYPE type;double op,sl;
   return FindOurPosition(ticket,type,op,sl);
}

bool OpenStructuralTrade(const int side,const MqlTick &tick)
{
   if(!g_structLevelsReady || g_structAtr<=0.0) return false;
   if(AccountInfoDouble(ACCOUNT_BALANCE)+1e-9<InpStructuralMinBalance) return false;

   const double volume=NormalizeVolume(InpStructuralLots);
   const double brokerMin=InpRespectBrokerStops?BrokerStopsDistance()+TickSize():0.0;
   const double sd=MathMax(InpStructuralStopATR*g_structAtr,brokerMin);
   const double ts=TickSize();
   double sl=0.0;bool sent=false;

   structuralTrade.SetExpertMagicNumber(InpStructuralMagic);
   ResetLastError();
   if(side>0)
   {
      sl=NormalizePrice(tick.ask-sd);
      if(InpRespectBrokerStops)
         sl=MathMin(sl,NormalizePrice(tick.bid-brokerMin-ts));
      sent=structuralTrade.Buy(volume,_Symbol,0.0,sl,0.0,STRUCT_TAG+" BUY");
   }
   else
   {
      sl=NormalizePrice(tick.bid+sd);
      if(InpRespectBrokerStops)
         sl=MathMax(sl,NormalizePrice(tick.ask+brokerMin+ts));
      sent=structuralTrade.Sell(volume,_Symbol,0.0,sl,0.0,STRUCT_TAG+" SELL");
   }

   if(!sent || !StructuralResultAccepted())
   {
      PrintFormat("%s: %s failed; retcode=%u (%s), lastError=%d",
                  STRUCT_TAG,side>0?"BUY":"SELL",
                  structuralTrade.ResultRetcode(),structuralTrade.ResultRetcodeDescription(),GetLastError());
      return false;
   }

   g_structHighWater=tick.bid;
   g_structLowWater=tick.ask;
   g_structHadPosition=true;
   if(InpVerbose)
      PrintFormat("%s: %s entry upper=%.5f lower=%.5f ATR=%.5f balance=%.2f",
                  STRUCT_TAG,side>0?"BUY":"SELL",g_structUpper,g_structLower,g_structAtr,
                  AccountInfoDouble(ACCOUNT_BALANCE));
   return true;
}

void ManageStructuralPosition(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   if(!g_structLevelsReady || g_structAtr<=0.0) return;

   const double trail=MathMax(InpStructuralTrailATR*g_structAtr,TickSize());
   const double broker=InpRespectBrokerStops?BrokerStopsDistance():0.0;
   const double ts=TickSize();
   double cand=0.0;

   if(type==POSITION_TYPE_BUY)
   {
      if(g_structHighWater<=0.0) g_structHighWater=MathMax(openPrice,tick.bid);
      if(tick.bid>g_structHighWater) g_structHighWater=tick.bid;
      cand=NormalizePrice(g_structHighWater-trail);
      if(InpRespectBrokerStops)
         cand=MathMin(cand,NormalizePrice(tick.bid-broker-ts));
      if(cand<=0.0 || cand<=currentSL+ts*0.5) return;
   }
   else
   {
      if(g_structLowWater<=0.0) g_structLowWater=MathMin(openPrice,tick.ask);
      if(tick.ask<g_structLowWater) g_structLowWater=tick.ask;
      cand=NormalizePrice(g_structLowWater+trail);
      if(InpRespectBrokerStops)
         cand=MathMax(cand,NormalizePrice(tick.ask+broker+ts));
      if(cand<=0.0 || (currentSL>0.0 && cand>=currentSL-ts*0.5)) return;
   }

   structuralTrade.SetExpertMagicNumber(InpStructuralMagic);
   ResetLastError();
   if(!structuralTrade.PositionModify(ticket,cand,0.0) || !StructuralResultAccepted())
      PrintFormat("%s: trail modify failed; retcode=%u (%s), lastError=%d",
                  STRUCT_TAG,structuralTrade.ResultRetcode(),structuralTrade.ResultRetcodeDescription(),GetLastError());
}

void StructuralReconcile(const MqlTick &tick)
{
   if(!InpStructuralEnabled) return;

   RefreshStructuralLevels();
   const double mid=(tick.ask+tick.bid)*0.5;

   ulong ticket;ENUM_POSITION_TYPE type;double openPrice,currentSL;
   const bool have=FindStructuralPosition(ticket,type,openPrice,currentSL);
   if(have)
   {
      g_structHadPosition=true;
      ManageStructuralPosition(tick,ticket,type,openPrice,currentSL);
      g_structPrevMid=mid;
      return;
   }

   if(g_structHadPosition)
   {
      g_structHadPosition=false;
      g_structHighWater=0.0;
      g_structLowWater=0.0;
   }

   if(!g_structLevelsReady || AccountInfoDouble(ACCOUNT_BALANCE)+1e-9<InpStructuralMinBalance)
   {
      g_structPrevMid=mid;
      return;
   }

   if(!InpStructuralAllowConcurrentCore && CorePositionExists())
   {
      g_structPrevMid=mid;
      return;
   }

   if(g_structPrevMid<=0.0)
   {
      g_structPrevMid=mid;
      return;
   }

   const bool up=(g_structPrevMid<g_structUpper && mid>=g_structUpper);
   const bool dn=(g_structPrevMid>g_structLower && mid<=g_structLower);

   if(up && !dn) OpenStructuralTrade(1,tick);
   else if(dn && !up) OpenStructuralTrade(-1,tick);

   g_structPrevMid=mid;
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
      InpHunterPipPrice<=0.0 || InpAtrPeriod<=0 || InpMaxSpreadPoints<0 ||
      InpStructuralLots<=0.0 || InpStructuralDonchianBars<1 || InpStructuralAtrBars<1 ||
      InpStructuralStopATR<=0.0 || InpStructuralTrailATR<=0.0 || InpStructuralMinBalance<0.0)
   {
      Print(EA_TAG,": invalid inputs");return INIT_PARAMETERS_INCORRECT;
   }
   if(InpCoreEnabled && InpStructuralEnabled && InpStructuralAllowConcurrentCore &&
      (ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
   {
      Print(EA_TAG,": concurrent core + structural sleeves require a hedging account; disable concurrency or structural sleeve on netting accounts.");
      return INIT_PARAMETERS_INCORRECT;
   }

   trade.SetExpertMagicNumber(InpMagic);trade.SetDeviationInPoints(InpDeviationPoints);trade.SetAsyncMode(false);
   structuralTrade.SetExpertMagicNumber(InpStructuralMagic);structuralTrade.SetDeviationInPoints(InpDeviationPoints);structuralTrade.SetAsyncMode(false);
   if(!trade.SetTypeFillingBySymbol(_Symbol)) Log("warning: unable to derive filling mode");
   if(!structuralTrade.SetTypeFillingBySymbol(_Symbol)) Log("warning: unable to derive structural filling mode");
   if(InpCoreEnabled && InpUseRegimeGate)
   {
      g_atrHandle=iATR(_Symbol,InpAtrTimeframe,InpAtrPeriod);
      if(g_atrHandle==INVALID_HANDLE){ PrintFormat("%s: ATR handle failed lastError=%d",EA_TAG,GetLastError());return INIT_FAILED; }
   }
   PrintFormat("%s initialized core=%s gap=%d stop=%d trail=%d act=%d velLB=%d minVel=%d eff=%.2f range=%d maxHold=%d rearms=%d",
               EA_TAG,InpCoreEnabled?"ON":"OFF",InpGapPips,InpStopLossPips,InpTrailPips,InpTrailActivationPips,InpVelocityLookbackSec,InpMinVelocityPips,InpMinDirectionalEff,InpMinRangePips,InpMaxHoldSeconds,InpMaxSameMinuteRearms);
   PrintFormat("%s initialized enabled=%s N=%d ATR=%d stop=%.2fATR trail=%.2fATR minBalance=%.2f concurrentCore=%s",
               STRUCT_TAG,InpStructuralEnabled?"ON":"OFF",InpStructuralDonchianBars,InpStructuralAtrBars,
               InpStructuralStopATR,InpStructuralTrailATR,InpStructuralMinBalance,
               InpStructuralAllowConcurrentCore?"YES":"NO");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_atrHandle!=INVALID_HANDLE){ IndicatorRelease(g_atrHandle);g_atrHandle=INVALID_HANDLE; }
   Log(StringFormat("deinit reason=%d",reason));
}

void OnTick()
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol,tick) || tick.bid<=0.0 || tick.ask<=0.0) return;
   if(InpCoreEnabled) Reconcile(tick);
   StructuralReconcile(tick);
}
