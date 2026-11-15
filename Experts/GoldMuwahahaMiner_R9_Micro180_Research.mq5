#property strict
#property version "1.95"
#property description "R9 micro180 research fork. Demo trading disabled by default. Millisecond CopyTicks, executable-side breakout, 180s bounded quote windows."
#include <Trade/Trade.mqh>

// RESEARCH FORK: original R9 v1.94 and its rollback remain unmodified.
// NOT COMPILED BY METAEDITOR / NOT FOR LIVE. Do not enable without source-exact parity.
input group "SAFE RESEARCH EXECUTION"
input bool   InpEnableDemoOrders        = false;  // OFF until MetaEditor & demo validated
input ulong  InpMagic                   = 559180;
input double InpLots                    = 0.01;
input int    InpDeviationPoints         = 20;
input int    InpMaxEntriesPerMinute     = 4;
input int    InpMaxHoldMs               = 30000;
input double InpAdditionalCostCash      = 0.20;   // broker-UNVERIFIED, beyond Bid/Ask spread
input double InpExtraSlipReserveCash    = 0.10;   // research allowance; not a fill guarantee
input double InpMinNetProfitCash        = 0.10;
input double InpPreferredNetProfitCash  = 1.75;
input double InpMaxIntendedLossCash     = 2.00;
input bool   InpExperimentalRunner      = false;  // OFF: continuation unvalidated
input double InpRunnerTrailingCash      = 0.25;
input int    InpBaseStopPricePoints     = 30;     // R9 0.30 quote-price distance

input group "MICRO180 ASYMMETRIC SIGNAL"
input int    InpMinBasketMovePoints     = 10;
input int    InpMin15sStructurePoints  = 6;
input int    InpBreakoutBufferPoints   = 1;
input int    InpMaxQuoteGapMs          = 2500;
input int    InpMaxSpreadPoints        = 25;
input double InpMaxSpreadShockRatio    = 1.35;
input double InpMinDirectionalEff      = 0.55;
input double InpMinNormalizedBreakout  = 0.25;
input int    InpMinCompleted15s        = 10;
input int    InpMinCompleted30s        = 18;
input int    InpMinQuotes5s            = 5;

input group "NATIVE MT5 PRICE INDICATORS + QUOTE PROXY"
input bool   InpM1DirectionalVeto      = true;
input int    InpADXWilderPeriod        = 14;
input int    InpEMAPeriod              = 20;
input int    InpATRPeriod              = 14;
input double InpMinM5ATRPrice          = 1.75;  // frozen pilot, not original session-adaptive parity

input group "ACCOUNT RISK GOVERNOR"
input double InpCapitalFloorPct        = 25.0;  // persistent loss from starting equity
input double InpMaxPeakDrawdownPct     = 10.0;  // stricter preexisting R9 protection
input double InpDailyGrossBasePct      = 4.0;
input double InpDailyGrossMaxPct       = 12.0;
input double InpProfitRecycleFrac      = 0.25;
input double InpMinMarginLevelPct      = 150.0;

CTrade g_trade;
#define MICRO_SECS 192
#define MICRO_BATCH 1024

struct QBar
{
   long startMs;
   long firstMs;
   long lastMs;
   int n;
   double bo,bh,bl,bc,ao,ah,al,ac,spread;
};
QBar g_second, g_5s, g_15s, g_30s, g_closed15;
QBar g_s[ MICRO_SECS ];
int g_sh=0,g_sn=0;
bool g_haveSecond=false,g_have5=false,g_have15=false,g_have30=false,g_haveClosed15=false;
ulong g_cursorMs=0;
int g_cursorAtSameMs=0;
long g_lastQuoteMs=0,g_prevQuoteMs=0;
int g_lastQuoteGap=0;
bool g_dataFault=false;
int g_entriesThisMinute=0;
long g_entryMinute=-1,g_exitMs=-1,g_exit5=-1,g_exit15=-1;
long g_entryMs=0;
double g_peakObservedNet=-1e30;
int g_hADX=INVALID_HANDLE,g_hEMA=INVALID_HANDLE,g_hATR1=INVALID_HANDLE,g_hATR5=INVALID_HANDLE;
string g_riskKey="";
double g_accountBase=0,g_accountPeak=0,g_dayStartEquity=0;
double g_dayGrossLoss=0,g_dayGrossProfit=0,g_dayCharges=0;
long g_lastRiskRefresh=0;
long g_dayNumber=-1;
bool g_riskHalt=false,g_dayHalt=false;

