#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "0.20"
#property strict
#property description "Gold Hunter V8-style XAUUSD M1 breakout / reversal-rearm / trailing baseline."

#include <Trade/Trade.mqh>

CTrade trade;

input group "Observed V8 fingerprint"
input double InpLots                = 0.01;
input int    InpGapPips             = 50;
input int    InpStopLossPips        = 50;
input bool   InpTrailingEnabled     = true;
input int    InpTrailPips           = 20;
input int    InpTrailActivationPips = 20;
input ulong  InpMagic               = 5555;

input group "Price normalization"
input double InpHunterPipPrice      = 0.01;  // reference XAUUSD report: 50 -> $0.50
input bool   InpRespectBrokerStops  = true;

input group "Unresolved V8 input"
input bool   InpUseDailyProfitTarget = false; // strict $100/day contradicts reference report
input double InpDailyProfitTarget    = 100.0;

input group "Execution"
input int    InpDeviationPoints     = 20;
input bool   InpVerbose             = true;

string EA_TAG = "GM_V8_BASE";

bool               g_reconcileBusy   = false;
bool               g_wasInPosition   = false;
ENUM_POSITION_TYPE g_lastPositionType = POSITION_TYPE_BUY;

datetime g_cycleBar       = 0;
double   g_cycleBuyPrice  = 0.0;
double   g_cycleSellPrice = 0.0;

//+------------------------------------------------------------------+
//| Logging / normalization                                           |
//+------------------------------------------------------------------+
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

//+------------------------------------------------------------------+
//| Order / position discovery                                        |
//+------------------------------------------------------------------+
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

//+------------------------------------------------------------------+
//| Optional daily target                                             |
//+------------------------------------------------------------------+
double ClosedProfitToday()
{
   MqlDateTime now;
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

//+------------------------------------------------------------------+
//| Pending-order placement                                           |
//+------------------------------------------------------------------+
bool PlaceBuyStopAtCycleBoundary()
{
   if(g_cycleBuyPrice <= 0.0 || g_cycleSellPrice <= 0.0)
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

   Log(StringFormat("re-armed BUY %.2f SL %.2f", g_cycleBuyPrice, sl));
   return true;
}

bool PlaceSellStopAtCycleBoundary()
{
   if(g_cycleBuyPrice <= 0.0 || g_cycleSellPrice <= 0.0)
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

   Log(StringFormat("re-armed SELL %.2f SL %.2f", g_cycleSellPrice, sl));
   return true;
}

bool PlaceFreshMinuteBracket(const datetime barTime)
{
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
   {
      PrintFormat("%s: invalid fresh bracket bid=%.5f ask=%.5f buy=%.5f sell=%.5f",
                  EA_TAG, tick.bid, tick.ask, buyPrice, sellPrice);
      return false;
   }

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

   g_cycleBar = barTime;
   g_cycleBuyPrice = buyPrice;
   g_cycleSellPrice = sellPrice;

   Log(StringFormat("new M1 bracket BUY %.2f / SELL %.2f / width %.2f",
                    buyPrice,
                    sellPrice,
                    buyPrice - sellPrice));
   return true;
}

//+------------------------------------------------------------------+
//| Trailing                                                          |
//+------------------------------------------------------------------+
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

//+------------------------------------------------------------------+
//| V8 state machine                                                  |
//+------------------------------------------------------------------+
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

      // Observed V8 fingerprint: once one side fills, the opposite pending
      // order is canceled immediately.
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

   // Observed V8 fingerprint: after a position exits inside the same M1 bar,
   // only the opposite boundary is re-armed at the original minute price.
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

   // Every new M1 bar resets the old one-sided reversal order and creates a
   // fresh symmetric bracket. This exact pattern is visible in the report.
   if(currentBar != 0 && currentBar != g_cycleBar)
   {
      DeleteAllOurPending();
      PlaceFreshMinuteBracket(currentBar);
      g_reconcileBusy = false;
      return;
   }

   // Mid-bar startup/recovery: if state was lost, reconstruct a safe fresh
   // bracket rather than guessing which reversal leg V8 was on.
   if(buyTicket == 0 && sellTicket == 0)
      PlaceFreshMinuteBracket(currentBar);

   g_reconcileBusy = false;
}

//+------------------------------------------------------------------+
//| Expert lifecycle                                                  |
//+------------------------------------------------------------------+
int OnInit()
{
   if(InpLots <= 0.0 ||
      InpGapPips <= 0 ||
      InpStopLossPips <= 0 ||
      InpHunterPipPrice <= 0.0)
   {
      Print(EA_TAG, ": invalid inputs");
      return INIT_PARAMETERS_INCORRECT;
   }

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPoints);
   trade.SetAsyncMode(false);

   if(!trade.SetTypeFillingBySymbol(_Symbol))
      Log("warning: unable to derive symbol filling mode");

   PrintFormat("%s initialized on %s; point=%g tick=%g stops=%d freeze=%d",
               EA_TAG,
               _Symbol,
               SymbolInfoDouble(_Symbol, SYMBOL_POINT),
               TickSize(),
               (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL),
               (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL));

   Reconcile();
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
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
   // MetaQuotes explicitly warns that trade-transaction arrival order is not
   // guaranteed. Treat this only as a wake-up signal and rebuild truth from
   // current terminal orders/positions in Reconcile().
   if(trans.symbol == _Symbol || request.symbol == _Symbol)
      Reconcile();
}
