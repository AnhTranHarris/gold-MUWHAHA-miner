#ifndef HG5_OPERATIONAL_GATE
#define HG5_OPERATIONAL_GATE
// Non-trading fail-closed controller. All limits are externally specified engineering
// limits, not fitted trading policy. No terminal calls, no automatic rearm.
struct HG5OpsLimits {long max_quote_age_ms,max_queue_us,max_service_us,max_trade_lag_ms;int max_queue,max_active,max_mailbox;};
struct HG5OpsSample {long now_us,quote_age_ms,queue_us,service_us,trade_lag_ms;int queue,active,mailbox;bool connected,calendar_ok,identity_ok,history_ok,reconciled,storage_ok;};
class HG5OperationalGate{
 HG5OpsLimits limits;long last;int faults;bool initialized,armed;
public:
 HG5OperationalGate(){last=-1;faults=0;initialized=false;armed=false;}
 bool Init(const HG5OpsLimits &x){if(initialized||x.max_quote_age_ms<=0||x.max_queue_us<=0||x.max_service_us<=0||x.max_trade_lag_ms<=0||x.max_queue<=0||x.max_active<=0||x.max_mailbox<=0)return false;limits=x;initialized=true;return true;}
 int Check(const HG5OpsSample &s){if(!initialized){faults|=1;return faults;}if(s.now_us<0||s.now_us<last)faults|=2;if(s.now_us>=last)last=s.now_us;
  if(!s.connected)faults|=4;if(!s.calendar_ok||!s.identity_ok)faults|=8;if(!s.history_ok)faults|=16;if(!s.reconciled)faults|=32;if(!s.storage_ok)faults|=64;
  if(s.quote_age_ms<0||s.quote_age_ms>limits.max_quote_age_ms)faults|=128;if(s.queue_us<0||s.queue_us>limits.max_queue_us||s.service_us<0||s.service_us>limits.max_service_us)faults|=256;
  if(s.trade_lag_ms<0||s.trade_lag_ms>limits.max_trade_lag_ms)faults|=512;if(s.queue<0||s.queue>limits.max_queue||s.active<0||s.active>limits.max_active||s.mailbox<0||s.mailbox>limits.max_mailbox)faults|=1024;
  if(faults)armed=false;return faults;}
 // User approval and all startup gates must be supplied by the terminal adapter.
 bool Arm(const HG5OpsSample &s,bool authorized){if(!authorized||Check(s)!=0)return false;armed=true;return true;}
 bool EntriesAllowed()const{return initialized&&armed&&faults==0;}
 void Disarm(){armed=false;}
 int Faults()const{return faults;}
};
#define HG5_INTENT_PREPARED 1
#define HG5_INTENT_UNKNOWN 2
#define HG5_INTENT_ACKED 3
#define HG5_INTENT_PARTIAL 4
#define HG5_INTENT_FILLED 5
#define HG5_INTENT_REJECTED 6
#define HG5_INTENT_FROZEN 7
struct HG5IntentRecord{long seq,requested,filled;int state,attempts;};
// Transport-specific deal enumeration is external. Its authoritative cumulative unique deal
// volume must be persisted and reconciled; no resend in ambiguous states. No trade API.
class HG5IntentGate{
 HG5IntentRecord rec;bool valid,permit,restored;
public:
 HG5IntentGate(){valid=false;permit=false;restored=false;rec.seq=-1;rec.requested=rec.filled=0;rec.state=rec.attempts=0;}
 bool Prepare(long seq,long qty){if(valid||seq<0||qty<=0)return false;rec.seq=seq;rec.requested=qty;rec.filled=0;rec.state=HG5_INTENT_PREPARED;rec.attempts=0;valid=true;return true;}
 bool Restore(const HG5IntentRecord &r){if(valid||r.seq<0||r.requested<=0||r.filled<0||r.filled>r.requested||r.state<1||r.state>7||r.attempts<0||r.attempts>1)return false;if((r.state==HG5_INTENT_PREPARED)!=(r.attempts==0)|| ((r.state==HG5_INTENT_PREPARED||r.state==HG5_INTENT_ACKED)&&r.filled!=0)||(r.state==HG5_INTENT_FILLED&&r.filled!=r.requested)||(r.state==HG5_INTENT_REJECTED&&r.filled!=0)||(r.state==HG5_INTENT_PARTIAL&&(r.filled<=0||r.filled>=r.requested)))return false;rec=r;valid=true;permit=false;restored=true;return true;}
 // Stage record for durable write BEFORE dispatch. A persistence receipt for this exact
 // record is mandatory; a recovered object can never gain an old dispatch permit.
 bool MarkUnknown(HG5IntentRecord &r){if(!valid||restored||rec.state!=HG5_INTENT_PREPARED||rec.attempts!=0)return false;rec.state=HG5_INTENT_UNKNOWN;rec.attempts=1;permit=true;r=rec;return true;}
 bool ConsumePermit(const HG5IntentRecord &durable,bool storage_verified){if(!permit)return false;permit=false;return storage_verified&&durable.seq==rec.seq&&durable.requested==rec.requested&&durable.filled==rec.filled&&durable.state==rec.state&&durable.attempts==rec.attempts;}
 bool Reconcile(long qty,int observed,bool authoritative){if(!valid||rec.attempts!=1)return false;permit=false;if(rec.state==HG5_INTENT_FROZEN)return false;
  if(qty<rec.filled||qty>rec.requested||observed==HG5_INTENT_FROZEN){rec.state=HG5_INTENT_FROZEN;return false;}
  if(!authoritative){if(rec.state!=HG5_INTENT_FILLED&&rec.state!=HG5_INTENT_REJECTED)rec.state=HG5_INTENT_UNKNOWN;return false;}
  if(rec.state==HG5_INTENT_FILLED||rec.state==HG5_INTENT_REJECTED){if(qty!=rec.filled||observed!=rec.state){rec.state=HG5_INTENT_FROZEN;return false;}return true;}
  rec.filled=qty;
  if(qty==rec.requested&&observed==HG5_INTENT_FILLED)rec.state=HG5_INTENT_FILLED;
  else if(qty>0&&qty<rec.requested&&observed==HG5_INTENT_PARTIAL)rec.state=HG5_INTENT_PARTIAL;
  else if(qty==0&&observed==HG5_INTENT_REJECTED)rec.state=HG5_INTENT_REJECTED;
  else if(qty==0&&observed==HG5_INTENT_ACKED)rec.state=HG5_INTENT_ACKED;
  else{rec.state=HG5_INTENT_UNKNOWN;return false;}return true;}
 bool Snapshot(HG5IntentRecord &r)const{if(!valid)return false;r=rec;return true;}
 bool MayRelease()const{return valid&&(rec.state==HG5_INTENT_FILLED||rec.state==HG5_INTENT_REJECTED);}
};
#endif
