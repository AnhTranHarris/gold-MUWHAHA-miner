#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "2.00"
#property strict
#property description "Gold MUWHAHA R10: R9 hybrid architecture with internally selected Coinexx server-time S1 execution regimes."

#include <Trade/Trade.mqh>
CTrade trade;

enum ENUM_GMM_SESSION
{
   GMM_SESSION_OFF = 0,
   GMM_SESSION_LONDON = 1,
   GMM_SESSION_OVERLAP = 2,
   GMM_SESSION_NEWYORK = 3
};

struct ExecProfile
{
   int gapPips;
   int stopPips;
   int trailPips;
   int activationPips;
   int maxRearms;
   int maxHoldSeconds;
   int velocityLookbackSec;
   int minVelocityPips;
   double minDirectionalEff;
   int rangeLookbackSec;
   int minRangePips;
   int maxTurns;
};

input group "R10 account/execution"
input double InpLots                = 0.01;
input ulong  InpMagic               = 5560;
input int    InpDeviationPoints     = 20;
input bool   InpVerbose             = true;

input group "R10 strategic regime gate"
input bool            InpUseRegimeGate     = true;
input ENUM_TIMEFRAMES InpAtrTimeframe      = PERIOD_M5;
input int             InpAtrPeriod         = 14;
input int             InpMaxSpreadPoints   = 25;
input bool            InpFailClosedOnNoATR = true;

input group "R10 session-adaptive ATR"
input bool   InpUseSessionAdaptiveAtr = true;
input int    InpQuoteUtcOffsetMinutes = 0;
input double InpAtrLondonPrice        = 2.00;
input double InpAtrOverlapPrice       = 1.75;
input double InpAtrNewYorkPrice       = 1.75;
input double InpAtrOffSessionPrice    = 2.50;

input group "Price normalization"
input double InpHunterPipPrice       = 0.01;
input bool   InpRespectBrokerStops   = true;

string EA_TAG = "GM_R10_SESSION_REGIME";

#define MICRO_CAPACITY 160
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
double g_bucketOpen=0.0;
double g_bucketHigh=0.0;
double g_bucketLow=0.0;
double g_bucketClose=0.0;

datetime g_cycleMinute=0;
double g_cycleBuy=0.0;
double g_cycleSell=0.0;
int g_pendingMode=0; // 2 both, 1 buy only, -1 sell only, 0 none
int g_rearms=0;
ExecProfile g_cycleProfile;

bool g_hadPosition=false;
ENUM_POSITION_TYPE g_lastPositionType=POSITION_TYPE_BUY;
datetime g_positionOpenedAt=0;
datetime g_tradeCycleMinute=0;
ExecProfile g_tradeProfile;

int g_atrHandle=INVALID_HANDLE;
datetime g_lastGateLogBar=0;

void Log(const string text)
{
   if(InpVerbose)
      Print(EA_TAG, ": ", text);
}

int DigitsForSymbol()
{
   return (int)SymbolInfoInteger(_Symbol,SYMBOL_DIGITS);
}

double TickSize()
{
   double value=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   if(value<=0.0)
      value=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   return value;
}

double NormalizePrice(const double price)
{
   const double tick=TickSize();
   if(tick<=0.0)
      return NormalizeDouble(price,DigitsForSymbol());
   return NormalizeDouble(MathRound(price/tick)*tick,DigitsForSymbol());
}

double NormalizeVolume(const double requested)
{
   const double minimum=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   const double maximum=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   const double step=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   double volume=MathMax(minimum,MathMin(maximum,requested));
   if(step>0.0)
      volume=minimum+MathRound((volume-minimum)/step)*step;
   return NormalizeDouble(MathMax(minimum,MathMin(maximum,volume)),8);
}

double HunterDistance(const int pips)
{
   return (double)pips*InpHunterPipPrice;
}

double BrokerStopsDistance()
{
   const long stops=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL);
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   return (double)MathMax((long)0,stops)*point;
}

