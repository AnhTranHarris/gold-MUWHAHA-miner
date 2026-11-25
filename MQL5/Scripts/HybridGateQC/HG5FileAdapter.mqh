#ifndef HG5_FILE_ADAPTER_MQH
#define HG5_FILE_ADAPTER_MQH
#include "HG5PackedCore.mqh"
// Expected digest supplied by frozen manifest. No orders, no networking.
bool HG5ReadVerified(const string path,const string expected,const int max_bytes,uchar &data[]){
 ArrayFree(data);int h=FileOpen(path,FILE_READ|FILE_BIN);if(h==INVALID_HANDLE)return false;
 ulong len=FileSize(h);if(len==0||len>(ulong)max_bytes){FileClose(h);return false;}
 int n=(int)len;if(ArrayResize(data,n)!=n){FileClose(h);return false;}
 uint got=FileReadArray(h,data,0,n);FileClose(h);if(got!=(uint)n){ArrayFree(data);return false;}
 uchar key[];uchar digest[];ArrayResize(key,0);
 if(CryptEncode(CRYPT_HASH_SHA256,data,key,digest)!=32){ArrayFree(data);return false;}
 string hex="";for(int i=0;i<32;i++)hex+=StringFormat("%02x",(uint)digest[i]);
 if(hex!=expected){ArrayFree(data);return false;}return true;
}
#endif
