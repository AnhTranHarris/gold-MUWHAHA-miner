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
   if(start==g_r9GovDayStart) return true;

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
   const bool marginTrip=(margin>0.0 && marginLevel>0.0 &&
                          marginLevel<InpR9GovMinMarginPct);
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
   double pnl=0.0;
   if(!OrderCalcProfit(side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL,
                       _Symbol,volume,entry,stopLoss,pnl)) return false;
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
