"""January-only original Bid/Ask causal ATR/H1 profit-harvest engine research CHILD.
Owner-frozen V1 code untouched. Uses unchanged 627 S15 source events recovered by
sha-verified source archive. Changes EXIT ONLY; no hindsight R9 entry labels.
0.01 assumed 1oz, $0.20 fixed round-trip fee, 250ms min quote latency,
$100/$200 real starting cash (per independent replay), singleton funded slot.
"""
from __future__ import annotations
from pathlib import Path
import sys,time,itertools
import numpy as np,pandas as pd
from numba import njit
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r9_teacher_informed_dukas_executor as ORIGINAL
DATA=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
PARENT=HERE/'jan_parent_causal_squeeze_signals.npz'

# Columns are low-ATR modifiers and high-ATR modifiers relative to original:
# stop,target,arm,trail-gap,maximum-hold seconds
# Parameters are defined in advance, not fitted to R9's individual future prices.
CONFIGS=[
 ('UNCHANGED_SQUEEZE', (7.,20.,5.,2.5,1500.),(7.,20.,5.,2.5,1500.),0),
 ('WIDEN_ONLY_HIGH', (7.,20.,5.,2.5,1500.),(7.,30.,7.,3.5,1800.),1),
 ('HIGH_RUNNER_30MIN', (7.,20.,5.,2.5,1500.),(7.,32.,6.,3.0,1800.),1),
 ('HIGH_RUNNER_45MIN', (7.,20.,5.,2.5,1500.),(7.,40.,7.,3.5,2700.),1),
 ('HIGH_REPAIR_TIGHT_TRAIL',(7.,20.,5.,2.5,1500.),(7.,30.,5.,2.0,1500.),1),
 ('HIGH_REPAIR_WIDE_TRAIL',(7.,20.,5.,2.5,1500.),(7.,30.,5.,3.5,1500.),1),
 ('LOW_QUICK_RELEASE',(7.,10.,3.5,1.8,900.),(7.,20.,5.,2.5,1500.),2),
 ('LOW_QUICK_HIGH_RUNNER',(7.,10.,3.5,1.8,900.),(7.,30.,7.,3.5,1800.),2),
 ('LOW_FAST_HIGH_PATIENT',(7.,12.,4.,2.0,900.),(7.,26.,6.5,3.0,2100.),2),
 ('LOW_FAST_HIGH_QUICK',(7.,12.,4.,2.0,900.),(7.,26.,6.5,3.0,1500.),2),
 ('MID_SCALP_HIGH_RUNNER',(7.,12.,4.,2.0,1200.),(7.,30.,6.,3.0,1800.),3),
 ('HIGH_ONLY_EXIT_MONO',(7.,20.,5.,2.5,1500.),(7.,24.,5.,2.5,1500.),1),
]

@njit(cache=True)
def replay(ms,bid,ask,secs,sig,atr5,h1sign,m5sign,cap,settings,mode):
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
    if newsec and sig[ssidx]!=0:
      pending=int(sig[ssidx]);pending_ms=now;sigref=now;pbase=a if pending==1 else b
      p_atr=atr5[ssidx];offered+=1
  lastb=bid[-1]/1000.;lasta=ask[-1]/1000.
  equity=cash+(lastb-entry if pos==1 else entry-lasta)-.20 if pos else cash
  return trades[:n],np.array((cash-cap,equity,maxdd,halt,offered,filled,timeout,blocked,pos))

def main():
  st=time.time()
  d=pd.read_csv(DATA,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'});ms=d.timestamp_ms_utc.to_numpy();bid=d.bid_raw.to_numpy();ask=d.ask_raw.to_numpy();del d
  sp=np.load(PARENT);sec=sp['sec'];signal=sp['signal'];assert ms[0]//1000==sec[0]
  sec2,first,hi,lo,cl,f=ORIGINAL.features(ms,bid)
  assert np.array_equal(sec,sec2)
  atr=f[300][1]
  # H1/M5 close signs from previous FULLY COMPLETED bars; this run does not veto directions.
  hs=np.zeros(len(sec),np.int8);ms5=np.zeros(len(sec),np.int8)
  rows=[];top=[]
  for cap in (100.,200.):
    for ci,(name,low,high,mode) in enumerate(CONFIGS):
      a=np.array([low,high],np.float64)
      led,stat=replay(ms,bid,ask,sec,signal,atr,hs,ms5,cap,a,mode)
      cash=float(stat[0]);gp=float(np.maximum(led[:,6],0).sum()) if len(led) else 0.;gl=float(np.minimum(led[:,6],0).sum()) if len(led) else 0.
      frame=pd.DataFrame(led,columns=['signal_ms','entry_ms','exit_ms','side','entry_quote','exit_quote','net','exit_reason','best_fav_gross','asof_m5_atr','stop','target','trail_arm','trail_gap'])
      if len(frame):
        frame['day']=pd.to_datetime(frame.exit_ms,unit='ms',utc=True).dt.strftime('%Y-%m-%d')
        frame['hour']=pd.to_datetime(frame.exit_ms,unit='ms',utc=True).dt.strftime('%Y-%m-%dT%H')
        sums=frame.groupby('day').net.sum()
      else:sums=pd.Series(dtype=float)
      row=dict(id=ci,name=name,cap=cap,net=round(cash,5),trades=len(led),pf=round(gp/-gl,5) if gl else None,maxdd=round(float(stat[2]),5),halt=int(stat[3]),positive_days=int((sums>0).sum()),negative_days=int((sums<0).sum()),offered=int(stat[4]),filled=int(stat[5]))
      rows.append(row)
      if ci in (0,1,2,3,4,5,6,7,8,9,10,11):
        # persist only top 3 after scoring to avoid disk bloat, in-memory for full run.
        top.append((cap,name,cash,frame.copy(),row))
    print('BALANCE_FINISHED',cap,'sec',round(time.time()-st,2),flush=True)
  data=pd.DataFrame(rows);data.to_csv(HERE/'JAN_ATR_EXIT_REGIME_24_MICROCAPITAL_SCREENS.csv',index=False)
  for cap in (100.,200.):
    cand=sorted([x for x in top if x[0]==cap],key=lambda x:x[2],reverse=True)[:4]
    for i,(_,name,cash,frame,row) in enumerate(cand):
      safe=f'JAN_ATR_REGIME_{int(cap)}_TOP{i+1}'
      frame.to_csv(HERE/(safe+'_LEDGER.csv'),index=False)
      frame.groupby('day').agg(net=('net','sum'),n=('net','size'),wins=('net',lambda v:int((v>0).sum()))).to_csv(HERE/(safe+'_DAILY.csv'))
  print('TOP_RESULTS',data.sort_values(['cap','net'],ascending=[True,False]).groupby('cap').head(8).to_string(index=False),flush=True)
  print('ALL_DONE',round(time.time()-st,2),flush=True)
if __name__=='__main__':main()