void BarReset(QBar &b,const MqlTick &t,const long start)
{
   b.startMs=start;b.firstMs=(long)t.time_msc;b.lastMs=(long)t.time_msc;b.n=1;
   b.bo=t.bid;b.bh=t.bid;b.bl=t.bid;b.bc=t.bid;
   b.ao=t.ask;b.ah=t.ask;b.al=t.ask;b.ac=t.ask;b.spread=t.ask-t.bid;
}
void BarQuote(QBar &b,const MqlTick &t)
{
   b.lastMs=(long)t.time_msc;b.n++;
   b.bh=MathMax(b.bh,t.bid);b.bl=MathMin(b.bl,t.bid);b.bc=t.bid;
   b.ah=MathMax(b.ah,t.ask);b.al=MathMin(b.al,t.ask);b.ac=t.ask;
   b.spread=t.ask-t.bid;
}
void PushSecond()
{
   g_s[g_sh]=g_second;
   g_sh=(g_sh+1)%MICRO_SECS;
   if(g_sn<MICRO_SECS) g_sn++;
}
int SecFromLatest(const int offset)
{
   int i=g_sh-1-offset;
   while(i<0)i+=MICRO_SECS;
   return i%MICRO_SECS;
}
void AcceptHistoricalQuote(const MqlTick &t)
{
   const long ms=(long)t.time_msc;
   if(g_lastQuoteMs>0 && ms<g_lastQuoteMs){g_dataFault=true;return;}
   g_lastQuoteGap=(g_lastQuoteMs>0?(int)(ms-g_lastQuoteMs):0);
   g_prevQuoteMs=g_lastQuoteMs;g_lastQuoteMs=ms;
   const long s=ms/1000*1000, f=ms/5000*5000,
              q=ms/15000*15000, h=ms/30000*30000;
   if(!g_haveSecond){BarReset(g_second,t,s);g_haveSecond=true;}
   else if(s==g_second.startMs)BarQuote(g_second,t);
   else {PushSecond();BarReset(g_second,t,s);}
   if(!g_have5){BarReset(g_5s,t,f);g_have5=true;}
   else if(f==g_5s.startMs)BarQuote(g_5s,t);
   else BarReset(g_5s,t,f);
   if(!g_have15){BarReset(g_15s,t,q);g_have15=true;}
   else if(q==g_15s.startMs)BarQuote(g_15s,t);
   else {g_closed15=g_15s;g_haveClosed15=true;BarReset(g_15s,t,q);}
   if(!g_have30){BarReset(g_30s,t,h);g_have30=true;}
   else if(h==g_30s.startMs)BarQuote(g_30s,t);
   else BarReset(g_30s,t,h);
}

// CopyTicks is required because OnTick does NOT guarantee one callback per tick.
// At equal time_msc the cursor stores the number of previously consumed source
// records at that millisecond. Unknown/incomplete pagination fails CLOSED.
bool SyncQuoteHistory(const MqlTick &latest)
{
   if(g_dataFault)return false;
   MqlTick copied[];
   ArrayResize(copied,MICRO_BATCH);
   if(g_cursorMs==0)
   {
      const ulong now=(ulong)latest.time_msc;
      g_cursorMs=(now>180000?now-180000:1);
      g_cursorAtSameMs=0;
   }
   for(int batch=0;batch<8;++batch)
   {
      const int n=CopyTicks(_Symbol,copied,COPY_TICKS_ALL,g_cursorMs,MICRO_BATCH);
      if(n<0){g_dataFault=true;return false;}
      int oldSkipped=0,processed=0;
      for(int i=0;i<n;++i)
      {
         const ulong ms=(ulong)copied[i].time_msc;
         if(ms==g_cursorMs && oldSkipped<g_cursorAtSameMs){oldSkipped++;continue;}
         if(ms<g_cursorMs){g_dataFault=true;return false;}
         if(copied[i].bid<=0 || copied[i].ask<copied[i].bid)continue;
         AcceptHistoricalQuote(copied[i]);
         if(g_dataFault)return false;
         if(ms==g_cursorMs)g_cursorAtSameMs++;
         else {g_cursorMs=ms;g_cursorAtSameMs=1;}
         processed++;
      }
      if(n==MICRO_BATCH && processed==0){g_dataFault=true;return false;}
      if(n<MICRO_BATCH)return g_lastQuoteMs>0 && g_lastQuoteMs>=(long)latest.time_msc;
   }
   // Excessive backlog: no trading until the cursor catches up, no data loss.
   return false;
}

