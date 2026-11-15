#ifndef __GMM_R9_V6_PAST_ONLY_CASH_MQH__
#define __GMM_R9_V6_PAST_ONLY_CASH_MQH__
// RESEARCH ONLY / V6 economic proxy. Include after QBar/g_s/g_sh/g_sn.
// No executed volume, depth or high-AUC. Only COMPLETED real quote seconds.
// No synthetic 250 ms bars or future readings. Cash via OrderCalcProfit.
// MQL5 ↔ Python indicator / risk / fill parity NOT certified.

#define V6_HORIZON 6
#define V6_STRIDE 8
#define V6_MIN_OBS 8

struct V6CashHistory
{
   int n;
   double meanNet,penalizedNet,profitFraction,lossFraction,worstNet;
   int skippedGaps;
};

bool V6PastFirstPassage(const int side,const MqlTick &now,
                        const double vol,V6CashHistory &out)
{
   out.n=0;out.meanNet=0;out.penalizedNet=-DBL_MAX;
   out.profitFraction=0;out.lossFraction=0;out.worstNet=DBL_MAX;
   out.skippedGaps=0;
   if(side!=1 && side!=-1)return false;
   if(g_sn<V6_HORIZON+V6_MIN_OBS*V6_STRIDE)return false;
   double total=0.0,sq=0.0;
   int hitProfit=0,hitLoss=0;
   const ENUM_ORDER_TYPE kind=(side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL);
   for(int i=0;i+V6_HORIZON<g_sn;i+=V6_STRIDE)
   {
      QBar anchor=g_s[SecFromLatest(g_sn-1-i)];
      if((long)now.time_msc-anchor.startMs>180000)continue;
      double entry=side>0?anchor.ac:anchor.bc;
      bool valid=true;
      double observedNet=0.0;
      for(int j=1;j<=V6_HORIZON;++j)
      {
         QBar previous=g_s[SecFromLatest(g_sn-i-j)];
         QBar current=g_s[SecFromLatest(g_sn-1-i-j)];
         // These are actual finished 1s bars, no missing-second OHLC fill.
         const long msGap=current.startMs-previous.startMs;
         if(msGap<=0 || msGap>2000){valid=false;break;}
         const double liquidation=side>0?current.bc:current.ac;
         double gross=0.0;
         if(!OrderCalcProfit(kind,_Symbol,vol,entry,liquidation,gross))
           {valid=false;break;}
         observedNet=gross-InpAdditionalCostCash;
         if(observedNet>=InpMinNetProfitCash)
         {hitProfit++;break;}
         if(observedNet<=-InpMaxIntendedLossCash)
         {hitLoss++;break;}
      }
      if(!valid){out.skippedGaps++;continue;}
      total+=observedNet;sq+=observedNet*observedNet;
      out.worstNet=MathMin(out.worstNet,observedNet);
      out.n++;
   }
   if(out.n<V6_MIN_OBS)return false;
   out.meanNet=total/out.n;
   const double variance=MathMax(0.0,(sq-out.n*out.meanNet*out.meanNet)/
                                MathMax(1,out.n-1));
   out.penalizedNet=out.meanNet-InpV6UncertaintyMultiplier*
                    MathSqrt(variance/out.n);
   out.profitFraction=(double)hitProfit/out.n;
   out.lossFraction=(double)hitLoss/out.n;
   return true;
}

// Compare incremental holding against immediate liquidation. Entry spread and
// already incurred commission must NOT be paid again in this quantity.
bool V6PastHoldIncrement(const int side,const MqlTick &now,const double vol,
                         double &penalizedIncrement)
{
   penalizedIncrement=-DBL_MAX;
   if(side!=1 && side!=-1 || g_sn<32)return false;
   const ENUM_ORDER_TYPE kind=(side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL);
   int count=0;double total=0.0,sq=0.0;
   for(int i=0;i+3<g_sn;i+=V6_STRIDE)
   {
      QBar start=g_s[SecFromLatest(g_sn-1-i)];
      if((long)now.time_msc-start.startMs>180000)continue;
      QBar end=g_s[SecFromLatest(g_sn-1-i-3)];
      bool valid=true;
      for(int j=1;j<=3;++j)
      {
         QBar p=g_s[SecFromLatest(g_sn-i-j)];
         QBar n=g_s[SecFromLatest(g_sn-1-i-j)];
         if(n.startMs-p.startMs<=0 || n.startMs-p.startMs>2000)
         {valid=false;break;}
      }
      if(!valid)continue;
      const double priceStart=side>0?start.bc:start.ac;
      const double priceEnd=side>0?end.bc:end.ac;
      double increment=0.0;
      if(!OrderCalcProfit(kind,_Symbol,vol,priceStart,priceEnd,increment))
        return false;
      total+=increment;sq+=increment*increment;count++;
   }
   if(count<V6_MIN_OBS)return false;
   const double m=total/count;
   const double variance=MathMax(0.0,(sq-count*m*m)/MathMax(1,count-1));
   penalizedIncrement=m-InpV6UncertaintyMultiplier*
                             MathSqrt(variance/count);
   return true;
}
#endif
