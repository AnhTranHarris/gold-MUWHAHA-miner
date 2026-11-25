#ifndef HG6_TERMINAL_MQH
#define HG6_TERMINAL_MQH
#include "HG6Feed.mqh"
#include "HG6Storage.mqh"
#include "HG5OperationalGate.mqh"
// SECTION O1: broker session and explicit UTC mapping. No broker-time guess is an entry permit.
bool HG6TradeSession(string symbol,datetime server){
 MqlDateTime t;if(server<=0||!TimeToStruct(server,t))return false;long sec=t.hour*3600+t.min*60+t.sec;
 for(int day=0;day<2;day++){ENUM_DAY_OF_WEEK d=(ENUM_DAY_OF_WEEK)((t.day_of_week+7-day)%7);long target=sec+(long)day*86400;
  for(uint i=0;i<32;i++){datetime from=0,to=0;if(!SymbolInfoSessionTrade(symbol,d,i,from,to))break;long f=(long)from,z=(long)to;if(f<0||f>=86400||z<0||z>172800)return false;if(z<=f)z+=86400;if(target>=f&&target<z)return true;}}
 return false;
}
bool HG6ClockMapping(int offset,bool confirmed,bool tester,datetime server){
 if(!confirmed||offset< -840||offset>840||server<=0)return false;if(tester)return offset==0;
 datetime utc=TimeGMT();if(utc<=0)return false;return MathAbs((double)((long)server-(long)utc-(long)offset*60))<=3.0;
}
// SECTION O2: bounded diagnostic telemetry; not the authoritative trade or checkpoint ledger.
// Critical trade intent is persisted separately before any order submission.
class HG6Telemetry {
 string stem;int handle,slot;long records;
 public:
 HG6Telemetry(){handle=INVALID_HANDLE;slot=0;records=0;}
 bool Open(string p){stem=p;handle=FileOpen(stem+".0.csv",FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI,',');if(handle==INVALID_HANDLE)return false;FileSeek(handle,0,SEEK_END);if(FileSize(handle)>8388608){FileClose(handle);handle=INVALID_HANDLE;return false;}return true;}
 bool Event(string kind,long ms,long id,int code,long a,long b){
  if(handle==INVALID_HANDLE)return false;
  if(FileSize(handle)>4194304){FileFlush(handle);FileClose(handle);slot=1-slot;handle=FileOpen(stem+"."+IntegerToString(slot)+".csv",FILE_WRITE|FILE_CSV|FILE_ANSI,',');if(handle==INVALID_HANDLE)return false;records=0;}
  uint n=FileWrite(handle,kind,ms,id,code,a,b);if(n==0)return false;if(++records%128==0)FileFlush(handle);return true;
 }
 void Close(){if(handle!=INVALID_HANDLE){FileFlush(handle);FileClose(handle);handle=INVALID_HANDLE;}}
};
#endif
