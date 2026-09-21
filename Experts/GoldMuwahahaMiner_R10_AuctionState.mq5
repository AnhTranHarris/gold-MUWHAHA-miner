#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "2.10"
#property strict
#property description "Gold MUWHAHA R10: causal R9 event population with strengthened auction-state routing, tight harvest lifecycle, and catastrophe memory."

#include <Trade/Trade.mqh>
CTrade trade;

enum ENUM_GMM_SESSION
{
   GMM_SESSION_OFF = 0,
   GMM_SESSION_LONDON = 1,
   GMM_SESSION_OVERLAP = 2,
   GMM_SESSION_NEWYORK = 3
};

enum ENUM_R10_ROUTER_PROFILE
{
   R10_ROUTER_BALANCED = 0,   // research knee: preserve net while reducing gross loss
   R10_ROUTER_DEFENSIVE = 1   // lower participation, lower gross-loss frontier
};

// -----------------------------------------------------------------------------
// R10 certification inputs
// Strategy geometry is intentionally internal so tester presets cannot silently
// mutate the research lineage. The only strategy profile choice exposed is the
// two validated transparent router frontiers.
// -----------------------------------------------------------------------------
input group "R10 certification execution"
input double                  InpLots             = 0.01;
input ulong                   InpMagic            = 5560;
input int                     InpDeviationPoints  = 20;
input ENUM_R10_ROUTER_PROFILE InpRouterProfile    = R10_ROUTER_BALANCED;
input bool                    InpRequireXAUUSD    = true;
input bool                    InpVerbose          = true;

input group "R10 R9-population eligibility"
input bool            InpUseRegimeGate     = true;
input ENUM_TIMEFRAMES InpAtrTimeframe      = PERIOD_M5;
input int             InpAtrPeriod         = 14;
input int             InpQuoteUtcOffsetMinutes = 0;
input bool            InpFailClosedOnNoATR = true;

input group "R10 broker normalization"
input double InpHunterPipPrice     = 0.01;
input bool   InpRespectBrokerStops = true;

string EA_TAG = "GM_R10_AUCTION_STATE";

// -----------------------------------------------------------------------------
// Frozen research geometry carried from the causal R9 event population.
// -----------------------------------------------------------------------------
const int    R10_EVENT_GAP_PIPS          = 30;
const int    R10_EVENT_VEL_LOOKBACK_SEC  = 10;
const int    R10_EVENT_MIN_VEL_PIPS      = 15;
const double R10_EVENT_MIN_EFF           = 0.70;
const int    R10_EVENT_RANGE_LOOKBACK_SEC= 10;
const int    R10_EVENT_MIN_RANGE_PIPS    = 50;
const int    R10_EVENT_MAX_TURNS         = 9;
const int    R10_MAX_SAME_MIN_REARMS     = 3;

const int    R10_MAX_SPREAD_POINTS       = 25;
const double R10_ATR_LONDON_PRICE        = 2.00;
const double R10_ATR_OVERLAP_PRICE       = 1.75;
const double R10_ATR_NEWYORK_PRICE       = 1.75;
const double R10_ATR_OFFSESSION_PRICE    = 2.50;

// Wide emergency room + near-immediate favorable-excursion harvest.
// At 0.01 lot on standard XAUUSD contract sizing this was the research geometry
// behind the low-catastrophe lifecycle screens. Broker minimum stop distance is
// still respected when it is wider than the requested harvest trail.
const double R10_EMERGENCY_STOP_PRICE    = 5.00;
const double R10_HARVEST_ACTIVATION_PRICE= 0.01;
const double R10_HARVEST_TRAIL_PRICE     = 0.01;
const int    R10_MAX_HOLD_SECONDS        = 120;

// Same-direction memory after a genuine emergency-stop loss.
const int    R10_CATASTROPHE_MEMORY_SEC  = 10;

