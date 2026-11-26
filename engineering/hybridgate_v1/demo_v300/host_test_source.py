from pathlib import Path
import re,subprocess,os
h=Path('/tmp/hg10');old=Path('/tmp/hg9host');inc=old/'include';src=(old/'test_host.py').read_text();exec(src[src.index('types=r'):src.index('for src in')]);
shim=(old/'host_compat.hpp').read_text();shim=shim.replace('assert(mock_tester);','assert(mock_tester||AccountInfoInteger(ACCOUNT_TRADE_MODE)==ACCOUNT_TRADE_MODE_DEMO);');shim=shim.replace('static bool mock_tester=false,','static bool mock_real=false; static bool mock_tester=false,');shim=shim.replace('case ACCOUNT_TRADE_MODE:return ACCOUNT_TRADE_MODE_DEMO;','case ACCOUNT_TRADE_MODE:return mock_real?0:ACCOUNT_TRADE_MODE_DEMO;');shim=shim.replace('for(int i=0;i<mock_visible&&n<(int)std::min(count,(uint)out.size());i++){if(mock_ticks[i].time_msc>=(long)from)out[n++]=mock_ticks[i];}', 'auto it=std::lower_bound(mock_ticks.begin(),mock_ticks.begin()+mock_visible,(long)from,[](const MqlTick &t,long ms){return t.time_msc<ms;});for(;it!=mock_ticks.begin()+mock_visible&&n<(int)std::min(count,(uint)out.size());++it)out[n++]=*it;');(h/'host_compat.hpp').write_text(shim)
pre=trans((h/'headers.mqh').read_text());runtime=trans((h/'DemoController.mq5').read_text()).replace('MqlTick d_raw[HG6_TICK_BATCH];','std::vector<MqlTick> d_raw(HG6_TICK_BATCH);');
# The native crypto loader is independently verified as bytes, host uses the original bank.
cpp='#include "host_compat.hpp"\n'+pre+'\n#include "HG5FileAdapter.mqh"\n'+r'''
bool HG8ReadModel(int i,const string expected,std::vector<uchar>&out){return HG5ReadVerified("HG5QC\\"+HG_ID[i]+".hg5p",expected,67108864,out);}
'''+runtime+'\n#include "HG5CoreFixtureManifest.mqh"\n'
# Existing expected trade fixture, but no legacy broker state or controller in this harness.
t=(old/'host_dispatch_tests.cpp').read_text();t=t[t.index('int main'):t.index(' std::vector<long> ids;')];t=t.replace('bool burst=argc==2&&string(argv[1])=="burst";','string mode=argc>1?argv[1]:"tester";');t=t.replace('int n=16000,','int n=mode=="long"?131072:16000,');t=t[:t.index(' mock_tester=true;')]+r'''
 mock_tester=mode!="demo"&&mode!="real";mock_real=mode=="real";InpWarmupMinutes=0;
 mock_visible=1;mock_clock=mock_ticks[0].time;
 if(mode=="real"){assert(OnInit()==INIT_FAILED);assert(send_count==0);std::cout<<"PASS real-account refusal\n";return 0;}
 assert(OnInit()==INIT_SUCCEEDED);OnTick();assert(!d_fault&&send_count==0);
 std::vector<long> ids;std::map<long,long> pos_to_id;std::map<long,double> actual_net;int eq_entry=0,eq_exit=0,eq_net=0;long observed_closed=0;
 for(int i=2;i<=n;){
   if(mode=="reject"&&send_count==0)mock_send_mode=4;
   size_t old_deals=md.size();mock_visible=i;mock_clock=mock_ticks[i-1].time;int before=send_count;OnTick();if(d_fault){std::cerr<<"FATAL index="<<i<<" phase="<<d_phase<<"\n";return 3;}
   if(send_count>before&&md.size()>old_deals){assert(send_count==before+1);auto &d=md.back();if(d.entry==DEAL_ENTRY_IN){long id=d_proposal;ids.push_back(id);pos_to_id[d.pos]=id;auto it=entry.find(id);if(it!=entry.end()){auto q=mock_ticks.at(it->second);eq_entry+=(it->second==i-1&&d.ms==q.time_msc&&d.price==(side[id]>0?q.ask:q.bid));}}else{long id=pos_to_id.at(d.pos);auto it=exit.find(id);if(it!=exit.end()){auto q=mock_ticks.at(it->second);eq_exit+=(it->second==i-1&&d.ms==q.time_msc&&d.price==(side[id]>0?q.bid:q.ask));}}actual_net[pos_to_id.at(d.pos)]+=d.profit+d.commission+d.swap+d.fee;}
   if(d_closed>observed_closed){assert(d_closed==observed_closed+1);observed_closed=d_closed;}
   if(mode=="reject"&&send_count>0)mock_send_mode=0;
   if(i==n)break;i=std::min(n,i+(mode=="burst"?(i%3==0?257:i%3==1?17:3):1));
 }
 for(long id:ids)if(exit.count(id)&&std::abs(actual_net[id]-mark[id]/100.)<1e-8)eq_net++;
 std::cout<<"RESULT mode="<<mode<<" quotes="<<d_cursor.Ordinal()<<" proposals="<<d_seen<<" expected="<<expected.size()<<" entries="<<ids.size()<<" closed="<<d_closed<<" exact_entry="<<eq_entry<<" exact_exit="<<eq_exit<<" exact_net="<<eq_net<<" stale="<<d_stale<<" busy="<<d_busy<<" rejects="<<d_reject<<" phase="<<d_phase<<" fatal="<<d_fault<<"\n";
 if(mode!="long"&&mode!="burst")assert(ids.size()>1&&d_closed>1);if(mode=="reject")assert(d_reject>=1&&d_closed>1);OnDeinit(0);return 0;}
''';(h/'test.cpp').write_text(cpp+t)
cmd=['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-parameter','-I'+str(h),'-I'+str(inc),str(h/'test.cpp'),'-lcrypto','-o',str(h/'test')];subprocess.run(cmd,check=True)
