// Full EA event-loop reachability. All orders are in-memory mock receipts.
#include "HG5CoreFixtureManifest.mqh"
int main(){
 std::vector<uchar> data;assert(HG5ReadVerified("HG5QC\\HG5CoreFixture.bin",HG5_CORE_FIXTURE_SHA,16777216,data));
 int n=16000;for(int i=0;i<n;i++){int p=36+16*i;MqlTick t;t.time_msc=HG6Get64(data,p);t.time=t.time_msc/1000;int bi=0,ai=0;for(int k=0;k<4;k++){bi|=(int)((uint)data[p+8+k]<<(8*k));ai|=(int)((uint)data[p+12+k]<<(8*k));}t.bid=bi/100.;t.ask=ai/100.;t.flags=6;mock_ticks.push_back(t);}
 mock_tester=true;InpRequestTesterExecution=true;InpClockMappingConfirmed=true;InpEmergencyCloseAuthorized=true;InpRunId="HOSTTESTER";InpQuoteCapacity=32768;InpMaxGroupsPerPump=4096;InpMaxServiceUs=10000000;InpCheckpointSeconds=100000;
 mock_visible=1024;mock_clock=mock_ticks[mock_visible-1].time;assert(OnInit()==INIT_SUCCEEDED);OnTick();assert(g_caught_up&&!g_fatal&&send_count==0);
 for(int i=1025;i<=n;i++){mock_visible=i;mock_clock=mock_ticks[i-1].time;OnTick();assert(!g_fatal);if(g_broker.ClosedPositions()>=3&&!g_broker.Outstanding()&&!mock_pt)break;}
 std::cerr<<"tester proposals="<<g_seen_proposals<<" suppressed="<<g_suppressed_proposals<<" gate_blocked="<<g_gate_blocked<<" sends="<<send_count<<" closed="<<g_broker.ClosedPositions()<<" active="<<mock_pt<<" ordinal="<<g_cursor.Ordinal()<<" actual_state="<<g_core.ActualState()<<"\n";
 assert(g_origin_verified&&g_dispatched>0&&g_broker.ClosedPositions()>=3&&send_count>=6&&!mock_pt&&!g_broker.Outstanding());g_overdue=true;HG6Exposure flat;assert(HG6Reconcile(flat)&&!g_overdue);double net=0;for(auto&d:md)net+=d.profit+d.commission+d.swap+d.fee;assert(std::abs(net-g_broker.ActualNet())<1e-9);
 // Prove fatal-model independent rescue of a known, already reconciled position.
 for(int i=mock_visible+1;i<=n;i++){mock_visible=i;mock_clock=mock_ticks[i-1].time;OnTick();assert(!g_fatal);if(mock_pt&&!g_broker.Outstanding()&&g_broker.ActiveLedgerPosition()==(long)mock_pt)break;}
 assert(mock_pt&&g_broker.ActiveLedgerPosition()==(long)mock_pt);long closed=g_broker.ClosedPositions();int prior=send_count;HG6Fault("host injected model failure");OnTimer();assert(send_count==prior+1&&!mock_pt);OnTimer();assert(g_broker.ClosedPositions()==closed+1&&!g_broker.Outstanding());OnTimer();assert(send_count==prior+1);
 assert(g_broker.RescueMode()&&!g_broker.CheckLink(g_applied_seq,g_store.Generation()));std::cerr<<"PERF saves="<<g_save_count<<" total_us="<<g_save_total_us<<" max_us="<<g_save_max_us<<" max_bytes="<<g_save_max_bytes<<" pump_max_us="<<g_pump_max_us<<" copy_max_us="<<g_copy_max_us<<"\n";OnDeinit(0);Print("HG6D FULL TESTER MOCK: normal entry/holding/exit, financial reconciliation, fatal-state rescue and no post-quarantine entry PASS");return 0;
}
