#ifndef GM_R9_M60_QRB_QAF_SHADOW_INCLUDED
#define GM_R9_M60_QRB_QAF_SHADOW_INCLUDED
// R9 M60 quote-flow SHADOW, v1.  NO trade decisions, orders, or stops.
// QRB/QAF describe observed Bid/Ask revisions, NOT actual traded volume or L2 OFI.
// OnTick observation may miss updates when MT5 coalesces NewTick events.

#define GM_M60_NWINDOWS 7
#define GM_M60_NQAF 3
#define GM_M60_SECOND_CAP 65

struct GM_M60_Quote
{
   long ms;
   long sequence;
   long cum_qrb;
   long cum_up;
   long cum_down;
   long cum_widen;
   long cum_tighten;
};

struct GM_M60_Second
{
   long sec;
   double high;
   double low;
   double close;
   long count;
};

struct GM_M60_FlowWindow
{
   bool ready;
   double qrb;
   double signed_fraction;
   double spread_pressure;
   double quote_activity_log;
   long revisions;
};

class CGM_M60_QuoteFlowShadow
{
private:
   GM_M60_Quote m_quotes[];
   GM_M60_Second m_seconds[GM_M60_SECOND_CAP];
   int m_capacity,m_head,m_count,m_sec_head,m_sec_count,m_file;
   long m_sequence,m_qrb,m_up,m_down,m_widen,m_tighten,m_last_ms;
   double m_last_mid,m_last_spread;
   bool m_has_last,m_second_open;
   GM_M60_Second m_active_sec;
   long m_windows[GM_M60_NWINDOWS];
   long m_qaf_windows[GM_M60_NQAF];

   int Slot(const int logical) const
   {
      return (m_head+logical)%m_capacity;
   }

   void ResetHistory()
   {
      m_head=0;m_count=0;m_sec_head=0;m_sec_count=0;
      m_sequence=0;m_qrb=0;m_up=0;m_down=0;m_widen=0;m_tighten=0;
      m_last_ms=0;m_last_mid=0.0;m_last_spread=0.0;
      m_has_last=false;m_second_open=false;
   }

   void PushSecond()
   {
      if(!m_second_open) return;
      int pos;
      if(m_sec_count<GM_M60_SECOND_CAP)
      {
         pos=(m_sec_head+m_sec_count)%GM_M60_SECOND_CAP;
         m_sec_count++;
      }
      else
      {
         pos=m_sec_head;
         m_sec_head=(m_sec_head+1)%GM_M60_SECOND_CAP;
      }
      m_seconds[pos]=m_active_sec;
   }

   bool ComputeWindow(const long now,const long width,GM_M60_FlowWindow &out) const
   {
      out.ready=false;out.qrb=0.0;out.signed_fraction=0.0;
      out.spread_pressure=0.0;out.quote_activity_log=0.0;out.revisions=0;
      if(m_count<2) return false;
      const GM_M60_Quote oldest=m_quotes[Slot(0)];
      if(now-oldest.ms<width) return false;  // No full historical coverage; never fill with zeros.
      const long cutoff=now-width;
      int lo=0,hi=m_count;
      while(lo<hi)
      {
         const int mid=lo+(hi-lo)/2;
         const GM_M60_Quote q=m_quotes[Slot(mid)];
         if(q.ms<cutoff) lo=mid+1; else hi=mid;
      }
      if(lo>=m_count) return false;
      const GM_M60_Quote first=m_quotes[Slot(lo)];
      const GM_M60_Quote last=m_quotes[Slot(m_count-1)];
      // Match prior Python convention: exclude first event's incoming delta.
      const long n=last.sequence-first.sequence;
      if(n<=0 || now<=first.ms) return false;
      const long up=last.cum_up-first.cum_up;
      const long down=last.cum_down-first.cum_down;
      const long wid=last.cum_widen-first.cum_widen;
      const long tight=last.cum_tighten-first.cum_tighten;
      out.qrb=(double)(last.cum_qrb-first.cum_qrb);
      out.signed_fraction=out.qrb/(double)(up+down+1);
      out.spread_pressure=(double)(wid-tight)/(double)(n+1);
      out.quote_activity_log=MathLog(1.0+(double)n*1000.0/(double)(now-first.ms));
      out.revisions=n;
      out.ready=true;
      return true;
   }

