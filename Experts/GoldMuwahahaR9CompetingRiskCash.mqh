#ifndef __GMM_R9_COMPETING_RISK_CASH_MQH__
#define __GMM_R9_COMPETING_RISK_CASH_MQH__
// R9 v1.95. Account-currency competing-risks utility with exact archived
// 155-feature + time-bin hazard model probabilities. Historical research
// barriers do NOT represent actual trailing stops or guaranteed fills.
// Default SHADOW: never changes R9 trade entry/hold/exit decisions.

long   g_r9CRiskEligible=0;
long   g_r9CRiskMatched=0;
long   g_r9CRiskUnavailable=0;
long   g_r9CRiskInvalidCash=0;
long   g_r9CRiskWouldFail=0;
long   g_r9CRiskVetoed=0;
double g_r9CRiskSumEV=0.0;
double g_r9CRiskSumTail=0.0;
double g_r9CRiskSumRiskUtility=0.0;

struct R9CRiskSignal
{
   int    stopCents;
   int    targetCents;
   double pFav5;
   double pAdv5;
   double pAlive5;
   double pFav15;
   double pAdv15;
   double pAlive15;
};

string R9CRiskPacketName()
{
   return StringFormat("R9_CRISK155_%s_%I64d_%I64u.csv",
                       _Symbol,AccountInfoInteger(ACCOUNT_LOGIN),InpMagic);
}
bool R9CRiskProbabilitiesValid(const double a,const double b,const double s)
{
   if(!MathIsValidNumber(a)||!MathIsValidNumber(b)||!MathIsValidNumber(s))
      return false;
   if(a<0.0 || b<0.0 || s<0.0 || a>1.0 || b>1.0 || s>1.0)
      return false;
   return (MathAbs(a+b+s-1.0)<=0.000001);
}
bool R9CRiskRead(const MqlTick &tick,const int side,R9CRiskSignal &m)
{
   const string name=R9CRiskPacketName();
   if(!FileIsExist(name,FILE_COMMON)) return false;
   const int fh=FileOpen(name,FILE_READ|FILE_CSV|FILE_ANSI|FILE_COMMON|
                         FILE_SHARE_READ|FILE_SHARE_WRITE,',');
   if(fh==INVALID_HANDLE) return false;
   string f[23];
   for(int i=0;i<23;++i)
   {
      if(FileIsEnding(fh)){ FileClose(fh); return false; }
      f[i]=FileReadString(fh);
   }
   const bool extra=!FileIsEnding(fh);
   FileClose(fh);
   if(extra || f[0]!="R9_CRISK155_V1" ||
      f[2]!=_Symbol || f[8]!="155" ||
      f[21]!="ASOF_PINNED" ||
      f[22]!="R9_CRISK_155_20261113_V1" ||
      f[9]!=InpR9CRiskExpectedHazardSha ||
      StringToInteger(f[1])!=AccountInfoInteger(ACCOUNT_LOGIN) ||
      StringToInteger(f[3])!=(long)InpMagic ||
      StringToInteger(f[4])!=(long)tick.time_msc ||
      StringToInteger(f[5])!=(long)MathRound(tick.bid*100.0) ||
      StringToInteger(f[6])!=(long)MathRound(tick.ask*100.0) ||
      StringToInteger(f[7])!=(long)side ||
      StringToInteger(f[11])!=(long)tick.time_msc ||
      StringToInteger(f[12])<=0 ||
      StringLen(f[10])<8)
      return false;

   const long stop=StringToInteger(f[13]);
   const long target=StringToInteger(f[14]);
   if(stop<=0 || target<=0 || stop>100000 || target>100000)
      return false;
   for(int i=15;i<=20;++i)
      if(StringLen(f[i])==0) return false;
   m.stopCents=(int)stop;
   m.targetCents=(int)target;
   m.pFav5=StringToDouble(f[15]);
   m.pAdv5=StringToDouble(f[16]);
   m.pAlive5=StringToDouble(f[17]);
   m.pFav15=StringToDouble(f[18]);
   m.pAdv15=StringToDouble(f[19]);
   m.pAlive15=StringToDouble(f[20]);
   if(!R9CRiskProbabilitiesValid(m.pFav5,m.pAdv5,m.pAlive5) ||
      !R9CRiskProbabilitiesValid(m.pFav15,m.pAdv15,m.pAlive15))
      return false;
   // Cumulative favorable/adverse incidence cannot decrease over time;
   // survival cannot increase. This catches misordered CSV score fields.
   const double eps=0.000001;
   return (m.pFav15+eps>=m.pFav5 &&
           m.pAdv15+eps>=m.pAdv5 &&
           m.pAlive15<=m.pAlive5+eps);
}

