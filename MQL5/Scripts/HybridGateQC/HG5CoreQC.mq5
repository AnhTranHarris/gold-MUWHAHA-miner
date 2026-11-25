#property strict
#property description "HybridGate V1 integrated offline QC candidate. No order APIs."
#include "HG5FileAdapter.mqh"
#include "HG5QCManifest.mqh"
#include "HG5Core.mqh"
#include "HG5CoreFixtureManifest.mqh"
ulong HGQRead(const uchar &b[],int p,int n){ulong v=0;for(int i=0;i<n;i++)v|=((ulong)b[p+i])<<(8*i);return v;}
long HGQL(const uchar &b[],int p){return (long)HGQRead(b,p,8);}
int HGQI(const uchar &b[],int p){return (int)(uint)HGQRead(b,p,4);}
float HGQF(const uchar &b[],int p){HGFloatBits v;v.u=(uint)HGQRead(b,p,4);return v.f;}
double HGQD(const uchar &b[],int p){HGDoubleBits v;v.u=HGQRead(b,p,8);return v.d;}
HG5Core core;
// Fixture integrity and fixed size layout checked BEFORE any offset reads.
bool HGQTest(){uchar data[],bytes[];if(!HG5ReadVerified("HG5QC\\HG5CoreFixture.bin",HG5_CORE_FIXTURE_SHA,16777216,data)||ArraySize(data)<36)return false;
 if(HGQI(data,0)!=1362446152||HGQI(data,4)!=1)return false;
 int n=HGQI(data,8),nw=HGQI(data,12),ns=HGQI(data,16),np=HGQI(data,20),nh=HGQI(data,24),na=HGQI(data,28),cap=HGQI(data,32);
 if(n<=0||n>262144||nw<=0||nw>2048||ns<0||np<0||nh<0||na<0||ns>n*4||np>n||nh>n*3||na>n*12||cap!=32768)return false;
 long size=36+(long)n*16+(long)nw*32+(long)ns*44+(long)np*32+(long)nh*52+(long)na*32+12*12*8+12*331*8+64;if(size!=ArraySize(data))return false;
 int qp=36,wp=qp+16*n,sp=wp+32*nw,cf=sp+40*ns,pp=cf+4*ns,hp=pp+32*np,hi=hp+40*nh,ap=hi+12*nh,vp=ap+32*na,zp=vp+12*12*8,cp=zp+12*331*8;
 for(int i=0;i<88;i++){if(!HG5ReadVerified("HG5QC\\"+HG_ID[i]+".hg5p",HG_MODEL_SHA[i],67108864,bytes)||!core.Load(i,bytes)){PrintFormat("HG5CoreQC model fail %d",i);return false;}ArrayFree(bytes);}
 HG5Window w[];if(ArrayResize(w,nw)!=nw)return false;for(int i=0;i<nw;i++){int p=wp+32*i;w[i].open_ms=HGQL(data,p);w[i].block_ms=HGQL(data,p+8);w[i].flatten_ms=HGQL(data,p+16);w[i].close_ms=HGQL(data,p+24);}if(!core.Start(w,cap))return false;
 int si=0,pi=0,he=0,ae=0;HG5Quote g[];HG5StageEvent s[];HG5Proposal r[];HG5PathEvent h[];HG5AccountEvent a[];ulong started=GetMicrosecondCount();
 for(int lo=0;lo<n;){if(IsStopped())return false;int end=lo+1;long ms=HGQL(data,qp+16*lo);while(end<n&&HGQL(data,qp+16*end)==ms)end++;if(ArrayResize(g,end-lo)!=end-lo)return false;for(int k=lo;k<end;k++){int p=qp+16*k;g[k-lo].ms=HGQL(data,p);g[k-lo].bid=HGQI(data,p+8);g[k-lo].ask=HGQI(data,p+12);}if(!core.StepGroup(g,s,r,h,a)){PrintFormat("HG5CoreQC step fail %d",lo);return false;}
  for(int i=0;i<ArraySize(s);i++){if(si>=ns)return false;int p=sp+40*si;if(s[i].stage!=HGQL(data,p)||s[i].ms!=HGQL(data,p+8)||s[i].side!=HGQL(data,p+16)||s[i].rank!=HGQL(data,p+24)||s[i].source!=HGQL(data,p+32)||s[i].confidence!=HGQF(data,cf+4*si)){PrintFormat("HG5CoreQC stage mismatch %d quote %d",si,lo);return false;}si++;}
  for(int i=0;i<ArraySize(r);i++){if(pi>=np)return false;int p=pp+32*pi;if(r[i].id!=HGQL(data,p)||r[i].t!=HGQL(data,p+8)||r[i].side!=HGQL(data,p+16)||r[i].origin!=HGQL(data,p+24))return false;pi++;}
  for(int i=0;i<ArraySize(h);i++){if(he>=nh)return false;int p=hp+40*he;if(h[i].id!=HGQL(data,p)||h[i].ordinal!=HGQL(data,p+8)||h[i].kind!=HGQL(data,p+16)||h[i].why!=HGQL(data,p+24)||h[i].net!=HGQL(data,p+32)||h[i].h4!=HGQF(data,hi+12*he)||h[i].v4!=HGQF(data,hi+12*he+4)||h[i].h5!=HGQF(data,hi+12*he+8)){PrintFormat("HG5CoreQC path mismatch %d",he);return false;}he++;}
  for(int i=0;i<ArraySize(a);i++){if(ae>=na)return false;int p=ap+32*ae;if(a[i].id!=HGQL(data,p)||a[i].ordinal!=HGQL(data,p+8)||a[i].account!=HGQL(data,p+16)||a[i].kind!=HGQL(data,p+24))return false;ae++;}lo=end;
 }
 if(si!=ns||pi!=np||he!=nh||ae!=na)return false;double v[];long z[];for(int k=0;k<12;k++){if(!core.Snapshot(k,v,z))return false;for(int i=0;i<12;i++)if(v[i]!=HGQD(data,vp+8*(k*12+i)))return false;for(int i=0;i<331;i++)if(z[i]!=HGQL(data,zp+8*(k*331+i)))return false;}if(!core.Stats(z))return false;for(int i=0;i<8;i++)if(z[i]!=HGQL(data,cp+8*i))return false;
 PrintFormat("HG5CoreQC quotes=%d stages=%d proposals=%d path_events=%d account_events=%d elapsed_us=%I64u",n,si,pi,he,ae,GetMicrosecondCount()-started);return true;
}
void OnStart(){Print(HGQTest()?"HG5CoreQC PASS":"HG5CoreQC FAIL");}
