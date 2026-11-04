//+------------------------------------------------------------------+
//| R24_ExportMT5_HistoricalEconomicsAndBrokerSessions.mq5           |
//| NON-TRADING observational script for an ONLINE MT5 chart ONLY.   |
//| DO NOT use in Strategy Tester; economic-calendar API is blocked.  |
//| Output fields are in TRADE SERVER TIME, never presumed UTC.       |
//| Historical schedule and actual releases may be retro-edited:     |
//| not point-in-time causally verified from an online current DB.    |
//+------------------------------------------------------------------+
#property strict
#property script_show_inputs
#property version "1.00"
input datetime InpStartServer=D'2026.01.01 00:00:00';
input datetime InpEndServer  =D'2026.02.01 00:00:00';
input string InpNamePrefix  ="R24_MT5_NEWS_SESSION_SOURCE";
input bool InpOnlyMediumHigh =true;

void LogStatus(const int fh,const string key,const string value)
  {
   FileWrite(fh,key,value);
   FileFlush(fh);
  }
string Sanitize(string v)
  {
   StringReplace(v,"\t"," ");
   StringReplace(v,"\r"," ");
   StringReplace(v,"\n"," ");
   return v;
  }

void OnStart()
  {
   const string dateStamp=TimeToString(TimeTradeServer(),TIME_DATE|TIME_SECONDS);
   string base=InpNamePrefix+"_"+IntegerToString((long)TimeLocal());
   const int flags=FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI;
   int status=FileOpen(base+"_STATUS.tsv",flags,'\t');
   if(status==INVALID_HANDLE)
     {
      Print("R24 cannot open status; error=",GetLastError());
      return;
     }
   FileWrite(status,"key","value");
   LogStatus(status,"research_contract","R24_PRESERVATION_ONLY_NOT_EXECUTABLE_TRADING_POLICY");
   LogStatus(status,"symbol",_Symbol);
   LogStatus(status,"account_server",AccountInfoString(ACCOUNT_SERVER));
   LogStatus(status,"current_server_time_at_export",dateStamp);
   LogStatus(status,"current_GMT_at_export",TimeToString(TimeGMT(),TIME_DATE|TIME_SECONDS));
   LogStatus(status,"historical_UTC_mapping","UNKNOWN_REQUIRES_SOURCE_EXACT_BROKER_OFFSET_INTERVALS");
   LogStatus(status,"historical_schedule_asof_revisions","UNKNOWN_PROVIDER_DB_CAN_BE_RETROSPECTIVE");
   LogStatus(status,"external_prop_firm_trading_permission","UNKNOWN_NOT_IN_MT5_CALENDAR");
   LogStatus(status,"from_server",TimeToString(InpStartServer,TIME_DATE|TIME_SECONDS));
   LogStatus(status,"to_server",TimeToString(InpEndServer,TIME_DATE|TIME_SECONDS));
   if((bool)MQLInfoInteger(MQL_TESTER))
     {
      LogStatus(status,"calendar_export_status","FUNCTION_NOT_ALLOWED_STRATEGY_TESTER");
      FileClose(status);
      return;
     }
   if(InpEndServer<=InpStartServer)
     {
      LogStatus(status,"calendar_export_status","FAIL_INVALID_SERVER_INTERVAL");
      FileClose(status);
      return;
     }
   int news=FileOpen(base+"_EVENTS_SERVER_TIME.tsv",flags,'\t');
   int sess=FileOpen(base+"_CURRENT_SESSION_WEEK_TEMPLATE.tsv",flags,'\t');
   if(news==INVALID_HANDLE || sess==INVALID_HANDLE)
     {
      LogStatus(status,"calendar_export_status","FAIL_FILE_OPEN");
      if(news!=INVALID_HANDLE)FileClose(news);
      if(sess!=INVALID_HANDLE)FileClose(sess);
      FileClose(status);
      return;
     }
   FileWrite(news,"currency_filter","calendar_value_id","event_id","server_scheduled_time",
     "event_importance","event_time_mode","event_currency_country_unknown","event_name",
     "event_revision","values_actual_forecast_are_NOT_PRE_RELEASE_FEATURES");
   FileWrite(sess,"snapshot_server_time","symbol","snapshot_type","weekday_enum","session_index",
     "session_start_seconds","session_end_seconds","HISTORICAL_VERIFICATION");
   // The terminal supplies CURRENT known weekly trading/quoting sessions only;
   // exchange holidays and prop-firm constraints must be sourced separately.
   for(int day=0; day<7; day++)
     {
      ENUM_DAY_OF_WEEK weekday=(ENUM_DAY_OF_WEEK)day;
      for(uint idx=0;idx<16;idx++)
        {
         datetime s0=0,s1=0;
         if(!SymbolInfoSessionTrade(_Symbol,weekday,idx,s0,s1))break;
         FileWrite(sess,dateStamp,_Symbol,"CURRENT_TRADE",IntegerToString(day),IntegerToString((int)idx),
           IntegerToString((long)s0),IntegerToString((long)s1),"CURRENT_ONLY_NOT_VERIFIED_FOR_2026_HISTORY");
        }
      for(uint idx=0;idx<16;idx++)
        {
         datetime s0=0,s1=0;
         if(!SymbolInfoSessionQuote(_Symbol,weekday,idx,s0,s1))break;
         FileWrite(sess,dateStamp,_Symbol,"CURRENT_QUOTE",IntegerToString(day),IntegerToString((int)idx),
           IntegerToString((long)s0),IntegerToString((long)s1),"CURRENT_ONLY_NOT_VERIFIED_FOR_2026_HISTORY");
        }
     }
   FileFlush(sess);
   // USD is central to XAUUSD; other currencies only research-context.
   string currencies[6]={"USD","EUR","GBP","JPY","CNY","AUD"};
   int total=0;bool provider_failed=false;
   for(int k=0;k<6;k++)
     {
      MqlCalendarValue releases[];
      ResetLastError();
      int n=CalendarValueHistory(releases,InpStartServer,InpEndServer,NULL,currencies[k]);
      int err=GetLastError();
      if(n<0 || err==5400 || err==5401 || err==4014)
        {
         LogStatus(status,"failed_currency_"+currencies[k],IntegerToString(err));
         provider_failed=true;
         continue;
        }
      LogStatus(status,"raw_event_rows_"+currencies[k],IntegerToString(n));
      for(int j=0;j<n;j++)
        {
         MqlCalendarEvent ev;
         if(!CalendarEventById(releases[j].event_id,ev))
           {
            provider_failed=true;
            LogStatus(status,"event_metadata_lookup_error",IntegerToString(GetLastError()));
            continue;
           }
         if(InpOnlyMediumHigh && ev.importance!=CALENDAR_IMPORTANCE_MODERATE && ev.importance!=CALENDAR_IMPORTANCE_HIGH)continue;
         FileWrite(news,currencies[k],StringFormat("%I64u",releases[j].id),
           StringFormat("%I64u",releases[j].event_id),TimeToString(releases[j].time,TIME_DATE|TIME_SECONDS),
           EnumToString(ev.importance),EnumToString(ev.time_mode),
           "COUNTRY_LOOKUP_NOT_PERFORMED",Sanitize(ev.name),
           IntegerToString(releases[j].revision),"DO_NOT_USE_ACTUAL_OR_REVISED_HISTORICAL_VALUE_AT_ENTRY");
         total++;
        }
     }
   FileFlush(news);
   LogStatus(status,"retained_medium_high_event_rows",IntegerToString(total));
   LogStatus(status,"calendar_export_status",provider_failed?"INCOMPLETE_PROVIDER_ERROR_FAIL_CLOSED":"COMPLETE_RETROSPECTIVE_METADATA_UNVERIFIED_POINT_IN_TIME");
   FileClose(news);FileClose(sess);FileClose(status);
   Print("R24 export complete. Files in MT5 terminal Common Files: ",base);
  }