double R9CRiskLossCVaR95(const double pFav,const double pAdv,
                         const double pAlive,const double winNet,
                         const double stopNet,const double timeoutNet)
{
   // Exact worst 5% distribution of cash LOSS=max(0,-net outcome).
   double prob[3]; double loss[3];
   prob[0]=pFav; prob[1]=pAdv; prob[2]=pAlive;
   loss[0]=MathMax(0.0,-winNet);
   loss[1]=MathMax(0.0,-stopNet);
   loss[2]=MathMax(0.0,-timeoutNet);
   double left=0.05,tail=0.0;
   for(int j=0;j<3;++j)
   {
      int maxIndex=-1;
      double maxLoss=-1.0;
      for(int i=0;i<3;++i)
      {
         if(prob[i]>0.0 && loss[i]>maxLoss)
         {
            maxLoss=loss[i];
            maxIndex=i;
         }
      }
      if(maxIndex<0 || left<=0.0) break;
      const double part=MathMin(left,prob[maxIndex]);
      tail+=part*loss[maxIndex];
      left-=part;
      prob[maxIndex]=0.0;
   }
   return tail/0.05;
}
bool R9CRiskCashUtility(const int side,const MqlTick &tick,
                        const double volume,const R9CRiskSignal &m,
                        double &expectedNet,double &riskUtility,
                        double &lossCVaR,double &lowerBound,
                        double &upperBound)
{
   expectedNet=0.0;riskUtility=0.0;lossCVaR=0.0;
   lowerBound=0.0;upperBound=0.0;
   if(side!=1 && side!=-1) return false;
   const ENUM_ORDER_TYPE direction=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;
   const double entry=side>0?tick.ask:tick.bid;
   if(entry<=0.0 || volume<=0.0) return false;
   const double up=NormalizePrice(entry+side*0.01*m.targetCents);
   const double down=NormalizePrice(entry-side*0.01*m.stopCents);
   if(up<=0.0 || down<=0.0) return false;
   double gain=0.0,stopPnl=0.0;
   // Bid liquidation for BUY, Ask for SELL is captured by the research
   // model's gross price barriers measured from original executable entry.
   // Broker profit conversion returns ACCOUNT CURRENCY, not fixed USD.
   if(!OrderCalcProfit(direction,_Symbol,volume,entry,up,gain) ||
      !OrderCalcProfit(direction,_Symbol,volume,entry,down,stopPnl))
      return false;
   if(!MathIsValidNumber(gain) || !MathIsValidNumber(stopPnl) ||
      gain<=0.0 || stopPnl>=0.0) return false;

   const double fee=InpR9CRiskRoundtripCostAccountCash;
   const double winNet=gain-fee;
   const double stopNet=stopPnl-fee;
   const double timeoutNet=InpR9CRiskTimeoutGrossAccountCash-fee;
   expectedNet=m.pFav15*winNet+m.pAdv15*stopNet+m.pAlive15*timeoutNet;
   lossCVaR=R9CRiskLossCVaR95(m.pFav15,m.pAdv15,m.pAlive15,
                              winNet,stopNet,timeoutNet);
   riskUtility=expectedNet-InpR9CRiskCVaRWeight*lossCVaR;
   lowerBound=expectedNet+m.pAlive15*(stopPnl-InpR9CRiskTimeoutGrossAccountCash);
   upperBound=expectedNet+m.pAlive15*(gain-InpR9CRiskTimeoutGrossAccountCash);
   return (MathIsValidNumber(expectedNet) &&
           MathIsValidNumber(riskUtility) &&
           MathIsValidNumber(lossCVaR));
}
bool R9CRiskPermitOriginalEntry(const MqlTick &tick,const int side)
{
   if(InpR9CRiskMode==0) return true;
   ++g_r9CRiskEligible;
   R9CRiskSignal m;
   if(!R9CRiskRead(tick,side,m))
   {
      ++g_r9CRiskUnavailable;
      // Shadow has NO trading effect; experimental filter refuses to invent
      // a score from stale quotes, untrained indicators, or a fake model.
      return (InpR9CRiskMode==1);
   }
   double ev=0.0,utility=0.0,cvar=0.0,lower=0.0,upper=0.0;
   if(!R9CRiskCashUtility(side,tick,NormalizeVolume(InpLots),m,
                          ev,utility,cvar,lower,upper))
   {
      ++g_r9CRiskInvalidCash;
      return (InpR9CRiskMode==1);
   }
   ++g_r9CRiskMatched;
   g_r9CRiskSumEV+=ev;
   g_r9CRiskSumTail+=cvar;
   g_r9CRiskSumRiskUtility+=utility;
   const bool wouldPass=(utility>=InpR9CRiskMinUtilityAccountCash);
   if(!wouldPass) ++g_r9CRiskWouldFail;
   if(InpR9CRiskLogEveryN>0 &&
      g_r9CRiskMatched%InpR9CRiskLogEveryN==0)
      PrintFormat("GM_R9: CRISK SHADOW currency=%s n=%I64d p5(+/-/S)=%.4f/%.4f/%.4f p15(+/-/S)=%.4f/%.4f/%.4f cashEV=%.4f CVaR95=%.4f riskU=%.4f hypotheticalRange=[%.4f,%.4f] threshold=%.4f",
                  AccountInfoString(ACCOUNT_CURRENCY),g_r9CRiskMatched,
                  m.pFav5,m.pAdv5,m.pAlive5,
                  m.pFav15,m.pAdv15,m.pAlive15,
                  ev,cvar,utility,lower,upper,InpR9CRiskMinUtilityAccountCash);
   if(InpR9CRiskMode==1) return true;
   if(!wouldPass)
   {
      ++g_r9CRiskVetoed;
      return false;
   }
   return true;
}
void R9CRiskReport()
{
   if(InpR9CRiskMode==0) return;
   const double denom=MathMax(1.0,(double)g_r9CRiskMatched);
   PrintFormat("GM_R9: CRISK mode=%d currency=%s eligible=%I64d matched=%I64d unavailable=%I64d invalidCash=%I64d wouldFail=%I64d vetoed=%I64d meanEV=%.5f meanCVaR=%.5f meanUtility=%.5f",
               InpR9CRiskMode,AccountInfoString(ACCOUNT_CURRENCY),
               g_r9CRiskEligible,g_r9CRiskMatched,g_r9CRiskUnavailable,
               g_r9CRiskInvalidCash,g_r9CRiskWouldFail,g_r9CRiskVetoed,
               g_r9CRiskSumEV/denom,g_r9CRiskSumTail/denom,
               g_r9CRiskSumRiskUtility/denom);
}
#endif
