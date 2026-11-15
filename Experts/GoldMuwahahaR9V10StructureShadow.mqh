// R9 V10 research-only native market-structure observer.
// Source: completed MT5 Bid bars + current executable Bid/Ask. NO orders.
// Intentionally not claimed bit-identical to Python's source-quote mid bars.
// Use ONLY after SyncQuoteHistory has caught up to the current terminal quote.
#ifndef __GMM_R9_V10_STRUCTURE_SHADOW_MQH__
#define __GMM_R9_V10_STRUCTURE_SHADOW_MQH__

struct R9V10Zone
{
   int kind;                 // +1 resistance, -1 support
   double center,half;
   datetime confirmed;
   int tfMask,touches;
};

class R9V10StructureShadow
{
private:
   ENUM_TIMEFRAMES m_frames[5];
   int m_atr[5];
   bool m_ownAtr[5];
   int m_adx,m_ema,m_bands;
   datetime m_lastClosedBar[5];
   R9V10Zone m_zone[40];
   int m_zones;
   bool m_ready;
   long m_lastSecond,m_lastQuoteMs,m_probeMs,m_lastLogMinute;
   double m_prevBid,m_prevAsk,m_boundary,m_zoneLow,m_zoneHigh;
   int m_probeSide,m_phase,m_confirm,m_parent,m_micro;
   double m_bbRatio,m_adxValue;

   bool BufferOne(const int handle,const int buffer,const int shift,double &value)
   {
      if(handle==INVALID_HANDLE)return false;
      double x[1];
      if(CopyBuffer(handle,buffer,shift,1,x)!=1)return false;
      if(!MathIsValidNumber(x[0]))return false;
      value=x[0];
      return true;
   }

   void ZoneAdd(const int kind,const double price,const double half,
                const datetime confirmed,const int sourceBit)
   {
      int matched=-1;
      for(int i=0;i<m_zones;++i)
      {
         if(m_zone[i].kind==kind &&
            MathAbs(price-m_zone[i].center)<=1.5*MathMax(half,m_zone[i].half))
         {matched=i;break;}
      }
      if(matched>=0)
      {
         const double weight=(double)MathMin(8,m_zone[matched].touches);
         m_zone[matched].center=(m_zone[matched].center*weight+price)/(weight+1.);
         m_zone[matched].half=MathMax(m_zone[matched].half,half);
         m_zone[matched].tfMask|=sourceBit;
         m_zone[matched].touches++;
         m_zone[matched].confirmed=confirmed;
         return;
      }
      int slot=m_zones;
      if(slot>=40)
      {
         slot=0;
         double worst=DBL_MAX;
         for(int i=0;i<m_zones;++i)
         {
            const double score=(double)m_zone[i].touches+
                               (double)m_zone[i].tfMask*0.01+
                               (double)m_zone[i].confirmed/1e9;
            if(score<worst){worst=score;slot=i;}
         }
      }
      else m_zones++;
      m_zone[slot].kind=kind;
      m_zone[slot].center=price;
      m_zone[slot].half=half;
      m_zone[slot].confirmed=confirmed;
      m_zone[slot].tfMask=sourceBit;
      m_zone[slot].touches=1;
   }

   void UpdateClosedPivots(const MqlTick &tick)
   {
      // Called only once at a new observed terminal minute, never on every quote.
      // CopyRates shift=1 excludes forming bars. Physical order is oldest first.
      for(int f=0;f<5;++f)
      {
         const datetime closed=iTime(_Symbol,m_frames[f],1);
         if(closed<=0 || closed==m_lastClosedBar[f])continue;
         MqlRates q[5];
         if(CopyRates(_Symbol,m_frames[f],1,5,q)!=5)continue;
         const int seconds=PeriodSeconds(m_frames[f]);
         bool continuous=true;
         for(int j=0;j<4;++j)
            if(q[j+1].time-q[j].time!=seconds){continuous=false;break;}
         m_lastClosedBar[f]=closed;
         if(!continuous)continue; // weekends, gaps and missing bars: no fake pivots
         double atr=0.;
         if(!BufferOne(m_atr[f],0,1,atr) || atr<=0)continue;
         const double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
         if(point<=0)continue;
         const double half=MathMin(500.*point,
                           MathMax(2.*point,MathMax((tick.ask-tick.bid)*.5,atr*.16)));
         bool high=true,low=true;
         for(int j=0;j<5;++j)
         {
            if(j==2)continue;
            if(q[2].high<=q[j].high)high=false;
            if(q[2].low>=q[j].low)low=false;
         }
         // q[2] is closed shift=3; two NEWER closed bars establish confirmation.
         if(high)ZoneAdd(1,q[2].high,half,closed,1<<f);
         if(low)ZoneAdd(-1,q[2].low,half,closed,1<<f);
      }
   }

