// Source-exact observer/holding model fixtures; no native orders.
#include "host_compat.hpp"
#include "HG6Core.mqh"
#include "HG5FileAdapter.mqh"
#include "HG5QCManifest.mqh"
#include "HG5CoreFixtureManifest.mqh"
#include "HG6Storage.mqh"
int main(){
 std::vector<uchar> data,bytes;assert(HG5ReadVerified("HG5QC\\HG5CoreFixture.bin",HG5_CORE_FIXTURE_SHA,16777216,data));
 auto I=[&](int p){uint z=0;for(int k=0;k<4;k++)z|=(uint)data.at(p+k)<<(8*k);return (int)z;};int n=I(8),nw=I(12),wp=36+16*n;std::vector<HG5Window>w(nw);for(int i=0;i<nw;i++){int p=wp+32*i;w[i]={HG6Get64(data,p),HG6Get64(data,p+8),HG6Get64(data,p+16),HG6Get64(data,p+24)};}
 auto q=[&](int i){int p=36+16*i;return HG5Quote{HG6Get64(data,p),I(p+8),I(p+12)};};
 auto fresh=[&](){auto c=std::make_unique<HG6Core>();for(int k=0;k<88;k++){assert(HG5ReadVerified("HG5QC\\"+HG_ID[k]+".hg5p",HG_MODEL_SHA[k],67108864,bytes)&&c->Load(k,bytes));}assert(c->Start(w,32768));return c;};
 auto drive=[&](HG6Core &c,int lo,int end){for(int i=lo;i<end;){int j=i+1;std::vector<HG5Quote>g{q(i)};while(j<end&&q(j).ms==q(i).ms)g.push_back(q(j++));assert(j==n||q(j).ms>q(i).ms);std::vector<HG5StageEvent>s;std::vector<HG5Proposal>p;std::vector<HG5PathEvent>h;std::vector<HG5AccountEvent>a;assert(c.StepGroup(g,s,p,h,a));i=j;}};
 auto early=fresh();drive(*early,0,10640);std::vector<uchar> prefix;assert(early->ExportState(prefix));auto late=fresh();assert(late->RestoreState(prefix));
 // Fill occurs strictly inside a gap, with a slipped execution price and partial-sized volume.
 long fm=q(10639).ms+1;assert(fm<q(10640).ms);int px=q(10639).bid-3;
 assert(early->BindActual(90002,fm,-1,px,2)&&early->ActualState()==1);drive(*early,10640,10700);drive(*late,10640,10700);assert(late->BindActual(90002,fm,-1,px,2)&&early->ActualState()==2&&late->ActualState()==2);
 std::vector<uchar> a,b;assert(early->ExportState(a)&&late->ExportState(b)&&a==b&&early->ActualReason()==late->ActualReason());
 // Confirmed partial close is volume-only, not a reset of original fill age or priors.
 assert(early->ReduceActual(90002,1)&&early->ActualMs()==fm&&early->ActualPx()==px&&early->ActualUnits()==1);assert(late->ReduceActual(90002,1)&&late->ExportState(b)&&early->ExportState(a)&&a==b);
 assert(early->ConfirmFlat(90002)&&late->ConfirmFlat(90002));
 // Two distinct quote observations at identical ms: no fabricated intrams fill anchor.
 drive(*early,10700,11710);drive(*late,10700,11710);assert(q(11706).ms==q(11707).ms&&q(11710).ms>q(11709).ms);
 assert(!early->BindActual(90003,q(11707).ms,1,q(11707).ask,1)&&early->ActualState()==3);std::vector<long> stats;assert(early->Stats(stats)&&stats[0]==11710);
 assert(early->ConfirmFlat(90003)&&early->ExportState(a)&&late->ExportState(b)&&a==b);
 std::cout<<"HG6D4 FILL: gap/as-of/slipped fill early versus late exact serialized state; partial-close age invariant; same-ms ambiguous fill quarantines only actual path PASS\n";
}