bool ResultAccepted()
{
   const uint code=trade.ResultRetcode();
   return (code==TRADE_RETCODE_DONE ||
           code==TRADE_RETCODE_PLACED ||
           code==TRADE_RETCODE_DONE_PARTIAL ||
           code==TRADE_RETCODE_NO_CHANGES);
}

void LogTradeFailure(const string action)
{
   PrintFormat("%s: %s failed; retcode=%u (%s), lastError=%d",
               EA_TAG,action,trade.ResultRetcode(),trade.ResultRetcodeDescription(),GetLastError());
}

// The execution profiles are intentionally internal rather than external inputs.
// This prevents accidental tester/preset changes from silently altering the certified geometry.
void SelectExecutionProfile(const datetime quoteTime,ExecProfile &p)
{
   MqlDateTime tm={};
   TimeToStruct(quoteTime,tm);
   const int hour=tm.hour;

   p.velocityLookbackSec=10;
   p.rangeLookbackSec=10;

   if(hour<=6)
   {
      // 00:00-06:59 Coinexx server time
      p.gapPips=20;
      p.stopPips=35;
      p.trailPips=5;
      p.activationPips=6;
      p.maxRearms=4;
      p.maxHoldSeconds=20;
      p.minVelocityPips=2;
      p.minDirectionalEff=0.65;
      p.minRangePips=75;
      p.maxTurns=99;
   }
   else if(hour<=11)
   {
      // 07:00-11:59
      p.gapPips=15;
      p.stopPips=35;
      p.trailPips=5;
      p.activationPips=25;
      p.maxRearms=7;
      p.maxHoldSeconds=20;
      p.minVelocityPips=0;
      p.minDirectionalEff=0.70;
      p.minRangePips=75;
      p.maxTurns=99;
   }
   else if(hour<=15)
   {
      // 12:00-15:59
      p.gapPips=15;
      p.stopPips=35;
      p.trailPips=10;
      p.activationPips=6;
      p.maxRearms=3;
      p.maxHoldSeconds=35;
      p.minVelocityPips=2;
      p.minDirectionalEff=0.65;
      p.minRangePips=75;
      p.maxTurns=7;
   }
   else if(hour<=20)
   {
      // 16:00-20:59
      p.gapPips=15;
      p.stopPips=35;
      p.trailPips=5;
      p.activationPips=25;
      p.maxRearms=7;
      p.maxHoldSeconds=20;
      p.minVelocityPips=0;
      p.minDirectionalEff=0.70;
      p.minRangePips=75;
      p.maxTurns=99;
   }
   else
   {
      // 21:00-23:59
      p.gapPips=15;
      p.stopPips=28;
      p.trailPips=8;
      p.activationPips=25;
      p.maxRearms=2;
      p.maxHoldSeconds=15;
      p.minVelocityPips=18;
      p.minDirectionalEff=0.65;
      p.minRangePips=60;
      p.maxTurns=12;
   }
}

int DaysInMonth(const int year,const int month)
{
   if(month==2)
   {
      const bool leap=((year%400)==0 || ((year%4)==0 && (year%100)!=0));
      return leap?29:28;
   }
   if(month==4 || month==6 || month==9 || month==11)
      return 30;
   return 31;
}

int DayOfWeekUtc(const int year,const int month,const int day)
{
   MqlDateTime value={};
   value.year=year; value.mon=month; value.day=day; value.hour=12;
   const datetime stamp=StructToTime(value);
   MqlDateTime result={};
   if(!TimeToStruct(stamp,result))
      return -1;
   return result.day_of_week;
}

int NthSunday(const int year,const int month,const int nth)
{
   const int firstDow=DayOfWeekUtc(year,month,1);
   if(firstDow<0)
      return 0;
   const int firstSunday=1+((7-firstDow)%7);
   return firstSunday+(nth-1)*7;
}

int LastSunday(const int year,const int month)
{
   const int lastDay=DaysInMonth(year,month);
   const int dow=DayOfWeekUtc(year,month,lastDay);
   if(dow<0)
      return 0;
   return lastDay-dow;
}

