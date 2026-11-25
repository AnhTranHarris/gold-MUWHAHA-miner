#ifndef HG6_BROKER_MQH
#define HG6_BROKER_MQH
#include "HG6Storage.mqh"
#include "HG6Feed.mqh"
#include "HG5OperationalGate.mqh"
// SECTION B1: actual broker facts. No modeled trade is ever booked as a real fill.
// This build is intentionally locked for native QC; user input alone cannot send orders.
#define HG6_EXECUTION_RELEASED 0
struct HG6Exposure {ulong ticket,identifier;long time_ms;int side,price_cents,units;double volume;bool foreign,pending,ambiguous;};
bool HG6VolumeUnits(double v,int &units){if(!MathIsValidNumber(v)||v<=0||v>100.0)return false;double q=v*100.0,r=MathRound(q);if(MathAbs(q-r)>0.000001)return false;units=(int)r;return units>0;}
bool HG6BrokerSpec(const string sym){
 return AccountInfoString(ACCOUNT_CURRENCY)=="USD"&&AccountInfoInteger(ACCOUNT_LEVERAGE)>0&&
  MathAbs(SymbolInfoDouble(sym,SYMBOL_TRADE_CONTRACT_SIZE)-100.0)<1e-8&&
  MathAbs(SymbolInfoDouble(sym,SYMBOL_TRADE_TICK_SIZE)-0.01)<1e-10&&SymbolInfoInteger(sym,SYMBOL_DIGITS)>=2;
}
bool HG6ExposureRead(const string sym,ulong magic,HG6Exposure &x){
 x.ticket=0;x.identifier=0;x.time_ms=0;x.side=x.price_cents=x.units=0;x.volume=0;x.foreign=x.pending=x.ambiguous=false;
 for(int i=PositionsTotal()-1;i>=0;i--){ulong t=PositionGetTicket(i);if(t==0||!PositionSelectByTicket(t))return false;if(PositionGetString(POSITION_SYMBOL)!=sym)continue;
  if((ulong)PositionGetInteger(POSITION_MAGIC)!=magic){x.foreign=true;continue;}if(x.ticket!=0){x.ambiguous=true;continue;}
  x.ticket=t;x.identifier=(ulong)PositionGetInteger(POSITION_IDENTIFIER);x.time_ms=PositionGetInteger(POSITION_TIME_MSC);
  long type=PositionGetInteger(POSITION_TYPE);if(type!=POSITION_TYPE_BUY&&type!=POSITION_TYPE_SELL)return false;x.side=type==POSITION_TYPE_BUY?1:-1;x.volume=PositionGetDouble(POSITION_VOLUME);
  if(!HG6Cents(PositionGetDouble(POSITION_PRICE_OPEN),x.price_cents)||!HG6VolumeUnits(x.volume,x.units)||x.identifier==0||x.time_ms<=0)x.ambiguous=true;
 }
 for(int i=OrdersTotal()-1;i>=0;i--){ulong t=OrderGetTicket(i);if(t==0||!OrderSelect(t))return false;if(OrderGetString(ORDER_SYMBOL)!=sym)continue;if((ulong)OrderGetInteger(ORDER_MAGIC)==magic)x.pending=true;else x.foreign=true;}
 return true;
}
bool HG6VolumeAllowed(const string sym,double volume){double minv=SymbolInfoDouble(sym,SYMBOL_VOLUME_MIN),maxv=SymbolInfoDouble(sym,SYMBOL_VOLUME_MAX),step=SymbolInfoDouble(sym,SYMBOL_VOLUME_STEP);if(!MathIsValidNumber(volume)||step<=0.0||volume<minv-1e-9||volume>maxv+1e-9)return false;double k=(volume-minv)/step;return MathAbs(k-MathRound(k))<1e-7;}
// SECTION B2: persistent one-attempt order intent; strict FOK candidate until other fill modes certified.
// Unknown/partial outcomes stay locked. Terminal receipt or bool return never means filled.
struct HG6TradeIntent {long seq,proposal,created_ms,position_id,order_id,deal_id;int kind,side,units,state;};
class HG6Broker {
 string sym;ulong magic;HG6Store store;HG6TradeIntent intent;bool ready,fault,authorized;long sequence;
 bool Encode(uchar &out[]){HG5StateCodec c;int version=1;if(!c.BeginWrite()||!c.I32(version)||!c.I64(sequence)||!c.I64(intent.seq)||!c.I64(intent.proposal)||!c.I64(intent.created_ms)||!c.I64(intent.position_id)||!c.I64(intent.order_id)||!c.I64(intent.deal_id)||!c.I32(intent.kind)||!c.I32(intent.side)||!c.I32(intent.units)||!c.I32(intent.state))return false;return c.Finish(out);}
 bool Decode(const uchar &in[]){HG5StateCodec c;int version=0;if(!c.BeginRead(in)||!c.I32(version)||version!=1||!c.I64(sequence)||!c.I64(intent.seq)||!c.I64(intent.proposal)||!c.I64(intent.created_ms)||!c.I64(intent.position_id)||!c.I64(intent.order_id)||!c.I64(intent.deal_id)||!c.I32(intent.kind)||!c.I32(intent.side)||!c.I32(intent.units)||!c.I32(intent.state)||!c.Done())return false;return sequence>=0&&intent.seq>=0&&intent.seq<=sequence&&intent.state>=0&&intent.state<=HG5_INTENT_FROZEN;}
 bool Persist(){uchar b[];if(!Encode(b)||!store.Save(b)){fault=true;return false;}return true;}
 void ResetIntent(){intent.seq=sequence;intent.proposal=-1;intent.created_ms=intent.position_id=intent.order_id=intent.deal_id=0;intent.kind=intent.side=intent.units=intent.state=0;}
 public:
 HG6Broker(){ready=fault=authorized=false;sequence=0;ResetIntent();}
 bool Init(string symbol,ulong mg,string path,const uchar &identity[],bool permit){
  if(ready||mg==0)return false;sym=symbol;magic=mg;authorized=permit&&HG6_EXECUTION_RELEASED==1;
  if(!store.Init(path,identity))return false;uchar b[];int load=store.Load(b);if(load<0||(load>0&&!Decode(b)))return false;
  if(load==0&&!Persist())return false;if(!store.Healthy()||intent.state==HG5_INTENT_UNKNOWN||intent.state==HG5_INTENT_PARTIAL||intent.state==HG5_INTENT_ACKED||intent.state==HG5_INTENT_FROZEN)fault=true;
  ready=true;return true;
 }
 bool Ready()const{return ready&&!fault&&store.Healthy();}
 bool Outstanding()const{return intent.state!=0;}
 long Proposal()const{return intent.proposal;}
 long PositionId()const{return intent.position_id;}
 int IntentKind()const{return intent.kind;}
 // SECTION B3: authoritative history scan keyed by known broker order identifier.
 // No unproven "absence" conclusion. Reconciliation is bounded to this outstanding order.
 bool Reconcile(const HG6Exposure &x){
  if(!ready)return false;if(x.foreign||x.ambiguous){fault=true;return false;}if(!Outstanding())return !x.pending;
  if(intent.order_id<=0){fault=true;return false;}
  if(!HistorySelect((datetime)(intent.created_ms/1000-60),TimeCurrent()+60)){fault=true;return false;}
  double total=0,weighted=0;long pos_id=0,first_ms=0;int n=HistoryDealsTotal();if(n<0||n>100000){fault=true;return false;}
  for(int i=0;i<n;i++){ulong d=HistoryDealGetTicket(i);if(d==0){fault=true;return false;}if(HistoryDealGetInteger(d,DEAL_ORDER)!=intent.order_id)continue;
   if(HistoryDealGetString(d,DEAL_SYMBOL)!=sym||(ulong)HistoryDealGetInteger(d,DEAL_MAGIC)!=magic){fault=true;return false;}
   long e=HistoryDealGetInteger(d,DEAL_ENTRY),type=HistoryDealGetInteger(d,DEAL_TYPE),pos=HistoryDealGetInteger(d,DEAL_POSITION_ID);
   if((intent.kind==1&&e!=DEAL_ENTRY_IN)||(intent.kind==2&&(e!=DEAL_ENTRY_OUT||pos!=intent.position_id))||(intent.side>0&&type!=DEAL_TYPE_BUY)||(intent.side<0&&type!=DEAL_TYPE_SELL)){fault=true;return false;}
   long tm=HistoryDealGetInteger(d,DEAL_TIME_MSC);if(tm<=0||pos<=0||(pos_id!=0&&pos_id!=pos)){fault=true;return false;}pos_id=pos;if(first_ms==0||tm<first_ms)first_ms=tm;double v=HistoryDealGetDouble(d,DEAL_VOLUME);if(!MathIsValidNumber(v)||v<=0){fault=true;return false;}total+=v;weighted+=v*HistoryDealGetDouble(d,DEAL_PRICE);
  }
  int units=0;if(total>0&&!HG6VolumeUnits(total,units)){fault=true;return false;}if(units>intent.units){fault=true;return false;}
  if(units==intent.units&&units>0){
   if(intent.kind==1){if(x.ticket==0||x.identifier!=(ulong)pos_id||x.time_ms!=first_ms||x.side!=intent.side||x.units!=units||MathAbs(weighted/total-(double)x.price_cents/100.0)>1e-7){fault=true;return false;}}
   if(intent.kind==2&&x.ticket!=0){fault=true;return false;}
   if(x.pending){fault=true;return false;}intent.state=HG5_INTENT_FILLED;if(!Persist())return false;return true;
  }
  if(units>0){intent.state=HG5_INTENT_PARTIAL;Persist();fault=true;return false;}
  // Explicit terminal history state proves rejection/cancel/expiry only if no matching exposure/order remains.
  if(HistoryOrderSelect((ulong)intent.order_id)){
   long st=HistoryOrderGetInteger((ulong)intent.order_id,ORDER_STATE);
   if((st==ORDER_STATE_REJECTED||st==ORDER_STATE_CANCELED||st==ORDER_STATE_EXPIRED)&&!x.pending&&((intent.kind==1&&x.ticket==0)||(intent.kind==2&&x.identifier==(ulong)intent.position_id))){intent.state=HG5_INTENT_REJECTED;return Persist();}
  }
  return false;
 }
 bool Resolved()const{return intent.state==HG5_INTENT_FILLED||intent.state==HG5_INTENT_REJECTED;}
 bool Filled()const{return intent.state==HG5_INTENT_FILLED;}
 // Release is called after corresponding core/exposure state has been durably saved.
 bool Release(){if(!Resolved())return false;ResetIntent();return Persist();}
 // SECTION B4: only executable in a future, separately approved DEMO build.
 bool Submit(int kind,long proposal,int side,int units,const MqlTick &tick,const HG6Exposure &x,ulong deviation){
  if(!authorized||HG6_EXECUTION_RELEASED!=1||!Ready()||Outstanding()||(kind!=1&&kind!=2)||(side!=1&&side!=-1)||units<=0||x.foreign||x.ambiguous||x.pending||!TerminalInfoInteger(TERMINAL_CONNECTED)||!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)||!MQLInfoInteger(MQL_TRADE_ALLOWED)||AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO||!AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)||!AccountInfoInteger(ACCOUNT_TRADE_EXPERT))return false;
  if((kind==1&&x.ticket!=0)||(kind==2&&(x.ticket==0||units!=x.units||side!=-x.side)))return false;
  if(AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING||!HG6BrokerSpec(sym)||!(SymbolInfoInteger(sym,SYMBOL_FILLING_MODE)&SYMBOL_FILLING_FOK))return false;
  double vol=(double)units/100.;if(!HG6VolumeAllowed(sym,vol))return false;long mode=SymbolInfoInteger(sym,SYMBOL_TRADE_MODE);
  if(mode==SYMBOL_TRADE_MODE_DISABLED||(kind==1&&(mode==SYMBOL_TRADE_MODE_CLOSEONLY||(side>0&&mode==SYMBOL_TRADE_MODE_SHORTONLY)||(side<0&&mode==SYMBOL_TRADE_MODE_LONGONLY))))return false;
  MqlTradeRequest req={};MqlTradeCheckResult chk={};MqlTradeResult result={};req.action=TRADE_ACTION_DEAL;req.symbol=sym;req.magic=magic;req.volume=vol;req.type=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;req.price=side>0?tick.ask:tick.bid;req.deviation=deviation;req.type_filling=ORDER_FILLING_FOK;req.position=kind==2?x.ticket:0;
  if(kind==1){double margin=0;if(!OrderCalcMargin(req.type,sym,vol,req.price,margin)||!MathIsValidNumber(margin)||margin<=0||margin>AccountInfoDouble(ACCOUNT_MARGIN_FREE))return false;}
  req.comment="HG6-"+IntegerToString(sequence+1);if(!OrderCheck(req,chk)||(chk.retcode!=0&&chk.retcode!=TRADE_RETCODE_DONE)||(kind==1&&chk.margin_free<0))return false;
  sequence++;intent.seq=sequence;intent.proposal=proposal;intent.created_ms=tick.time_msc;intent.position_id=(long)x.identifier;intent.order_id=intent.deal_id=0;intent.kind=kind;intent.side=side;intent.units=units;intent.state=HG5_INTENT_UNKNOWN;
  if(!Persist())return false; // before any network call; no resend after a crash.
  ResetLastError();bool sent=OrderSend(req,result);intent.order_id=(long)result.order;intent.deal_id=(long)result.deal;
  if(intent.order_id==0&&intent.deal_id>0&&HistoryDealSelect((ulong)intent.deal_id))intent.order_id=HistoryDealGetInteger((ulong)intent.deal_id,DEAL_ORDER);
  PrintFormat("HG6 order attempt seq=%I64d sent=%d retcode=%u order=%I64u deal=%I64u error=%d",sequence,(int)sent,result.retcode,result.order,result.deal,GetLastError());
  if(!Persist())return false;if(intent.order_id<=0){fault=true;return false;}return sent;
 }
};
#endif
