// Fresh-process transaction test. External broker evidence is a deterministic mock,
// not a persisted terminal or real broker; the actual MQL-oriented stores and broker
// controller execute through the compatibility shim. Every phase is a separate PID.
#include "host_compat.hpp"
#include "HG6Broker.mqh"
static bool save_applied(HG6Store &store,long seq){std::vector<uchar> b(8);HG6Put64(b,0,seq);return store.Save(b);}
int main(int argc,char **argv){
 assert(argc==2);string phase=argv[1];mock_tester=true;mock_clock=1;MqlTick t;t.time=1;t.time_msc=1000;t.bid=2000;t.ask=2000.01;t.flags=6;mock_ticks={t};mock_visible=1;
 std::vector<uchar> id,core_id,b;assert(HG6TextDigest("journal-broker",id)&&HG6TextDigest("journal-core",core_id));HG6Store core;assert(core.Init("core",core_id));int loaded=core.Load(b);
 if(phase=="corrupt"){
  // A missing generation 2 can resemble an initial one-slot generation 1.
  // The independent durable broker watermark is the decisive rollback check.
  if(loaded>=0&&core.Healthy()){HG6Broker joint;assert(loaded==1&&joint.Init(_Symbol,19,"intent",id,true)&&!joint.CheckLink(HG6Get64(b,0),core.Generation()));}
  std::cout<<"PASS damaged or rolled-back core rejected by joint contract\n";return 0;
 }
 assert(loaded>=0&&core.Healthy());long applied=loaded?HG6Get64(b,0):0;HG6Broker broker;assert(broker.Init(_Symbol,19,"intent",id,true));HG6Exposure x;
 if(phase=="genesis"){assert(loaded==0&&broker.CheckLink(0,0)&&save_applied(core,0));}
 else if(phase=="unknown"){assert(loaded==1&&broker.CheckLink(0,1)&&HG6ExposureRead(_Symbol,19,x));mock_send_mode=2;assert(!broker.Submit(1,17,1,1,t,x,10)&&broker.Outstanding()&&send_count==1);}
 else {
  // Exact deterministic broker-side result from the UNKNOWN phase. Never call
  // OrderSend in recovery phases. Reconstruct the external mocked order/deal evidence.
  mo.push_back({101,19,103,1000,ORDER_TYPE_BUY,ORDER_STATE_FILLED,_Symbol,"HG6-1",false});
  md.push_back({102,101,19,103,1000,DEAL_ENTRY_IN,DEAL_TYPE_BUY,.01,2000.01,0,-.01,0,0,_Symbol});
  mock_pt=103;mock_magic=19;mock_ptime=1000;mock_side=POSITION_TYPE_BUY;mock_volume=.01;mock_price=2000.01;assert(HG6ExposureRead(_Symbol,19,x));
  if(phase=="resolved"){assert(applied==0&&broker.CheckLink(0,1)&&!broker.Ready()&&broker.Reconcile(x)&&broker.Resolved()&&broker.Filled());assert(!broker.ReleaseApplied(0,1));}
  else if(phase=="applied"){assert(applied==0&&broker.Resolved()&&broker.CheckLink(0,1)&&broker.Reconcile(x)&&save_applied(core,1));}
  else if(phase=="release"){assert(applied==1&&broker.CheckLink(1,2)&&broker.Resolved()&&broker.Reconcile(x)&&broker.ReleaseApplied(1,2));}
  else if(phase=="verified"){assert(applied==1&&broker.Ready()&&broker.CheckLink(1,2)&&!broker.CheckLink(0,1)&&!broker.CheckLink(1,1)&&std::abs(broker.ActualNet()+.01)<1e-10);}
  else if(phase=="rescue"){assert(applied==1&&broker.Ready()&&broker.EnterRescue()&&!broker.CheckLink(1,2));}
  else if(phase=="quarantine"){assert(broker.RescueMode()&&!broker.CheckLink(1,2));}
  else return 2;
  assert(send_count==0);
 }
 std::cout<<"PASS "<<phase<<" sequence="<<broker.Sequence()<<" generation="<<core.Generation()<<" sends="<<send_count<<"\n";return 0;
}
