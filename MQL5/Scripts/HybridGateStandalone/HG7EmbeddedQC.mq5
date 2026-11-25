#property strict
#property description "Standalone embedded model inference QA. No trading calls."
#include <HybridGateV1/HG5FileAdapter.mqh>
#include <HybridGateV1/HG7EmbeddedModels.mqh>
#include <HybridGateV1/HG5QCManifest.mqh>
uint HGReadU32(const uchar &b[],const int p){uint u=0;for(int k=0;k<4;k++)u|=((uint)b[p+k])<<(8*k);return u;}
float HGReadF32(const uchar &b[],const int p){HGFloatBits u;u.u=HGReadU32(b,p);return u.f;}
double HGReadF64(const uchar &b[],const int p){HGDoubleBits u;u.u=0;for(int k=0;k<8;k++)u.u|=((ulong)b[p+k])<<(8*k);return u.d;}
bool HGTest(const int i,long &rawdiff,long &f32diff,long &scorediff,double &maxerr,long &rows){
 uchar b[];uchar f[];HG5PackedCore m;string prefix="HG5QC\\"+HG_ID[i];
 if(!HG7ReadEmbedded(i,HG_MODEL_SHA[i],b)||!m.LoadBytes(b))return false;
 ArrayFree(b);if(!HG5ReadVerified(prefix+".hg5f",HG_FIXTURE_SHA[i],67108864,f))return false;
 int n=HG_ROWS[i],w=HG_WIDTH[i],o=HG_OUTPUTS[i];long expected=20+(long)n*w*4+(long)n*o*16;
 if(ArraySize(f)!=expected||f[0]!=72||f[1]!=71||f[2]!=53||f[3]!=70||HGReadU32(f,4)!=1||HGReadU32(f,8)!=(uint)n||HGReadU32(f,12)!=(uint)w||HGReadU32(f,16)!=(uint)o||m.Features()!=w||m.Outputs()!=o)return false;
 float x[];double y[];if(ArrayResize(x,w)!=w)return false;int p=20+n*w*4,q=p+n*o*8;
 ulong start=GetMicrosecondCount();
 for(int j=0;j<n;j++){
  if(IsStopped())return false;
  for(int k=0;k<w;k++)x[k]=HGReadF32(f,20+4*(j*w+k));
  if(!m.Predict(x,y,true))return false;
  for(int k=0;k<o;k++)if(y[k]!=HGReadF64(f,q+8*(j*o+k)))rawdiff++;
  if(!m.Predict(x,y,false))return false;
  for(int k=0;k<o;k++){double z=HGReadF64(f,p+8*(j*o+k));if(y[k]!=z)scorediff++;if((float)y[k]!=(float)z)f32diff++;maxerr=MathMax(maxerr,MathAbs(y[k]-z));}
 }
 rows+=n;PrintFormat("HG7QC head=%s rows=%d elapsed_us=%I64u",HG_ID[i],n,GetMicrosecondCount()-start);return true;
}
void OnStart(){long rd=0,fd=0,sd=0,rows=0;double err=0;int n=ArraySize(HG_ID);if(n!=88||ArraySize(HG_MODEL_SHA)!=88){Print("HG7QC FAIL model manifest");return;}for(int i=0;i<n;i++)if(!HGTest(i,rd,fd,sd,err,rows)){PrintFormat("HG7QC FAIL head=%s",HG_ID[i]);return;}PrintFormat("HG7QC %s heads=%d rows=%I64d raw_diff=%I64d float32_diff=%I64d score_diff=%I64d max_error=%.17g",(rd==0&&fd==0&&err<=1e-14?"PASS":"FAIL"),n,rows,rd,fd,sd,err);}