bool Read1(const int handle,const int buffer,const int shift,double &out)
{
   if(handle==INVALID_HANDLE)return false;
   double x[1];
   if(CopyBuffer(handle,buffer,shift,1,x)!=1 || !MathIsValidNumber(x[0]))return false;
   out=x[0];return true;
}

bool NativeDirectionAllows(const int side)
{
   double atr5=0;
   if(!Read1(g_hATR5,0,1,atr5))return false; // fail CLOSED on missing M5 regime
   if(atr5<InpMinM5ATRPrice)return false;
   double pd=0,md=0,ema1=0,ema2=0,atr1=0;
   if(Read1(g_hADX,1,1,pd) && Read1(g_hADX,2,1,md) &&
      Read1(g_hEMA,0,1,ema1) && Read1(g_hEMA,0,2,ema2) &&
      Read1(g_hATR1,0,1,atr1) && atr1>0)
   {
      const double di=side*(pd-md);
      const double slope=side*(ema1-ema2)/atr1;
      const double score=MathMax(-1,MathMin(1,0.7*di/20.0+0.3*slope/0.05));
      return (!InpM1DirectionalVeto || score>=-0.25);
   }
   // Explicit quote-only proxy fallback: S1 + both executable breakouts remain
   // required; no claim of missing native DI/EMA having been reconstructed.
   return true;
}

bool S1Quality(const int side,const long nowMs)
{
   if(g_sn<11)return false;
   double prev=0,start=0,travel=0,hi=-DBL_MAX,lo=DBL_MAX;
   long prevSecond=-1;
   int turns=0,lastSign=0;
   for(int off=9;off>=0;--off)
   {
      QBar b=g_s[SecFromLatest(off)];
      if(nowMs-b.lastMs>15000)return false;
      if(prevSecond>=0 && b.startMs-prevSecond>2000)return false;
      if(off==9){start=b.bc;prev=b.bc;}
      else
      {
         const double delta=b.bc-prev;
         travel+=MathAbs(delta);
         const int sign=delta>0?1:delta<0?-1:0;
         if(sign!=0){if(lastSign!=0 && sign!=lastSign)turns++;lastSign=sign;}
         prev=b.bc;
      }
      prevSecond=b.startMs;
      hi=MathMax(hi,b.bh);lo=MathMin(lo,b.bl);
   }
   if(turns>9 || hi-lo<0.50)return false;
   const double net=prev-start;
   if(side*net<0.15)return false;
   return MathAbs(net)/(travel+1e-9)>=0.70;
}

