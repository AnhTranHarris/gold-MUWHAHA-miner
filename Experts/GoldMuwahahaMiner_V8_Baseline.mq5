#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "0.10"
#property strict
#property description "Gold Hunter V8-style XAUUSD M1 breakout/trailing baseline."

#include <Trade/Trade.mqh>

CTrade trade;

input group "V8 fingerprint"
input double InpLots                  = 0.01;
input int    InpGapPips               = 50;
input int    InpStopLossPips          = 50;
input bool   InpTrailingEnabled       = true;
input int    InpTrailPips             = 20;
input int    InpTrailActivationPips   = 20;
input ulong  InpMagic                 = 5555;

input group "Price normalization"
input double InpHunterPipPrice        = 0.01;   // 50 -> $0.50 on XAUUSD in the reference report
input bool   InpGapIsTotalBandWidth   = true;   // observed first buy/sell stop separation was $0.50
input bool   InpRespectBrokerStops    = true;

input group "Behavior switches"
input bool   InpCancelOppositeOnFill  = true;
input bool   InpRearmImmediately      = true;
input bool   InpRefreshOnNewM1Bar     = false;  // unknown V8 behavior; keep false for baseline fingerprint
input bool   InpUseDailyProfitTarget  = false;  // report exposed 100, but strict $100/day is inconsistent with results
input double InpDailyProfitTarget     = 100.0;

input group "Execution"
input int    InpDeviationPoints       = 20;
input bool   InpVerbose               = true;

string   EA_TAG = "GM_V8_BASE";
datetime g_lastM1Bar = 0;
double   g_cycleCenter = 0.0;
bool     g_reconcileBusy = false;

//+------------------------------------------------------------------+
//| Helpers                                                          |
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
   double v = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(v <= 0.0)
      v = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   return v;
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
   const double vmin  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   const double vmax  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   const double vstep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   double volume = MathMax(vmin, MathMin(vmax, requested));
   if(vstep > 0.0)
      volume = vmin + MathRound((volume - vmin) / vstep) * vstep;

   return NormalizeDouble(MathMax(vmin, MathMin(vmax, volume)), 8);
}

double HunterDistance(const int pips)
{
   return ((double)pips) * InpHunterPipPrice;
}

double BrokerStopsDistance()
{
   const long stops = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   return ((double)MathMax((long)0, stops)) * SymbolInfoDouble(_Symbol, SYMBOL_POINT);
}