datetime MakeUtc(const int year,const int month,const int day,const int hour,const int minute=0)
{
   MqlDateTime value={};
   value.year=year; value.mon=month; value.day=day; value.hour=hour; value.min=minute;
   return StructToTime(value);
}

bool IsLondonDstUtc(const datetime utc)
{
   MqlDateTime now={};
   if(!TimeToStruct(utc,now))
      return false;
   const datetime start=MakeUtc(now.year,3,LastSunday(now.year,3),1,0);
   const datetime end=MakeUtc(now.year,10,LastSunday(now.year,10),1,0);
   return (utc>=start && utc<end);
}

bool IsNewYorkDstUtc(const datetime utc)
{
   MqlDateTime now={};
   if(!TimeToStruct(utc,now))
      return false;
   const datetime start=MakeUtc(now.year,3,NthSunday(now.year,3,2),7,0);
   const datetime end=MakeUtc(now.year,11,NthSunday(now.year,11,1),6,0);
   return (utc>=start && utc<end);
}

int LocalMinuteOfDay(const datetime utc,const int offsetMinutes)
{
   MqlDateTime value={};
   if(!TimeToStruct(utc+(datetime)(offsetMinutes*60),value))
      return -1;
   return value.hour*60+value.min;
}

ENUM_GMM_SESSION CurrentSession()
{
   const datetime quote=TimeCurrent();
   const datetime utc=quote-(datetime)(InpQuoteUtcOffsetMinutes*60);
   const int londonOffset=IsLondonDstUtc(utc)?60:0;
   const int nyOffset=IsNewYorkDstUtc(utc)?-240:-300;
   const int londonMinute=LocalMinuteOfDay(utc,londonOffset);
   const int nyMinute=LocalMinuteOfDay(utc,nyOffset);
   const bool london=(londonMinute>=8*60 && londonMinute<16*60+30);
   const bool newYork=(nyMinute>=8*60 && nyMinute<17*60);
   if(london && newYork) return GMM_SESSION_OVERLAP;
   if(london) return GMM_SESSION_LONDON;
   if(newYork) return GMM_SESSION_NEWYORK;
   return GMM_SESSION_OFF;
}

double SessionAtrMinimum(const ENUM_GMM_SESSION session)
{
   if(!InpUseSessionAdaptiveAtr) return InpAtrLondonPrice;
   if(session==GMM_SESSION_OVERLAP) return InpAtrOverlapPrice;
   if(session==GMM_SESSION_NEWYORK) return InpAtrNewYorkPrice;
   if(session==GMM_SESSION_LONDON) return InpAtrLondonPrice;
   return InpAtrOffSessionPrice;
}

bool GetCompletedAtr(double &atr)
{
   atr=0.0;
   if(!InpUseRegimeGate)
      return true;
   if(g_atrHandle==INVALID_HANDLE || BarsCalculated(g_atrHandle)<InpAtrPeriod+2)
      return false;
   double buffer[1];
   ResetLastError();
   if(CopyBuffer(g_atrHandle,0,1,1,buffer)!=1 || !MathIsValidNumber(buffer[0]) || buffer[0]<=0.0)
      return false;
   atr=buffer[0];
   return true;
}

bool GateAllowsEntry(const MqlTick &tick)
{
   if(!InpUseRegimeGate)
      return true;
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(point<=0.0 || tick.ask<=0.0 || tick.bid<=0.0)
      return false;
   const double spreadPoints=(tick.ask-tick.bid)/point;
   if(InpMaxSpreadPoints>0 && spreadPoints>(double)InpMaxSpreadPoints+1e-9)
      return false;
   double atr=0.0;
   const bool haveAtr=GetCompletedAtr(atr);
   if(!haveAtr)
      return !InpFailClosedOnNoATR;
   const double minimumAtr=SessionAtrMinimum(CurrentSession());
   if(minimumAtr>0.0 && atr+1e-12<minimumAtr)
   {
      const datetime bar=iTime(_Symbol,PERIOD_M1,0);
      if(InpVerbose && bar!=g_lastGateLogBar)
      {
         PrintFormat("%s: gate CLOSED ATR=%.5f min=%.5f spread=%.1f",
                     EA_TAG,atr,minimumAtr,spreadPoints);
         g_lastGateLogBar=bar;
      }
      return false;
   }
   return true;
}

