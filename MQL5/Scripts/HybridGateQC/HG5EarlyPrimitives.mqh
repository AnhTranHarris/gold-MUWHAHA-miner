#ifndef HG5_EARLY_PRIMITIVES_MQH
#define HG5_EARLY_PRIMITIVES_MQH
#include "HG5StateCodec.mqh"
#include "HG5RX136.mqh"
// All input quote times are source UTC milliseconds; never infer broker offset here.
long HG5MinL(long a,long b){return a<b?a:b;}long HG5MaxL(long a,long b){return a>b?a:b;}long HG5AbsL(long a){return a<0?-a:a;}
struct HG5EarlyRow {long ordinal,ms;int kind,width;double x[64];
 void ZeroFields(){{ordinal=0;}{ms=0;}{kind=0;}{width=0;}for(int i=0;i<64;i++){x[i]=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(ordinal))return false;}{if(!codec.I64(ms))return false;}{if(!codec.I32(kind))return false;}{if(!codec.I32(width))return false;}for(int i=0;i<64;i++){if(!codec.F64(x[i]))return false;}return true;}
};
void HG5RowBegin(HG5EarlyRow &r,long ordinal,long ms,int kind,int width){r.ordinal=ordinal;r.ms=ms;r.kind=kind;r.width=width;for(int i=0;i<64;i++)r.x[i]=0;}
// C++ default ostream uses six significant digits on floating values. Preserve that
// historical numerical boundary instead of silently injecting higher-precision features.
// Actual terminal StringFormat/StringToDouble parity is a mandatory native test.
double HG5CsvFloat(double x){return StringToDouble(StringFormat("%.6g",x));}
int HG5Weekday(int y,int m,int d){int offsets[12]={0,3,2,5,0,3,5,1,4,6,2,4};if(m<3)y--;return (y+y/4-y/100+y/400+offsets[m-1]+d)%7;}
bool HG5Leap(int y){return y%400==0||(y%4==0&&y%100!=0);}
int HG5LastSunday(int y,int m){int len=m==2?(HG5Leap(y)?29:28):(m==4||m==6||m==9||m==11?30:31);return len-HG5Weekday(y,m,len);}
int HG5NthSunday(int y,int m,int n){return 1+(7-HG5Weekday(y,m,1))%7+7*(n-1);}
long HG5CivilDays(int y,int m,int d){y-=(m<=2);long era=y/400,yoe=y-era*400,mp=m+(m>2?-3:9),doy=(153*mp+2)/5+d-1,doe=yoe*365+yoe/4-yoe/100+doy;return era*146097+doe-719468;}
int HG5YearUTC(long sec){long z=sec/86400+719468,era=z/146097,doe=z-era*146097,yoe=(doe-doe/1460+doe/36524-doe/146096)/365,y=yoe+era*400,doy=doe-(365*yoe+yoe/4-yoe/100),mp=(5*doy+2)/153,m=mp+(mp<10?3:-9);return (int)(y+(m<=2));}
long HG5StampUTC(int y,int m,int d,int h){return HG5CivilDays(y,m,d)*86400+(long)h*3600;}
int HG5SourceSession(long sec){int y=HG5YearUTC(sec);bool ld=sec>=HG5StampUTC(y,3,HG5LastSunday(y,3),1)&&sec<HG5StampUTC(y,10,HG5LastSunday(y,10),1),nd=sec>=HG5StampUTC(y,3,HG5NthSunday(y,3,2),7)&&sec<HG5StampUTC(y,11,HG5NthSunday(y,11,1),6);int minute=(int)((sec%86400)/60),lond=(minute+(ld?60:0))%1440,ny=(minute+(nd?-240:-300)+1440)%1440;bool l=lond>=480&&lond<990,n=ny>=480&&ny<1020;return l&&n?2:l?1:n?3:0;}
struct HG5EarlyAtr {
 long bucket,high,low,close,previous_close;int completed,seed_n,period;double seed_sum,atr;
 void Reset(){bucket=-1;high=0;low=0;close=0;previous_close=-1;completed=0;seed_n=0;period=14;seed_sum=0;atr=-1;}
 void Update(const HG5Quote &t){long k=(t.ms/1000/300)*300;if(bucket==-1){bucket=k;high=low=close=t.bid;return;}if(k==bucket){high=HG5MaxL(high,t.bid);low=HG5MinL(low,t.bid);close=t.bid;return;}if(previous_close>=0){long tr=HG5MaxL(high-low,HG5MaxL(HG5AbsL(high-previous_close),HG5AbsL(low-previous_close)));if(atr<0){seed_sum+=tr;++seed_n;if(seed_n==period)atr=seed_sum/period;}else atr=(atr*(period-1)+tr)/period;}++completed;previous_close=close;bucket=k;high=low=close=t.bid;}
 bool Ready()const{return atr>=0&&completed>=period+2;}

