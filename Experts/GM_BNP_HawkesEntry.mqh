#ifndef __GM_BNP_HAWKES_ENTRY_MQH__
#define __GM_BNP_HAWKES_ENTRY_MQH__
// R9 causal sub-minute entry v1. An untrained model fails closed.
// Feature 7 = quote-update-weighted average PRICE, not true traded VWAP.
#define BNP_CLOCKS 7
#define BNP_FEATURES 11
#define BNP_BARS 64
#define BNP_GAP_RESET_MS 15000

struct BNPBar
{
   long begin_ms;
   double o,h,l,c;
   int observations;
};
struct BNPClockFeatures
{
   double impulse,efficiency,atr_accel,rsi,boll,qwap,fib,atr;
};

class CBNPClock
{
private:
   long m_width,m_bucket;
   double m_o,m_h,m_l,m_c;
   int m_observations,m_head,m_count;
   BNPBar m_bars[BNP_BARS];
   bool m_cache_valid;
   BNPClockFeatures m_cache;
public:
   void Init(const long width) {m_width=width;Reset();}
   void Reset()
   {
      m_bucket=-1;m_o=0;m_h=0;m_l=0;m_c=0;
      m_observations=0;m_head=0;m_count=0;m_cache_valid=false;
   }
   void Add(const long ms,const double mid)
   {
      long bucket=ms/m_width*m_width;
      if(m_bucket<0)
      {
         m_bucket=bucket;m_o=mid;m_h=mid;m_l=mid;m_c=mid;m_observations=1;return;
      }
      if(bucket<m_bucket)return;
      if(bucket!=m_bucket)
      {
         m_bars[m_head].begin_ms=m_bucket;
         m_bars[m_head].o=m_o;m_bars[m_head].h=m_h;
         m_bars[m_head].l=m_l;m_bars[m_head].c=m_c;
         m_bars[m_head].observations=m_observations;
         m_head=(m_head+1)%BNP_BARS;
         if(m_count<BNP_BARS)m_count++;
         m_bucket=bucket;m_o=mid;m_h=mid;m_l=mid;m_c=mid;
         m_observations=1;m_cache_valid=false;
      }
      else
      {
         if(mid>m_h)m_h=mid;
         if(mid<m_l)m_l=mid;
         m_c=mid;m_observations++;
      }
   }
   bool Get(const long ms,BNPClockFeatures &out)
   {
      if(m_count<34)return false;
      int last=(m_head+BNP_BARS-1)%BNP_BARS;
      if(ms-(m_bars[last].begin_ms+m_width)>3*m_width)return false;
      if(m_cache_valid){out=m_cache;return true;}
      int n=m_count;
      double cl[BNP_BARS],hi[BNP_BARS],lo[BNP_BARS];
      int obs[BNP_BARS];
      for(int i=0;i<n;i++)
      {
         int idx=(m_head+BNP_BARS-n+i)%BNP_BARS;
         cl[i]=m_bars[idx].c;hi[i]=m_bars[idx].h;
         lo[i]=m_bars[idx].l;obs[i]=m_bars[idx].observations;
      }
      double trlast=0.0,trold=0.0;
      for(int j=n-28;j<n;j++)
      {
         double tr=MathMax(hi[j]-lo[j],MathMax(MathAbs(hi[j]-cl[j-1]),MathAbs(lo[j]-cl[j-1])));
         if(j>=n-14)trlast+=tr;else trold+=tr;
      }
      double atr=trlast/14.0+1e-8;
      double oldatr=trold/14.0+1e-8;
      double travel=0.0;
      for(int j=n-4;j<n;j++)travel+=MathAbs(cl[j]-cl[j-1]);
      double displacement=cl[n-1]-cl[n-5];
      double up=0.0,down=0.0;
      for(int j=n-14;j<n;j++)
      {
         double d=cl[j]-cl[j-1];
         if(d>0)up+=d;else down-=d;
      }
      double mean=0.0;
      for(int j=n-20;j<n;j++)mean+=cl[j];
      mean/=20.0;
      double var=0.0;
      for(int j=n-20;j<n;j++)var+=(cl[j]-mean)*(cl[j]-mean);
      var/=20.0;
      double wsum=0.0,wn=0.0;
      for(int j=n-20;j<n;j++){wsum+=cl[j]*obs[j];wn+=obs[j];}
      double bottom=DBL_MAX,top=-DBL_MAX;
      for(int j=n-34;j<n;j++)
      {
         if(lo[j]<bottom)bottom=lo[j];
         if(hi[j]>top)top=hi[j];
      }
      out.impulse=displacement/atr;
      out.efficiency=MathAbs(displacement)/(travel+1e-9);
      out.atr_accel=atr/oldatr-1.0;
      out.rsi=(up-down)/(up+down+1e-9);
      out.boll=(cl[n-1]-mean)/(2.0*MathSqrt(var)+1e-8);
      out.qwap=(cl[n-1]-wsum/MathMax(1.0,wn))/atr;
      out.fib=2.0*(cl[n-1]-bottom)/(top-bottom+1e-9)-1.0;
      out.atr=atr;
      m_cache=out;m_cache_valid=true;return true;
   }
};

