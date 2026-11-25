#ifndef HG5_EARLY_OBSERVERS_MQH
#define HG5_EARLY_OBSERVERS_MQH
#include "HG5StateCodec.mqh"
#include "HG5EarlyPrimitives.mqh"
// Generated state and event expressions from frozen Stage4 sources.
class HG5V16 {
private:
 bool emitted[20],valid;long last_output_msc;int last_output_role;long last_quote_ms,prev_spread,prior_minute_mid,events;
 void Write(const HG5Quote &t,HG5EarlyRow &row,long ordinal,int role,int event,int phase,int gap,bool flipped,long contraction){
    if(last_output_msc==t.ms && last_output_role==role)return; // avoid identical slot duplicates
    last_output_msc=t.ms;last_output_role=role; ++events;
    HG5RowBegin(row,ordinal,t.ms,0,31);row.x[0]=role;row.x[1]=event;row.x[2]=phase;row.x[3]=(t.ask-t.bid);row.x[4]=(int)atr.atr;row.x[5]=(t.bid-origin_mid);row.x[6]=s1.Mom();row.x[7]=s5.Mom();row.x[8]=s15.Mom();row.x[9]=s30.Mom();row.x[10]=m1.Slope();row.x[11]=m5.Mom();row.x[12]=m15.Mom();row.x[13]=h1.Mom();row.x[14]=b250.Mom();row.x[15]=s1.Range();row.x[16]=s5.Range();row.x[17]=s15.Range();row.x[18]=s1.prev.updates;row.x[19]=s5.prev.updates;row.x[20]=s15.prev.updates;row.x[21]=s1.cur.updates;row.x[22]=s5.cur.updates;row.x[23]=gap;row.x[24]=dc.dir;row.x[25]=(t.ms-dc.last_flip)/1000;row.x[26]=(dc.dir*(t.bid-dc.reference));row.x[27]=int(flipped);row.x[28]=contraction;row.x[29]=((t.ms/3600000)%24);row.x[30]=((t.ms/86400000+3)%7);
  }
 void Attempt(const HG5Quote &t,HG5EarlyRow &row,long ordinal,long phase,int gap,bool flipped,long contraction,int event,int role,bool condition){if(condition&&!emitted[event]){emitted[event]=true;Write(t,row,ordinal,role,event,(int)phase,gap,flipped,contraction);}}
public:
 HG5EarlyAtr atr;HG5EarlyDC dc;HG5EarlySeries b250,s1,s5,s15,s30,m1,m5,m15,h1;long minute,origin_mid,quotes;double min_atr;
 HG5V16(){ZeroFields();Reset();}
 void Reset(){valid=true;atr.Reset();dc.Reset();b250.Reset(250);s1.Reset(1000);s5.Reset(5000);s15.Reset(15000);s30.Reset(30000);m1.Reset(60000);m5.Reset(300000);m15.Reset(900000);h1.Reset(3600000);minute=-1;origin_mid=0;last_quote_ms=-1;prev_spread=0;quotes=0;events=0;prior_minute_mid=0;min_atr=250;for(int i=0;i<20;i++)emitted[i]=false;last_output_msc=-1;last_output_role=-1;}
 bool Push(const HG5Quote &t,HG5EarlyRow &row){row.width=0;if(!valid||t.ms<0||t.ms<last_quote_ms||t.bid<=0||t.ask<t.bid){valid=false;return false;}long ordinal=quotes+1;
    ++quotes;
    long phase=(t.ms/1000)%60, min=(t.ms/1000)/60;
    const int gap=last_quote_ms<0?0:int(HG5MinL(2147483647,t.ms-last_quote_ms));
    const long oldspread=prev_spread,spread=t.ask-t.bid;
    last_quote_ms=t.ms;prev_spread=spread;
    atr.Update(t);const int dcthresh=int(MathMax(15.,MathMin(160.,atr.Ready()?atr.atr*.12:60.)));
    bool flipped=dc.On(t,dcthresh);
    const bool c1=s1.On(t),c5=s5.On(t);
    b250.On(t);s15.On(t);s30.On(t);m1.On(t);m5.On(t);m15.On(t);h1.On(t);
    if(min!=minute){minute=min;origin_mid=((long)t.ask+t.bid)/2;prior_minute_mid=origin_mid;for(int i=0;i<20;i++)emitted[i]=false;
      const int session=HG5SourceSession(min*60);min_atr=(session==2||session==3)?175:(session==1?200:250);}
    if(spread>25 || !atr.Ready() || atr.atr<min_atr) return true; // original R9 spread/session ATR gate
    
    // Each candidate is a first-occurrence *as-of* market event, never an offline best-of-minute selection.
    if(phase<=14){
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,0,0,phase>=0); // earliest bid/ask valid quote of new minute
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,1,0,phase>=2); // original minute setup scout, earlier than V14 second5
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,2,0,phase>=1 && (flipped || (c1 && s1.Mom()*s1.Slope()>0 && HG5AbsL(s1.Mom())>=15)));
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,3,0,phase>=1 && gap>=450 && c1);
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,4,0,phase>=1 && oldspread>25 && spread<=25);
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,5,0,phase>=1 && c1 && s1.prev.updates>=4 && HG5AbsL(s1.Mom())>=15);
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,6,0,phase>=5); // V14 fallback anchor
    }
    if(phase>=15 && phase<=42){
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,7,1,phase>=15 && flipped);
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,8,1,phase>=16 && c1 && s1.Mom()*s1.Slope()<0 && HG5AbsL(s1.Mom())>=10);
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,9,1,phase>=18 && gap>=450 && c1);
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,10,1,phase>=19 && oldspread>25 && spread<=25);
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,11,1,phase>=18 && c5 && HG5AbsL(s5.Mom())>=30);
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,12,1,phase>=21); // quote-confirmed phase-one rearm anchor
      Attempt(t,row,ordinal,phase,gap,flipped,oldspread-spread,13,1,phase>=25); // original V14 fallback anchor
    }
  return true;}

