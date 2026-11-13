#property copyright "Clean-room behavioral reconstruction for AnhTranHarris"
#property version   "1.94"
#property strict
#property description "Gold MUWHAHA R9: R5-style minute bracket plus causal S1 momentum/efficiency quality gate."

#include <Trade/Trade.mqh>
CTrade trade;

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

input group "R9 account-wide gross loss governor (experimental defaults)"
input bool   InpR9GovEnabled                  = true;
input double InpR9GovBasePct                  = 4.0;
input double InpR9GovMaxPct                   = 12.0;
input double InpR9GovProfitRecycle            = 0.25;
input double InpR9GovPeakDrawdownPct          = 10.0;
input double InpR9GovMinMarginPct             = 150.0;
input double InpR9GovMinFreeEquityPct         = 10.0;
input double InpR9GovCashReservePerTrade      = 0.25;
input int    InpR9GovRefreshSeconds           = 5;
input bool   InpR9GovFlattenOwnOnHalt         = true;

input group "R9 Coinexx quote-only native M1 indicators"
input bool   InpR9CashGeometryShadow          = false;
input double InpR9TargetNetAccountCash        = 1.75;
input double InpR9AssumedRoundTripCostAccountCash = 0.20;
input group "M60 archived 155-feature LightGBM bridge"
input int    InpR9M60Mode                     = 1; // 0 off, 1 observational, 2 experimental filter
input bool   InpR9M60ExperimentalFilterUnlock = false; // deliberate owner-facing, NOT a performance certification
input string InpR9M60ExpectedModelSha         = "09e1f1b9514dd18bbf6966055e2c277da3695d43cd4c861f997f5ad2c5d75b2f";
input double InpR9M60MinProbability          = 0.0; // filter-only, not calibrated for trading
input bool   InpR9M1ShadowEnabled             = true;
input bool   InpR9M1RescueEnabled             = false; // OFF: requires source-exact replay
input int    InpR9M1ADXPeriod                 = 14;
input int    InpR9M1EMAPeriod                 = 20;
input int    InpR9M1ATRPeriod                 = 14;
input double InpR9M1MinADX                    = 18.0;
input double InpR9M1MinDIGap                  = 6.0;
input double InpR9M1RescueScore               = 0.82;

string EA_TAG = "GM_R9_HYBRID";

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
datetime g_r9LastTimeoutCloseSecond=0;
// R9_STANDALONE_BEGIN GoldMuwahahaR9PortfolioGovernor.mqh
#ifndef __GMM_R9_PORTFOLIO_GOVERNOR_MQH__
#define __GMM_R9_PORTFOLIO_GOVERNOR_MQH__
// v1.93 research module. Account-wide historical gross losses, NOT net losses.
// Config inputs are declared in the including EA. No tick tape files written.
// IMPORTANT: equity reference and lock persist in this terminal, NOT across terminals.

datetime g_r9GovDayStart=0;
datetime g_r9GovLastLedger=0;
bool     g_r9GovDirty=true;
bool     g_r9GovHealthy=false;
bool     g_r9GovLocked=false;
string   g_r9GovKey="";
double   g_r9GovDayEquity=0.0;
double   g_r9GovPeakEquity=0.0;
double   g_r9GovGrossLoss=0.0;
double   g_r9GovGrossProfit=0.0;
double   g_r9GovCashCharges=0.0;
double   g_r9GovFloatingLoss=0.0;
double   g_r9GovBudget=0.0;
datetime g_r9GovLastCloseRequest=0;