void PushCompletedSecond(const datetime sec,const double o,const double h,const double l,const double c)
{
   g_micro[g_microHead].second=sec;
   g_micro[g_microHead].open=o;
   g_micro[g_microHead].high=h;
   g_micro[g_microHead].low=l;
   g_micro[g_microHead].close=c;
   g_microHead=(g_microHead+1)%MICRO_CAPACITY;
   if(g_microCount<MICRO_CAPACITY)
      g_microCount++;
}

int RingIndexFromNewest(const int offset)
{
   int idx=g_microHead-1-offset;
   while(idx<0) idx+=MICRO_CAPACITY;
   return idx%MICRO_CAPACITY;
}

void UpdateSecondBucket(const MqlTick &tick)
{
   const datetime sec=tick.time;
   if(!g_bucketReady)
   {
      g_bucketReady=true;
      g_bucketSecond=sec;
      g_bucketOpen=tick.bid;
      g_bucketHigh=tick.bid;
      g_bucketLow=tick.bid;
      g_bucketClose=tick.bid;
      return;
   }
   if(sec!=g_bucketSecond)
   {
      PushCompletedSecond(g_bucketSecond,g_bucketOpen,g_bucketHigh,g_bucketLow,g_bucketClose);
      g_bucketSecond=sec;
      g_bucketOpen=tick.bid;
      g_bucketHigh=tick.bid;
      g_bucketLow=tick.bid;
      g_bucketClose=tick.bid;
      return;
   }
   if(tick.bid>g_bucketHigh) g_bucketHigh=tick.bid;
   if(tick.bid<g_bucketLow) g_bucketLow=tick.bid;
   g_bucketClose=tick.bid;
}

bool S1QualityForSide(const int side,const ExecProfile &p,double &disp,double &eff,double &recentRange,int &turns)
{
   disp=0.0; eff=0.0; recentRange=0.0; turns=0;
   const int need=MathMax(p.velocityLookbackSec,p.rangeLookbackSec)+1;
   if(g_microCount<need)
      return false;

   const int oldest=RingIndexFromNewest(p.velocityLookbackSec-1);
   double previous=g_micro[oldest].close;
   const double start=previous;
   double travel=0.0;
   double previousSign=0.0;

   for(int offset=p.velocityLookbackSec-2;offset>=0;--offset)
   {
      const int idx=RingIndexFromNewest(offset);
      const double value=g_micro[idx].close;
      const double delta=value-previous;
      travel+=MathAbs(delta);
      const double sign=(delta>0.0?1.0:(delta<0.0?-1.0:0.0));
      if(sign!=0.0)
      {
         if(previousSign!=0.0 && sign!=previousSign)
            turns++;
         previousSign=sign;
      }
      previous=value;
   }

   const int newest=RingIndexFromNewest(0);
   disp=g_micro[newest].close-start;
   eff=MathAbs(disp)/(travel+1e-9);

   double hi=-DBL_MAX;
   double lo=DBL_MAX;
   for(int offset=0;offset<p.rangeLookbackSec;++offset)
   {
      const int idx=RingIndexFromNewest(offset);
      if(g_micro[idx].high>hi) hi=g_micro[idx].high;
      if(g_micro[idx].low<lo) lo=g_micro[idx].low;
   }
   recentRange=hi-lo;

   if(eff+1e-12<p.minDirectionalEff) return false;
   if(turns>p.maxTurns) return false;
   if(recentRange+1e-12<HunterDistance(p.minRangePips)) return false;
   const double minVelocity=HunterDistance(p.minVelocityPips);
   if(side>0 && disp+1e-12<minVelocity) return false;
   if(side<0 && disp-1e-12>-minVelocity) return false;
   return true;
}

