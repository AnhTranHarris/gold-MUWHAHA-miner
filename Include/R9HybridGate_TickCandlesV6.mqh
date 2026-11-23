// R9 HybridGate V6 — source-tick completed-candle observer, NO order actions.
// Only as-of observations. Quotes may be coalesced in OnTick; for complete
// source verification, feed a full ordered CopyTicksRange or Coinexx TickLogger.
#ifndef R9_HYBRIDGATE_TICKCANDLES_V6
#define R9_HYBRIDGATE_TICKCANDLES_V6
#define R9_V6_FRAME_COUNT 9
#define R9_V6_CANDLE_CAP 64
struct R9V6Candle
{
   long bucket;
   long first_msc;
   long last_msc;
   double open;
   double high;
   double low;
   double close;
   int observed_ticks;
};
struct R9V6CandleSeries
{
   R9V6Candle active;
   R9V6Candle completed[R9_V6_CANDLE_CAP];
   bool initialized;
   int head;
   int count;
};
class CR9V6TickCandles
{
private:
   R9V6CandleSeries m_frames[R9_V6_FRAME_COUNT];
   long m_last_msc;
   ulong m_count;
   ulong m_bad_order;
   long FrameMillis(const int frame)const
   {
      switch(frame)
      {
         case 0:return 250;
         case 1:return 1000;
         case 2:return 5000;
         case 3:return 15000;
         case 4:return 30000;
         case 5:return 60000;
         case 6:return 300000;
         case 7:return 900000;
         case 8:return 3600000;
      }
      return 0;
   }
   void NewActive(const int frame,const long bucket,const long msc,const double price)
   {
      m_frames[frame].active.bucket=bucket;
      m_frames[frame].active.first_msc=msc;
      m_frames[frame].active.last_msc=msc;
      m_frames[frame].active.open=price;
      m_frames[frame].active.high=price;
      m_frames[frame].active.low=price;
      m_frames[frame].active.close=price;
      m_frames[frame].active.observed_ticks=1;
      m_frames[frame].initialized=true;
   }
   void PushFrame(const int frame,const MqlTick &tick)
   {
      const long msc=(long)tick.time_msc;
      const long bucket=msc/FrameMillis(frame);
      const double price=tick.bid; // Original R9 S1 source convention.
      if(!m_frames[frame].initialized)
      {
         NewActive(frame,bucket,msc,price);
         return;
      }
      if(bucket!=m_frames[frame].active.bucket)
      {
         const int h=m_frames[frame].head;
         m_frames[frame].completed[h]=m_frames[frame].active;
         m_frames[frame].head=(h+1)%R9_V6_CANDLE_CAP;
         if(m_frames[frame].count<R9_V6_CANDLE_CAP)m_frames[frame].count++;
         NewActive(frame,bucket,msc,price);
         return;
      }
      m_frames[frame].active.last_msc=msc;
      if(price>m_frames[frame].active.high)m_frames[frame].active.high=price;
      if(price<m_frames[frame].active.low)m_frames[frame].active.low=price;
      m_frames[frame].active.close=price;
      m_frames[frame].active.observed_ticks++;
   }
public:
   CR9V6TickCandles(){Reset();}
   void Reset()
   {
      m_last_msc=-1;m_count=0;m_bad_order=0;
      for(int i=0;i<R9_V6_FRAME_COUNT;i++)
      {
         m_frames[i].initialized=false;
         m_frames[i].head=0;
         m_frames[i].count=0;
      }
   }
   bool Push(const MqlTick &tick)
   {
      if(tick.time_msc<=0 || tick.bid<=0.0 || tick.ask<tick.bid)return false;
      const long t=(long)tick.time_msc;
      if(m_last_msc>=0 && t<m_last_msc){m_bad_order++;return false;}
      // Same-millisecond rows are independent; never deduplicate by timestamp.
      m_last_msc=t;m_count++;
      for(int i=0;i<R9_V6_FRAME_COUNT;i++)PushFrame(i,tick);
      return true;
   }
   bool Closed(const int frame,const int newest_offset,R9V6Candle &result)const
   {
      if(frame<0 || frame>=R9_V6_FRAME_COUNT || newest_offset<0)return false;
      if(newest_offset>=m_frames[frame].count)return false;
      int index=m_frames[frame].head-1-newest_offset;
      while(index<0)index+=R9_V6_CANDLE_CAP;
      result=m_frames[frame].completed[index];
      return true;
   }
   int CompletedCount(const int frame)const
   {
      if(frame<0 || frame>=R9_V6_FRAME_COUNT)return 0;
      return m_frames[frame].count;
   }
   ulong Count()const{return m_count;}
   ulong OutOfOrder()const{return m_bad_order;}
   long LastMillis()const{return m_last_msc;}
};
#endif