   int ParentDirection()
   {
      // Confirmed M5 directional slope used only as a shadow contextual proxy.
      MqlRates q[5];
      if(CopyRates(_Symbol,PERIOD_M5,1,5,q)!=5)return 0;
      for(int i=0;i<4;++i)
         if(q[i+1].time-q[i].time!=300)return 0;
      double travel=0.;
      for(int i=0;i<4;++i)travel+=MathAbs(q[i+1].close-q[i].close);
      const double net=q[4].close-q[0].close;
      if(MathAbs(net)/MathMax(_Point,travel)<.60)return 0;
      double atr=0.;
      if(!BufferOne(m_atr[1],0,1,atr) || MathAbs(net)<.6*atr)return 0;
      return net>0?1:-1;
   }

   int Nearest(const int kind,const double price,const datetime now)
   {
      int winner=-1;
      double best=DBL_MAX;
      for(int i=0;i<m_zones;++i)
      {
         if(m_zone[i].kind!=kind ||
            now-m_zone[i].confirmed>14*86400)continue;
         const double distance=MathAbs(m_zone[i].center-price);
         if(distance<best){best=distance;winner=i;}
      }
      return winner;
   }

   void RefreshIndicators()
   {
      double adx=0.,atr=0.,upper=0.,lower=0.;
      m_adxValue=0.;m_bbRatio=-1.;
      if(BufferOne(m_adx,0,1,adx))m_adxValue=adx;
      if(BufferOne(m_atr[0],0,1,atr) && atr>0 &&
         BufferOne(m_bands,1,1,upper) &&
         BufferOne(m_bands,2,1,lower))
         m_bbRatio=(upper-lower)/atr;
   }

public:
   R9V10StructureShadow()
   {
      m_ready=false;m_zones=0;m_lastSecond=-1;m_lastQuoteMs=-1;
      m_probeMs=-1;m_lastLogMinute=-1;
      m_prevBid=0.;m_prevAsk=0.;m_boundary=0.;
      m_zoneLow=0.;m_zoneHigh=0.;
      m_probeSide=0;m_phase=0;m_confirm=0;m_parent=0;m_micro=0;
      m_bbRatio=-1.;m_adxValue=0.;
      for(int f=0;f<5;++f)
      {m_atr[f]=INVALID_HANDLE;m_ownAtr[f]=false;m_lastClosedBar[f]=0;}
      m_adx=m_ema=m_bands=INVALID_HANDLE;
   }

   bool Init(const int existingAtrM1,const int existingAtrM5,
             const int existingAdx,const int existingEma)
   {
      m_frames[0]=PERIOD_M1;m_frames[1]=PERIOD_M5;m_frames[2]=PERIOD_M15;
      m_frames[3]=PERIOD_H1;m_frames[4]=PERIOD_H4;
      m_atr[0]=existingAtrM1;m_atr[1]=existingAtrM5;
      m_adx=existingAdx;m_ema=existingEma;
      if(m_adx==INVALID_HANDLE || m_ema==INVALID_HANDLE ||
         m_atr[0]==INVALID_HANDLE || m_atr[1]==INVALID_HANDLE)return false;
      for(int f=2;f<5;++f)
      {
         m_atr[f]=iATR(_Symbol,m_frames[f],14);
         m_ownAtr[f]=true;
         if(m_atr[f]==INVALID_HANDLE){Release();return false;}
      }
      m_bands=iBands(_Symbol,PERIOD_M1,20,0,2.,PRICE_CLOSE);
      if(m_bands==INVALID_HANDLE){Release();return false;}
      m_ready=true;
      return true;
   }

