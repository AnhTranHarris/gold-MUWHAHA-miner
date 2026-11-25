// Compare actual mock execution on every quote with the sealed Stage 5 reference.
#include "HG5CoreFixtureManifest.mqh"
int main(int argc,char **argv){
 bool burst=argc==2&&string(argv[1])=="burst";
 std::vector<uchar> data;assert(HG5ReadVerified("HG5QC\\HG5CoreFixture.bin",HG5_CORE_FIXTURE_SHA,16777216,data));
 auto I=[&](int p){uint z=0;for(int k=0;k<4;k++)z|=(uint)data.at(p+k)<<(8*k);return (int)z;};
 int n=16000,nfull=I(8),nw=I(12),ns=I(16),np=I(20),nh=I(24),na=I(28);int pp=36+16*nfull+32*nw+44*ns,hp=pp+32*np,ap=hp+52*nh;
 std::map<long,long> entry,exit,proposal;std::map<long,int> side;std::map<long,long> decision;std::map<long,int> mark;
 for(int i=0;i<np;i++){int p=pp+32*i;long id=HG6Get64(data,p);proposal[id]=HG6Get64(data,p+8);side[id]=(int)HG6Get64(data,p+16);}
 for(int i=0;i<nh;i++){int p=hp+40*i;long id=HG6Get64(data,p),ordinal=HG6Get64(data,p+8),kind=HG6Get64(data,p+16);if(kind==0)entry[id]=ordinal;else if(kind==1)decision[id]=ordinal;else if(kind==2){exit[id]=ordinal;mark[id]=(int)HG6Get64(data,p+32);}}
 std::vector<long> expected;for(int i=0;i<na;i++){int p=ap+32*i;if(HG6Get64(data,p+16)==1&&HG6Get64(data,p+24)==1&&HG6Get64(data,p+8)<n-1)expected.push_back(HG6Get64(data,p));}
 for(int i=0;i<n;i++){int p=36+16*i;MqlTick t;t.time_msc=HG6Get64(data,p);t.time=t.time_msc/1000;t.bid=I(p+8)/100.;t.ask=I(p+12)/100.;t.flags=6;mock_ticks.push_back(t);}
 mock_tester=true;InpRequestTesterExecution=true;InpClockMappingConfirmed=true;InpEmergencyCloseAuthorized=true;InpRunId=burst?"HOSTBURST":"HOSTDISPATCH";InpQuoteCapacity=32768;InpMaxGroupsPerPump=4096;InpMaxServiceUs=10000000;InpCheckpointSeconds=100000;
 mock_visible=1024;mock_clock=mock_ticks[mock_visible-1].time;assert(OnInit()==INIT_SUCCEEDED);OnTick();assert(g_caught_up&&!g_fatal&&send_count==0);
 std::vector<long> ids;int eq_entry=0,eq_exit=0,eq_net=0;long max_lag=0;std::map<long,long> pos_to_id;std::map<long,double> net;
 for(int i=1025;i<=n;){mock_visible=i;mock_clock=mock_ticks[i-1].time;int before=send_count;OnTick();assert(!g_fatal);if(send_count>before){assert(send_count==before+1&&g_broker.Outstanding());const auto &d=md.back();if(d.entry==DEAL_ENTRY_IN){long id=g_broker.Proposal();assert(entry.count(id)&&side[id]==(d.type==DEAL_TYPE_BUY?1:-1));ids.push_back(id);pos_to_id[d.pos]=id;long ref=entry[id];auto q=mock_ticks.at(ref);eq_entry+=(ref==i-1&&d.ms==q.time_msc&&d.price==(side[id]>0?q.ask:q.bid));long lag=d.ms-proposal[id];assert(lag>0&&lag<=InpMaxQuoteAgeMs);int prior=i-2;while(prior>=0&&mock_ticks[prior].time_msc==d.ms)prior--;assert(prior>=0&&mock_ticks[prior].time_msc==proposal[id]);max_lag=std::max(max_lag,lag);}else {long id=pos_to_id.at(d.pos);assert(exit.count(id));long ref=exit[id];auto q=mock_ticks.at(ref);eq_exit+=(ref==i-1&&d.ms==q.time_msc&&d.price==(side[id]>0?q.bid:q.ask));}net[pos_to_id.at(d.pos)]+=d.profit+d.commission+d.swap+d.fee;}if(i==n)break;i=std::min(n,i+(burst?(i%3==0?257:i%3==1?17:3):1));}
 for(long id:ids)if(exit.count(id)&&std::abs(net[id]-mark[id]/100.)<1e-8)eq_net++;
 std::cout<<"DISPATCH expected="<<expected.size()<<" actual="<<ids.size()<<" matched_entry="<<eq_entry<<" matched_exit="<<eq_exit<<" matched_net="<<eq_net<<" max_decision_to_entry_ms="<<max_lag<<" suppressed="<<g_suppressed_proposals<<" blocked="<<g_gate_blocked<<" closed="<<g_broker.ClosedPositions()<<"\n";
 for(long id:expected)if(std::find(ids.begin(),ids.end(),id)==ids.end())std::cout<<"MISSING_REFERENCE "<<id<<"\n";
 for(long id:ids)if(std::find(expected.begin(),expected.end(),id)==expected.end())std::cout<<"EXTRA_ACTUAL "<<id<<"\n";
 if(burst){for(int i=0;i<100&&(!g_caught_up);i++)OnTimer();std::vector<long> stats;assert(g_core.Stats(stats)&&stats[0]==g_cursor.Ordinal()&&!g_fatal);int final_group=n-1;while(final_group>0&&mock_ticks[final_group-1].time_msc==mock_ticks.back().time_msc)final_group--;assert(g_cursor.Ordinal()==final_group);long seen=0;for(auto &x:proposal)if(x.second<=g_cursor.Last())seen++;assert(g_seen_proposals==seen);assert(g_suppressed_proposals+g_gate_blocked+g_dispatched==g_seen_proposals);assert(g_suppressed_proposals>0);std::cout<<"BURST source proposals="<<seen<<" committed="<<g_cursor.Ordinal()<<" retired="<<stats[1]<<" peak="<<stats[2]<<" pump_max_us="<<g_pump_max_us<<"\n";OnDeinit(0);return 0;}
 assert(g_broker.ClosedPositions()==(long)ids.size()&&!g_broker.Outstanding()&&!mock_pt);OnDeinit(0);
 // Different broker policy or timing is not silently accepted. Record the divergence.
 return ids==expected&&eq_entry==(int)ids.size()&&eq_exit==(int)ids.size()&&eq_net==(int)ids.size()?0:2;
}
