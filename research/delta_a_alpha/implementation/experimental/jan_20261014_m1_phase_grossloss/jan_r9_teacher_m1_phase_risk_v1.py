"""Jan 2026 tick-to-M1 first-10s phase risk mutation, as-of candidate only, finite funded slot.
Source inspiration: original R9 M1 Coinexx SYNTH exact trade phase clustering, causal Dukascopy price repays.
No future labels or bar close M1; clock and pre-completed M5 ATR only. No production promotion.
"""
from pathlib import Path
import sys,time
import pandas as pd,numpy as np
from numba import njit
D=Path(__file__).resolve().parent;P=Path('/mnt/data/jan_new_discovery_20261014');sys.path.insert(0,str(P))
from r9_teacher_informed_dukas_executor import features
SOURCE=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz');
@njit(cache=True)
def replay_phase(ms,bid,ask,secs,sig,atr5,h1sign,m5sign,cap,settings,mode,loss_age_ms,loss_cut,peak_qualifier,phase_min,phase_max,session_mask):
  # settings 2x5 low/high. Entry signal is unchanged; regimes change trailing/exit only.
  trades=np.zeros((15000,14),np.float64);n=0
  cash=cap;equity=cap;eqpeak=cap;maxdd=0.;halt=0
  ssidx=-1;prevsec=-1;minute=-1;used=0
  pos=0;entry=0.;entry_time=0;sl=0.;peak=0.;stop=7.;tp=20.;trig=5.;gap=2.5;hold=1500_000;srcsignal=0
  pending=0;pending_ms=0;pbase=0.;p_atr=np.nan;sigref=0;lastclose=0
  offered=0;filled=0;timeout=0;blocked=0;end_open=0
  for i in range(len(ms)):
    now=ms[i];sec=now//1000
    newsec=sec!=prevsec
    if newsec:
      ssidx+=1;prevsec=sec
      if ssidx>=len(secs) or secs[ssidx]!=sec:break
    newmin=now//60000
    if newmin!=minute:minute=newmin;used=0
    b=bid[i]/1000.;a=ask[i]/1000.;sp=a-b
    equity=cash+(b-entry if pos==1 else entry-a)-.20 if pos else cash
    if equity>eqpeak:eqpeak=equity
    if eqpeak-equity>maxdd:maxdd=eqpeak-equity
    if equity<cap*.60:halt=1
    if pos:
      fav=b-entry if pos==1 else entry-a
      if fav>peak:peak=fav
      reason=0
      if pos==1 and b<=sl or pos==-1 and a>=sl:reason=1
      elif fav>=tp:reason=2
      elif now-entry_time>=hold:reason=3
      # EARLY FAILURE INVALIDATION: observe only current original opposing-side quote,
      # prior observed favorable peak, and elapsed wall-clock milliseconds. No future bars.
      elif loss_age_ms>=0 and now-entry_time>=loss_age_ms and peak<peak_qualifier and fav<=-loss_cut:reason=4
      if reason:
        exit_price=b if pos==1 else a
        pnl=pos*(exit_price-entry)-.20
        if n<len(trades):
          trades[n,0]=srcsignal;trades[n,1]=entry_time;trades[n,2]=now
          trades[n,3]=pos;trades[n,4]=entry;trades[n,5]=exit_price;trades[n,6]=pnl;trades[n,7]=reason
          trades[n,8]=peak;trades[n,9]=p_atr;trades[n,10]=stop;trades[n,11]=tp;trades[n,12]=trig;trades[n,13]=gap
          n+=1
        cash+=pnl;pos=0;pending=0;lastclose=now;continue
      if peak>=trig:
        candidate=max(entry+.20,b-gap) if pos==1 else min(entry-.20,a+gap)
        if pos==1 and candidate>sl:sl=candidate
        if pos==-1 and candidate<sl:sl=candidate
      continue
    if pending:
      if now-pending_ms>15000:
        pending=0;timeout+=1
      elif now>=pending_ms+250:
        px=a if pending==1 else b
        if abs(px-pbase)>1.50:
          pending=0;timeout+=1
        elif sp>.55:
          blocked+=1
        elif cash<cap*.60 or px/500.+sp+.20>cash*.8:
          pending=0;timeout+=1
        else:
          pos=pending;entry=px;entry_time=now;srcsignal=pending_ms;pending=0;filled+=1;used+=1;peak=0.
          low_idx=0;hi_idx=0
          # Prior-completed M5 ATR available at signal instant only.
          if np.isfinite(p_atr):
            if mode==1 and p_atr>=7.77:hi_idx=1
            elif mode==2:
              if p_atr<=3.95:low_idx=1
              if p_atr>=7.77:hi_idx=1
            elif mode==3:
              if p_atr<=5.25:low_idx=1
              if p_atr>=7.77:hi_idx=1
          # index 0 low, index 1 high, normal uses low template except the first 6 setups whose low is baseline
          row=1 if hi_idx else 0
          if mode==2 and low_idx==0 and not hi_idx:row=2
          if mode==3 and low_idx==0 and not hi_idx:row=2
          if row==2:
            stop=7.;tp=20.;trig=5.;gap=2.5;hold=1500_000
          else:
            stop=settings[row,0];tp=settings[row,1];trig=settings[row,2];gap=settings[row,3];hold=int(settings[row,4]*1000)
          sl=b-stop if pos==1 else a+stop
          continue
    if pos or pending or halt or now<lastclose+1000 or used>=5:continue
    # Phase is based on original as-of signal clock, not future R9 entry labels.
    if newsec and sig[ssidx]!=0 and sec%60>=phase_min and sec%60<=phase_max and ((1<<((sec//3600)%24))&session_mask)!=0:
      pending=int(sig[ssidx]);pending_ms=now;sigref=now;pbase=a if pending==1 else b
      p_atr=atr5[ssidx];offered+=1
  lastb=bid[-1]/1000.;lasta=ask[-1]/1000.
  equity=cash+(lastb-entry if pos==1 else entry-lasta)-.20 if pos else cash
  return trades[:n],np.array((cash-cap,equity,maxdd,halt,offered,filled,timeout,blocked,pos))

COLS=['signal_ms','entry_ms','exit_ms','side','entry_quote','exit_quote','net','exit_reason','best_fav_gross','asof_m5_atr','stop','target','trail_arm','trail_gap']
def main():
 st=time.time();d=pd.read_csv(SOURCE,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'});ms=d.timestamp_ms_utc.to_numpy();b=d.bid_raw.to_numpy();a=d.ask_raw.to_numpy();del d
 z=np.load(P/'jan_parent_causal_squeeze_signals.npz');sec,_,_,_,_,fts=features(ms,b);assert np.array_equal(sec,z['sec']);sig=z['signal'];atr=fts[300][1];dummy=np.zeros(len(sec),np.int8)
 settings=np.array([(7.,20.,5.,2.5,1500.),(7.,40.,7.,3.5,2700.)],np.float64)
 masks=[(1<<24)-1]
 # Seven fixed session windows, not fitted to January date.
 for start,end in [(0,8),(8,13),(13,17),(17,22),(22,24),(0,17),(8,22)]:
  masks.append(sum(1<<h for h in range(start,end)))
 cases=[]
 for start,end in [(0,59),(2,59),(5,59),(8,59),(10,59),(12,59),(15,59),(20,59),(10,39),(10,49),(10,55),(15,45),(5,45),(20,49),(0,39),(0,49)]:cases.append((start,end,(1<<24)-1,'PHASE'))
 for start,end in [(0,59),(5,59),(10,59),(10,39),(15,59)]:
  for mask in masks[1:]: cases.append((start,end,mask,'SESSION_PHASE'))
 rows=[]; good=[]
 for i,(lo,hi,mask,family) in enumerate(cases):
  ledger,stat=replay_phase(ms,b,a,sec,sig,atr,dummy,dummy,100.,settings,1,-1,999.,0.,lo,hi,mask)
  p=ledger[:,6] if len(ledger) else np.array([]);gp=float(np.maximum(p,0).sum());gl=float(np.minimum(p,0).sum());
  dates=pd.to_datetime(ledger[:,2],unit='ms',utc=True) if len(ledger) else pd.DatetimeIndex([])
  if len(ledger):
   T=pd.DataFrame({'day':dates.floor('D'),'net':p});L=T.groupby('day').net.sum();pos=int((L>0).sum());neg=int((L<0).sum());T['half']=np.where(dates.day<=15,1,2);S=T.groupby('half').net.sum().to_dict()
  else:pos=neg=0;S={}
  rr=dict(id=i,family=family,phase_min=lo,phase_max=hi,session_mask=mask,net=round(float(stat[0]),5),trades=len(ledger),gp=round(gp,5),gl=round(gl,5),pf=round(gp/-gl,5) if gl<0 else None,dd=round(float(stat[2]),5),halt=int(stat[3]),positive_days=pos,negative_days=neg,jan_first_half=round(S.get(1,0),5),jan_second_half=round(S.get(2,0),5))
  rows.append(rr)
  if not stat[3] and float(stat[0])>0:good.append((float(stat[0]),rr,ledger.copy()))
 df=pd.DataFrame(rows);df.to_csv(D/'JAN_R9_TEACHER_TICK_M1_PHASE_ADMISSION_51_EXPERIMENTS.csv',index=False)
 print('BEST_NET',df.sort_values('net',ascending=False).head(20).to_string(index=False),flush=True)
 print('PARETO_LOSS_NET',df[(df.net>=171.868)&(df.trades>=150)].sort_values('gl',ascending=False).head(20).to_string(index=False),flush=True)
 good.sort(key=lambda x:x[0],reverse=True);more=sorted((x for x in good if x[1]['net']>=171.868 and x[1]['trades']>=150),key=lambda x:x[1]['gl'],reverse=True);seen=set()
 for net,r,led in good[:6]+more[:6]:
  if r['id'] not in seen:pd.DataFrame(led,columns=COLS).to_csv(D/f'JAN_PHASE_CASE_{r["id"]}_LEDGER.csv',index=False);seen.add(r['id'])
 print('DONE',round(time.time()-st,2),len(cases),flush=True)
if __name__=='__main__':main()
