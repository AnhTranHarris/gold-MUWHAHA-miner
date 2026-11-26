from pathlib import Path
import re,subprocess
w=Path('/tmp/hg11test'); out=Path('/tmp/hg12test');out.mkdir(exist_ok=True)
b=Path('/mnt/data/GoldMuwahahaMiner_HybridGate_Demo_v320.mq5').read_text(); pre=b.split('// Single-source model payload codec.')[0];ctrl=b[b.index('// HG10 clean native terminal adapter.'):]; h=(w/'host.hpp').read_text();h=h.replace('static double mock_balance=100.;','static double mock_balance=100.;static int mock_stop_level=0;static double mock_floating=0;')
h=h.replace('case ACCOUNT_BALANCE:case ACCOUNT_EQUITY:return mock_balance;', 'case ACCOUNT_BALANCE:return mock_balance;case ACCOUNT_EQUITY:return mock_balance+mock_floating;')
h=h.replace('if(p==SYMBOL_DIGITS)return 2;', 'if(p==SYMBOL_TRADE_STOPS_LEVEL)return mock_stop_level;if(p==SYMBOL_DIGITS)return 2;')
# capture native equivalent broker stop execution independently of EA; no fabricated good fills
h+='''\nint mock_stop_count=0;
void MockStops(){mock_floating=0;if(!mock_pt||mock_visible<=0)return;auto t=mock_ticks.at(mock_visible-1);double price=mock_side==POSITION_TYPE_BUY?t.bid:t.ask;double pnl=(price-mock_price)*(mock_side==POSITION_TYPE_BUY?1:-1)*mock_volume*100;mock_floating=pnl;
 if(mock_sl>0&&(mock_side==POSITION_TYPE_BUY?price<=mock_sl:price>=mock_sl)){ulong o=++mock_next,d=++mock_next;int side=mock_side==POSITION_TYPE_BUY?DEAL_TYPE_SELL:DEAL_TYPE_BUY;mo.push_back({o,mock_magic,mock_pt,t.time_msc,side,ORDER_STATE_FILLED,_Symbol,"broker stop",false});md.push_back({d,o,mock_magic,mock_pt,t.time_msc,DEAL_ENTRY_OUT,side,mock_volume,price,pnl,-.01,0,0,_Symbol});mock_balance+=pnl-.01;mock_pt=0;mock_volume=0;mock_floating=0;mock_stop_count++;}}
'''
(out/'host.hpp').write_text(h)
for name in ['model_bank','fixture.bin']:
 p=out/name
 if not p.exists():p.symlink_to(w/name,target_is_directory=name=='model_bank')
