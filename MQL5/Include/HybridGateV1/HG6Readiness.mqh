#ifndef HG6_READINESS_MQH
#define HG6_READINESS_MQH
#include "HG5OperationalGate.mqh"
// SECTION R1: current-sample readiness, independent sticky integrity quarantine.
// No implicit authorization. Transient failures disarm; a new explicit Arm can
// succeed only on a fresh healthy sample. Identity/storage/time regression latch.
class HG6Readiness {
 HG5OpsLimits limits;long last;int transient,sticky;bool initialized,armed;
 public:
 HG6Readiness(){last=-1;transient=sticky=0;initialized=armed=false;}
 bool Init(const HG5OpsLimits &x){if(initialized||x.max_quote_age_ms<=0||x.max_queue_us<=0||x.max_service_us<=0||x.max_trade_lag_ms<=0||x.max_queue<=0||x.max_active<=0||x.max_mailbox<=0)return false;limits=x;initialized=true;return true;}
 int Check(const HG5OpsSample &s){
  transient=0;if(!initialized){sticky|=1;armed=false;return sticky;}
  if(s.now_us<0||s.now_us<last)sticky|=2;else last=s.now_us;
  if(!s.connected)transient|=4;if(!s.calendar_ok)transient|=8;if(!s.identity_ok)sticky|=8;
  if(!s.history_ok)transient|=16;if(!s.reconciled)transient|=32;if(!s.storage_ok)sticky|=64;
  if(s.quote_age_ms<0||s.quote_age_ms>limits.max_quote_age_ms)transient|=128;
  if(s.queue_us<0||s.queue_us>limits.max_queue_us||s.service_us<0||s.service_us>limits.max_service_us)transient|=256;
  if(s.trade_lag_ms<0||s.trade_lag_ms>limits.max_trade_lag_ms)transient|=512;
  if(s.queue<0||s.active<0||s.mailbox<0)sticky|=1024;
  else if(s.queue>limits.max_queue||s.active>limits.max_active||s.mailbox>limits.max_mailbox)transient|=1024;
  if(sticky||transient)armed=false;return sticky|transient;
 }
 bool Arm(const HG5OpsSample &s,bool authorized){armed=false;if(Check(s)!=0||!authorized)return false;armed=true;return true;}
 bool EntriesAllowed()const{return initialized&&armed&&sticky==0&&transient==0;}
 void Disarm(){armed=false;}
 void Quarantine(){sticky|=2048;armed=false;}
 int Faults()const{return sticky|transient;}
 int IntegrityFaults()const{return sticky;}
};
#endif
