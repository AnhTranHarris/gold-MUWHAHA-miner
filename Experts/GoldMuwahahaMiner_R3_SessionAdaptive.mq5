#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "1.50"
#property strict
#property description "Gold MUWHAHA R3: R2 regime gate plus DST-aware London/New York adaptive ATR thresholds."

#include <Trade/Trade.mqh>

CTrade trade;

enum ENUM_GMM_SESSION
{
   GMM_SESSION_OFF = 0,
   GMM_SESSION_LONDON = 1,
   GMM_SESSION_OVERLAP = 2,
   GMM_SESSION_NEWYORK = 3
};

input group "R3 geometry"
input double InpLots                = 0.01;
input int    InpGapPips             = 100;
input int    InpStopLossPips        = 50;
input bool   InpTrailingEnabled     = true;
input int    InpTrailPips           = 15;
input int    InpTrailActivationPips = 15;
input ulong  InpMagic               = 5555;

input group "R3 regime gate"
input bool            InpUseRegimeGate     = true;
input ENUM_TIMEFRAMES InpAtrTimeframe      = PERIOD_M5;
input int             InpAtrPeriod         = 14;
input int             InpMaxSpreadPoints   = 25;
input bool            InpFailClosedOnNoATR = true;

input group "R3 session-adaptive ATR"
input bool   InpUseSessionAdaptiveAtr = true;
input int    InpQuoteUtcOffsetMinutes = 0;
input double InpAtrLondonPrice        = 2.00;
input double InpAtrOverlapPrice       = 1.75;
input double InpAtrNewYorkPrice       = 1.75;
input double InpAtrOffSessionPrice    = 2.50;

input group "Price normalization"
input double InpHunterPipPrice       = 0.01;
input bool   InpRespectBrokerStops   = true;

input group "Unresolved V8 input"
input bool   InpUseDailyProfitTarget = false;
input double InpDailyProfitTarget    = 100.0;

input group "Execution"
input int    InpDeviationPoints      = 20;
input bool   InpVerbose              = true;

string EA_TAG = "GM_R3_SESSION";

bool               g_reconcileBusy    = false;
bool               g_wasInPosition    = false;
ENUM_POSITION_TYPE g_lastPositionType = POSITION_TYPE_BUY;

datetime g_cycleBar       = 0;
double   g_cycleBuyPrice  = 0.0;
double   g_cycleSellPrice = 0.0;

int      g_atrHandle      = INVALID_HANDLE;
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
               EA_TAG,
               action,
               trade.ResultRetcode(),
               trade.ResultRetcodeDescription(),
               GetLastError());
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
   value.year = year;
   value.mon = month;
   value.day = day;
   value.hour = 12;
   const datetime stamp = StructToTime(value);
   MqlDateTime result = {};
   if(!TimeToStruct(stamp, result))
      return -1;
   return result.day_of_week;
}

int NthSunday(const int year, const int month, const int nth)
{
   const int firstDow = DayOfWeekUtc(year, month, 1);
   if(firstDow < 0)
      return 0;
   const int firstSunday = 1 + ((7 - firstDow) % 7);
   return firstSunday + (nth - 1) * 7;
}

int LastSunday(const int year, const int month)
{
   const int lastDay = DaysInMonth(year, month);
   const int dow = DayOfWeekUtc(year, month, lastDay);
   if(dow < 0)
      return 0;
   return lastDay - dow;
}

datetime MakeUtc(const int year,
                 const int month,
                 const int day,
                 const int hour,
                 const int minute = 0)
{
   MqlDateTime value = {};
   value.year = year;
   value.mon = month;
   value.day = day;
   value.hour = hour;
   value.min = minute;
   return StructToTime(value);
}

bool IsLondonDstUtc(const datetime utc)
{
   MqlDateTime now = {};
   if(!TimeToStruct(utc, now))
      return false;

   const int startDay = LastSunday(now.year, 3);
   const int endDay   = LastSunday(now.year, 10);
   const datetime start = MakeUtc(now.year, 3, startDay, 1, 0);
   const datetime end   = MakeUtc(now.year, 10, endDay, 1, 0);
   return (utc >= start && utc < end);
}

