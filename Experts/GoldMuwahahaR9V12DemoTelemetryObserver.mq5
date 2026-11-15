//+------------------------------------------------------------------+
//| Gold MUWHAHAHA Miner R9 V12 — DEMO-ONLY transaction observer     |
//| Standalone research EA. NEVER sends, modifies or closes orders.  |
//| Not installed into R9/V9/V10/V11 or enabled by default.          |
//| Server deal timestamps differ from callback receipt timestamps. |
//+------------------------------------------------------------------+
#property strict
#property version "12.00"
#property description "Read-only demo execution telemetry. No order methods."

input bool   InpEnableObserver       = false;
input string InpExactSymbol          = "XAUUSD";
input ulong  InpExactMagic           = 0;          // 0 observes manual DEMO transactions only
input string InpOutputFilename       = "R9_V12_DEMO_EXECUTION_EVENTS.csv";

#define V12_ROWS 512
#define V12_DEALS 256

string g_rows[V12_ROWS];
int    g_rows_count=0;
ulong  g_deals[V12_DEALS];
ulong  g_deal_queued_ms[V12_DEALS];
long   g_deal_callback_server_s[V12_DEALS];
long   g_deal_quote_ms[V12_DEALS];
double g_deal_bid[V12_DEALS];
double g_deal_ask[V12_DEALS];
int    g_deal_count=0;
int    g_drop_rows=0;
int    g_drop_deals=0;
int    g_file=INVALID_HANDLE;
bool   g_active=false;
string g_session="";

string U64(const ulong value) { return StringFormat("%I64u",value); }
string I64(const long value)  { return StringFormat("%I64d",value); }
string F64(const double value) { return DoubleToString(value,8); }

void QuoteSnapshot(long &quote_msc,double &bid,double &ask)
  {
   MqlTick tick;
   quote_msc=0; bid=0; ask=0;
   if(SymbolInfoTick(InpExactSymbol,tick))
     {
      quote_msc=(long)tick.time_msc;
      bid=tick.bid;
      ask=tick.ask;
     }
  }

string PrefixAt(const string kind,const string symbol,const long magic,
                const ulong callback_mono_ms,const long callback_server_s,
                const long quote_msc,const double bid,const double ask)
  {
   return "V12,"+g_session+",DEMO,"+kind+","+
      U64(callback_mono_ms)+","+I64(callback_server_s)+","+
      I64(quote_msc)+","+F64(bid)+","+F64(ask)+","+
      symbol+","+I64(magic)+",";
  }

string Prefix(const string kind,const string symbol,const long magic)
  {
   long quote_msc;double bid,ask;
   QuoteSnapshot(quote_msc,bid,ask);
   // Server seconds are RECEIPT context, never a deal or request send time.
   return PrefixAt(kind,symbol,magic,GetTickCount64(),
                   (long)TimeTradeServer(),quote_msc,bid,ask);
  }

void QueueLine(const string line)
  {
   if(g_rows_count>=V12_ROWS)
     {g_drop_rows++;return;}
   g_rows[g_rows_count]=line;
   g_rows_count++;
  }

void QueueDeal(const ulong id)
  {
   if(id==0)return;
   for(int k=0;k<g_deal_count;k++)if(g_deals[k]==id)return;
   if(g_deal_count>=V12_DEALS)
     {g_drop_deals++;return;}
   g_deals[g_deal_count]=id;
   g_deal_queued_ms[g_deal_count]=GetTickCount64();
   g_deal_callback_server_s[g_deal_count]=(long)TimeTradeServer();
   QuoteSnapshot(g_deal_quote_ms[g_deal_count],
                 g_deal_bid[g_deal_count],g_deal_ask[g_deal_count]);
   g_deal_count++;
  }

int OnInit()
  {
   if(!InpEnableObserver)
     {
      Print("V12 telemetry inactive (default). No transactions observed.");
      return INIT_SUCCEEDED;
     }
   // A hard fail on live/contest accounts; never use to justify live orders.
   if((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO)
     {Print("V12 telemetry requires a DEMO account.");return INIT_FAILED;}
   if(_Symbol!=InpExactSymbol || StringLen(InpExactSymbol)==0 ||
      StringFind(InpExactSymbol,",")>=0 || InpOutputFilename=="" ||
      StringFind(InpOutputFilename,"/")>=0 ||
      StringFind(InpOutputFilename,"\\")>=0 ||
      StringFind(InpOutputFilename,",")>=0)
     {Print("V12 telemetry symbol/file configuration rejected.");return INIT_FAILED;}
   g_session=I64((long)TimeLocal())+"-"+U64(GetTickCount64());
   g_file=FileOpen(InpOutputFilename,
      FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_COMMON,
      0,CP_UTF8);
   if(g_file==INVALID_HANDLE)
     {Print("V12 telemetry cannot open COMMON file, error=",GetLastError());return INIT_FAILED;}
   if(FileSize(g_file)==0)
     {
      FileWriteString(g_file,
       "version,session,environment,event,callback_mono_ms,callback_server_s,quote_time_msc,bid,ask,symbol,magic,order_id,deal_id,position_id,request_side,retcode,request_price,deal_time_msc,deal_price,volume,commission,fee,swap,profit,deal_entry,deal_reason\r\n");
      FileFlush(g_file);
     }
   FileSeek(g_file,0,SEEK_END);
   g_active=true;
   if(!EventSetTimer(1))
     {Print("V12 telemetry timer unavailable");FileClose(g_file);g_file=INVALID_HANDLE;g_active=false;return INIT_FAILED;}
   Print("V12 DEMO telemetry observer ON, read-only. Source magic=",InpExactMagic);
   return INIT_SUCCEEDED;
  }

// All trade events are buffered by OnTradeTransaction; disk I/O on timer only.
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(!g_active)return;
   if(trans.type==TRADE_TRANSACTION_REQUEST)
     {
      // For REQUEST, only request/result structs contain reliable details.
      if(request.symbol!=InpExactSymbol || request.magic!=InpExactMagic)return;
      string row=Prefix("REQUEST",request.symbol,(long)request.magic)+
           U64(result.order)+","+U64(result.deal)+","+U64(request.position)+","+
           I64((long)request.type)+","+I64((long)result.retcode)+","+
           F64(request.price)+",0,0,"+F64(request.volume)+",0,0,0,0,0,0";
      QueueLine(row);
      return;
     }
   if(trans.type==TRADE_TRANSACTION_DEAL_ADD)
     {
      // Deal details can only safely be fetched from history after
      // transaction notification; do not assume transactions ordered.
      QueueDeal(trans.deal);
     }
  }