 void ZeroFields(){{bucket=0;}{high=0;}{low=0;}{close=0;}{previous_close=0;}{completed=0;}{seed_n=0;}{period=0;}{seed_sum=0;}{atr=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(bucket))return false;}{if(!codec.I64(high))return false;}{if(!codec.I64(low))return false;}{if(!codec.I64(close))return false;}{if(!codec.I64(previous_close))return false;}{if(!codec.I32(completed))return false;}{if(!codec.I32(seed_n))return false;}{if(!codec.I32(period))return false;}{if(!codec.F64(seed_sum))return false;}{if(!codec.F64(atr))return false;}return true;}
};
struct HG5EarlyBar {long bucket,open,high,low,close,updates;
 void ZeroFields(){{bucket=0;}{open=0;}{high=0;}{low=0;}{close=0;}{updates=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(bucket))return false;}{if(!codec.I64(open))return false;}{if(!codec.I64(high))return false;}{if(!codec.I64(low))return false;}{if(!codec.I64(close))return false;}{if(!codec.I64(updates))return false;}return true;}
};
struct HG5EarlySeries {
 long span;bool ready;HG5EarlyBar cur,prev,prev2;int closed;
 void Clear(HG5EarlyBar &b){b.bucket=b.open=b.high=b.low=b.close=b.updates=0;}
 void Reset(long n){span=n;ready=false;Clear(cur);Clear(prev);Clear(prev2);closed=0;}
 void NewBar(const long b,const int bid){cur.bucket=b;cur.open=cur.high=cur.low=cur.close=bid;cur.updates=1;}
 bool On(const HG5Quote &t){long b=t.ms/span;if(!ready){ready=true;NewBar(b,t.bid);return false;}if(b!=cur.bucket){prev2=prev;prev=cur;++closed;NewBar(b,t.bid);return true;}cur.high=HG5MaxL(cur.high,t.bid);cur.low=HG5MinL(cur.low,t.bid);cur.close=t.bid;++cur.updates;return false;}
 long Mom()const{return closed>1?prev.close-prev2.close:0;}long Slope()const{return closed>0?prev.close-prev.open:0;}long Range()const{return closed>0?prev.high-prev.low:0;}

 void ZeroFields(){{span=0;}{ready=0;}{cur.ZeroFields();}{prev.ZeroFields();}{prev2.ZeroFields();}{closed=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(span))return false;}{if(!codec.Flag(ready))return false;}{if(!cur.StateFields(codec))return false;}{if(!prev.StateFields(codec))return false;}{if(!prev2.StateFields(codec))return false;}{if(!codec.I32(closed))return false;}return true;}
};
struct HG5EarlyDC {
 int dir;long extreme,high,low,reference,last_flip;
 void Reset(){dir=0;extreme=high=low=reference=0;last_flip=-1;}
 bool On(const HG5Quote &t,long thresh){bool flipped=false;if(!high){high=low=extreme=reference=t.bid;last_flip=t.ms;return false;}if(dir==0){high=HG5MaxL(high,t.bid);low=HG5MinL(low,t.bid);if(t.bid-low>=thresh){dir=1;extreme=reference=t.bid;flipped=true;}else if(high-t.bid>=thresh){dir=-1;extreme=reference=t.bid;flipped=true;}}else if(dir>0){if(t.bid>extreme)extreme=t.bid;if(extreme-t.bid>=thresh){dir=-1;extreme=reference=t.bid;flipped=true;}}else{if(t.bid<extreme)extreme=t.bid;if(t.bid-extreme>=thresh){dir=1;extreme=reference=t.bid;flipped=true;}}if(flipped)last_flip=t.ms;return flipped;}