bool IsNewYorkDstUtc(const datetime utc)
{
   MqlDateTime now = {};
   if(!TimeToStruct(utc, now))
      return false;

   const int startDay = NthSunday(now.year, 3, 2);
   const int endDay   = NthSunday(now.year, 11, 1);
   const datetime start = MakeUtc(now.year, 3, startDay, 7, 0);
   const datetime end   = MakeUtc(now.year, 11, endDay, 6, 0);
   return (utc >= start && utc < end);
}

int LocalMinuteOfDay(const datetime utc, const int offsetMinutes)
{
   const datetime local = utc + (datetime)(offsetMinutes * 60);
   MqlDateTime value = {};
   if(!TimeToStruct(local, value))
      return -1;
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

   if(london && newYork)
      return GMM_SESSION_OVERLAP;
   if(london)
      return GMM_SESSION_LONDON;
   if(newYork)
      return GMM_SESSION_NEWYORK;
   return GMM_SESSION_OFF;
}

string SessionName(const ENUM_GMM_SESSION session)
{
   if(session == GMM_SESSION_LONDON)
      return "LONDON";
   if(session == GMM_SESSION_OVERLAP)
      return "OVERLAP";
   if(session == GMM_SESSION_NEWYORK)
      return "NEWYORK";
   return "OFF";
}

double SessionAtrMinimum(const ENUM_GMM_SESSION session)
{
   if(!InpUseSessionAdaptiveAtr)
      return InpAtrLondonPrice;
   if(session == GMM_SESSION_OVERLAP)
      return InpAtrOverlapPrice;
   if(session == GMM_SESSION_NEWYORK)
      return InpAtrNewYorkPrice;
   if(session == GMM_SESSION_LONDON)
      return InpAtrLondonPrice;
   return InpAtrOffSessionPrice;
}

bool GetCompletedAtr(double &atrValue)
{
   atrValue = 0.0;

   if(!InpUseRegimeGate)
      return true;
   if(g_atrHandle == INVALID_HANDLE)
      return false;
   if(BarsCalculated(g_atrHandle) < InpAtrPeriod + 2)
      return false;

   double buffer[1];
   ResetLastError();
   const int copied = CopyBuffer(g_atrHandle, 0, 1, 1, buffer);
   if(copied != 1 || !MathIsValidNumber(buffer[0]) || buffer[0] <= 0.0)
      return false;

   atrValue = buffer[0];
   return true;
}

bool GateAllowsEntry()
{
   if(!InpUseRegimeGate)
      return true;

   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick) || tick.ask <= 0.0 || tick.bid <= 0.0)
      return false;

   const double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   if(point <= 0.0)
      return false;

   const double spreadPoints = (tick.ask - tick.bid) / point;
   if(InpMaxSpreadPoints > 0 && spreadPoints > (double)InpMaxSpreadPoints + 1e-9)
      return false;

   double atrValue = 0.0;
   const bool haveAtr = GetCompletedAtr(atrValue);
   if(!haveAtr)
      return !InpFailClosedOnNoATR;

   const ENUM_GMM_SESSION session = CurrentSession();
   const double minimumAtr = SessionAtrMinimum(session);

   if(minimumAtr > 0.0 && atrValue + 1e-12 < minimumAtr)
   {
      const datetime bar = iTime(_Symbol, PERIOD_M1, 0);
      if(InpVerbose && bar != g_lastGateLogBar)
      {
         PrintFormat("%s: gate CLOSED session=%s ATR=%.5f minimum=%.5f spread=%.1f",
                     EA_TAG,
                     SessionName(session),
                     atrValue,
                     minimumAtr,
                     spreadPoints);
         g_lastGateLogBar = bar;
      }
      return false;
   }

   return true;
}

bool IsOurPendingSelected()
{
   if(OrderGetString(ORDER_SYMBOL) != _Symbol)
      return false;
   if((ulong)OrderGetInteger(ORDER_MAGIC) != InpMagic)
      return false;

   const ENUM_ORDER_TYPE type = (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE);
   return (type == ORDER_TYPE_BUY_STOP || type == ORDER_TYPE_SELL_STOP);
}