src=Path('/tmp/hg11host.py').read_text();trans_source=src[src.index('types=r'):src.index('# archive model loader')].replace('HG(?:5|6|11)','HG(?:5|6|11|12)');exec(trans_source)
loader=src[src.index("loader='''"):src.index('# Retain exact core')];exec(loader)
main=r'''
int main(int argc,char **argv){
 string mode=argc>1?argv[1]:"fixture";
 if(mode=="economic"){
  HG12Economic e;long t=1767315600000L;std::vector<float> c(72,0);HG12Context x;double p=0,d=0,n=0;int route=0;
  for(int k=0;k<100;k++){long now=t+k*1000;assert(e.Advance(now,400000+10*k,400003+10*k));assert(e.MakeContext(now,400000+10*k,400003+10*k,c,x));assert(e.Sample(x));if(k<=65)assert(!e.Predict(x,1,15,0,12,0,p,d,n,route));}
  assert(e.Labels()>0&&e.Paths()==0);assert(e.Predict(x,1,15,0,12,0,p,d,n,route)&&route==2&&d>0);assert(!e.Predict(x,-1,15,0,12,0,p,d,n,route));
  for(int k=100;k<900;k++){long now=t+k*1000;int bid=401000-10*(k-100);assert(e.Advance(now,bid,bid+3));assert(e.MakeContext(now,bid,bid+3,c,x));assert(e.Sample(x));}
  assert(!e.Predict(x,1,15,0,12,0,p,d,n,route));assert(e.Predict(x,-1,15,0,12,0,p,d,n,route));long labels=e.Labels();assert(e.Advance(t+10000000,401000,401003));assert(e.Labels()==labels&&e.Expired()>0);std::cout<<"PASS independent mature labels, cold abstention, directional reversal, gap expiry, no proposal dependency\n";return 0;
 }
 if(mode=="risk"){
  HG11Risk r;bool changed=false;long t=1767315600000L;assert(r.Update(t,100,100,5,10,changed)&&changed);assert(std::abs(r.Budget(100,2,5,10)-2)<1e-8);assert(r.Update(t+1,96,96,5,10,changed));assert(!r.Update(t+2,94.99,94.99,5,10,changed)&&r.daily&&!r.halted);assert(!r.Update(t+3,96,96,5,10,changed));assert(r.Update(t+86400000,95,95,5,10,changed)&&!r.daily);assert(!r.Update(t+86400001,89,89,5,10,changed)&&r.halted);HG5StateCodec c,rd;std::vector<uchar>b;assert(c.BeginWrite()&&r.State(c)&&c.Finish(b));HG11Risk restored;assert(rd.BeginRead(b)&&restored.State(rd)&&rd.Done()&&restored.Valid()&&restored.halted);std::cout<<"PASS budget, daily rollover, permanent drawdown halt and serialized restore\n";return 0;
 }
 std::vector<uchar> data;assert(HG6ReadFile("fixture.bin",16777216,data));auto I=[&](int p){uint z=0;for(int k=0;k<4;k++)z|=uint(data.at(p+k))<<(8*k);return (int)z;};int n=I(8);for(int i=0;i<n;i++){int p=36+16*i;MqlTick t;t.time_msc=HG6Get64(data,p);t.time=t.time_msc/1000;t.bid=I(p+8)/100.;t.ask=I(p+12)/100.;t.flags=6;mock_ticks.push_back(t);}mock_tester=true;mock_visible=1;mock_clock=mock_ticks[0].time;if(mode=="stops")mock_stop_level=50;if(mode=="blocked")mock_stop_level=100000;if(mode=="short")n=16000;
 assert(OnInit()==INIT_SUCCEEDED);for(int i=1;i<=n;i++){mock_visible=i;mock_clock=mock_ticks[i-1].time;MockStops();OnTick();if(d_fault){std::cout<<"FATAL at "<<i<<"\n";return 1;}}
 std::cout<<"HG12 RESULT mode="<<mode<<" quotes="<<d_cursor.Ordinal()<<" proposals="<<d_seen<<" labels="<<d_edge.Labels()<<" lifecycle="<<d_edge.Paths()<<" missed="<<d_edge.Missed()<<" edge_block="<<d_edge_block<<" risk_block="<<d_risk_block<<" stop_block="<<d_stop_block<<" prior_block="<<d_prior_block<<" route1="<<d_route1<<" route2="<<d_route2<<" cut="<<d_hold_cut<<" broker_stops="<<mock_stop_count<<" sends="<<d_sends<<" closed="<<d_closed<<" net="<<d_net<<" balance="<<mock_balance<<" fatal="<<d_fault<<"\n";
 assert(d_seen>0&&d_edge.Labels()>0&&!d_fault);if(mode=="blocked")assert(d_sends==0&&d_stop_block>0);else assert(d_closed>0);OnDeinit(0);return 0;
}
'''
s=trans(pre+loader+ctrl);s=s.replace('"HG10_"+HG6Hex(digest)','string("HG10_")+HG6Hex(digest)').replace('"HG12_"+HG6Hex(digest)','string("HG12_")+HG6Hex(digest)').replace('"HG10-"+IntegerToString(d_seq)','string("HG10-")+IntegerToString(d_seq)');(out/'test.cpp').write_text('#include "host.hpp"\n'+s+'\n'+main)
