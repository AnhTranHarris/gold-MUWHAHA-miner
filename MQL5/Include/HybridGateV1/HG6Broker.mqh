#ifndef HG6_BROKER_MQH
#define HG6_BROKER_MQH
#include "HG6Storage.mqh"
#include "HG6CommitLink.mqh"
#include "HG6Feed.mqh"
#include "HG5OperationalGate.mqh"
// SECTION B1: actual broker facts. No modeled trade is ever booked as a real fill.
// Explicit Strategy Tester execution only. Demo/live remain hard locked.
#define HG6_EXECUTION_RELEASED 0
#define HG6_TESTER_EXECUTION_ENABLED 1
#define HG6_LOCAL_NOT_SENT -6001 // durable local cancellation, NOT a broker retcode
struct HG6Exposure {ulong ticket,identifier,pending_ticket;long time_ms;int side,price_cents,units;double volume,price;bool anchor_ok,foreign,pending,ambiguous;};
bool HG6VolumeUnits(double v,int &units){if(!MathIsValidNumber(v)||v<=0||v>100.0)return false;double q=v*100.0,r=MathRound(q);if(MathAbs(q-r)>0.000001)return false;units=(int)r;return units>0;}
bool HG6BrokerSpec(const string sym){
 return AccountInfoString(ACCOUNT_CURRENCY)=="USD"&&AccountInfoInteger(ACCOUNT_LEVERAGE)>0&&
  MathAbs(SymbolInfoDouble(sym,SYMBOL_TRADE_CONTRACT_SIZE)-100.0)<1e-8&&
  MathAbs(SymbolInfoDouble(sym,SYMBOL_TRADE_TICK_SIZE)-0.01)<1e-10&&SymbolInfoInteger(sym,SYMBOL_DIGITS)>=2;
}
bool HG6ExposureRead(const string sym,ulong magic,HG6Exposure &x){
 x.ticket=0;x.identifier=0;x.pending_ticket=0;x.time_ms=0;x.side=x.price_cents=x.units=0;x.volume=x.price=0;x.anchor_ok=false;x.foreign=x.pending=x.ambiguous=false;
 for(int i=PositionsTotal()-1;i>=0;i--){ulong t=PositionGetTicket(i);if(t==0||!PositionSelectByTicket(t))return false;if(PositionGetString(POSITION_SYMBOL)!=sym)continue;
  if((ulong)PositionGetInteger(POSITION_MAGIC)!=magic){x.foreign=true;continue;}if(x.ticket!=0){x.ambiguous=true;continue;}
  x.ticket=t;x.identifier=(ulong)PositionGetInteger(POSITION_IDENTIFIER);x.time_ms=PositionGetInteger(POSITION_TIME_MSC);
  long type=PositionGetInteger(POSITION_TYPE);if(type!=POSITION_TYPE_BUY&&type!=POSITION_TYPE_SELL)return false;x.side=type==POSITION_TYPE_BUY?1:-1;x.volume=PositionGetDouble(POSITION_VOLUME);
  x.price=PositionGetDouble(POSITION_PRICE_OPEN);x.anchor_ok=HG6Cents(x.price,x.price_cents);if(!MathIsValidNumber(x.price)||x.price<=0||!HG6VolumeUnits(x.volume,x.units)||x.identifier==0||x.time_ms<=0)x.ambiguous=true;
 }
 for(int i=OrdersTotal()-1;i>=0;i--){ulong t=OrderGetTicket(i);if(t==0||!OrderSelect(t))return false;if(OrderGetString(ORDER_SYMBOL)!=sym)continue;if((ulong)OrderGetInteger(ORDER_MAGIC)==magic){if(x.pending)x.ambiguous=true;x.pending=true;x.pending_ticket=t;}else x.foreign=true;}
 return true;
}
bool HG6VolumeAllowed(const string sym,double volume){double minv=SymbolInfoDouble(sym,SYMBOL_VOLUME_MIN),maxv=SymbolInfoDouble(sym,SYMBOL_VOLUME_MAX),step=SymbolInfoDouble(sym,SYMBOL_VOLUME_STEP);if(!MathIsValidNumber(volume)||step<=0.0||volume<minv-1e-9||volume>maxv+1e-9)return false;double k=(volume-minv)/step;return MathAbs(k-MathRound(k))<1e-7;}
// SECTION B1A: actual account facts, independent of the twelve research books.
struct HG6AccountFacts {double balance,equity,margin,free_margin,level,call,stop;long stop_mode,leverage;};
bool HG6ReadAccount(HG6AccountFacts &a){
 a.balance=AccountInfoDouble(ACCOUNT_BALANCE);a.equity=AccountInfoDouble(ACCOUNT_EQUITY);a.margin=AccountInfoDouble(ACCOUNT_MARGIN);a.free_margin=AccountInfoDouble(ACCOUNT_MARGIN_FREE);a.level=AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);a.call=AccountInfoDouble(ACCOUNT_MARGIN_SO_CALL);a.stop=AccountInfoDouble(ACCOUNT_MARGIN_SO_SO);a.stop_mode=AccountInfoInteger(ACCOUNT_MARGIN_SO_MODE);a.leverage=AccountInfoInteger(ACCOUNT_LEVERAGE);
 return MathIsValidNumber(a.balance)&&MathIsValidNumber(a.equity)&&MathIsValidNumber(a.margin)&&MathIsValidNumber(a.free_margin)&&MathIsValidNumber(a.level)&&MathIsValidNumber(a.call)&&MathIsValidNumber(a.stop)&&a.margin>=0&&a.call>=0&&a.stop>=0&&a.leverage>0;
}
bool HG6AdmissionAccount(const HG6AccountFacts &a){return a.stop_mode==ACCOUNT_STOPOUT_MODE_PERCENT&&a.balance>0&&a.equity>0&&a.free_margin>=0&&(a.margin==0||a.level>MathMax(a.call,a.stop));}
bool HG6AccountUrgent(const HG6AccountFacts &a){return a.equity<=0||(a.margin>0&&a.stop_mode==ACCOUNT_STOPOUT_MODE_PERCENT&&a.level<=a.stop);}
// SECTION B1B: each broker deal is accounted once, keyed by unique ticket. A
// position ledger is bounded and reset only after authoritative flat confirmation.
#define HG6_MAX_POSITION_DEALS 1024
struct HG6ActualLedger {
 long position,last_closed,closed;int count;long tickets[HG6_MAX_POSITION_DEALS];double costs[HG6_MAX_POSITION_DEALS][4];
 double profit,commission,swap,fee,total_profit,total_commission,total_swap,total_fee;
 void Reset(){position=last_closed=closed=0;count=0;profit=commission=swap=fee=total_profit=total_commission=total_swap=total_fee=0;for(int i=0;i<HG6_MAX_POSITION_DEALS;i++)tickets[i]=0;}
 bool Apply(long pos,long ticket,double p,double c,double s,double f){
  if(pos<=0||ticket<=0||!MathIsValidNumber(p)||!MathIsValidNumber(c)||!MathIsValidNumber(s)||!MathIsValidNumber(f)||pos==last_closed||(position!=0&&position!=pos))return false;
  for(int i=0;i<count;i++)if(tickets[i]==ticket)return costs[i][0]==p&&costs[i][1]==c&&costs[i][2]==s&&costs[i][3]==f;
  if(count>=HG6_MAX_POSITION_DEALS)return false;position=pos;tickets[count]=ticket;costs[count][0]=p;costs[count][1]=c;costs[count][2]=s;costs[count][3]=f;count++;profit+=p;commission+=c;swap+=s;fee+=f;return MathIsValidNumber(profit+commission+swap+fee);
 }
 bool Flat(long pos){if(pos==last_closed&&position==0)return true;if(pos<=0||position!=pos||count<=0)return false;total_profit+=profit;total_commission+=commission;total_swap+=swap;total_fee+=fee;last_closed=pos;closed++;position=0;count=0;profit=commission=swap=fee=0;return MathIsValidNumber(total_profit+total_commission+total_swap+total_fee);}
 bool StateFields(HG5StateCodec &c){if(!c.I64(position)||!c.I64(last_closed)||!c.I64(closed)||!c.I32(count)||count<0||count>HG6_MAX_POSITION_DEALS||position<0||last_closed<0||closed<0||(position==0)!=(count==0))return false;for(int i=0;i<count;i++){if(!c.I64(tickets[i])||tickets[i]<=0)return false;for(int k=0;k<4;k++)if(!c.F64(costs[i][k])||!MathIsValidNumber(costs[i][k]))return false;for(int j=0;j<i;j++)if(tickets[j]==tickets[i])return false;}return c.F64(profit)&&c.F64(commission)&&c.F64(swap)&&c.F64(fee)&&c.F64(total_profit)&&c.F64(total_commission)&&c.F64(total_swap)&&c.F64(total_fee)&&MathIsValidNumber(profit+commission+swap+fee+total_profit+total_commission+total_swap+total_fee);}
};
// SECTION B2: persistent one-attempt order intent; strict FOK candidate until other fill modes certified.
// Unknown/partial outcomes stay locked. Terminal receipt or bool return never means filled.
struct HG6TradeIntent {long seq,proposal,created_ms,position_id,order_id,deal_id;int kind,side,units,state,filled_units,retcode;bool cancel_attempt;};
class HG6Broker {
 string sym;ulong magic;HG6Store store;HG6TradeIntent intent;HG6ActualLedger ledger;HG6CommitLink link;HG5StateCodec encode_scratch;bool ready,fault,authorized;long sequence;
 bool Encode(uchar &out[]){int version=4;if(!encode_scratch.BeginWrite()||!encode_scratch.I32(version)||!encode_scratch.I64(sequence)||!encode_scratch.I64(intent.seq)||!encode_scratch.I64(intent.proposal)||!encode_scratch.I64(intent.created_ms)||!encode_scratch.I64(intent.position_id)||!encode_scratch.I64(intent.order_id)||!encode_scratch.I64(intent.deal_id)||!encode_scratch.I32(intent.kind)||!encode_scratch.I32(intent.side)||!encode_scratch.I32(intent.units)||!encode_scratch.I32(intent.state)||!encode_scratch.I32(intent.filled_units)||!encode_scratch.I32(intent.retcode)||!encode_scratch.Flag(intent.cancel_attempt)||!ledger.StateFields(encode_scratch)||!link.StateFields(encode_scratch))return false;return encode_scratch.Finish(out);}
 bool Decode(const uchar &in[]){HG5StateCodec c;int version=0;if(!c.BeginRead(in)||!c.I32(version)||version!=4||!c.I64(sequence)||!c.I64(intent.seq)||!c.I64(intent.proposal)||!c.I64(intent.created_ms)||!c.I64(intent.position_id)||!c.I64(intent.order_id)||!c.I64(intent.deal_id)||!c.I32(intent.kind)||!c.I32(intent.side)||!c.I32(intent.units)||!c.I32(intent.state)||!c.I32(intent.filled_units)||!c.I32(intent.retcode)||!c.Flag(intent.cancel_attempt)||!ledger.StateFields(c)||!link.StateFields(c)||!c.Done())return false;return sequence>=0&&intent.seq>=0&&intent.seq<=sequence&&intent.state>=0&&intent.state<=HG5_INTENT_FROZEN&&intent.filled_units>=0&&intent.filled_units<=intent.units&&(!intent.state||(intent.seq==sequence&&intent.units>0&&(intent.kind==1||intent.kind==2)&&(intent.side==1||intent.side==-1)&&intent.created_ms>0));}
 bool Persist(){uchar b[];if(!Encode(b)||!store.Save(b)){fault=true;return false;}return true;}
 void ResetIntent(){intent.seq=sequence;intent.proposal=-1;intent.created_ms=intent.position_id=intent.order_id=intent.deal_id=0;intent.kind=intent.side=intent.units=intent.state=intent.filled_units=intent.retcode=0;intent.cancel_attempt=false;}
 public:
 HG6Broker(){ready=fault=authorized=false;sequence=0;ledger.Reset();ResetIntent();}
 bool Init(string symbol,ulong mg,string path,const uchar &identity[],bool permit){
  if(ready||mg==0)return false;sym=symbol;magic=mg;authorized=permit&&HG6_TESTER_EXECUTION_ENABLED==1&&MQLInfoInteger(MQL_TESTER)!=0;
  if(!store.Init(path,identity))return false;uchar b[];int load=store.Load(b);if(load<0||(load>0&&!Decode(b)))return false;
  if(load==0&&!Persist())return false;if(!store.Healthy()||intent.state==HG5_INTENT_FROZEN)fault=true;
  ready=true;return true;
 }
 bool Ready()const{return ready&&!fault&&store.Healthy()&&!Outstanding();}
 bool CheckLink(long applied,long generation)const{return ready&&!fault&&link.Check(sequence,Outstanding(),Resolved(),applied,generation);}
 long Sequence()const{return sequence;}
 bool RescueMode()const{return link.Rescue();}
 bool EnterRescue(){if(!ready||fault)return false;if(link.Rescue())return true;link.Quarantine();return Persist();}
 bool IntegrityHealthy()const{return ready&&!fault&&store.Healthy();}
 bool Outstanding()const{return intent.state!=0;}
 long Proposal()const{return intent.proposal;}
 long PositionId()const{return intent.position_id;}
 int IntentKind()const{return intent.kind;}
 int FilledUnits()const{return intent.filled_units;}
 long CreatedMs()const{return intent.created_ms;}
 long ActiveLedgerPosition()const{return ledger.position;}
 double ActualNet()const{return ledger.total_profit+ledger.total_commission+ledger.total_swap+ledger.total_fee+ledger.profit+ledger.commission+ledger.swap+ledger.fee;}
 long ClosedPositions()const{return ledger.closed;}
 // SECTION B3: recover missing order identifier only from unique matching broker evidence.
 bool CorrelateOrder(){
  if(intent.order_id>0)return true;long match=0;string comment="HG6-"+IntegerToString(intent.seq);
  int n=HistoryOrdersTotal();if(n<0||n>100000)return false;
  for(int i=0;i<n;i++){ulong t=HistoryOrderGetTicket(i);if(!t)return false;if(HistoryOrderGetString(t,ORDER_SYMBOL)!=sym||(ulong)HistoryOrderGetInteger(t,ORDER_MAGIC)!=magic||HistoryOrderGetString(t,ORDER_COMMENT)!=comment)continue;
   long tm=HistoryOrderGetInteger(t,ORDER_TIME_SETUP_MSC),type=HistoryOrderGetInteger(t,ORDER_TYPE);if(tm<intent.created_ms-1000||tm>(long)TimeCurrent()*1000+1000||(intent.kind==2&&HistoryOrderGetInteger(t,ORDER_POSITION_ID)!=intent.position_id)||type!=(intent.side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL))continue;if(match&&match!=(long)t){fault=true;return false;}match=(long)t;}
  for(int i=0;i<OrdersTotal();i++){ulong t=OrderGetTicket(i);if(!t||!OrderSelect(t))return false;if(OrderGetString(ORDER_SYMBOL)!=sym||(ulong)OrderGetInteger(ORDER_MAGIC)!=magic||OrderGetString(ORDER_COMMENT)!=comment)continue;
   if(OrderGetInteger(ORDER_TIME_SETUP_MSC)<intent.created_ms-1000||OrderGetInteger(ORDER_TIME_SETUP_MSC)>(long)TimeCurrent()*1000+1000||(intent.kind==2&&OrderGetInteger(ORDER_POSITION_ID)!=intent.position_id)||OrderGetInteger(ORDER_TYPE)!=(intent.side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL))continue;if(match&&match!=(long)t){fault=true;return false;}match=(long)t;}
  if(!match)return false;intent.order_id=match;return Persist();
 }
 bool ExplicitRejection()const{return intent.retcode==TRADE_RETCODE_REQUOTE||intent.retcode==TRADE_RETCODE_PRICE_CHANGED||intent.retcode==TRADE_RETCODE_PRICE_OFF||intent.retcode==TRADE_RETCODE_REJECT||intent.retcode==TRADE_RETCODE_INVALID||intent.retcode==TRADE_RETCODE_INVALID_VOLUME||intent.retcode==TRADE_RETCODE_INVALID_PRICE||intent.retcode==TRADE_RETCODE_TRADE_DISABLED||intent.retcode==TRADE_RETCODE_MARKET_CLOSED||intent.retcode==TRADE_RETCODE_NO_MONEY||intent.retcode==TRADE_RETCODE_INVALID_FILL;}
 bool Reconcile(const HG6Exposure &x){
  if(!ready||fault)return false;if(x.foreign||x.ambiguous)return false;if(!Outstanding())return !x.pending;
  // A locally cancelled entry was explicitly never submitted. An unexpected
  // exposure still requires intervention; no broker outcome is invented.
  if(intent.retcode==HG6_LOCAL_NOT_SENT)return intent.state==HG5_INTENT_REJECTED&&intent.filled_units==0&&intent.order_id==0&&intent.deal_id==0&&!x.pending&&((intent.kind==1&&!x.ticket)||(intent.kind==2&&(!x.ticket||(x.identifier==(ulong)intent.position_id&&x.units==intent.units&&x.side==-intent.side))));
  if(!HistorySelect((datetime)(intent.created_ms/1000-60),TimeCurrent()+60))return false;
  if(!CorrelateOrder()){
   if(!fault&&intent.filled_units==0&&intent.deal_id==0&&ExplicitRejection()&&!x.pending&&((intent.kind==1&&x.ticket==0)||(intent.kind==2&&x.identifier==(ulong)intent.position_id&&x.units==intent.units))){intent.state=HG5_INTENT_REJECTED;return Persist();}return false;}
  double total=0,weighted=0;long pos_id=0,first_ms=0;long seen[];int n=HistoryDealsTotal();if(n<0||n>100000)return false;
  for(int i=0;i<n;i++){ulong d=HistoryDealGetTicket(i);if(!d)return false;if(HistoryDealGetInteger(d,DEAL_ORDER)!=intent.order_id)continue;
   bool duplicate=false;for(int k=0;k<ArraySize(seen);k++)if(seen[k]==(long)d)duplicate=true;if(duplicate)continue;
   int z=ArraySize(seen);if(z>=HG6_MAX_POSITION_DEALS||ArrayResize(seen,z+1)!=z+1){fault=true;return false;}seen[z]=(long)d;
   if(HistoryDealGetString(d,DEAL_SYMBOL)!=sym||(ulong)HistoryDealGetInteger(d,DEAL_MAGIC)!=magic){fault=true;return false;}
   long e=HistoryDealGetInteger(d,DEAL_ENTRY),type=HistoryDealGetInteger(d,DEAL_TYPE),pos=HistoryDealGetInteger(d,DEAL_POSITION_ID);
   if((intent.kind==1&&e!=DEAL_ENTRY_IN)||(intent.kind==2&&(e!=DEAL_ENTRY_OUT||pos!=intent.position_id))||(intent.side>0&&type!=DEAL_TYPE_BUY)||(intent.side<0&&type!=DEAL_TYPE_SELL)){fault=true;return false;}
   long tm=HistoryDealGetInteger(d,DEAL_TIME_MSC);double v=HistoryDealGetDouble(d,DEAL_VOLUME),px=HistoryDealGetDouble(d,DEAL_PRICE);
   if(tm<=0||pos<=0||(pos_id!=0&&pos_id!=pos)||!MathIsValidNumber(v)||v<=0||!MathIsValidNumber(px)||px<=0){fault=true;return false;}pos_id=pos;if(first_ms==0||tm<first_ms)first_ms=tm;total+=v;weighted+=v*px;
  }
  int units=0;if(total>0&&!HG6VolumeUnits(total,units)){fault=true;return false;}if(units>intent.units||units<intent.filled_units){fault=true;return false;}
  // Read order terminal state only AFTER enumerating deals; pending order may still grow.
  bool terminal=false;if(HistoryOrderSelect((ulong)intent.order_id)){long st=HistoryOrderGetInteger((ulong)intent.order_id,ORDER_STATE);terminal=st==ORDER_STATE_FILLED||st==ORDER_STATE_REJECTED||st==ORDER_STATE_CANCELED||st==ORDER_STATE_EXPIRED;}
  if(x.pending||(!terminal&&units<intent.units)){if(units>0&&(intent.state!=HG5_INTENT_PARTIAL||units!=intent.filled_units)){intent.state=HG5_INTENT_PARTIAL;intent.filled_units=units;if(!Persist())return false;}return false;}
  if(units==0){if(terminal&&((intent.kind==1&&x.ticket==0)||(intent.kind==2&&x.identifier==(ulong)intent.position_id&&x.units==intent.units))){intent.state=HG5_INTENT_REJECTED;return Persist();}return false;}
  if(intent.kind==1){if(x.ticket==0||x.identifier!=(ulong)pos_id||x.time_ms!=first_ms||x.side!=intent.side||x.units!=units||MathAbs(weighted/total-x.price)>1e-7)return false;}
  if(intent.kind==2){int remaining=intent.units-units;if((remaining==0&&x.ticket!=0)||(remaining>0&&(x.ticket==0||x.identifier!=(ulong)intent.position_id||x.units!=remaining||x.side!=-intent.side)))return false;}
  // Reconcile all unique matching deals and costs; repeat scans are idempotent.
  // A final close moves the position ledger to realized totals exactly once.
  if(intent.state==HG5_INTENT_FILLED){if(units!=intent.filled_units)return false;if(ledger.position==pos_id){for(int i=0;i<ArraySize(seen);i++){ulong d=(ulong)seen[i];if(!ledger.Apply(pos_id,seen[i],HistoryDealGetDouble(d,DEAL_PROFIT),HistoryDealGetDouble(d,DEAL_COMMISSION),HistoryDealGetDouble(d,DEAL_SWAP),HistoryDealGetDouble(d,DEAL_FEE))){fault=true;return false;}}}return true;}
  for(int i=0;i<ArraySize(seen);i++){ulong d=(ulong)seen[i];if(!ledger.Apply(pos_id,seen[i],HistoryDealGetDouble(d,DEAL_PROFIT),HistoryDealGetDouble(d,DEAL_COMMISSION),HistoryDealGetDouble(d,DEAL_SWAP),HistoryDealGetDouble(d,DEAL_FEE))){fault=true;return false;}}
  if(intent.kind==2&&units==intent.units&&!ledger.Flat(pos_id)){fault=true;return false;}
  intent.filled_units=units;intent.state=HG5_INTENT_FILLED;return Persist();
 }
 // Cancellation applies only to the known, owned order and is attempted once durably.
 bool CancelPending(const HG6Exposure &x){
  if(!authorized||!MQLInfoInteger(MQL_TESTER)||!ready||fault||!Outstanding()||!x.pending||x.foreign||x.ambiguous||intent.order_id<=0||x.pending_ticket!=(ulong)intent.order_id||intent.cancel_attempt)return false;
  HG6Exposure fresh;if(!HG6ExposureRead(sym,magic,fresh)||fresh.foreign||fresh.ambiguous||!fresh.pending||fresh.pending_ticket!=x.pending_ticket)return false;
  intent.cancel_attempt=true;if(!Persist())return false;MqlTradeRequest req={};MqlTradeResult result={};req.action=TRADE_ACTION_REMOVE;req.order=x.pending_ticket;req.symbol=sym;req.magic=magic;return OrderSend(req,result);
 }
 // Unexpected broker-side liquidation: verify complete position history before booking flat.
 bool ExternalFlat(long pos){
  if(!ready||fault||Outstanding()||pos<=0||!HistorySelectByPosition((ulong)pos))return false;
  if(ledger.last_closed==pos&&ledger.position==0)return true;if(ledger.position!=pos)return false;
  double in_vol=0,out_vol=0;long seen[];int n=HistoryDealsTotal();if(n<1||n>HG6_MAX_POSITION_DEALS)return false;
  for(int i=0;i<n;i++){ulong d=HistoryDealGetTicket(i);if(!d)return false;bool dup=false;for(int k=0;k<ArraySize(seen);k++)if(seen[k]==(long)d)dup=true;if(dup)continue;int j=ArraySize(seen);if(ArrayResize(seen,j+1)!=j+1)return false;seen[j]=(long)d;
   if(HistoryDealGetInteger(d,DEAL_POSITION_ID)!=pos||HistoryDealGetString(d,DEAL_SYMBOL)!=sym)return false;
   long e=HistoryDealGetInteger(d,DEAL_ENTRY);double v=HistoryDealGetDouble(d,DEAL_VOLUME);if(!MathIsValidNumber(v)||v<=0)return false;if(e==DEAL_ENTRY_IN){if((ulong)HistoryDealGetInteger(d,DEAL_MAGIC)!=magic)return false;in_vol+=v;}else if(e==DEAL_ENTRY_OUT)out_vol+=v;else return false;
  }
  if(in_vol<=0||MathAbs(in_vol-out_vol)>1e-7)return false;
  for(int i=0;i<ArraySize(seen);i++){ulong d=(ulong)seen[i];if(!ledger.Apply(pos,seen[i],HistoryDealGetDouble(d,DEAL_PROFIT),HistoryDealGetDouble(d,DEAL_COMMISSION),HistoryDealGetDouble(d,DEAL_SWAP),HistoryDealGetDouble(d,DEAL_FEE))){fault=true;return false;}}
  if(!ledger.Flat(pos)){fault=true;return false;}return Persist();
 }
 bool Resolved()const{return intent.state==HG5_INTENT_FILLED||intent.state==HG5_INTENT_REJECTED;}
 bool Filled()const{return intent.state==HG5_INTENT_FILLED;}
 // Release is called after corresponding core/exposure state has been durably saved.
 bool ReleaseApplied(long applied,long generation){if(!Resolved()||!link.Commit(intent.seq,applied,generation))return false;ResetIntent();return Persist();}
 bool ReleaseRescue(){if(!Resolved()||!link.RescueRelease(intent.seq))return false;ResetIntent();return Persist();}
 // SECTION B4: explicit Strategy Tester only; never send on terminal charts.
 bool Submit(int kind,long proposal,int side,int units,const MqlTick &tick,const HG6Exposure &x,ulong deviation,ulong deadline_us=0){
  if(!authorized||HG6_TESTER_EXECUTION_ENABLED!=1||!MQLInfoInteger(MQL_TESTER)||!Ready()||Outstanding()||(kind!=1&&kind!=2)||(side!=1&&side!=-1)||units<=0||x.foreign||x.ambiguous||x.pending||!TerminalInfoInteger(TERMINAL_CONNECTED)||!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)||!MQLInfoInteger(MQL_TRADE_ALLOWED)||!AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)||!AccountInfoInteger(ACCOUNT_TRADE_EXPERT))return false;
  if((kind==1&&(x.ticket!=0||link.Rescue()))||(kind==2&&(x.ticket==0||units!=x.units||side!=-x.side)))return false;
  HG6Exposure fresh;if(!HG6ExposureRead(sym,magic,fresh)||fresh.foreign||fresh.ambiguous||fresh.pending||fresh.ticket!=x.ticket||fresh.identifier!=x.identifier||fresh.units!=x.units||fresh.side!=x.side)return false;
  MqlTick current;if(!SymbolInfoTick(sym,current)||!HG6TickEqual(current,tick))return false;
  if(AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING||!HG6BrokerSpec(sym)||!(SymbolInfoInteger(sym,SYMBOL_FILLING_MODE)&SYMBOL_FILLING_FOK))return false;
  double vol=(double)units/100.;if(!HG6VolumeAllowed(sym,vol))return false;long mode=SymbolInfoInteger(sym,SYMBOL_TRADE_MODE);
  if(mode==SYMBOL_TRADE_MODE_DISABLED||(kind==1&&(mode==SYMBOL_TRADE_MODE_CLOSEONLY||(side>0&&mode==SYMBOL_TRADE_MODE_SHORTONLY)||(side<0&&mode==SYMBOL_TRADE_MODE_LONGONLY))))return false;
  MqlTradeRequest req={};MqlTradeCheckResult chk={};MqlTradeResult result={};req.action=TRADE_ACTION_DEAL;req.symbol=sym;req.magic=magic;req.volume=vol;req.type=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;req.price=side>0?tick.ask:tick.bid;req.deviation=deviation;req.type_filling=ORDER_FILLING_FOK;req.position=kind==2?x.ticket:0;
  if(kind==1){HG6AccountFacts facts;if(!HG6ReadAccount(facts)||!HG6AdmissionAccount(facts))return false;double margin=0;if(!OrderCalcMargin(req.type,sym,vol,req.price,margin)||!MathIsValidNumber(margin)||margin<=0||margin>AccountInfoDouble(ACCOUNT_MARGIN_FREE))return false;}
  req.comment="HG6-"+IntegerToString(sequence+1);if(!OrderCheck(req,chk)||(chk.retcode!=0&&chk.retcode!=TRADE_RETCODE_DONE)||(kind==1&&(!MathIsValidNumber(chk.margin_free)||chk.margin_free<0||!MathIsValidNumber(chk.equity)||chk.equity<=0)))return false;
  sequence++;intent.seq=sequence;intent.proposal=proposal;intent.created_ms=tick.time_msc;intent.position_id=(long)x.identifier;intent.order_id=intent.deal_id=0;intent.kind=kind;intent.side=side;intent.units=units;intent.state=HG5_INTENT_UNKNOWN;intent.filled_units=intent.retcode=0;intent.cancel_attempt=false;
  if(!Persist())return false; // before any network call; no resend after a crash.
  // A quote or budget can become stale during OrderCheck / durable I/O. Only
  // a positively known NO-SEND is released locally. A crash before recording
  // this outcome remains UNKNOWN and cannot be retried automatically.
  MqlTick after;HG6Exposure after_x;
  if((kind==1&&deadline_us>0&&GetMicrosecondCount()>=deadline_us)||!SymbolInfoTick(sym,after)||!HG6TickEqual(after,tick)||!HG6ExposureRead(sym,magic,after_x)||after_x.ticket!=x.ticket||after_x.identifier!=x.identifier||after_x.units!=x.units||after_x.side!=x.side||after_x.pending||after_x.foreign||after_x.ambiguous||!TerminalInfoInteger(TERMINAL_CONNECTED)||!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)||!MQLInfoInteger(MQL_TRADE_ALLOWED)||!AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)||!AccountInfoInteger(ACCOUNT_TRADE_EXPERT)){
   intent.retcode=HG6_LOCAL_NOT_SENT;intent.state=HG5_INTENT_REJECTED;Persist();return false;
  }
  ResetLastError();bool sent=OrderSend(req,result);intent.order_id=(long)result.order;intent.deal_id=(long)result.deal;intent.retcode=(int)result.retcode;
  if(intent.order_id==0&&intent.deal_id>0&&HistoryDealSelect((ulong)intent.deal_id))intent.order_id=HistoryDealGetInteger((ulong)intent.deal_id,DEAL_ORDER);
  PrintFormat("HG6 order attempt seq=%I64d sent=%d retcode=%u order=%I64u deal=%I64u error=%d",sequence,(int)sent,result.retcode,result.order,result.deal,GetLastError());
  if(!Persist())return false;return sent;
 }
};
#endif