#define MICRO_CAPACITY 256
struct MicroBar
{
   datetime second;
   double open;
   double high;
   double low;
   double close;
   int ticks;
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
int g_bucketTicks=0;

datetime g_cycleMinute=0;
double g_cycleBuy=0.0;
double g_cycleSell=0.0;
int g_pendingMode=0; // 2 both R9 event directions, 1 buy event, -1 sell event, 0 none
int g_rearms=0;

bool g_hadPosition=false;
ENUM_POSITION_TYPE g_lastPositionType=POSITION_TYPE_BUY;
int g_lastEventSide=0; // original boundary-event direction, not necessarily traded direction
datetime g_positionOpenedAt=0;
datetime g_tradeCycleMinute=0;
bool g_tradeHarvestArmed=false;
double g_tradeMFE=0.0;
double g_tradeMAE=0.0;

int g_catastropheBlockedSide=0;
datetime g_catastropheBlockedUntil=0;

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

bool IsExpectedSymbol()
{
   if(!InpRequireXAUUSD)
      return true;
   return (StringFind(_Symbol,"XAUUSD")>=0);
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
   if(session==GMM_SESSION_OVERLAP) return R10_ATR_OVERLAP_PRICE;
   if(session==GMM_SESSION_NEWYORK) return R10_ATR_NEWYORK_PRICE;
   if(session==GMM_SESSION_LONDON) return R10_ATR_LONDON_PRICE;
   return R10_ATR_OFFSESSION_PRICE;
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
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(point<=0.0 || tick.ask<=0.0 || tick.bid<=0.0)
      return false;

   const double spreadPoints=(tick.ask-tick.bid)/point;
   if(R10_MAX_SPREAD_POINTS>0 && spreadPoints>(double)R10_MAX_SPREAD_POINTS+1e-9)
      return false;

   if(!InpUseRegimeGate)
      return true;

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

void PushCompletedSecond(const datetime sec,const double o,const double h,const double l,const double c,const int ticks)
{
   g_micro[g_microHead].second=sec;
   g_micro[g_microHead].open=o;
   g_micro[g_microHead].high=h;
   g_micro[g_microHead].low=l;
   g_micro[g_microHead].close=c;
   g_micro[g_microHead].ticks=ticks;
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
      g_bucketTicks=1;
      return;
   }

   if(sec!=g_bucketSecond)
   {
      PushCompletedSecond(g_bucketSecond,g_bucketOpen,g_bucketHigh,g_bucketLow,g_bucketClose,g_bucketTicks);
      g_bucketSecond=sec;
      g_bucketOpen=tick.bid;
      g_bucketHigh=tick.bid;
      g_bucketLow=tick.bid;
      g_bucketClose=tick.bid;
      g_bucketTicks=1;
      return;
   }

   if(tick.bid>g_bucketHigh) g_bucketHigh=tick.bid;
   if(tick.bid<g_bucketLow) g_bucketLow=tick.bid;
   g_bucketClose=tick.bid;
   g_bucketTicks++;
}

bool R9EventQualityForSide(const int side,double &disp,double &eff,double &recentRange,int &turns)
{
   disp=0.0; eff=0.0; recentRange=0.0; turns=0;
   const int need=MathMax(R10_EVENT_VEL_LOOKBACK_SEC,R10_EVENT_RANGE_LOOKBACK_SEC)+1;
   if(g_microCount<need)
      return false;

   const int oldest=RingIndexFromNewest(R10_EVENT_VEL_LOOKBACK_SEC-1);
   double previous=g_micro[oldest].close;
   const double start=previous;
   double travel=0.0;
   double previousSign=0.0;

   for(int offset=R10_EVENT_VEL_LOOKBACK_SEC-2;offset>=0;--offset)
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
   for(int offset=0;offset<R10_EVENT_RANGE_LOOKBACK_SEC;++offset)
   {
      const int idx=RingIndexFromNewest(offset);
      if(g_micro[idx].high>hi) hi=g_micro[idx].high;
      if(g_micro[idx].low<lo) lo=g_micro[idx].low;
   }
   recentRange=hi-lo;

   if(eff+1e-12<R10_EVENT_MIN_EFF) return false;
   if(turns>R10_EVENT_MAX_TURNS) return false;
   if(recentRange+1e-12<HunterDistance(R10_EVENT_MIN_RANGE_PIPS)) return false;

   const double minVelocity=HunterDistance(R10_EVENT_MIN_VEL_PIPS);
   if(side>0 && disp+1e-12<minVelocity) return false;
   if(side<0 && disp-1e-12>-minVelocity) return false;
   return true;
}

void RouterThresholds(double &continueMaxAligned,double &fadeMinAligned)
{
   if(InpRouterProfile==R10_ROUTER_DEFENSIVE)
   {
      continueMaxAligned=-0.290;
      fadeMinAligned=0.310;
      return;
   }

   // Balanced-strengthened research frontier.
   continueMaxAligned=-0.255;
   fadeMinAligned=0.275;
}

int RouteAuctionEvent(const int eventSide,double &alignedRet1,double &range1,int &ticks1,string &state)
{
   alignedRet1=0.0;
   range1=0.0;
   ticks1=0;
   state="ABSTAIN";

   if(g_microCount<1)
      return 0;

   const int idx=RingIndexFromNewest(0);
   const MicroBar bar=g_micro[idx];
   alignedRet1=(bar.close-bar.open)*(double)eventSide;
   range1=bar.high-bar.low;
   ticks1=bar.ticks;

   double continueMaxAligned=0.0;
   double fadeMinAligned=0.0;
   RouterThresholds(continueMaxAligned,fadeMinAligned);

   // Pullback against a still-valid ten-second break: continue the original event.
   if(alignedRet1<=continueMaxAligned && range1+1e-12>=0.285)
   {
      state="CONTINUE";
      return eventSide;
   }

   // Late/chased impulse exhaustion: fade the original event.
   if(alignedRet1>=fadeMinAligned && ticks1>=5)
   {
      state="FADE";
      return -eventSide;
   }

   return 0;
}

bool CatastropheMemoryAllows(const int tradeSide,const datetime now)
{
   if(g_catastropheBlockedSide==0 || now>=g_catastropheBlockedUntil)
      return true;
   return (tradeSide!=g_catastropheBlockedSide);
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

bool OpenTrade(const int tradeSide,const int eventSide,const string routerState,const MqlTick &tick,
               const double alignedRet1,const double range1,const int ticks1)
{
   const double volume=NormalizeVolume(InpLots);
   const double brokerMinimum=InpRespectBrokerStops?BrokerStopsDistance()+TickSize():0.0;
   const double stopDistance=MathMax(R10_EMERGENCY_STOP_PRICE,brokerMinimum);
   double sl=0.0;
   bool sent=false;

   ResetLastError();
   if(tradeSide>0)
   {
      sl=NormalizePrice(tick.bid-stopDistance);
      sent=trade.Buy(volume,_Symbol,0.0,sl,0.0,EA_TAG+" "+routerState);
   }
   else
   {
      sl=NormalizePrice(tick.ask+stopDistance);
      sent=trade.Sell(volume,_Symbol,0.0,sl,0.0,EA_TAG+" "+routerState);
   }

   if(!sent || !ResultAccepted())
   {
      LogTradeFailure(tradeSide>0?"BUY":"SELL");
      return false;
   }

   g_positionOpenedAt=tick.time;
   g_tradeCycleMinute=g_cycleMinute;
   g_lastEventSide=eventSide;
   g_lastPositionType=(tradeSide>0?POSITION_TYPE_BUY:POSITION_TYPE_SELL);
   g_pendingMode=0;
   g_tradeHarvestArmed=false;
   g_tradeMFE=0.0;
   g_tradeMAE=0.0;

   if(InpVerbose)
      PrintFormat("%s: ENTRY state=%s eventSide=%d tradeSide=%d ret1=%.3f range1=%.3f ticks1=%d stop=%.2f act=%.2f trail=%.2f",
                  EA_TAG,routerState,eventSide,tradeSide,alignedRet1,range1,ticks1,
                  R10_EMERGENCY_STOP_PRICE,R10_HARVEST_ACTIVATION_PRICE,R10_HARVEST_TRAIL_PRICE);
   return true;
}

void UpdateExcursion(const MqlTick &tick,const ENUM_POSITION_TYPE type,const double openPrice)
{
   double favorable=0.0;
   double adverse=0.0;
   if(type==POSITION_TYPE_BUY)
   {
      favorable=tick.bid-openPrice;
      adverse=openPrice-tick.bid;
   }
   else
   {
      favorable=openPrice-tick.ask;
      adverse=tick.ask-openPrice;
   }
   if(favorable>g_tradeMFE) g_tradeMFE=favorable;
   if(adverse>g_tradeMAE) g_tradeMAE=adverse;
}

void ManagePosition(const MqlTick &tick,const ulong ticket,const ENUM_POSITION_TYPE type,const double openPrice,const double currentSL)
{
   UpdateExcursion(tick,type,openPrice);

   if(g_positionOpenedAt>0 && (tick.time-g_positionOpenedAt)>=R10_MAX_HOLD_SECONDS)
   {
      ResetLastError();
      if(!trade.PositionClose(ticket) || !ResultAccepted())
         LogTradeFailure("max-hold close");
      return;
   }

   const double brokerDistance=InpRespectBrokerStops?BrokerStopsDistance():0.0;
   const double tickSize=TickSize();
   double candidate=0.0;

   if(type==POSITION_TYPE_BUY)
   {
      if((tick.bid-openPrice)+1e-12<R10_HARVEST_ACTIVATION_PRICE)
         return;
      g_tradeHarvestArmed=true;
      candidate=NormalizePrice(tick.bid-R10_HARVEST_TRAIL_PRICE);
      candidate=MathMin(candidate,NormalizePrice(tick.bid-brokerDistance-tickSize));
      if(candidate<=0.0 || candidate<=currentSL+tickSize*0.5)
         return;
   }
   else
   {
      if((openPrice-tick.ask)+1e-12<R10_HARVEST_ACTIVATION_PRICE)
         return;
      g_tradeHarvestArmed=true;
      candidate=NormalizePrice(tick.ask+R10_HARVEST_TRAIL_PRICE);
      candidate=MathMax(candidate,NormalizePrice(tick.ask+brokerDistance+tickSize));
      if(candidate<=0.0 || (currentSL>0.0 && candidate>=currentSL-tickSize*0.5))
         return;
   }

   ResetLastError();
   if(!trade.PositionModify(ticket,candidate,0.0) || !ResultAccepted())
      LogTradeFailure("harvest trail modify");
}

void StartMinuteCycle(const MqlTick &tick)
{
   const datetime minute=(datetime)((long)tick.time-((long)tick.time%60));
   if(minute==g_cycleMinute)
      return;

   g_cycleMinute=minute;
   g_rearms=0;
   g_pendingMode=2;

   const double mid=(tick.ask+tick.bid)*0.5;
   const double half=HunterDistance(R10_EVENT_GAP_PIPS)*0.5;
   g_cycleBuy=NormalizePrice(mid+half);
   g_cycleSell=NormalizePrice(mid-half);
}

void ArmOppositeEventAfterExit()
{
   if(g_rearms>=R10_MAX_SAME_MIN_REARMS || g_lastEventSide==0)
   {
      g_pendingMode=0;
      return;
   }
   g_rearms++;
   g_pendingMode=-g_lastEventSide;
}

void ProcessEntries(const MqlTick &tick)
{
   if(g_pendingMode==0)
      return;
   if(!GateAllowsEntry(tick))
      return;

   int eventSide=0;
   if((g_pendingMode==2 || g_pendingMode==1) && tick.ask>=g_cycleBuy)
      eventSide=1;
   else if((g_pendingMode==2 || g_pendingMode==-1) && tick.bid<=g_cycleSell)
      eventSide=-1;
   if(eventSide==0)
      return;

   double disp10=0.0,eff10=0.0,range10=0.0;
   int turns10=0;
   if(!R9EventQualityForSide(eventSide,disp10,eff10,range10,turns10))
      return;

   double alignedRet1=0.0,range1=0.0;
   int ticks1=0;
   string routerState="ABSTAIN";
   const int tradeSide=RouteAuctionEvent(eventSide,alignedRet1,range1,ticks1,routerState);
   if(tradeSide==0)
   {
      if(InpVerbose)
         PrintFormat("%s: ABSTAIN eventSide=%d ret1=%.3f range1=%.3f ticks1=%d disp10=%.3f eff10=%.3f range10=%.3f turns10=%d",
                     EA_TAG,eventSide,alignedRet1,range1,ticks1,disp10,eff10,range10,turns10);
      // The same boundary crossing is not repeatedly reconsidered on every tick.
      // It remains an observed event, but no trade is forced from the ambiguous state.
      g_pendingMode=0;
      return;
   }

   if(!CatastropheMemoryAllows(tradeSide,tick.time))
   {
      if(InpVerbose)
         PrintFormat("%s: catastrophe memory BLOCK state=%s eventSide=%d tradeSide=%d until=%s",
                     EA_TAG,routerState,eventSide,tradeSide,
                     TimeToString(g_catastropheBlockedUntil,TIME_DATE|TIME_SECONDS));
      // Consume this event but keep the opposite boundary eligible. The blocked
      // event is not allowed to become a stale delayed entry when memory expires.
      g_pendingMode=-eventSide;
      return;
   }

   OpenTrade(tradeSide,eventSide,routerState,tick,alignedRet1,range1,ticks1);
}

void Reconcile(const MqlTick &tick)
{
   UpdateSecondBucket(tick);

   ulong ticket=0;
   ENUM_POSITION_TYPE type=POSITION_TYPE_BUY;
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
      // Preserve the just-closed trade's harvest/MFE/MAE state until the next
      // entry. TradeTransaction delivery ordering is not guaranteed by MT5.

      const datetime nowMinute=(datetime)((long)tick.time-((long)tick.time%60));
      if(nowMinute==g_tradeCycleMinute && nowMinute==g_cycleMinute)
         ArmOppositeEventAfterExit();
      else
      {
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
   if(InpLots<=0.0 || InpHunterPipPrice<=0.0 || InpAtrPeriod<=0 || InpDeviationPoints<0)
   {
      Print(EA_TAG,": invalid inputs");
      return INIT_PARAMETERS_INCORRECT;
   }

   if(!IsExpectedSymbol())
   {
      PrintFormat("%s: symbol guard rejected %s; R10 is XAUUSD-only",EA_TAG,_Symbol);
      return INIT_FAILED;
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

   double cont=0.0,fade=0.0;
   RouterThresholds(cont,fade);
   PrintFormat("%s initialized profile=%d CONT<=%.3f FADE>=%.3f range1>=0.285 fadeTicks>=5 emergency=%.2f activation=%.2f trail=%.2f memory=%ds",
               EA_TAG,(int)InpRouterProfile,cont,fade,R10_EMERGENCY_STOP_PRICE,
               R10_HARVEST_ACTIVATION_PRICE,R10_HARVEST_TRAIL_PRICE,R10_CATASTROPHE_MEMORY_SEC);
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

void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   if(trans.type!=TRADE_TRANSACTION_DEAL_ADD || trans.deal==0)
      return;
   if(!HistoryDealSelect(trans.deal))
      return;

   const string symbol=HistoryDealGetString(trans.deal,DEAL_SYMBOL);
   const ulong magic=(ulong)HistoryDealGetInteger(trans.deal,DEAL_MAGIC);
   if(symbol!=_Symbol || magic!=InpMagic)
      return;

   const ENUM_DEAL_ENTRY entry=(ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal,DEAL_ENTRY);
   if(entry!=DEAL_ENTRY_OUT && entry!=DEAL_ENTRY_OUT_BY)
      return;

   const ENUM_DEAL_REASON reason=(ENUM_DEAL_REASON)HistoryDealGetInteger(trans.deal,DEAL_REASON);
   const double profit=HistoryDealGetDouble(trans.deal,DEAL_PROFIT);

   // Catastrophe memory is intentionally narrow: only an unharvested losing SL
   // blocks the same traded direction. Opposite-direction auctions remain eligible.
   if(reason==DEAL_REASON_SL && profit<0.0 && !g_tradeHarvestArmed)
   {
      g_catastropheBlockedSide=(g_lastPositionType==POSITION_TYPE_BUY?1:-1);
      const datetime dealTime=(datetime)HistoryDealGetInteger(trans.deal,DEAL_TIME);
      g_catastropheBlockedUntil=dealTime+R10_CATASTROPHE_MEMORY_SEC;
      if(InpVerbose)
         PrintFormat("%s: CATASTROPHE side=%d profit=%.2f blockUntil=%s MFE=%.3f MAE=%.3f",
                     EA_TAG,g_catastropheBlockedSide,profit,
                     TimeToString(g_catastropheBlockedUntil,TIME_DATE|TIME_SECONDS),
                     g_tradeMFE,g_tradeMAE);
   }
}
