from pathlib import Path
import re,json,base64,zipfile
w=Path('/tmp/hg11test'); b=Path('/mnt/data/GoldMuwahahaMiner_HybridGate_Demo_v310.mq5').read_text(); pre=b.split('// Single-source model payload codec.')[0]; ctrl=b[b.index('// HG10 clean native terminal adapter.'):];
files=json.loads(Path('/mnt/data/TEMP_HG9_HOST_SOURCE_TRANSFER.txt').read_text(encoding='utf-8-sig'))['files']; shim=base64.b64decode(files[0]['base64']).decode();
# Native API behavior is mocked explicitly. Record actual account equity and protective stops.
shim=shim.replace('double volume=0,price=0;','double volume=0,price=0,sl=0;').replace('SYMBOL_TRADE_EXEMODE=1001','SYMBOL_TRADE_STOPS_LEVEL=1002,SYMBOL_POINT=1003,POSITION_SL=1004,SYMBOL_TRADE_EXEMODE=1001')
shim=shim.replace('static double mock_volume=0,mock_price=0;','static double mock_volume=0,mock_price=0,mock_sl=0;')
shim=shim.replace('return p==POSITION_VOLUME?mock_volume:mock_price;','return p==POSITION_SL?mock_sl:(p==POSITION_VOLUME?mock_volume:mock_price);')
shim=shim.replace('case SYMBOL_TRADE_TICK_SIZE:return .01;', 'case SYMBOL_POINT:case SYMBOL_TRADE_TICK_SIZE:return .01;')
shim=shim.replace('mock_volume=vol;mock_price=r.price;', 'mock_volume=vol;mock_price=r.price;mock_sl=r.sl;')
shim=shim.replace('if(closing){mock_volume-=vol;', 'mock_balance+=pnl-.01; if(closing){mock_volume-=vol;')
shim+='\ndouble MathCeil(double x){return std::ceil(x);} double MathFloor(double x){return std::floor(x);}\nbool OrderCalcProfit(int type,string sym,double volume,double a,double b,double &p){(void)sym;p=(type==ORDER_TYPE_BUY?b-a:a-b)*volume*100;return true;}\n'
# Host substitute only for APIs unavailable in C++.
shim+='''
int StringLen(const string &s){return (int)s.size();}
#define FILE_COMMON 32
bool FileIsExist(string p,int flags){(void)flags;return FileIsExist(p);}
'''
# inspect shim duplicate symbols
shim+='\nconstexpr uint TRADE_RETCODE_INVALID_STOPS=10016;\n'
(w/'host.hpp').write_text(shim)
# Transform arrays in portable MQL source (same method as previous host harness)
types=r'HG(?:5|6|11)\w+|MqlTick|uchar|int|long|double|float|uint|string'
def trans(s):
 s=re.sub(r'^#property.*$','',s,flags=re.M);s=re.sub(r'^input group.*$','',s,flags=re.M);s=re.sub(r'^input\s+','',s,flags=re.M);s=s.replace("D'2026.01.01 00:00'",'1767225600L');s=re.sub(r'\b(const )?('+types+r') &(\w+)\[\]',lambda m:f'{m[1] or ""}std::vector<{m[2]}> &{m[3]}',s);s=re.sub(r'\b('+types+r') ((?:\w+\[\],)*\w+\[\]);',lambda m:';'.join('std::vector<'+m[1]+'> '+v[:-2] for v in m[2].split(','))+';',s);s=s.replace('MqlTick d_raw[HG6_TICK_BATCH];','std::vector<MqlTick> d_raw(HG6_TICK_BATCH);').replace('float x[],f5[],p[8];','std::vector<float> x,f5;float p[8];').replace('const std::vector<int> &idx','const int *idx');return s
# archive model loader uses original pinned data, not decoder implementation.
z=zipfile.ZipFile('/mnt/data/R9_HYBRIDGATE_V1_STAGE5_PORTABLE_ENGINEERING_20261125.zip');
for n in z.namelist():
 if n.endswith('.hg5p'):z.extract(n,w)
