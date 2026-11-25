#pragma once
#include <vector>
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <fstream>
#include <string>
#include <memory>
#include <stdexcept>
using uchar=uint8_t;using uint=uint32_t;using ulong=uint64_t;
static_assert(sizeof(long)==8);
template<typename T> int ArraySize(const std::vector<T>&v){return int(v.size());}
template<typename T,size_t N> int ArraySize(const T(&)[N]){return int(N);}
template<typename T> int ArrayResize(std::vector<T>&v,int n){if(n<0)return -1;try{v.resize(n);return n;}catch(...){return -1;}}
template<typename T> void ArrayFree(std::vector<T>&v){std::vector<T>().swap(v);}
template<typename T,typename V> void ArrayInitialize(std::vector<T>&v,V x){std::fill(v.begin(),v.end(),T(x));}
template<typename T> int ArrayCopy(std::vector<T>&d,const std::vector<T>&s,int p,int q,int n){if(p+n>int(d.size())||q+n>int(s.size()))return -1;std::copy_n(s.begin()+q,n,d.begin()+p);return n;}
double MathAbs(double x){return std::abs(x);} double MathExp(double x){return std::exp(x);} double MathExpm1(double x){return std::expm1(x);} double MathSqrt(double x){return std::sqrt(x);} double MathMax(double a,double b){return std::max(a,b);} double MathMin(double a,double b){return std::min(a,b);} bool MathIsValidNumber(double x){return std::isfinite(x);}
#include <cstdio>
template<class...A>std::string StringFormat(const char*fmt,A...v){char b[256];std::snprintf(b,sizeof(b),fmt,v...);return b;}double StringToDouble(const std::string&s){return std::stod(s);}double MathLog(double x){return std::log(x);}double MathTanh(double x){return std::tanh(x);}
// Host compatibility shim ONLY: actual terminal calls and broker behavior remain unverified.
#include <cassert>
#include <chrono>
#include <ctime>
#include <filesystem>
#include <iostream>
#include <map>
#include <sstream>
#include <openssl/sha.h>
using string=std::string;using datetime=long;using ushort=uint16_t;
struct MqlTick{datetime time=0;double bid=0,ask=0,last=0;ulong volume=0;long time_msc=0;uint flags=0;double volume_real=0;};
struct MqlDateTime{int year,mon,day,hour,min,sec,day_of_week,day_of_year;};
using ENUM_DAY_OF_WEEK=int;
struct MqlTradeRequest {int action=0,type=0,type_filling=0;string symbol,comment;ulong magic=0,position=0,deviation=0;double volume=0,price=0;};
struct MqlTradeCheckResult {uint retcode=0;double margin_free=1000;};
struct MqlTradeResult {uint retcode=0;ulong order=0,deal=0;};struct MqlTradeTransaction{};
enum{INVALID_HANDLE=-1,FILE_READ=1,FILE_WRITE=2,FILE_BIN=4,FILE_CSV=8,FILE_ANSI=16,FILE_COMMON=32,WHOLE_ARRAY=-1,CP_UTF8=65001,CRYPT_HASH_SHA256=1,INIT_SUCCEEDED=0,INIT_FAILED=1,INIT_PARAMETERS_INCORRECT=2};
enum{ACCOUNT_CURRENCY=1,ACCOUNT_SERVER,ACCOUNT_LEVERAGE,ACCOUNT_LOGIN,ACCOUNT_TRADE_MODE,ACCOUNT_TRADE_ALLOWED,ACCOUNT_TRADE_EXPERT,ACCOUNT_MARGIN_MODE,ACCOUNT_BALANCE,ACCOUNT_MARGIN_FREE,ACCOUNT_TRADE_MODE_DEMO,ACCOUNT_MARGIN_MODE_RETAIL_HEDGING};
enum{SYMBOL_TRADE_CONTRACT_SIZE=101,SYMBOL_TRADE_TICK_SIZE,SYMBOL_DIGITS,SYMBOL_VOLUME_MIN,SYMBOL_VOLUME_MAX,SYMBOL_VOLUME_STEP,SYMBOL_FILLING_MODE,SYMBOL_TRADE_MODE,SYMBOL_FILLING_FOK=1,SYMBOL_TRADE_MODE_DISABLED=0,SYMBOL_TRADE_MODE_CLOSEONLY=3,SYMBOL_TRADE_MODE_SHORTONLY=2,SYMBOL_TRADE_MODE_LONGONLY=1};
enum{POSITION_SYMBOL=201,POSITION_MAGIC,POSITION_IDENTIFIER,POSITION_TIME_MSC,POSITION_TYPE,POSITION_VOLUME,POSITION_PRICE_OPEN,POSITION_TYPE_BUY=0,POSITION_TYPE_SELL=1};
enum{ORDER_SYMBOL=301,ORDER_MAGIC,ORDER_STATE,ORDER_STATE_REJECTED,ORDER_STATE_CANCELED,ORDER_STATE_EXPIRED,ORDER_TYPE_BUY=0,ORDER_TYPE_SELL=1,ORDER_FILLING_FOK=0};
enum{DEAL_ORDER=401,DEAL_SYMBOL,DEAL_MAGIC,DEAL_ENTRY,DEAL_TYPE,DEAL_POSITION_ID,DEAL_TIME_MSC,DEAL_VOLUME,DEAL_PRICE,DEAL_ENTRY_IN=0,DEAL_ENTRY_OUT=1,DEAL_TYPE_BUY=0,DEAL_TYPE_SELL=1};
enum{TERMINAL_CONNECTED=501,TERMINAL_TRADE_ALLOWED,MQL_TRADE_ALLOWED,MQL_TESTER,TRADE_ACTION_DEAL,TRADE_RETCODE_DONE=10009,COPY_TICKS_ALL=0};
string _Symbol="XAUUSD";static long mock_clock=1767225600;static int send_count=0;static int mock_error=0;static std::vector<MqlTick> mock_ticks;static int mock_visible=0;
static std::map<int,FILE*> open_files;static int next_handle=1;
string host_path(string s){std::replace(s.begin(),s.end(),'\\','/');return s;}
int FileOpen(string p,int flags,int delimiter=0){(void)delimiter;auto path=host_path(p);const char*mode=(flags&FILE_WRITE)?((flags&FILE_READ)?"r+b":"wb"):"rb";FILE*f=fopen(path.c_str(),mode);if(!f&&(flags&FILE_WRITE)&&(flags&FILE_READ))f=fopen(path.c_str(),"w+b");if(!f)return -1;open_files[next_handle]=f;return next_handle++;}
void FileClose(int h){auto it=open_files.find(h);if(it!=open_files.end()){fclose(it->second);open_files.erase(it);}}
ulong FileSize(int h){FILE*f=open_files.at(h);auto p=ftell(f);fseek(f,0,SEEK_END);auto n=ftell(f);fseek(f,p,SEEK_SET);return (ulong)n;}
bool FileSeek(int h,long offset,int origin){return fseek(open_files.at(h),offset,origin)==0;}
void FileFlush(int h){fflush(open_files.at(h));}
bool FileIsExist(string p){return std::filesystem::exists(host_path(p));}
uint FileReadArray(int h,std::vector<uchar>&a,int p,int n){return (uint)fread(a.data()+p,1,n,open_files.at(h));}
uint FileWriteArray(int h,const std::vector<uchar>&a,int p,int n){return (uint)fwrite(a.data()+p,1,n,open_files.at(h));}
template<class...A>uint FileWrite(int h,const A&...v){std::ostringstream s;((s<<v<<','),...);s<<'\n';auto x=s.str();return (uint)fwrite(x.data(),1,x.size(),open_files.at(h));}
int CryptEncode(int method,const std::vector<uchar>&data,const std::vector<uchar>&key,std::vector<uchar>&out){(void)method;(void)key;out.resize(32);SHA256(data.data(),data.size(),out.data());return 32;}
int StringToCharArray(const string&s,std::vector<uchar>&b,int p,int n,int cp){(void)p;(void)n;(void)cp;b.assign(s.begin(),s.end());b.push_back(0);return (int)b.size();}
int StringLen(const string&s){return (int)s.size();}ushort StringGetCharacter(const string&s,int i){return (ushort)s.at(i);}int StringFind(const string&s,const string&p){auto q=s.find(p);return q==string::npos?-1:(int)q;}string IntegerToString(long x){return std::to_string(x);}
double MathPow(double x,double y){return std::pow(x,y);}
double MathRound(double v){return std::round(v);}template<class T,size_t N,size_t M>int ArrayRange(const T(&)[N][M],int d){return d==0?(int)N:(int)M;}
bool TimeToStruct(datetime t,MqlDateTime&x){std::time_t a=t;auto*b=std::gmtime(&a);if(!b)return false;x={b->tm_year+1900,b->tm_mon+1,b->tm_mday,b->tm_hour,b->tm_min,b->tm_sec,b->tm_wday,b->tm_yday};return true;}
datetime TimeTradeServer(){return mock_clock;}datetime TimeCurrent(){return mock_clock;}datetime TimeGMT(){return mock_clock;}
bool SymbolInfoSessionTrade(string s,int d,uint i,datetime&f,datetime&t){(void)s;(void)d;if(i)return false;f=0;t=86400;return true;}
string AccountInfoString(int p){return p==ACCOUNT_CURRENCY?"USD":"HOST-MOCK";}
long AccountInfoInteger(int p){switch(p){case ACCOUNT_LEVERAGE:return 500;case ACCOUNT_LOGIN:return 10001;case ACCOUNT_TRADE_MODE:return ACCOUNT_TRADE_MODE_DEMO;case ACCOUNT_MARGIN_MODE:return ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;default:return 1;}}
double AccountInfoDouble(int p){return p==ACCOUNT_BALANCE?100.0:1000.0;}
double SymbolInfoDouble(string s,int p){(void)s;switch(p){case SYMBOL_TRADE_CONTRACT_SIZE:return 100.;case SYMBOL_TRADE_TICK_SIZE:return .01;case SYMBOL_VOLUME_MIN:return .01;case SYMBOL_VOLUME_MAX:return 100.;case SYMBOL_VOLUME_STEP:return .01;default:return 0.;}}
long SymbolInfoInteger(string s,int p){(void)s;if(p==SYMBOL_DIGITS)return 2;if(p==SYMBOL_FILLING_MODE)return SYMBOL_FILLING_FOK;if(p==SYMBOL_TRADE_MODE)return 4;return 0;}
long TerminalInfoInteger(int p){(void)p;return 1;}long MQLInfoInteger(int p){(void)p;return 1;}
int PositionsTotal(){return 0;}ulong PositionGetTicket(int i){(void)i;return 0;}bool PositionSelectByTicket(ulong t){(void)t;return false;}string PositionGetString(int p){(void)p;return "";}long PositionGetInteger(int p){(void)p;return 0;}double PositionGetDouble(int p){(void)p;return 0;}
int OrdersTotal(){return 0;}ulong OrderGetTicket(int i){(void)i;return 0;}bool OrderSelect(ulong t){(void)t;return false;}string OrderGetString(int p){(void)p;return "";}long OrderGetInteger(int p){(void)p;return 0;}
bool HistorySelect(datetime a,datetime b){(void)a;(void)b;return true;}int HistoryDealsTotal(){return 0;}ulong HistoryDealGetTicket(int i){(void)i;return 0;}string HistoryDealGetString(ulong t,int p){(void)t;(void)p;return "";}long HistoryDealGetInteger(ulong t,int p){(void)t;(void)p;return 0;}double HistoryDealGetDouble(ulong t,int p){(void)t;(void)p;return 0;}bool HistoryDealSelect(ulong t){(void)t;return false;}bool HistoryOrderSelect(ulong t){(void)t;return false;}long HistoryOrderGetInteger(ulong t,int p){(void)t;(void)p;return 0;}
bool OrderCalcMargin(int type,string s,double volume,double price,double&m){(void)type;(void)s;m=volume*price/5;return true;}bool OrderCheck(const MqlTradeRequest&r,MqlTradeCheckResult&c){(void)r;c.retcode=0;return true;}bool OrderSend(const MqlTradeRequest&r,MqlTradeResult&v){(void)r;(void)v;++send_count;return false;}
bool SymbolInfoTick(string s,MqlTick&t){(void)s;if(mock_visible<=0)return false;t=mock_ticks.at(mock_visible-1);return true;}
int CopyTicks(string sym,std::vector<MqlTick>&out,uint flags,ulong from,uint count){(void)sym;(void)flags;int n=0;for(int i=0;i<mock_visible&&n<(int)std::min(count,(uint)out.size());i++){if(mock_ticks[i].time_msc>=(long)from)out[n++]=mock_ticks[i];}return n;}
ulong GetMicrosecondCount(){return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}bool IsStopped(){return false;}void ResetLastError(){mock_error=0;}int GetLastError(){return mock_error;}
bool EventSetMillisecondTimer(int n){return n>0;}void EventKillTimer(){}
template<class...A>void Print(const A&...v){((std::cout<<v),...);std::cout<<'\n';}
template<class...A>void PrintFormat(const char*f,const A&...v){(void)sizeof...(v);std::cout<<f<<'\n';}
template<class...A>void Comment(const A&...v){(void)sizeof...(v);}
