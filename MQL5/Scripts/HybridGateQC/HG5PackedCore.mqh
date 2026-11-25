#ifndef HG5_PACKED_CORE_MQH
#define HG5_PACKED_CORE_MQH
// Non-trading candidate. HG5P v1; actual MetaEditor compilation pending.
union HGDoubleBits { ulong u; double d; };
union HGFloatBits { uint u; float f; };
class HG5PackedCore {
private:
 uchar buf[];
 int offsets[];
 int counts[];
 int nf,nc,nt,objective;
 double sigmoid;
 bool ready;
 uint U32(const int p) const {uint v=0;for(int k=0;k<4;k++)v|=((uint)buf[p+k])<<(8*k);return v;}
 int I32(const int p) const {return (int)U32(p);}
 ulong U64(const int p) const {ulong v=0;for(int k=0;k<8;k++)v|=((ulong)buf[p+k])<<(8*k);return v;}
 double F64(const int p) const {HGDoubleBits x;x.u=U64(p);return x.d;}
 bool NaN64(const ulong x) const {return ((x>>52)&2047)==2047 && (x&0x000FFFFFFFFFFFFF)!=0;}
 bool Finite64(const ulong x) const {return ((x>>52)&2047)!=2047;}
 bool Fail(){Clear();return false;}
public:
 HG5PackedCore(){ready=false;nf=0;nc=0;nt=0;objective=0;sigmoid=0;}
 void Clear(){ready=false;ArrayFree(buf);ArrayFree(offsets);ArrayFree(counts);nf=0;nc=0;nt=0;objective=0;sigmoid=0;}
 int Features() const {return ready?nf:0;}
 int Outputs() const {return ready?nc:0;}
 bool LoadBytes(const uchar &src[]){
  Clear();int len=ArraySize(src);if(len<32||len>67108864)return false;
  if(ArrayResize(buf,len)!=len||ArrayCopy(buf,src,0,0,len)!=len)return Fail();
  if(buf[0]!=72||buf[1]!=71||buf[2]!=53||buf[3]!=80||U32(4)!=1)return Fail();
  nf=I32(8);nc=I32(12);nt=I32(16);objective=I32(20);sigmoid=F64(24);
  if(nf<1||nf>4096||nc<1||nc>64||nt<1||nt>100000||nt%nc!=0||objective<0||objective>2||((objective==2)!=(nc>1))||!Finite64(U64(24))||sigmoid<=0)return Fail();
  if(ArrayResize(offsets,nt)!=nt||ArrayResize(counts,nt)!=nt)return Fail();
  int p=32;
  for(int t=0;t<nt;t++){
   if(len-p<4)return Fail();
   int n=I32(p);p+=4;if(n<0||n>65535||len-p<27*n+8)return Fail();
   offsets[t]=p;counts[t]=n;int flagp=p+2*n,lp=p+3*n,rp=p+7*n,tp=p+11*n,yp=p+19*n;
   for(int i=0;i<n;i++){
    int f=(int)buf[p+2*i]+256*(int)buf[p+2*i+1],flag=(int)buf[flagp+i],l=I32(lp+4*i),r=I32(rp+4*i);
    if(f>=nf||(flag!=2&&flag!=8&&flag!=10)||NaN64(U64(tp+8*i))||l>=n||r>=n||l< -n-1||r< -n-1)return Fail();
   }
   for(int i=0;i<=n;i++)if(!Finite64(U64(yp+8*i)))return Fail();
   uchar visited[];uchar leaves[];int stack[];
   if(ArrayResize(visited,n)!=n||ArrayResize(leaves,n+1)!=n+1||ArrayResize(stack,n+2)!=n+2)return Fail();
   ArrayInitialize(visited,0);ArrayInitialize(leaves,0);int sp=1,ns=0,nl=0;stack[0]=(n==0?-1:0);
   while(sp>0){int j=stack[--sp];if(j<0){int leaf=~j;if(leaf>n||leaves[leaf]!=0)return Fail();leaves[leaf]=1;nl++;}
    else{if(j>=n||visited[j]!=0||sp+2>n+2)return Fail();visited[j]=1;ns++;stack[sp++]=I32(lp+4*j);stack[sp++]=I32(rp+4*j);}}
   if(ns!=n||nl!=n+1)return Fail();
   p+=27*n+8;
  }
  if(p!=len)return Fail();
  ready=true;return true;
 }
 bool Predict(const float &x[],double &y[],const bool raw=false) const {
  if(!ready||ArraySize(x)!=nf||ArrayResize(y,nc)!=nc)return false;
  ArrayInitialize(y,0.0);
  for(int t=0;t<nt;t++){
   int p=offsets[t],n=counts[t],j=(n==0?-1:0),steps=0;
   while(j>=0){if(j>=n||++steps>n)return false;
    int f=(int)buf[p+2*j]+256*(int)buf[p+2*j+1],flag=(int)buf[p+2*n+j];double threshold=F64(p+11*n+8*j);
    HGFloatBits fb;fb.f=x[f];uint bits=fb.u;bool nan=((bits>>23)&255)==255&&(bits&0x007FFFFF)!=0;bool left=false;
    if(nan)left=(flag&8)!=0?((flag&2)!=0):(0.0<=threshold);
    else{double v=(double)x[f];if(MathAbs(v)<=(double)(float)1e-35)v=0.0;left=v<=threshold;}
    j=I32(p+(left?3:7)*n+4*j);
   }
   y[t%nc]+=F64(p+19*n+8*(~j));
  }
  if(!raw&&objective==1)y[0]=1.0/(1.0+MathExp(-sigmoid*y[0]));
  else if(!raw&&objective==2){double m=y[0],s=0;for(int c=1;c<nc;c++)if(y[c]>m)m=y[c];for(int c=0;c<nc;c++){y[c]=MathExp(y[c]-m);s+=y[c];}if(s<=0)return false;for(int c=0;c<nc;c++)y[c]/=s;}
  for(int c=0;c<nc;c++)if(!MathIsValidNumber(y[c]))return false;
  return true;
 }
};
#endif