bool R9GovSet(const string key,const double value)
{
   return GlobalVariableSet(key,value)!=0;
}
bool R9GovInitDay(const datetime now)
{
   if(now<=0) return false;
   MqlDateTime t={};
   if(!TimeToStruct(now,t)) return false;
   t.hour=0;t.min=0;t.sec=0;
   const datetime start=StructToTime(t);
   if(start<=0) return false;
   if(start==g_r9GovDayStart) return (g_r9GovDayEquity>0.0 && g_r9GovPeakEquity>0.0 && g_r9GovKey!="");

   g_r9GovDayStart=start;
   g_r9GovKey=StringFormat("R9G.%I64d.%04d%02d%02d",
                          AccountInfoInteger(ACCOUNT_LOGIN),t.year,t.mon,t.day);
   const double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(!MathIsValidNumber(equity) || equity<=0.0) return false;
   if(!GlobalVariableCheck(g_r9GovKey+".base") &&
      !R9GovSet(g_r9GovKey+".base",equity)) return false;
   if(!GlobalVariableCheck(g_r9GovKey+".peak") &&
      !R9GovSet(g_r9GovKey+".peak",equity)) return false;
   g_r9GovDayEquity=GlobalVariableGet(g_r9GovKey+".base");
   g_r9GovPeakEquity=GlobalVariableGet(g_r9GovKey+".peak");
   if(g_r9GovDayEquity<=0.0 || g_r9GovPeakEquity<=0.0) return false;
   g_r9GovLocked=(GlobalVariableCheck(g_r9GovKey+".halt") &&
                  GlobalVariableGet(g_r9GovKey+".halt")>0.5);
   g_r9GovLastLedger=0;
   g_r9GovDirty=true;
   return true;
}
bool R9GovRefresh(const bool force=false)
{
   if(!InpR9GovEnabled) return true;
   const datetime now=TimeTradeServer();
   g_r9GovHealthy=false;
   if(!R9GovInitDay(now)) return false;

   const double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(!MathIsValidNumber(equity) || equity<=0.0) return false;
   if(GlobalVariableCheck(g_r9GovKey+".halt") &&
      GlobalVariableGet(g_r9GovKey+".halt")>0.5) g_r9GovLocked=true;
   // Peak is shared across EAs in the SAME TERMINAL and persists across restarts.
   const double sharedPeak=GlobalVariableGet(g_r9GovKey+".peak");
   if(sharedPeak>g_r9GovPeakEquity) g_r9GovPeakEquity=sharedPeak;
   if(equity>g_r9GovPeakEquity)
   {
      g_r9GovPeakEquity=equity;
      if(!R9GovSet(g_r9GovKey+".peak",equity)) return false;
   }

   if(force || g_r9GovDirty || g_r9GovLastLedger==0 ||
      now-g_r9GovLastLedger>=InpR9GovRefreshSeconds)
   {
      if(!HistorySelect(g_r9GovDayStart,now)) return false;
      double losses=0.0,profits=0.0,charges=0.0;
      const int n=HistoryDealsTotal();
      for(int i=0;i<n;++i)
      {
         const ulong ticket=HistoryDealGetTicket(i);
         if(ticket==0) continue;
         const ENUM_DEAL_TYPE type=(ENUM_DEAL_TYPE)HistoryDealGetInteger(ticket,DEAL_TYPE);
         const double raw=HistoryDealGetDouble(ticket,DEAL_PROFIT);
         if(type==DEAL_TYPE_BUY || type==DEAL_TYPE_SELL)
         {
            const double p=raw+HistoryDealGetDouble(ticket,DEAL_SWAP);
            if(p<0.0) losses-=p; else profits+=p;
            charges+=MathMax(0.0,-HistoryDealGetDouble(ticket,DEAL_COMMISSION));
            charges+=MathMax(0.0,-HistoryDealGetDouble(ticket,DEAL_FEE));
         }
         else if(type==DEAL_TYPE_COMMISSION || type==DEAL_TYPE_COMMISSION_DAILY ||
                 type==DEAL_TYPE_COMMISSION_MONTHLY ||
                 type==DEAL_TYPE_COMMISSION_AGENT_DAILY ||
                 type==DEAL_TYPE_COMMISSION_AGENT_MONTHLY ||
                 type==DEAL_TYPE_CHARGE)
            charges+=MathMax(0.0,-raw);
      }
      g_r9GovGrossLoss=losses;
      g_r9GovGrossProfit=profits;
      g_r9GovCashCharges=charges;
      g_r9GovLastLedger=now;
      g_r9GovDirty=false;
   }

   double floatingLoss=0.0;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      if(PositionGetTicket(i)==0) continue;
      const double p=PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
      floatingLoss+=MathMax(0.0,-p);
   }
   g_r9GovFloatingLoss=floatingLoss;

   const double initial=InpR9GovBasePct*0.01*g_r9GovDayEquity;
   const double cap=InpR9GovMaxPct*0.01*g_r9GovDayEquity;
   g_r9GovBudget=MathMin(cap,initial+
                           InpR9GovProfitRecycle*MathMax(0.0,g_r9GovGrossProfit));
   const double consumed=g_r9GovGrossLoss+g_r9GovCashCharges+g_r9GovFloatingLoss;
   const bool grossTrip=(consumed>=g_r9GovBudget-1e-8);
   const bool ddTrip=(g_r9GovPeakEquity-equity>
                      InpR9GovPeakDrawdownPct*0.01*g_r9GovPeakEquity);
   const double margin=AccountInfoDouble(ACCOUNT_MARGIN);
   const double marginLevel=AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   const bool marginTrip=(margin>0.0 &&
                          (marginLevel<=0.0 || marginLevel<InpR9GovMinMarginPct));
   if((grossTrip || ddTrip || marginTrip) && !g_r9GovLocked)
   {
      if(!R9GovSet(g_r9GovKey+".halt",1.0)) return false;
      g_r9GovLocked=true;
      PrintFormat("GM_R9: PORTFOLIO HALT gross=%.2f charge=%.2f floating=%.2f cap=%.2f dd=%.2f%% margin=%.1f%%",
                  g_r9GovGrossLoss,g_r9GovCashCharges,g_r9GovFloatingLoss,
                  g_r9GovBudget,100.0*(g_r9GovPeakEquity-equity)/
                  MathMax(1.0,g_r9GovPeakEquity),marginLevel);
      GlobalVariablesFlush();
   }
   g_r9GovHealthy=true;
   return true;
}
bool R9GovAllowsOrder(const int side,const double volume,
                      const double entry,const double stopLoss)
{
   if(!InpR9GovEnabled) return true;
   if(!R9GovRefresh(false) || !g_r9GovHealthy || g_r9GovLocked) return false;
   const ENUM_ORDER_TYPE action=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;
   // Existing portfolio exposure is reflected in ACCOUNT_MARGIN_FREE.
   // New incremental margin is an intentionally conservative estimate;
   // on netting/hedged accounts OrderCheck can give a more exact projection.
   double requiredMargin=0.0;
   if(!OrderCalcMargin(action,_Symbol,volume,entry,requiredMargin)) return false;
   const double freeMargin=AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   const double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(!MathIsValidNumber(requiredMargin) || requiredMargin<0.0 ||
      !MathIsValidNumber(freeMargin) || !MathIsValidNumber(equity) ||
      equity<=0.0 || freeMargin-requiredMargin<
      equity*InpR9GovMinFreeEquityPct*0.01) return false;
   double pnl=0.0;
   if(!OrderCalcProfit(action,_Symbol,volume,entry,stopLoss,pnl)) return false;
   const double risk=MathMax(0.0,-pnl)+InpR9GovCashReservePerTrade;
   return (g_r9GovGrossLoss+g_r9GovCashCharges+
           g_r9GovFloatingLoss+risk<=g_r9GovBudget+1e-8);
}
void R9GovCloseOurPositions()
{
   if(!InpR9GovEnabled || !InpR9GovFlattenOwnOnHalt ||
      !g_r9GovHealthy || !g_r9GovLocked) return;
   const datetime now=TimeTradeServer();
   if(now<=g_r9GovLastCloseRequest) return;
   g_r9GovLastCloseRequest=now;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong ticket=PositionGetTicket(i);
      if(ticket==0 || PositionGetString(POSITION_SYMBOL)!=_Symbol ||
         (ulong)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
      if(!trade.PositionClose(ticket) ||
         (trade.ResultRetcode()!=TRADE_RETCODE_DONE &&
          trade.ResultRetcode()!=TRADE_RETCODE_DONE_PARTIAL))
         PrintFormat("GM_R9: governor close failed ticket=%I64u retcode=%u",
                     ticket,trade.ResultRetcode());
   }
}
#endif
// R9_STANDALONE_END GoldMuwahahaR9PortfolioGovernor.mqh
// R9_STANDALONE_BEGIN GoldMuwahahaR9M1IndicatorContext.mqh
#ifndef __GMM_R9_M1_INDICATOR_CONTEXT_MQH__
#define __GMM_R9_M1_INDICATOR_CONTEXT_MQH__
// Coinexx quote-price-only context. Closed M1 bars, no L2/volume claims.
// Can be reconstructed from source-ordered Coinexx Bid/Ask ticks.
// Default rescue OFF. Only shadow observation by default.

