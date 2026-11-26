// HG10 clean native terminal adapter. No HG6Broker, HG6Readiness, or HG9 wrapper.
#define HG10_BUILD "HG10-DEMO-699da4f6-v1"
input group "HybridGate demo trading"
input ulong InpMagic=6202610;
input bool InpLotLadder=false;
input int InpLadderCapUnits=10;
input bool InpWeeklyClock=false;
input group "Quote processing"
input int InpWarmupMinutes=120; // demo only; history never submits orders
input int InpTesterUtcOffsetMinutes=0; // tester does not expose actual historical UTC offset
input int InpMaxQuoteAgeMs=2000;
input int InpDeviationPoints=10;
input int InpTimerMs=250;
// Only one outstanding order or owned position. Persist before each send.
enum D10Phase { D10_FLAT=0,D10_ENTRY=1,D10_OPEN=2,D10_EXIT=3 };
HG6Core d_core; HG6Cursor d_cursor; HG6Store d_store;
HG5Window d_windows[]; MqlTick d_raw[HG6_TICK_BATCH]; HG5Quote d_group[];
HG5StageEvent d_stage[]; HG5Proposal d_proposals[]; HG5PathEvent d_paths[]; HG5AccountEvent d_accounts[];
int d_phase=0,d_side=0,d_units=0,d_offset=0,d_lock=INVALID_HANDLE;
long d_seq=0,d_position=0,d_order=0,d_deal=0,d_created=0,d_last_flat=0,d_closed=0,d_proposal=-1;
double d_net=0;
bool d_test=false,d_initialized=false,d_clock_set=false,d_started=false,d_ready=false,d_fault=false,d_recovered=false,d_protect=false;
long d_seen=0,d_stale=0,d_busy=0,d_clock_block=0,d_account=0,d_reject=0,d_sends=0,d_history_wait=0,d_invalid=0,d_callbacks=0;
long d_last_report=0,d_start_ms=0,d_first_ms=0;ulong d_last_attempt=0;
string d_scope="",d_status="INITIALIZING";
void D10Status(string msg){if(msg!=d_status){d_status=msg;Print("HG10 STATUS: ",msg);}}
void D10Fault(string why){if(!d_fault){Print("HG10 FATAL: ",why," phase=",d_phase," position=",d_position," error=",GetLastError());}d_fault=true;D10Status("QUARANTINED - see Journal");}
bool D10Permission(){return MQLInfoInteger(MQL_TESTER)!=0||AccountInfoInteger(ACCOUNT_TRADE_MODE)==ACCOUNT_TRADE_MODE_DEMO;}
bool D10CanSend(){return D10Permission()&&(d_test||(TerminalInfoInteger(TERMINAL_CONNECTED)!=0&&TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)!=0))&&MQLInfoInteger(MQL_TRADE_ALLOWED)!=0&&AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)!=0&&AccountInfoInteger(ACCOUNT_TRADE_EXPERT)!=0;}
string D10Comment(){return "HG10-"+IntegerToString(d_seq);}
bool D10Save(){HG5StateCodec c;uchar bytes[];int version=1;if(!c.BeginWrite()||!c.I32(version)||!c.I32(d_phase)||!c.I32(d_side)||!c.I32(d_units)||!c.I64(d_seq)||!c.I64(d_position)||!c.I64(d_order)||!c.I64(d_deal)||!c.I64(d_created)||!c.I64(d_last_flat)||!c.I64(d_closed)||!c.I64(d_proposal)||!c.F64(d_net)||!c.Finish(bytes)||!d_store.Save(bytes)){D10Fault("durable order state write failed");return false;}return true;}
bool D10Restore(const uchar &bytes[]){HG5StateCodec c;int version=0;if(!c.BeginRead(bytes)||!c.I32(version)||version!=1||!c.I32(d_phase)||!c.I32(d_side)||!c.I32(d_units)||!c.I64(d_seq)||!c.I64(d_position)||!c.I64(d_order)||!c.I64(d_deal)||!c.I64(d_created)||!c.I64(d_last_flat)||!c.I64(d_closed)||!c.I64(d_proposal)||!c.F64(d_net)||!c.Done())return false;
 if(d_phase<0||d_phase>3||d_seq<0||d_position<0||d_order<0||d_deal<0||d_created<0||d_last_flat<0||d_closed<0||!MathIsValidNumber(d_net))return false;
 if(d_phase==D10_FLAT)return d_position==0&&d_units==0&&d_side==0;
 return (d_side==1||d_side==-1)&&d_units>0&&d_units<=100&&d_created>0&&(d_phase==D10_ENTRY?d_position==0:d_position>0);
}
void D10Clear(){d_phase=D10_FLAT;d_side=d_units=0;d_position=d_order=d_deal=d_created=0;d_proposal=-1;d_protect=false;d_recovered=false;}
// Live clocks are validated every pump. In tester use explicit historical offset.
bool D10Clock(int &offset,long &now){datetime server=d_test?TimeCurrent():TimeTradeServer();if(server<=0)return false;now=(long)server*1000;if(d_test){offset=InpTesterUtcOffsetMinutes;return true;}datetime utc=TimeGMT();if(utc<=0)return false;long diff=(long)server-(long)utc;offset=(int)(MathRound((double)diff/900.0)*15.0);return offset>=-840&&offset<=840&&MathAbs((double)(diff-(long)offset*60))<=5.0;}
long D10UTC(long raw){return raw-(long)d_offset*60000;}
bool D10DefiniteReject(uint code){return code==TRADE_RETCODE_REQUOTE||code==TRADE_RETCODE_PRICE_CHANGED||code==TRADE_RETCODE_PRICE_OFF||code==TRADE_RETCODE_REJECT||code==TRADE_RETCODE_INVALID||code==TRADE_RETCODE_INVALID_VOLUME||code==TRADE_RETCODE_INVALID_PRICE||code==TRADE_RETCODE_TRADE_DISABLED||code==TRADE_RETCODE_MARKET_CLOSED||code==TRADE_RETCODE_NO_MONEY||code==TRADE_RETCODE_INVALID_FILL;}
// Broker entry identity is established from the unique entry order/deal, not a mocked callback or assumed fill price.
bool D10EntryEvidence(const HG6Exposure &x){
 if(x.ticket==0||x.identifier==0||x.side!=d_side||x.units!=d_units||x.time_ms<d_created||!HistorySelectByPosition(x.identifier))return false;
 int n=HistoryDealsTotal(),units=0;long entry_order=0;bool matched=false;
 for(int i=0;i<n;i++){ulong t=HistoryDealGetTicket(i);if(t==0)return false;if(HistoryDealGetInteger(t,DEAL_ENTRY)!=DEAL_ENTRY_IN)continue;
  if(HistoryDealGetString(t,DEAL_SYMBOL)!=_Symbol||(ulong)HistoryDealGetInteger(t,DEAL_MAGIC)!=InpMagic||HistoryDealGetInteger(t,DEAL_POSITION_ID)!=(long)x.identifier||HistoryDealGetInteger(t,DEAL_TYPE)!=(d_side>0?DEAL_TYPE_BUY:DEAL_TYPE_SELL))return false;
  long order=HistoryDealGetInteger(t,DEAL_ORDER);int u=0;if(order<=0||!HG6VolumeUnits(HistoryDealGetDouble(t,DEAL_VOLUME),u)||(entry_order!=0&&entry_order!=order))return false;entry_order=order;units+=u;if(d_deal==(long)t||d_order==order)matched=true;
 }
 if(units!=d_units||entry_order<=0)return false;
 if(!matched&&d_order==0&&d_deal==0){if(!HistoryOrderSelect((ulong)entry_order)||HistoryOrderGetString((ulong)entry_order,ORDER_COMMENT)!=D10Comment()||(ulong)HistoryOrderGetInteger((ulong)entry_order,ORDER_MAGIC)!=InpMagic)return false;matched=true;}
 return matched;
}
// A closed trade is recorded from complete position history and only when the broker is flat.
bool D10ClosedEvidence(double &net){net=0;if(d_position<=0||!HistorySelectByPosition((ulong)d_position))return false;int n=HistoryDealsTotal(),ins=0,outs=0;if(n<2||n>4096)return false;
 long seen[];for(int i=0;i<n;i++){ulong t=HistoryDealGetTicket(i);if(t==0)return false;bool dup=false;for(int k=0;k<ArraySize(seen);k++)if(seen[k]==(long)t)dup=true;if(dup)continue;int k=ArraySize(seen);if(ArrayResize(seen,k+1)!=k+1)return false;seen[k]=(long)t;
  if(HistoryDealGetString(t,DEAL_SYMBOL)!=_Symbol||HistoryDealGetInteger(t,DEAL_POSITION_ID)!=d_position)return false;
  long e=HistoryDealGetInteger(t,DEAL_ENTRY),type=HistoryDealGetInteger(t,DEAL_TYPE);int u=0;if(!HG6VolumeUnits(HistoryDealGetDouble(t,DEAL_VOLUME),u))return false;
  if(e==DEAL_ENTRY_IN){if((ulong)HistoryDealGetInteger(t,DEAL_MAGIC)!=InpMagic||type!=(d_side>0?DEAL_TYPE_BUY:DEAL_TYPE_SELL))return false;ins+=u;}
  else if(e==DEAL_ENTRY_OUT){if(type!=(d_side>0?DEAL_TYPE_SELL:DEAL_TYPE_BUY))return false;outs+=u;}else return false;
  double p=HistoryDealGetDouble(t,DEAL_PROFIT)+HistoryDealGetDouble(t,DEAL_COMMISSION)+HistoryDealGetDouble(t,DEAL_SWAP)+HistoryDealGetDouble(t,DEAL_FEE);if(!MathIsValidNumber(p))return false;net+=p;
 }
 return ins>0&&ins==outs&&ins>=d_units&&MathIsValidNumber(net);
}
// Terminal rejected/cancelled/expired orders with no fills can release their intent.
bool D10NoFill(){
 if(d_order<=0||d_deal!=0||!HistorySelect((datetime)(d_created/1000-60),TimeCurrent()+60))return false;
 int n=HistoryDealsTotal();for(int i=0;i<n;i++){ulong t=HistoryDealGetTicket(i);if(t==0||HistoryDealGetInteger(t,DEAL_ORDER)==d_order)return false;}
 if(!HistoryOrderSelect((ulong)d_order)||HistoryOrderGetString((ulong)d_order,ORDER_SYMBOL)!=_Symbol||(ulong)HistoryOrderGetInteger((ulong)d_order,ORDER_MAGIC)!=InpMagic)return false;
 long st=HistoryOrderGetInteger((ulong)d_order,ORDER_STATE);return st==ORDER_STATE_REJECTED||st==ORDER_STATE_CANCELED||st==ORDER_STATE_EXPIRED;
}
bool D10Reconcile(HG6Exposure &x,long raw_now){
 if(!HG6ExposureRead(_Symbol,InpMagic,x)||x.ambiguous||x.foreign){D10Status("WAIT: foreign or ambiguous exposure");return false;}
 if(d_phase==D10_FLAT){if(x.ticket||x.pending){D10Status("WAIT: exposure without matching durable intent; manual reconciliation required");return false;}return true;}
 if(x.pending){D10Status("WAIT: broker order pending");return false;}
 if(d_phase==D10_ENTRY){
  if(!x.ticket){
   if(D10NoFill()){D10Clear();return D10Save();}
   if(d_deal>0&&HistoryDealSelect((ulong)d_deal)&&HistoryDealGetString((ulong)d_deal,DEAL_SYMBOL)==_Symbol&&(ulong)HistoryDealGetInteger((ulong)d_deal,DEAL_MAGIC)==InpMagic&&HistoryDealGetInteger((ulong)d_deal,DEAL_ENTRY)==DEAL_ENTRY_IN){
    long pos=HistoryDealGetInteger((ulong)d_deal,DEAL_POSITION_ID);if(pos>0){d_position=pos;double net=0;if(D10ClosedEvidence(net)){d_net+=net;d_closed++;d_last_flat=raw_now;D10Clear();d_recovered=false;return D10Save();}d_position=0;}
   }
   D10Status("WAIT: unresolved entry receipt; never resend an unknown order");return false;
  }
  if(!D10EntryEvidence(x)){D10Status("WAIT: entry deal evidence not yet available");return false;}
  d_position=(long)x.identifier;d_phase=D10_OPEN;d_last_attempt=0;if(!D10Save())return false;
  PrintFormat("HG10 ENTRY CONFIRMED position=%I64d side=%d volume=%.2f fill=%.2f ms=%I64d",d_position,d_side,x.volume,x.price,x.time_ms);
 }
 if(!x.ticket){double net=0;if(!D10ClosedEvidence(net)){D10Status("WAIT: closed position history not yet complete");return false;}
  long pos=d_position;if(d_core.ActualState()!=0&&!d_core.ConfirmFlat(pos)){D10Fault("holding identity at flat");return false;}
  d_net+=net;d_closed++;d_last_flat=raw_now;D10Clear();if(!D10Save())return false;d_recovered=false;
  PrintFormat("HG10 CLOSED position=%I64d net=%.8f total=%I64d",pos,net,d_closed);return true;
 }
 if((long)x.identifier!=d_position||x.side!=d_side||x.units>d_units){D10Status("WAIT: position identity/volume conflict");return false;}
 if(d_phase==D10_EXIT){if(D10NoFill()){d_phase=D10_OPEN;if(!D10Save())return false;}else {D10Status("WAIT: unresolved exit receipt; never resend an unknown order");return false;}}
 if(x.units<d_units){d_units=x.units;d_protect=true;if(d_core.ActualState()!=0&&!d_core.ReduceActual(d_position,d_units)){D10Fault("holding volume reconciliation");return false;}if(!D10Save())return false;}
 if(d_started&&d_core.ActualState()==0&&!d_recovered&&!d_protect){
  bool bound=x.anchor_ok&&d_core.BindActual(d_position,D10UTC(x.time_ms),d_side,x.price_cents,d_units);
  if(!bound){d_protect=true;Print("HG10 PROTECT: actual fill anchor unavailable; close owned demo exposure");}
 }
 return true;
}
// Native synchronous trade request, durable pre-send state, and fresh quote/position revalidation.
bool D10Submit(int kind,const HG5Proposal &proposal,const MqlTick &tick,const HG6Exposure &x,int units){
 if(!D10CanSend()||!d_store.Healthy()||units<=0||units>100||!HG6VolumeAllowed(_Symbol,(double)units/100.0)||!HG6FokAllowed(_Symbol))return false;
 if(kind==1&&(d_phase!=D10_FLAT||x.ticket||x.pending||x.foreign||x.ambiguous||d_fault))return false;
 if(kind==2&&(d_phase!=D10_OPEN||!x.ticket||(long)x.identifier!=d_position||x.pending||x.foreign||x.ambiguous))return false;
 int side=kind==1?proposal.side:-x.side;if(side!=1&&side!=-1)return false;
 long mode=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_MODE);if(mode==SYMBOL_TRADE_MODE_DISABLED||(kind==1&&(mode==SYMBOL_TRADE_MODE_CLOSEONLY||(mode==SYMBOL_TRADE_MODE_LONGONLY&&side<0)||(mode==SYMBOL_TRADE_MODE_SHORTONLY&&side>0))))return false;
 MqlTradeRequest r={};MqlTradeResult v={};MqlTradeCheckResult c={};r.action=TRADE_ACTION_DEAL;r.symbol=_Symbol;r.magic=InpMagic;r.type=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;r.volume=(double)units/100.0;r.price=side>0?tick.ask:tick.bid;r.deviation=(ulong)InpDeviationPoints;r.type_filling=ORDER_FILLING_FOK;r.position=kind==2?x.ticket:0;
 if(kind==1){HG6AccountFacts a;double margin=0;if(!HG6ReadAccount(a)||!HG6AdmissionAccount(a)||!OrderCalcMargin(r.type,_Symbol,r.volume,r.price,margin)||!MathIsValidNumber(margin)||margin<0||margin>a.free_margin){d_account++;return false;}}
 if(!OrderCheck(r,c)||(c.retcode!=0&&c.retcode!=TRADE_RETCODE_DONE)){d_reject++;PrintFormat("HG10 ORDER CHECK rejected kind=%d retcode=%u error=%d",kind,c.retcode,GetLastError());return false;}
 if(d_seq>=0x7ffffffffffffffe){D10Fault("order sequence exhausted");return false;}d_seq++;r.comment=D10Comment();d_phase=kind==1?D10_ENTRY:D10_EXIT;d_created=tick.time_msc;d_order=d_deal=0;
 if(kind==1){d_side=side;d_units=units;d_proposal=proposal.id;}
 if(!D10Save())return false;
 MqlTick fresh={};HG6Exposure fx;bool unchanged=D10CanSend()&&SymbolInfoTick(_Symbol,fresh)&&HG6TickEqual(tick,fresh)&&HG6ExposureRead(_Symbol,InpMagic,fx)&&!fx.pending&&!fx.ambiguous&&!fx.foreign&&fx.ticket==x.ticket&&fx.identifier==x.identifier&&fx.units==x.units;
 if(!unchanged){if(kind==1)D10Clear();else d_phase=D10_OPEN;d_stale++;D10Save();return false;}
 ResetLastError();bool sent=OrderSend(r,v);int err=GetLastError();d_sends++;d_order=(long)v.order;d_deal=(long)v.deal;PrintFormat("HG10 SEND kind=%d seq=%I64d sent=%d retcode=%u order=%I64u deal=%I64u error=%d",kind,d_seq,(int)sent,v.retcode,v.order,v.deal,err);
 if(D10DefiniteReject(v.retcode)&&v.order==0&&v.deal==0){d_reject++;if(kind==1)D10Clear();else d_phase=D10_OPEN;D10Save();return false;}
 return D10Save(); // successful acknowledgement is NOT a confirmed fill
}
void D10Manage(HG6Exposure &x,const MqlTick &tick,long now,bool clock_ok){
 if(d_phase!=D10_OPEN||x.ticket==0||x.pending||x.foreign||x.ambiguous)return;
 HG6AccountFacts a;bool risk=HG6ReadAccount(a)&&HG6AccountUrgent(a);bool age=now-x.time_ms>=30000;
 int action=HG5Clock(D10UTC(now),true,false,HG6TradeSession(_Symbol,(datetime)(now/1000)),clock_ok,true,false,d_windows,ArraySize(d_windows));
 bool urgent=d_fault||d_protect||d_recovered||d_core.ActualState()==3||age||risk||action==HG5_FLATTEN;
 if(!urgent&&d_core.ActualReason()<=0)return;
 if(!HG6TradeSession(_Symbol,(datetime)(now/1000))||now-tick.time_msc>InpMaxQuoteAgeMs||!D10CanSend()){D10Status("WAIT: exit due, market/quote/permission unavailable");return;}
 ulong us=GetMicrosecondCount();if(!d_test&&d_last_attempt>0&&us-d_last_attempt<250000)return;d_last_attempt=us;
 HG5Proposal p;p.ZeroFields();PrintFormat("HG10 EXIT REQUEST position=%I64d model_reason=%d protective=%d age_ms=%I64d",d_position,d_core.ActualReason(),(int)urgent,now-x.time_ms);D10Submit(2,p,tick,x,x.units);
}
bool D10Start(const MqlTick &tick,int offset){d_offset=offset;d_clock_set=true;if(!HG6Windows(InpWeeklyClock,0,d_windows)||!d_core.Start(d_windows,262144))return false;d_first_ms=tick.time_msc;d_start_ms=tick.time_msc-(d_test?0:(long)InpWarmupMinutes*60000);if(!d_cursor.Init(d_start_ms))return false;d_started=true;PrintFormat("HG10 SOURCE START server_offset=%d start=%I64d first=%I64d warmup_min=%d",offset,d_start_ms,d_first_ms,d_test?0:InpWarmupMinutes);return true;}
void D10Report(){PrintFormat("HG10 SUMMARY callbacks=%I64d quotes=%I64d proposals=%I64d stale=%I64d busy=%I64d clock=%I64d account=%I64d rejects=%I64d sends=%I64d closed=%I64d net=%.8f history_wait=%I64d phase=%d fatal=%d",d_callbacks,d_cursor.Ordinal(),d_seen,d_stale,d_busy,d_clock_block,d_account,d_reject,d_sends,d_closed,d_net,d_history_wait,d_phase,(int)d_fault);}
void D10Pump(){
 if(!d_initialized)return;d_callbacks++;if(!D10Permission()){D10Status("BLOCK: real money account");return;}
 if(!d_test&&TerminalInfoInteger(TERMINAL_CONNECTED)==0){D10Status("WAIT: terminal disconnected");return;}
 MqlTick latest={};HG5Quote q;if(!SymbolInfoTick(_Symbol,latest)||!HG6Normalize(latest,q)){D10Status("WAIT: valid bid/ask");return;}
 long now=latest.time_msc;int offset=0;bool clock_ok=D10Clock(offset,now);if(now<latest.time_msc)now=latest.time_msc;
 if(!d_started&&clock_ok&&!d_fault&&!D10Start(latest,offset)){D10Fault("core/clock startup");}
 if(d_clock_set&&offset!=d_offset)clock_ok=false;
 HG6Exposure x;bool reconciled=D10Reconcile(x,now);if(reconciled)D10Manage(x,latest,now,clock_ok);
 if(d_fault||!d_started||!clock_ok){if(!clock_ok)D10Status("WAIT: clock mapping changed or unavailable; restart flat after mapping verified");return;}
 // A close request changes the durable phase before any later entry decision.
 if(d_cursor.Last()>latest.time_msc){D10Fault("quote stream time regression");return;}
 ResetLastError();int n=CopyTicks(_Symbol,d_raw,COPY_TICKS_ALL,(ulong)d_cursor.From(),HG6_TICK_BATCH);int err=GetLastError();
 if(n<0||n>ArraySize(d_raw)||err!=0){d_history_wait++;D10Status("WAIT: tick history synchronization");return;}
 while(n>0&&d_raw[n-1].time_msc>latest.time_msc)n--;
 int lo=0,status=d_cursor.ClassifyBatch(d_raw,n,lo);if(status<0){D10Fault("historical quote overlap/order/cents grid mismatch");return;}if(status==0){d_history_wait++;return;}
 bool previous_ready=d_ready;d_ready=false;
 while(lo<n&&!IsStopped()){
  int end=d_cursor.NextEnd(d_raw,n,lo);if(end<0){D10Fault("same-millisecond group overflow/order");return;}if(end==0)break;
  if(!d_cursor.Group(d_raw,lo,end,d_group)){D10Fault("quote group integrity");return;}
  for(int j=0;j<ArraySize(d_group);j++)d_group[j].ms=D10UTC(d_group[j].ms);
  if(!d_core.StepGroup(d_group,d_stage,d_proposals,d_paths,d_accounts)||!d_cursor.Commit(d_raw,lo,end)){D10Fault("frozen strategy processing");return;}lo=end;
  if(d_core.ActualState()==3)d_protect=true;
  if(reconciled&&d_phase==D10_OPEN&&d_core.ActualReason()>0)D10Manage(x,latest,now,clock_ok);
  int count=ArraySize(d_proposals);d_seen+=count;if(count<=0)continue;
  bool fresh=previous_ready&&n<HG6_TICK_BATCH&&lo<n&&d_raw[lo].time_msc==latest.time_msc&&d_raw[n-1].time_msc==latest.time_msc&&D10UTC(latest.time_msc)>d_proposals[0].t&&D10UTC(latest.time_msc)-d_proposals[0].t<=InpMaxQuoteAgeMs&&now-latest.time_msc<=InpMaxQuoteAgeMs;
  if(!fresh){d_stale+=count;continue;}
  if(!reconciled||d_phase!=D10_FLAT||x.ticket||x.pending||x.foreign||x.ambiguous||d_core.ActualState()!=0||d_proposals[0].t<=D10UTC(d_last_flat)){d_busy+=count;continue;}
  bool session=HG6TradeSession(_Symbol,(datetime)(now/1000));if(HG5Clock(d_proposals[0].t,false,false,session,clock_ok,true,false,d_windows,ArraySize(d_windows))!=HG5_TRADE||HG5Clock(D10UTC(now),false,false,session,clock_ok,true,false,d_windows,ArraySize(d_windows))!=HG5_TRADE){d_clock_block+=count;continue;}
  HG6AccountFacts a;if(!HG6ReadAccount(a)||!HG6AdmissionAccount(a)||a.balance>9e13){d_account+=count;continue;}
  int units=HG5LotUnits((long)MathRound(a.balance*100.0),InpLotLadder,InpLadderCapUnits);if(count>1)d_stale+=count-1;
  if(!D10Submit(1,d_proposals[0],latest,x,units)){if(!d_fault)D10Status("WAIT: entry rejected or quote changed");}
 }
 d_ready=n>0&&n<HG6_TICK_BATCH&&lo<n&&d_raw[lo].time_msc==latest.time_msc&&d_raw[n-1].time_msc==latest.time_msc;
 if(!d_fault&&d_ready&&d_phase==D10_FLAT&&reconciled)D10Status(D10CanSend()?"ACTIVE - waiting for HybridGate proposal":"WAIT: Algo Trading permission");else if(!d_ready)D10Status("WARMUP / CATCHUP - no historical orders");
 if(d_callbacks-d_last_report>=10000){D10Report();d_last_report=d_callbacks;}
 Comment("HybridGate DEMO | ",d_status,"\nQuotes: ",d_cursor.Ordinal()," | proposals: ",d_seen," | sends: ",d_sends," | closed: ",d_closed,"\nPhase: ",d_phase," | actual net: ",d_net," | stale: ",d_stale," | blocked: ",d_busy+d_clock_block+d_account);
}
int OnInit(){
 d_test=MQLInfoInteger(MQL_TESTER)!=0;if(!D10Permission()){Print("HG10: REAL MONEY ACCOUNT PROHIBITED");return INIT_FAILED;}
 if(InpMagic==0||InpLadderCapUnits<1||InpLadderCapUnits>100||InpWarmupMinutes<0||InpWarmupMinutes>720||InpTesterUtcOffsetMinutes< -840||InpTesterUtcOffsetMinutes>840||InpMaxQuoteAgeMs<1||InpDeviationPoints<0||InpTimerMs<50||InpTimerMs>5000){Print("HG10 invalid inputs");return INIT_PARAMETERS_INCORRECT;}
 if(StringFind(_Symbol,"XAUUSD")<0||!HG6BrokerSpec(_Symbol)||AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING||!HG6FokAllowed(_Symbol)||!HG6VolumeAllowed(_Symbol,0.01)){Print("HG10 incompatible XAUUSD broker: requires USD, 100 oz contract, cents grid, hedging and FOK, 0.01 lot");return INIT_FAILED;}
 string key=AccountInfoString(ACCOUNT_SERVER)+"|"+IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN))+"|"+_Symbol+"|"+IntegerToString((long)InpMagic);uchar digest[],id[];if(!HG6TextDigest(key,digest))return INIT_FAILED;string prefix="HG10_"+HG6Hex(digest);
 if(!d_test){d_lock=FileOpen(prefix+".lock",FILE_READ|FILE_WRITE|FILE_BIN|FILE_COMMON);if(d_lock==INVALID_HANDLE){Print("HG10 another owner instance or lock unavailable");return INIT_FAILED;}d_scope=prefix;}
 else {for(int i=0;i<10000;i++){string candidate=prefix+"_TEST_"+IntegerToString(i);if(!FileIsExist(candidate+".genesis")&&!FileIsExist(candidate+".0.bin")&&!FileIsExist(candidate+".1.bin")){d_scope=candidate;break;}}if(d_scope=="")return INIT_FAILED;}
 if(!HG6TextDigest(d_scope+"|"+HG10_BUILD,id)||!d_store.Init(d_scope,id))return INIT_FAILED;uchar bytes[];int loaded=d_store.Load(bytes);if(loaded<0||!d_store.Healthy()||(loaded>0&&!D10Restore(bytes))){Print("HG10 durable state corrupt/incompatible; preserve files and reconcile manually");return INIT_FAILED;}if(loaded==0&&!D10Save())return INIT_FAILED;d_recovered=d_phase!=D10_FLAT;
 if(ArraySize(HG_ID)!=88||ArraySize(HG_MODEL_SHA)!=88)return INIT_FAILED;
 for(int i=0;i<88;i++){ArrayFree(bytes);if(IsStopped()||!HG8ReadModel(i,HG_MODEL_SHA[i],bytes)||!d_core.Load(i,bytes)){PrintFormat("HG10 MODEL ERROR index=%d name=%s error=%d",i,HG_ID[i],GetLastError());return INIT_FAILED;}if((i+1)%11==0)PrintFormat("HG10 models verified %d/88",i+1);}
 ArrayFree(bytes);d_initialized=true;if(!d_test&&!EventSetMillisecondTimer(InpTimerMs)){d_initialized=false;Print("HG10 timer setup failed");return INIT_FAILED;}
 Print("HG10 READY: 88 embedded models verified. ",d_test?"STRATEGY TESTER":"DEMO ACCOUNT ONLY",". Native broker execution enabled; real money forbidden.");return INIT_SUCCEEDED;
}
void OnTick(){D10Pump();}
void OnTimer(){D10Pump();}
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result){ // notification only; next tick/timer reads authoritative exposure
}
void OnDeinit(const int reason){EventKillTimer();if(d_initialized)D10Report();if(d_lock!=INVALID_HANDLE)FileClose(d_lock);Comment("");PrintFormat("HG10 DEINIT reason=%d phase=%d; no automatic liquidation on removal",reason,d_phase);}
