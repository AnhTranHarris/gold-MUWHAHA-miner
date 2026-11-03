// R11S5 research-only MT5 native calendar & broker-session exporter.
// Copyright owner: Gold MUWHAHA Miner. THIS DOES NOT TRADE.
// Run as a SCRIPT on an ONLINE-connected MetaTrader 5 terminal, not tester.
// All CalendarValueHistory() timestamps are BROKER SERVER time.
// Never silently apply today's TimeTradeServer-TimeGMT offset to a prior month.
// Historical UTC conversion is a separate verified Python ingestion step.
#property strict
#property script_show_inputs

input datetime InpStartServer = D'2026.01.01 00:00:00';
input datetime InpEndServer = D'2026.02.01 00:00:00';
input string   InpCurrencies = "USD,EUR,GBP,JPY,CNY,AUD";
input string   InpOutputStem = "R11S5_MT5_CALENDAR_2026_01";
input int      InpChunkHours = 24;    // hour/day chunks avoid 5401/5400 large responses
input bool     InpExportTradeSessions = true;

string Sanitize(string text)
{
   StringReplace(text,"\t"," ");
   StringReplace(text,"\r"," ");
   StringReplace(text,"\n"," ");
   return text;
}

bool ExportSessions(const string filename)
{
   int f=FileOpen(filename,FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,'\t',CP_UTF8);
   if(f==INVALID_HANDLE) {Print("R11S5 session output open error=",GetLastError());return false;}
   FileWrite(f,"capture_server","capture_utc","broker_symbol","weekday_mql","session_kind","session_index","server_begin_hhmm","server_end_hhmm","historical_validity");
   for(int day=0;day<7;day++)
   {
      for(uint n=0;n<32;n++)
      {
         datetime a,b;
         if(!SymbolInfoSessionTrade(_Symbol,(ENUM_DAY_OF_WEEK)day,n,a,b))break;
         FileWrite(f,TimeToString(TimeTradeServer(),TIME_DATE|TIME_SECONDS),
                   TimeToString(TimeGMT(),TIME_DATE|TIME_SECONDS),_Symbol,day,"TRADE",n,
                   TimeToString(a,TIME_MINUTES),TimeToString(b,TIME_MINUTES),
                   "CURRENT_SNAPSHOT_NOT_HISTORICAL_PROOF");
      }
      for(uint q=0;q<32;q++)
      {
         datetime a,b;
         if(!SymbolInfoSessionQuote(_Symbol,(ENUM_DAY_OF_WEEK)day,q,a,b))break;
         FileWrite(f,TimeToString(TimeTradeServer(),TIME_DATE|TIME_SECONDS),
                   TimeToString(TimeGMT(),TIME_DATE|TIME_SECONDS),_Symbol,day,"QUOTE",q,
                   TimeToString(a,TIME_MINUTES),TimeToString(b,TIME_MINUTES),
                   "CURRENT_SNAPSHOT_NOT_HISTORICAL_PROOF");
      }
   }
   FileFlush(f);FileClose(f);return true;
}

