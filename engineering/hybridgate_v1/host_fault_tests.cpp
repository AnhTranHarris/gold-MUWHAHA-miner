// Stage 6D4. Actual EA methods and frozen fixture; no MT5 or external broker.
#include "HG5CoreFixtureManifest.mqh"
int main(int argc,char **argv){
 bool partial=argc==2&&string(argv[1])=="partial";bool external=argc==2&&string(argv[1])=="external";
 std::vector<uchar> data;assert(HG5ReadVerified("HG5QC\\HG5CoreFixture.bin",HG5_CORE_FIXTURE_SHA,16777216,data));
 int n=16000;for(int i=0;i<n;i++){int p=36+16*i;MqlTick t;t.time_msc=HG6Get64(data,p);t.time=t.time_msc/1000;int bi=0,ai=0;for(int k=0;k<4;k++){bi|=(int)((uint)data[p+8+k]<<(8*k));ai|=(int)((uint)data[p+12+k]<<(8*k));}t.bid=bi/100.;t.ask=ai/100.;t.flags=6;mock_ticks.push_back(t);}
 mock_tester=true;InpRequestTesterExecution=true;InpClockMappingConfirmed=true;InpEmergencyCloseAuthorized=true;InpRunId="HOSTFAULT";InpQuoteCapacity=32768;InpMaxGroupsPerPump=4096;InpMaxServiceUs=10000000;InpCheckpointSeconds=100000;
 if(partial){mock_balance=5000.;InpLotLadder=true;mock_send_mode=3;}
 mock_visible=1024;mock_clock=mock_ticks[mock_visible-1].time;assert(OnInit()==INIT_SUCCEEDED);OnTick();assert(g_caught_up&&!g_fatal&&send_count==0);
 // Wait for the first normal owned, reconciled position, then simulate absent quotes
 // and a server clock at the source's exact flatten boundary.
 for(int i=1025;i<=n;i++){mock_visible=i;mock_clock=mock_ticks[i-1].time;OnTick();assert(!g_fatal);if(mock_pt&&(partial?g_broker.Outstanding():!g_broker.Outstanding()&&g_broker.ActiveLedgerPosition()==(long)mock_pt))break;}
 if(partial){
  assert(mock_pt&&g_broker.Outstanding()&&mock_volume==.01&&OrdersTotal()==1);int before=send_count;long age_deadline=mock_ptime+30000;
  mock_quote_available=false;mock_clock=(age_deadline+999)/1000;OnTimer();assert(g_overdue&&mock_pt&&OrdersTotal()==0&&send_count==before+1); // cancellation is quote-independent
  OnTimer();assert(g_overdue&&mock_pt&&!g_broker.Outstanding()&&g_broker.ActiveLedgerPosition()==(long)mock_pt);
  MqlTick resumed=mock_ticks[mock_visible-1];resumed.time_msc=mock_clock*1000+1000;resumed.time=resumed.time_msc/1000;mock_ticks.resize(mock_visible);mock_ticks.push_back(resumed);mock_visible++;mock_clock=resumed.time;mock_quote_available=true;mock_send_mode=0;
  OnTimer();assert(!mock_pt&&send_count==before+2);mock_quote_available=false;OnTimer();assert(!g_fatal&&!g_overdue&&!g_broker.Outstanding()&&g_core.ActualState()==0&&g_broker.ClosedPositions()==1);
  OnDeinit(0);Print("HG6D4 PARTIAL ENTRY: no-quote hold deadline cancels remainder, reconciles fill and closes residual at fresh quote PASS");return 0;
 }
 assert(mock_pt&&g_broker.ActiveLedgerPosition()==(long)mock_pt);ulong pos=mock_pt;int before=send_count;
 if(external){long prior_gen=g_store.Generation(),applied=g_applied_seq,prior_closed=g_broker.ClosedPositions();md.push_back({++mock_next,++mock_next,0,pos,mock_ticks[mock_visible-1].time_msc,DEAL_ENTRY_OUT,mock_side==POSITION_TYPE_BUY?DEAL_TYPE_SELL:DEAL_TYPE_BUY,mock_volume,mock_ticks[mock_visible-1].bid,-.02,-.01,0,0,_Symbol});mock_pt=0;mock_volume=0;mock_quote_available=false;OnTimer();std::cerr<<"external fatal="<<g_fatal<<" actual="<<g_core.ActualState()<<" pending="<<g_broker.ExternalPending()<<" applied="<<g_external_applied<<" pos="<<pos<<" closed="<<g_broker.ClosedPositions()<<" generation="<<g_store.Generation()<<" prior="<<prior_gen<<" seq="<<applied<<" sends="<<send_count<<" before="<<before<<" healthy="<<g_broker.IntegrityHealthy()<<"\n";assert(!g_fatal&&g_core.ActualState()==0&&g_broker.ExternalPending()==0&&g_external_applied==(long)pos&&g_broker.ClosedPositions()==prior_closed+1&&g_broker.CheckLink(applied,g_store.Generation())&&!g_broker.CheckLink(applied,prior_gen)&&send_count==before);OnDeinit(0);Print("PASS full EA external liquidation, no quote, linked checkpoint and no extra send");return 0;}
 int wi=HG5WindowIndex(mock_ticks[mock_visible-1].time_msc,g_windows,(int)g_windows.size());assert(wi>=0);long flat_ms=g_windows[wi].flatten_ms;
 mock_quote_available=false;mock_clock=flat_ms/1000;mock_session_open=false;OnTimer();assert(g_overdue&&!g_fatal&&mock_pt==pos&&send_count==before&&!g_ops.EntriesAllowed());
 // Stale last quote is not a valid close execution price even if retrieval resumes.
 mock_quote_available=true;OnTimer();assert(g_overdue&&mock_pt==pos&&send_count==before);
 // A current quote returns after market reopen; close at observed price. No invented fill.
 MqlTick resumed=mock_ticks[mock_visible-1];resumed.time_msc=flat_ms+1000;resumed.time=resumed.time_msc/1000;mock_ticks.resize(mock_visible);mock_ticks.push_back(resumed);mock_visible++;mock_clock=resumed.time;mock_session_open=true;
 OnTimer();assert(!mock_pt&&send_count==before+1);
 // Confirmation must clear actual state without a quote and preserve the cooldown.
 mock_quote_available=false;OnTimer();assert(!g_fatal&&!g_overdue&&g_core.ActualState()==0&&!g_broker.Outstanding()&&g_last_flat_ms==resumed.time_msc);
 long lastflat=g_last_flat_ms;assert(lastflat>=flat_ms);
 // The fatal latch must persist even when already flat; no sends on subsequent timers.
 HG6Fault("flat-state injected integrity failure");assert(g_broker.RescueMode()&&!g_broker.CheckLink(g_applied_seq,g_store.Generation()));OnTimer();assert(send_count==before+1);
 OnDeinit(0);Print("HG6D4 FULL EA: no-quote clock flatten, stale quote, closed session, fresh close, no-quote flat confirmation, durable flat quarantine PASS");return 0;
}