   bool ComputeQAF(const long entry_sec,const long span,double &value) const
   {
      // Only COMPLETED seconds strictly before the entry's current second.
      double numerator=0.0,denominator=0.0;
      for(int i=0;i<m_sec_count;++i)
      {
         const GM_M60_Second s=m_seconds[(m_sec_head+i)%GM_M60_SECOND_CAP];
         if(s.sec<entry_sec-span || s.sec>=entry_sec) continue;
         double close_location=0.0;
         if(s.high>s.low)
            close_location=(2.0*s.close-s.high-s.low)/(s.high-s.low);
         numerator+=(double)s.count*close_location;
         denominator+=(double)s.count;
      }
      if(denominator<=0.0) return false;
      value=numerator/denominator;
      return true;
   }

   string F(const bool ready,const double v) const
   {
      if(!ready) return "NA";
      return DoubleToString(v,8);
   }

public:
   CGM_M60_QuoteFlowShadow()
   {
      m_capacity=0;m_file=INVALID_HANDLE;
      m_windows[0]=100;m_windows[1]=500;m_windows[2]=1000;
      m_windows[3]=3000;m_windows[4]=5000;m_windows[5]=15000;m_windows[6]=60000;
      m_qaf_windows[0]=5;m_qaf_windows[1]=15;m_qaf_windows[2]=60;
      ResetHistory();
   }

   bool Init(const int capacity,const string file_name)
   {
      if(capacity<128 || capacity>131072) return false;
      m_capacity=capacity;
      if(ArrayResize(m_quotes,m_capacity)!=m_capacity) return false;
      ResetHistory();
      if(file_name=="") return false;
      m_file=FileOpen(file_name,FILE_COMMON|FILE_CSV|FILE_READ|FILE_WRITE|FILE_SHARE_READ,',');
      if(m_file==INVALID_HANDLE) return false;
      const bool empty=(FileSize(m_file)==0);
      FileSeek(m_file,0,SEEK_END);
      if(empty)
      {
         FileWrite(m_file,"time_msc","side","bid","ask","source","qrb_100ms","frac_100ms","spread_100ms","activity_100ms",
            "qrb_500ms","frac_500ms","spread_500ms","activity_500ms",
            "qrb_1000ms","frac_1000ms","spread_1000ms","activity_1000ms",
            "qrb_3000ms","frac_3000ms","spread_3000ms","activity_3000ms",
            "qrb_5000ms","frac_5000ms","spread_5000ms","activity_5000ms",
            "qrb_15000ms","frac_15000ms","spread_15000ms","activity_15000ms",
            "qrb_60000ms","frac_60000ms","spread_60000ms","activity_60000ms",
            "qaf_completed_5s","qaf_completed_15s","qaf_completed_60s");
      }
      return true;
   }