int      g_r9AdxHandle=INVALID_HANDLE;
int      g_r9EmaHandle=INVALID_HANDLE;
int      g_r9AtrM1Handle=INVALID_HANDLE;
datetime g_r9IndicatorBar=0;
datetime g_r9IndicatorLogMinute=0;
bool     g_r9IndicatorReady=false;
double   g_r9Adx=0.0,g_r9PlusDi=0.0,g_r9MinusDi=0.0;
double   g_r9Ema1=0.0,g_r9Ema2=0.0,g_r9AtrM1=0.0;

bool R9IndicatorInitialize()
{
   if(!InpR9M1ShadowEnabled && !InpR9M1RescueEnabled) return true;
   g_r9AdxHandle=iADX(_Symbol,PERIOD_M1,InpR9M1ADXPeriod);
   g_r9EmaHandle=iMA(_Symbol,PERIOD_M1,InpR9M1EMAPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_r9AtrM1Handle=iATR(_Symbol,PERIOD_M1,InpR9M1ATRPeriod);
   if(g_r9AdxHandle==INVALID_HANDLE || g_r9EmaHandle==INVALID_HANDLE ||
      g_r9AtrM1Handle==INVALID_HANDLE)
   {
      Print("GM_R9: M1 indicator handle init failed; rescue must remain disabled");
      return !InpR9M1RescueEnabled;
   }
   return true;
}
void R9IndicatorRelease()
{
   if(g_r9AdxHandle!=INVALID_HANDLE) IndicatorRelease(g_r9AdxHandle);
   if(g_r9EmaHandle!=INVALID_HANDLE) IndicatorRelease(g_r9EmaHandle);
   if(g_r9AtrM1Handle!=INVALID_HANDLE) IndicatorRelease(g_r9AtrM1Handle);
   g_r9AdxHandle=INVALID_HANDLE;
   g_r9EmaHandle=INVALID_HANDLE;
   g_r9AtrM1Handle=INVALID_HANDLE;
}
bool R9IndicatorUpdate(const datetime currentTick)
{
   if(g_r9AdxHandle==INVALID_HANDLE || g_r9EmaHandle==INVALID_HANDLE ||
      g_r9AtrM1Handle==INVALID_HANDLE) return false;
   const datetime closed=iTime(_Symbol,PERIOD_M1,1);
   if(closed<=0 || currentTick-closed>180) return false;
   if(g_r9IndicatorReady && g_r9IndicatorBar==closed) return true;
   double adx[1],pdi[1],mdi[1],ema1[1],ema2[1],atr[1];
   if(CopyBuffer(g_r9AdxHandle,0,1,1,adx)!=1 ||
      CopyBuffer(g_r9AdxHandle,1,1,1,pdi)!=1 ||
      CopyBuffer(g_r9AdxHandle,2,1,1,mdi)!=1 ||
      CopyBuffer(g_r9EmaHandle,0,1,1,ema1)!=1 ||
      CopyBuffer(g_r9EmaHandle,0,2,1,ema2)!=1 ||
      CopyBuffer(g_r9AtrM1Handle,0,1,1,atr)!=1)
      return false;
   if(!MathIsValidNumber(adx[0]) || !MathIsValidNumber(pdi[0]) ||
      !MathIsValidNumber(mdi[0]) || !MathIsValidNumber(ema1[0]) ||
      !MathIsValidNumber(ema2[0]) || !MathIsValidNumber(atr[0]) ||
      atr[0]<=0.0) return false;
   g_r9Adx=adx[0];
   g_r9PlusDi=pdi[0];
   g_r9MinusDi=mdi[0];
   g_r9Ema1=ema1[0];g_r9Ema2=ema2[0];g_r9AtrM1=atr[0];
   g_r9IndicatorBar=closed;
   g_r9IndicatorReady=true;
   return true;
}
double R9Clamp(const double x)
{
   return MathMax(-1.0,MathMin(1.0,x));
}
bool R9IndicatorConfluence(const int side,const datetime quoteSecond,
                           double &score)
{
   score=0.0;
   if(!R9IndicatorUpdate(quoteSecond)) return false;
   // QUOTE impulse: last three COMPLETED observed seconds; reject long gaps.
   if(g_microCount<4) return false;
   const int newest=RingIndexFromNewest(0);
   const int old=RingIndexFromNewest(3);
   const datetime secNew=g_micro[newest].second;
   const datetime secOld=g_micro[old].second;
   if(quoteSecond-secNew>2 || secNew-secOld>6 || secNew<=secOld) return false;
   const double impulse=g_micro[newest].close-g_micro[old].close;
   const double di=(g_r9PlusDi-g_r9MinusDi);
   const double ema=(g_r9Ema1-g_r9Ema2)/MathMax(g_r9AtrM1,1e-8);
   score=0.45*R9Clamp(side*di/10.0)+
         0.35*R9Clamp(side*ema/0.08)+
         0.20*R9Clamp(side*impulse/0.12);
   return true;
}
bool R9IndicatorRescue(const int side,const datetime quoteSecond,
                       double &score)
{
   if(!InpR9M1RescueEnabled) return false;
   if(!R9IndicatorConfluence(side,quoteSecond,score)) return false;
   if(g_r9Adx<InpR9M1MinADX) return false;
   if(side*(g_r9PlusDi-g_r9MinusDi)<InpR9M1MinDIGap) return false;
   return (score>=InpR9M1RescueScore);
}
#endif
// R9_STANDALONE_END GoldMuwahahaR9M1IndicatorContext.mqh
// R9_STANDALONE_BEGIN GoldMuwahahaR9CashGeometry.mqh
#ifndef __GMM_R9_CASH_GEOMETRY_MQH__
#define __GMM_R9_CASH_GEOMETRY_MQH__
// Only an executable-side SCENARIO calculation, not a prediction or trading gate.
// The $1.75 user's objective means net account currency when ACCOUNT_CURRENCY=USD.
// Assumed execution costs are input; Coinexx Bid/Ask ticklogs do not contain fills,
// paid commissions, broker stop fill slippage or real margin accounting.

datetime g_r9CashLastLogMinute=0;

bool R9CashScenario(const int side,const MqlTick &tick,
                    const double volume,const double stopLoss,
                    double &targetLiquidationQuote,
                    double &targetQuoteDistance,
                    double &cashLossAtStop)
{
   targetLiquidationQuote=0.0;
   targetQuoteDistance=0.0;
   cashLossAtStop=0.0;
   const ENUM_ORDER_TYPE action=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;
   const double fill=side>0?tick.ask:tick.bid; // spread already embedded!
   if(fill<=0.0 || volume<=0.0) return false;
   double cashPerQuoteDollar=0.0;
   // Probe $1 XAUUSD favorable change using the actual symbol profit formula.
   if(!OrderCalcProfit(action,_Symbol,volume,fill,fill+side*1.0,
                       cashPerQuoteDollar) || cashPerQuoteDollar<=0.0)
      return false;
   const double requiredGross=InpR9TargetNetAccountCash+
                               InpR9AssumedRoundTripCostAccountCash;
   const double wanted=requiredGross/cashPerQuoteDollar;
   const double priceStep=TickSize();
   if(priceStep<=0.0) return false;
   double target=fill+side*wanted;
   if(side>0) target=MathCeil(target/priceStep)*priceStep;
   else       target=MathFloor(target/priceStep)*priceStep;
   target=NormalizePrice(target);
   double grossAtTarget=0.0;
   bool good=false;
   for(int k=0;k<16;++k)
   {
      if(!OrderCalcProfit(action,_Symbol,volume,fill,target,grossAtTarget))
         return false;
      if(grossAtTarget-InpR9AssumedRoundTripCostAccountCash+1e-7 >=
         InpR9TargetNetAccountCash) {good=true;break;}
      target=NormalizePrice(target+side*priceStep);
   }
   if(!good) return false;
   double rawStop=0.0;
   if(!OrderCalcProfit(action,_Symbol,volume,fill,stopLoss,rawStop))
      return false;
   targetLiquidationQuote=target;
   targetQuoteDistance=side*(target-fill);
   cashLossAtStop=MathMax(0.0,-rawStop)+InpR9AssumedRoundTripCostAccountCash;
   return true;
}
#endif
// R9_STANDALONE_END GoldMuwahahaR9CashGeometry.mqh
// R9_STANDALONE_BEGIN GoldMuwahahaR9M60ModelBridge.mqh
#ifndef __GMM_R9_M60_155_SCORE_BRIDGE_MQH__
#define __GMM_R9_M60_155_SCORE_BRIDGE_MQH__
// R9 v1.94 — exact 155-feature archived LightGBM score consumption.
// Native EA does NOT reconstruct or fabricate the 155 feature vector.
// External scorer must apply frozen source-order feature contract, producing
// one quote/side-exact packet from a PAST-ONLY source (not future labels).
// File checks are nonblocking and default to SHADOW; never imply OOS P&L.
//
// Packet (single CSV record, comma delimiter, UTF-8/ANSI ASCII only):
// R9M60_155_V1,login,symbol,magic,time_msc,bid_cents,ask_cents,side,
// 155,model_sha256,model_id,feature_end_msc,source_ordinal,
// score,status,schema_id
// Authoritative protocol: research/.../m60_155_integration/README.md.

long g_r9M60Qualified=0;
long g_r9M60Matched=0;
long g_r9M60Missing=0;
long g_r9M60Rejected=0;
double g_r9M60ScoreSum=0.0;

string R9M60PacketPath()
{
   return StringFormat("R9_M60_155_%s_%I64d_%I64u.csv",
                       _Symbol,AccountInfoInteger(ACCOUNT_LOGIN),InpMagic);
}
bool R9M60GetScore(const MqlTick &tick,const int side,double &score)
{
   score=0.0;
   if(InpR9M60Mode==0) return false;
   if(!FileIsExist(R9M60PacketPath(),FILE_COMMON)) return false;
   const int fh=FileOpen(R9M60PacketPath(),
                         FILE_READ|FILE_CSV|FILE_ANSI|FILE_COMMON|
                         FILE_SHARE_READ|FILE_SHARE_WRITE,',');
   if(fh==INVALID_HANDLE) return false;
   // Reading all fields before accepting prevents partially published packets
   // from generating trades. The producer must atomically replace this file.
   const string tag=FileReadString(fh);
   const string login=FileReadString(fh);
   const string symbol=FileReadString(fh);
   const string magic=FileReadString(fh);
   const string stamp=FileReadString(fh);
   const string bid=FileReadString(fh);
   const string ask=FileReadString(fh);
   const string packetSide=FileReadString(fh);
   const string dimensions=FileReadString(fh);
   const string modelHash=FileReadString(fh);
   const string modelId=FileReadString(fh);
   const string featureEnd=FileReadString(fh);
   const string sourceOrdinal=FileReadString(fh);
   const string probability=FileReadString(fh);
   const string status=FileReadString(fh);
   const string schemaId=FileReadString(fh);
   const bool hasTail=!FileIsEnding(fh);
   FileClose(fh);
   if(hasTail || tag!="R9M60_155_V1" || symbol!=_Symbol ||
      schemaId!="R9_M60_155_20261113_V1" ||
      status!="ASOF_PINNED" ||
      StringToInteger(login)!=AccountInfoInteger(ACCOUNT_LOGIN) ||
      StringToInteger(magic)!=(long)InpMagic ||
      StringToInteger(stamp)!=(long)tick.time_msc ||
      StringToInteger(bid)!=(long)MathRound(tick.bid*100.0) ||
      StringToInteger(ask)!=(long)MathRound(tick.ask*100.0) ||
      StringToInteger(packetSide)!=(long)side ||
      StringToInteger(dimensions)!=155 ||
      StringToInteger(featureEnd)!=(long)tick.time_msc ||
      StringToInteger(sourceOrdinal)<=0 ||
      modelHash!=InpR9M60ExpectedModelSha ||
      StringLen(modelId)<4 || StringLen(probability)<1)
      return false;
   const double value=StringToDouble(probability);
   if(!MathIsValidNumber(value) || value<0.0 || value>1.0) return false;
   score=value;
   return true;
}
bool R9M60PermitOriginalEntry(const MqlTick &tick,const int side)
{
   if(InpR9M60Mode==0) return true;
   ++g_r9M60Qualified;
   double score=0.0;
   if(!R9M60GetScore(tick,side,score))
   {
      ++g_r9M60Missing;
      // SHADOW: no change to R9 fills. FILTER: fail closed, no fake score.
      return (InpR9M60Mode==1);
   }
   ++g_r9M60Matched;
   g_r9M60ScoreSum+=score;
   if(InpR9M60Mode==1) return true;
   if(score+1e-12<InpR9M60MinProbability)
   {
      ++g_r9M60Rejected;
      return false;
   }
   return true;
}
void R9M60ReportStats()
{
   if(InpR9M60Mode==0) return;
   PrintFormat("GM_R9: MODEL155 mode=%d qualified=%I64d exact_matches=%I64d missing_or_mismatch=%I64d model_veto=%I64d mean_score=%.6f",
               InpR9M60Mode,g_r9M60Qualified,g_r9M60Matched,
               g_r9M60Missing,g_r9M60Rejected,
               g_r9M60Matched>0?g_r9M60ScoreSum/(double)g_r9M60Matched:0.0);
}
#endif
// R9_STANDALONE_END GoldMuwahahaR9M60ModelBridge.mqh

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
   if(side>0) sl=NormalizePrice(tick.bid-sd);
   else sl=NormalizePrice(tick.ask+sd);
   if(!R9GovAllowsOrder(side,volume,side>0?tick.ask:tick.bid,sl)) return false;
   if(InpR9CashGeometryShadow && g_r9CashLastLogMinute!=g_cycleMinute)
   {
      double goalQuote=0.0,move=0.0,loss=0.0;
      if(R9CashScenario(side,tick,volume,sl,goalQuote,move,loss))
         PrintFormat("%s: CASH SCENARIO account=%s netGoal=%.2f assumedCost=%.2f side=%d requiredQuoteMove=%.3f liquidationQuote=%.3f estimatedCashStopLoss=%.2f",
                     EA_TAG,AccountInfoString(ACCOUNT_CURRENCY),
                     InpR9TargetNetAccountCash,InpR9AssumedRoundTripCostAccountCash,
                     side,move,goalQuote,loss);
      g_r9CashLastLogMinute=g_cycleMinute;
   }
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
   const datetime ageNow=TimeTradeServer();
   const datetime actualOpened=(datetime)PositionGetInteger(POSITION_TIME);
   if(actualOpened>0 && ageNow>0 && ageNow-actualOpened>=InpMaxHoldSeconds)
   {
      if(g_r9LastTimeoutCloseSecond>=ageNow) return;
      g_r9LastTimeoutCloseSecond=ageNow;
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
   if(InpR9GovEnabled && !R9GovRefresh(false)) return;
   if(InpR9GovEnabled && g_r9GovLocked) return;
   if(!GateAllowsEntry(tick)) return;

   int side=0;
   if((g_pendingMode==2 || g_pendingMode==1) && tick.ask>=g_cycleBuy) side=1;
   else if((g_pendingMode==2 || g_pendingMode==-1) && tick.bid<=g_cycleSell) side=-1;
   if(side==0) return;

   double disp,eff,rng;int turns;
   const bool originalQualified=S1QualityForSide(side,disp,eff,rng,turns);
   double indicatorScore=0.0;
   if(InpR9M1ShadowEnabled && g_r9IndicatorLogMinute!=g_cycleMinute)
   {
      if(R9IndicatorConfluence(side,tick.time,indicatorScore) && InpVerbose)
         PrintFormat("%s: INDICATOR SHADOW minute=%s side=%d adx=%.2f pDI=%.2f mDI=%.2f emaATR=%.3f score=%.3f",
                     EA_TAG,TimeToString(g_cycleMinute,TIME_DATE|TIME_MINUTES),
                     side,g_r9Adx,g_r9PlusDi,g_r9MinusDi,
                     (g_r9Ema1-g_r9Ema2)/MathMax(g_r9AtrM1,1e-8),indicatorScore);
      g_r9IndicatorLogMinute=g_cycleMinute;
   }
   if(!originalQualified)
   {
      if(!R9IndicatorRescue(side,tick.time,indicatorScore)) return;
      // 155-feature model was only evaluated at ORIGINAL R9 entry moments:
      // never score the untrained rescued universe as if it were equivalent.
      if(InpR9M60Mode==2) return;
      if(InpVerbose) PrintFormat("%s: EXPERIMENTAL INDICATOR RESCUE side=%d score=%.3f",EA_TAG,side,indicatorScore);
   }
   else if(InpVerbose)
      PrintFormat("%s: qualified side=%d disp=%.3f eff=%.3f range=%.3f turns=%d",
                  EA_TAG,side,disp,eff,rng,turns);
   if(originalQualified && !R9M60PermitOriginalEntry(tick,side)) return;
   OpenTrade(side,tick);
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
       InpR9GovBasePct<=0.0 || InpR9GovMaxPct<InpR9GovBasePct ||
       InpR9GovProfitRecycle<0.0 || InpR9GovProfitRecycle>1.0 ||
       InpR9GovPeakDrawdownPct<=0.0 || InpR9GovMinMarginPct<=0.0 ||
       InpR9GovMinFreeEquityPct<0.0 || InpR9GovMinFreeEquityPct>=100.0 ||
       InpR9GovCashReservePerTrade<0.0 || InpR9GovRefreshSeconds<1 ||
       InpR9M1ADXPeriod<2 || InpR9M1EMAPeriod<2 || InpR9M1ATRPeriod<2 ||
       InpR9M1RescueScore<0.0 || InpR9M1RescueScore>1.0 ||
       InpR9M1MinDIGap<0.0 || InpR9M1MinADX<0.0 ||
       InpR9TargetNetAccountCash<=0.0 || InpR9AssumedRoundTripCostAccountCash<0.0 ||
       InpR9M60Mode<0 || InpR9M60Mode>2 ||
       InpR9M60MinProbability<0.0 || InpR9M60MinProbability>1.0 ||
       (InpR9M60Mode!=0 && StringLen(InpR9M60ExpectedModelSha)!=64))
   {
      Print(EA_TAG,": invalid inputs");return INIT_PARAMETERS_INCORRECT;
   }
   // Safe checkpoint cannot silently turn a shadow research model into a
   // money-risking entry gate.  These are necessary, NOT sufficient, conditions.
   if(InpR9M60Mode==2)
   {
      if(!InpR9M60ExperimentalFilterUnlock ||
         InpR9M60MinProbability<=0.0 ||
         InpR9M1RescueEnabled ||
         _Symbol!="XAUUSD" ||
         MathAbs(InpHunterPipPrice-0.01)>0.0000001)
      {
         Print(EA_TAG,": MODEL155 FILTER REFUSED: requires explicit unlock, nonzero prevalidated threshold, unmodified original-side universe and exact XAUUSD 0.01 quote scale");
         return INIT_PARAMETERS_INCORRECT;
      }
      Print(EA_TAG,": WARNING: experimental model filter enabled; same-tick 155-feature live producer, OOS profitability, and MQL5 parity are NOT certified");
   }
   else if(InpR9M60Mode==1)
   {
      Print(EA_TAG,": CHECKPOINT v1.94 MODEL155 SHADOW: original R9 entries unaffected; no valid packet means model UNOBSERVED");
   }
   trade.SetExpertMagicNumber(InpMagic);trade.SetDeviationInPoints(InpDeviationPoints);trade.SetAsyncMode(false);
   if(!trade.SetTypeFillingBySymbol(_Symbol)) Log("warning: unable to derive filling mode");
   if(InpUseRegimeGate)
   {
      g_atrHandle=iATR(_Symbol,InpAtrTimeframe,InpAtrPeriod);
      if(g_atrHandle==INVALID_HANDLE){ PrintFormat("%s: ATR handle failed lastError=%d",EA_TAG,GetLastError());return INIT_FAILED; }
   }
   if(!R9IndicatorInitialize()) return INIT_FAILED;
   if(!EventSetTimer(1))
   {
      Print(EA_TAG,": 1s timer unavailable; fail closed");
      return INIT_FAILED;
   }
   if(InpR9GovEnabled && !R9GovRefresh(true))
   {
      Print(EA_TAG,": portfolio risk history/anchor unavailable; fail closed");
      EventKillTimer();
      return INIT_FAILED;
   }
   PrintFormat("%s CHECKPOINT v1.94 mode=%d governor=%d rescue=%d expected_model_sha=%s",EA_TAG,InpR9M60Mode,(int)InpR9GovEnabled,(int)InpR9M1RescueEnabled,InpR9M60ExpectedModelSha);
   PrintFormat("%s initialized gap=%d stop=%d trail=%d act=%d velLB=%d minVel=%d eff=%.2f range=%d maxHold=%d rearms=%d",
               EA_TAG,InpGapPips,InpStopLossPips,InpTrailPips,InpTrailActivationPips,InpVelocityLookbackSec,InpMinVelocityPips,InpMinDirectionalEff,InpMinRangePips,InpMaxHoldSeconds,InpMaxSameMinuteRearms);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_atrHandle!=INVALID_HANDLE){ IndicatorRelease(g_atrHandle);g_atrHandle=INVALID_HANDLE; }
   EventKillTimer();
   R9IndicatorRelease();
   GlobalVariablesFlush();
   R9M60ReportStats();
   Log(StringFormat("deinit reason=%d",reason));
}