class CBNPHawkesEntry
{
private:
   CBNPClock m_clock[BNP_CLOCKS];
   long m_last_ms;
   double m_last_mid,m_ex_up,m_ex_down;
   double m_prior,m_threshold,m_weights[BNP_FEATURES][5];
   bool m_model_ready;
   int m_evaluations,m_gaps;
   double Bound(const double x) {return MathMin(1.0,MathMax(-1.0,x));}
   int Bin(const double x)
   {
      int b=0;
      if(x>-.6)b++;if(x>-.2)b++;if(x>.2)b++;if(x>.6)b++;
      return b;
   }
public:
   void Init()
   {
      m_clock[0].Init(250);m_clock[1].Init(500);m_clock[2].Init(1000);
      m_clock[3].Init(5000);m_clock[4].Init(15000);
      m_clock[5].Init(30000);m_clock[6].Init(45000);
      m_last_ms=-1;m_last_mid=0.0;m_ex_up=0.0;m_ex_down=0.0;
      m_model_ready=false;m_prior=0.0;m_threshold=0.0;
      m_evaluations=0;m_gaps=0;
   }
   bool Ready(){return m_model_ready;}
   int Gaps(){return m_gaps;}
   int Evaluations(){return m_evaluations;}
   void UpdateQuote(const MqlTick &t)
   {
      long ms=t.time_msc;
      if(t.bid<=0.0 || t.ask<t.bid || (m_last_ms>=0 && ms<m_last_ms))return;
      double mid=(t.bid+t.ask)*0.5;
      if(m_last_ms>=0)
      {
         long elapsed=ms-m_last_ms;
         if(elapsed>BNP_GAP_RESET_MS)
         {
            for(int k=0;k<BNP_CLOCKS;k++)m_clock[k].Reset();
            m_ex_up=0;m_ex_down=0;m_gaps++;
         }
         else
         {
            double decay=MathExp(-4.0*elapsed/1000.0);
            m_ex_up*=decay;m_ex_down*=decay;
            double move=mid-m_last_mid;
            if(move>.005){m_ex_up+=.7;m_ex_down+=.2;}
            else if(move<-.005){m_ex_down+=.7;m_ex_up+=.2;}
         }
      }
      m_last_ms=ms;m_last_mid=mid;
      for(int k=0;k<BNP_CLOCKS;k++)m_clock[k].Add(ms,mid);
   }
   bool Candidate(const MqlTick &t,const double max_spread,int &side,int &bins[],double &features[])
   {
      side=0;
      if(t.bid<=0.0 || t.ask<t.bid || t.ask-t.bid>max_spread+1e-9)return false;
      BNPClockFeatures f[BNP_CLOCKS];
      for(int k=0;k<BNP_CLOCKS;k++)if(!m_clock[k].Get(t.time_msc,f[k]))return false;
      double up=.5+m_ex_up,down=.5+m_ex_down;
      double pressure=(up-down)/(up+down),burst=(up+down-1.0)/(up+down);
      double wt[BNP_CLOCKS]={.32,.24,.18,.12,.07,.045,.025};
      double dirscore=.6*pressure;
      for(int k=0;k<BNP_CLOCKS;k++)dirscore+=wt[k]*f[k].impulse;
      if(MathAbs(dirscore)<.35)return false;
      side=(dirscore>0?1:-1);
      double sw[4]={.4,.3,.2,.1};
      double impulse=0,eff=0,accel=0,rsi=0,boll=0,qwap=0,fib=0;
      for(int k=0;k<4;k++)
      {
         impulse+=sw[k]*f[k].impulse;eff+=sw[k]*f[k].efficiency;
         accel+=sw[k]*f[k].atr_accel;rsi+=sw[k]*f[k].rsi;
         boll+=sw[k]*f[k].boll;qwap+=sw[k]*f[k].qwap;
         fib+=sw[k]*f[k].fib;
      }
      double vote=0.0;
      for(int k=0;k<BNP_CLOCKS;k++)vote+=(side*f[k].impulse>0?1.0:-1.0);
      vote/=BNP_CLOCKS;
      ArrayResize(bins,BNP_FEATURES);ArrayResize(features,BNP_FEATURES);
      features[0]=Bound(side*impulse/3.0);
      features[1]=Bound(2.0*eff-1.0);
      features[2]=Bound(side*pressure);
      features[3]=Bound(2.0*burst-1.0);
      features[4]=Bound(accel/2.0);
      features[5]=Bound(side*rsi);
      features[6]=Bound(side*boll/2.0);
      features[7]=Bound(side*qwap/3.0);
      features[8]=Bound(side*fib);
      features[9]=Bound(side*vote);
      features[10]=Bound((.12-(t.ask-t.bid))/.12);
      for(int i=0;i<BNP_FEATURES;i++)bins[i]=Bin(features[i]);
      m_evaluations++;return true;
   }
   bool LoadModel(const string filename)
   {
      m_model_ready=false;
      int h=FileOpen(filename,FILE_READ|FILE_CSV|FILE_COMMON|FILE_ANSI,',');
      if(h==INVALID_HANDLE)return false;
      string head=FileReadString(h),version=FileReadString(h);
      if(head!="version" || version!="r9_bnp_hawkes_entry_v1_20261101")
      {FileClose(h);return false;}
      int nseen=0;bool p=false,th=false;
      bool seen[BNP_FEATURES][5];
      for(int i=0;i<BNP_FEATURES;i++)for(int b=0;b<5;b++)seen[i][b]=false;
      while(!FileIsEnding(h))
      {
         string key=FileReadString(h);
         if(FileIsEnding(h) && key=="")break;
         string value=FileReadString(h);
         if(key=="prior"){m_prior=StringToDouble(value);p=true;}
         else if(key=="threshold"){m_threshold=StringToDouble(value);th=true;}
         else if(StringLen(key)==5 && StringSubstr(key,0,1)=="w")
         {
            int f=(int)StringToInteger(StringSubstr(key,1,2));
            int b=(int)StringToInteger(StringSubstr(key,3,2));
            if(f>=0 && f<BNP_FEATURES && b>=0 && b<5)
            {
               if(!seen[f][b])nseen++;
               seen[f][b]=true;m_weights[f][b]=StringToDouble(value);
            }
         }
      }
      FileClose(h);
      m_model_ready=(p && th && nseen==BNP_FEATURES*5 && MathIsValidNumber(m_prior) && MathIsValidNumber(m_threshold));
      return m_model_ready;
   }
   bool Approve(const int &bins[],double &score)
   {
      if(!m_model_ready || ArraySize(bins)!=BNP_FEATURES)return false;
      score=m_prior;
      for(int i=0;i<BNP_FEATURES;i++)
      {
         if(bins[i]<0 || bins[i]>4)return false;
         score+=.25*m_weights[i][bins[i]];
      }
      return score>m_threshold;
   }
};
#endif