bool FindOurPosition(ulong &ticket,ENUM_POSITION_TYPE &type,double &openPrice,double &stopLoss)
{
   ticket=0; openPrice=0.0; stopLoss=0.0; type=POSITION_TYPE_BUY;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong current=PositionGetTicket(i);
      if(current==0) continue;
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
      ticket=current;
      type=(ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      openPrice=PositionGetDouble(POSITION_PRICE_OPEN);
      stopLoss=PositionGetDouble(POSITION_SL);
      return true;
   }
   return false;
}

bool OpenTrade(const int side,const MqlTick &tick)
{
   const double volume=NormalizeVolume(InpLots);
   const double brokerMinimum=InpRespectBrokerStops?BrokerStopsDistance()+TickSize():0.0;
   const double stopDistance=MathMax(HunterDistance(g_cycleProfile.stopPips),brokerMinimum);
   double sl=0.0;
   bool sent=false;
   ResetLastError();
   if(side>0)
   {
      sl=NormalizePrice(tick.bid-stopDistance);
      sent=trade.Buy(volume,_Symbol,0.0,sl,0.0,EA_TAG+" BUY");
   }
   else
   {
      sl=NormalizePrice(tick.ask+stopDistance);
      sent=trade.Sell(volume,_Symbol,0.0,sl,0.0,EA_TAG+" SELL");
   }
   if(!sent || !ResultAccepted())
   {
      LogTradeFailure(side>0?"BUY":"SELL");
      return false;
   }

   g_positionOpenedAt=tick.time;
   g_tradeCycleMinute=g_cycleMinute;
   g_tradeProfile=g_cycleProfile;
   g_pendingMode=0;

   if(InpVerbose)
      PrintFormat("%s: %s entry minute=%s profile gap=%d stop=%d trail=%d act=%d hold=%d rearm=%d",
                  EA_TAG,side>0?"BUY":"SELL",TimeToString(g_cycleMinute,TIME_DATE|TIME_MINUTES),
                  g_tradeProfile.gapPips,g_tradeProfile.stopPips,g_tradeProfile.trailPips,
                  g_tradeProfile.activationPips,g_tradeProfile.maxHoldSeconds,g_rearms);
   return true;
}

void ManagePosition(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   if(g_positionOpenedAt>0 && (tick.time-g_positionOpenedAt)>=g_tradeProfile.maxHoldSeconds)
   {
      ResetLastError();
      if(!trade.PositionClose(ticket) || !ResultAccepted())
         LogTradeFailure("max-hold close");
      return;
   }

   if(g_tradeProfile.trailPips<=0)
      return;

   const double trail=HunterDistance(g_tradeProfile.trailPips);
   const double activation=HunterDistance(g_tradeProfile.activationPips);
   const double brokerDistance=InpRespectBrokerStops?BrokerStopsDistance():0.0;
   const double tickSize=TickSize();
   double candidate=0.0;

   if(type==POSITION_TYPE_BUY)
   {
      if((tick.bid-openPrice)<activation) return;
      candidate=NormalizePrice(tick.bid-trail);
      candidate=MathMin(candidate,NormalizePrice(tick.bid-brokerDistance-tickSize));
      if(candidate<=0.0 || candidate<=currentSL+tickSize*0.5) return;
   }
   else
   {
      if((openPrice-tick.ask)<activation) return;
      candidate=NormalizePrice(tick.ask+trail);
      candidate=MathMax(candidate,NormalizePrice(tick.ask+brokerDistance+tickSize));
      if(candidate<=0.0 || (currentSL>0.0 && candidate>=currentSL-tickSize*0.5)) return;
   }

   ResetLastError();
   if(!trade.PositionModify(ticket,candidate,0.0) || !ResultAccepted())
      LogTradeFailure("trail modify");
}

void StartMinuteCycle(const MqlTick &tick)
{
   const datetime minute=(datetime)((long)tick.time-((long)tick.time%60));
   if(minute==g_cycleMinute)
      return;

   g_cycleMinute=minute;
   g_rearms=0;
   g_pendingMode=2;
   SelectExecutionProfile(tick.time,g_cycleProfile);

   const double mid=(tick.ask+tick.bid)*0.5;
   const double half=HunterDistance(g_cycleProfile.gapPips)*0.5;
   g_cycleBuy=NormalizePrice(mid+half);
   g_cycleSell=NormalizePrice(mid-half);
}