   void Observe(const MqlTick &tick)
   {
      if(m_capacity<=0 || tick.bid<=0.0 || tick.ask<tick.bid) return;
      const long now=tick.time_msc;
      if(m_has_last && now<m_last_ms) ResetHistory(); // nonmonotone clock; no false continuity
      const double mid=(tick.bid+tick.ask)*0.5;
      const double spread=tick.ask-tick.bid;
      int direction=0,spread_direction=0;
      if(m_has_last)
      {
         if(mid>m_last_mid+1e-9) direction=1;
         else if(mid<m_last_mid-1e-9) direction=-1;
         if(spread>m_last_spread+1e-9) spread_direction=1;
         else if(spread<m_last_spread-1e-9) spread_direction=-1;
      }
      m_qrb+=direction;
      if(direction>0) m_up++; else if(direction<0) m_down++;
      if(spread_direction>0) m_widen++; else if(spread_direction<0) m_tighten++;
      m_sequence++;
      GM_M60_Quote q;
      q.ms=now;q.sequence=m_sequence;q.cum_qrb=m_qrb;
      q.cum_up=m_up;q.cum_down=m_down;q.cum_widen=m_widen;q.cum_tighten=m_tighten;
      int pos;
      if(m_count<m_capacity){pos=Slot(m_count);m_count++;}
      else{pos=m_head;m_head=(m_head+1)%m_capacity;}
      m_quotes[pos]=q;
      // Keep one predecessor quote older than 60s to establish complete window coverage.
      // Amortized O(1) eviction outside largest rolling window.
      while(m_count>2 && now-m_quotes[Slot(1)].ms>60000)
      {m_head=(m_head+1)%m_capacity;m_count--;}
      const long sec=now/1000;
      if(!m_second_open || sec!=m_active_sec.sec)
      {
         if(m_second_open) PushSecond();
         m_second_open=true;m_active_sec.sec=sec;
         m_active_sec.high=mid;m_active_sec.low=mid;m_active_sec.close=mid;m_active_sec.count=1;
      }
      else
      {
         if(mid>m_active_sec.high) m_active_sec.high=mid;
         if(mid<m_active_sec.low) m_active_sec.low=mid;
         m_active_sec.close=mid;m_active_sec.count++;
      }
      m_last_ms=now;m_last_mid=mid;m_last_spread=spread;m_has_last=true;
   }

   void LogCandidate(const MqlTick &tick,const int side)
   {
      if(m_file==INVALID_HANDLE || !m_has_last || tick.time_msc!=m_last_ms) return;
      GM_M60_FlowWindow w[GM_M60_NWINDOWS];
      for(int j=0;j<GM_M60_NWINDOWS;j++) ComputeWindow(tick.time_msc,m_windows[j],w[j]);
      double qaf[GM_M60_NQAF];bool ready[GM_M60_NQAF];
      for(int j=0;j<GM_M60_NQAF;j++)
      {
         qaf[j]=0.0;
         ready[j]=ComputeQAF(tick.time_msc/1000,m_qaf_windows[j],qaf[j]);
      }
      FileWrite(m_file,tick.time_msc,side,DoubleToString(tick.bid,_Digits),DoubleToString(tick.ask,_Digits),"ON_TICK_UNVERIFIED_PARITY",
         F(w[0].ready,w[0].qrb),F(w[0].ready,w[0].signed_fraction),F(w[0].ready,w[0].spread_pressure),F(w[0].ready,w[0].quote_activity_log),
         F(w[1].ready,w[1].qrb),F(w[1].ready,w[1].signed_fraction),F(w[1].ready,w[1].spread_pressure),F(w[1].ready,w[1].quote_activity_log),
         F(w[2].ready,w[2].qrb),F(w[2].ready,w[2].signed_fraction),F(w[2].ready,w[2].spread_pressure),F(w[2].ready,w[2].quote_activity_log),
         F(w[3].ready,w[3].qrb),F(w[3].ready,w[3].signed_fraction),F(w[3].ready,w[3].spread_pressure),F(w[3].ready,w[3].quote_activity_log),
         F(w[4].ready,w[4].qrb),F(w[4].ready,w[4].signed_fraction),F(w[4].ready,w[4].spread_pressure),F(w[4].ready,w[4].quote_activity_log),
         F(w[5].ready,w[5].qrb),F(w[5].ready,w[5].signed_fraction),F(w[5].ready,w[5].spread_pressure),F(w[5].ready,w[5].quote_activity_log),
         F(w[6].ready,w[6].qrb),F(w[6].ready,w[6].signed_fraction),F(w[6].ready,w[6].spread_pressure),F(w[6].ready,w[6].quote_activity_log),
         F(ready[0],qaf[0]),F(ready[1],qaf[1]),F(ready[2],qaf[2]));
   }

   void Close()
   {
      if(m_file!=INVALID_HANDLE){FileFlush(m_file);FileClose(m_file);m_file=INVALID_HANDLE;}
      ArrayFree(m_quotes);m_capacity=0;
   }
};

#endif // GM_R9_M60_QRB_QAF_SHADOW_INCLUDED
