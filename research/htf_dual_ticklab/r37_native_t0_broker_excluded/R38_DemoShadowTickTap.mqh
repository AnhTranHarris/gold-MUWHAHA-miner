#ifndef R38_DEMO_SHADOW_TICK_TAP_MQH
#define R38_DEMO_SHADOW_TICK_TAP_MQH
// Research-only source envelope capture for original R34/R36 Python shadow.
// No trade commands, no active veto. Must be called in the original EA at its
// genuine, pre-OrderSend intent boundary for representative signal supply.
class CR38DemoShadowTickTap
  {
private:
   int m_file;
   string m_broker;
   string m_symbol;
   long m_last_msc;
   ulong m_same_ms_seen;
   ulong m_quote_ordinal;
   bool m_healthy;
   void Append(const string line)
     {
      if(m_file==INVALID_HANDLE) {m_healthy=false;return;}
      FileWriteString(m_file,line+"\r\n");
      FileFlush(m_file);
     }
   bool SafeId(const string id)
     {
      if(StringLen(id)<1 || StringLen(id)>100)return false;
      for(int k=0;k<StringLen(id);k++)
        {
         ushort c=StringGetCharacter(id,k);
         if(!((c>=48 && c<=57)||(c>=65 && c<=90)||(c>=97 && c<=122)||c==45||c==95))return false;
        }
      return true;
     }
public:
   CR38DemoShadowTickTap():m_file(INVALID_HANDLE),m_broker(""),m_symbol(""),m_last_msc(0),m_same_ms_seen(0),m_quote_ordinal(0),m_healthy(false){}
   bool Start(const string broker,const string symbol,const string filename)
     {
      if(AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO)return false;
      if(broker!="coinexx" && broker!="dukascopy")return false;
      m_broker=broker;m_symbol=symbol;
      m_file=FileOpen(filename,FILE_COMMON|FILE_READ|FILE_WRITE|FILE_TXT|FILE_SHARE_READ|FILE_SHARE_WRITE);
      if(m_file==INVALID_HANDLE)return false;
      FileSeek(m_file,0,SEEK_END);
      MqlTick current;
      if(!SymbolInfoTick(symbol,current)){FileClose(m_file);m_file=INVALID_HANDLE;return false;}
      // A new observer has no reliable current same-ms replay ordinal. Begin
      // at NEXT millisecond, cold-start and abstain until feature warm-up.
      m_last_msc=(long)current.time_msc+1;
      m_same_ms_seen=0;m_quote_ordinal=0;m_healthy=true;
      return true;
     }
   void Stop()
     {
      if(m_file!=INVALID_HANDLE){FileFlush(m_file);FileClose(m_file);m_file=INVALID_HANDLE;}
      m_healthy=false;
     }
   bool Healthy(){return m_healthy;}
   ulong LastOrdinal(){return m_quote_ordinal;}
   long LastMsc(){return m_last_msc;}
   void ObserveTicks()
     {
      if(!m_healthy)return;
      for(int batch=0;batch<32;batch++)
        {
         MqlTick q[];
         int count=CopyTicks(m_symbol,q,COPY_TICKS_ALL,(ulong)m_last_msc,4096);
         if(count<0){m_healthy=false;return;}
         if(count==0)return;
         const long initial_ms=m_last_msc;
         const ulong initial_seen=m_same_ms_seen;
         ulong same_skipped=0;
         int new_count=0;
         for(int i=0;i<count;i++)
           {
            long ms=(long)q[i].time_msc;
            if(ms<m_last_msc)continue;
            if(ms==initial_ms && same_skipped<initial_seen){same_skipped++;continue;}
            if(ms>m_last_msc){m_last_msc=ms;m_same_ms_seen=0;}
            m_same_ms_seen++;m_quote_ordinal++;new_count++;
            if(!MathIsValidNumber(q[i].bid) || !MathIsValidNumber(q[i].ask) || q[i].ask<q[i].bid || q[i].bid<=0)
              {m_healthy=false;return;}
            string line=StringFormat("{\"type\":\"quote\",\"broker\":\"%s\",\"msc\":%I64d,\"ordinal\":%I64u,\"bid\":%s,\"ask\":%s}",
             m_broker,ms,m_quote_ordinal,DoubleToString(q[i].bid,8),DoubleToString(q[i].ask,8));
            Append(line);
            if(!m_healthy)return;
           }
         if(count<4096)return;
         if(new_count==0){m_healthy=false;return;}
        }
      // More than bounded 32*4096 updates waiting. Do not silently drop the backlog.
      m_healthy=false;
     }
   bool RecordIntent(const string event_id,const int side,const long original_t0_msc,
                     const ulong source_quote_ordinal,const bool already_filled)
     {
      if(!m_healthy || !SafeId(event_id) || (side!=1 && side!=-1))return false;
      if(original_t0_msc>m_last_msc || source_quote_ordinal>m_quote_ordinal)return false;
      string filled=already_filled?"true":"false";
      Append(StringFormat("{\"type\":\"intent\",\"broker\":\"%s\",\"event_id\":\"%s\",\"t0_msc\":%I64d,\"side\":%d,\"source_quote_ordinal\":%I64u,\"already_filled\":%s}",
      m_broker,event_id,original_t0_msc,side,source_quote_ordinal,filled));
      return m_healthy;
     }
  };
#endif
