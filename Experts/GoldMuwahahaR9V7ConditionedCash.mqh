#ifndef __GMM_R9_V7_CONDITIONED_CASH_MQH__
#define __GMM_R9_V7_CONDITIONED_CASH_MQH__
// V7 RESEARCH SHADOW ONLY by default. Include AFTER QBar, g_s and SecFromLatest.
// Six-second past-first-passage, conditioned on signed 5s/15s *executable* path,
// spread ratio and QUOTE COUNT proxy. No trade-volume/DOM claim and no AUC.
// Not MetaEditor-compiled or parity-certified against the original-source Python.
// No historical bar is fabricated for a missing quote-second.
#define V7_MAX_BARS 181
#define V7_HORIZON 6
#define V7_STRIDE 7

struct V7ConditionedResult
{
   double mean,penalized,effective,firstProfit,firstAdverse;
   int samples,gapRejected;
   bool ready;
};
struct V7QuoteSetup
{
   double e5,e15,spreadRatio,quoteIntensity;
};
bool V7Continuous(QBar &q[],const int lo,const int hi)
{
   if(lo<0 || hi>=ArraySize(q) || hi<lo)return false;
   for(int i=lo+1;i<=hi;++i)
      if(q[i].startMs<=q[i-1].startMs || q[i].startMs-q[i-1].startMs>2000)return false;
   return true;
}
bool V7Setup(QBar &q[],const int i,const int side,
             const double bid,const double ask,const int quoteCount,
             V7QuoteSetup &f)
{
   if(i<15 || !V7Continuous(q,i-15,i-1))return false;
   double liq=(side>0?bid:ask);
   double first5=(side>0?q[i-5].bc:q[i-5].ac);
   double first15=(side>0?q[i-15].bc:q[i-15].ac);
   double travel5=0.0,travel15=0.0,prior5=first5,prior15=first15;
   double spreads[15];double sumCounts=0.0;
   for(int k=i-15;k<i;++k)
   {
      const double x=(side>0?q[k].bc:q[k].ac);
      if(k>i-15)travel15+=MathAbs(x-prior15);
      prior15=x;
      if(k>=i-5)
      {
         if(k>i-5)travel5+=MathAbs(x-prior5);
         prior5=x;
      }
      spreads[k-(i-15)]=q[k].ac-q[k].bc;
      sumCounts+=q[k].n;
   }
   travel5+=MathAbs(liq-prior5);
   travel15+=MathAbs(liq-prior15);
   f.e5=MathMax(-1.0,MathMin(1.0,side*(liq-first5)/MathMax(_Point,travel5)));
   f.e15=MathMax(-1.0,MathMin(1.0,side*(liq-first15)/MathMax(_Point,travel15)));
   ArraySort(spreads);
   f.spreadRatio=(ask-bid)/MathMax(_Point,spreads[7]);
   f.quoteIntensity=MathMin(4.0,(double)quoteCount/MathMax(1.0,sumCounts/15.0));
   return true;
}
bool V7PastConditioned(const int side,const MqlTick &now,
                       const double lots,V7ConditionedResult &out)
{
   out.ready=false;out.samples=0;out.gapRejected=0;
   out.mean=0;out.penalized=-DBL_MAX;out.effective=0;
   out.firstProfit=0;out.firstAdverse=0;
   if(side!=1 && side!=-1)return false;
   const long firstAllowed=(long)now.time_msc/1000*1000-180000;
   const long currentSecond=(long)now.time_msc/1000*1000;
   QBar history[];
   ArrayResize(history,V7_MAX_BARS);
   int n=0;
   for(int off=g_sn-1;off>=0;--off)
   {
      QBar v=g_s[SecFromLatest(off)];
      if(v.startMs<firstAllowed || v.startMs>=currentSecond)continue;
      if(n>=V7_MAX_BARS)return false;
      history[n]=v;n++;
   }
   if(n<30 || (long)now.time_msc-history[n-1].lastMs>2500)return false;
   if(!V7Continuous(history,n-15,n-1))return false;
   V7QuoteSetup current;
   if(!V7Setup(history,n,side,now.bid,now.ask,g_second.n,current))return false;
   double sumW=0,sumW2=0,sumWX=0,sumWX2=0,profitW=0,adverseW=0;
   const ENUM_ORDER_TYPE kind=(side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL);
   for(int i=15;i+V7_HORIZON<n;i+=V7_STRIDE)
   {
      if(!V7Continuous(history,i-15,i+V7_HORIZON))
      {out.gapRejected++;continue;}
      V7QuoteSetup past;
      if(!V7Setup(history,i,side,history[i].bc,history[i].ac,history[i].n,past))
      {out.gapRejected++;continue;}
      if(past.e5*current.e5<0 || past.e15*current.e15<0)continue;
      double d5=(past.e5-current.e5)/InpV7SimilarityWidth;
      double d15=(past.e15-current.e15)/InpV7SimilarityWidth;
      double ds=(past.spreadRatio-current.spreadRatio)/0.5;
      double dq=(past.quoteIntensity-current.quoteIntensity)/1.5;
      double w=MathExp(-0.5*(d5*d5+d15*d15+ds*ds+dq*dq));
      if(w<0.01)continue;
      double entry=(side>0?history[i].ac:history[i].bc);
      double cash=0.0;
      int hit=0;
      for(int j=i+1;j<=i+V7_HORIZON;++j)
      {
         double liq=(side>0?history[j].bc:history[j].ac);
         double gross=0.0;
         if(!OrderCalcProfit(kind,_Symbol,lots,entry,liq,gross))return false;
         cash=gross-InpAdditionalCostCash;
         if(cash>=InpMinNetProfitCash){hit=1;break;}
         if(cash<=-InpMaxIntendedLossCash){hit=-1;break;}
      }
      out.samples++;
      sumW+=w;sumW2+=w*w;sumWX+=w*cash;sumWX2+=w*cash*cash;
      if(hit>0)profitW+=w;
      if(hit<0)adverseW+=w;
   }
   if(out.samples==0 || sumW2<=0.0)return false;
   out.effective=sumW*sumW/sumW2;
   out.mean=sumWX/sumW;
   double variance=MathMax(0.0,sumWX2/sumW-out.mean*out.mean);
   out.penalized=out.mean-InpV7UncertaintyMultiplier*
                       MathSqrt(variance/MathMax(1.0,out.effective));
   out.firstProfit=profitW/sumW;
   out.firstAdverse=adverseW/sumW;
   out.ready=(out.effective>=InpV7MinEffectiveSamples);
   return out.ready;
}
#endif
