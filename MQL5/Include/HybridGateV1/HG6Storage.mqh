#ifndef HG6_STORAGE_MQH
#define HG6_STORAGE_MQH
#include "HG5StateCodec.mqh"
// SECTION S1: terminal-local two-generation storage. SHA-256 detects corruption,
// not malicious alteration. FileFlush/readback is not a proof of OS crash durability.
#define HG6_MAX_ENVELOPE 33554432
bool HG6Hash(const uchar &data[],uchar &digest[]){uchar key[];ArrayResize(key,0);return CryptEncode(CRYPT_HASH_SHA256,data,key,digest)==32;}
string HG6Hex(const uchar &data[]){string s="";for(int i=0;i<ArraySize(data);i++)s+=StringFormat("%02x",(uint)data[i]);return s;}
bool HG6TextDigest(const string text,uchar &digest[]){uchar b[];int n=StringToCharArray(text,b,0,WHOLE_ARRAY,CP_UTF8);if(n<=1||ArrayResize(b,n-1)!=n-1)return false;return HG6Hash(b,digest);}
void HG6Put64(uchar &b[],int p,long n){ulong u=(ulong)n;for(int i=0;i<8;i++)b[p+i]=(uchar)(u>>(8*i));}
long HG6Get64(const uchar &b[],int p){ulong u=0;for(int i=0;i<8;i++)u|=((ulong)b[p+i])<<(8*i);return (long)u;}
bool HG6BytesEqual(const uchar &a[],const uchar &b[]){if(ArraySize(a)!=ArraySize(b))return false;for(int i=0;i<ArraySize(a);i++)if(a[i]!=b[i])return false;return true;}
bool HG6ReadFile(string path,int limit,uchar &bytes[]){ArrayFree(bytes);int f=FileOpen(path,FILE_READ|FILE_BIN);if(f==INVALID_HANDLE)return false;ulong sz=FileSize(f);if(sz==0||sz>(ulong)limit||ArrayResize(bytes,(int)sz)!=(int)sz){FileClose(f);return false;}uint n=FileReadArray(f,bytes,0,(int)sz);FileClose(f);return n==(uint)sz;}
bool HG6WriteFile(string path,const uchar &bytes[]){int f=FileOpen(path,FILE_WRITE|FILE_BIN);if(f==INVALID_HANDLE)return false;uint n=FileWriteArray(f,bytes,0,ArraySize(bytes));FileFlush(f);FileClose(f);if(n!=(uint)ArraySize(bytes))return false;uchar check[];return HG6ReadFile(path,HG6_MAX_ENVELOPE,check)&&HG6BytesEqual(bytes,check);}
// SECTION S2: fixed-width envelope [sha32][magic,version,generation,len,identity32,payload].
class HG6Store {
 string stem;uchar identity[];long gen;bool ready,damaged;
 bool Decode(const uchar &x[],long &g,uchar &payload[]){
  int n=ArraySize(x);if(n<96||n>HG6_MAX_ENVELOPE)return false;uchar body[],digest[];if(ArrayResize(body,n-32)!=n-32||ArrayCopy(body,x,0,32,n-32)!=n-32||!HG6Hash(body,digest))return false;
  for(int i=0;i<32;i++)if(x[i]!=digest[i])return false;
  if(HG6Get64(body,0)!=0x4847365354415445||HG6Get64(body,8)!=1)return false;
  g=HG6Get64(body,16);long len=HG6Get64(body,24);if(g<=0||len<=0||len!=(long)ArraySize(body)-64)return false;
  for(int i=0;i<32;i++)if(body[32+i]!=identity[i])return false;
  if(ArrayResize(payload,(int)len)!=(int)len||ArrayCopy(payload,body,0,64,(int)len)!=(int)len)return false;return true;
 }
 string Slot(int i)const{return stem+"."+IntegerToString(i)+".bin";}
 string Marker()const{return stem+".genesis";}
 public:
 HG6Store(){gen=0;ready=false;damaged=false;}
 bool Init(string name,const uchar &id[]){if(ready||StringLen(name)==0||ArraySize(id)!=32)return false;stem=name;if(ArrayResize(identity,32)!=32||ArrayCopy(identity,id,0,0,32)!=32)return false;ready=true;return true;}
 // Returns 0 new, 1 recovered, -1 invalid. A damaged slot is latched even with valid fallback.
 int Load(uchar &payload[]){
  if(!ready)return -1;uchar a[],b[],x[],y[];long ga=0,gb=0;
  bool ea=FileIsExist(Slot(0)),eb=FileIsExist(Slot(1)),em=FileIsExist(Marker());
  uchar marker[];if(em&&(!HG6ReadFile(Marker(),32,marker)||!HG6BytesEqual(marker,identity))){damaged=true;return -1;}
  // Existing snapshots from older build schemas are not silently adopted.
  if(!em&&(ea||eb)){damaged=true;return -1;}
  if(em&&!ea&&!eb){damaged=true;return -1;}
  bool va=ea&&HG6ReadFile(Slot(0),HG6_MAX_ENVELOPE,a)&&Decode(a,ga,x)&&ga%2==0;
  bool vb=eb&&HG6ReadFile(Slot(1),HG6_MAX_ENVELOPE,b)&&Decode(b,gb,y)&&gb%2==1;
  damaged=(ea&&!va)||(eb&&!vb)||(va&&!eb)||(vb&&!ea&&gb!=1);if(!va&&!vb)return ea||eb?-1:0;
  if(va&&vb&&((ga==gb)||MathAbs((double)(ga-gb))!=1.0)){damaged=true;return -1;}
  bool choose=va&&(!vb||ga>gb);gen=choose?ga:gb;int n=choose?ArraySize(x):ArraySize(y);if(ArrayResize(payload,n)!=n)return -1;
  if((choose?ArrayCopy(payload,x,0,0,n):ArrayCopy(payload,y,0,0,n))!=n)return -1;return 1;
 }
 bool Save(const uchar &payload[]){
  int n=ArraySize(payload);if(!ready||damaged||n<=0||n>HG6_MAX_ENVELOPE-96||gen>=0x7ffffffffffffffe)return false;
  uchar body[],digest[],out[],check[];if(ArrayResize(body,n+64)!=n+64)return false;
  HG6Put64(body,0,0x4847365354415445);HG6Put64(body,8,1);HG6Put64(body,16,gen+1);HG6Put64(body,24,n);
  if(ArrayCopy(body,identity,32,0,32)!=32||ArrayCopy(body,payload,64,0,n)!=n||!HG6Hash(body,digest)||ArrayResize(out,n+96)!=n+96||ArrayCopy(out,digest,0,0,32)!=32||ArrayCopy(out,body,32,0,n+64)!=n+64)return false;
  if(gen==0&&!HG6WriteFile(Marker(),identity)){damaged=true;return false;}
  if(!HG6WriteFile(Slot((int)((gen+1)%2)),out)){damaged=true;return false;}long g=0;if(!Decode(out,g,check)||g!=gen+1||!HG6BytesEqual(payload,check)){damaged=true;return false;}gen=g;return true;
 }
 bool Healthy()const{return ready&&!damaged;}
 long Generation()const{return gen;}
};
#endif
