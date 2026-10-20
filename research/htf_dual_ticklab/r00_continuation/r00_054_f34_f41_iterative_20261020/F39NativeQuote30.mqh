// F39 ordered 30-column bid/ask first source quote research port.
// Research only. NOT MT5 EA trading permission. Must compile in MetaEditor and test numeric parity.
// Each input MqlTick corresponds to one genuine recorded raw source quote, chronological,
// and event_k must be FIRST source quote index for the original R00-054 event timestamp.
// Caller must maintain feed specific clock/index maps and verify quoted data source identity.
#ifndef __XAUUSD_F39_QUOTE_30__
#define __XAUUSD_F39_QUOTE_30__

bool F39NativeQuote30(const MqlTick &ticks[], const int event_k, const int side, double &features[])
  {
   ArrayResize(features,30);
   ArrayInitialize(features,0.0);
   const int available=ArraySize(ticks);
   if(event_k<0 || event_k>=available || (side!=1 && side!=-1)) return false;
   const double tiny=0.0000001;
   const int k=event_k;
   if(k==0)
     {
      features[3]=1000.;features[4]=1000.;
      features[16]=ticks[0].ask-ticks[0].bid;
      features[17]=features[16];features[29]=1000000.;
      return true;
     }
   const int start=MathMax(1,k-63);
   const int start8=MathMax(1,k-7);
   const double mid_now=0.5*(ticks[k].bid+ticks[k].ask);
   const double mid_prev=0.5*(ticks[start-1].bid+ticks[start-1].ask);
   const double mid8_before=0.5*(ticks[start8-1].bid+ticks[start8-1].ask);
   int bon=0,aon=0,joint=0,unchanged=0,turns=0,turns8=0;
   int previousSign=0,previous8Sign=0,bidLast=-1,askLast=-1;
   double imbalance=0.,imbalance8=0.,vol=0.,vol8=0.;
   double spreadSum=0.,spreadMax=-1.e9,spreadMin=1.e9;
   double interMax=0.,interSum=0.,tick8b=0.,tick8a=0.;
   const double spread_init=ticks[start-1].ask-ticks[start-1].bid;
   const double spread8=ticks[start8-1].ask-ticks[start8-1].bid;
   for(int q=start;q<=k;q++)
     {
      const double db=ticks[q].bid-ticks[q-1].bid;
      const double da=ticks[q].ask-ticks[q-1].ask;
      const bool ub=(MathAbs(db)>tiny);
      const bool ua=(MathAbs(da)>tiny);
      if(ub && ua)joint++;
      else if(ub)bon++;
      else if(ua)aon++;
      else unchanged++;
      if(ub)bidLast=q;
      if(ua)askLast=q;
      const double dm=0.5*(db+da);
      const int sgn=(dm>tiny)?1:((dm< -tiny)?-1:0);
      if(sgn!=0)
        {
         imbalance+=sgn;
         if(previousSign!=0 && previousSign!=sgn)turns++;
         previousSign=sgn;
        }
      vol+=MathAbs(dm);
      if(q>=start8)
        {
         tick8b+=db;tick8a+=da;vol8+=MathAbs(dm);imbalance8+=sgn;
         if(sgn!=0)
           {
            if(previous8Sign!=0 && previous8Sign!=sgn)turns8++;
            previous8Sign=sgn;
           }
        }
      const double spr=ticks[q].ask-ticks[q].bid;
      spreadSum+=spr;
      spreadMax=MathMax(spreadMax,spr);
      spreadMin=MathMin(spreadMin,spr);
      const double gap=(double)(ticks[q].time_msc-ticks[q-1].time_msc);
      interSum+=gap;interMax=MathMax(interMax,gap);
     }
   const double N=(double)(k-start+1),N8=(double)(k-start8+1);
   const double spreadNow=ticks[k].ask-ticks[k].bid;
   features[0]=bon/N;features[1]=aon/N;features[2]=joint/N;
   features[3]=(bidLast>=0)?((double)(ticks[k].time_msc-ticks[bidLast].time_msc)/1000.):1000.;
   features[4]=(askLast>=0)?((double)(ticks[k].time_msc-ticks[askLast].time_msc)/1000.):1000.;
   features[5]=side*(mid_now-mid_prev);
   features[6]=side*(ticks[k].bid-ticks[start-1].bid);
   features[7]=side*(ticks[k].ask-ticks[start-1].ask);
   features[8]=side*(mid_now-mid8_before);
   features[9]=side*tick8b;features[10]=side*tick8a;
   features[11]=side*imbalance/N;features[12]=side*imbalance8/N8;
   features[13]=(N-1.)/MathMax((double)(ticks[k].time_msc-ticks[start-1].time_msc)/1000.,0.001);
   features[14]=interSum/N;features[15]=interMax;
   features[16]=spreadNow;features[17]=spreadSum/N;
   features[18]=spreadMax-spreadMin;
   features[19]=spreadNow-spread_init;
   features[20]=spreadNow-spread8;
   features[21]=turns/N;features[22]=turns8/N8;
   features[23]=MathAbs(mid_now-mid_prev)/MathMax(vol,tiny);
   features[24]=MathAbs(mid_now-mid8_before)/MathMax(vol8,tiny);
   features[25]=(tick8b*tick8a<0.)?1.:0.;
   features[26]=unchanged/N;features[27]=(bon-aon)/N;
   features[28]=side*(spreadNow-spread_init);
   features[29]=(double)(ticks[k].time_msc-ticks[k-1].time_msc);
   return true;
  }
#endif