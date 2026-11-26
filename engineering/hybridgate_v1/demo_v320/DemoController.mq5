// HG10 clean native terminal adapter. No HG6Broker, HG6Readiness, or HG9 wrapper.
#define HG10_BUILD "HG12-DEMO-ECONOMIC-320-v1"
input group "HybridGate demo trading"
input ulong InpMagic=6202610;
input bool InpLotLadder=false;
input int InpLadderCapUnits=10;
input bool InpWeeklyClock=false;
input group "Quote processing"
input int InpWarmupMinutes=120; // demo only; history never submits orders
input int InpTesterUtcOffsetMinutes=0; // tester does not expose actual historical UTC offset
input int InpMaxQuoteAgeMs=2000;
input int InpDeviationPoints=10;
input int InpTimerMs=250;
input group "Economic competence and independent protection"
input int InpMinEconomicSamples=12;
input double InpMinEdgeCents=0.0;
input double InpPositionRiskPercent=2.0;
input double InpDailyLossPercent=5.0;
input double InpPeakLossPercent=10.0;
// Execution cost cushion in cents per cent-lot, beyond price-to-stop loss.
input double InpStopCostCents=7.0;
// Only one outstanding order or owned position. Persist before each send.
enum D10Phase { D10_FLAT=0,D10_ENTRY=1,D10_OPEN=2,D10_EXIT=3 };
// HG12: causal executable-outcome learning, independent of trade affordability and proposal cadence.
// Features use the original HG5CandleState; the original RX01 duration/value heads remain inputs.
// All labels use observed subsequent quote groups, never a historical trade identity or future candle.
#define HG12_DIM 22
#define HG12_RING 512
#define HG12_QUEUE 64
struct HG12Context { double x[HG12_DIM]; long ms; int session; bool valid,prior_valid; double prior_feature; };
struct HG12Observation { HG12Context x; long ended; double buy,sell,spread; };
struct HG12Future { HG12Context x; long entry; int bid,ask,stage; bool used; };
struct HG12ProposalObs { HG12Context x; long id; int side; bool used; };
class HG12History {
 HG12Observation rows[HG12_RING]; int head,count;
 public:
 HG12History(){head=count=0;}
 void Add(const HG12Context &x,long ended,double buy,double sell,double spread=0){if(!x.valid||ended<=x.ms||!MathIsValidNumber(buy)||!MathIsValidNumber(sell))return;rows[head].x=x;rows[head].ended=ended;rows[head].buy=buy;rows[head].sell=sell;rows[head].spread=spread;head=(head+1)%HG12_RING;if(count<HG12_RING)count++;}
 int Count(){return count;}
 // A decayed local regression with effective sample size. No confidence-interval claim.
 bool Estimate(const HG12Context &x,int side,int min_count,double &mean,double &score,double &ess,bool continuation=false){
  mean=score=ess=0;if(!x.valid||(side!=1&&side!=-1))return false;
  double sw=0,sw2=0,sy=0,sy2=0;int n=0;double closest=1e100;
  for(int k=0;k<count;k++){int j=(head+HG12_RING-1-k)%HG12_RING;long age=x.ms-rows[j].ended;if(age<0||age>7200000)continue;
   double d=0;for(int f=0;f<HG12_DIM;f++){double v=x.x[f]-rows[j].x.x[f];d+=v*v;}d/=HG12_DIM;
   if(rows[j].x.session!=x.session)d+=0.25;
   if(x.prior_valid&&rows[j].x.prior_valid){double v=x.prior_feature-rows[j].x.prior_feature;d+=0.20*v*v;}
   if(d>4.0)continue;closest=MathMin(closest,d);
   double w=1.0/((1.0+3.0*d)*(1.0+3.0*d)*(1.0+(double)age/900000.0));
   double y=(side>0?rows[j].buy:rows[j].sell)+(continuation?rows[j].spread+2.0:0.0);sw+=w;sw2+=w*w;sy+=w*y;sy2+=w*y*y;n++;
  }
  if(sw<=0||sw2<=0)return false;ess=sw*sw/sw2;mean=sy/sw;
  double variance=MathMax(0.0,sy2/sw-mean*mean);
  // Modest uncertainty penalty; samples overlap, so not a statistical confidence bound.
  score=mean-0.5*MathSqrt(variance/MathMax(1.0,ess));
  return n>=min_count&&ess>=0.6*(double)min_count&&closest<=1.0;
 }
};
class HG12Economic {
 HG12History future[3],path[2],pooled; HG12Future pending[HG12_QUEUE]; HG12ProposalObs proposed[HG5_MAX_ACTIVE*4];
 long last_sample,last_group,first_group,next_due; int sample_cursor;
 long labels,paths,missed,expired;
 double Clamp(double v){return MathMax(-3.0,MathMin(3.0,v));}
 int Horizon(int i){return i==0?5000:i==1?15000:30000;}
 public:
 HG12Economic(){last_sample=-1;last_group=-1;first_group=-1;sample_cursor=0;next_due=0;labels=paths=missed=expired=0;for(int i=0;i<HG12_QUEUE;i++)pending[i].used=false;for(int i=0;i<HG5_MAX_ACTIVE*4;i++)proposed[i].used=false;}
 bool NeedContext(long t){return last_sample<0||t/1000>last_sample/1000;}
 bool MakeContext(long t,int bid,int ask,const float &c[],HG12Context &x){
  x.valid=false;x.prior_valid=false;x.prior_feature=0;x.ms=t;x.session=HG5SourceSession(t/1000);if(ArraySize(c)!=72||bid<=0||ask<bid)return false;
  // Original six candle horizons: body, location, previous displacement; price-scale normalization.
  for(int k=0;k<6;k++){int a=12*k,b=3*k;x.x[b]=Clamp((double)c[a]);x.x[b+1]=Clamp(2.0*(double)c[a+2]-1.0);x.x[b+2]=Clamp((double)c[a+11]);}
  double atr=MathMax(1.0,(double)c[32]);x.x[18]=Clamp(MathLog(1.0+(double)(ask-bid)/atr));
  x.x[19]=Clamp(MathLog(1.0+atr)/3.0);x.x[20]=Clamp(MathLog(1.0+(double)c[9])/2.0);x.x[21]=Clamp((double)c[25]);
  for(int k=0;k<HG12_DIM;k++)if(!MathIsValidNumber(x.x[k]))return false;
  x.valid=first_group>=0&&t-first_group>=60000;return true;
 }
 // Every completed timestamp group matures pending labels. A gap >2s at entry, or >5s at exit, is not a valid short-horizon observation.
 bool Advance(long t,int bid,int ask){
  if(t<=last_group||bid<=0||ask<bid)return false;if(first_group<0)first_group=t;last_group=t;if(next_due==0||t<next_due)return true;next_due=0;
  for(int j=0;j<HG12_QUEUE;j++){if(!pending[j].used)continue;
   if(pending[j].entry==0){if(t-pending[j].x.ms>2000){pending[j].used=false;expired++;continue;}pending[j].entry=t;pending[j].bid=bid;pending[j].ask=ask;long due=t+Horizon(0);if(next_due==0||due<next_due)next_due=due;continue;}
   while(pending[j].stage<3&&t>=pending[j].entry+Horizon(pending[j].stage)){
    int h=pending[j].stage++;if(t-pending[j].entry-Horizon(h)<=5000){future[h].Add(pending[j].x,t,(double)(bid-pending[j].ask)-2.0,(double)(pending[j].bid-ask)-2.0,(double)(pending[j].ask-pending[j].bid));labels++;}else expired++;
   }if(pending[j].stage>=3)pending[j].used=false;else{long due=pending[j].entry+Horizon(pending[j].stage);if(next_due==0||due<next_due)next_due=due;}
  }return true;
 }
 bool Sample(const HG12Context &x){if(!NeedContext(x.ms))return true;last_sample=x.ms;if(!x.valid)return true;int j=sample_cursor;sample_cursor=(j+1)%HG12_QUEUE;if(pending[j].used){expired++;pending[j].used=false;}pending[j].x=x;pending[j].entry=0;pending[j].stage=0;pending[j].used=true;long due=x.ms+1;if(next_due==0||due<next_due)next_due=due;return true;}
 void SetPrior(HG12Context &x,float value){x.prior_valid=MathIsValidNumber(value);x.prior_feature=x.prior_valid?Clamp((value>=0?1.0:-1.0)*MathLog(1.0+MathAbs((double)value)/25.0)):0;}
 void Orient(HG12Context &x,int side){for(int k=0;k<18;k++)x.x[k]*=(double)side;}
 bool Register(long id,int side,const HG12Context &x){if(id<0||(side!=1&&side!=-1))return false;int j=(int)(id%(HG5_MAX_ACTIVE*4));if(proposed[j].used)missed++;proposed[j].id=id;proposed[j].side=side;proposed[j].x=x;proposed[j].used=true;return true;}
 void Complete(long id,long t,int net){if(id<0)return;int j=(int)(id%(HG5_MAX_ACTIVE*4));if(!proposed[j].used||proposed[j].id!=id){missed++;return;}HG12Context x=proposed[j].x;int side=proposed[j].side;proposed[j].used=false;if(!x.valid||t<=x.ms)return;path[side>0?0:1].Add(x,t,(double)net,(double)net);Orient(x,side);pooled.Add(x,t,(double)net,(double)net);paths++;}
 bool Predict(const HG12Context &x,int side,float duration,float prior,int min_samples,double edge,double &net,double &direct,double &support,int &route){
  net=direct=support=0;route=0;if(!x.valid)return false;
  // Select the forward horizon by the existing RX01 duration prediction, not by observed future return.
  int h=duration<=10.f?0:duration<=22.5f?1:2;double pm=0,ps=0,pe=0,dm=0,ds=0,de=0;
  bool p=path[side>0?0:1].Estimate(x,side,min_samples,pm,ps,pe);
  bool d=future[h].Estimate(x,side,min_samples,dm,ds,de);net=pm;direct=dm;support=MathMax(pe,de);
  HG12Context oriented=x;Orient(oriented,side);double qm=0,qs=0,qe=0;bool q=pooled.Estimate(oriented,1,min_samples,qm,qs,qe);support=MathMax(support,qe);
  // Original lifecycle is the primary route; independent future-outcome evidence can admit a new regime
  // only when its own executable expectancy is positive and no established lifecycle evidence vetoes it.
  if(p&&ps>edge){route=1;return true;}
  // Pool direction-normalized source lifecycle labels only for sparse directions, never over a known negative directional estimate.
  if(!p&&q&&qs>edge&&(pe<4.0||pm>=0.0)){net=qm;route=3;return true;}
  if(d&&ds>edge&&(!p||pm>=0.0)&&(!q||qm>=0.0||p)&&MathIsValidNumber(prior)){route=2;return true;}
  return false;
 }
 bool Deterioration(const HG12Context &x,int side,int min_samples){
  double a=0,b=0,c=0,d=0,e=0,f=0;
  if(!future[0].Estimate(x,side,min_samples,a,b,c,true)||!future[1].Estimate(x,side,min_samples,d,e,f,true))return false;
  // Direct liquidation-to-liquidation labels, not fresh-entry spread approximations.
  return a< -5.0&&d< -5.0;
 }
 long Labels(){return labels;} long Paths(){return paths;} long Missed(){return missed;} long Expired(){return expired;}
};

