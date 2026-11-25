#ifndef HG5_STATE_CODEC_MQH
#define HG5_STATE_CODEC_MQH
#include "HG5PackedCore.mqh"
#define HG5_STATE_MAX 16777216
// Little-endian, bounded field codec. Integrity/authentication is the external envelope's responsibility.
class HG5StateCodec{
 uchar b[];int pos,limit;bool reading,ok;
 bool Bits(ulong &v,int n){if(!ok||n<1||n>8||pos>limit-n){ok=false;return false;}if(reading){v=0;for(int i=0;i<n;i++)v|=((ulong)b[pos+i])<<(8*i);}else for(int i=0;i<n;i++)b[pos+i]=(uchar)(v>>(8*i));pos+=n;return true;}
public:
 HG5StateCodec(){pos=limit=0;reading=false;ok=false;}
 bool BeginWrite(){reading=false;pos=0;limit=HG5_STATE_MAX;ok=ArrayResize(b,limit)==limit;return ok;}
 bool BeginRead(const uchar &x[]){reading=true;pos=0;limit=ArraySize(x);ok=limit>0&&limit<=HG5_STATE_MAX;if(!ok)return false;ok=ArrayResize(b,limit)==limit&&ArrayCopy(b,x,0,0,limit)==limit;return ok;}
 bool Reading()const{return reading;}
 bool I64(long &v){ulong u=reading?0:(ulong)v;if(!Bits(u,8))return false;if(reading)v=(long)u;return true;}
 bool I32(int &v){ulong u=reading?0:(uint)v;if(!Bits(u,4))return false;if(reading)v=(int)(uint)u;return true;}
 bool F32(float &v){HGFloatBits x;if(!reading)x.f=v;ulong u=reading?0:x.u;if(!Bits(u,4))return false;if(reading){x.u=(uint)u;v=x.f;}return true;}
 bool F64(double &v){HGDoubleBits x;if(!reading)x.d=v;ulong u=reading?0:x.u;if(!Bits(u,8))return false;if(reading){x.u=u;v=x.d;}return true;}
 bool Flag(bool &v){ulong u=reading?0:(v?1:0);if(!Bits(u,1)||u>1){ok=false;return false;}if(reading)v=u!=0;return true;}
 bool Finish(uchar &x[]){if(!ok||reading||ArrayResize(x,pos)!=pos)return false;return ArrayCopy(x,b,0,0,pos)==pos;}
 bool Done()const{return ok&&reading&&pos==limit;}
};
#endif