void OnStart()
{
   if(MQLInfoInteger(MQL_TESTER)!=0)
   {
      Print("R11S5 FAIL CLOSED: economic calendar functions are unavailable in Strategy Tester (4014). Export from online chart.");
      return;
   }
   if(InpStartServer>=InpEndServer || InpChunkHours<1 || InpChunkHours>48)
   {
      Print("R11S5 FAIL CLOSED: invalid server date interval or chunk hours.");return;
   }
   const string suffix=".tsv";
   int f=FileOpen(InpOutputStem+suffix,FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,'\t',CP_UTF8);
   int status=FileOpen(InpOutputStem+"_STATUS.tsv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,'\t',CP_UTF8);
   if(f==INVALID_HANDLE || status==INVALID_HANDLE)
   {
      Print("R11S5 FAIL CLOSED: file open error=",GetLastError());
      if(f!=INVALID_HANDLE)FileClose(f);
      if(status!=INVALID_HANDLE)FileClose(status);
      return;
   }
   FileWrite(f,"value_id","event_id","event_time_server","importance","currency","country","event_name","event_code","time_mode","actual_value_raw1e6","forecast_value_raw1e6","prev_value_raw1e6","impact_type","capture_server","capture_utc","data_provenance");
   FileWrite(status,"kind","state","currency","chunk_start_server","chunk_end_server","error_code","event_rows","capture_server","capture_utc");
   string currencies[];
   int ncur=StringSplit(InpCurrencies,',',currencies);
   int errors=0;int rows=0;int requests=0;
   if(ncur<=0)errors++;
   for(int ci=0;ci<ncur;ci++)
   {
      string currency=currencies[ci];
      StringTrimLeft(currency);StringTrimRight(currency);
      if(StringLen(currency)!=3)
      {
         Print("R11S5 unsupported currency code: ",currency);errors++;continue;
      }
      for(datetime st=InpStartServer;st<InpEndServer;st+=(InpChunkHours*3600))
      {
         datetime en=st+InpChunkHours*3600;
         if(en>InpEndServer)en=InpEndServer;
         MqlCalendarValue values[];
         ResetLastError();
         int count=CalendarValueHistory(values,st,en,NULL,currency);
         requests++;
         if(count<0)
         {
            int ec=GetLastError();errors++;
            FileWrite(status,"CALENDAR_QUERY","ERROR",currency,TimeToString(st,TIME_DATE|TIME_SECONDS),
                      TimeToString(en,TIME_DATE|TIME_SECONDS),ec,0,
                      TimeToString(TimeTradeServer(),TIME_DATE|TIME_SECONDS),TimeToString(TimeGMT(),TIME_DATE|TIME_SECONDS));
            Print("R11S5 QUERY FAIL CLOSED ",currency," ",TimeToString(st)," code ",ec);
            continue;
         }
         FileWrite(status,"CALENDAR_QUERY","OK",currency,TimeToString(st,TIME_DATE|TIME_SECONDS),
                   TimeToString(en,TIME_DATE|TIME_SECONDS),0,count,
                   TimeToString(TimeTradeServer(),TIME_DATE|TIME_SECONDS),TimeToString(TimeGMT(),TIME_DATE|TIME_SECONDS));
         for(int i=0;i<count;i++)
         {
            MqlCalendarEvent ev;
            ResetLastError();
            if(!CalendarEventById(values[i].event_id,ev))
            {
               errors++;Print("R11S5 event meta error ",values[i].event_id," error=",GetLastError());continue;
            }
            if(ev.importance<CALENDAR_IMPORTANCE_MODERATE)continue;
            MqlCalendarCountry country;
            if(!CalendarCountryById(ev.country_id,country))
            {
               errors++;Print("R11S5 country meta failure id=",ev.country_id);continue;
            }
            FileWrite(f,values[i].id,values[i].event_id,TimeToString(values[i].time,TIME_DATE|TIME_SECONDS),
                      EnumToString(ev.importance),currency,Sanitize(country.code),Sanitize(ev.name),
                      Sanitize(ev.event_code),EnumToString(ev.time_mode),
                      values[i].actual_value,values[i].forecast_value,values[i].prev_value,
                      EnumToString(values[i].impact_type),
                      TimeToString(TimeTradeServer(),TIME_DATE|TIME_SECONDS),
                      TimeToString(TimeGMT(),TIME_DATE|TIME_SECONDS),
                      "RETROSPECTIVE_CALENDAR_DATABASE_NOT_ASOF_SNAPSHOT");
            rows++;
         }
         FileFlush(f);FileFlush(status);
      }
   }
   FileWrite(status,"EXPORT_COMPLETION",(errors==0?"COMPLETE":"INCOMPLETE_ERRORS"),"ALL",
             TimeToString(InpStartServer,TIME_DATE|TIME_SECONDS),
             TimeToString(InpEndServer,TIME_DATE|TIME_SECONDS),errors,rows,
             TimeToString(TimeTradeServer(),TIME_DATE|TIME_SECONDS),
             TimeToString(TimeGMT(),TIME_DATE|TIME_SECONDS));
   FileFlush(f);FileFlush(status);FileClose(f);FileClose(status);
   if(InpExportTradeSessions && !ExportSessions(InpOutputStem+"_SESSIONS.tsv"))
       Print("R11S5 session metadata could not be exported");
   Print("R11S5 calendar rows=",rows," requests=",requests," errors=",errors,
         "; output in Terminal/Common/Files; UTC historical offset NOT inferred.");
}