 void ZeroFields(){{dir=0;}{extreme=0;}{high=0;}{low=0;}{reference=0;}{last_flip=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I32(dir))return false;}{if(!codec.I64(extreme))return false;}{if(!codec.I64(high))return false;}{if(!codec.I64(low))return false;}{if(!codec.I64(reference))return false;}{if(!codec.I64(last_flip))return false;}return true;}
};
// Exact V14/V15 source series use same bid-price candle geometry. V15 intrinsic DC
// keeps reference at the flip quote (not at the extreme before reversal).
struct HG5Intrinsic {
 int direction;long hi,lo,extreme,last_flip_ms,reference_price,prior_quote_ms,gap_ms;
 void Reset(){direction=0;hi=lo=extreme=last_flip_ms=reference_price=gap_ms=0;prior_quote_ms=-1;}
 void Update(const HG5Quote &t,int threshold){gap_ms=prior_quote_ms<0?0:t.ms-prior_quote_ms;prior_quote_ms=t.ms;if(!hi){hi=lo=extreme=reference_price=t.bid;last_flip_ms=t.ms;return;}if(!direction){hi=HG5MaxL(hi,t.bid);lo=HG5MinL(lo,t.bid);if(t.bid-lo>=threshold){direction=1;extreme=reference_price=t.bid;last_flip_ms=t.ms;}else if(hi-t.bid>=threshold){direction=-1;extreme=reference_price=t.bid;last_flip_ms=t.ms;}}else if(direction>0){if(t.bid>extreme)extreme=t.bid;if(extreme-t.bid>=threshold){direction=-1;extreme=reference_price=t.bid;last_flip_ms=t.ms;}}else{if(t.bid<extreme)extreme=t.bid;if(t.bid-extreme>=threshold){direction=1;extreme=reference_price=t.bid;last_flip_ms=t.ms;}}}
 long AgeS(long ms)const{return (ms-last_flip_ms)/1000;}long Overshoot(long bid)const{return direction*(bid-reference_price);}