void ArmOppositeAfterExit()
{
   if(g_rearms>=g_cycleProfile.maxRearms)
   {
      g_pendingMode=0;
      return;
   }
   g_rearms++;
   g_pendingMode=(g_lastPositionType==POSITION_TYPE_SELL)?1:-1;
}

void ProcessEntries(const MqlTick &tick)
{
   if(g_pendingMode==0)
      return;
   if(!GateAllowsEntry(tick))
      return;

   int side=0;
   if((g_pendingMode==2 || g_pendingMode==1) && tick.ask>=g_cycleBuy)
      side=1;
   else if((g_pendingMode==2 || g_pendingMode==-1) && tick.bid<=g_cycleSell)
      side=-1;
   if(side==0)
      return;

   double disp=0.0,eff=0.0,recentRange=0.0;
   int turns=0;
   if(!S1QualityForSide(side,g_cycleProfile,disp,eff,recentRange,turns))
      return;

   if(InpVerbose)
      PrintFormat("%s: qualified side=%d disp=%.3f eff=%.3f range=%.3f turns=%d profileHour=%s",
                  EA_TAG,side,disp,eff,recentRange,turns,TimeToString(tick.time,TIME_MINUTES));

   OpenTrade(side,tick);
}

void Reconcile(const MqlTick &tick)
{
   UpdateSecondBucket(tick);

   ulong ticket;
   ENUM_POSITION_TYPE type;
   double openPrice=0.0,currentSL=0.0;
   const bool havePosition=FindOurPosition(ticket,type,openPrice,currentSL);

   if(havePosition)
   {
      g_hadPosition=true;
      g_lastPositionType=type;
      if(g_positionOpenedAt<=0)
         g_positionOpenedAt=(datetime)PositionGetInteger(POSITION_TIME);
      ManagePosition(tick,ticket,type,openPrice,currentSL);
      return;
   }

   if(g_hadPosition)
   {
      g_hadPosition=false;
      g_positionOpenedAt=0;
      const datetime nowMinute=(datetime)((long)tick.time-((long)tick.time%60));
      if(nowMinute==g_tradeCycleMinute && nowMinute==g_cycleMinute)
         ArmOppositeAfterExit();
      else
      {
         // A trade that survived into a new minute does not re-arm the old boundary.
         g_cycleMinute=0;
         StartMinuteCycle(tick);
      }
      g_tradeCycleMinute=0;
      return;
   }

   StartMinuteCycle(tick);
   ProcessEntries(tick);
}

int OnInit()
{
   if(InpLots<=0.0 || InpHunterPipPrice<=0.0 || InpAtrPeriod<=0 || InpMaxSpreadPoints<0)
   {
      Print(EA_TAG,": invalid inputs");
      return INIT_PARAMETERS_INCORRECT;
   }

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPoints);
   trade.SetAsyncMode(false);
   if(!trade.SetTypeFillingBySymbol(_Symbol))
      Log("warning: unable to derive filling mode");

   if(InpUseRegimeGate)
   {
      g_atrHandle=iATR(_Symbol,InpAtrTimeframe,InpAtrPeriod);
      if(g_atrHandle==INVALID_HANDLE)
      {
         PrintFormat("%s: ATR handle failed lastError=%d",EA_TAG,GetLastError());
         return INIT_FAILED;
      }
   }

   Print(EA_TAG,": initialized with internally certified Coinexx server-time profiles");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_atrHandle!=INVALID_HANDLE)
   {
      IndicatorRelease(g_atrHandle);
      g_atrHandle=INVALID_HANDLE;
   }
   Log(StringFormat("deinit reason=%d",reason));
}

void OnTick()
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol,tick) || tick.bid<=0.0 || tick.ask<=0.0)
      return;
   Reconcile(tick);
}