void FindOurPending(ulong &buyTicket, ulong &sellTicket)
{
   buyTicket = 0;
   sellTicket = 0;

   for(int index = OrdersTotal() - 1; index >= 0; --index)
   {
      const ulong ticket = OrderGetTicket(index);
      if(ticket == 0 || !IsOurPendingSelected())
         continue;

      const ENUM_ORDER_TYPE type = (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE);
      if(type == ORDER_TYPE_BUY_STOP && buyTicket == 0)
         buyTicket = ticket;
      else if(type == ORDER_TYPE_SELL_STOP && sellTicket == 0)
         sellTicket = ticket;
   }
}

bool FindOurPosition(ulong &ticket,
                     ENUM_POSITION_TYPE &type,
                     double &openPrice,
                     double &stopLoss)
{
   ticket = 0;
   openPrice = 0.0;
   stopLoss = 0.0;
   type = POSITION_TYPE_BUY;

   for(int index = PositionsTotal() - 1; index >= 0; --index)
   {
      const ulong currentTicket = PositionGetTicket(index);
      if(currentTicket == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;

      ticket = currentTicket;
      type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      stopLoss = PositionGetDouble(POSITION_SL);
      return true;
   }

   return false;
}

bool DeletePending(const ulong ticket)
{
   if(ticket == 0)
      return true;

   ResetLastError();
   if(!trade.OrderDelete(ticket) || !ResultAccepted())
   {
      LogTradeFailure(StringFormat("OrderDelete #%I64u", ticket));
      return false;
   }
   return true;
}

void DeleteAllOurPending()
{
   ulong buyTicket, sellTicket;
   FindOurPending(buyTicket, sellTicket);
   if(buyTicket != 0)
      DeletePending(buyTicket);
   if(sellTicket != 0)
      DeletePending(sellTicket);
}

double ClosedProfitToday()
{
   MqlDateTime now = {};
   TimeToStruct(TimeCurrent(), now);
   now.hour = 0;
   now.min = 0;
   now.sec = 0;

   const datetime dayStart = StructToTime(now);
   if(!HistorySelect(dayStart, TimeCurrent()))
      return 0.0;

   double total = 0.0;
   const int count = HistoryDealsTotal();
   for(int index = 0; index < count; ++index)
   {
      const ulong deal = HistoryDealGetTicket(index);
      if(deal == 0)
         continue;
      if(HistoryDealGetString(deal, DEAL_SYMBOL) != _Symbol)
         continue;
      if((ulong)HistoryDealGetInteger(deal, DEAL_MAGIC) != InpMagic)
         continue;
      if((ENUM_DEAL_ENTRY)HistoryDealGetInteger(deal, DEAL_ENTRY) != DEAL_ENTRY_OUT)
         continue;

      total += HistoryDealGetDouble(deal, DEAL_PROFIT);
      total += HistoryDealGetDouble(deal, DEAL_SWAP);
      total += HistoryDealGetDouble(deal, DEAL_COMMISSION);
   }
   return total;
}

bool DailyTargetReached()
{
   return (InpUseDailyProfitTarget &&
           InpDailyProfitTarget > 0.0 &&
           ClosedProfitToday() >= InpDailyProfitTarget);
}

bool PlaceBuyStopAtCycleBoundary()
{
   if(g_cycleBuyPrice <= 0.0 || g_cycleSellPrice <= 0.0 || !GateAllowsEntry())
      return false;

   const double volume = NormalizeVolume(InpLots);
   const double stopDistance = HunterDistance(InpStopLossPips);
   const double sl = NormalizePrice(g_cycleBuyPrice - stopDistance);

   ResetLastError();
   const bool sent = trade.BuyStop(volume,
                                   g_cycleBuyPrice,
                                   _Symbol,
                                   sl,
                                   0.0,
                                   ORDER_TIME_GTC,
                                   0,
                                   EA_TAG + " BUY");
   if(!sent || !ResultAccepted())
   {
      LogTradeFailure("re-arm BuyStop");
      return false;
   }
   return true;
}

bool PlaceSellStopAtCycleBoundary()
{
   if(g_cycleBuyPrice <= 0.0 || g_cycleSellPrice <= 0.0 || !GateAllowsEntry())
      return false;

   const double volume = NormalizeVolume(InpLots);
   const double stopDistance = HunterDistance(InpStopLossPips);
   const double sl = NormalizePrice(g_cycleSellPrice + stopDistance);

   ResetLastError();
   const bool sent = trade.SellStop(volume,
                                    g_cycleSellPrice,
                                    _Symbol,
                                    sl,
                                    0.0,
                                    ORDER_TIME_GTC,
                                    0,
                                    EA_TAG + " SELL");
   if(!sent || !ResultAccepted())
   {
      LogTradeFailure("re-arm SellStop");
      return false;
   }
   return true;
}

bool PlaceFreshMinuteBracket(const datetime barTime)
{
   if(!GateAllowsEntry())
      return false;

   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick) || tick.ask <= 0.0 || tick.bid <= 0.0)
      return false;

   if(DailyTargetReached())
      return false;

   const double requestedBand = HunterDistance(InpGapPips);
   if(requestedBand <= 0.0)
      return false;

   double center = (tick.ask + tick.bid) * 0.5;
   double halfBand = requestedBand * 0.5;

   if(InpRespectBrokerStops)
   {
      const double minimumDistance = BrokerStopsDistance() + TickSize();
      const double buyNeed  = (tick.ask - center) + minimumDistance;
      const double sellNeed = (center - tick.bid) + minimumDistance;
      halfBand = MathMax(halfBand, MathMax(buyNeed, sellNeed));
   }

   const double buyPrice  = NormalizePrice(center + halfBand);
   const double sellPrice = NormalizePrice(center - halfBand);
   const double stopDistance = HunterDistance(InpStopLossPips);
   const double buySL  = NormalizePrice(buyPrice - stopDistance);
   const double sellSL = NormalizePrice(sellPrice + stopDistance);
   const double volume = NormalizeVolume(InpLots);

   if(buyPrice <= tick.ask || sellPrice >= tick.bid || volume <= 0.0)
      return false;

   ResetLastError();
   const bool buySent = trade.BuyStop(volume,
                                      buyPrice,
                                      _Symbol,
                                      buySL,
                                      0.0,
                                      ORDER_TIME_GTC,
                                      0,
                                      EA_TAG + " BUY");
   if(!buySent || !ResultAccepted())
   {
      LogTradeFailure("fresh BuyStop");
      return false;
   }
   const ulong buyTicket = trade.ResultOrder();

   ResetLastError();
   const bool sellSent = trade.SellStop(volume,
                                        sellPrice,
                                        _Symbol,
                                        sellSL,
                                        0.0,
                                        ORDER_TIME_GTC,
                                        0,
                                        EA_TAG + " SELL");
   if(!sellSent || !ResultAccepted())
   {
      LogTradeFailure("fresh SellStop");
      DeletePending(buyTicket);
      return false;
   }

   g_cycleBuyPrice = buyPrice;
   g_cycleSellPrice = sellPrice;
   return true;
}