bool MicroSignal(const MqlTick &t,int &side)
{
   side=0;
   const long now=(long)t.time_msc;
   if(!g_haveClosed15 || !g_have5 || g_sn<InpMinCompleted30s ||
      g_lastQuoteGap>InpMaxQuoteGapMs || t.ask<=0 || t.bid<=0)return false;
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(point<=0)return false;
   const double spread=(t.ask-t.bid)/point;
   if(spread>InpMaxSpreadPoints)return false;
   const double move=(t.bid+t.ask-g_5s.bo-g_5s.ao)/(2*point);
   if(move>=InpMinBasketMovePoints)side=1;
   else if(move<=-InpMinBasketMovePoints)side=-1;
   else return false;
   if(now-(g_closed15.startMs+15000)>15000 ||
      side*(g_closed15.bc+g_closed15.ac-g_closed15.bo-g_closed15.ao)/(2*point)<InpMin15sStructurePoints)
      return false;
   if(!S1Quality(side,now))return false;

   double highB15=-DBL_MAX,highB30=-DBL_MAX,lowA15=DBL_MAX,lowA30=DBL_MAX;
   int n15=0,n30=0,n5=0;
   double lastSpreads[32],lastMid[32];int nsp=0;
   long recentLast=-1;
   for(int off=0;off<g_sn;++off)
   {
      QBar b=g_s[SecFromLatest(off)];
      const long age=now-b.lastMs;
      if(age<0){g_dataFault=true;return false;}
      if(age>30000)break;
      if(age<=30000)
      {
         highB30=MathMax(highB30,b.bc);lowA30=MathMin(lowA30,b.ac);n30++;
      }
      if(age<=15000)
      {
         highB15=MathMax(highB15,b.bc);lowA15=MathMin(lowA15,b.ac);n15++;
         if(nsp<32){lastSpreads[nsp]=(b.ac-b.bc)/point;lastMid[nsp]=(b.bc+b.ac)/2;nsp++;}
      }
      if(age<=5000)n5+=b.n;
      if(recentLast<0)recentLast=b.lastMs;
   }
   if(recentLast<0 || now-recentLast>2500 || n15<InpMinCompleted15s ||
      n30<InpMinCompleted30s || n5<InpMinQuotes5s)return false;
   const double buffer=InpBreakoutBufferPoints*point;
   double delta=0;
   if(side>0)
   {
      if(t.bid<highB15+buffer || t.bid<highB30+buffer)return false;
      delta=(t.bid-highB30)/point;
   }
   else
   {
      if(t.ask>lowA15-buffer || t.ask>lowA30-buffer)return false;
      delta=(lowA30-t.ask)/point;
   }
   if(nsp<3)return false;
   // Reverse-history arrays are newest first. Direction sign reflects oldest
   // to newest, while efficiency and volatility are time-order symmetric.
   const double signedMove=side*(lastMid[0]-lastMid[nsp-1]);
   double travel=0,sumSq=0;
   for(int i=1;i<nsp;++i)
   {
      const double diff=(lastMid[i-1]-lastMid[i])/point;
      travel+=MathAbs(diff);
      sumSq+=diff*diff;
   }
   if(signedMove<=0 || MathAbs(signedMove)/MathMax(point,travel*point)<InpMinDirectionalEff)return false;
   const double sigma=MathMax(1.0,MathSqrt(sumSq/(nsp-1)));
   if(delta/sigma<InpMinNormalizedBreakout)return false;
   // Sort only the populated observed seconds, not the unused 32-slot tail.
   for(int i=1;i<nsp;++i)
   {
      const double v=lastSpreads[i];int j=i-1;
      while(j>=0 && lastSpreads[j]>v){lastSpreads[j+1]=lastSpreads[j];--j;}
      lastSpreads[j+1]=v;
   }
   const double med=lastSpreads[nsp/2];
   if(spread/MathMax(1.0,med)>InpMaxSpreadShockRatio)return false;
   return NativeDirectionAllows(side);
}

double ExecNet(const int side,const double vol,const double openPrice,const double closePrice)
{
   double gross=0;
   const ENUM_ORDER_TYPE type=(side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL);
   if(!OrderCalcProfit(type,_Symbol,vol,openPrice,closePrice,gross))return -DBL_MAX;
   return gross-InpAdditionalCostCash;
}

bool OwnPosition(ulong &ticket,ENUM_POSITION_TYPE &type,double &open,double &stop,double &volume,long &openedMs)
{
   ticket=0;open=0;stop=0;volume=0;openedMs=0;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      const ulong id=PositionGetTicket(i);
      if(id==0 || PositionGetString(POSITION_SYMBOL)!=_Symbol ||
         (ulong)PositionGetInteger(POSITION_MAGIC)!=InpMagic)continue;
      ticket=id;type=(ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      open=PositionGetDouble(POSITION_PRICE_OPEN);
      stop=PositionGetDouble(POSITION_SL);
      volume=PositionGetDouble(POSITION_VOLUME);
      openedMs=(long)PositionGetInteger(POSITION_TIME_MSC);
      return true;
   }
   return false;
}

bool GVEnsure(const string key,const double initial)
{
   if(GlobalVariableCheck(key))return true;
   return GlobalVariableSet(key,initial)!=0;
}

