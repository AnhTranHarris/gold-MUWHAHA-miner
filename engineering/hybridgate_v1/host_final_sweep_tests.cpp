// Final source-derived adapter adversarial checks. All sends are mock-only.
#include "HG5CoreFixtureManifest.mqh"
static void ExternalExit(double volume){assert(mock_pt&&volume>0&&volume<=mock_volume);auto t=mock_ticks.at(mock_visible-1);auto side=mock_side==POSITION_TYPE_BUY?DEAL_TYPE_SELL:DEAL_TYPE_BUY;double px=side==DEAL_TYPE_SELL?t.bid:t.ask;double pnl=(px-mock_price)*(mock_side==POSITION_TYPE_BUY?1:-1)*volume*100;md.push_back({++mock_next,++mock_next,0,mock_pt,t.time_msc,DEAL_ENTRY_OUT,side,volume,px,pnl,-.01,0,0,_Symbol});mock_volume-=volume;if(mock_volume<1e-9){mock_volume=0;mock_pt=0;}}
static double Net(){double r=0;for(const auto &d:md)r+=d.profit+d.commission+d.swap+d.fee;return r;}
int main(int argc,char **argv){
 assert(argc==2);string mode=argv[1];mock_tester=true;mock_clock=1767315600;MqlTick t;t.time=mock_clock;t.time_msc=mock_clock*1000;t.bid=4324.37;t.ask=4327.44;t.flags=6;mock_ticks={t};mock_visible=1;
 if(mode=="fok"){
  mock_fill_flags=0;mock_execution=SYMBOL_TRADE_EXECUTION_MARKET;assert(!HG6FokAllowed(_Symbol));mock_execution=SYMBOL_TRADE_EXECUTION_EXCHANGE;assert(!HG6FokAllowed(_Symbol));mock_execution=SYMBOL_TRADE_EXECUTION_REQUEST;assert(HG6FokAllowed(_Symbol));mock_execution=SYMBOL_TRADE_EXECUTION_INSTANT;assert(HG6FokAllowed(_Symbol));mock_execution=SYMBOL_TRADE_EXECUTION_MARKET;mock_fill_flags=SYMBOL_FILLING_FOK;assert(HG6FokAllowed(_Symbol));std::cout<<"PASS exact FOK capability matrix\n";return 0;
 }
 if(mode=="full_ea_entry"||mode=="full_ea_reject"){
  std::vector<uchar> data;assert(HG5ReadVerified("HG5QC\\HG5CoreFixture.bin",HG5_CORE_FIXTURE_SHA,16777216,data));auto I=[&](int p){uint z=0;for(int k=0;k<4;k++)z|=(uint)data.at(p+k)<<(8*k);return (int)z;};mock_ticks.clear();
  for(int i=0;i<16000;i++){int p=36+16*i;MqlTick q;q.time_msc=HG6Get64(data,p);q.time=q.time_msc/1000;q.bid=I(p+8)/100.;q.ask=I(p+12)/100.;q.flags=6;mock_ticks.push_back(q);}
  InpRequestTesterExecution=true;InpEmergencyCloseAuthorized=true;InpClockMappingConfirmed=true;InpRunId="FINALSWE";mock_clock=mock_ticks.front().time;assert(OnInit()==INIT_SUCCEEDED);OnTick();bool injected=false;long closed_before=0;int sends_after=0;
  for(int i=2;i<=16000;i++){mock_visible=i;mock_clock=mock_ticks[i-1].time;OnTick();assert(!g_fatal);if(!injected&&mock_pt&&g_broker.Outstanding()&&g_broker.IntentKind()==1){
    ulong pos=mock_pt;if(mode=="full_ea_reject"){HG6Exposure x;assert(HG6Reconcile(x)&&g_core.ActualId()==(long)pos);mock_send_mode=4;assert(!g_broker.Submit(2,(long)pos,-x.side,x.units,mock_ticks[i-1],x,10));mock_send_mode=0;}
    closed_before=g_broker.ClosedPositions();ExternalExit(mock_volume);sends_after=send_count;mock_quote_available=false;OnTimer();mock_quote_available=true;
    assert(!g_fatal&&!g_broker.Outstanding()&&g_broker.Ready()&&g_core.ActualState()==0&&g_broker.ClosedPositions()==closed_before+1&&g_external_applied==(long)pos&&send_count==sends_after&&std::abs(g_broker.ActualNet()-Net())<1e-8);injected=true;
  }}
  assert(injected&&!g_fatal&&!mock_pt&&!g_broker.Outstanding()&&g_broker.ClosedPositions()>closed_before+1&&send_count>sends_after&&std::abs(g_broker.ActualNet()-Net())<1e-8);std::cout<<"PASS "<<mode<<" full EA recovery and subsequent trades closed="<<g_broker.ClosedPositions()<<" sends="<<send_count<<" net_exact\n";OnDeinit(0);return 0;
 }
 std::vector<uchar> id;assert(HG6TextDigest(mode,id));auto b=std::make_unique<HG6Broker>();assert(b->Init(_Symbol,17,"intent",id,true));HG6Exposure x;assert(HG6ExposureRead(_Symbol,17,x));
 auto recover=[&](){b=std::make_unique<HG6Broker>();assert(b->Init(_Symbol,17,"intent",id,true));};
 if(mode=="offline"){mock_connected=false;assert(b->Submit(1,1,1,1,t,x,10)&&send_count==1);assert(HG6ExposureRead(_Symbol,17,x)&&b->Reconcile(x)&&b->ReleaseApplied(1,1));assert(b->Submit(2,1,-1,1,t,x,10)&&send_count==2);assert(HG6ExposureRead(_Symbol,17,x)&&!x.ticket&&b->Reconcile(x)&&b->ReleaseApplied(2,2));mock_tester=false;assert(!b->Submit(1,2,1,1,t,x,10)&&send_count==2);std::cout<<"PASS simulated offline connection flag no longer blocks tester; non-tester still blocked\n";return 0;}
 assert(b->Submit(1,1,1,2,t,x,10));long pos=mock_pt;assert(pos>0);
 if(mode=="entry_flat"||mode=="entry_resolved_flat"||mode=="entry_incomplete"||mode=="entry_conflict"){
  if(mode=="entry_resolved_flat"){assert(HG6ExposureRead(_Symbol,17,x)&&b->Reconcile(x)&&b->Filled());recover();}
  ExternalExit(.02);assert(HG6ExposureRead(_Symbol,17,x)&&!x.ticket);if(mode=="entry_incomplete"){auto d=md.back();md.pop_back();assert(!b->Reconcile(x)&&b->Outstanding());md.push_back(d);}
  if(mode=="entry_conflict"){md.front().magic=999;assert(!b->Reconcile(x)&&b->Outstanding()&&send_count==1);std::cout<<"PASS foreign entry evidence rejected\n";return 0;}
  assert(b->Reconcile(x)&&b->IntentAlreadyFlat()&&b->PositionId()==pos&&b->FilledUnits()==2&&b->ClosedPositions()==1&&std::abs(b->ActualNet()-Net())<1e-8);long j=b->JournalLast();recover();assert(b->Reconcile(x)&&b->JournalLast()==j&&b->IntentAlreadyFlat()&&b->ReleaseApplied(1,1)&&b->Ready()&&send_count==1);std::cout<<"PASS "<<mode<<" full history verified, journal replay idempotent\n";return 0;
 }
 assert(HG6ExposureRead(_Symbol,17,x)&&b->Reconcile(x)&&b->ReleaseApplied(1,1));
 if(mode=="close_reject_flat"){
  mock_send_mode=4;assert(!b->Submit(2,1,-1,2,t,x,10));ExternalExit(.02);assert(HG6ExposureRead(_Symbol,17,x)&&!x.ticket);mock_history=false;assert(!b->Reconcile(x));mock_history=true;recover();assert(b->Reconcile(x)&&b->Resolved()&&!b->Filled()&&b->ReleaseApplied(2,2));assert(b->ExternalFlat(pos)&&b->ExternalPending()==pos&&b->ReleaseExternal(pos,2,3)&&b->Ready()&&send_count==2&&std::abs(b->ActualNet()-Net())<1e-8);std::cout<<"PASS rejected close then external flat exact ledger and link\n";return 0;
 }
 if(mode=="partial_close_flat"){
  mock_send_mode=3;assert(b->Submit(2,1,-1,2,t,x,10));assert(HG6ExposureRead(_Symbol,17,x)&&x.pending&&!b->Reconcile(x)&&b->FilledUnits()==1);assert(b->CancelPending(x));ExternalExit(.01);assert(HG6ExposureRead(_Symbol,17,x)&&!x.ticket&&!x.pending);assert(b->Reconcile(x)&&b->IntentAlreadyFlat()&&b->FilledUnits()==1&&b->ReleaseApplied(2,2)&&b->Ready()&&b->ClosedPositions()==1&&std::abs(b->ActualNet()-Net())<1e-8);std::cout<<"PASS partial close then external residual flat\n";return 0;
 }
 if(mode=="prior_external_partial"){
  ExternalExit(.01);assert(HG6ExposureRead(_Symbol,17,x)&&x.units==1);assert(b->Submit(2,1,-1,1,t,x,10));assert(HG6ExposureRead(_Symbol,17,x)&&!x.ticket&&b->Reconcile(x)&&b->IntentAlreadyFlat()&&b->ReleaseApplied(2,2)&&b->ClosedPositions()==1&&std::abs(b->ActualNet()-Net())<1e-8);std::cout<<"PASS prior external partial cost included at definitive flat\n";return 0;
 }
 return 2;
}
