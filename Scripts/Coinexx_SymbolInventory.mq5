#property strict
#property script_show_inputs
#property description "Export all broker/server symbols and metadata to FILE_COMMON for R10 Coinexx research."

input bool InpSelectedOnly = false;

string Safe(const string s)
{
   string x=s;
   StringReplace(x,",",";");
   StringReplace(x,"\r"," ");
   StringReplace(x,"\n"," ");
   return x;
}

void OnStart()
{
   const int total=SymbolsTotal(InpSelectedOnly);
   string stamp=TimeToString(TimeLocal(),TIME_DATE|TIME_MINUTES|TIME_SECONDS);
   StringReplace(stamp,".","");
   StringReplace(stamp,":","");
   StringReplace(stamp," ","_");
   const string file="Coinexx_SymbolInventory_"+stamp+".csv";

   const int h=FileOpen(file,FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
   if(h==INVALID_HANDLE)
   {
      PrintFormat("SymbolInventory: FileOpen failed error=%d",GetLastError());
      return;
   }

   FileWrite(h,
      "index","name","description","path","selected","visible",
      "currency_base","currency_profit","currency_margin",
      "digits","point","tick_size","tick_value","contract_size",
      "spread_points","spread_float","trade_mode","calc_mode",
      "volume_min","volume_max","volume_step",
      "session_deals","session_buy_orders","session_sell_orders");

   for(int i=0;i<total;++i)
   {
      const string sym=SymbolName(i,InpSelectedOnly);
      if(sym=="") continue;

      SymbolSelect(sym,true);

      FileWrite(h,
         i,
         Safe(sym),
         Safe(SymbolInfoString(sym,SYMBOL_DESCRIPTION)),
         Safe(SymbolInfoString(sym,SYMBOL_PATH)),
         (int)SymbolInfoInteger(sym,SYMBOL_SELECT),
         (int)SymbolInfoInteger(sym,SYMBOL_VISIBLE),
         Safe(SymbolInfoString(sym,SYMBOL_CURRENCY_BASE)),
         Safe(SymbolInfoString(sym,SYMBOL_CURRENCY_PROFIT)),
         Safe(SymbolInfoString(sym,SYMBOL_CURRENCY_MARGIN)),
         (int)SymbolInfoInteger(sym,SYMBOL_DIGITS),
         DoubleToString(SymbolInfoDouble(sym,SYMBOL_POINT),10),
         DoubleToString(SymbolInfoDouble(sym,SYMBOL_TRADE_TICK_SIZE),10),
         DoubleToString(SymbolInfoDouble(sym,SYMBOL_TRADE_TICK_VALUE),10),
         DoubleToString(SymbolInfoDouble(sym,SYMBOL_TRADE_CONTRACT_SIZE),4),
         (int)SymbolInfoInteger(sym,SYMBOL_SPREAD),
         (int)SymbolInfoInteger(sym,SYMBOL_SPREAD_FLOAT),
         (int)SymbolInfoInteger(sym,SYMBOL_TRADE_MODE),
         (int)SymbolInfoInteger(sym,SYMBOL_TRADE_CALC_MODE),
         DoubleToString(SymbolInfoDouble(sym,SYMBOL_VOLUME_MIN),8),
         DoubleToString(SymbolInfoDouble(sym,SYMBOL_VOLUME_MAX),8),
         DoubleToString(SymbolInfoDouble(sym,SYMBOL_VOLUME_STEP),8),
         (long)SymbolInfoInteger(sym,SYMBOL_SESSION_DEALS),
         (long)SymbolInfoInteger(sym,SYMBOL_SESSION_BUY_ORDERS),
         (long)SymbolInfoInteger(sym,SYMBOL_SESSION_SELL_ORDERS));
   }

   FileFlush(h);
   FileClose(h);

   PrintFormat("SymbolInventory: exported %d symbols -> %s\\Files\\%s",
               total,TerminalInfoString(TERMINAL_COMMONDATA_PATH),file);
}