void RefreshRisk(const bool force)
{
   const long now=(long)TimeTradeServer();
   if(now<=0){g_riskHalt=true;return;}
   const double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity<=0){g_riskHalt=true;return;}
   if(equity>g_accountPeak)
   {
      g_accountPeak=equity;
      if(GlobalVariableSet(g_riskKey+".peak",equity)==0)g_riskHalt=true;
   }
   if(GlobalVariableCheck(g_riskKey+".halt") && GlobalVariableGet(g_riskKey+".halt")>0.5)g_riskHalt=true;
   if(equity<=(1-InpCapitalFloorPct/100.0)*g_accountBase ||
      equity<=(1-InpMaxPeakDrawdownPct/100.0)*g_accountPeak)g_riskHalt=true;
   const long day=(long)(now/86400);
   if(day!=g_dayNumber)
   {
      g_dayNumber=day;
      const string dkey=g_riskKey+".day."+IntegerToString(day);
      if(!GVEnsure(dkey,equity))g_riskHalt=true;
      g_dayStartEquity=GlobalVariableGet(dkey);
      g_dayHalt=(GlobalVariableCheck(dkey+".halt") && GlobalVariableGet(dkey+".halt")>0.5);
      g_lastRiskRefresh=0;
   }
   if(g_riskHalt){GlobalVariableSet(g_riskKey+".halt",1);return;}
   if(!force && now-g_lastRiskRefresh<5)return;
   g_lastRiskRefresh=now;
   if(!HistorySelect((datetime)(day*86400),(datetime)now))
   {g_riskHalt=true;GlobalVariableSet(g_riskKey+".halt",1);return;}
   g_dayGrossLoss=0;g_dayGrossProfit=0;g_dayCharges=0;
   for(int i=0;i<HistoryDealsTotal();++i)
   {
      const ulong id=HistoryDealGetTicket(i);
      if(id==0)continue;
      const ENUM_DEAL_TYPE k=(ENUM_DEAL_TYPE)HistoryDealGetInteger(id,DEAL_TYPE);
      if(k!=DEAL_TYPE_BUY && k!=DEAL_TYPE_SELL)
      {
         // Broker-side cash charge ledger may create a separate commission deal.
         if(k==DEAL_TYPE_COMMISSION || k==DEAL_TYPE_COMMISSION_DAILY ||
            k==DEAL_TYPE_COMMISSION_MONTHLY || k==DEAL_TYPE_CHARGE)
            g_dayCharges+=MathMax(0,-HistoryDealGetDouble(id,DEAL_PROFIT));
         continue;
      }
      const double pnl=HistoryDealGetDouble(id,DEAL_PROFIT)+HistoryDealGetDouble(id,DEAL_SWAP);
      if(pnl<0)g_dayGrossLoss-=pnl;else g_dayGrossProfit+=pnl;
      g_dayCharges+=MathMax(0,-HistoryDealGetDouble(id,DEAL_COMMISSION));
      g_dayCharges+=MathMax(0,-HistoryDealGetDouble(id,DEAL_FEE));
   }
   double floatingLoss=0;
   for(int i=PositionsTotal()-1;i>=0;--i)
   {
      if(PositionGetTicket(i)==0)continue;
      floatingLoss+=MathMax(0,-PositionGetDouble(POSITION_PROFIT)-PositionGetDouble(POSITION_SWAP));
   }
   const double limit=MathMin(InpDailyGrossMaxPct*.01*g_dayStartEquity,
                     InpDailyGrossBasePct*.01*g_dayStartEquity+
                     InpProfitRecycleFrac*g_dayGrossProfit);
   if(g_dayGrossLoss+g_dayCharges+floatingLoss>=limit ||
      (AccountInfoDouble(ACCOUNT_MARGIN)>0 &&
       AccountInfoDouble(ACCOUNT_MARGIN_LEVEL)<InpMinMarginLevelPct))
   {
      g_dayHalt=true;
      const string dkey=g_riskKey+".day."+IntegerToString(day);
      GlobalVariableSet(dkey+".halt",1);
   }
}

void CloseOwnOnRisk()
{
   if(!InpEnableDemoOrders)return;
   if(!g_riskHalt && !g_dayHalt)return;
   ulong ticket;ENUM_POSITION_TYPE type;double open,stop,volume;long opened;
   if(OwnPosition(ticket,type,open,stop,volume,opened))g_trade.PositionClose(ticket);
}

