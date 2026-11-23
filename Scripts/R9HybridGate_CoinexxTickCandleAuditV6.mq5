// R9 HybridGate V6 source-only CopyTicksRange audit.
// Research script, no trading actions. Requires Include/R9HybridGate_TickCandlesV6.mqh
#property strict
#property script_show_inputs
#include <R9HybridGate_TickCandlesV6.mqh>
input datetime InpFrom=D'2026.01.02 00:00:00';
input datetime InpUntil=D'2026.02.01 00:00:00';
input string InpAuditSymbol="XAUUSD";
void OnStart()
{
   if(InpUntil<=InpFrom){Print("Invalid date range");return;}
   CR9V6TickCandles builder;
   const ulong end_exclusive=(ulong)InpUntil*1000;
   ulong start=(ulong)InpFrom*1000;
   ulong seen=0;
   MqlTick quotes[];
   while(start<end_exclusive)
   {
      const ulong day_end=start+86400000-1;
      const ulong last=(day_end<end_exclusive-1)?day_end:end_exclusive-1;
      ResetLastError();
      const int count=CopyTicksRange(InpAuditSymbol,quotes,COPY_TICKS_ALL,start,last);
      if(count<0){PrintFormat("CopyTicksRange failed from=%I64u error=%d",start,GetLastError());return;}
      for(int i=0;i<count;i++)
      {
         if(!builder.Push(quotes[i])){PrintFormat("Rejected source tick at %I64d",quotes[i].time_msc);return;}
         seen++;
      }
      start=last+1;
   }
   PrintFormat("R9 V6 full tick-candle audit: ticks=%I64u lastms=%I64d outoforder=%I64u",seen,builder.LastMillis(),builder.OutOfOrder());
   for(int i=0;i<R9_V6_FRAME_COUNT;i++)
   {
      R9V6Candle bar;
      if(builder.Closed(i,0,bar))
         PrintFormat("frame=%d completed=%d bucket=%I64d O=%.5f H=%.5f L=%.5f C=%.5f quote_updates=%d",
                     i,builder.CompletedCount(i),bar.bucket,bar.open,bar.high,bar.low,bar.close,bar.observed_ticks);
   }
}