#ifndef HG5_RX136_MQH
#define HG5_RX136_MQH
#include "HG5StateCodec.mqh"
// Original Stage4 RX136 feature calculation, local retained indices.
// Caller must guarantee chronological validated quotes and stable ordinal identity.
// This is not the live tick adapter. No future quotes are used.
struct HG5Quote {long ms;int bid,ask;
 void ZeroFields(){{ms=0;}{bid=0;}{ask=0;}}
 bool StateFields(HG5StateCodec &codec){{if(!codec.I64(ms))return false;}{if(!codec.I32(bid))return false;}{if(!codec.I32(ask))return false;}return true;}
};
double HG5Mid(const HG5Quote &q){return ((double)q.bid+(double)q.ask)*0.5;}
int HG5Prev(const HG5Quote &q[],const int e,const long time){int lo=0,hi=e+1;while(lo<hi){int m=lo+(hi-lo)/2;if(q[m].ms<=time)lo=m+1;else hi=m;}return lo>0?lo-1:0;}
bool HG5RXFeatures(const HG5Quote &q[],const int n,const int e,const int s,const int p,const long base_ordinal,float &f[]){
 if(n<=0||n>ArraySize(q)||e<0||e>=n||p<0||p>e||base_ordinal<0||(s!=1&&s!=-1))return false;
 // Do not silently clamp at a retired ring edge. At true chronology start, the source clamps to index 0.
 if(base_ordinal>0&&(e<256||q[0].ms>q[e].ms-900000))return false;
 if(ArrayResize(f,136)!=136)return false;
 int z=0;double m=HG5Mid(q[e]);f[z++]=(float)s;f[z++]=(float)(q[e].ask-q[e].bid);f[z++]=(float)(m/100.0);f[z++]=(float)(q[e].ms-q[p].ms);f[z++]=(float)(s*(m-HG5Mid(q[p])));f[z++]=(float)(q[p].ask-q[p].bid);
 int horizons[8]={250,1000,3000,8000,20000,60000,180000,900000};
 for(int k=0;k<8;k++){
  int h=horizons[k],l=HG5Prev(q,e,q[e].ms-h);double lo=m,hi=m,travel=0,rv=0,mean=0,sq=0,sp=0,agree=0,rev=0,weighted=0,wt=0;int old=0;double last=HG5Mid(q[l]);
  for(int j=l;j<=e;j++){
   double v=HG5Mid(q[j]),d=v-m;lo=MathMin(lo,v);hi=MathMax(hi,v);mean+=d;sq+=d*d;sp+=q[j].ask-q[j].bid;
   if(j>l){double ch=v-last,dt=(double)(q[j].ms-q[j-1].ms);int sg=(int)(ch>0)-(int)(ch<0);if(sg&&old&&sg!=old)rev++;if(sg)old=sg;travel+=MathAbs(ch);rv+=ch*ch;weighted+=(last-m)*dt;wt+=dt;long db=(long)s*((long)q[j].bid-q[j-1].bid),da=(long)s*((long)q[j].ask-q[j-1].ask);agree+=(int)(db>0&&da>0)-(int)(db<0&&da<0);}
   last=v;
  }
  double c=e-l+1,mu=mean/c,sd=MathSqrt(MathMax(0.0,sq/c-mu*mu));f[z++]=(float)(s*(m-HG5Mid(q[l])));f[z++]=(float)(hi-lo);f[z++]=(float)(s>0?(m-lo)/(hi-lo+1):(hi-m)/(hi-lo+1));f[z++]=(float)(-s*mu/(sd+1));f[z++]=(float)sd;f[z++]=(float)MathSqrt(rv);f[z++]=(float)(s*(m-HG5Mid(q[l]))/(travel+1));f[z++]=(float)(c/(h*.001));f[z++]=(float)(sp/c);f[z++]=(float)(agree/c);f[z++]=(float)(rev/c);f[z++]=(float)(-s*weighted/(wt+1));
 }
 int lags[8]={2,4,8,16,32,64,128,256};for(int k=0;k<8;k++){int l=e>lags[k]?e-lags[k]:0;double d=(double)(q[e].ms-q[l].ms);f[z++]=(float)(d/(e-l+1));f[z++]=(float)((long)s*((long)q[e].bid-q[l].bid));f[z++]=(float)((long)s*((long)q[e].ask-q[l].ask));f[z++]=(float)((q[e].ask-q[e].bid)-(q[l].ask-q[l].bid));}
 f[z++]=(float)((long)s*((long)q[e].bid-q[p].bid));f[z++]=(float)((long)s*((long)q[e].ask-q[p].ask));return z==136;
}
#endif