bool RiskAllowsNew(const int side,const double vol,const double entry,const double sl)
{
   RefreshRisk(false);
   if(g_riskHalt || g_dayHalt)return false;
   const ENUM_ORDER_TYPE kind=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;
   double pl=0,margin=0;
   if(!OrderCalcProfit(kind,_Symbol,vol,entry,sl,pl) ||
      !OrderCalcMargin(kind,_Symbol,vol,entry,margin))return false;
   const double risk=MathMax(0,-pl)+InpAdditionalCostCash+InpExtraSlipReserveCash;
   if(risk>InpMaxIntendedLossCash)return false;
   if(AccountInfoDouble(ACCOUNT_MARGIN_FREE)-margin<0.10*AccountInfoDouble(ACCOUNT_EQUITY))return false;
   const double maxBudget=MathMin(InpDailyGrossMaxPct*.01*g_dayStartEquity,
                       InpDailyGrossBasePct*.01*g_dayStartEquity+InpProfitRecycleFrac*g_dayGrossProfit);
   if(g_dayGrossLoss+g_dayCharges+risk>=maxBudget)return false;
   if(AccountInfoDouble(ACCOUNT_EQUITY)-risk<=(1-InpCapitalFloorPct/100.0)*g_accountBase)return false;
   if(AccountInfoDouble(ACCOUNT_EQUITY)-risk<=(1-InpMaxPeakDrawdownPct/100.0)*g_accountPeak)return false;
   return true;
}

