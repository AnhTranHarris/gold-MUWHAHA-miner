#ifndef HG6_FEED_MQH
#define HG6_FEED_MQH
#include "HG5StateCodec.mqh"
#include "HG5StatePrimitives.mqh"
#include "HG5RX136.mqh"
// SECTION T1: exact quote tuple and bounded chronological transport.
// Source price model is integer cents. Reject off-grid prices; never coerce an incompatible feed.
#define HG6_TICK_BATCH 4096
#define HG6_MAX_TIE 1024
bool HG6Cents(double price,int &cents){
 if(!MathIsValidNumber(price)||price<=0.0||price>21474836.0)return false;
 double q=price*100.0,rounded=MathRound(q);
 if(MathAbs(q-rounded)>0.000001)return false;cents=(int)rounded;return cents>0;
}
bool HG6Normalize(const MqlTick &t,HG5Quote &q){
 if(t.time_msc<=0||!HG6Cents(t.bid,q.bid)||!HG6Cents(t.ask,q.ask)||q.ask<q.bid||!MathIsValidNumber(t.last)||!MathIsValidNumber(t.volume_real))return false;
 q.ms=t.time_msc;return true;
}
bool HG6TickEqual(const MqlTick &a,const MqlTick &b){
 return a.time_msc==b.time_msc&&a.time==b.time&&a.bid==b.bid&&a.ask==b.ask&&a.last==b.last&&a.volume==b.volume&&a.flags==b.flags&&a.volume_real==b.volume_real;
}
// SECTION T2: full ordered overlap for the last committed group. Identical observations
// are kept at their exact multiplicities. A group is not committed without a later timestamp.
class HG6Cursor {
 long start_ms,last_ms,ordinal;MqlTick tail[];bool valid;
 public:
 HG6Cursor(){start_ms=last_ms=ordinal=0;valid=false;}
 bool Init(long start){if(start<=0||valid)return false;start_ms=start;last_ms=ordinal=0;ArrayResize(tail,0);valid=true;return true;}
 long From()const{return last_ms>0?last_ms:start_ms;}
 long Last()const{return last_ms;}
 long Ordinal()const{return ordinal;}
 int TailCount()const{return ArraySize(tail);}
 bool Ready()const{return valid;}
 void Fail(){valid=false;}
 bool VerifyBatch(const MqlTick &raw[],int n,int &first){
  first=0;if(!valid||n<0||n>ArraySize(raw)||n>HG6_TICK_BATCH)return false;
  for(int i=0;i<n;i++){HG5Quote q;if(!HG6Normalize(raw[i],q)||q.ms<From()||(i&&q.ms<raw[i-1].time_msc))return false;}
  if(last_ms==0)return true;
  int k=ArraySize(tail);if(k<=0||n<k)return false;
  for(int i=0;i<k;i++)if(!HG6TickEqual(raw[i],tail[i]))return false;
  if(n>k&&raw[k].time_msc<=last_ms)return false;first=k;return true;
 }
 // returns exclusive end of the next complete group; 0 means trailing uncommitted group.
 int NextEnd(const MqlTick &raw[],int n,int lo){
  if(!valid||lo<0||lo>=n||n>ArraySize(raw))return -1;int e=lo+1;long t=raw[lo].time_msc;
  while(e<n&&raw[e].time_msc==t)e++;
  if(e-lo>HG6_MAX_TIE)return -1;
  if(e==n)return n==HG6_TICK_BATCH&&lo==TailCount()?-1:0;
  if(raw[e].time_msc<=t)return -1;return e;
 }
 bool Group(const MqlTick &raw[],int lo,int end,HG5Quote &out[]){
  int n=end-lo;if(!valid||lo<0||end>=ArraySize(raw)||n<=0||n>HG6_MAX_TIE||raw[end].time_msc<=raw[lo].time_msc||raw[lo].time_msc<=last_ms||ArrayResize(out,n)!=n)return false;
  for(int i=0;i<n;i++)if(!HG6Normalize(raw[lo+i],out[i])||out[i].ms!=raw[lo].time_msc)return false;return true;
 }
 bool Commit(const MqlTick &raw[],int lo,int end){
  int n=end-lo;if(!valid||lo<0||end>=ArraySize(raw)||n<=0||n>HG6_MAX_TIE||raw[end].time_msc<=raw[lo].time_msc||raw[lo].time_msc<=last_ms)return false;
  for(int i=lo;i<end;i++)if(raw[i].time_msc!=raw[lo].time_msc)return false;
  if(ArrayResize(tail,n)!=n)return false;for(int i=0;i<n;i++)tail[i]=raw[lo+i];last_ms=raw[lo].time_msc;ordinal+=n;return true;
 }
 bool Transfer(HG5StateCodec &c){
  long expected=start_ms;if(!c.I64(start_ms)||start_ms!=expected||!c.I64(last_ms)||!c.I64(ordinal)||!c.Flag(valid)||!valid||last_ms<0||ordinal<0)return false;
  int n=ArraySize(tail);if(!c.I32(n)||n<0||n>HG6_MAX_TIE||(last_ms==0)!=(n==0)||ordinal<n)return false;
  if(c.Reading()&&ArrayResize(tail,n)!=n)return false;
  for(int i=0;i<n;i++){
   long tm=c.Reading()?0:(long)tail[i].time,vol=c.Reading()?0:(long)tail[i].volume;int flags=c.Reading()?0:(int)tail[i].flags;
   if(!c.I64(tm)||!c.I64(tail[i].time_msc)||!c.F64(tail[i].bid)||!c.F64(tail[i].ask)||!c.F64(tail[i].last)||!c.I64(vol)||!c.I32(flags)||!c.F64(tail[i].volume_real))return false;
   if(c.Reading()){tail[i].time=(datetime)tm;tail[i].volume=(ulong)vol;tail[i].flags=(uint)flags;}
   HG5Quote q;if(tail[i].time_msc!=last_ms||!HG6Normalize(tail[i],q))return false;
  }return true;
 }
};
#endif