   void Release()
   {
      for(int f=2;f<5;++f)
         if(m_ownAtr[f] && m_atr[f]!=INVALID_HANDLE)
         {IndicatorRelease(m_atr[f]);m_atr[f]=INVALID_HANDLE;}
      if(m_bands!=INVALID_HANDLE){IndicatorRelease(m_bands);m_bands=INVALID_HANDLE;}
      m_ready=false;
   }

   void OnQuote(const MqlTick &tick,const int microDirection)
   {
      if(!m_ready)return;
      const long now=(long)tick.time_msc;
      if(now<m_lastQuoteMs || tick.bid<=0 || tick.ask<tick.bid)return;
      if(m_lastQuoteMs>0 && now-m_lastQuoteMs>2500)
      {m_phase=0;m_confirm=0;}
      const long minute=now/60000;
      if(minute!=m_lastLogMinute)
      {
         // MQL5 built-in higher timeframe indicators and pivots refresh by bar.
         UpdateClosedPivots(tick);
         RefreshIndicators();
         m_parent=ParentDirection();
      }

      const long second=now/1000;
      if(m_lastSecond>=0 && second!=m_lastSecond && m_phase==1)
      {
         if(second-m_lastSecond!=1)m_confirm=0;
         else
         {
            const bool beyond=(m_probeSide>0?m_prevBid>m_boundary:
                                             m_prevAsk<m_boundary);
            m_confirm=beyond?m_confirm+1:0;
            if(m_confirm>=2 && now>=m_probeMs+1000)m_phase=2;
         }
      }
      if(m_phase==1)
      {
         const bool failed=(m_probeSide>0?tick.bid<m_zoneLow:tick.ask>m_zoneHigh);
         if(failed)m_phase=3;
         else if(now-m_probeMs>15000)m_phase=4;
      }
      if(m_phase!=0 && now-m_probeMs>30000)
      {m_phase=0;m_confirm=0;}
      const int priorPhase=m_phase;
      if(m_phase==0 && m_prevBid>0.)
      {
         const double mid=(tick.bid+tick.ask)*.5;
         const int r=Nearest(1,mid,tick.time);
         const int s=Nearest(-1,mid,tick.time);
         if(r>=0 && m_prevBid<=m_zone[r].center+m_zone[r].half+_Point &&
            tick.bid>m_zone[r].center+m_zone[r].half+_Point)
         {
            m_probeSide=1;m_phase=1;
            m_boundary=m_zone[r].center+m_zone[r].half+_Point;
            m_zoneLow=m_zone[r].center-m_zone[r].half;
            m_zoneHigh=m_zone[r].center+m_zone[r].half;
         }
         else if(s>=0 && m_prevAsk>=m_zone[s].center-m_zone[s].half-_Point &&
                 tick.ask<m_zone[s].center-m_zone[s].half-_Point)
         {
            m_probeSide=-1;m_phase=1;
            m_boundary=m_zone[s].center-m_zone[s].half-_Point;
            m_zoneLow=m_zone[s].center-m_zone[s].half;
            m_zoneHigh=m_zone[s].center+m_zone[s].half;
         }
         if(m_phase==1){m_probeMs=now;m_confirm=0;}
      }
      m_micro=microDirection;
      if(m_phase!=priorPhase || minute!=m_lastLogMinute)
      {
         const bool compression=(m_bbRatio>=0 && m_bbRatio<2.2 &&
                                 m_adxValue>0 && m_adxValue<18.);
         const int nested=(m_parent!=0 && m_micro!=0?
                           (m_parent==m_micro?1:-1):0);
         PrintFormat("R9 V10 STRUCTURE SHADOW ms=%I64d phase=%d side=%d zones=%d parent=%d micro=%d nested=%d compression=%d bbATR=%.3f adx=%.2f Bid=%.5f Ask=%.5f NO ORDER",
                    now,m_phase,m_probeSide,m_zones,m_parent,m_micro,nested,
                    (int)compression,m_bbRatio,m_adxValue,tick.bid,tick.ask);
      }
      m_lastSecond=second;m_lastQuoteMs=now;m_prevBid=tick.bid;m_prevAsk=tick.ask;
      m_lastLogMinute=minute;
   }
};
#endif