// Closed balance high-water mark and UTC-day opening equity; loss halt survives restart.
class HG11Risk {
 public:
 double anchor,peak,day_equity;long day;bool daily,halted;
 HG11Risk(){anchor=peak=day_equity=0;day=-1;daily=halted=false;}
 bool State(HG5StateCodec &c){return c.F64(anchor)&&c.F64(peak)&&c.F64(day_equity)&&c.I64(day)&&c.Flag(daily)&&c.Flag(halted);}
 bool Valid(){return MathIsValidNumber(anchor)&&MathIsValidNumber(peak)&&MathIsValidNumber(day_equity)&&anchor>=0&&peak>=anchor&&day_equity>=0&&day>=-1&&(day==-1?(anchor==0&&peak==0&&day_equity==0&&!daily&&!halted):(anchor>0&&peak>0&&day_equity>0));}
 bool Update(long t,double balance,double equity,double day_pct,double max_pct,bool &changed){
  changed=false;if(t<=0||!MathIsValidNumber(balance)||!MathIsValidNumber(equity)||balance<=0||equity<=0){if(!halted){halted=true;changed=true;}return false;}
  long d=t/86400000;if(day<0){anchor=balance;peak=balance;day_equity=equity;day=d;changed=true;}
  else if(d<day)return false;
  else if(d>day){day=d;day_equity=equity;daily=false;changed=true;}
  if(balance>peak){peak=balance;changed=true;}
  if(!daily&&equity<=day_equity*(1.0-day_pct/100.0)){daily=true;changed=true;}
  if(!halted&&equity<=peak*(1.0-max_pct/100.0)){halted=true;changed=true;}
  return !daily&&!halted;
 }
 double Budget(double equity,double trade_pct,double day_pct,double max_pct){
  if(day<0||daily||halted||equity<=0)return 0;return MathMax(0.0,MathMin(equity*trade_pct/100.0,MathMin(equity-day_equity*(1.0-day_pct/100.0),equity-peak*(1.0-max_pct/100.0))));
 }
};