 void ZeroFields(){{direction=0;}{hi=0;}{lo=0;}{extreme=0;}{last_flip_ms=0;}{reference_price=0;}{prior_quote_ms=0;}{gap_ms=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I32(direction))return false;}{if(!codec.I64(hi))return false;}{if(!codec.I64(lo))return false;}{if(!codec.I64(extreme))return false;}{if(!codec.I64(last_flip_ms))return false;}{if(!codec.I64(reference_price))return false;}{if(!codec.I64(prior_quote_ms))return false;}{if(!codec.I64(gap_ms))return false;}return true;}
};
class HG5PhaseObserver {
private:
 HG5EarlyAtr atr;HG5Intrinsic intrinsic;HG5EarlySeries sub250,sec1,sec5,sec15,sec30,m1,m5,m15,h1;
 long minute,opening_mid,last_entry_signal_ms,last_grid_bucket,n,last;int count,first_direction;double current_atrmin;bool grid,valid;
 int InitialSide(const HG5Quote &t)const{long d=0;if(sec5.closed>1)d=sec5.Mom();if(!d&&sec1.closed>1)d=sec1.Mom();if(!d&&m1.closed>0)d=m1.Slope();if(!d&&sec15.closed>1)d=sec15.Mom();if(!d)d=t.bid-opening_mid;return d>=0?1:-1;}
 void Write(const HG5Quote &t,int side,int kind,int phase,int spread,int dc_threshold,HG5EarlyRow &r){HG5RowBegin(r,n,t.ms,kind,grid?29:20);int i=0;r.x[i++]=side;r.x[i++]=phase;r.x[i++]=spread;r.x[i++]=HG5CsvFloat(atr.atr);r.x[i++]=sec5.Mom();r.x[i++]=sec15.Mom();r.x[i++]=m1.Slope();r.x[i++]=sub250.Mom();r.x[i++]=sec1.Mom();r.x[i++]=sec30.Mom();r.x[i++]=m5.Mom();r.x[i++]=m15.Mom();r.x[i++]=h1.Mom();r.x[i++]=t.bid-opening_mid;r.x[i++]=sec1.Range();r.x[i++]=sec5.Range();r.x[i++]=m1.Range();r.x[i++]=sec1.cur.updates;r.x[i++]=sec5.cur.updates;if(grid){r.x[i++]=sec1.prev.updates;r.x[i++]=sec5.prev.updates;r.x[i++]=sec5.prev2.updates;r.x[i++]=sec15.prev.updates;r.x[i++]=intrinsic.gap_ms;r.x[i++]=intrinsic.direction;r.x[i++]=intrinsic.AgeS(t.ms);r.x[i++]=intrinsic.Overshoot(t.bid);r.x[i++]=dc_threshold;}r.width=i;}
public:
 HG5PhaseObserver(){ZeroFields();Reset(false);}
 void Reset(bool v15){grid=v15;valid=true;atr.Reset();intrinsic.Reset();sub250.Reset(250);sec1.Reset(1000);sec5.Reset(5000);sec15.Reset(15000);sec30.Reset(30000);m1.Reset(60000);m5.Reset(300000);m15.Reset(900000);h1.Reset(3600000);minute=-1;opening_mid=0;last_entry_signal_ms=last_grid_bucket=-1;n=0;last=-1;count=first_direction=0;current_atrmin=250;}
 bool Push(const HG5Quote &t,HG5EarlyRow &r){r.width=0;if(!valid||t.ms<0||t.ms<last||t.bid<=0||t.ask<t.bid){valid=false;return false;}last=t.ms;++n;atr.Update(t);int dc_threshold=(int)MathMax(15.,MathMin(160.,atr.Ready()?atr.atr*.12:60.));if(grid)intrinsic.Update(t,dc_threshold);sub250.On(t);sec1.On(t);sec5.On(t);sec15.On(t);sec30.On(t);m1.On(t);m5.On(t);m15.On(t);h1.On(t);long m=t.ms/1000/60;if(m!=minute){minute=m;count=0;first_direction=0;opening_mid=((long)t.bid+t.ask)/2;int session=HG5SourceSession(m*60);current_atrmin=(session==2||session==3)?175:session==1?200:250;}int phase=(int)(t.ms/1000%60),spread=t.ask-t.bid;if(grid){long g=t.ms/1000/5;if(g!=last_grid_bucket){last_grid_bucket=g;Write(t,InitialSide(t),2,phase,spread,dc_threshold,r);}return true;}if(spread>25||!atr.Ready()||atr.atr<current_atrmin-1.e-9)return true;if(count==0&&phase>=5){first_direction=InitialSide(t);count=1;Write(t,first_direction,0,phase,spread,dc_threshold,r);last_entry_signal_ms=t.ms;return true;}if(count==1&&phase>=25&&t.ms>=last_entry_signal_ms){count=2;Write(t,-first_direction,1,phase,spread,dc_threshold,r);last_entry_signal_ms=t.ms;}return true;}

public:
 void ZeroFields(){{atr.ZeroFields();}{intrinsic.ZeroFields();}{sub250.ZeroFields();}{sec1.ZeroFields();}{sec5.ZeroFields();}{sec15.ZeroFields();}{sec30.ZeroFields();}{m1.ZeroFields();}{m5.ZeroFields();}{m15.ZeroFields();}{h1.ZeroFields();}{minute=0;}{opening_mid=0;}{last_entry_signal_ms=0;}{last_grid_bucket=0;}{n=0;}{last=0;}{count=0;}{first_direction=0;}{current_atrmin=0;}{grid=0;}{valid=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!atr.StateFields(codec))return false;}{if(!intrinsic.StateFields(codec))return false;}{if(!sub250.StateFields(codec))return false;}{if(!sec1.StateFields(codec))return false;}{if(!sec5.StateFields(codec))return false;}{if(!sec15.StateFields(codec))return false;}{if(!sec30.StateFields(codec))return false;}{if(!m1.StateFields(codec))return false;}{if(!m5.StateFields(codec))return false;}{if(!m15.StateFields(codec))return false;}{if(!h1.StateFields(codec))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(opening_mid))return false;}{if(!codec.I64(last_entry_signal_ms))return false;}{if(!codec.I64(last_grid_bucket))return false;}{if(!codec.I64(n))return false;}{if(!codec.I64(last))return false;}{if(!codec.I32(count))return false;}{if(!codec.I32(first_direction))return false;}{if(!codec.F64(current_atrmin))return false;}{if(!codec.Flag(grid))return false;}{if(!codec.Flag(valid))return false;}return true;}
};
#endif