public:
 void ZeroFields(){for(int i=0;i<20;i++){emitted[i]=0;}{valid=0;}{last_output_msc=0;}{last_output_role=0;}{last_quote_ms=0;}{prev_spread=0;}{prior_minute_mid=0;}{events=0;}{atr.ZeroFields();}{dc.ZeroFields();}{b250.ZeroFields();}{s1.ZeroFields();}{s5.ZeroFields();}{s15.ZeroFields();}{s30.ZeroFields();}{m1.ZeroFields();}{m5.ZeroFields();}{m15.ZeroFields();}{h1.ZeroFields();}{minute=0;}{origin_mid=0;}{quotes=0;}{min_atr=0;}}
 bool StateFields(HG5StateCodec &codec){for(int i=0;i<20;i++){if(!codec.Flag(emitted[i]))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.I64(last_output_msc))return false;}{if(!codec.I32(last_output_role))return false;}{if(!codec.I64(last_quote_ms))return false;}{if(!codec.I64(prev_spread))return false;}{if(!codec.I64(prior_minute_mid))return false;}{if(!codec.I64(events))return false;}{if(!atr.StateFields(codec))return false;}{if(!dc.StateFields(codec))return false;}{if(!b250.StateFields(codec))return false;}{if(!s1.StateFields(codec))return false;}{if(!s5.StateFields(codec))return false;}{if(!s15.StateFields(codec))return false;}{if(!s30.StateFields(codec))return false;}{if(!m1.StateFields(codec))return false;}{if(!m5.StateFields(codec))return false;}{if(!m15.StateFields(codec))return false;}{if(!h1.StateFields(codec))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(origin_mid))return false;}{if(!codec.I64(quotes))return false;}{if(!codec.F64(min_atr))return false;}return true;}
};
struct HG5SecClose {long sec,h,l,c;
 void ZeroFields(){{sec=0;}{h=0;}{l=0;}{c=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(sec))return false;}{if(!codec.I64(h))return false;}{if(!codec.I64(l))return false;}{if(!codec.I64(c))return false;}return true;}
};
class HG5V17 {
private:
 HG5SecClose recent[65];long moves[64],gaps[64],prev_ms,prev_bid,last_pulse_ms;int recent_count,recent_head,move_head,move_count,pulse_side;long snapshots,valid_quotes;bool valid;
 HG5SecClose Recent(int k)const{return recent[(recent_head+k)%65];}
 void AppendRecent(const HG5EarlyBar &b){int k=(recent_head+recent_count)%65;if(recent_count==65){recent_head=(recent_head+1)%65;}else recent_count++;recent[k].sec=b.bucket;recent[k].h=b.high;recent[k].l=b.low;recent[k].c=b.close;}
 void AppendMove(long m,long gap){int k=(move_head+move_count)%64;if(move_count==64){move_head=(move_head+1)%64;}else move_count++;moves[k]=m;gaps[k]=gap;}
public:
 HG5V16 g;long prev_second,seen;
 HG5V17(){ZeroFields();Reset();}
 void Reset(){valid=true;g.Reset();recent_count=recent_head=move_head=move_count=0;prev_ms=-1;prev_bid=0;prev_second=-1;last_pulse_ms=-1;pulse_side=0;seen=snapshots=valid_quotes=0;}
 int MoveCount()const{return move_count;}long Move(int k)const{return moves[(move_head+k)%64];}long Gap(int k)const{return gaps[(move_head+k)%64];}
 double Efficiency(int limit)const{if(recent_count<limit+1)return 0.;long d=Recent(recent_count-1).c-Recent(recent_count-limit-1).c,sum=0;for(int k=recent_count-limit;k<recent_count;k++)sum+=HG5AbsL(Recent(k).c-Recent(k-1).c);return (double)HG5AbsL(d)/HG5MaxL(1,sum);}
 double Vratio()const{if(recent_count<9)return 1.;double sum1=0,sum4=0;for(int k=recent_count-8;k<recent_count;k++){double x=(double)(Recent(k).c-Recent(k-1).c);sum1+=x*x;}for(int k=recent_count-5;k<recent_count;k++){double x=(double)(Recent(k).c-Recent(k-4).c);sum4+=x*x;}return (sum4/4.)/(sum1+1e-6);}
 double Bipowerjump()const{if(recent_count<10)return 0.;double rv=0,bpv=0;for(int k=recent_count-8;k<recent_count;k++){double x=(double)(Recent(k).c-Recent(k-1).c);rv+=x*x;if(k>recent_count-8){double p=(double)(Recent(k-1).c-Recent(k-2).c);bpv+=MathAbs(x*p);}}bpv*=3.141592653589793238462643383279502884/2.;return MathMax(0.,(rv-bpv)/(rv+1.e-6));}
 int S1Qual()const{if(recent_count<11)return 0;long disp=Recent(recent_count-1).c-Recent(recent_count-11).c,minc=9223372036854775807,maxc=-9223372036854775807;int turns=0,last=0;for(int k=recent_count-10;k<recent_count;k++){minc=HG5MinL(minc,Recent(k).l);maxc=HG5MaxL(maxc,Recent(k).h);long d=Recent(k).c-Recent(k-1).c;int sg=(int)(d>0)-(int)(d<0);if(sg){if(last&&last!=sg)turns++;last=sg;}}double eff=Efficiency(10);if(maxc-minc<50||eff<.70||turns>9||HG5AbsL(disp)<15)return 0;return (int)(disp>0)-(int)(disp<0);}
 bool Push(const HG5Quote &t,HG5EarlyRow &row){row.width=0;if(!valid||t.ms<0||t.ms<prev_ms||t.bid<=0||t.ask<t.bid){valid=false;return false;}long ordinal=seen+1;
  ++seen;
  const long second=(t.ms/1000);const long gap=prev_ms<0?0:t.ms-prev_ms;
  long mv=prev_bid? t.bid-prev_bid:0;
  if(prev_ms>=0)AppendMove(mv,gap);
  prev_ms=t.ms;prev_bid=t.bid;
  const bool newsec=(second!=prev_second);
  prev_second=second;
  HG5EarlyRow discard;if(!g.Push(t,discard)){valid=false;return false;}
  if(newsec&&g.s1.closed){
    AppendRecent(g.s1.prev);
  }
  if(!g.atr.Ready())return true;
  if(g.atr.atr<g.min_atr || t.ask-t.bid>25)return true;
  ++valid_quotes;
  int side=S1Qual();
  
  if(side && (((long)t.bid+t.ask)/2>=g.origin_mid+15 || ((long)t.bid+t.ask)/2<=g.origin_mid-15)) {
    last_pulse_ms=t.ms;pulse_side=side;
  }
  // One record at the first observed quote of a second IF that first quote passes ATR/spread gates.
  // Later quote improvements in the same second are deliberately not sampled.
  if(!newsec)return true;
  const int phase=int(second%60);
  // Candidate covers the entire 0..59s minute, with no rank-imposed time windows.
  double pos=0,neg=0,tot=0,lagmean=0,lag2=0;
  for(int k=0;k<move_count;++k){long d=Move(k);pos+=d>0;neg+=d<0;tot+=HG5AbsL(d);lagmean+=Gap(k);lag2+=double(Gap(k))*double(Gap(k));}
  double qn=double(move_count),mean=lagmean/MathMax(1.,qn);
  double gapcv=MathSqrt(MathMax(0.,lag2/MathMax(1.,qn)-mean*mean))/MathMax(1.,mean);
  long pulse_age=last_pulse_ms<0?999999:HG5MinL(999999,(t.ms-last_pulse_ms)/1000);
  long minute_delta=t.bid-g.origin_mid;
  // A recent pulse is a setup precursor. It is not assumed to be a trade.
  HG5RowBegin(row,ordinal,t.ms,0,33);row.x[0]=phase;row.x[1]=t.ask-t.bid;row.x[2]=int(g.atr.atr);row.x[3]=minute_delta;row.x[4]=g.b250.Mom();row.x[5]=g.s1.Mom();row.x[6]=g.s5.Mom();row.x[7]=g.s15.Mom();row.x[8]=g.s30.Mom();row.x[9]=g.m1.Slope();row.x[10]=g.m5.Mom();row.x[11]=g.m15.Mom();row.x[12]=g.h1.Mom();row.x[13]=g.s1.prev.updates;row.x[14]=g.s5.prev.updates;row.x[15]=g.s15.prev.updates;row.x[16]=gap;row.x[17]=g.dc.dir;row.x[18]=(t.ms-g.dc.last_flip)/1000;row.x[19]=g.dc.dir*(t.bid-g.dc.reference);row.x[20]=side;row.x[21]=pulse_side;row.x[22]=pulse_age;row.x[23]=HG5CsvFloat(Efficiency(10));row.x[24]=HG5CsvFloat(Efficiency(4));row.x[25]=HG5CsvFloat(Vratio());row.x[26]=HG5CsvFloat(Bipowerjump());row.x[27]=HG5CsvFloat((pos-neg)/MathMax(1.,pos+neg));row.x[28]=HG5CsvFloat(tot/MathMax(1.,qn));row.x[29]=HG5CsvFloat(mean);row.x[30]=HG5CsvFloat(gapcv);row.x[31]=(t.ms/3600000)%24;row.x[32]=((t.ms/86400000+3)%7);
  ++snapshots;
 return true;}

public:
 void ZeroFields(){for(int i=0;i<65;i++){recent[i].ZeroFields();}for(int i=0;i<64;i++){moves[i]=0;}for(int i=0;i<64;i++){gaps[i]=0;}{prev_ms=0;}{prev_bid=0;}{last_pulse_ms=0;}{recent_count=0;}{recent_head=0;}{move_head=0;}{move_count=0;}{pulse_side=0;}{snapshots=0;}{valid_quotes=0;}{valid=0;}{prev_second=0;}{seen=0;}}
 bool StateFields(HG5StateCodec &codec){for(int i=0;i<65;i++){if(!recent[i].StateFields(codec))return false;}for(int i=0;i<64;i++){if(!codec.I64(moves[i]))return false;}for(int i=0;i<64;i++){if(!codec.I64(gaps[i]))return false;}{if(!codec.I64(prev_ms))return false;}{if(!codec.I64(prev_bid))return false;}{if(!codec.I64(last_pulse_ms))return false;}{if(!codec.I32(recent_count))return false;}{if(!codec.I32(recent_head))return false;}{if(!codec.I32(move_head))return false;}{if(!codec.I32(move_count))return false;}{if(!codec.I32(pulse_side))return false;}{if(!codec.I64(snapshots))return false;}{if(!codec.I64(valid_quotes))return false;}{if(!codec.Flag(valid))return false;}{if(!g.StateFields(codec))return false;}{if(!codec.I64(prev_second))return false;}{if(!codec.I64(seen))return false;}return true;}
};
class HG5V19 {
private:
 HG5V17 src;bool valid;long minute,last_emit,last_pulse,origin,sec_prev,prev_spread,prev_bid,minute_high,minute_low,after_pulse_extreme,last_pullback_ms,last_reclaim_ms,last_sweep_ms,last_dc_ms,prev_dcflip;int pulse_side,stage,emits,impulses,pullbacks,reclaims,sweeps,early_move_side;
public:
 HG5V19(){ZeroFields();Reset();}
 void Reset(){valid=true;src.Reset();minute=last_emit=last_pulse=sec_prev=last_pullback_ms=last_reclaim_ms=last_sweep_ms=last_dc_ms=prev_dcflip=-1;origin=prev_spread=prev_bid=minute_high=minute_low=after_pulse_extreme=0;pulse_side=stage=emits=impulses=pullbacks=reclaims=sweeps=early_move_side=0;}
 bool Push(const HG5Quote &t,HG5EarlyRow &row){row.width=0;if(!valid)return false;
  const long oldsec=src.prev_second;const long oldspread=prev_spread;const long obid=prev_bid;
  HG5EarlyRow discard;if(!src.Push(t,discard)){valid=false;return false;}long ordinal=src.seen;prev_spread=t.ask-t.bid;prev_bid=t.bid;
  if(!src.g.atr.Ready())return true;
  const long sec=(t.ms/1000),mn=sec/60;
  if(mn!=minute){minute=mn;origin=src.g.origin_mid;minute_high=minute_low=t.bid;last_emit=-1;stage=emits=impulses=pullbacks=reclaims=sweeps=0;
   last_pulse=last_pullback_ms=last_reclaim_ms=last_sweep_ms=-1;pulse_side=early_move_side=0;}
  const long oldhigh=minute_high,oldlow=minute_low;
  minute_high=MathMax(minute_high,t.bid);minute_low=MathMin(minute_low,t.bid);
  // All state updates depend solely on observed current and completed prior quote-second bars.
  const int r9=src.S1Qual();
  if(r9 && (t.bid-origin)*r9>=15 && r9!=0){
   if(pulse_side!=r9 || last_pulse<0){pulse_side=r9;last_pulse=t.ms;after_pulse_extreme=t.bid;stage=1;impulses++;}
  }
  if(stage>=1 && pulse_side!=0){
   if(pulse_side*(t.bid-after_pulse_extreme)>0)after_pulse_extreme=t.bid;
   const long pullback=pulse_side*(after_pulse_extreme-t.bid);
   if(pullback>=20 && stage==1){stage=2;last_pullback_ms=t.ms;pullbacks++;}
   if(stage==2 && pulse_side*(t.bid-obid)>=8 && t.ms>last_pullback_ms){stage=3;last_reclaim_ms=t.ms;reclaims++;}
  }
  if((t.bid>=oldhigh+10 && src.g.dc.dir<0) || (t.bid<=oldlow-10 && src.g.dc.dir>0)){last_sweep_ms=t.ms;sweeps++;}
  const bool isnew=(sec!=oldsec);
  if(!isnew)return true;
  if(t.ask-t.bid>25||src.g.atr.atr<src.g.min_atr)return true;
  const int phase=int(sec%60);int flag=0;
  // Bits mark causal transitions. No label/reference time is used as a trigger.
  if(phase==0)flag|=1;
  if(last_pulse>=0 && t.ms-last_pulse<=1000)flag|=2;
  if(last_pullback_ms>=0 && t.ms-last_pullback_ms<=1000)flag|=4;
  if(last_reclaim_ms>=0 && t.ms-last_reclaim_ms<=1000)flag|=8;
  if(src.g.dc.last_flip>=0 && t.ms-src.g.dc.last_flip<1000)flag|=16;
  if(oldspread>25 && t.ask-t.bid<=25)flag|=32;
  if(src.g.s1.prev.updates>=10 && src.g.s1.prev.updates>src.g.s5.prev.updates/3)flag|=64;
  if(src.g.s1.Mom()*src.g.s5.Mom()<0 && HG5AbsL(src.g.s1.Mom())>=12)flag|=128;
  if(src.g.s1.prev.high-src.g.s1.prev.low>=50 && HG5AbsL(src.g.s1.Mom())<=15)flag|=256;
  if(last_sweep_ms>=0 && t.ms-last_sweep_ms<2000)flag|=512;
  if(src.g.s5.prev.high-src.g.s5.prev.low<=20 && src.g.s1.prev.high-src.g.s1.prev.low>=12)flag|=1024;
  // The following are periodic *evaluation opportunities*, not automatic entry triggers.
  if(phase==7||phase==12||phase==17||phase==22||phase==28||phase==33||phase==39||phase==46||phase==53)flag|=2048;
  if(!flag)return true;
  // Bound state evaluation, but do not prevent source-state transitions between observations.
  if(last_emit>=0 && t.ms-last_emit<1500)return true;
  last_emit=t.ms;emits++;
  const long gap=src.MoveCount()==0?0:src.Gap(src.MoveCount()-1);
  const long pulse_age=last_pulse<0?9999:HG5MinL(9999,(t.ms-last_pulse)/1000);
  const long pb_age=last_pullback_ms<0?9999:HG5MinL(9999,(t.ms-last_pullback_ms)/1000);
  const long reclaim_age=last_reclaim_ms<0?9999:HG5MinL(9999,(t.ms-last_reclaim_ms)/1000);
  double pos=0.,neg=0.,abs_move=0.,gapmean=0.;
  for(int i=0;i<src.MoveCount();++i){long v=src.Move(i);pos+=v>0;neg+=v<0;abs_move+=HG5AbsL(v);gapmean+=src.Gap(i);}
  const double qsize=double(src.MoveCount());
  HG5RowBegin(row,ordinal,t.ms,0,37);row.x[0]=phase;row.x[1]=flag;row.x[2]=emits;row.x[3]=stage;row.x[4]=pulse_side;row.x[5]=pulse_age;row.x[6]=pb_age;row.x[7]=reclaim_age;row.x[8]=(t.bid-origin);row.x[9]=(minute_high-minute_low);row.x[10]=pulse_side*(after_pulse_extreme-t.bid);row.x[11]=(t.ask-t.bid);row.x[12]=int(src.g.atr.atr);row.x[13]=src.g.s1.Mom();row.x[14]=src.g.s5.Mom();row.x[15]=src.g.s15.Mom();row.x[16]=src.g.s30.Mom();row.x[17]=src.g.m1.Slope();row.x[18]=src.g.m5.Mom();row.x[19]=src.g.s1.prev.updates;row.x[20]=src.g.s5.prev.updates;row.x[21]=src.g.s15.prev.updates;row.x[22]=src.g.s1.prev.high-src.g.s1.prev.low;row.x[23]=gap;row.x[24]=src.g.dc.dir;row.x[25]=(t.ms-src.g.dc.last_flip)/1000;row.x[26]=src.g.dc.dir*(t.bid-src.g.dc.reference);row.x[27]=r9;row.x[28]=HG5CsvFloat(src.Efficiency(10));row.x[29]=HG5CsvFloat(src.Efficiency(4));row.x[30]=HG5CsvFloat(src.Vratio());row.x[31]=HG5CsvFloat(src.Bipowerjump());row.x[32]=HG5CsvFloat((pos-neg)/MathMax(1.,pos+neg));row.x[33]=HG5CsvFloat(abs_move/MathMax(1.,qsize));row.x[34]=HG5CsvFloat(gapmean/MathMax(1.,qsize));row.x[35]=((t.ms/3600000)%24);row.x[36]=((t.ms/86400000+3)%7);
 return true;}

public:
 void ZeroFields(){{valid=0;}{minute=0;}{last_emit=0;}{last_pulse=0;}{origin=0;}{sec_prev=0;}{prev_spread=0;}{prev_bid=0;}{minute_high=0;}{minute_low=0;}{after_pulse_extreme=0;}{last_pullback_ms=0;}{last_reclaim_ms=0;}{last_sweep_ms=0;}{last_dc_ms=0;}{prev_dcflip=0;}{pulse_side=0;}{stage=0;}{emits=0;}{impulses=0;}{pullbacks=0;}{reclaims=0;}{sweeps=0;}{early_move_side=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!src.StateFields(codec))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(last_emit))return false;}{if(!codec.I64(last_pulse))return false;}{if(!codec.I64(origin))return false;}{if(!codec.I64(sec_prev))return false;}{if(!codec.I64(prev_spread))return false;}{if(!codec.I64(prev_bid))return false;}{if(!codec.I64(minute_high))return false;}{if(!codec.I64(minute_low))return false;}{if(!codec.I64(after_pulse_extreme))return false;}{if(!codec.I64(last_pullback_ms))return false;}{if(!codec.I64(last_reclaim_ms))return false;}{if(!codec.I64(last_sweep_ms))return false;}{if(!codec.I64(last_dc_ms))return false;}{if(!codec.I64(prev_dcflip))return false;}{if(!codec.I32(pulse_side))return false;}{if(!codec.I32(stage))return false;}{if(!codec.I32(emits))return false;}{if(!codec.I32(impulses))return false;}{if(!codec.I32(pullbacks))return false;}{if(!codec.I32(reclaims))return false;}{if(!codec.I32(sweeps))return false;}{if(!codec.I32(early_move_side))return false;}return true;}
};
class HG5V22 {
private:
 HG5V17 src;bool valid;long minute,last_emit,last_pulse,origin,sec_prev,prev_spread,prev_bid,minute_high,minute_low,after_pulse_extreme,last_pullback_ms,last_reclaim_ms,last_sweep_ms,last_dc_ms,prev_dcflip;int pulse_side,stage,emits,impulses,pullbacks,reclaims,sweeps,early_move_side;
public:
 HG5V22(){ZeroFields();Reset();}
 void Reset(){valid=true;src.Reset();minute=last_emit=last_pulse=sec_prev=last_pullback_ms=last_reclaim_ms=last_sweep_ms=last_dc_ms=prev_dcflip=-1;origin=prev_spread=prev_bid=minute_high=minute_low=after_pulse_extreme=0;pulse_side=stage=emits=impulses=pullbacks=reclaims=sweeps=early_move_side=0;}
 bool Push(const HG5Quote &t,HG5EarlyRow &row){row.width=0;if(!valid)return false;
  const long oldsec=src.prev_second;const long oldspread=prev_spread;const long obid=prev_bid;
  HG5EarlyRow discard;if(!src.Push(t,discard)){valid=false;return false;}long ordinal=src.seen;prev_spread=t.ask-t.bid;prev_bid=t.bid;
  if(!src.g.atr.Ready())return true;
  const long sec=(t.ms/1000),mn=sec/60;
  if(mn!=minute){minute=mn;origin=src.g.origin_mid;minute_high=minute_low=t.bid;last_emit=-1;stage=emits=impulses=pullbacks=reclaims=sweeps=0;
   last_pulse=last_pullback_ms=last_reclaim_ms=last_sweep_ms=-1;pulse_side=early_move_side=0;}
  const long oldhigh=minute_high,oldlow=minute_low;
  minute_high=MathMax(minute_high,t.bid);minute_low=MathMin(minute_low,t.bid);
  // All state updates depend solely on observed current and completed prior quote-second bars.
  const int r9=src.S1Qual();
  if(r9 && (t.bid-origin)*r9>=15 && r9!=0){
   if(pulse_side!=r9 || last_pulse<0){pulse_side=r9;last_pulse=t.ms;after_pulse_extreme=t.bid;stage=1;impulses++;}
  }
  if(stage>=1 && pulse_side!=0){
   if(pulse_side*(t.bid-after_pulse_extreme)>0)after_pulse_extreme=t.bid;
   const long pullback=pulse_side*(after_pulse_extreme-t.bid);
   if(pullback>=20 && stage==1){stage=2;last_pullback_ms=t.ms;pullbacks++;}
   if(stage==2 && pulse_side*(t.bid-obid)>=8 && t.ms>last_pullback_ms){stage=3;last_reclaim_ms=t.ms;reclaims++;}
  }
  if((t.bid>=oldhigh+10 && src.g.dc.dir<0) || (t.bid<=oldlow-10 && src.g.dc.dir>0)){last_sweep_ms=t.ms;sweeps++;}
  const bool isnew=(sec!=oldsec);
  if(!isnew)return true;
  const bool eligible=(t.ask-t.bid<=25 && src.g.atr.atr>=src.g.min_atr);
  const int phase=int(sec%60);int flag=0;
  // Bits mark causal transitions. No label/reference time is used as a trigger.
  if(phase==0)flag|=1;
  if(last_pulse>=0 && t.ms-last_pulse<=1000)flag|=2;
  if(last_pullback_ms>=0 && t.ms-last_pullback_ms<=1000)flag|=4;
  if(last_reclaim_ms>=0 && t.ms-last_reclaim_ms<=1000)flag|=8;
  if(src.g.dc.last_flip>=0 && t.ms-src.g.dc.last_flip<1000)flag|=16;
  if(oldspread>25 && t.ask-t.bid<=25)flag|=32;
  if(src.g.s1.prev.updates>=10 && src.g.s1.prev.updates>src.g.s5.prev.updates/3)flag|=64;
  if(src.g.s1.Mom()*src.g.s5.Mom()<0 && HG5AbsL(src.g.s1.Mom())>=12)flag|=128;
  if(src.g.s1.prev.high-src.g.s1.prev.low>=50 && HG5AbsL(src.g.s1.Mom())<=15)flag|=256;
  if(last_sweep_ms>=0 && t.ms-last_sweep_ms<2000)flag|=512;
  if(src.g.s5.prev.high-src.g.s5.prev.low<=20 && src.g.s1.prev.high-src.g.s1.prev.low>=12)flag|=1024;
  // The following are periodic *evaluation opportunities*, not automatic entry triggers.
  if(phase==7||phase==12||phase==17||phase==22||phase==28||phase==33||phase==39||phase==46||phase==53)flag|=2048;
  const bool emit=eligible && flag && (last_emit<0 || t.ms-last_emit>=1500);
  if(emit){last_emit=t.ms;emits++;}
  if(phase>29)return true;
  const long gap=src.MoveCount()==0?0:src.Gap(src.MoveCount()-1);
  const long pulse_age=last_pulse<0?9999:HG5MinL(9999,(t.ms-last_pulse)/1000);
  const long pb_age=last_pullback_ms<0?9999:HG5MinL(9999,(t.ms-last_pullback_ms)/1000);
  const long reclaim_age=last_reclaim_ms<0?9999:HG5MinL(9999,(t.ms-last_reclaim_ms)/1000);
  double pos=0.,neg=0.,abs_move=0.,gapmean=0.;
  for(int i=0;i<src.MoveCount();++i){long v=src.Move(i);pos+=v>0;neg+=v<0;abs_move+=HG5AbsL(v);gapmean+=src.Gap(i);}
  const double qsize=double(src.MoveCount());
  HG5RowBegin(row,ordinal,t.ms,0,45);row.x[0]=phase;row.x[1]=flag;row.x[2]=emits;row.x[3]=stage;row.x[4]=pulse_side;row.x[5]=pulse_age;row.x[6]=pb_age;row.x[7]=reclaim_age;row.x[8]=(t.bid-origin);row.x[9]=(minute_high-minute_low);row.x[10]=pulse_side*(after_pulse_extreme-t.bid);row.x[11]=(t.ask-t.bid);row.x[12]=int(src.g.atr.atr);row.x[13]=src.g.s1.Mom();row.x[14]=src.g.s5.Mom();row.x[15]=src.g.s15.Mom();row.x[16]=src.g.s30.Mom();row.x[17]=src.g.m1.Slope();row.x[18]=src.g.m5.Mom();row.x[19]=src.g.s1.prev.updates;row.x[20]=src.g.s5.prev.updates;row.x[21]=src.g.s15.prev.updates;row.x[22]=src.g.s1.prev.high-src.g.s1.prev.low;row.x[23]=gap;row.x[24]=src.g.dc.dir;row.x[25]=(t.ms-src.g.dc.last_flip)/1000;row.x[26]=src.g.dc.dir*(t.bid-src.g.dc.reference);row.x[27]=r9;row.x[28]=HG5CsvFloat(src.Efficiency(10));row.x[29]=HG5CsvFloat(src.Efficiency(4));row.x[30]=HG5CsvFloat(src.Vratio());row.x[31]=HG5CsvFloat(src.Bipowerjump());row.x[32]=HG5CsvFloat((pos-neg)/MathMax(1.,pos+neg));row.x[33]=HG5CsvFloat(abs_move/MathMax(1.,qsize));row.x[34]=HG5CsvFloat(gapmean/MathMax(1.,qsize));row.x[35]=((t.ms/3600000)%24);row.x[36]=((t.ms/86400000+3)%7);row.x[37]=eligible;row.x[38]=emit;row.x[39]=HG5CsvFloat(src.g.min_atr);row.x[40]=src.g.b250.Mom();row.x[41]=src.g.m15.Mom();row.x[42]=src.g.h1.Mom();row.x[43]=(t.bid-minute_low);row.x[44]=(minute_high-t.bid);
 return true;}

public:
 void ZeroFields(){{valid=0;}{minute=0;}{last_emit=0;}{last_pulse=0;}{origin=0;}{sec_prev=0;}{prev_spread=0;}{prev_bid=0;}{minute_high=0;}{minute_low=0;}{after_pulse_extreme=0;}{last_pullback_ms=0;}{last_reclaim_ms=0;}{last_sweep_ms=0;}{last_dc_ms=0;}{prev_dcflip=0;}{pulse_side=0;}{stage=0;}{emits=0;}{impulses=0;}{pullbacks=0;}{reclaims=0;}{sweeps=0;}{early_move_side=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!src.StateFields(codec))return false;}{if(!codec.Flag(valid))return false;}{if(!codec.I64(minute))return false;}{if(!codec.I64(last_emit))return false;}{if(!codec.I64(last_pulse))return false;}{if(!codec.I64(origin))return false;}{if(!codec.I64(sec_prev))return false;}{if(!codec.I64(prev_spread))return false;}{if(!codec.I64(prev_bid))return false;}{if(!codec.I64(minute_high))return false;}{if(!codec.I64(minute_low))return false;}{if(!codec.I64(after_pulse_extreme))return false;}{if(!codec.I64(last_pullback_ms))return false;}{if(!codec.I64(last_reclaim_ms))return false;}{if(!codec.I64(last_sweep_ms))return false;}{if(!codec.I64(last_dc_ms))return false;}{if(!codec.I64(prev_dcflip))return false;}{if(!codec.I32(pulse_side))return false;}{if(!codec.I32(stage))return false;}{if(!codec.I32(emits))return false;}{if(!codec.I32(impulses))return false;}{if(!codec.I32(pullbacks))return false;}{if(!codec.I32(reclaims))return false;}{if(!codec.I32(sweeps))return false;}{if(!codec.I32(early_move_side))return false;}return true;}
};
#endif
