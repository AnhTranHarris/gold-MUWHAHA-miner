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
