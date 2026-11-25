// Actual EA and broker through host shim. No terminal or real orders.
int main(int argc,char **argv){
 assert(argc==2);string mode=argv[1];mock_tester=true;mock_clock=1767315600;MqlTick t;t.time=mock_clock;t.time_msc=mock_clock*1000;t.bid=4324.37;t.ask=4327.44;t.flags=6;mock_ticks={t};mock_visible=1;
 std::vector<uchar> id,scope_id;InpRequestTesterExecution=true;InpEmergencyCloseAuthorized=true;InpClockMappingConfirmed=true;InpRunId="RESCUE";string scope=AccountInfoString(ACCOUNT_SERVER)+"|"+IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN))+"|"+_Symbol+"|"+IntegerToString((long)InpMagic);assert(HG6TextDigest(scope,scope_id));string stem="HybridGateV1_"+HG6Hex(scope_id)+"_"+InpRunId+"_TEST_intent";assert(HG6TextDigest(stem.substr(0,stem.size()-7)+"|HG6D_INTENT_V6",id));
 HG6Exposure x;assert(HG6ExposureRead(_Symbol,InpMagic,x));
 if(mode=="noledger"){InpTesterRescueExisting=true;assert(OnInit()==INIT_FAILED&&send_count==0);return 0;}
 if(mode=="foreign"){mock_pt=501;mock_magic=999;mock_ptime=t.time_msc;mock_volume=.01;mock_price=t.ask;assert(OnInit()==INIT_FAILED&&send_count==0);return 0;}
 HG6Broker seed;assert(seed.Init(_Symbol,InpMagic,stem,id,true));
 if(mode=="retry"||mode=="timeout"||mode=="exhaust"){
  mock_send_mode=3;assert(seed.Submit(1,1,1,2,t,x,10));assert(HG6ExposureRead(_Symbol,InpMagic,x)&&x.pending&&!seed.Reconcile(x));mock_cancel_mode=mode=="timeout"?2:1;
  assert(!seed.CancelPending(x)&&send_count==2);assert(!seed.CancelPending(x)&&send_count==2);mock_clock++;
  HG6Broker recovered;assert(recovered.Init(_Symbol,InpMagic,stem,id,true));
  if(mode=="timeout"){mock_cancel_mode=0;assert(!recovered.CancelPending(x)&&send_count==2&&x.pending);}
  else if(mode=="retry"){mock_history=false;assert(!recovered.CancelPending(x)&&send_count==2);mock_history=true;mock_cancel_mode=0;assert(recovered.CancelPending(x)&&send_count==3);assert(HG6ExposureRead(_Symbol,InpMagic,x)&&!x.pending&&recovered.Reconcile(x)&&recovered.FilledUnits()==1&&recovered.ReleaseApplied(1,1));mock_send_mode=0;assert(recovered.Submit(2,1,-1,1,t,x,10));assert(HG6ExposureRead(_Symbol,InpMagic,x)&&!x.ticket&&recovered.Reconcile(x)&&recovered.ReleaseApplied(2,2));}
  else{assert(!recovered.CancelPending(x)&&send_count==3);mock_clock++;assert(!recovered.CancelPending(x)&&send_count==4);mock_clock++;mock_cancel_mode=0;assert(!recovered.CancelPending(x)&&send_count==4);}
  std::cout<<"PASS cancellation "<<mode<<" sends="<<send_count<<"\n";return 0;
 }
 // Seed owned exposure and durable ledger, without model files or core checkpoints.
 assert(seed.Submit(1,1,1,1,t,x,10));assert(HG6ExposureRead(_Symbol,InpMagic,x)&&seed.Reconcile(x)&&seed.ReleaseApplied(1,1));assert(mock_pt&&send_count==1);
 if(mode=="wrongowner"){mock_magic=999;InpTesterRescueExisting=true;assert(OnInit()==INIT_FAILED&&send_count==1&&mock_pt);return 0;}
 if(mode=="ordinary"){assert(OnInit()==INIT_FAILED&&send_count==1&&mock_pt);return 0;}
 assert(mode=="rescue");InpTesterRescueExisting=true;assert(!std::filesystem::exists("HG5QC"));assert(OnInit()==INIT_SUCCEEDED&&g_initialized&&g_fatal&&g_broker.RescueMode());
 mock_quote_available=false;OnTimer();assert(mock_pt&&send_count==1);mock_quote_available=true;OnTimer();assert(!mock_pt&&send_count==2);OnTimer();assert(!g_broker.Outstanding()&&g_broker.ClosedPositions()==1);OnTimer();assert(send_count==2);OnDeinit(0);std::cout<<"PASS explicit independent startup rescue; no models/core, no entry\n";
}
