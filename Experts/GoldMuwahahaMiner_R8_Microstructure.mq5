#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "1.80"
#property strict
#property description "Gold MUWHAHA R8: R5 strategic regime context plus tick-native S1 liquidity-break / sweep-reclaim execution."

#include <Trade/Trade.mqh>
CTrade trade;

enum ENUM_GMM_SESSION
{
   GMM_SESSION_OFF = 0,
   GMM_SESSION_LONDON = 1,
   GMM_SESSION_OVERLAP = 2,
   GMM_SESSION_NEWYORK = 3
};

enum ENUM_MICRO_STATE
{
   MICRO_IDLE = 0,
   MICRO_UPPER_BREAK = 1,
   MICRO_LOWER_BREAK = -1,
   MICRO_UPPER_RECLAIM = 2,
   MICRO_LOWER_RECLAIM = -2
};

input group "R8 execution geometry"
input double InpLots                   = 0.01;
input int    InpStopLossPips           = 300;
input bool   InpTrailingEnabled        = true;
input int    InpTrailPips              = 5;
input int    InpTrailActivationPips    = 18;
input int    InpMaxHoldSeconds         = 60;
input int    InpCooldownSeconds        = 1;
input int    InpMaxTradesPerMinute     = 5;
input ulong  InpMagic                  = 5555;

input group "R8 microstructure"
input int    InpLiquidityLookbackSec   = 20;
input int    InpVelocityLookbackSec    = 5;
input int    InpStatePersistenceSec    = 2;
input int    InpStateExpirySec         = 20;
input int    InpBreakBufferPips        = 10;
input int    InpReclaimPips            = 15;
input int    InpConfirmBufferPips      = 8;
input int    InpMinVelocityPips        = 15;
input double InpMinDirectionalEff      = 0.30;

input group "R8 strategic regime gate"
input bool            InpUseRegimeGate     = true;
input ENUM_TIMEFRAMES InpAtrTimeframe      = PERIOD_M5;
input int             InpAtrPeriod         = 14;
input int             InpMaxSpreadPoints   = 25;
input bool            InpFailClosedOnNoATR = true;

input group "R8 session-adaptive ATR"
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

string EA_TAG = "GM_R8_MICRO";

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
int      g_microHead  = 0;
int      g_microCount = 0;

bool     g_bucketReady = false;
datetime g_bucketSecond = 0;
double   g_bucketOpen = 0.0;
double   g_bucketHigh = 0.0;
double   g_bucketLow = 0.0;
double   g_bucketClose = 0.0;

ENUM_MICRO_STATE g_microState = MICRO_IDLE;
double   g_stateLevel = 0.0;
datetime g_stateStarted = 0;
datetime g_cooldownUntil = 0;

datetime g_tradeMinute = 0;
int      g_tradesThisMinute = 0;

bool     g_hadPosition = false;
datetime g_positionOpenedAt = 0;

int      g_atrHandle = INVALID_HANDLE;
datetime g_lastGateLogBar = 0;

void Log(const string text)
{
   if(InpVerbose)
      Print(EA_TAG, ": ", text);
}