void OnTick()
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol,tick) || tick.bid<=0.0 || tick.ask<=0.0) return;
   // Loss-accounting history refresh is amortized; market risk is independently
   // inspected by the 1-second timer. No quote tick data is persisted here.
   if(InpR9GovEnabled && g_r9GovLocked) R9GovCloseOurPositions();
   Reconcile(tick);
}
void OnTimer()
{
   if(InpR9GovEnabled)
   {
      R9GovRefresh(false);
      R9GovCloseOurPositions();
   }
   const datetime now=TimeTradeServer();
   if(now<=0 || g_r9LastTimeoutCloseSecond>=now) return;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong ticket=PositionGetTicket(i);
      if(ticket==0 || PositionGetString(POSITION_SYMBOL)!=_Symbol ||
         (ulong)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
      const datetime opened=(datetime)PositionGetInteger(POSITION_TIME);
      if(opened<=0 || now-opened<InpMaxHoldSeconds) continue;
      g_r9LastTimeoutCloseSecond=now;
      if(!trade.PositionClose(ticket) ||
         (trade.ResultRetcode()!=TRADE_RETCODE_DONE &&
          trade.ResultRetcode()!=TRADE_RETCODE_DONE_PARTIAL))
         LogTradeFailure("timer close");
      break; // 1 close request per second, never a request storm
   }
}
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   if(trans.type!=TRADE_TRANSACTION_DEAL_ADD) return;
   g_r9GovDirty=true; // cheap notification; expensive history scan outside callback
   if(trans.deal==0 || !HistoryDealSelect(trans.deal)) return;
   if(HistoryDealGetString(trans.deal,DEAL_SYMBOL)!=_Symbol ||
      (ulong)HistoryDealGetInteger(trans.deal,DEAL_MAGIC)!=InpMagic) return;
   const ENUM_DEAL_ENTRY state=(ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal,DEAL_ENTRY);
   if(state==DEAL_ENTRY_IN || state==DEAL_ENTRY_INOUT)
   {
      g_hadPosition=true;
      g_positionOpenedAt=(datetime)HistoryDealGetInteger(trans.deal,DEAL_TIME);
      g_lastPositionType=(HistoryDealGetInteger(trans.deal,DEAL_TYPE)==DEAL_TYPE_BUY)?
                         POSITION_TYPE_BUY:POSITION_TYPE_SELL;
   }
}