HG12Economic d_edge; HG11Risk d_risk;
HG12Context d_context;
long d_route1=0,d_route2=0,d_route3=0,d_prior_block=0,d_hold_cut=0,d_stop_last=0,d_edge_last=0,d_hold_second=-1,d_permission_block=0;int d_hold_negative=0;
long d_edge_block=0,d_risk_block=0,d_shadow_closed=0,d_stop_block=0;
bool d_risk_ok=false;
HG6Core d_core; HG6Cursor d_cursor; HG6Store d_store;
HG5Window d_windows[]; MqlTick d_raw[HG6_TICK_BATCH]; HG5Quote d_group[];
HG5StageEvent d_stage[]; HG5Proposal d_proposals[]; HG5PathEvent d_paths[]; HG5AccountEvent d_accounts[];
int d_phase=0,d_side=0,d_units=0,d_offset=0,d_lock=INVALID_HANDLE;
long d_seq=0,d_position=0,d_order=0,d_deal=0,d_created=0,d_last_flat=0,d_closed=0,d_proposal=-1;
double d_net=0;
bool d_test=false,d_initialized=false,d_clock_set=false,d_started=false,d_ready=false,d_fault=false,d_recovered=false,d_protect=false;
long d_seen=0,d_stale=0,d_busy=0,d_clock_block=0,d_account=0,d_reject=0,d_sends=0,d_history_wait=0,d_invalid=0,d_callbacks=0;
long d_last_report=0,d_start_ms=0,d_first_ms=0;ulong d_last_attempt=0;
string d_scope="",d_status="INITIALIZING";
void D10Status(string msg){if(msg!=d_status){d_status=msg;Print("HG10 STATUS: ",msg);}}
void D10Fault(string why){if(!d_fault){Print("HG10 FATAL: ",why," phase=",d_phase," position=",d_position," error=",GetLastError());}d_fault=true;D10Status("QUARANTINED - see Journal");}
bool D10Permission(){return MQLInfoInteger(MQL_TESTER)!=0||AccountInfoInteger(ACCOUNT_TRADE_MODE)==ACCOUNT_TRADE_MODE_DEMO;}
bool D10CanSend(){return D10Permission()&&(d_test||(TerminalInfoInteger(TERMINAL_CONNECTED)!=0&&TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)!=0))&&MQLInfoInteger(MQL_TRADE_ALLOWED)!=0&&AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)!=0&&AccountInfoInteger(ACCOUNT_TRADE_EXPERT)!=0;}
string D10Comment(){return "HG10-"+IntegerToString(d_seq);}
bool D10Save(){HG5StateCodec c;uchar bytes[];int version=2;if(!c.BeginWrite()||!c.I32(version)||!c.I32(d_phase)||!c.I32(d_side)||!c.I32(d_units)||!c.I64(d_seq)||!c.I64(d_position)||!c.I64(d_order)||!c.I64(d_deal)||!c.I64(d_created)||!c.I64(d_last_flat)||!c.I64(d_closed)||!c.I64(d_proposal)||!c.F64(d_net)||!d_risk.State(c)||!c.Finish(bytes)||!d_store.Save(bytes)){D10Fault("durable order state write failed");return false;}return true;}
bool D10Restore(const uchar &bytes[]){HG5StateCodec c;int version=0;if(!c.BeginRead(bytes)||!c.I32(version)||version!=2||!c.I32(d_phase)||!c.I32(d_side)||!c.I32(d_units)||!c.I64(d_seq)||!c.I64(d_position)||!c.I64(d_order)||!c.I64(d_deal)||!c.I64(d_created)||!c.I64(d_last_flat)||!c.I64(d_closed)||!c.I64(d_proposal)||!c.F64(d_net)||!d_risk.State(c)||!d_risk.Valid()||!c.Done())return false;
 if(d_phase<0||d_phase>3||d_seq<0||d_position<0||d_order<0||d_deal<0||d_created<0||d_last_flat<0||d_closed<0||!MathIsValidNumber(d_net))return false;
 if(d_phase==D10_FLAT)return d_position==0&&d_units==0&&d_side==0;
 return (d_side==1||d_side==-1)&&d_units>0&&d_units<=100&&d_created>0&&(d_phase==D10_ENTRY?d_position==0:d_position>0);
}
void D10Clear(){d_hold_second=-1;d_hold_negative=0;d_phase=D10_FLAT;d_side=d_units=0;d_position=d_order=d_deal=d_created=0;d_proposal=-1;d_protect=false;d_recovered=false;}
// Live clocks are validated every pump. In tester use explicit historical offset.
bool D10Clock(int &offset,long &now){datetime server=d_test?TimeCurrent():TimeTradeServer();if(server<=0)return false;now=(long)server*1000;if(d_test){offset=InpTesterUtcOffsetMinutes;return true;}datetime utc=TimeGMT();if(utc<=0)return false;long diff=(long)server-(long)utc;offset=(int)(MathRound((double)diff/900.0)*15.0);return offset>=-840&&offset<=840&&MathAbs((double)(diff-(long)offset*60))<=5.0;}
long D10UTC(long raw){return raw-(long)d_offset*60000;}
// Risk uses account equity, not the modeled historical account balance.
bool D11RiskUpdate(long now,bool clock_ok){
 HG6AccountFacts a;d_risk_ok=false;if(!clock_ok||!d_clock_set||!HG6ReadAccount(a))return false;
 bool changed=false;d_risk_ok=d_risk.Update(D10UTC(now),a.balance,a.equity,InpDailyLossPercent,InpPeakLossPercent,changed);
 if(changed){if(!D10Save())return false;if(d_risk.daily||d_risk.halted)PrintFormat("HG11 CAPITAL HALT equity=%.2f peak=%.2f daily=%d permanent=%d",a.equity,d_risk.peak,(int)d_risk.daily,(int)d_risk.halted);}
 return d_risk_ok;
}
// Supported XAUUSD contract is exactly 100 oz/lot, 0.01 price grid, USD.
// Round stop TOWARD entry so rounding never increases intended risk.
bool D11Stop(MqlTradeRequest &r,const MqlTick &tick,int units,const HG6AccountFacts &a){
 if(!d_risk_ok||units<=0)return false;
 double budget=d_risk.Budget(a.equity,InpPositionRiskPercent,InpDailyLossPercent,InpPeakLossPercent);
 double cost=InpStopCostCents*(double)units/100.0;
 double distance=(budget-cost)/(100.0*r.volume);
 if(!MathIsValidNumber(distance)||distance<=0.01)return false;
 bool buy=r.type==ORDER_TYPE_BUY;
 double price=buy?MathCeil((r.price-distance)*100.0)/100.0:MathFloor((r.price+distance)*100.0)/100.0;
 double min_dist=MathMax(0.01,(double)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*SymbolInfoDouble(_Symbol,SYMBOL_POINT));
 if(price<=0||(buy?tick.bid-price:price-tick.ask)<min_dist-1e-9)return false;
 double gross=0;if(!OrderCalcProfit(r.type,_Symbol,r.volume,r.price,price,gross)||!MathIsValidNumber(gross)||gross>=0||-gross+cost>budget+1e-7)return false;
 r.sl=price;return true;
}
bool D10DefiniteReject(uint code){return code==TRADE_RETCODE_REQUOTE||code==TRADE_RETCODE_PRICE_CHANGED||code==TRADE_RETCODE_PRICE_OFF||code==TRADE_RETCODE_REJECT||code==TRADE_RETCODE_INVALID||code==TRADE_RETCODE_INVALID_VOLUME||code==TRADE_RETCODE_INVALID_PRICE||code==TRADE_RETCODE_INVALID_STOPS||code==TRADE_RETCODE_TRADE_DISABLED||code==TRADE_RETCODE_MARKET_CLOSED||code==TRADE_RETCODE_NO_MONEY||code==TRADE_RETCODE_INVALID_FILL;}
// Broker entry identity is established from the unique entry order/deal, not a mocked callback or assumed fill price.
bool D10EntryEvidence(const HG6Exposure &x){
 if(x.ticket==0||x.identifier==0||x.side!=d_side||x.units!=d_units||x.time_ms<d_created||!HistorySelectByPosition(x.identifier))return false;
 int n=HistoryDealsTotal(),units=0;long entry_order=0;bool matched=false;
 for(int i=0;i<n;i++){ulong t=HistoryDealGetTicket(i);if(t==0)return false;if(HistoryDealGetInteger(t,DEAL_ENTRY)!=DEAL_ENTRY_IN)continue;
  if(HistoryDealGetString(t,DEAL_SYMBOL)!=_Symbol||(ulong)HistoryDealGetInteger(t,DEAL_MAGIC)!=InpMagic||HistoryDealGetInteger(t,DEAL_POSITION_ID)!=(long)x.identifier||HistoryDealGetInteger(t,DEAL_TYPE)!=(d_side>0?DEAL_TYPE_BUY:DEAL_TYPE_SELL))return false;
  long order=HistoryDealGetInteger(t,DEAL_ORDER);int u=0;if(order<=0||!HG6VolumeUnits(HistoryDealGetDouble(t,DEAL_VOLUME),u)||(entry_order!=0&&entry_order!=order))return false;entry_order=order;units+=u;if(d_deal==(long)t||d_order==order)matched=true;
 }
 if(units!=d_units||entry_order<=0)return false;
 if(!matched&&d_order==0&&d_deal==0){if(!HistoryOrderSelect((ulong)entry_order)||HistoryOrderGetString((ulong)entry_order,ORDER_COMMENT)!=D10Comment()||(ulong)HistoryOrderGetInteger((ulong)entry_order,ORDER_MAGIC)!=InpMagic)return false;matched=true;}
 return matched;
}
// A closed trade is recorded from complete position history and only when the broker is flat.
bool D10ClosedEvidence(double &net){net=0;if(d_position<=0||!HistorySelectByPosition((ulong)d_position))return false;int n=HistoryDealsTotal(),ins=0,outs=0;if(n<2||n>4096)return false;
 long seen[];for(int i=0;i<n;i++){ulong t=HistoryDealGetTicket(i);if(t==0)return false;bool dup=false;for(int k=0;k<ArraySize(seen);k++)if(seen[k]==(long)t)dup=true;if(dup)continue;int k=ArraySize(seen);if(ArrayResize(seen,k+1)!=k+1)return false;seen[k]=(long)t;
  if(HistoryDealGetString(t,DEAL_SYMBOL)!=_Symbol||HistoryDealGetInteger(t,DEAL_POSITION_ID)!=d_position)return false;
  long e=HistoryDealGetInteger(t,DEAL_ENTRY),type=HistoryDealGetInteger(t,DEAL_TYPE);int u=0;if(!HG6VolumeUnits(HistoryDealGetDouble(t,DEAL_VOLUME),u))return false;
  if(e==DEAL_ENTRY_IN){if((ulong)HistoryDealGetInteger(t,DEAL_MAGIC)!=InpMagic||type!=(d_side>0?DEAL_TYPE_BUY:DEAL_TYPE_SELL))return false;ins+=u;}
  else if(e==DEAL_ENTRY_OUT){if(type!=(d_side>0?DEAL_TYPE_SELL:DEAL_TYPE_BUY))return false;outs+=u;}else return false;
  double p=HistoryDealGetDouble(t,DEAL_PROFIT)+HistoryDealGetDouble(t,DEAL_COMMISSION)+HistoryDealGetDouble(t,DEAL_SWAP)+HistoryDealGetDouble(t,DEAL_FEE);if(!MathIsValidNumber(p))return false;net+=p;
 }
 return ins>0&&ins==outs&&ins>=d_units&&MathIsValidNumber(net);
}
// Terminal rejected/cancelled/expired orders with no fills can release their intent.
bool D10NoFill(){
 if(d_order<=0||d_deal!=0||!HistorySelect((datetime)(d_created/1000-60),TimeCurrent()+60))return false;
 int n=HistoryDealsTotal();for(int i=0;i<n;i++){ulong t=HistoryDealGetTicket(i);if(t==0||HistoryDealGetInteger(t,DEAL_ORDER)==d_order)return false;}
 if(!HistoryOrderSelect((ulong)d_order)||HistoryOrderGetString((ulong)d_order,ORDER_SYMBOL)!=_Symbol||(ulong)HistoryOrderGetInteger((ulong)d_order,ORDER_MAGIC)!=InpMagic)return false;
 long st=HistoryOrderGetInteger((ulong)d_order,ORDER_STATE);return st==ORDER_STATE_REJECTED||st==ORDER_STATE_CANCELED||st==ORDER_STATE_EXPIRED;
}
bool D10Reconcile(HG6Exposure &x,long raw_now){
 if(!HG6ExposureRead(_Symbol,InpMagic,x)||x.ambiguous||x.foreign){D10Status("WAIT: foreign or ambiguous exposure");return false;}
 if(d_phase==D10_FLAT){if(x.ticket||x.pending){D10Status("WAIT: exposure without matching durable intent; manual reconciliation required");return false;}return true;}
 if(x.pending){D10Status("WAIT: broker order pending");return false;}
 if(d_phase==D10_ENTRY){
  if(!x.ticket){
   if(D10NoFill()){D10Clear();return D10Save();}
   if(d_deal>0&&HistoryDealSelect((ulong)d_deal)&&HistoryDealGetString((ulong)d_deal,DEAL_SYMBOL)==_Symbol&&(ulong)HistoryDealGetInteger((ulong)d_deal,DEAL_MAGIC)==InpMagic&&HistoryDealGetInteger((ulong)d_deal,DEAL_ENTRY)==DEAL_ENTRY_IN){
    long pos=HistoryDealGetInteger((ulong)d_deal,DEAL_POSITION_ID);if(pos>0){d_position=pos;double net=0;if(D10ClosedEvidence(net)){d_net+=net;d_closed++;d_last_flat=raw_now;D10Clear();d_recovered=false;return D10Save();}d_position=0;}
   }
   D10Status("WAIT: unresolved entry receipt; never resend an unknown order");return false;
  }
  if(!D10EntryEvidence(x)){D10Status("WAIT: entry deal evidence not yet available");return false;}
  d_position=(long)x.identifier;d_phase=D10_OPEN;d_last_attempt=0;if(!D10Save())return false;
  PrintFormat("HG10 ENTRY CONFIRMED position=%I64d side=%d volume=%.2f fill=%.2f ms=%I64d",d_position,d_side,x.volume,x.price,x.time_ms);
 }
 if(!x.ticket){double net=0;if(!D10ClosedEvidence(net)){D10Status("WAIT: closed position history not yet complete");return false;}
  long pos=d_position;if(d_core.ActualState()!=0&&!d_core.ConfirmFlat(pos)){D10Fault("holding identity at flat");return false;}
  d_net+=net;d_closed++;d_last_flat=raw_now;D10Clear();if(!D10Save())return false;d_recovered=false;
  PrintFormat("HG10 CLOSED position=%I64d net=%.8f total=%I64d",pos,net,d_closed);return true;
 }
 if((long)x.identifier!=d_position||x.side!=d_side||x.units>d_units){D10Status("WAIT: position identity/volume conflict");return false;}
 if(d_phase==D10_EXIT){if(D10NoFill()){d_phase=D10_OPEN;if(!D10Save())return false;}else {D10Status("WAIT: unresolved exit receipt; never resend an unknown order");return false;}}
 if(x.units<d_units){d_units=x.units;d_protect=true;if(d_core.ActualState()!=0&&!d_core.ReduceActual(d_position,d_units)){D10Fault("holding volume reconciliation");return false;}if(!D10Save())return false;}
 if(d_started&&d_core.ActualState()==0&&!d_recovered&&!d_protect){
  bool bound=x.anchor_ok&&d_core.BindActual(d_position,D10UTC(x.time_ms),d_side,x.price_cents,d_units);
  if(!bound){d_protect=true;Print("HG10 PROTECT: actual fill anchor unavailable; close owned demo exposure");}
 }
 return true;
}
// Native synchronous trade request, durable pre-send state, and fresh quote/position revalidation.
bool D10Submit(int kind,const HG5Proposal &proposal,const MqlTick &tick,const HG6Exposure &x,int units){
 if(!D10CanSend()){d_permission_block++;D10Status("WAIT: broker/terminal trading permission");return false;}if(!d_store.Healthy()||units<=0||units>100||!HG6VolumeAllowed(_Symbol,(double)units/100.0)||!HG6FokAllowed(_Symbol))return false;
 if(kind==1&&(d_phase!=D10_FLAT||x.ticket||x.pending||x.foreign||x.ambiguous||d_fault))return false;
 if(kind==2&&(d_phase!=D10_OPEN||!x.ticket||(long)x.identifier!=d_position||x.pending||x.foreign||x.ambiguous))return false;
 int side=kind==1?proposal.side:-x.side;if(side!=1&&side!=-1)return false;
 long mode=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_MODE);if(mode==SYMBOL_TRADE_MODE_DISABLED||(kind==1&&(mode==SYMBOL_TRADE_MODE_CLOSEONLY||(mode==SYMBOL_TRADE_MODE_LONGONLY&&side<0)||(mode==SYMBOL_TRADE_MODE_SHORTONLY&&side>0))))return false;
 MqlTradeRequest r={};MqlTradeResult v={};MqlTradeCheckResult c={};r.action=TRADE_ACTION_DEAL;r.symbol=_Symbol;r.magic=InpMagic;r.type=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;r.volume=(double)units/100.0;r.price=side>0?tick.ask:tick.bid;r.deviation=(ulong)InpDeviationPoints;r.type_filling=ORDER_FILLING_FOK;r.position=kind==2?x.ticket:0;
 if(kind==1){if(!d_risk_ok||d_risk.daily||d_risk.halted)return false;HG6AccountFacts a;double margin=0;if(!HG6ReadAccount(a)||!HG6AdmissionAccount(a)||!OrderCalcMargin(r.type,_Symbol,r.volume,r.price,margin)||!MathIsValidNumber(margin)||margin<0||margin>a.free_margin){d_account++;return false;}
  // If the requested ladder size is too risky, reduce only to a broker-supported cent-lot.
  // No unprotected entry fallback. If even minimum lot is infeasible, abstain.
  while(units>0){r.volume=(double)units/100.0;if(HG6VolumeAllowed(_Symbol,r.volume)&&D11Stop(r,tick,units,a))break;units--;}
  if(units<=0){d_stop_block++;if(d_stop_last==0||tick.time_msc-d_stop_last>=60000){d_stop_last=tick.time_msc;PrintFormat("HG12 STOP_BLOCK budget=%.2f spread=%.2f broker_min_distance=%.2f equity=%.2f",d_risk.Budget(a.equity,InpPositionRiskPercent,InpDailyLossPercent,InpPeakLossPercent),tick.ask-tick.bid,(double)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*SymbolInfoDouble(_Symbol,SYMBOL_POINT),a.equity);}return false;}
 }
 if(!OrderCheck(r,c)||(c.retcode!=0&&c.retcode!=TRADE_RETCODE_DONE)){d_reject++;PrintFormat("HG10 ORDER CHECK rejected kind=%d retcode=%u error=%d",kind,c.retcode,GetLastError());return false;}
 if(d_seq>=0x7ffffffffffffffe){D10Fault("order sequence exhausted");return false;}d_seq++;r.comment=D10Comment();d_phase=kind==1?D10_ENTRY:D10_EXIT;d_created=tick.time_msc;d_order=d_deal=0;
 if(kind==1){d_side=side;d_units=units;d_proposal=proposal.id;}
 if(!D10Save())return false;
 MqlTick fresh={};HG6Exposure fx;bool unchanged=D10CanSend()&&SymbolInfoTick(_Symbol,fresh)&&HG6TickEqual(tick,fresh)&&HG6ExposureRead(_Symbol,InpMagic,fx)&&!fx.pending&&!fx.ambiguous&&!fx.foreign&&fx.ticket==x.ticket&&fx.identifier==x.identifier&&fx.units==x.units;
 if(!unchanged){if(kind==1)D10Clear();else d_phase=D10_OPEN;d_stale++;D10Save();return false;}
 ResetLastError();bool sent=OrderSend(r,v);int err=GetLastError();d_sends++;d_order=(long)v.order;d_deal=(long)v.deal;PrintFormat("HG10 SEND kind=%d seq=%I64d sent=%d retcode=%u order=%I64u deal=%I64u error=%d",kind,d_seq,(int)sent,v.retcode,v.order,v.deal,err);
 if(D10DefiniteReject(v.retcode)&&v.order==0&&v.deal==0){d_reject++;if(kind==1)D10Clear();else d_phase=D10_OPEN;D10Save();return false;}
 return D10Save(); // successful acknowledgement is NOT a confirmed fill
}
void D10Manage(HG6Exposure &x,const MqlTick &tick,long now,bool clock_ok){
 if(d_phase!=D10_OPEN||x.ticket==0||x.pending||x.foreign||x.ambiguous)return;
 HG6AccountFacts a;bool risk=HG6ReadAccount(a)&&HG6AccountUrgent(a);bool age=now-x.time_ms>=30000;
 int action=HG5Clock(D10UTC(now),true,false,HG6TradeSession(_Symbol,(datetime)(now/1000)),clock_ok,true,false,d_windows,ArraySize(d_windows));
 // A missing broker-side stop, a triggered risk suspension, or an invalid risk snapshot
 // independently requires liquidation of a confirmed owned exposure.
 bool missing_stop=!PositionSelectByTicket(x.ticket)||PositionGetDouble(POSITION_SL)<=0;
 bool urgent=d_fault||d_protect||d_recovered||d_core.ActualState()==3||age||risk||!d_risk_ok||missing_stop||action==HG5_FLATTEN;
 // The original holding model remains authoritative. Independent continuation prediction can cut a losing position.
 long second=D10UTC(now)/1000;
 if(d_context.valid&&second>d_hold_second&&now-x.time_ms>=5000&&D10UTC(now)-d_context.ms>=0&&D10UTC(now)-d_context.ms<=2000){
  d_hold_second=second;double mark=(double)x.side*((x.side>0?tick.bid:tick.ask)-x.price);
  if(mark<0&&d_edge.Deterioration(d_context,x.side,InpMinEconomicSamples))d_hold_negative++;else d_hold_negative=0;
  if(d_hold_negative>=2){urgent=true;d_hold_cut++;}
 }
 if(!urgent&&d_core.ActualReason()<=0)return;
 if(!HG6TradeSession(_Symbol,(datetime)(now/1000))||now-tick.time_msc>InpMaxQuoteAgeMs||!D10CanSend()){D10Status("WAIT: exit due, market/quote/permission unavailable");return;}
 ulong us=GetMicrosecondCount();if(!d_test&&d_last_attempt>0&&us-d_last_attempt<250000)return;d_last_attempt=us;
 HG5Proposal p;p.ZeroFields();PrintFormat("HG10 EXIT REQUEST position=%I64d model_reason=%d protective=%d age_ms=%I64d",d_position,d_core.ActualReason(),(int)urgent,now-x.time_ms);D10Submit(2,p,tick,x,x.units);
}
bool D10Start(const MqlTick &tick,int offset){d_offset=offset;d_clock_set=true;if(!HG6Windows(InpWeeklyClock,0,d_windows)||!d_core.Start(d_windows,262144))return false;d_first_ms=tick.time_msc;d_start_ms=tick.time_msc-(d_test?0:(long)InpWarmupMinutes*60000);if(!d_cursor.Init(d_start_ms))return false;d_started=true;PrintFormat("HG10 SOURCE START server_offset=%d start=%I64d first=%I64d warmup_min=%d",offset,d_start_ms,d_first_ms,d_test?0:InpWarmupMinutes);return true;}
void D10Report(){PrintFormat("HG12 LEARNING labels=%I64d lifecycle=%I64d expired=%I64d missed=%I64d prior_block=%I64d lifecycle_pass=%I64d future_pass=%I64d pooled_pass=%I64d holding_override=%I64d permission_block=%I64d",d_edge.Labels(),d_edge.Paths(),d_edge.Expired(),d_edge.Missed(),d_prior_block,d_route1,d_route2,d_route3,d_hold_cut,d_permission_block);PrintFormat("HG12 ECONOMIC shadow_closed=%I64d edge_block=%I64d risk_block=%I64d stop_block=%I64d daily=%d halt=%d peak=%.2f",d_shadow_closed,d_edge_block,d_risk_block,d_stop_block,(int)d_risk.daily,(int)d_risk.halted,d_risk.peak);PrintFormat("HG10 SUMMARY callbacks=%I64d quotes=%I64d proposals=%I64d stale=%I64d busy=%I64d clock=%I64d account=%I64d rejects=%I64d sends=%I64d closed=%I64d net=%.8f history_wait=%I64d phase=%d fatal=%d",d_callbacks,d_cursor.Ordinal(),d_seen,d_stale,d_busy,d_clock_block,d_account,d_reject,d_sends,d_closed,d_net,d_history_wait,d_phase,(int)d_fault);}
void D10Pump(){
 if(!d_initialized)return;d_callbacks++;if(!D10Permission()){D10Status("BLOCK: real money account");return;}
 if(!d_test&&TerminalInfoInteger(TERMINAL_CONNECTED)==0){D10Status("WAIT: terminal disconnected");return;}
 MqlTick latest={};HG5Quote q;if(!SymbolInfoTick(_Symbol,latest)||!HG6Normalize(latest,q)){D10Status("WAIT: valid bid/ask");return;}
 long now=latest.time_msc;int offset=0;bool clock_ok=D10Clock(offset,now);if(now<latest.time_msc)now=latest.time_msc;
 if(!d_started&&clock_ok&&!d_fault&&!D10Start(latest,offset)){D10Fault("core/clock startup");}
 if(d_clock_set&&offset!=d_offset)clock_ok=false;
 HG6Exposure x;bool reconciled=D10Reconcile(x,now);D11RiskUpdate(now,clock_ok);if(reconciled)D10Manage(x,latest,now,clock_ok);
 if(d_fault||!d_started||!clock_ok){if(!clock_ok)D10Status("WAIT: clock mapping changed or unavailable; restart flat after mapping verified");return;}
 // A close request changes the durable phase before any later entry decision.
 if(d_cursor.Last()>latest.time_msc){D10Fault("quote stream time regression");return;}
 ResetLastError();int n=CopyTicks(_Symbol,d_raw,COPY_TICKS_ALL,(ulong)d_cursor.From(),HG6_TICK_BATCH);int err=GetLastError();
 if(n<0||n>ArraySize(d_raw)||err!=0){d_history_wait++;D10Status("WAIT: tick history synchronization");return;}
 while(n>0&&d_raw[n-1].time_msc>latest.time_msc)n--;
 int lo=0,status=d_cursor.ClassifyBatch(d_raw,n,lo);if(status<0){D10Fault("historical quote overlap/order/cents grid mismatch");return;}if(status==0){d_history_wait++;return;}
 bool previous_ready=d_ready;d_ready=false;
 while(lo<n&&!IsStopped()){
  int end=d_cursor.NextEnd(d_raw,n,lo);if(end<0){D10Fault("same-millisecond group overflow/order");return;}if(end==0)break;
  if(!d_cursor.Group(d_raw,lo,end,d_group)){D10Fault("quote group integrity");return;}
  for(int j=0;j<ArraySize(d_group);j++)d_group[j].ms=D10UTC(d_group[j].ms);
  if(!d_core.StepGroup(d_group,d_stage,d_proposals,d_paths,d_accounts)||!d_cursor.Commit(d_raw,lo,end)){D10Fault("frozen strategy processing");return;}lo=end;
  int qlast=ArraySize(d_group)-1;long stamp=d_group[qlast].ms;int bid=d_group[qlast].bid,ask=d_group[qlast].ask;
  // Mature forward price labels first; all features and proposals are as-of this completed quote group.
  if(!d_edge.Advance(stamp,bid,ask)){D10Fault("economic quote sequence");return;}
  for(int k=0;k<ArraySize(d_paths);k++)if(d_paths[k].kind==2){d_edge.Complete(d_paths[k].id,stamp,d_paths[k].net);d_shadow_closed++;}
  bool sample_due=d_edge.NeedContext(stamp);int proposal_count=ArraySize(d_proposals);float proposal_duration=0,proposal_prior=0;bool proposal_prior_ok=false;
  if(sample_due||proposal_count>0){float c[],raw[];HG12Context cx={};cx.valid=false;
   if(d_core.EconomicCandles(c,raw)&&d_edge.MakeContext(stamp,bid,ask,c,cx)){d_context=cx;if(sample_due)d_edge.Sample(cx);}else d_context.valid=false;
   for(int k=0;k<proposal_count;k++){HG12Context pc=cx;float dt=0,pv=0;bool prior_ok=d_core.EconomicPriors(d_proposals[k].side,dt,pv);if(prior_ok)d_edge.SetPrior(pc,pv);if(k==0){proposal_prior_ok=prior_ok;proposal_duration=dt;proposal_prior=pv;}if(!d_edge.Register(d_proposals[k].id,d_proposals[k].side,pc)){D10Fault("invalid economic proposal identity");return;}}
  }
  if(d_core.ActualState()==3)d_protect=true;
  if(reconciled&&d_phase==D10_OPEN&&d_core.ActualReason()>0)D10Manage(x,latest,now,clock_ok);
  int count=ArraySize(d_proposals);d_seen+=count;if(count<=0)continue;
  bool fresh=previous_ready&&n<HG6_TICK_BATCH&&lo<n&&d_raw[lo].time_msc==latest.time_msc&&d_raw[n-1].time_msc==latest.time_msc&&D10UTC(latest.time_msc)>d_proposals[0].t&&D10UTC(latest.time_msc)-d_proposals[0].t<=InpMaxQuoteAgeMs&&now-latest.time_msc<=InpMaxQuoteAgeMs;
  if(!fresh){d_stale+=count;continue;}
  if(!reconciled||d_phase!=D10_FLAT||x.ticket||x.pending||x.foreign||x.ambiguous||d_core.ActualState()!=0||d_proposals[0].t<=D10UTC(d_last_flat)){d_busy+=count;continue;}
  bool session=HG6TradeSession(_Symbol,(datetime)(now/1000));if(HG5Clock(d_proposals[0].t,false,false,session,clock_ok,true,false,d_windows,ArraySize(d_windows))!=HG5_TRADE||HG5Clock(D10UTC(now),false,false,session,clock_ok,true,false,d_windows,ArraySize(d_windows))!=HG5_TRADE){d_clock_block+=count;continue;}
  HG6AccountFacts a;if(!HG6ReadAccount(a)||!HG6AdmissionAccount(a)||a.balance>9e13){d_account+=count;continue;}
  if(!d_risk_ok||d_risk.daily||d_risk.halted){d_risk_block+=count;continue;}
  float duration=proposal_duration,prior=proposal_prior;if(!proposal_prior_ok){d_prior_block+=count;continue;}
  double net=0,direct=0,support=0;int route=0;
  HG12Context proposal_context=d_context;d_edge.SetPrior(proposal_context,prior);
  if(!d_edge.Predict(proposal_context,d_proposals[0].side,duration,prior,InpMinEconomicSamples,InpMinEdgeCents,net,direct,support,route)){d_edge_block+=count;if(d_edge_last==0||stamp-d_edge_last>=60000){d_edge_last=stamp;PrintFormat("HG12 EDGE_WAIT lifecycle=%.2f future=%.2f effective=%.1f labels=%I64d paths=%I64d prior=%.2f duration=%.2f",net,direct,support,d_edge.Labels(),d_edge.Paths(),(double)prior,(double)duration);}continue;}
  if(route==1)d_route1++;else if(route==2)d_route2++;else d_route3++;
  int units=HG5LotUnits((long)MathRound(a.balance*100.0),InpLotLadder,InpLadderCapUnits);if(count>1)d_stale+=count-1;
  if(!D10Submit(1,d_proposals[0],latest,x,units)){if(!d_fault)D10Status("WAIT: entry rejected or quote changed");}
 }
 d_ready=n>0&&n<HG6_TICK_BATCH&&lo<n&&d_raw[lo].time_msc==latest.time_msc&&d_raw[n-1].time_msc==latest.time_msc;
 if(!d_fault&&d_ready&&d_phase==D10_FLAT&&reconciled)D10Status(d_risk.halted?"CAPITAL HALT - persistent":d_risk.daily?"DAILY LOSS HALT - shadow learning continues":!d_risk_ok?"WAIT: account risk snapshot":D10CanSend()?"ACTIVE - causal forward-outcome learning / trading":"WAIT: Algo Trading permission");else if(!d_ready)D10Status("WARMUP / CATCHUP - no historical orders");
 if(d_callbacks-d_last_report>=10000){D10Report();d_last_report=d_callbacks;}
 Comment("HybridGate DEMO | ",d_status,"\nQuotes: ",d_cursor.Ordinal()," | proposals: ",d_seen," | sends: ",d_sends," | closed: ",d_closed,"\nPhase: ",d_phase," | actual net: ",d_net," | stale: ",d_stale," | blocked: ",d_busy+d_clock_block+d_account+d_edge_block+d_risk_block+d_stop_block+d_prior_block,"\nLabels: ",d_edge.Labels()," | edge waits: ",d_edge_block," | stops blocked: ",d_stop_block," | risk blocks: ",d_risk_block);
}
int OnInit(){
 d_context.valid=false;
 if(InpMinEconomicSamples<8||InpMinEconomicSamples>64||!MathIsValidNumber(InpMinEdgeCents)||InpMinEdgeCents<0||!MathIsValidNumber(InpPositionRiskPercent)||!MathIsValidNumber(InpDailyLossPercent)||!MathIsValidNumber(InpPeakLossPercent)||!MathIsValidNumber(InpStopCostCents)||InpStopCostCents<2||InpPositionRiskPercent<=0||InpPositionRiskPercent>InpDailyLossPercent||InpDailyLossPercent>=InpPeakLossPercent||InpPeakLossPercent>25){Print("HG11 invalid protective settings");return INIT_PARAMETERS_INCORRECT;}
 d_test=MQLInfoInteger(MQL_TESTER)!=0;if(!D10Permission()){Print("HG10: REAL MONEY ACCOUNT PROHIBITED");return INIT_FAILED;}
 if(InpMagic==0||InpLadderCapUnits<1||InpLadderCapUnits>100||InpWarmupMinutes<0||InpWarmupMinutes>720||InpTesterUtcOffsetMinutes< -840||InpTesterUtcOffsetMinutes>840||InpMaxQuoteAgeMs<1||InpDeviationPoints<0||InpTimerMs<50||InpTimerMs>5000){Print("HG10 invalid inputs");return INIT_PARAMETERS_INCORRECT;}
 if(StringFind(_Symbol,"XAUUSD")<0||!HG6BrokerSpec(_Symbol)||AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING||!HG6FokAllowed(_Symbol)||!HG6VolumeAllowed(_Symbol,0.01)){Print("HG10 incompatible XAUUSD broker: requires USD, 100 oz contract, cents grid, hedging and FOK, 0.01 lot");return INIT_FAILED;}
 string key=AccountInfoString(ACCOUNT_SERVER)+"|"+IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN))+"|"+_Symbol+"|"+IntegerToString((long)InpMagic);uchar digest[],id[];if(!HG6TextDigest(key,digest))return INIT_FAILED;string prefix="HG10_"+HG6Hex(digest);
 if(!d_test){d_lock=FileOpen(prefix+".lock",FILE_READ|FILE_WRITE|FILE_BIN|FILE_COMMON);if(d_lock==INVALID_HANDLE){Print("HG10 another owner instance or lock unavailable");return INIT_FAILED;}d_scope="HG12_"+HG6Hex(digest);}
 else {for(int i=0;i<10000;i++){string candidate="HG12_"+HG6Hex(digest)+"_TEST_"+IntegerToString(i);if(!FileIsExist(candidate+".genesis")&&!FileIsExist(candidate+".0.bin")&&!FileIsExist(candidate+".1.bin")){d_scope=candidate;break;}}if(d_scope=="")return INIT_FAILED;}
 if(!HG6TextDigest(d_scope+"|"+HG10_BUILD,id)||!d_store.Init(d_scope,id))return INIT_FAILED;uchar bytes[];int loaded=d_store.Load(bytes);if(loaded<0||!d_store.Healthy()||(loaded>0&&!D10Restore(bytes))){Print("HG10 durable state corrupt/incompatible; preserve files and reconcile manually");return INIT_FAILED;}if(loaded==0&&!D10Save())return INIT_FAILED;d_recovered=d_phase!=D10_FLAT;
 if(ArraySize(HG_ID)!=88||ArraySize(HG_MODEL_SHA)!=88)return INIT_FAILED;
 for(int i=0;i<88;i++){ArrayFree(bytes);if(IsStopped()||!HG8ReadModel(i,HG_MODEL_SHA[i],bytes)||!d_core.Load(i,bytes)){PrintFormat("HG10 MODEL ERROR index=%d name=%s error=%d",i,HG_ID[i],GetLastError());return INIT_FAILED;}if((i+1)%11==0)PrintFormat("HG10 models verified %d/88",i+1);}
 ArrayFree(bytes);d_initialized=true;if(!d_test&&!EventSetMillisecondTimer(InpTimerMs)){d_initialized=false;Print("HG10 timer setup failed");return INIT_FAILED;}
 PrintFormat("HG12 BROKER point=%.5f stops_level=%I64d tick_size=%.5f min_volume=%.2f",SymbolInfoDouble(_Symbol,SYMBOL_POINT),SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL),SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE),SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN));
 Print("HG12 READY: 88 embedded models verified. ",d_test?"STRATEGY TESTER":"DEMO ACCOUNT ONLY",". Native broker execution enabled; real money forbidden.");return INIT_SUCCEEDED;
}
void OnTick(){D10Pump();}
void OnTimer(){D10Pump();}
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result){ // notification only; next tick/timer reads authoritative exposure
}
void OnDeinit(const int reason){EventKillTimer();if(d_initialized)D10Report();if(d_lock!=INVALID_HANDLE)FileClose(d_lock);Comment("");PrintFormat("HG10 DEINIT reason=%d phase=%d; no automatic liquidation on removal",reason,d_phase);}