void FlushPendingDeals()
  {
   int retained=0;
   for(int i=0;i<g_deal_count;i++)
     {
      ulong id=g_deals[i];
      if(!HistoryDealSelect(id))
        {
         if(GetTickCount64()-g_deal_queued_ms[i]>10000)
           {g_drop_deals++;continue;}
         g_deals[retained]=id;
         g_deal_queued_ms[retained]=g_deal_queued_ms[i];
         g_deal_callback_server_s[retained]=g_deal_callback_server_s[i];
         g_deal_quote_ms[retained]=g_deal_quote_ms[i];
         g_deal_bid[retained]=g_deal_bid[i];
         g_deal_ask[retained]=g_deal_ask[i];
         retained++;
         continue;
        }
      string symbol=HistoryDealGetString(id,DEAL_SYMBOL);
      long magic=HistoryDealGetInteger(id,DEAL_MAGIC);
      if(symbol!=InpExactSymbol || magic!=(long)InpExactMagic)continue;
      // Original event callback snapshot, NOT this OnTimer flush timestamp.
      string row=PrefixAt("DEAL",symbol,magic,g_deal_queued_ms[i],
         g_deal_callback_server_s[i],g_deal_quote_ms[i],
         g_deal_bid[i],g_deal_ask[i])+
         U64((ulong)HistoryDealGetInteger(id,DEAL_ORDER))+","+U64(id)+","+
         U64((ulong)HistoryDealGetInteger(id,DEAL_POSITION_ID))+
         ",0,0,0,"+
         I64(HistoryDealGetInteger(id,DEAL_TIME_MSC))+","+
         F64(HistoryDealGetDouble(id,DEAL_PRICE))+","+
         F64(HistoryDealGetDouble(id,DEAL_VOLUME))+","+
         F64(HistoryDealGetDouble(id,DEAL_COMMISSION))+","+
         F64(HistoryDealGetDouble(id,DEAL_FEE))+","+
         F64(HistoryDealGetDouble(id,DEAL_SWAP))+","+
         F64(HistoryDealGetDouble(id,DEAL_PROFIT))+","+
         I64(HistoryDealGetInteger(id,DEAL_ENTRY))+","+
         I64(HistoryDealGetInteger(id,DEAL_REASON));
      QueueLine(row);
     }
   g_deal_count=retained;
  }

void FlushRows()
  {
   if(g_file==INVALID_HANDLE)return;
   for(int i=0;i<g_rows_count;i++)FileWriteString(g_file,g_rows[i]+"\r\n");
   g_rows_count=0;
   if(g_drop_rows>0 || g_drop_deals>0)
     {
      FileWriteString(g_file,Prefix("LOSS_DIAGNOSTIC",InpExactSymbol,(long)InpExactMagic)+
         "0,0,0,0,"+I64((long)g_drop_rows)+",0,0,0,0,0,0,0,0,0,"+
         I64((long)g_drop_deals)+"\r\n");
      g_drop_rows=0;g_drop_deals=0;
     }
   FileFlush(g_file);
  }

void OnTimer()
  {
   if(!g_active)return;
   FlushPendingDeals();
   FlushRows();
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   if(g_file!=INVALID_HANDLE)
     {
      FlushPendingDeals();
      // Any history event remaining after teardown is explicitly marked LOST.
      g_drop_deals+=g_deal_count;
      g_deal_count=0;
      FlushRows();FileClose(g_file);g_file=INVALID_HANDLE;
     }
   g_active=false;
  }

void OnTick()
  {
   // Intentionally empty: MT5 coalesces NewTick events. For actual quote
   // sequence, use the independently source-verified CopyTicks history.
   // A callback-time SymbolInfoTick snapshot is NOT a fill-time quote.
  }
