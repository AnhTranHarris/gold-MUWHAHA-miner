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
