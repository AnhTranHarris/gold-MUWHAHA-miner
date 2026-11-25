// Full source fixture, using actual EA pump with host-only hook after each committed
// timestamp group. The production EA contains no hook or historical witness reads.
#include "HG5CoreFixtureManifest.mqh"
#include <sys/resource.h>
static std::vector<uchar> witness;
static int si=0,pi=0,he=0,ae=0,ns=0,np=0,nh=0,na=0,sp=0,cf=0,pp=0,hp=0,hi=0,ap=0;
static int I(int p){uint z=0;for(int k=0;k<4;k++)z|=(uint)witness.at(p+k)<<(8*k);return (int)z;}
static long L(int p){return HG6Get64(witness,p);}
static float F(int p){HGFloatBits v;v.u=(uint)I(p);return v.f;}
void HG6HostCheckGroup(){
 for(auto &s:g_stage){assert(si<ns);int p=sp+40*si;assert(s.stage==L(p)&&s.ms==L(p+8)&&s.side==L(p+16)&&s.rank==L(p+24)&&s.source==L(p+32)&&s.confidence==F(cf+4*si));si++;}
 for(auto &r:g_proposals){assert(pi<np);int p=pp+32*pi;assert(r.id==L(p)&&r.t==L(p+8)&&r.side==L(p+16)&&r.origin==L(p+24));pi++;}
 for(auto &h:g_paths){assert(he<nh);int p=hp+40*he;assert(h.id==L(p)&&h.ordinal==L(p+8)&&h.kind==L(p+16)&&h.why==L(p+24)&&h.net==L(p+32)&&h.h4==F(hi+12*he)&&h.v4==F(hi+12*he+4)&&h.h5==F(hi+12*he+8));he++;}
 for(auto &a:g_accounts){assert(ae<na);int p=ap+32*ae;assert(a.id==L(p)&&a.ordinal==L(p+8)&&a.account==L(p+16)&&a.kind==L(p+24));ae++;}
}
int main(){
 assert(HG5ReadVerified("HG5QC\\HG5CoreFixture.bin",HG5_CORE_FIXTURE_SHA,16777216,witness));int n=I(8),nw=I(12);ns=I(16);np=I(20);nh=I(24);na=I(28);assert(n==131072&&I(32)==32768);
 sp=36+16*n+32*nw;cf=sp+40*ns;pp=cf+4*ns;hp=pp+32*np;hi=hp+40*nh;ap=hi+12*nh;
 for(int i=0;i<n;i++){int p=36+16*i;MqlTick t;t.time_msc=L(p);t.time=t.time_msc/1000;t.bid=I(p+8)/100.;t.ask=I(p+12)/100.;t.flags=6;mock_ticks.push_back(t);}
 mock_tester=true;InpRunId="BURSTQC";InpQuoteCapacity=32768;InpMaxGroupsPerPump=256;InpMaxServiceUs=250000;InpCheckpointSeconds=15;InpRequestTesterExecution=false;mock_visible=1;mock_clock=mock_ticks[0].time;assert(OnInit()==INIT_SUCCEEDED);
 std::vector<ulong> us,backlogs;int callbacks=0,timers=0,pattern[]={1,17,257,4096,32,1024};
 auto pump=[&](bool timer){ulong start=GetMicrosecondCount();if(timer){OnTimer();timers++;}else{OnTick();callbacks++;}us.push_back(GetMicrosecondCount()-start);assert(!g_fatal&&send_count==0);};
 for(int i=1,k=0;;k++){
  mock_visible=i;mock_clock=mock_ticks[i-1].time;int expected=i-1;while(expected>0&&mock_ticks[expected-1].time_msc==mock_ticks[i-1].time_msc)expected--;
  backlogs.push_back((ulong)(expected-g_cursor.Ordinal()));pump(false);int drains=0;while(g_cursor.Ordinal()<expected){assert(++drains<=256);pump(true);}assert(g_cursor.Ordinal()==expected&&g_core.LastGroup()==(expected?mock_ticks[expected-1].time_msc:-1));if(i==n)break;i=std::min(n,i+pattern[k%6]);
 }
 long committed=g_cursor.Ordinal(),last=g_cursor.Last();int se=0,pe=0,he2=0,ae2=0;while(se<ns&&L(sp+40*se+8)<=last)se++;while(pe<np&&L(pp+32*pe+8)<=last)pe++;while(he2<nh&&L(hp+40*he2+8)<committed)he2++;while(ae2<na&&L(ap+32*ae2+8)<committed)ae2++;
 assert(si==se&&pi==pe&&he==he2&&ae==ae2&&g_seen_proposals==pi);std::vector<long> stats;assert(g_core.Stats(stats)&&stats[0]==committed&&stats[1]>0&&stats[2]<=32768);assert(HG6Save());
 auto pct=[](std::vector<ulong>&v,double p){std::sort(v.begin(),v.end());return v[(size_t)std::ceil(p*v.size())-1];};struct rusage ru{};getrusage(RUSAGE_SELF,&ru);
 std::cout<<"BURSTQC quotes="<<n<<" committed="<<committed<<" stage="<<si<<" proposal="<<pi<<" path="<<he<<" account="<<ae<<" retired="<<stats[1]<<" peak="<<stats[2]<<" callbacks="<<callbacks<<" drain_timers="<<timers<<" pump_p50_us="<<pct(us,.50)<<" p95="<<pct(us,.95)<<" p99="<<pct(us,.99)<<" max="<<pct(us,1.)<<" backlog_p50="<<pct(backlogs,.50)<<" p95="<<pct(backlogs,.95)<<" p99="<<pct(backlogs,.99)<<" max="<<pct(backlogs,1.)<<" max_rss_kib="<<ru.ru_maxrss<<" copy_max_us="<<g_copy_max_us<<" save_max_us="<<g_save_max_us<<" sends="<<send_count<<"\n";
 OnDeinit(0);return 0;
}
