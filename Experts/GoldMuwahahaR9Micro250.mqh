#ifndef __GMM_R9_V5_MICRO250_MQH__
#define __GMM_R9_V5_MICRO250_MQH__
// RESEARCH SHADOW ONLY: source-ordered 250ms quote motion, not trade volume.
// Include AFTER g_prevQuoteMs and other required globals in V5 research EA.
// Exactly 720 completed + one active quarter-bin; no missing-bin synthesis.
#define V5_Q250_BINS 720

struct V5QuarterBin
{
   long startMs,firstMs,lastMs;
   double firstBid,firstAsk,lastBid,lastAsk,pathBid,pathAsk;
   int n,up,down,observed;
};
V5QuarterBin g_q250[V5_Q250_BINS],g_q250Cur;
int g_q250Head=0,g_q250Count=0;
bool g_q250Ready=false;

void V5QuarterReset(V5QuarterBin &b,const MqlTick &t,const long start)
{
   b.startMs=start;b.firstMs=(long)t.time_msc;b.lastMs=(long)t.time_msc;
   b.firstBid=t.bid;b.firstAsk=t.ask;b.lastBid=t.bid;b.lastAsk=t.ask;
   b.pathBid=0.0;b.pathAsk=0.0;
   b.n=1;b.up=0;b.down=0;b.observed=0;
}
void V5QuarterMotion(V5QuarterBin &b,const double db,const double da)
{
   b.pathBid+=MathAbs(db);b.pathAsk+=MathAbs(da);
   b.observed++;
   if(db>0.0 && da>0.0)b.up++;
   if(db<0.0 && da<0.0)b.down++;
}
void V5QuarterUpdate(const MqlTick &t)
{
   const long ms=(long)t.time_msc;
   const long start=ms/250*250;
   const double db=g_q250Ready?t.bid-g_q250Cur.lastBid:0.0;
   const double da=g_q250Ready?t.ask-g_q250Cur.lastAsk:0.0;
   const bool valid=g_q250Ready && g_prevQuoteMs>0 &&
                    ms-g_prevQuoteMs<=2500;
   if(!g_q250Ready || start!=g_q250Cur.startMs)
   {
      if(g_q250Ready)
      {
         g_q250[g_q250Head]=g_q250Cur;
         g_q250Head=(g_q250Head+1)%V5_Q250_BINS;
         if(g_q250Count<V5_Q250_BINS)g_q250Count++;
      }
      V5QuarterReset(g_q250Cur,t,start);
      if(valid)V5QuarterMotion(g_q250Cur,db,da);
      g_q250Ready=true;
   }
   else
   {
      g_q250Cur.lastMs=ms;g_q250Cur.lastBid=t.bid;g_q250Cur.lastAsk=t.ask;
      g_q250Cur.n++;
      if(valid)V5QuarterMotion(g_q250Cur,db,da);
   }
}
bool V5QuarterEvidence(const int side,const long now,
                       double &eff,double &coh)
{
   eff=0.0;coh=0.0;
   if(!g_q250Ready || now-g_q250Cur.lastMs>2500)return false;
   const long minStart=now/250*250-5000;
   int bins=0,observed=0,joined=0;
   long prevStart=-1;
   double first=0.0,last=0.0,travel=0.0;
   for(int off=g_q250Count-1;off>=0;--off)
   {
      int idx=g_q250Head-1-off;
      while(idx<0)idx+=V5_Q250_BINS;
      V5QuarterBin b=g_q250[idx%V5_Q250_BINS];
      if(b.startMs<minStart)continue;
      if(prevStart>=0 && b.startMs-prevStart>2500)return false;
      if(bins==0)first=side>0?b.firstBid:b.firstAsk;
      last=side>0?b.lastBid:b.lastAsk;
      travel+=side>0?b.pathBid:b.pathAsk;
      joined+=side>0?b.up:b.down;
      observed+=b.observed;
      prevStart=b.startMs;bins++;
   }
   if(g_q250Cur.startMs>=minStart)
   {
      if(prevStart>=0 && g_q250Cur.startMs-prevStart>2500)return false;
      if(bins==0)first=side>0?g_q250Cur.firstBid:g_q250Cur.firstAsk;
      last=side>0?g_q250Cur.lastBid:g_q250Cur.lastAsk;
      travel+=side>0?g_q250Cur.pathBid:g_q250Cur.pathAsk;
      joined+=side>0?g_q250Cur.up:g_q250Cur.down;
      observed+=g_q250Cur.observed;
      bins++;
   }
   if(bins<2 || observed==0)return false;
   const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(point<=0.0)return false;
   eff=MathMax(-1.0,MathMin(1.0,side*(last-first)/MathMax(point,travel)));
   coh=(double)joined/(double)observed;
   return true;
}
#endif