z=zipfile.ZipFile('/mnt/data/R9_HYBRIDGATE_V1_STAGE5_D_I_ENGINEERING_QC_20261125.zip'); (w/'fixture.bin').write_bytes(z.read('hg_stage5i/fixtures/HG5CoreFixture.bin'))
loader='''\nbool HG8ReadModel(int i,string expected,std::vector<uchar>&bytes){string file="model_bank/"+HG_ID[i]+".hg5p";if(!HG6ReadFile(file,67108864,bytes))return false;std::vector<uchar> h;return HG6Hash(bytes,h)&&HG6Hex(h)==expected;}\n'''
# Retain exact core and new controller source under translation; shim uses C++ string operations.
main='''
int main(int argc,char **argv){
 if(argc==2 && string(argv[1])=="risk"){
 assert(D10DefiniteReject(TRADE_RETCODE_INVALID_STOPS));
  HG11Risk r;bool changed=false;long t=1767315600000L;assert(r.Update(t,100,100,5,10,changed)&&changed);assert(std::abs(r.Budget(100,2,5,10)-2)<1e-8);assert(r.Update(t+1,96,96,5,10,changed));assert(!r.Update(t+2,94.99,94.99,5,10,changed)&&r.daily&&!r.halted);assert(!r.Update(t+3,96,96,5,10,changed));assert(r.Update(t+86400000,95,95,5,10,changed)&&!r.daily);assert(!r.Update(t+86400001,89,89,5,10,changed)&&r.halted);assert(!r.Update(t+172800000,100,100,5,10,changed)); HG5StateCodec c,rd;std::vector<uchar>b;assert(c.BeginWrite()&&r.State(c)&&c.Finish(b));HG11Risk restored;assert(rd.BeginRead(b)&&restored.State(rd)&&rd.Done()&&restored.Valid()&&restored.halted);std::cout<<"PASS risk budgets, daily rollover, peak halt, persistent state\\n";return 0;}
 if(argc==2 && string(argv[1])=="edge"){
  HG11Edge e;long t=1767315600000L;for(int j=0;j<61;j++)e.Observe(t+j*1000,400000+j,400010+j);t+=60000;HG11Context x;assert(e.Context(t,1,400060,400070,x)&&x.valid);double m,s,n;assert(!e.Predict(x,24,5,m,s,n));for(int j=0;j<30;j++){x.ms=t+j*1000;assert(e.Register(j,x)&&e.Complete(j,x.ms+500,90));}x.ms=t+31000;assert(e.Predict(x,24,5,m,s,n)&&m>89);for(int j=30;j<60;j++){x.ms=t+j*1000;assert(e.Register(j,x)&&e.Complete(j,x.ms+500,-100));}x.ms=t+61000;assert(!e.Predict(x,24,5,m,s,n));x.side=-1;assert(!e.Predict(x,24,5,m,s,n));x.side=1;x.ms=t+8000000;assert(!e.Predict(x,24,5,m,s,n));std::cout<<"PASS cold abstention, positive competence, negative quarantine, side isolation, expiry\\n";return 0;}
 std::vector<uchar> data;assert(HG6ReadFile("fixture.bin",16777216,data));auto I=[&](int p){uint z=0;for(int k=0;k<4;k++)z|=uint(data.at(p+k))<<(8*k);return (int)z;};int n=I(8);for(int i=0;i<n;i++){int p=36+16*i;MqlTick t;t.time_msc=HG6Get64(data,p);t.time=t.time_msc/1000;t.bid=I(p+8)/100.;t.ask=I(p+12)/100.;t.flags=6;mock_ticks.push_back(t);}mock_tester=true;mock_visible=1;mock_clock=mock_ticks[0].time;assert(OnInit()==INIT_SUCCEEDED);for(int i=1;i<=n;i++){mock_visible=i;mock_clock=mock_ticks[i-1].time;OnTick();if(d_fault){std::cout<<"FATAL at "<<i<<"\\n";return 1;}}
 std::cout<<"HG11 FIXTURE quotes="<<d_cursor.Ordinal()<<" proposals="<<d_seen<<" shadows="<<d_shadow_closed<<" edge_block="<<d_edge_block<<" risk_block="<<d_risk_block<<" stop_block="<<d_stop_block<<" sends="<<d_sends<<" closed="<<d_closed<<" net="<<d_net<<" balance="<<mock_balance<<" fatal="<<d_fault<<"\\n";assert(d_seen>0&&d_shadow_closed>0&&d_closed>0&&!d_fault);OnDeinit(0);return 0;}
'''
# host enum int aliases and string concatenate changes
s=trans(pre+loader+ctrl); s=s.replace('"HG10_"+HG6Hex(digest)','string("HG10_")+HG6Hex(digest)').replace('"HG11_"+HG6Hex(digest)','string("HG11_")+HG6Hex(digest)').replace('"HG10-"+IntegerToString(d_seq)','string("HG10-")+IntegerToString(d_seq)');
(w/'test.cpp').write_text('#include "host.hpp"\n'+s+'\n'+main)

# Reproduce loss-injection harness separately so ordinary test keeps real mock P&L.
old='double pnl=closing?(r.price-mock_price)*(mock_side==POSITION_TYPE_BUY?1:-1)*vol*100:0;'
assert shim.count(old)==1
(w/'host_loss.hpp').write_text(shim.replace(old,'double pnl=closing?-1.20:0;'))
loss=(w/'test.cpp').read_text().replace('#include "host.hpp"','#include "host_loss.hpp"',1).replace('assert(d_seen>0&&d_shadow_closed>0&&d_closed>0&&!d_fault);','assert(d_seen>0&&d_shadow_closed>0&&d_closed>0&&!d_fault&&d_stop_block>0&&mock_balance>=95.0&&d_closed==4);')
(w/'loss.cpp').write_text(loss)