bool ResultAccepted()
{
   const uint rc = trade.ResultRetcode();
   return (rc == TRADE_RETCODE_DONE ||
           rc == TRADE_RETCODE_PLACED ||
           rc == TRADE_RETCODE_DONE_PARTIAL ||
           rc == TRADE_RETCODE_NO_CHANGES);
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

bool IsOurPendingOrderSelected()
{
   if(OrderGetString(ORDER_SYMBOL) != _Symbol)
      return false;
   if((ulong)OrderGetInteger(ORDER_MAGIC) != InpMagic)
      return false;

   const ENUM_ORDER_TYPE type = (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE);
   return (type == ORDER_TYPE_BUY_STOP || type == ORDER_TYPE_SELL_STOP);
}

bool FindOurPending(ulong &buyTicket, ulong &sellTicket)
{
   buyTicket = 0;
   sellTicket = 0;

   for(int i = OrdersTotal() - 1; i >= 0; --i)
   {
      const ulong ticket = OrderGetTicket(i);
      if(ticket == 0 || !IsOurPendingOrderSelected())
         continue;

      const ENUM_ORDER_TYPE type = (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE);
      if(type == ORDER_TYPE_BUY_STOP && buyTicket == 0)
         buyTicket = ticket;
      else if(type == ORDER_TYPE_SELL_STOP && sellTicket == 0)
         sellTicket = ticket;
   }
   return (buyTicket != 0 || sellTicket != 0);
}

bool FindOurPosition(ulong &ticket, ENUM_POSITION_TYPE &type, double &openPrice, double &sl)
{
   ticket = 0;
   openPrice = 0.0;
   sl = 0.0;
   type = POSITION_TYPE_BUY;

   for(int i = PositionsTotal() - 1; i >= 0; --i)
   {
      const ulong t = PositionGetTicket(i);
      if(t == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;

      ticket = t;
      type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      sl = PositionGetDouble(POSITION_SL);
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
//| Daily target (optional research switch)                          |
//+------------------------------------------------------------------+
double ClosedProfitToday()
{
   MqlDateTime nowStruct;
   TimeToStruct(TimeCurrent(), nowStruct);
   nowStruct.hour = 0;
   nowStruct.min = 0;
   nowStruct.sec = 0;
   const datetime dayStart = StructToTime(nowStruct);

   if(!HistorySelect(dayStart, TimeCurrent()))
      return 0.0;

   double total = 0.0;
   const int deals = HistoryDealsTotal();
   for(int i = 0; i < deals; ++i)
   {
      const ulong deal = HistoryDealGetTicket(i);
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
   return (InpUseDailyProfitTarget && InpDailyProfitTarget > 0.0 &&
           ClosedProfitToday() >= InpDailyProfitTarget);
}

//+------------------------------------------------------------------+
//| Build the observed stop-entry bracket                            |
//+------------------------------------------------------------------+
bool PlaceFreshBracket()
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick) || tick.ask <= 0.0 || tick.bid <= 0.0)
      return false;

   if(DailyTargetReached())
   {
      DeleteAllOurPending();
      return false;
   }

   double band = HunterDistance(InpGapPips);
   if(band <= 0.0)
      return false;

   double half = (InpGapIsTotalBandWidth ? band * 0.5 : band);
   double center = (tick.ask + tick.bid) * 0.5;

   if(InpRespectBrokerStops)
   {
      const double minDist = BrokerStopsDistance() + TickSize();
      const double requiredHalfBuy  = (tick.ask - center) + minDist;
      const double requiredHalfSell = (center - tick.bid) + minDist;
      half = MathMax(half, MathMax(requiredHalfBuy, requiredHalfSell));
   }

   const double buyPrice  = NormalizePrice(center + half);
   const double sellPrice = NormalizePrice(center - half);

   // The reference report's first bracket showed each initial stop at the
   // opposite trigger. If StopLossPips differs from GapPips, honor the input.
   const double stopDist = HunterDistance(InpStopLossPips);
   const double buySL  = NormalizePrice(buyPrice  - stopDist);
   const double sellSL = NormalizePrice(sellPrice + stopDist);
   const double volume = NormalizeVolume(InpLots);

   if(buyPrice <= tick.ask || sellPrice >= tick.bid || volume <= 0.0)
   {
      PrintFormat("%s: invalid bracket bid=%.5f ask=%.5f buy=%.5f sell=%.5f",
                  EA_TAG, tick.bid, tick.ask, buyPrice, sellPrice);
      return false;
   }

   ResetLastError();
   const bool buySent = trade.BuyStop(volume, buyPrice, _Symbol, buySL, 0.0,
                                      ORDER_TIME_GTC, 0, EA_TAG + " BUY");
   if(!buySent || !ResultAccepted())
   {
      LogTradeFailure("BuyStop");
      return false;
   }
   const ulong buyTicket = trade.ResultOrder();

   ResetLastError();
   const bool sellSent = trade.SellStop(volume, sellPrice, _Symbol, sellSL, 0.0,
                                        ORDER_TIME_GTC, 0, EA_TAG + " SELL");
   if(!sellSent || !ResultAccepted())
   {
      LogTradeFailure("SellStop");
      DeletePending(buyTicket);
      return false;
   }

   g_cycleCenter = center;
   Log(StringFormat("armed buy %.2f / sell %.2f / buySL %.2f / sellSL %.2f",
                    buyPrice, sellPrice, buySL, sellSL));
   return true;
}

//+------------------------------------------------------------------+
//| Trailing                                                         |
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

   const double trailDist = HunterDistance(InpTrailPips);
   const double activationDist = HunterDistance(MathMax(InpTrailActivationPips, 0));
   const double minDist = (InpRespectBrokerStops ? BrokerStopsDistance() : 0.0);
   const double tickSize = TickSize();
   double candidate = 0.0;

   if(type == POSITION_TYPE_BUY)
   {
      if((tick.bid - openPrice) < activationDist)
         return;
      candidate = NormalizePrice(tick.bid - trailDist);
      const double maxAllowed = NormalizePrice(tick.bid - minDist - tickSize);
      candidate = MathMin(candidate, maxAllowed);
      if(candidate <= 0.0 || candidate <= currentSL + tickSize * 0.5)
         return;
   }
   else if(type == POSITION_TYPE_SELL)
   {
      if((openPrice - tick.ask) < activationDist)
         return;
      candidate = NormalizePrice(tick.ask + trailDist);
      const double minAllowed = NormalizePrice(tick.ask + minDist + tickSize);
      candidate = MathMax(candidate, minAllowed);
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
//| State reconciliation                                              |
//+------------------------------------------------------------------+
void Reconcile()
{
   if(g_reconcileBusy)
      return;
   g_reconcileBusy = true;

   ulong positionTicket;
   ENUM_POSITION_TYPE positionType;
   double openPrice, currentSL;
   const bool havePosition = FindOurPosition(positionTicket, positionType, openPrice, currentSL);

   ulong buyTicket, sellTicket;
   FindOurPending(buyTicket, sellTicket);

   if(havePosition)
   {
      if(InpCancelOppositeOnFill)
      {
         if(positionType == POSITION_TYPE_BUY && sellTicket != 0)
            DeletePending(sellTicket);
         else if(positionType == POSITION_TYPE_SELL && buyTicket != 0)
            DeletePending(buyTicket);
      }
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

   // A one-sided orphan is not a valid OCO bracket. Rebuild atomically.
   if((buyTicket == 0) != (sellTicket == 0))
   {
      if(buyTicket != 0)
         DeletePending(buyTicket);
      if(sellTicket != 0)
         DeletePending(sellTicket);
      buyTicket = 0;
      sellTicket = 0;
   }

   if(buyTicket == 0 && sellTicket == 0 && InpRearmImmediately)
      PlaceFreshBracket();

   g_reconcileBusy = false;
}

//+------------------------------------------------------------------+
//| Expert lifecycle                                                  |
//+------------------------------------------------------------------+
int OnInit()
{
   if(InpLots <= 0.0 || InpGapPips <= 0 || InpStopLossPips <= 0 || InpHunterPipPrice <= 0.0)
   {
      Print(EA_TAG, ": invalid inputs");
      return INIT_PARAMETERS_INCORRECT;
   }

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPoints);
   trade.SetAsyncMode(false);
   if(!trade.SetTypeFillingBySymbol(_Symbol))
      Log("warning: unable to derive symbol filling mode");

   g_lastM1Bar = iTime(_Symbol, PERIOD_M1, 0);

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
   if(InpRefreshOnNewM1Bar)
   {
      const datetime bar = iTime(_Symbol, PERIOD_M1, 0);
      if(bar != 0 && bar != g_lastM1Bar)
      {
         g_lastM1Bar = bar;

         ulong positionTicket;
         ENUM_POSITION_TYPE positionType;
         double openPrice, currentSL;
         if(!FindOurPosition(positionTicket, positionType, openPrice, currentSL))
            DeleteAllOurPending();
      }
   }

   Reconcile();
}

void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   // MetaQuotes documents that transaction arrival order is not guaranteed.
   // We therefore treat this handler as a wake-up signal and reconstruct the
   // current state from terminal orders/positions instead of trusting sequence.
   if(trans.symbol == _Symbol || request.symbol == _Symbol)
      Reconcile();
}