void ManageTrailing(const ulong positionTicket,
                    const ENUM_POSITION_TYPE type,
                    const double openPrice,
                    const double currentSL)
{
   if(!InpTrailingEnabled || InpTrailPips <= 0)
      return;

   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick))
      return;

   const double trailDistance = HunterDistance(InpTrailPips);
   const int activationPips = (InpTrailActivationPips < 0 ? 0 : InpTrailActivationPips);
   const double activationDistance = HunterDistance(activationPips);
   const double brokerDistance = (InpRespectBrokerStops ? BrokerStopsDistance() : 0.0);
   const double tickSize = TickSize();
   double candidate = 0.0;

   if(type == POSITION_TYPE_BUY)
   {
      if((tick.bid - openPrice) < activationDistance)
         return;
      candidate = NormalizePrice(tick.bid - trailDistance);
      const double brokerMaximum = NormalizePrice(tick.bid - brokerDistance - tickSize);
      candidate = MathMin(candidate, brokerMaximum);
      if(candidate <= 0.0 || candidate <= currentSL + tickSize * 0.5)
         return;
   }
   else if(type == POSITION_TYPE_SELL)
   {
      if((openPrice - tick.ask) < activationDistance)
         return;
      candidate = NormalizePrice(tick.ask + trailDistance);
      const double brokerMinimum = NormalizePrice(tick.ask + brokerDistance + tickSize);
      candidate = MathMax(candidate, brokerMinimum);
      if(candidate <= 0.0 || (currentSL > 0.0 && candidate >= currentSL - tickSize * 0.5))
         return;
   }
   else
      return;

   ResetLastError();
   if(!trade.PositionModify(positionTicket, candidate, 0.0) || !ResultAccepted())
      LogTradeFailure(StringFormat("PositionModify #%I64u", positionTicket));
}