int DigitsForSymbol()
{
   return (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
}

double TickSize()
{
   double value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(value <= 0.0)
      value = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   return value;
}

double NormalizePrice(const double price)
{
   const double tick = TickSize();
   if(tick <= 0.0)
      return NormalizeDouble(price, DigitsForSymbol());
   return NormalizeDouble(MathRound(price / tick) * tick, DigitsForSymbol());
}

double NormalizeVolume(const double requested)
{
   const double minimum = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   const double maximum = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   const double step    = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double volume = MathMax(minimum, MathMin(maximum, requested));
   if(step > 0.0)
      volume = minimum + MathRound((volume - minimum) / step) * step;
   return NormalizeDouble(MathMax(minimum, MathMin(maximum, volume)), 8);
}

double HunterDistance(const int pips)
{
   return (double)pips * InpHunterPipPrice;
}

double BrokerStopsDistance()
{
   const long stops = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   const double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   return (double)MathMax((long)0, stops) * point;
}

bool ResultAccepted()
{
   const uint code = trade.ResultRetcode();
   return (code == TRADE_RETCODE_DONE ||
           code == TRADE_RETCODE_PLACED ||
           code == TRADE_RETCODE_DONE_PARTIAL ||
           code == TRADE_RETCODE_NO_CHANGES);
}

void LogTradeFailure(const string action)
{
   PrintFormat("%s: %s failed; retcode=%u (%s), lastError=%d",
               EA_TAG, action, trade.ResultRetcode(),
               trade.ResultRetcodeDescription(), GetLastError());
}

int DaysInMonth(const int year, const int month)
{
   if(month == 2)
   {
      const bool leap = ((year % 400) == 0 || ((year % 4) == 0 && (year % 100) != 0));
      return leap ? 29 : 28;
   }
   if(month == 4 || month == 6 || month == 9 || month == 11)
      return 30;
   return 31;
}

int DayOfWeekUtc(const int year, const int month, const int day)
{
   MqlDateTime value = {};
   value.year = year; value.mon = month; value.day = day; value.hour = 12;
   const datetime stamp = StructToTime(value);
   MqlDateTime result = {};
   if(!TimeToStruct(stamp, result)) return -1;
   return result.day_of_week;
}

int NthSunday(const int year, const int month, const int nth)
{
   const int firstDow = DayOfWeekUtc(year, month, 1);
   if(firstDow < 0) return 0;
   const int firstSunday = 1 + ((7 - firstDow) % 7);
   return firstSunday + (nth - 1) * 7;
}

int LastSunday(const int year, const int month)
{
   const int lastDay = DaysInMonth(year, month);
   const int dow = DayOfWeekUtc(year, month, lastDay);
   if(dow < 0) return 0;
   return lastDay - dow;
}

datetime MakeUtc(const int year, const int month, const int day, const int hour, const int minute = 0)
{
   MqlDateTime value = {};
   value.year = year; value.mon = month; value.day = day; value.hour = hour; value.min = minute;
   return StructToTime(value);
}

bool IsLondonDstUtc(const datetime utc)
{
   MqlDateTime now = {};
   if(!TimeToStruct(utc, now)) return false;
   const datetime start = MakeUtc(now.year, 3, LastSunday(now.year, 3), 1, 0);
   const datetime end   = MakeUtc(now.year, 10, LastSunday(now.year, 10), 1, 0);
   return (utc >= start && utc < end);
}

bool IsNewYorkDstUtc(const datetime utc)
{
   MqlDateTime now = {};
   if(!TimeToStruct(utc, now)) return false;
   const datetime start = MakeUtc(now.year, 3, NthSunday(now.year, 3, 2), 7, 0);
   const datetime end   = MakeUtc(now.year, 11, NthSunday(now.year, 11, 1), 6, 0);
   return (utc >= start && utc < end);
}

int LocalMinuteOfDay(const datetime utc, const int offsetMinutes)
{
   const datetime local = utc + (datetime)(offsetMinutes * 60);
   MqlDateTime value = {};
   if(!TimeToStruct(local, value)) return -1;
   return value.hour * 60 + value.min;
}

ENUM_GMM_SESSION CurrentSession()
{
   const datetime quoteTime = TimeCurrent();
   const datetime utc = quoteTime - (datetime)(InpQuoteUtcOffsetMinutes * 60);
   const int londonOffset = IsLondonDstUtc(utc) ? 60 : 0;
   const int nyOffset = IsNewYorkDstUtc(utc) ? -240 : -300;
   const int londonMinute = LocalMinuteOfDay(utc, londonOffset);
   const int nyMinute = LocalMinuteOfDay(utc, nyOffset);
   const bool london = (londonMinute >= 8 * 60 && londonMinute < 16 * 60 + 30);
   const bool newYork = (nyMinute >= 8 * 60 && nyMinute < 17 * 60);
   if(london && newYork) return GMM_SESSION_OVERLAP;
   if(london) return GMM_SESSION_LONDON;
   if(newYork) return GMM_SESSION_NEWYORK;
   return GMM_SESSION_OFF;
}

double SessionAtrMinimum(const ENUM_GMM_SESSION session)
{
   if(!InpUseSessionAdaptiveAtr) return InpAtrLondonPrice;
   if(session == GMM_SESSION_OVERLAP) return InpAtrOverlapPrice;
   if(session == GMM_SESSION_NEWYORK) return InpAtrNewYorkPrice;
   if(session == GMM_SESSION_LONDON) return InpAtrLondonPrice;
   return InpAtrOffSessionPrice;
}

bool GetCompletedAtr(double &atrValue)
{
   atrValue = 0.0;
   if(!InpUseRegimeGate) return true;
   if(g_atrHandle == INVALID_HANDLE) return false;
   if(BarsCalculated(g_atrHandle) < InpAtrPeriod + 2) return false;
   double buffer[1];
   ResetLastError();
   const int copied = CopyBuffer(g_atrHandle, 0, 1, 1, buffer);
   if(copied != 1 || !MathIsValidNumber(buffer[0]) || buffer[0] <= 0.0) return false;
   atrValue = buffer[0];
   return true;
}

bool GateAllowsEntry(const MqlTick &tick)
{
   if(!InpUseRegimeGate) return true;
   const double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   if(point <= 0.0 || tick.ask <= 0.0 || tick.bid <= 0.0) return false;
   const double spreadPoints = (tick.ask - tick.bid) / point;
   if(InpMaxSpreadPoints > 0 && spreadPoints > (double)InpMaxSpreadPoints + 1e-9) return false;
   double atrValue = 0.0;
   const bool haveAtr = GetCompletedAtr(atrValue);
   if(!haveAtr) return !InpFailClosedOnNoATR;
   const ENUM_GMM_SESSION session = CurrentSession();
   const double minimumAtr = SessionAtrMinimum(session);
   if(minimumAtr > 0.0 && atrValue + 1e-12 < minimumAtr)
   {
      const datetime bar = iTime(_Symbol, PERIOD_M1, 0);
      if(InpVerbose && bar != g_lastGateLogBar)
      {
         PrintFormat("%s: gate CLOSED ATR=%.5f minimum=%.5f spread=%.1f",
                     EA_TAG, atrValue, minimumAtr, spreadPoints);
         g_lastGateLogBar = bar;
      }
      return false;
   }
   return true;
}

void PushCompletedSecond(const datetime second, const double o, const double h, const double l, const double c)
{
   g_micro[g_microHead].second = second;
   g_micro[g_microHead].open = o;
   g_micro[g_microHead].high = h;
   g_micro[g_microHead].low = l;
   g_micro[g_microHead].close = c;
   g_microHead = (g_microHead + 1) % MICRO_CAPACITY;
   if(g_microCount < MICRO_CAPACITY) g_microCount++;
}

int RingIndexFromNewest(const int offset)
{
   int idx = g_microHead - 1 - offset;
   while(idx < 0) idx += MICRO_CAPACITY;
   return idx % MICRO_CAPACITY;
}

void UpdateSecondBucket(const MqlTick &tick)
{
   const datetime sec = tick.time;
   if(!g_bucketReady)
   {
      g_bucketReady = true;
      g_bucketSecond = sec;
      g_bucketOpen = tick.bid;
      g_bucketHigh = tick.bid;
      g_bucketLow = tick.bid;
      g_bucketClose = tick.bid;
      return;
   }
   if(sec != g_bucketSecond)
   {
      PushCompletedSecond(g_bucketSecond, g_bucketOpen, g_bucketHigh, g_bucketLow, g_bucketClose);
      g_bucketSecond = sec;
      g_bucketOpen = tick.bid;
      g_bucketHigh = tick.bid;
      g_bucketLow = tick.bid;
      g_bucketClose = tick.bid;
      return;
   }
   if(tick.bid > g_bucketHigh) g_bucketHigh = tick.bid;
   if(tick.bid < g_bucketLow) g_bucketLow = tick.bid;
   g_bucketClose = tick.bid;
}

bool RollingLiquidity(double &upper, double &lower)
{
   upper = 0.0; lower = 0.0;
   if(g_microCount < InpLiquidityLookbackSec) return false;
   upper = -DBL_MAX;
   lower = DBL_MAX;
   for(int i = 0; i < InpLiquidityLookbackSec; ++i)
   {
      const int idx = RingIndexFromNewest(i);
      if(g_micro[idx].high > upper) upper = g_micro[idx].high;
      if(g_micro[idx].low < lower) lower = g_micro[idx].low;
   }
   return (upper > 0.0 && lower < DBL_MAX);
}

bool MicroVelocity(const double currentBid, double &displacement, double &efficiency)
{
   displacement = 0.0; efficiency = 0.0;
   if(g_microCount < InpVelocityLookbackSec) return false;
   const int oldestIdx = RingIndexFromNewest(InpVelocityLookbackSec - 1);
   double previous = g_micro[oldestIdx].close;
   const double start = previous;
   double travel = 0.0;
   for(int offset = InpVelocityLookbackSec - 2; offset >= 0; --offset)
   {
      const int idx = RingIndexFromNewest(offset);
      const double value = g_micro[idx].close;
      travel += MathAbs(value - previous);
      previous = value;
   }
   travel += MathAbs(currentBid - previous);
   displacement = currentBid - start;
   efficiency = MathAbs(displacement) / (travel + 1e-9);
   return true;
}

bool FindOurPosition(ulong &ticket, ENUM_POSITION_TYPE &type, double &openPrice, double &stopLoss)
{
   ticket = 0; openPrice = 0.0; stopLoss = 0.0; type = POSITION_TYPE_BUY;
   for(int index = PositionsTotal() - 1; index >= 0; --index)
   {
      const ulong currentTicket = PositionGetTicket(index);
      if(currentTicket == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      ticket = currentTicket;
      type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      stopLoss = PositionGetDouble(POSITION_SL);
      return true;
   }
   return false;
}

void ManagePosition(const MqlTick &tick,
                    const ulong ticket,
                    const ENUM_POSITION_TYPE type,
                    const double openPrice,
                    const double currentSL)
{
   if(g_positionOpenedAt > 0 && (tick.time - g_positionOpenedAt) >= InpMaxHoldSeconds)
   {
      ResetLastError();
      if(!trade.PositionClose(ticket) || !ResultAccepted())
         LogTradeFailure(StringFormat("max-hold close #%I64u", ticket));
      return;
   }
   if(!InpTrailingEnabled || InpTrailPips <= 0) return;
   const double trailDistance = HunterDistance(InpTrailPips);
   const double activation = HunterDistance(MathMax(0, InpTrailActivationPips));
   const double brokerDistance = InpRespectBrokerStops ? BrokerStopsDistance() : 0.0;
   const double tickSize = TickSize();
   double candidate = 0.0;
   if(type == POSITION_TYPE_BUY)
   {
      if((tick.bid - openPrice) < activation) return;
      candidate = NormalizePrice(tick.bid - trailDistance);
      const double brokerMaximum = NormalizePrice(tick.bid - brokerDistance - tickSize);
      candidate = MathMin(candidate, brokerMaximum);
      if(candidate <= 0.0 || candidate <= currentSL + tickSize * 0.5) return;
   }
   else
   {
      if((openPrice - tick.ask) < activation) return;
      candidate = NormalizePrice(tick.ask + trailDistance);
      const double brokerMinimum = NormalizePrice(tick.ask + brokerDistance + tickSize);
      candidate = MathMax(candidate, brokerMinimum);
      if(candidate <= 0.0 || (currentSL > 0.0 && candidate >= currentSL - tickSize * 0.5)) return;
   }
   ResetLastError();
   if(!trade.PositionModify(ticket, candidate, 0.0) || !ResultAccepted())
      LogTradeFailure(StringFormat("trail modify #%I64u", ticket));
}

bool OpenMicroTrade(const int side, const MqlTick &tick, const string reason)
{
   if(side != 1 && side != -1) return false;
   const double volume = NormalizeVolume(InpLots);
   const double stopDistance = HunterDistance(InpStopLossPips);
   const double brokerMin = InpRespectBrokerStops ? BrokerStopsDistance() + TickSize() : 0.0;
   const double effectiveStop = MathMax(stopDistance, brokerMin);
   double sl = 0.0;
   bool sent = false;
   ResetLastError();
   if(side == 1)
   {
      sl = NormalizePrice(tick.bid - effectiveStop);
      sent = trade.Buy(volume, _Symbol, 0.0, sl, 0.0, EA_TAG + " " + reason);
   }
   else
   {
      sl = NormalizePrice(tick.ask + effectiveStop);
      sent = trade.Sell(volume, _Symbol, 0.0, sl, 0.0, EA_TAG + " " + reason);
   }
   if(!sent || !ResultAccepted())
   {
      LogTradeFailure(side == 1 ? "micro BUY" : "micro SELL");
      return false;
   }
   g_positionOpenedAt = tick.time;
   g_tradesThisMinute++;
   g_microState = MICRO_IDLE;
   g_stateLevel = 0.0;
   g_stateStarted = 0;
   if(InpVerbose)
      PrintFormat("%s: %s entry reason=%s tradesThisMinute=%d",
                  EA_TAG, side == 1 ? "BUY" : "SELL", reason, g_tradesThisMinute);
   return true;
}

void UpdateMinuteCounter(const datetime now)
{
   const datetime minute = (datetime)((long)now - ((long)now % 60));
   if(minute != g_tradeMinute)
   {
      g_tradeMinute = minute;
      g_tradesThisMinute = 0;
      g_microState = MICRO_IDLE;
      g_stateLevel = 0.0;
      g_stateStarted = 0;
   }
}

void ProcessMicroSignal(const MqlTick &tick)
{
   if(tick.time < g_cooldownUntil) return;
   if(g_tradesThisMinute >= InpMaxTradesPerMinute) return;
   if(!GateAllowsEntry(tick)) return;

   double upper = 0.0, lower = 0.0;
   if(!RollingLiquidity(upper, lower)) return;

   double displacement = 0.0, efficiency = 0.0;
   if(!MicroVelocity(tick.bid, displacement, efficiency)) return;

   const double breakBuffer = HunterDistance(InpBreakBufferPips);
   const double reclaim = HunterDistance(InpReclaimPips);
   const double confirm = HunterDistance(InpConfirmBufferPips);
   const double minVelocity = HunterDistance(InpMinVelocityPips);

   if(g_microState == MICRO_IDLE)
   {
      if(tick.ask >= upper + breakBuffer)
      {
         g_microState = MICRO_UPPER_BREAK;
         g_stateLevel = upper;
         g_stateStarted = tick.time;
      }
      else if(tick.bid <= lower - breakBuffer)
      {
         g_microState = MICRO_LOWER_BREAK;
         g_stateLevel = lower;
         g_stateStarted = tick.time;
      }
   }

   if(g_microState == MICRO_UPPER_BREAK)
   {
      if(tick.ask <= g_stateLevel - reclaim)
      {
         g_microState = MICRO_UPPER_RECLAIM;
         g_stateStarted = tick.time;
      }
      else if((tick.time - g_stateStarted) >= InpStatePersistenceSec &&
              tick.ask >= g_stateLevel + confirm &&
              displacement >= minVelocity &&
              efficiency >= InpMinDirectionalEff)
      {
         OpenMicroTrade(1, tick, "CONT_UP");
         return;
      }
   }
   else if(g_microState == MICRO_LOWER_BREAK)
   {
      if(tick.bid >= g_stateLevel + reclaim)
      {
         g_microState = MICRO_LOWER_RECLAIM;
         g_stateStarted = tick.time;
      }
      else if((tick.time - g_stateStarted) >= InpStatePersistenceSec &&
              tick.bid <= g_stateLevel - confirm &&
              displacement <= -minVelocity &&
              efficiency >= InpMinDirectionalEff)
      {
         OpenMicroTrade(-1, tick, "CONT_DN");
         return;
      }
   }
   else if(g_microState == MICRO_UPPER_RECLAIM)
   {
      if(displacement <= -minVelocity && efficiency >= InpMinDirectionalEff)
      {
         OpenMicroTrade(-1, tick, "SWEEP_UP");
         return;
      }
   }
   else if(g_microState == MICRO_LOWER_RECLAIM)
   {
      if(displacement >= minVelocity && efficiency >= InpMinDirectionalEff)
      {
         OpenMicroTrade(1, tick, "SWEEP_DN");
         return;
      }
   }

   if(g_microState != MICRO_IDLE &&
      g_stateStarted > 0 &&
      (tick.time - g_stateStarted) > InpStateExpirySec)
   {
      g_microState = MICRO_IDLE;
      g_stateLevel = 0.0;
      g_stateStarted = 0;
   }
}

void Reconcile(const MqlTick &tick)
{
   UpdateMinuteCounter(tick.time);
   UpdateSecondBucket(tick);

   ulong positionTicket;
   ENUM_POSITION_TYPE positionType;
   double openPrice, currentSL;
   const bool havePosition = FindOurPosition(positionTicket, positionType, openPrice, currentSL);

   if(havePosition)
   {
      g_hadPosition = true;
      if(g_positionOpenedAt <= 0)
         g_positionOpenedAt = (datetime)PositionGetInteger(POSITION_TIME);
      ManagePosition(tick, positionTicket, positionType, openPrice, currentSL);
      return;
   }

   if(g_hadPosition)
   {
      g_hadPosition = false;
      g_positionOpenedAt = 0;
      g_cooldownUntil = tick.time + InpCooldownSeconds;
      g_microState = MICRO_IDLE;
      g_stateLevel = 0.0;
      g_stateStarted = 0;
      return;
   }

   ProcessMicroSignal(tick);
}

int OnInit()
{
   if(InpLots <= 0.0 || InpStopLossPips <= 0 || InpTrailPips < 0 ||
      InpTrailActivationPips < 0 || InpLiquidityLookbackSec < 5 ||
      InpLiquidityLookbackSec >= MICRO_CAPACITY || InpVelocityLookbackSec < 2 ||
      InpVelocityLookbackSec >= InpLiquidityLookbackSec ||
      InpStatePersistenceSec < 0 || InpStateExpirySec <= InpStatePersistenceSec ||
      InpBreakBufferPips < 0 || InpReclaimPips <= 0 || InpConfirmBufferPips < 0 ||
      InpMinVelocityPips <= 0 || InpMinDirectionalEff <= 0.0 || InpMinDirectionalEff > 1.0 ||
      InpMaxHoldSeconds <= 0 || InpCooldownSeconds < 0 || InpMaxTradesPerMinute <= 0 ||
      InpHunterPipPrice <= 0.0 || InpAtrPeriod <= 0 || InpMaxSpreadPoints < 0)
   {
      Print(EA_TAG, ": invalid inputs");
      return INIT_PARAMETERS_INCORRECT;
   }

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPoints);
   trade.SetAsyncMode(false);
   if(!trade.SetTypeFillingBySymbol(_Symbol))
      Log("warning: unable to derive symbol filling mode");

   if(InpUseRegimeGate)
   {
      g_atrHandle = iATR(_Symbol, InpAtrTimeframe, InpAtrPeriod);
      if(g_atrHandle == INVALID_HANDLE)
      {
         PrintFormat("%s: failed to create ATR handle; lastError=%d", EA_TAG, GetLastError());
         return INIT_FAILED;
      }
   }

   PrintFormat("%s initialized: S1 lookback=%d vel=%d stop=%d trail=%d activation=%d max/min=%d",
               EA_TAG, InpLiquidityLookbackSec, InpVelocityLookbackSec,
               InpStopLossPips, InpTrailPips, InpTrailActivationPips, InpMaxTradesPerMinute);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_atrHandle != INVALID_HANDLE)
   {
      IndicatorRelease(g_atrHandle);
      g_atrHandle = INVALID_HANDLE;
   }
   Log(StringFormat("deinit reason=%d", reason));
}

void OnTick()
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick) || tick.bid <= 0.0 || tick.ask <= 0.0)
      return;
   Reconcile(tick);
}

void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   // OnTick is intentionally the single state-machine driver.
}
