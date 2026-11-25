#property strict
// SECTION 00 — exact tester asset declarations; native transfer still requires QC.
#property tester_file "HG5QC\\000_first_in_sample_entry_router.hg5p"
#property tester_file "HG5QC\\001_rearm_in_sample_entry_router.hg5p"
#property tester_file "HG5QC\\002_v15_rank1_hazard_IS.hg5p"
#property tester_file "HG5QC\\003_v15_rank2_hazard_IS.hg5p"
#property tester_file "HG5QC\\004_v15f_first_side_IS.hg5p"
#property tester_file "HG5QC\\005_v15f_rearm_side_IS.hg5p"
#property tester_file "HG5QC\\006_v16_event_hazard_0.hg5p"
#property tester_file "HG5QC\\007_v16_event_hazard_1.hg5p"
#property tester_file "HG5QC\\008_v16_event_side_IS.hg5p"
#property tester_file "HG5QC\\009_v17_hazard_0.hg5p"
#property tester_file "HG5QC\\010_v17_hazard_1.hg5p"
#property tester_file "HG5QC\\011_v20_action_role0.hg5p"
#property tester_file "HG5QC\\012_v20_action_role1.hg5p"
#property tester_file "HG5QC\\013_v20_advantage_role0.hg5p"
#property tester_file "HG5QC\\014_v20_advantage_role1.hg5p"
#property tester_file "HG5QC\\015_v20_entry_confidence.hg5p"
#property tester_file "HG5QC\\016_v22_wide.hg5p"
#property tester_file "HG5QC\\017_v22_tight.hg5p"
#property tester_file "HG5QC\\018_v22_marginal.hg5p"
#property tester_file "HG5QC\\019_struct_gain.hg5p"
#property tester_file "HG5QC\\020_struct_loss.hg5p"
#property tester_file "HG5QC\\021_flip_gain.hg5p"
#property tester_file "HG5QC\\022_flip_loss.hg5p"
#property tester_file "HG5QC\\023_rg.hg5p"
#property tester_file "HG5QC\\024_rl.hg5p"
#property tester_file "HG5QC\\025_g.hg5p"
#property tester_file "HG5QC\\026_l.hg5p"
#property tester_file "HG5QC\\027_cont_gain.hg5p"
#property tester_file "HG5QC\\028_cont_loss.hg5p"
#property tester_file "HG5QC\\029_base_gain.hg5p"
#property tester_file "HG5QC\\030_base_loss.hg5p"
#property tester_file "HG5QC\\031_base_cont_gain.hg5p"
#property tester_file "HG5QC\\032_base_cont_loss.hg5p"
#property tester_file "HG5QC\\033_proxy_gain.hg5p"
#property tester_file "HG5QC\\034_proxy_loss.hg5p"
#property tester_file "HG5QC\\035_discount_gain.hg5p"
#property tester_file "HG5QC\\036_discount_loss.hg5p"
#property tester_file "HG5QC\\037_anchor_gain.hg5p"
#property tester_file "HG5QC\\038_anchor_loss.hg5p"
#property tester_file "HG5QC\\039_stack_gain.hg5p"
#property tester_file "HG5QC\\040_stack_loss.hg5p"
#property tester_file "HG5QC\\041_wide_15.hg5p"
#property tester_file "HG5QC\\042_wide_30.hg5p"
#property tester_file "HG5QC\\043_rev_g.hg5p"
#property tester_file "HG5QC\\044_rev_l.hg5p"
#property tester_file "HG5QC\\045_rev_w.hg5p"
#property tester_file "HG5QC\\046_disc_g.hg5p"
#property tester_file "HG5QC\\047_disc_l.hg5p"
#property tester_file "HG5QC\\048_disc_w.hg5p"
#property tester_file "HG5QC\\049_meta_g.hg5p"
#property tester_file "HG5QC\\050_meta_l.hg5p"
#property tester_file "HG5QC\\051_meta_w.hg5p"
#property tester_file "HG5QC\\052_anchor_g.hg5p"
#property tester_file "HG5QC\\053_anchor_l.hg5p"
#property tester_file "HG5QC\\054_anchor_w.hg5p"
#property tester_file "HG5QC\\055_option_g.hg5p"
#property tester_file "HG5QC\\056_option_l.hg5p"
#property tester_file "HG5QC\\057_option_w.hg5p"
#property tester_file "HG5QC\\058_stack_g.hg5p"
#property tester_file "HG5QC\\059_stack_l.hg5p"
#property tester_file "HG5QC\\060_stack_w.hg5p"
#property tester_file "HG5QC\\061_duration.hg5p"
#property tester_file "HG5QC\\062_value.hg5p"
#property tester_file "HG5QC\\063_duration_residual.hg5p"
#property tester_file "HG5QC\\064_value_residual.hg5p"
#property tester_file "HG5QC\\065_stack_duration.hg5p"
#property tester_file "HG5QC\\066_stack_value.hg5p"
#property tester_file "HG5QC\\067_micro_duration_residual.hg5p"
#property tester_file "HG5QC\\068_micro_value_residual.hg5p"
#property tester_file "HG5QC\\069_duration_residual_1.hg5p"
#property tester_file "HG5QC\\070_value_residual_1.hg5p"
#property tester_file "HG5QC\\071_duration_residual_2.hg5p"
#property tester_file "HG5QC\\072_value_residual_2.hg5p"
#property tester_file "HG5QC\\073_duration_residual_3.hg5p"
#property tester_file "HG5QC\\074_value_residual_3.hg5p"
#property tester_file "HG5QC\\075_duration_residual_4.hg5p"
#property tester_file "HG5QC\\076_value_residual_4.hg5p"
#property tester_file "HG5QC\\077_duration_residual_5.hg5p"
#property tester_file "HG5QC\\078_continuation_gain.hg5p"
#property tester_file "HG5QC\\079_continuation_risk.hg5p"
#property tester_file "HG5QC\\080_exit_actor.hg5p"
#property tester_file "HG5QC\\081_fill_premium.hg5p"
#property tester_file "HG5QC\\082_future_gain.hg5p"
#property tester_file "HG5QC\\083_local_downside.hg5p"
#property tester_file "HG5QC\\085_actor_1_1.hg5p"
#property tester_file "HG5QC\\086_renewal_gate.hg5p"
#property tester_file "HG5QC\\087_precision_actor.hg5p"
#property tester_file "HG5QC\\088_regret_head.hg5p"
#property version   "2.01"
#property description "Human Approved HybridGate V1 — tester-only integration candidate; demo/live execution locked"
#include <HybridGateV1/HG6Core.mqh>
#include <HybridGateV1/HG5FileAdapter.mqh>
#include <HybridGateV1/HG5QCManifest.mqh>
#include <HybridGateV1/HG6Calendar.mqh>
#include <HybridGateV1/HG6Feed.mqh>
#include <HybridGateV1/HG6Storage.mqh>
#include <HybridGateV1/HG6Broker.mqh>
#include <HybridGateV1/HG6Terminal.mqh>
#include <HybridGateV1/HG6Readiness.mqh>
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
input bool InpRequestDemoExecution=false; // demo/live remain hard locked
input bool InpRequestTesterExecution=false; // explicit simulated orders only in Strategy Tester
input long InpExpectedFirstQuoteMs=1767315600480; // exact Jan 2026 source anchor
input int InpExpectedFirstBidCents=432437;
input int InpExpectedFirstAskCents=432744;
input bool InpEmergencyCloseAuthorized=false; // separately approved emergency policy required
// ============================================================================
// SECTION 02 — state and lifecycle. Single serial event-loop owner.
// ============================================================================
HG6Core g_core;HG6Cursor g_cursor;HG6Store g_store;HG6Broker g_broker;HG6Telemetry g_log;HG6Readiness g_ops;
HG5Window g_windows[];MqlTick g_raw[HG6_TICK_BATCH];HG5Quote g_group[];
HG5StageEvent g_stage[];HG5Proposal g_proposals[];HG5PathEvent g_paths[];HG5AccountEvent g_accounts[];
string g_scope="";int g_lock=INVALID_HANDLE;bool g_initialized=false,g_fatal=false,g_caught_up=false,g_dirty=false,g_overdue=false,g_trade_dirty=true;
long g_last_flat_ms=-1,g_mailbox=0,g_seen_proposals=0,g_suppressed_proposals=0;ulong g_saved_us=0,g_last_service=0,g_last_copy_us=0;
bool g_tester=false,g_execute=false,g_origin_verified=false;ulong g_trade_first_us=0;long g_dispatched=0,g_gate_blocked=0;
void HG6Fault(string why){if(!g_fatal)Print("HG6 FAIL CLOSED: ",why);g_fatal=true;g_ops.Quarantine();}
bool HG6RunIdValid(string id){int n=StringLen(id);if(n<1||n>32)return false;for(int i=0;i<n;i++){ushort c=StringGetCharacter(id,i);if(!((c>=48&&c<=57)||(c>=65&&c<=90)||(c>=97&&c<=122)||c==45||c==95))return false;}return true;}
// ============================================================================
// SECTION 03 — snapshot identity, explicit field encoding, verified two-slot recovery.
// ============================================================================
bool HG6Save(){
 if(!g_initialized||g_fatal||!g_store.Healthy())return false;uchar core[],cursor[],all[];HG5StateCodec c;int version=2;
 if(!g_core.ExportState(core)||!c.BeginWrite()||!c.I32(version)||!g_cursor.Transfer(c)||!c.I64(g_last_flat_ms)||!c.Flag(g_overdue)||!c.Flag(g_origin_verified)||!c.Finish(cursor))return false;
 int a=ArraySize(cursor),b=ArraySize(core);if(a<=0||b<=0||a+b+16>HG6_MAX_ENVELOPE-96||ArrayResize(all,a+b+16)!=a+b+16)return false;
 HG6Put64(all,0,a);HG6Put64(all,8,b);if(ArrayCopy(all,cursor,16,0,a)!=a||ArrayCopy(all,core,16+a,0,b)!=b||!g_store.Save(all))return false;
 g_saved_us=GetMicrosecondCount();g_dirty=false;return true;
}
bool HG6Restore(const uchar &all[]){
 int n=ArraySize(all);if(n<18)return false;long a=HG6Get64(all,0),b=HG6Get64(all,8);if(a<=0||b<=0||a>HG5_STATE_MAX||b>HG5_STATE_MAX||a+b+16!=n)return false;
 uchar cursor[],core[];if(ArrayResize(cursor,(int)a)!=(int)a||ArrayResize(core,(int)b)!=(int)b||ArrayCopy(cursor,all,0,16,(int)a)!=(int)a||ArrayCopy(core,all,0,16+(int)a,(int)b)!=(int)b)return false;
 HG5StateCodec c;int v=0;if(!c.BeginRead(cursor)||!c.I32(v)||v!=2||!g_cursor.Transfer(c)||!c.I64(g_last_flat_ms)||!c.Flag(g_overdue)||!c.Flag(g_origin_verified)||!c.Done()||!g_core.RestoreState(core))return false;
 long z[];return g_core.Stats(z)&&z[0]==g_cursor.Ordinal()&&g_core.LastGroup()==(g_cursor.Last()>0?g_cursor.Last():-1);
}
// ============================================================================
// SECTION 04 — actual execution reconciliation, never the modeled account ledger.
// ============================================================================
bool HG6RecordFlat(long pos){
 if(g_core.ActualState()!=0&&!g_core.ConfirmFlat(pos))return false;
 MqlTick t;if(!SymbolInfoTick(_Symbol,t))return false;g_last_flat_ms=t.time_msc;g_overdue=false;g_dirty=true;return true;
}
bool HG6Reconcile(HG6Exposure &x){
 if(!HG6ExposureRead(_Symbol,InpMagic,x)||x.foreign||x.ambiguous){x.ambiguous=true;g_ops.Disarm();return false;}
 if(g_broker.Outstanding()){
  if(!g_broker.Reconcile(x)||!g_broker.Resolved())return false;
  if(g_broker.Filled()&&g_broker.IntentKind()==1){
   if(!x.ticket)return false;
   if(g_core.ActualState()==0){
    bool ok=x.anchor_ok?g_core.BindActual((long)x.identifier,x.time_ms,x.side,x.price_cents,x.units):g_core.BindUnmodeled((long)x.identifier,x.time_ms,x.side,x.units);
    if(!ok&&g_core.ActualState()!=3){HG6Fault("cannot bind confirmed position identity");return false;}
    if(g_core.ActualState()==3){g_ops.Disarm();g_log.Event("ACTUAL_ANCHOR_QUARANTINE",x.time_ms,(long)x.identifier,0,0,0);g_overdue=true;}
   }else if(g_core.ActualId()!=(long)x.identifier||g_core.ActualMs()!=x.time_ms||g_core.ActualSide()!=x.side||g_core.ActualUnits()!=x.units||(g_core.ActualState()!=3&&(!x.anchor_ok||g_core.ActualPx()!=x.price_cents))){HG6Fault("actual fill identity mismatch");return false;}
  }else if(g_broker.Filled()&&g_broker.IntentKind()==2){
   long pos=g_broker.PositionId();if(x.ticket){if((long)x.identifier!=pos||!g_core.ReduceActual(pos,x.units))return false;g_overdue=true;}
   else if(!HG6RecordFlat(pos))return false;
  }
  g_dirty=true;if(!HG6Save()||!g_broker.Release()){HG6Fault("reconciliation persistence failed");return false;}
 }
 if(x.pending)return false;
 if(x.ticket){if(g_core.ActualState()==0||g_core.ActualId()!=(long)x.identifier||g_core.ActualSide()!=x.side||g_core.ActualMs()!=x.time_ms||g_core.ActualUnits()!=x.units||(g_core.ActualState()!=3&&(!x.anchor_ok||g_core.ActualPx()!=x.price_cents)))return false;}
 else if(g_core.ActualState()!=0){long pos=g_core.ActualId();if(!g_broker.ExternalFlat(pos)||!HG6RecordFlat(pos)||!HG6Save()){g_ops.Disarm();return false;}}
 else if(g_broker.ActiveLedgerPosition()!=0){g_ops.Disarm();return false;}
 if(!x.ticket&&!x.pending&&g_overdue){g_overdue=false;g_dirty=true;if(!HG6Save()){HG6Fault("flat-state persistence failed");return false;}}
 g_trade_dirty=false;g_mailbox=0;g_trade_first_us=0;return g_broker.Ready();
}
// ============================================================================
// SECTION 05 — clock, account risk and actual-exposure protection.
// ============================================================================
int HG6Action(long source_ms,const HG6Exposure &x,bool mapped,bool session){return HG5Clock(source_ms,x.ticket!=0,x.pending,session,mapped,InpUseTradingClock,g_overdue,g_windows,ArraySize(g_windows));}
bool HG6MaybeClose(const HG6Exposure &x,const MqlTick &latest,int clock_action,bool reconciled){
 if(x.pending&&(clock_action==HG5_DRAIN_CANCEL_PENDING||clock_action==HG5_FLATTEN||g_overdue)){
  g_ops.Disarm();if(clock_action==HG5_FLATTEN)g_overdue=true;
  if(g_execute&&InpEmergencyCloseAuthorized&&!x.foreign&&!x.ambiguous)g_broker.CancelPending(x);
  return true;
 }
 if(x.ticket==0)return false;
 bool age_due=latest.time_msc-x.time_ms>=30000;datetime server=TimeTradeServer();if(server>0&&(long)server*1000-x.time_ms>=30000)age_due=true;
 HG6AccountFacts facts;bool risk=HG6ReadAccount(facts)&&HG6AccountUrgent(facts);
 bool urgent=clock_action==HG5_FLATTEN||age_due||g_overdue||g_core.ActualState()==3||risk;
 if(urgent){g_overdue=true;g_dirty=true;g_ops.Disarm();}
 int reason=g_core.ActualReason();if(!urgent&&reason<=0)return false;
 // The source software floor is not a broker stop. Unknown/partial/foreign exposures
 // cannot be guessed closed; report for operator intervention. Demo release locked.
 if(!g_execute||(!reconciled&&!(urgent&&g_broker.Ready()&&g_broker.ActiveLedgerPosition()==(long)x.identifier))||g_broker.Outstanding()||x.foreign||x.ambiguous||x.pending||(!InpEmergencyCloseAuthorized&&urgent&&reason<=0)){
  g_log.Event("CLOSE_BLOCKED",latest.time_msc,(long)x.identifier,reason,(long)urgent,clock_action);return true;
 }
 if(!HG6Save()){HG6Fault("cannot persist close intent context");return true;}
 if(!g_broker.Submit(2,g_core.ActualId(),-x.side,x.units,latest,x,(ulong)InpDeviationPoints))g_ops.Disarm();return true;
}
// Fatal-state protection never evaluates the failed model or creates an entry.
// Only a known owned position in the explicitly authorized simulated tester may be closed.
void HG6RiskOnly(){
 HG6Exposure x;MqlTick t;if(!HG6ExposureRead(_Symbol,InpMagic,x)||x.foreign||x.ambiguous||!SymbolInfoTick(_Symbol,t))return;
 if(!x.ticket&&!x.pending&&!g_broker.Outstanding()&&g_broker.ActiveLedgerPosition()==0)return;
 Comment("HG6 QUARANTINE: owned exposure detected; entries disabled");
 if(!g_execute||!InpEmergencyCloseAuthorized)return;
 if(g_broker.Outstanding()){bool resolved=g_broker.Reconcile(x)&&g_broker.Resolved();if(x.pending){g_broker.CancelPending(x);return;}if(!resolved||!g_broker.Release())return;}
 if(x.pending)return;
 if(!x.ticket&&g_broker.ActiveLedgerPosition()!=0){g_broker.ExternalFlat(g_broker.ActiveLedgerPosition());return;}
 if(x.ticket&&g_broker.Ready()&&g_broker.ActiveLedgerPosition()==(long)x.identifier)g_broker.Submit(2,(long)x.identifier,-x.side,x.units,t,x,(ulong)InpDeviationPoints);
}
bool HG6CheckReadiness(const HG6Exposure &x,const MqlTick &latest,long now,bool mapped,bool reconciled,bool fresh,int backlog,ulong started){
 HG5OpsSample sample;ulong now_us=GetMicrosecondCount();sample.now_us=(long)now_us;sample.quote_age_ms=now-latest.time_msc;sample.queue_us=(long)g_last_copy_us;sample.service_us=(long)(now_us-started);
 sample.trade_lag_ms=g_trade_first_us>0?(long)((now_us-g_trade_first_us)/1000):0;sample.queue=backlog;sample.active=x.ticket?1:0;sample.mailbox=(int)g_mailbox;
 sample.connected=g_tester||TerminalInfoInteger(TERMINAL_CONNECTED)!=0;sample.calendar_ok=mapped&&ArraySize(g_windows)>0&&now>=g_windows[0].open_ms&&now<g_windows[ArraySize(g_windows)-1].close_ms;sample.identity_ok=HG6BrokerSpec(_Symbol);
 sample.history_ok=fresh&&g_origin_verified;sample.reconciled=reconciled&&!g_trade_dirty;sample.storage_ok=g_store.Healthy()&&g_broker.IntegrityHealthy();
 return g_ops.Arm(sample,g_execute&&g_tester&&!g_fatal&&!g_overdue);
}
void HG6MaybeEntry(const HG5Proposal &p,const MqlTick &latest,const HG6Exposure &x,bool mapped,bool session,bool reconciled,bool fresh){
 if(!g_execute||!g_tester||!g_origin_verified||!fresh||!reconciled||!g_ops.EntriesAllowed()||g_broker.Outstanding()||x.ticket!=0||x.pending||x.foreign||x.ambiguous||g_core.ActualState()!=0||p.t<=g_last_flat_ms||p.t>=latest.time_msc||latest.time_msc-p.t>InpMaxQuoteAgeMs)return;
 datetime server=TimeTradeServer();long now=(long)server*1000;if(now<latest.time_msc)now=latest.time_msc;
 if(HG6Action(p.t,x,mapped,session)!=HG5_TRADE||HG6Action(now,x,mapped,session)!=HG5_TRADE)return;
 HG6AccountFacts facts;if(!HG6ReadAccount(facts)||!HG6AdmissionAccount(facts)||facts.balance>9e13)return;double bal=facts.balance;
 int units=HG5LotUnits((long)MathRound(bal*100.0),InpLotLadder,InpLadderCapUnits);if(units<=0)return;
 if(!HG6Save()){HG6Fault("cannot persist entry intent context");return;}
 if(g_broker.Submit(1,p.id,p.side,units,latest,x,(ulong)InpDeviationPoints))g_dispatched++;else g_ops.Disarm();
}
// ============================================================================
// SECTION 06 — bounded chronological group processing. The final same-ms group
// is deliberately withheld until a strictly later timestamp is observed.
// ============================================================================
void HG6Pump(){
 if(!g_initialized)return;if(g_fatal){HG6RiskOnly();return;}ulong started=GetMicrosecondCount();MqlTick latest;
 if(!SymbolInfoTick(_Symbol,latest)||latest.time_msc<=0)return;
 if(g_cursor.Last()>latest.time_msc){HG6Fault("terminal history moved behind committed cursor");return;}
 HG6Exposure x;bool reconciled=HG6Reconcile(x);if(g_fatal)return;
 datetime server=TimeTradeServer();bool mapped=HG6ClockMapping(InpSourceUtcOffsetMinutes,InpClockMappingConfirmed,g_tester,server),session=HG6TradeSession(_Symbol,server);
 long now=(long)server*1000;if(now<latest.time_msc)now=latest.time_msc;
 bool close_requested=HG6MaybeClose(x,latest,HG6Action(now,x,mapped,session),reconciled);if(g_fatal)return;
 ulong copy_start=GetMicrosecondCount();ResetLastError();int n=CopyTicks(_Symbol,g_raw,COPY_TICKS_ALL,(ulong)g_cursor.From(),HG6_TICK_BATCH);int err=GetLastError();g_last_copy_us=GetMicrosecondCount()-copy_start;
 if(n<0||n>ArraySize(g_raw)||err!=0){g_ops.Disarm();g_caught_up=false;g_log.Event("HISTORY_WAIT",latest.time_msc,0,err,n,0);return;}
 for(int k=1;k<n;k++)if(g_raw[k].time_msc<g_raw[k-1].time_msc){HG6Fault("unordered terminal response");return;}
 int available=n;while(available>0&&g_raw[available-1].time_msc>latest.time_msc)available--;n=available;
 int first=0;int status=g_cursor.ClassifyBatch(g_raw,n,first);
 if(status==0){g_ops.Disarm();g_caught_up=false;g_log.Event("HISTORY_INCOMPLETE",latest.time_msc,0,0,n,g_cursor.TailCount());return;}
 if(status<0){HG6Fault("quote overlap/order/grid integrity");return;}
 if(g_cursor.Ordinal()==0&&first<n){HG5Quote q0;if(!HG6Normalize(g_raw[first],q0)){HG6Fault("invalid first quote");return;}g_origin_verified=q0.ms==InpExpectedFirstQuoteMs&&q0.bid==InpExpectedFirstBidCents&&q0.ask==InpExpectedFirstAskCents;if(g_execute&&!g_origin_verified){HG6Fault("reference genesis mismatch; tester entries disabled");return;}}
 bool was_caught=g_caught_up;g_caught_up=false;int count=0,lo=first;
 for(;lo<n&&count<InpMaxGroupsPerPump;){
  int end=g_cursor.NextEnd(g_raw,n,lo);if(end<0){HG6Fault("timestamp group capacity/order");return;}if(end==0)break;
  if(!g_cursor.Group(g_raw,lo,end,g_group)||!g_core.StepGroup(g_group,g_stage,g_proposals,g_paths,g_accounts)||!g_cursor.Commit(g_raw,lo,end)){HG6Fault("frozen core or feed commit failure");return;}
  g_dirty=true;count++;lo=end;
  for(int j=0;j<ArraySize(g_proposals);j++)if(!g_log.Event("PROPOSAL",g_proposals[j].t,g_proposals[j].id,g_proposals[j].side,g_proposals[j].origin,g_cursor.Ordinal())){HG6Fault("telemetry failure");return;}
  // Send only a proposal from the final complete group of a live, caught-up batch.
  // Never replay a stale historical proposal. A close/busy epoch cannot admit a new one.
  bool fresh=was_caught&&n<HG6_TICK_BATCH&&g_raw[n-1].time_msc==latest.time_msc&&g_raw[lo].time_msc==latest.time_msc;
  // New holding decisions take priority over admission in the same pump.
  if(g_core.ActualReason()>0&&!close_requested)close_requested=HG6MaybeClose(x,latest,HG6Action(now,x,mapped,session),reconciled);
  g_seen_proposals+=ArraySize(g_proposals);
  bool budget=GetMicrosecondCount()-started<=(ulong)InpMaxServiceUs;
  if(!fresh||close_requested||!g_execute||!budget)g_suppressed_proposals+=ArraySize(g_proposals);
  else if(ArraySize(g_proposals)>1)g_suppressed_proposals+=ArraySize(g_proposals)-1;
  if(fresh&&!close_requested&&g_execute&&ArraySize(g_proposals)>0&&budget){
   if(ArraySize(g_proposals)>1)g_log.Event("MULTIPLE_PROPOSALS",g_proposals[0].t,g_proposals[0].id,ArraySize(g_proposals),0,0);
   long before=g_dispatched;if(HG6CheckReadiness(x,latest,now,mapped,reconciled,true,n-lo,started))HG6MaybeEntry(g_proposals[0],latest,x,mapped,session,reconciled,true);if(g_dispatched==before)g_gate_blocked++;
  }
  if(g_fatal)return;
  if(GetMicrosecondCount()-started>(ulong)InpMaxServiceUs)break;
 }
 g_caught_up=n>0&&n<HG6_TICK_BATCH&&lo<n&&g_raw[lo].time_msc==latest.time_msc&&g_raw[n-1].time_msc==latest.time_msc;
 g_last_service=GetMicrosecondCount()-started;
 if(!g_caught_up||g_trade_dirty)g_ops.Disarm();
 if(g_dirty&&GetMicrosecondCount()-g_saved_us>=(ulong)InpCheckpointSeconds*1000000&&!HG6Save()){HG6Fault("periodic checkpoint failure");return;}
 // No order API in OnTradeTransaction. Reconcile again next tick/timer.
 Comment("HybridGate V1 | ",g_execute?"STRATEGY TESTER CANDIDATE":"OBSERVATION ONLY","\nQuotes committed: ",g_cursor.Ordinal()," | lag: ",latest.time_msc-g_cursor.Last()," ms\nState: ",g_caught_up?"caught up":"catching up"," | demo/live locked","\nCopyTicks us: ",g_last_copy_us," | proposals observed: ",g_seen_proposals," | pre-gate suppressed: ",g_suppressed_proposals," | dispatched: ",g_dispatched," | gate blocked: ",g_gate_blocked);
}
// ============================================================================
// SECTION 07 — MetaTrader event entry points. All lifecycle transitions explicit.
// ============================================================================
int OnInit(){
 if(InpRequestDemoExecution&&HG6_EXECUTION_RELEASED==0){Print("HG6: execution release lock; compile and run QC first");return INIT_PARAMETERS_INCORRECT;}
 if(InpMagic==0||!HG6RunIdValid(InpRunId)||InpHistoryStart<=0||InpLadderCapUnits<1||InpLadderCapUnits>100||InpQuoteCapacity<32768||InpQuoteCapacity>262144||InpMaxGroupsPerPump<1||InpMaxGroupsPerPump>4096||InpTimerMilliseconds<50||InpTimerMilliseconds>5000||InpMaxQuoteAgeMs<1||InpMaxServiceUs<1000||InpCheckpointSeconds<1||InpDeviationPoints<0)return INIT_PARAMETERS_INCORRECT;
 if(StringFind(_Symbol,"XAUUSD")<0||!HG6BrokerSpec(_Symbol)){Print("HG6: incompatible XAUUSD/account grid/contract/currency");return INIT_FAILED;}
 g_tester=MQLInfoInteger(MQL_TESTER)!=0;g_execute=InpRequestTesterExecution&&g_tester&&HG6_TESTER_EXECUTION_ENABLED==1;
 if(InpRequestTesterExecution&&!g_execute)return INIT_PARAMETERS_INCORRECT;
 if(g_execute&&(!InpEmergencyCloseAuthorized||!InpClockMappingConfirmed||InpSourceUtcOffsetMinutes!=0||InpExpectedFirstQuoteMs<=0||InpExpectedFirstBidCents<=0||InpExpectedFirstAskCents<InpExpectedFirstBidCents))return INIT_PARAMETERS_INCORRECT;
 if(!HG6Windows(InpWeeklyClock,InpSourceUtcOffsetMinutes,g_windows)||!g_cursor.Init((long)InpHistoryStart*1000))return INIT_FAILED;
 uchar id[],lock_id[];string scope=AccountInfoString(ACCOUNT_SERVER)+"|"+IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN))+"|"+_Symbol+"|"+IntegerToString((long)InpMagic);
 if(!HG6TextDigest(scope,lock_id))return INIT_FAILED;g_scope="HybridGateV1_"+HG6Hex(lock_id)+"_"+InpRunId+(g_tester?"_TEST":"_OBS");
 // The common-directory lock prevents same-account/symbol/magic instances on this host.
 // It does not claim cross-machine mutual exclusion; broker ownership checks remain mandatory.
 if(!g_tester){g_lock=FileOpen("HybridGateV1_"+HG6Hex(lock_id)+".lock",FILE_READ|FILE_WRITE|FILE_BIN|FILE_COMMON);if(g_lock==INVALID_HANDLE){Print("HG6: instance lock unavailable");return INIT_FAILED;}}
 string config=scope+"|"+IntegerToString(InpExpectedFirstQuoteMs)+"|"+IntegerToString(InpExpectedFirstBidCents)+"|"+IntegerToString(InpExpectedFirstAskCents)+"|"+HG6_BUILD_ID+"|"+InpRunId+"|"+IntegerToString((long)InpHistoryStart)+"|"+IntegerToString(InpSourceUtcOffsetMinutes)+"|"+IntegerToString((int)InpClockMappingConfirmed)+"|"+IntegerToString((int)InpWeeklyClock)+"|"+IntegerToString((int)InpUseTradingClock)+"|"+IntegerToString((int)InpLotLadder)+"|"+IntegerToString(InpLadderCapUnits)+"|"+IntegerToString(InpQuoteCapacity)+"|"+IntegerToString((int)g_tester)+"|"+IntegerToString((int)g_execute)+"|"+IntegerToString(InpMaxGroupsPerPump)+"|"+IntegerToString(InpTimerMilliseconds)+"|"+IntegerToString(InpMaxQuoteAgeMs)+"|"+IntegerToString(InpMaxServiceUs)+"|"+IntegerToString(InpCheckpointSeconds)+"|"+IntegerToString(InpDeviationPoints)+"|"+IntegerToString((int)InpEmergencyCloseAuthorized);
 if(g_tester&&(FileIsExist(g_scope+"_state.genesis")||FileIsExist(g_scope+"_state.0.bin")||FileIsExist(g_scope+"_state.1.bin")||FileIsExist(g_scope+"_intent.genesis")||FileIsExist(g_scope+"_intent.0.bin")||FileIsExist(g_scope+"_intent.1.bin")))return INIT_FAILED;
 if(!HG6TextDigest(config,id)||!g_store.Init(g_scope+"_state",id)||!g_log.Open(g_scope+"_events"))return INIT_FAILED;
 // Reconcile actual account even before the model files load; no order can be sent.
 HG6Exposure x;if(!HG6ExposureRead(_Symbol,InpMagic,x))return INIT_FAILED;if(x.ticket||x.pending||x.foreign||x.ambiguous)Print("HG6 startup exposure requires reconciliation; no new orders");
 if(ArraySize(HG_ID)!=88||ArraySize(HG_MODEL_SHA)!=88)return INIT_FAILED;
 uchar bytes[];for(int i=0;i<88;i++){if(IsStopped()||!HG5ReadVerified("HG5QC\\"+HG_ID[i]+".hg5p",HG_MODEL_SHA[i],67108864,bytes)||!g_core.Load(i,bytes)){PrintFormat("HG6: model %d integrity/shape failure %s",i,HG_ID[i]);return INIT_FAILED;}ArrayFree(bytes);}
 if(!g_core.Start(g_windows,InpQuoteCapacity))return INIT_FAILED;
 int loaded=g_store.Load(bytes);if(g_tester&&loaded!=0){Print("HG6: tester run ID already used or corrupt; choose fresh run ID");return INIT_FAILED;}if(loaded<0||(loaded>0&&!HG6Restore(bytes))||!g_store.Healthy()){Print("HG6: checkpoint corrupt, ambiguous or incompatible; preserve files and reconcile manually");return INIT_FAILED;}
 ArrayFree(bytes);uchar intent_id[];string intent_scope=g_tester?g_scope:"HybridGateV1_"+HG6Hex(lock_id)+"_OBS_OWNERSHIP";if(!HG6TextDigest(intent_scope+"|HG6D_INTENT_V3",intent_id))return INIT_FAILED;
 if(g_tester&&(FileIsExist(intent_scope+"_intent.genesis")||FileIsExist(intent_scope+"_intent.0.bin")||FileIsExist(intent_scope+"_intent.1.bin")))return INIT_FAILED;
 if(!g_broker.Init(_Symbol,InpMagic,intent_scope+"_intent",intent_id,g_execute))return INIT_FAILED;
 HG5OpsLimits lim;lim.max_quote_age_ms=InpMaxQuoteAgeMs;lim.max_queue_us=InpMaxServiceUs;lim.max_service_us=InpMaxServiceUs;lim.max_trade_lag_ms=InpMaxQuoteAgeMs;lim.max_queue=HG6_TICK_BATCH;lim.max_active=1;lim.max_mailbox=1024;if(!g_ops.Init(lim))return INIT_FAILED;
 g_initialized=true;g_saved_us=GetMicrosecondCount();if(!EventSetMillisecondTimer(InpTimerMilliseconds)){g_initialized=false;return INIT_FAILED;}
 // Tester arming is evaluated afresh immediately before each proposed dispatch.
 // Demo/live remain hard disabled irrespective of input values.
 PrintFormat("HG6 initialized build=%s restored=%d ordinal=%I64d execution_lock=%d",HG6_BUILD_ID,loaded,g_cursor.Ordinal(),HG6_EXECUTION_RELEASED);return INIT_SUCCEEDED;
}
void OnTick(){HG6Pump();}
void OnTimer(){HG6Pump();}
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result){
 // All account transactions invalidate prior snapshot, irrespective of callback order.
 if(!g_trade_dirty||g_trade_first_us==0)g_trade_first_us=GetMicrosecondCount();g_trade_dirty=true;if(g_mailbox<1025)g_mailbox++;if(g_mailbox>1024)g_ops.Disarm();
}
void OnDeinit(const int reason){EventKillTimer();if(g_initialized&&g_dirty&&!g_fatal&&!HG6Save())Print("HG6: final checkpoint failed; preserve prior generation");if(g_initialized){MqlTick t;if(SymbolInfoTick(_Symbol,t)&&t.time_msc>g_cursor.Last())PrintFormat("HG6 end: uncommitted tail/latest=%I64d cursor=%I64d; no invented future quote",t.time_msc,g_cursor.Last());PrintFormat("HG6 totals proposals=%I64d suppressed=%I64d gate_blocked=%I64d acknowledged_sends=%I64d closed=%I64d actual_net=%.8f outstanding=%d",g_seen_proposals,g_suppressed_proposals,g_gate_blocked,g_dispatched,g_broker.ClosedPositions(),g_broker.ActualNet(),(int)g_broker.Outstanding());}g_log.Close();if(g_lock!=INVALID_HANDLE)FileClose(g_lock);Comment("");PrintFormat("HG6 deinit reason=%d ordinal=%I64d; no implied liquidation",reason,g_cursor.Ordinal());}