void Reconcile()
{
   if(g_reconcileBusy)
      return;
   g_reconcileBusy = true;

   const datetime currentBar = iTime(_Symbol, PERIOD_M1, 0);

   ulong positionTicket;
   ENUM_POSITION_TYPE positionType;
   double openPrice, currentSL;
   const bool havePosition = FindOurPosition(positionTicket,
                                             positionType,
                                             openPrice,
                                             currentSL);

   ulong buyTicket, sellTicket;
   FindOurPending(buyTicket, sellTicket);

   if(havePosition)
   {
      g_wasInPosition = true;
      g_lastPositionType = positionType;

      if(positionType == POSITION_TYPE_BUY && sellTicket != 0)
         DeletePending(sellTicket);
      else if(positionType == POSITION_TYPE_SELL && buyTicket != 0)
         DeletePending(buyTicket);

      ManageTrailing(positionTicket, positionType, openPrice, currentSL);
      g_reconcileBusy = false;
      return;
   }

   if(DailyTargetReached())
   {
      DeleteAllOurPending();
      g_reconcileBusy = false;
      return;
   }

   if(g_wasInPosition)
   {
      g_wasInPosition = false;
      FindOurPending(buyTicket, sellTicket);

      if(currentBar == g_cycleBar && g_cycleBuyPrice > 0.0 && g_cycleSellPrice > 0.0)
      {
         if(buyTicket != 0)
            DeletePending(buyTicket);
         if(sellTicket != 0)
            DeletePending(sellTicket);

         if(g_lastPositionType == POSITION_TYPE_SELL)
            PlaceBuyStopAtCycleBoundary();
         else
            PlaceSellStopAtCycleBoundary();

         g_reconcileBusy = false;
         return;
      }
   }

   FindOurPending(buyTicket, sellTicket);

   if(currentBar != 0 && currentBar != g_cycleBar)
   {
      DeleteAllOurPending();
      g_cycleBar = currentBar;
      g_cycleBuyPrice = 0.0;
      g_cycleSellPrice = 0.0;
      PlaceFreshMinuteBracket(currentBar);
      g_reconcileBusy = false;
      return;
   }

   g_reconcileBusy = false;
}

int OnInit()
{
   if(InpLots <= 0.0 ||
      InpGapPips <= 0 ||
      InpStopLossPips <= 0 ||
      InpHunterPipPrice <= 0.0 ||
      InpAtrPeriod <= 0 ||
      InpMaxSpreadPoints < 0 ||
      InpAtrLondonPrice < 0.0 ||
      InpAtrOverlapPrice < 0.0 ||
      InpAtrNewYorkPrice < 0.0 ||
      InpAtrOffSessionPrice < 0.0)
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

   PrintFormat("%s initialized on %s; gap=%d trail=%d spread<=%d UTC-offset=%d",
               EA_TAG,
               _Symbol,
               InpGapPips,
               InpTrailPips,
               InpMaxSpreadPoints,
               InpQuoteUtcOffsetMinutes);

   Reconcile();
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
   Reconcile();
}

void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   if(trans.symbol == _Symbol || request.symbol == _Symbol)
      Reconcile();
}
