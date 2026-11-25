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
struct MqlTradeRequest {int action=0,type=0,type_filling=0;string symbol,comment;ulong magic=0,position=0,deviation=0,order=0;double volume=0,price=0;};
struct MqlTradeCheckResult {uint retcode=0;double margin_free=1000,equity=100;};
struct MqlTradeResult {uint retcode=0;ulong order=0,deal=0;};struct MqlTradeTransaction{};
enum{INVALID_HANDLE=-1,FILE_READ=1,FILE_WRITE=2,FILE_BIN=4,FILE_CSV=8,FILE_ANSI=16,FILE_COMMON=32,WHOLE_ARRAY=-1,CP_UTF8=65001,CRYPT_HASH_SHA256=1,INIT_SUCCEEDED=0,INIT_FAILED=1,INIT_PARAMETERS_INCORRECT=2};
enum{ACCOUNT_CURRENCY=1,ACCOUNT_SERVER,ACCOUNT_LEVERAGE,ACCOUNT_LOGIN,ACCOUNT_TRADE_MODE,ACCOUNT_TRADE_ALLOWED,ACCOUNT_TRADE_EXPERT,ACCOUNT_MARGIN_MODE,ACCOUNT_BALANCE,ACCOUNT_MARGIN_FREE,ACCOUNT_TRADE_MODE_DEMO,ACCOUNT_MARGIN_MODE_RETAIL_HEDGING};
enum{SYMBOL_TRADE_CONTRACT_SIZE=101,SYMBOL_TRADE_TICK_SIZE,SYMBOL_DIGITS,SYMBOL_VOLUME_MIN,SYMBOL_VOLUME_MAX,SYMBOL_VOLUME_STEP,SYMBOL_FILLING_MODE,SYMBOL_TRADE_MODE,SYMBOL_FILLING_FOK=1,SYMBOL_TRADE_MODE_DISABLED=0,SYMBOL_TRADE_MODE_CLOSEONLY=3,SYMBOL_TRADE_MODE_SHORTONLY=2,SYMBOL_TRADE_MODE_LONGONLY=1};
enum{POSITION_SYMBOL=201,POSITION_MAGIC,POSITION_IDENTIFIER,POSITION_TIME_MSC,POSITION_TYPE,POSITION_VOLUME,POSITION_PRICE_OPEN,POSITION_TYPE_BUY=0,POSITION_TYPE_SELL=1};
enum{ORDER_SYMBOL=301,ORDER_MAGIC,ORDER_STATE,ORDER_STATE_REJECTED,ORDER_STATE_CANCELED,ORDER_STATE_EXPIRED,ORDER_TYPE_BUY=0,ORDER_TYPE_SELL=1,ORDER_FILLING_FOK=0};
enum{DEAL_ORDER=401,DEAL_SYMBOL,DEAL_MAGIC,DEAL_ENTRY,DEAL_TYPE,DEAL_POSITION_ID,DEAL_TIME_MSC,DEAL_VOLUME,DEAL_PRICE,DEAL_ENTRY_IN=0,DEAL_ENTRY_OUT=1,DEAL_TYPE_BUY=0,DEAL_TYPE_SELL=1};
enum{TERMINAL_CONNECTED=501,TERMINAL_TRADE_ALLOWED,MQL_TRADE_ALLOWED,MQL_TESTER,TRADE_ACTION_DEAL,TRADE_RETCODE_DONE=10009,COPY_TICKS_ALL=0};
enum{ACCOUNT_EQUITY=601,ACCOUNT_MARGIN,ACCOUNT_MARGIN_LEVEL,ACCOUNT_MARGIN_SO_CALL,ACCOUNT_MARGIN_SO_SO,ACCOUNT_MARGIN_SO_MODE,ACCOUNT_STOPOUT_MODE_PERCENT=0,ORDER_STATE_FILLED=701,ORDER_COMMENT,ORDER_TIME_SETUP_MSC,ORDER_TYPE,ORDER_POSITION_ID,DEAL_PROFIT=801,DEAL_COMMISSION,DEAL_SWAP,DEAL_FEE,TRADE_ACTION_REMOVE=901,TRADE_RETCODE_REJECT=10006,TRADE_RETCODE_INVALID=10013,TRADE_RETCODE_INVALID_VOLUME=10014,TRADE_RETCODE_INVALID_PRICE=10015,TRADE_RETCODE_TRADE_DISABLED=10017,TRADE_RETCODE_MARKET_CLOSED=10018,TRADE_RETCODE_NO_MONEY=10019,TRADE_RETCODE_INVALID_FILL=10030,TRADE_RETCODE_REQUOTE=10004,TRADE_RETCODE_PRICE_CHANGED=10020,TRADE_RETCODE_PRICE_OFF=10021};
enum{SYMBOL_TRADE_EXEMODE=10001,SYMBOL_TRADE_EXECUTION_REQUEST=0,SYMBOL_TRADE_EXECUTION_INSTANT=1,SYMBOL_TRADE_EXECUTION_MARKET=2,SYMBOL_TRADE_EXECUTION_EXCHANGE=3};
static int mock_execution=SYMBOL_TRADE_EXECUTION_MARKET,mock_fill_flags=SYMBOL_FILLING_FOK;
static bool mock_tester=false,mock_connected=true,mock_history=true,mock_quote_available=true,mock_session_open=true;static double mock_balance=100.;
string _Symbol="XAUUSD";static long mock_clock=1767225600;static int send_count=0;static int mock_error=0;static std::vector<MqlTick> mock_ticks;static int mock_visible=0;
static int mock_advance_on_flush=0;static std::map<int,FILE*> open_files;static int next_handle=1;
string host_path(string s){std::replace(s.begin(),s.end(),'\\','/');return s;}
int FileOpen(string p,int flags,int delimiter=0){(void)delimiter;auto path=host_path(p);const char*mode=(flags&FILE_WRITE)?((flags&FILE_READ)?"r+b":"wb"):"rb";FILE*f=fopen(path.c_str(),mode);if(!f&&(flags&FILE_WRITE)&&(flags&FILE_READ))f=fopen(path.c_str(),"w+b");if(!f)return -1;open_files[next_handle]=f;return next_handle++;}
void FileClose(int h){auto it=open_files.find(h);if(it!=open_files.end()){fclose(it->second);open_files.erase(it);}}
ulong FileSize(int h){FILE*f=open_files.at(h);auto p=ftell(f);fseek(f,0,SEEK_END);auto n=ftell(f);fseek(f,p,SEEK_SET);return (ulong)n;}
bool FileSeek(int h,long offset,int origin){return fseek(open_files.at(h),offset,origin)==0;}
void FileFlush(int h){fflush(open_files.at(h));if(mock_advance_on_flush>0&&--mock_advance_on_flush==0&&mock_visible<(int)mock_ticks.size())++mock_visible;}
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
bool SymbolInfoSessionTrade(string s,int d,uint i,datetime&f,datetime&t){(void)s;(void)d;if(i||!mock_session_open)return false;f=0;t=86400;return true;}
string AccountInfoString(int p){return p==ACCOUNT_CURRENCY?"USD":"HOST-MOCK";}
long AccountInfoInteger(int p){switch(p){case ACCOUNT_MARGIN_SO_MODE:return ACCOUNT_STOPOUT_MODE_PERCENT;case ACCOUNT_LEVERAGE:return 500;case ACCOUNT_LOGIN:return 10001;case ACCOUNT_TRADE_MODE:return ACCOUNT_TRADE_MODE_DEMO;case ACCOUNT_MARGIN_MODE:return ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;default:return 1;}}
double AccountInfoDouble(int p){switch(p){case ACCOUNT_BALANCE:case ACCOUNT_EQUITY:return mock_balance;case ACCOUNT_MARGIN:return 0.;case ACCOUNT_MARGIN_SO_CALL:return 100.;case ACCOUNT_MARGIN_SO_SO:return 50.;default:return 1000.;}}
double SymbolInfoDouble(string s,int p){(void)s;switch(p){case SYMBOL_TRADE_CONTRACT_SIZE:return 100.;case SYMBOL_TRADE_TICK_SIZE:return .01;case SYMBOL_VOLUME_MIN:return .01;case SYMBOL_VOLUME_MAX:return 100.;case SYMBOL_VOLUME_STEP:return .01;default:return 0.;}}
long SymbolInfoInteger(string s,int p){(void)s;if(p==SYMBOL_DIGITS)return 2;if(p==SYMBOL_FILLING_MODE)return mock_fill_flags;if(p==SYMBOL_TRADE_EXEMODE)return mock_execution;if(p==SYMBOL_TRADE_MODE)return 4;return 0;}
long TerminalInfoInteger(int p){return p==TERMINAL_CONNECTED?mock_connected:1;}long MQLInfoInteger(int p){return p==MQL_TESTER?mock_tester:1;}
struct MockOrder{ulong id,magic,pos;long ms;int type,state;string symbol,comment;bool active;};
struct MockDeal{ulong id,order,magic,pos;long ms;int entry,type;double volume,price,profit,commission,swap,fee;string symbol;};
static std::vector<MockOrder> mo;static std::vector<MockDeal> md;static ulong mock_next=100,selected_order=0,history_pos=0,mock_pt=0,mock_magic=0;static long mock_ptime=0;static int mock_side=0,mock_send_mode=0,mock_cancel_mode=0;static double mock_volume=0,mock_price=0;
int PositionsTotal(){return mock_pt?1:0;}ulong PositionGetTicket(int i){return i==0?mock_pt:0;}bool PositionSelectByTicket(ulong t){return t&&t==mock_pt;}string PositionGetString(int p){return p==POSITION_SYMBOL?_Symbol:"";}long PositionGetInteger(int p){switch(p){case POSITION_MAGIC:return mock_magic;case POSITION_IDENTIFIER:return mock_pt;case POSITION_TIME_MSC:return mock_ptime;case POSITION_TYPE:return mock_side;default:return 0;}}double PositionGetDouble(int p){return p==POSITION_VOLUME?mock_volume:mock_price;}
MockOrder* find_o(ulong t){for(auto &o:mo)if(o.id==t)return &o;return nullptr;}MockDeal* find_d(ulong t){for(auto &d:md)if(d.id==t)return &d;return nullptr;}
int OrdersTotal(){return std::count_if(mo.begin(),mo.end(),[](auto&o){return o.active;});}ulong OrderGetTicket(int i){for(auto&o:mo)if(o.active&&i--==0){selected_order=o.id;return o.id;}return 0;}bool OrderSelect(ulong t){auto o=find_o(t);if(!o||!o->active)return false;selected_order=t;return true;}
string mock_os(ulong t,int p){auto o=find_o(t);if(!o)return "";return p==ORDER_SYMBOL?o->symbol:o->comment;}
long mock_oi(ulong t,int p){auto o=find_o(t);if(!o)return 0;switch(p){case ORDER_MAGIC:return o->magic;case ORDER_STATE:return o->state;case ORDER_TYPE:return o->type;case ORDER_TIME_SETUP_MSC:return o->ms;case ORDER_POSITION_ID:return o->pos;default:return 0;}}
string OrderGetString(int p){return mock_os(selected_order,p);}long OrderGetInteger(int p){return mock_oi(selected_order,p);}
bool HistorySelect(datetime a,datetime b){(void)a;(void)b;history_pos=0;return mock_history;}bool HistorySelectByPosition(ulong t){history_pos=t;return mock_history;}
int HistoryDealsTotal(){return std::count_if(md.begin(),md.end(),[](auto&d){return !history_pos||d.pos==history_pos;});}ulong HistoryDealGetTicket(int i){for(auto&d:md)if((!history_pos||d.pos==history_pos)&&i--==0)return d.id;return 0;}
string HistoryDealGetString(ulong t,int p){auto d=find_d(t);return d&&p==DEAL_SYMBOL?d->symbol:"";}
long HistoryDealGetInteger(ulong t,int p){auto d=find_d(t);if(!d)return 0;switch(p){case DEAL_ORDER:return d->order;case DEAL_MAGIC:return d->magic;case DEAL_ENTRY:return d->entry;case DEAL_TYPE:return d->type;case DEAL_POSITION_ID:return d->pos;case DEAL_TIME_MSC:return d->ms;default:return 0;}}
double HistoryDealGetDouble(ulong t,int p){auto d=find_d(t);if(!d)return 0;switch(p){case DEAL_VOLUME:return d->volume;case DEAL_PRICE:return d->price;case DEAL_PROFIT:return d->profit;case DEAL_COMMISSION:return d->commission;case DEAL_SWAP:return d->swap;case DEAL_FEE:return d->fee;default:return 0;}}
bool HistoryDealSelect(ulong t){return mock_history&&find_d(t);}bool HistoryOrderSelect(ulong t){auto o=find_o(t);return mock_history&&o&&!o->active;}int HistoryOrdersTotal(){return std::count_if(mo.begin(),mo.end(),[](auto&o){return !o.active;});}ulong HistoryOrderGetTicket(int i){for(auto&o:mo)if(!o.active&&i--==0)return o.id;return 0;}long HistoryOrderGetInteger(ulong t,int p){return mock_oi(t,p);}string HistoryOrderGetString(ulong t,int p){return mock_os(t,p);}
bool OrderCalcMargin(int type,string s,double volume,double price,double&m){(void)type;(void)s;m=volume*price/5;return true;}bool OrderCheck(const MqlTradeRequest&r,MqlTradeCheckResult&c){(void)r;c.retcode=0;return true;}
bool OrderSend(const MqlTradeRequest&r,MqlTradeResult&v){++send_count;assert(mock_tester);if(r.action==TRADE_ACTION_REMOVE){if(mock_cancel_mode){v.retcode=mock_cancel_mode==1?TRADE_RETCODE_REJECT:10012;return false;}auto o=find_o(r.order);if(!o||!o->active)return false;o->active=false;o->state=ORDER_STATE_CANCELED;v.retcode=TRADE_RETCODE_DONE;return true;}if(mock_send_mode==1||mock_send_mode==4||mock_send_mode==5||mock_send_mode==6){v.retcode=mock_send_mode==4?TRADE_RETCODE_REQUOTE:mock_send_mode==5?TRADE_RETCODE_PRICE_CHANGED:mock_send_mode==6?TRADE_RETCODE_PRICE_OFF:TRADE_RETCODE_REJECT;return false;}
 bool closing=r.position!=0;double vol=mock_send_mode==3?r.volume/2:r.volume;ulong o=++mock_next,d=++mock_next,pos=closing?mock_pt:++mock_next;long ms=mock_ticks.at(mock_visible-1).time_msc;bool pending=mock_send_mode==3;
 mo.push_back({o,r.magic,pos,ms,r.type,pending?0:ORDER_STATE_FILLED,r.symbol,r.comment,pending});double pnl=closing?(r.price-mock_price)*(mock_side==POSITION_TYPE_BUY?1:-1)*vol*100:0;md.push_back({d,o,r.magic,pos,ms,closing?DEAL_ENTRY_OUT:DEAL_ENTRY_IN,r.type,vol,r.price,pnl,-.01,0,0,r.symbol});
 if(closing){mock_volume-=vol;if(mock_volume<1e-9){mock_volume=0;mock_pt=0;}}else{mock_pt=pos;mock_magic=r.magic;mock_ptime=ms;mock_side=r.type;mock_volume=vol;mock_price=r.price;}
 if(mock_send_mode==2){v.retcode=10012;return false;}v.order=o;v.deal=d;v.retcode=TRADE_RETCODE_DONE;return true;}
bool SymbolInfoTick(string s,MqlTick&t){(void)s;if(!mock_quote_available||mock_visible<=0)return false;t=mock_ticks.at(mock_visible-1);return true;}
int CopyTicks(string sym,std::vector<MqlTick>&out,uint flags,ulong from,uint count){(void)sym;(void)flags;int n=0;for(int i=0;i<mock_visible&&n<(int)std::min(count,(uint)out.size());i++){if(mock_ticks[i].time_msc>=(long)from)out[n++]=mock_ticks[i];}return n;}
ulong GetMicrosecondCount(){return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}bool IsStopped(){return false;}void ResetLastError(){mock_error=0;}int GetLastError(){return mock_error;}
bool EventSetMillisecondTimer(int n){return n>0;}void EventKillTimer(){}
template<class...A>void Print(const A&...v){((std::cout<<v),...);std::cout<<'\n';}
template<class...A>void PrintFormat(const char*f,const A&...v){(void)sizeof...(v);std::cout<<f<<'\n';}
template<class...A>void Comment(const A&...v){(void)sizeof...(v);}