void MicroSendEntry(const MqlTick &tick,const int side)
{
   if(!InpEnableDemoOrders || g_dataFault || g_entriesThisMinute>=InpMaxEntriesPerMinute)return;
   if((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO)return;
   const double tickSize=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(tickSize<=0 || point<=0)return;
   double volume=InpLots;
   const double minv=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   const double step=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   const double maxv=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   if(volume<minv || volume>maxv || step<=0 || MathAbs(MathRound(volume/step)*step-volume)>1e-7)return;
   const double stopMin=(double)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*point+tickSize;
   const double dist=MathMax(InpBaseStopPricePoints*point,stopMin);
   const double entry=side>0?tick.ask:tick.bid;
   double sl=side>0?tick.bid-dist:tick.ask+dist;
   sl=side>0?MathFloor(sl/tickSize)*tickSize:MathCeil(sl/tickSize)*tickSize;
   if(!RiskAllowsNew(side,volume,entry,sl))return;
   const bool sent=side>0?g_trade.Buy(volume,_Symbol,0,sl,0,"R9 MICRO180 BUY"):
                             g_trade.Sell(volume,_Symbol,0,sl,0,"R9 MICRO180 SELL");
   const uint code=g_trade.ResultRetcode();
   if(sent && (code==TRADE_RETCODE_DONE || code==TRADE_RETCODE_DONE_PARTIAL))
   {
      g_entriesThisMinute++;
      g_entryMs=(long)tick.time_msc;
      g_peakObservedNet=-1e30;
   }
}

bool StopProtectsCash(const int side,const double vol,const double open,const double sl,const double goal)
{
   return sl>0 && ExecNet(side,vol,open,sl)>=goal-1e-8;
}

void ManageOwnPosition(const MqlTick &tick)
{
   if(!InpEnableDemoOrders)return;
   ulong ticket;ENUM_POSITION_TYPE type;double open,sl,vol;long openedMs;
   if(!OwnPosition(ticket,type,open,sl,vol,openedMs))return;
   const int side=type==POSITION_TYPE_BUY?1:-1;
   const double exit=side>0?tick.bid:tick.ask;
   const double net=ExecNet(side,vol,open,exit);
   if(net==-DBL_MAX)return;
   g_peakObservedNet=MathMax(net,g_peakObservedNet);
   const long nowMs=(long)tick.time_msc;
   if(g_entryMs<=0)g_entryMs=openedMs;
   const long age=nowMs-openedMs;
   if(g_riskHalt || g_dayHalt || age>=InpMaxHoldMs ||
      net<=-InpMaxIntendedLossCash || g_lastQuoteGap>InpMaxQuoteGapMs)
   {
      g_trade.PositionClose(ticket);return;
   }
   if(net>=InpPreferredNetProfitCash)
   {
      g_trade.PositionClose(ticket);return;
   }
   if(net<InpMinNetProfitCash-1e-8)return;
   if(!InpExperimentalRunner)
   {
      g_trade.PositionClose(ticket);return;
   }
   // Runner must be independently certified before enabling this parameter.
   // Short 5s executable-side trend is an observational score, not an AUC claim.
   if(g_sn<3){g_trade.PositionClose(ticket);return;}
   const QBar b=g_s[SecFromLatest(2)];
   const double prev=(side>0?b.bc:b.ac);
   const double signedDist=side*(exit-prev);
   if(signedDist<=0){g_trade.PositionClose(ticket);return;}
   const double lock=MathMax(InpMinNetProfitCash,g_peakObservedNet-InpRunnerTrailingCash);
   const ENUM_ORDER_TYPE kind=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;
   double unitGain=0;
   if(!OrderCalcProfit(kind,_Symbol,vol,open,open+side*1.0,unitGain) || unitGain<=0)
   {g_trade.PositionClose(ticket);return;}
   const double tickSize=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(tickSize<=0 || point<=0){g_trade.PositionClose(ticket);return;}
   const double wanted=(lock+InpAdditionalCostCash)/unitGain;
   double next=side>0?MathCeil((open+wanted)/tickSize)*tickSize:
                      MathFloor((open-wanted)/tickSize)*tickSize;
   const double stopMinimum=(double)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*point+tickSize;
   const bool legal=(side>0?next<=tick.bid-stopMinimum:next>=tick.ask+stopMinimum);
   const bool tighter=(side>0?next>sl+tickSize*.5:next<sl-tickSize*.5);
   if(legal && tighter)
   {
      if(!g_trade.PositionModify(ticket,next,0) ||
         (g_trade.ResultRetcode()!=TRADE_RETCODE_DONE &&
          g_trade.ResultRetcode()!=TRADE_RETCODE_NO_CHANGES))g_trade.PositionClose(ticket);
   }
   else if(!StopProtectsCash(side,vol,open,sl,lock))
      g_trade.PositionClose(ticket);
}

void MicroCurrentTick(const MqlTick &tick)
{
   const long m=(long)tick.time_msc/60000;
   if(m!=g_entryMinute){g_entryMinute=m;g_entriesThisMinute=0;}
   RefreshRisk(false);
   if(!InpEnableDemoOrders)return;
   if(g_riskHalt || g_dayHalt){CloseOwnOnRisk();return;}
   ulong ticket;ENUM_POSITION_TYPE type;double open,stop,vol;long openedMs;
   if(OwnPosition(ticket,type,open,stop,vol,openedMs))
   {ManageOwnPosition(tick);return;}
   if(!InpEnableDemoOrders || g_dataFault || g_entriesThisMinute>=InpMaxEntriesPerMinute)return;
   // Closed position does not automatically rearm on 5s only.
   if(g_exitMs>0 && ((long)tick.time_msc-g_exitMs<3000 ||
       g_5s.startMs==g_exit5 || g_15s.startMs==g_exit15))return;
   int side=0;
   if(MicroSignal(tick,side))MicroSendEntry(tick,side);
}

int OnInit()
{
   if(_Symbol!="XAUUSD" || InpLots<=0 || InpMaxEntriesPerMinute<1 || InpMaxEntriesPerMinute>4 ||
      InpMaxHoldMs<1000 || InpBaseStopPricePoints<=0 ||
      InpMaxIntendedLossCash<=InpMinNetProfitCash ||
      InpPreferredNetProfitCash<=InpMinNetProfitCash ||
      InpCapitalFloorPct<=0 || InpCapitalFloorPct>=100 ||
      InpMaxPeakDrawdownPct<=0 || InpMaxPeakDrawdownPct>InpCapitalFloorPct ||
      InpAdditionalCostCash<0 || InpExtraSlipReserveCash<0)return INIT_PARAMETERS_INCORRECT;
   if(InpEnableDemoOrders &&
     (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO)
   {Print("R9 micro180: DEMO ONLY; production order mode refused");return INIT_PARAMETERS_INCORRECT;}
   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpDeviationPoints);
   g_trade.SetAsyncMode(false);
   if(!g_trade.SetTypeFillingBySymbol(_Symbol))return INIT_FAILED;
   g_hADX=iADXWilder(_Symbol,PERIOD_M1,InpADXWilderPeriod);
   g_hEMA=iMA(_Symbol,PERIOD_M1,InpEMAPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_hATR1=iATR(_Symbol,PERIOD_M1,InpATRPeriod);
   g_hATR5=iATR(_Symbol,PERIOD_M5,InpATRPeriod);
   if(g_hATR5==INVALID_HANDLE)return INIT_FAILED;
   g_riskKey="R9M180."+IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN));
   const double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity<=0 || !GVEnsure(g_riskKey+".base",equity) || !GVEnsure(g_riskKey+".peak",equity))return INIT_FAILED;
   g_accountBase=GlobalVariableGet(g_riskKey+".base");
   g_accountPeak=GlobalVariableGet(g_riskKey+".peak");
   if(g_accountBase<=0 || g_accountPeak<=0)return INIT_FAILED;
   RefreshRisk(true);
   if(!EventSetTimer(1))return INIT_FAILED;
   Print("R9 MICRO180: isolated demo-only research fork; 5/15/30ms candle streams, 180s buffer; old model OFF; real volume unavailable; live NOT certified");
   return INIT_SUCCEEDED;
}
void OnDeinit(const int reason)
{
   EventKillTimer();
   if(g_hADX!=INVALID_HANDLE)IndicatorRelease(g_hADX);
   if(g_hEMA!=INVALID_HANDLE)IndicatorRelease(g_hEMA);
   if(g_hATR1!=INVALID_HANDLE)IndicatorRelease(g_hATR1);
   if(g_hATR5!=INVALID_HANDLE)IndicatorRelease(g_hATR5);
   GlobalVariablesFlush();
}
void OnTick()
{
   MqlTick latest;
   if(!SymbolInfoTick(_Symbol,latest) || latest.bid<=0 || latest.ask<latest.bid)return;
   // Backfill every available real tick for features, but trade ONLY the latest.
   if(!SyncQuoteHistory(latest))return;
   if(g_lastQuoteMs!=(long)latest.time_msc)return;
   MqlTick current;
   if(!SymbolInfoTick(_Symbol,current) || current.time_msc!=latest.time_msc ||
      current.bid!=latest.bid || current.ask!=latest.ask)return;
   MicroCurrentTick(current);
}
void OnTimer()
{
   RefreshRisk(false);
   if(!InpEnableDemoOrders)return;
   if(g_riskHalt || g_dayHalt)CloseOwnOnRisk();
   MqlTick latest;
   if(!SymbolInfoTick(_Symbol,latest))return;
   // Failsafe holding-time check even if no NewTick event is enqueued.
   ulong ticket;ENUM_POSITION_TYPE type;double open,sl,vol;long openedMs;
   if(OwnPosition(ticket,type,open,sl,vol,openedMs))
   {
      if((long)TimeTradeServer()*1000-openedMs>=InpMaxHoldMs ||
         (g_riskHalt || g_dayHalt))g_trade.PositionClose(ticket);
   }
}
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   if(trans.type!=TRADE_TRANSACTION_DEAL_ADD || trans.deal==0)return;
   if(!HistoryDealSelect(trans.deal))return;
   if(HistoryDealGetString(trans.deal,DEAL_SYMBOL)!=_Symbol ||
      (ulong)HistoryDealGetInteger(trans.deal,DEAL_MAGIC)!=InpMagic)return;
   const ENUM_DEAL_ENTRY state=(ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal,DEAL_ENTRY);
   if(state==DEAL_ENTRY_OUT || state==DEAL_ENTRY_OUT_BY || state==DEAL_ENTRY_INOUT)
   {
      g_exitMs=(long)HistoryDealGetInteger(trans.deal,DEAL_TIME_MSC);
      g_exit5=g_5s.startMs;g_exit15=g_15s.startMs;
      g_entryMs=0;g_peakObservedNet=-1e30;
   }
}
