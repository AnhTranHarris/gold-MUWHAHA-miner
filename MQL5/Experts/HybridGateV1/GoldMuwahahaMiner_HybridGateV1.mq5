#property strict
#property version   "2.00"
#property description "Human Approved HybridGate V1 — native integration candidate; execution locked pending certification"
#include <HybridGateV1/HG6Core.mqh>
#include <HybridGateV1/HG5FileAdapter.mqh>
#include <HybridGateV1/HG5QCManifest.mqh>
#include <HybridGateV1/HG6Calendar.mqh>
#include <HybridGateV1/HG6Feed.mqh>
#include <HybridGateV1/HG6Storage.mqh>
#include <HybridGateV1/HG6Broker.mqh>
#include <HybridGateV1/HG6Terminal.mqh>
#include <HybridGateV1/HG6BuildIdentity.mqh>
// ============================================================================
// SECTION 01 — configuration. Strategy thresholds/weights are NOT external inputs.
// ============================================================================
input group "Identity and exact source history"
input ulong InpMagic=6202601;
input string InpRunId="QC001";
input datetime InpHistoryStart=D'2026.01.01 00:00'; // SOURCE clock, not guessed UTC
input int InpSourceUtcOffsetMinutes=0;
input bool InpClockMappingConfirmed=false;
input group "Frozen clock and sizing policy"
input bool InpUseTradingClock=true;
input bool InpWeeklyClock=false;
input bool InpLotLadder=false;
input int InpLadderCapUnits=10; // hundredths of a lot; original ladder default cap 0.10
input group "Operational limits — not fitted strategy parameters"
input int InpQuoteCapacity=262144;
input int InpMaxGroupsPerPump=256;
input int InpTimerMilliseconds=250;
input int InpMaxQuoteAgeMs=2000;
input int InpMaxServiceUs=250000;
input int InpCheckpointSeconds=15;
input int InpDeviationPoints=10;
input group "Execution certification lock"
input bool InpRequestDemoExecution=false; // build-time lock overrides this request
input bool InpEmergencyCloseAuthorized=false; // separately approved emergency policy required
// ============================================================================
// SECTION 02 — state and lifecycle. Single serial event-loop owner.
// ============================================================================
HG6Core g_core;HG6Cursor g_cursor;HG6Store g_store;HG6Broker g_broker;HG6Telemetry g_log;HG5OperationalGate g_ops;
HG5Window g_windows[];MqlTick g_raw[HG6_TICK_BATCH];HG5Quote g_group[];
HG5StageEvent g_stage[];HG5Proposal g_proposals[];HG5PathEvent g_paths[];HG5AccountEvent g_accounts[];
string g_scope="";int g_lock=INVALID_HANDLE;bool g_initialized=false,g_fatal=false,g_caught_up=false,g_dirty=false,g_overdue=false,g_trade_dirty=true;
long g_last_flat_ms=-1,g_mailbox=0;ulong g_saved_us=0,g_last_service=0;
bool g_tester=false,g_demo=false;
void HG6Fault(string why){if(!g_fatal)Print("HG6 FAIL CLOSED: ",why);g_fatal=true;g_ops.Disarm();}
bool HG6RunIdValid(string id){int n=StringLen(id);if(n<1||n>32)return false;for(int i=0;i<n;i++){ushort c=StringGetCharacter(id,i);if(!((c>=48&&c<=57)||(c>=65&&c<=90)||(c>=97&&c<=122)||c==45||c==95))return false;}return true;}
// ============================================================================
// SECTION 03 — snapshot identity, explicit field encoding, verified two-slot recovery.
// ============================================================================
bool HG6Save(){
 if(!g_initialized||g_fatal||!g_store.Healthy())return false;uchar core[],cursor[],all[];HG5StateCodec c;int version=1;
 if(!g_core.ExportState(core)||!c.BeginWrite()||!c.I32(version)||!g_cursor.Transfer(c)||!c.I64(g_last_flat_ms)||!c.Flag(g_overdue)||!c.Finish(cursor))return false;
 int a=ArraySize(cursor),b=ArraySize(core);if(a<=0||b<=0||a+b+16>HG6_MAX_ENVELOPE-96||ArrayResize(all,a+b+16)!=a+b+16)return false;
 HG6Put64(all,0,a);HG6Put64(all,8,b);if(ArrayCopy(all,cursor,16,0,a)!=a||ArrayCopy(all,core,16+a,0,b)!=b||!g_store.Save(all))return false;
 g_saved_us=GetMicrosecondCount();g_dirty=false;return true;
}
bool HG6Restore(const uchar &all[]){
 int n=ArraySize(all);if(n<18)return false;long a=HG6Get64(all,0),b=HG6Get64(all,8);if(a<=0||b<=0||a>HG5_STATE_MAX||b>HG5_STATE_MAX||a+b+16!=n)return false;
 uchar cursor[],core[];if(ArrayResize(cursor,(int)a)!=(int)a||ArrayResize(core,(int)b)!=(int)b||ArrayCopy(cursor,all,0,16,(int)a)!=(int)a||ArrayCopy(core,all,0,16+(int)a,(int)b)!=(int)b)return false;
 HG5StateCodec c;int v=0;if(!c.BeginRead(cursor)||!c.I32(v)||v!=1||!g_cursor.Transfer(c)||!c.I64(g_last_flat_ms)||!c.Flag(g_overdue)||!c.Done()||!g_core.RestoreState(core))return false;
 long z[];return g_core.Stats(z)&&z[0]==g_cursor.Ordinal()&&g_core.LastGroup()==(g_cursor.Last()>0?g_cursor.Last():-1);
}
// ============================================================================
// SECTION 04 — actual execution reconciliation, never the modeled account ledger.
// ============================================================================
bool HG6Reconcile(HG6Exposure &x){
 if(!HG6ExposureRead(_Symbol,InpMagic,x)||x.foreign||x.ambiguous){g_ops.Disarm();return false;}
 if(g_broker.Outstanding()){
  if(!g_broker.Reconcile(x)||!g_broker.Resolved())return false;
  if(g_broker.Filled()&&g_broker.IntentKind()==1){
   // A restored filled intent is idempotent only if the bound actual identity matches.
   if(g_core.ActualState()==0){if(x.ticket==0||!g_core.BindActual((long)x.identifier,x.time_ms,x.side,x.price_cents,x.units)){HG6Fault("actual fill anchor absent or behind committed history");return false;}}
   else if(g_core.ActualId()!=(long)x.identifier||g_core.ActualMs()!=x.time_ms||g_core.ActualPx()!=x.price_cents||g_core.ActualSide()!=x.side||g_core.ActualUnits()!=x.units){HG6Fault("actual fill identity mismatch");return false;}
  }else if(g_broker.Filled()&&g_broker.IntentKind()==2){
   if(x.ticket!=0){HG6Fault("close not flat");return false;}
   if(g_core.ActualState()>0&&(g_core.ActualId()!=g_broker.PositionId()||!g_core.ConfirmFlat(g_broker.PositionId())))return false;
   // Do not admit a fresh entry on the quote used for confirmed-flat reconciliation.
   MqlTick t;if(!SymbolInfoTick(_Symbol,t))return false;g_last_flat_ms=t.time_msc;g_overdue=false;
  }
  g_dirty=true;if(!HG6Save()||!g_broker.Release()){HG6Fault("reconciliation persistence failed");return false;}
 }
 if(x.pending)return false;
 if(x.ticket!=0){if(g_core.ActualState()==0||g_core.ActualId()!=(long)x.identifier||g_core.ActualSide()!=x.side||g_core.ActualPx()!=x.price_cents||g_core.ActualMs()!=x.time_ms||g_core.ActualUnits()!=x.units)return false;}
 else if(g_core.ActualState()!=0){HG6Fault("unreconciled external close; inspect authoritative deal history");return false;}
 g_trade_dirty=false;g_mailbox=0;return g_broker.Ready();
}
// ============================================================================
// SECTION 05 — clock, account risk and actual-exposure protection.
// ============================================================================
int HG6Action(long source_ms,const HG6Exposure &x,bool mapped,bool session){return HG5Clock(source_ms,x.ticket!=0,x.pending,session,mapped,InpUseTradingClock,g_overdue,g_windows,ArraySize(g_windows));}
bool HG6MaybeClose(const HG6Exposure &x,const MqlTick &latest,int clock_action,bool reconciled){
 if(x.ticket==0)return false;
 bool age_due=latest.time_msc-x.time_ms>=30000;datetime server=TimeTradeServer();if(server>0&&(long)server*1000-x.time_ms>=30000)age_due=true;
 bool urgent=clock_action==HG5_FLATTEN||age_due||g_overdue;
 if(urgent){g_overdue=true;g_dirty=true;g_ops.Disarm();}
 int reason=g_core.ActualReason();if(!urgent&&reason<=0)return false;
 // The source software floor is not a broker stop. Unknown/partial/foreign exposures
 // cannot be guessed closed; report for operator intervention. Demo release locked.
 if(!g_demo||!reconciled||g_broker.Outstanding()||x.foreign||x.ambiguous||x.pending||(!InpEmergencyCloseAuthorized&&urgent&&reason<=0)){
  g_log.Event("CLOSE_BLOCKED",latest.time_msc,(long)x.identifier,reason,(long)urgent,clock_action);return true;
 }
 if(!HG6Save()){HG6Fault("cannot persist close intent context");return true;}
 if(!g_broker.Submit(2,g_core.ActualId(),-x.side,x.units,latest,x,(ulong)InpDeviationPoints))g_ops.Disarm();return true;
}
void HG6MaybeEntry(const HG5Proposal &p,const MqlTick &latest,const HG6Exposure &x,bool mapped,bool session,bool reconciled,bool fresh){
 if(!g_demo||!fresh||!reconciled||!g_ops.EntriesAllowed()||g_broker.Outstanding()||x.ticket!=0||x.pending||x.foreign||x.ambiguous||g_core.ActualState()!=0||p.t<=g_last_flat_ms||p.t>=latest.time_msc||latest.time_msc-p.t>InpMaxQuoteAgeMs)return;
 datetime server=TimeTradeServer();long now=(long)server*1000;if(now<latest.time_msc)now=latest.time_msc;
 if(HG6Action(p.t,x,mapped,session)!=HG5_TRADE||HG6Action(now,x,mapped,session)!=HG5_TRADE)return;
 double bal=AccountInfoDouble(ACCOUNT_BALANCE);if(!MathIsValidNumber(bal)||bal<=0||bal>9e13)return;
 int units=HG5LotUnits((long)MathRound(bal*100.0),InpLotLadder,InpLadderCapUnits);if(units<=0)return;
 if(!HG6Save()){HG6Fault("cannot persist entry intent context");return;}
 if(!g_broker.Submit(1,p.id,p.side,units,latest,x,(ulong)InpDeviationPoints))g_ops.Disarm();
}
// ============================================================================
// SECTION 06 — bounded chronological group processing. The final same-ms group
// is deliberately withheld until a strictly later timestamp is observed.
// ============================================================================
void HG6Pump(){
 if(!g_initialized)return;if(g_fatal){HG6Exposure fault_exposure;if(HG6ExposureRead(_Symbol,InpMagic,fault_exposure)&&(fault_exposure.ticket||fault_exposure.pending))Comment("HG6 QUARANTINE: owned exposure or pending order; manual reconciliation required. No orders enabled.");return;}ulong started=GetMicrosecondCount();MqlTick latest;
 if(!SymbolInfoTick(_Symbol,latest)||latest.time_msc<=0)return;
 if(g_cursor.Last()>latest.time_msc){HG6Fault("terminal history moved behind committed cursor");return;}
 HG6Exposure x;bool reconciled=HG6Reconcile(x);if(g_fatal)return;
 datetime server=TimeTradeServer();bool mapped=HG6ClockMapping(InpSourceUtcOffsetMinutes,InpClockMappingConfirmed,g_tester,server),session=HG6TradeSession(_Symbol,server);
 long now=(long)server*1000;if(now<latest.time_msc)now=latest.time_msc;
 bool close_requested=HG6MaybeClose(x,latest,HG6Action(now,x,mapped,session),reconciled);if(g_fatal)return;
 ResetLastError();int n=CopyTicks(_Symbol,g_raw,COPY_TICKS_ALL,(ulong)g_cursor.From(),HG6_TICK_BATCH);int err=GetLastError();
 if(n<0||err!=0){g_ops.Disarm();g_caught_up=false;g_log.Event("HISTORY_WAIT",latest.time_msc,0,err,n,0);return;}
 int first=0;if(!g_cursor.VerifyBatch(g_raw,n,first)){HG6Fault("quote overlap/order/grid integrity");return;}
 bool was_caught=g_caught_up;g_caught_up=false;int count=0,lo=first;
 for(;lo<n&&count<InpMaxGroupsPerPump;){
  int end=g_cursor.NextEnd(g_raw,n,lo);if(end<0){HG6Fault("timestamp group capacity/order");return;}if(end==0)break;
  if(!g_cursor.Group(g_raw,lo,end,g_group)||!g_core.StepGroup(g_group,g_stage,g_proposals,g_paths,g_accounts)||!g_cursor.Commit(g_raw,lo,end)){HG6Fault("frozen core or feed commit failure");return;}
  g_dirty=true;count++;lo=end;
  for(int j=0;j<ArraySize(g_proposals);j++)if(!g_log.Event("PROPOSAL",g_proposals[j].t,g_proposals[j].id,g_proposals[j].side,g_proposals[j].origin,g_cursor.Ordinal())){HG6Fault("telemetry failure");return;}
  // Send only a proposal from the final complete group of a live, caught-up batch.
  // Never replay a stale historical proposal. A close/busy epoch cannot admit a new one.
  bool fresh=was_caught&&n<HG6_TICK_BATCH&&g_raw[n-1].time_msc==latest.time_msc&&g_raw[lo].time_msc==latest.time_msc;
  if(fresh&&!close_requested&&ArraySize(g_proposals)>0&&GetMicrosecondCount()-started<=(ulong)InpMaxServiceUs){
   if(ArraySize(g_proposals)>1)g_log.Event("MULTIPLE_PROPOSALS",g_proposals[0].t,g_proposals[0].id,ArraySize(g_proposals),0,0);
   HG6MaybeEntry(g_proposals[0],latest,x,mapped,session,reconciled,true);
  }
  if(g_fatal)return;
  if(GetMicrosecondCount()-started>(ulong)InpMaxServiceUs)break;
 }
 g_caught_up=n>0&&n<HG6_TICK_BATCH&&lo<n&&g_raw[lo].time_msc==latest.time_msc&&g_raw[n-1].time_msc==latest.time_msc;
 g_last_service=GetMicrosecondCount()-started;
 if(g_demo){HG5OpsSample s;s.now_us=(long)GetMicrosecondCount();s.quote_age_ms=now-latest.time_msc;s.queue_us=0;s.service_us=(long)g_last_service;s.trade_lag_ms=g_trade_dirty?InpMaxQuoteAgeMs+1:0;s.queue=n-lo;s.active=x.ticket!=0?1:0;s.mailbox=(int)g_mailbox;s.connected=TerminalInfoInteger(TERMINAL_CONNECTED)!=0;s.calendar_ok=mapped&&now>=g_windows[0].open_ms&&now<g_windows[ArraySize(g_windows)-1].close_ms;s.identity_ok=HG6BrokerSpec(_Symbol);s.history_ok=g_caught_up;s.reconciled=reconciled;s.storage_ok=g_store.Healthy()&&g_broker.Ready();g_ops.Check(s);}
 if(g_dirty&&GetMicrosecondCount()-g_saved_us>=(ulong)InpCheckpointSeconds*1000000&&!HG6Save()){HG6Fault("periodic checkpoint failure");return;}
 // No order API in OnTradeTransaction. Reconcile again next tick/timer.
 Comment("HybridGate V1 | ",g_demo?"DEMO CANDIDATE":"OBSERVATION ONLY","\nQuotes committed: ",g_cursor.Ordinal()," | lag: ",latest.time_msc-g_cursor.Last()," ms\nState: ",g_caught_up?"caught up":"catching up"," | native execution locked");
}
// ============================================================================
// SECTION 07 — MetaTrader event entry points. All lifecycle transitions explicit.
// ============================================================================
int OnInit(){
 if(InpRequestDemoExecution&&HG6_EXECUTION_RELEASED==0){Print("HG6: execution release lock; compile and run QC first");return INIT_PARAMETERS_INCORRECT;}
 if(InpMagic==0||!HG6RunIdValid(InpRunId)||InpHistoryStart<=0||InpLadderCapUnits<1||InpLadderCapUnits>100||InpQuoteCapacity<32768||InpQuoteCapacity>262144||InpMaxGroupsPerPump<1||InpMaxGroupsPerPump>4096||InpTimerMilliseconds<50||InpTimerMilliseconds>5000||InpMaxQuoteAgeMs<1||InpMaxServiceUs<1000||InpCheckpointSeconds<1||InpDeviationPoints<0)return INIT_PARAMETERS_INCORRECT;
 if(StringFind(_Symbol,"XAUUSD")<0||!HG6BrokerSpec(_Symbol)){Print("HG6: incompatible XAUUSD/account grid/contract/currency");return INIT_FAILED;}
 g_tester=MQLInfoInteger(MQL_TESTER)!=0;g_demo=InpRequestDemoExecution&&HG6_EXECUTION_RELEASED==1&&!g_tester&&AccountInfoInteger(ACCOUNT_TRADE_MODE)==ACCOUNT_TRADE_MODE_DEMO;
 if(!HG6Windows(InpWeeklyClock,InpSourceUtcOffsetMinutes,g_windows)||!g_cursor.Init((long)InpHistoryStart*1000))return INIT_FAILED;
 uchar id[],lock_id[];string scope=AccountInfoString(ACCOUNT_SERVER)+"|"+IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN))+"|"+_Symbol+"|"+IntegerToString((long)InpMagic);
 if(!HG6TextDigest(scope,lock_id))return INIT_FAILED;g_scope="HybridGateV1_"+HG6Hex(lock_id)+"_"+InpRunId+(g_tester?"_TEST":"_OBS");
 // The common-directory lock prevents same-account/symbol/magic instances on this host.
 // It does not claim cross-machine mutual exclusion; broker ownership checks remain mandatory.
 if(!g_tester){g_lock=FileOpen("HybridGateV1_"+HG6Hex(lock_id)+".lock",FILE_READ|FILE_WRITE|FILE_BIN|FILE_COMMON);if(g_lock==INVALID_HANDLE){Print("HG6: instance lock unavailable");return INIT_FAILED;}}
 string config=scope+"|"+HG6_BUILD_ID+"|"+InpRunId+"|"+IntegerToString((long)InpHistoryStart)+"|"+IntegerToString(InpSourceUtcOffsetMinutes)+"|"+IntegerToString((int)InpClockMappingConfirmed)+"|"+IntegerToString((int)InpWeeklyClock)+"|"+IntegerToString((int)InpUseTradingClock)+"|"+IntegerToString((int)InpLotLadder)+"|"+IntegerToString(InpLadderCapUnits)+"|"+IntegerToString(InpQuoteCapacity)+"|"+IntegerToString((int)g_tester)+"|"+IntegerToString((int)g_demo)+"|"+IntegerToString(InpMaxGroupsPerPump)+"|"+IntegerToString(InpTimerMilliseconds)+"|"+IntegerToString(InpMaxQuoteAgeMs)+"|"+IntegerToString(InpMaxServiceUs)+"|"+IntegerToString(InpCheckpointSeconds)+"|"+IntegerToString(InpDeviationPoints)+"|"+IntegerToString((int)InpEmergencyCloseAuthorized);
 if(!HG6TextDigest(config,id)||!g_store.Init(g_scope+"_state",id)||!g_log.Open(g_scope+"_events"))return INIT_FAILED;
 // Reconcile actual account even before the model files load; no order can be sent.
 HG6Exposure x;if(!HG6ExposureRead(_Symbol,InpMagic,x))return INIT_FAILED;if(x.ticket||x.pending||x.foreign||x.ambiguous)Print("HG6 startup exposure requires reconciliation; no new orders");
 if(ArraySize(HG_ID)!=88||ArraySize(HG_MODEL_SHA)!=88)return INIT_FAILED;
 uchar bytes[];for(int i=0;i<88;i++){if(IsStopped()||!HG5ReadVerified("HG5QC\\"+HG_ID[i]+".hg5p",HG_MODEL_SHA[i],67108864,bytes)||!g_core.Load(i,bytes)){PrintFormat("HG6: model %d integrity/shape failure %s",i,HG_ID[i]);return INIT_FAILED;}ArrayFree(bytes);}
 if(!g_core.Start(g_windows,InpQuoteCapacity)||!g_broker.Init(_Symbol,InpMagic,g_scope+"_intent",id,g_demo))return INIT_FAILED;
 int loaded=g_store.Load(bytes);if(loaded<0||(loaded>0&&!HG6Restore(bytes))||!g_store.Healthy()){Print("HG6: checkpoint corrupt, ambiguous or incompatible; preserve files and reconcile manually");return INIT_FAILED;}
 ArrayFree(bytes);HG5OpsLimits lim;lim.max_quote_age_ms=InpMaxQuoteAgeMs;lim.max_queue_us=InpMaxServiceUs;lim.max_service_us=InpMaxServiceUs;lim.max_trade_lag_ms=InpMaxQuoteAgeMs;lim.max_queue=HG6_TICK_BATCH;lim.max_active=1;lim.max_mailbox=1024;if(!g_ops.Init(lim))return INIT_FAILED;
 g_initialized=true;g_saved_us=GetMicrosecondCount();if(!EventSetMillisecondTimer(InpTimerMilliseconds)){g_initialized=false;return INIT_FAILED;}
 // Deliberately no automatic Arm(): final native acceptance, live mapping, warmup,
 // reconciliation and explicit release must precede any order authorization.
 PrintFormat("HG6 initialized build=%s restored=%d ordinal=%I64d execution_lock=%d",HG6_BUILD_ID,loaded,g_cursor.Ordinal(),HG6_EXECUTION_RELEASED);return INIT_SUCCEEDED;
}
void OnTick(){HG6Pump();}
void OnTimer(){HG6Pump();}
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result){
 // All account transactions invalidate prior snapshot, irrespective of callback order.
 g_trade_dirty=true;if(g_mailbox<1025)g_mailbox++;if(g_mailbox>1024)g_ops.Disarm();
}
void OnDeinit(const int reason){EventKillTimer();if(g_initialized&&g_dirty&&!g_fatal&&!HG6Save())Print("HG6: final checkpoint failed; preserve prior generation");g_log.Close();if(g_lock!=INVALID_HANDLE)FileClose(g_lock);Comment("");PrintFormat("HG6 deinit reason=%d ordinal=%I64d; no implied liquidation",reason,g_cursor.Ordinal());}
