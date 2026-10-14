"""R8 January causal approximation port from source `Experts/GoldMuwahahaMiner_R8_Microstructure.mq5`
Repo: AnhTranHarris/gold-MUWHAHA-miner, branch carson/mt5-r8-s1-wave-confirm-certification
Git blob 6b2460074ed35d04cb9b4f7620194a483df17c2a
Original Dukascopy Jan 2026 raw UTC Bid/Ask source only. Never consumes original MT5 deal times as signals.
Diffs vs MQL5: broker stop-level, tick-size, ATR bootstrap, actual fill rules approximated;
all results research only. No month hardcode in strategy rule. Tick timestamps matter.
"""
import gzip,json,datetime,hashlib,time,sys,os
from array import array
from pathlib import Path
import numpy as np
from numba import njit
P=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz');ROOT=Path(__file__).parent

def load():
 p=ROOT/'ticks_jan_cache.npz'
 if (ROOT/'ticks_t.npy').exists():
  return (np.load(ROOT/'ticks_t.npy',mmap_mode='r'),np.load(ROOT/'ticks_ask.npy',mmap_mode='r'),np.load(ROOT/'ticks_bid.npy',mmap_mode='r'))
 if p.exists():
  with np.load(p) as d:return d['t'],d['ask'],d['bid']
 tt=array('q');a=array('i');b=array('i')
 with gzip.open(P,'rt') as f:
  next(f)
  for row in f:
   x=row.split(',');tt.append(int(x[0]));a.append(int(x[1]));b.append(int(x[2]));
 t=np.frombuffer(tt,np.int64).copy();ask=np.frombuffer(a,np.int32).copy();bid=np.frombuffer(b,np.int32).copy()
 # Uncompressed .npy for rapid scientific reruns. Original compressed source remains untouched.
 np.save(ROOT/'ticks_t.npy',t);np.save(ROOT/'ticks_ask.npy',ask);np.save(ROOT/'ticks_bid.npy',bid)
 return t,ask,bid

@njit(cache=True)
def execute(t,ask,bid,spread_max_price=.25,latency_ms=250,roundtrip_fee=.20,initial_cash=100.,leverage=500.,stopout_ratio=1.,atr_on=True):
 n=len(t);BUFSZ=160;opens=np.zeros(BUFSZ,np.float64);highs=np.zeros(BUFSZ,np.float64);lows=np.zeros(BUFSZ,np.float64);closes=np.zeros(BUFSZ,np.float64)
 rhead=0;rcount=0;bucketsec=-1;bo=bh=bl=bc=0.
 # Completed M5 ATR14 only; no current-bar high or future bars in entry gate.
 m5=-1;mhigh=mlow=mclose=priorclose=0.;atr=0.;atrseed=0.;atr_n=0
 cash=initial_cash;equitymin=initial_cash;max_balance_dd=0.;balpeak=initial_cash;max_tick_dd=0.;eqpeak=initial_cash
 openposition=0;openprice=sl=0.;opened_ms=0;entry_i=0;entry_clock_ms=0;pending=0;pending_at=0
 microstate=0;statelevel=0.;statestart=-1;cooldown_s=0;minute=-1;minutetrades=0;hadpos=False
 trades=0;wins=0;losses=0;profits=0.;grossloss=0.;forced=0;stop=0;timeout=0
 reasons=np.zeros(4,np.int64);spreadpass=0;atrpass=0;velocitypass=0;signals=0;missed=0
 dur_sum=0.;max_concurrent=0;zero_at_i=-1;max_margin=0.;breach_margin=0
 # MT5 time is second resolution; 20 completed bid-second buckets and 5-second velocity.
 for i in range(n):
  ms=t[i];s=ms//1000;B=bid[i]/1000.;A=ask[i]/1000.;key=ms//300000
  # Candle completion and ATR: Wilder smoothed TR after initial 14 completed bars.
  if key!=m5:
   if m5>=0:
    tr=mhigh-mlow
    if priorclose>0:
     tr=max(tr,abs(mhigh-priorclose),abs(mlow-priorclose))
    if atr_n<14:
     atrseed+=tr;atr_n+=1
     if atr_n==14:atr=atrseed/14.
    else:atr=(atr*13.+tr)/14.
    priorclose=mclose
   m5=key;mhigh=B;mlow=B;mclose=B
  else:
   if B>mhigh:mhigh=B
   if B<mlow:mlow=B
   mclose=B
  # MT5 OnTick completed second ring
  if bucketsec<0:
   bucketsec=s;bo=bh=bl=bc=B
  elif bucketsec!=s:
   opens[rhead]=bo;highs[rhead]=bh;lows[rhead]=bl;closes[rhead]=bc
   rhead=(rhead+1)%BUFSZ;rcount=min(rcount+1,BUFSZ)
   bucketsec=s;bo=bh=bl=bc=B
  else:
   bh=max(bh,B);bl=min(bl,B);bc=B
  # UpdateMinuteCounter resets signal states at new report minute.
  m=s//60
  if m!=minute:
   minute=m;minutetrades=0;microstate=0;statestart=-1;statelevel=0.
  # Resolve delayed market request at first original future quote.
  if pending!=0 and ms>=pending_at:
   side=pending;pending=0
   margin=(A if side>0 else B)/leverage
   eq=cash - (A-B) - roundtrip_fee
   if eq>0 and cash>margin and eq/margin>stopout_ratio:
    openposition=side;openprice=A if side>0 else B;opened_ms=ms;entry_i=i;entry_clock_ms=s
    sl=(B-3.0) if side>0 else (A+3.0)
    minutetrades+=1;microstate=0;statelevel=0.;statestart=-1;max_concurrent=max(max_concurrent,1)
   else:missed+=1
  if openposition!=0:
   mprice=B if openposition>0 else A
   unreal=openposition*(mprice-openprice)-roundtrip_fee
   eq=cash+unreal
   equitymin=min(equitymin,eq);eqpeak=max(eqpeak,eq);max_tick_dd=max(max_tick_dd,eqpeak-eq)
   margin=openprice/leverage
   max_margin=max(max_margin,margin)
   reason=0
   if eq<=0 or eq/margin<=stopout_ratio:reason=3
   elif (openposition>0 and B<=sl) or (openposition<0 and A>=sl):reason=1
   elif s-entry_clock_ms>=60:reason=2
   else:
    if openposition>0 and B-openprice>=.18:sl=max(sl,B-.05)
    elif openposition<0 and openprice-A>=.18:sl=min(sl,A+.05)
   if reason>0:
    net=unreal;cash+=net;trades+=1
    if net>0:wins+=1;profits+=net
    else:losses+=1;grossloss+=net
    dur_sum+=(ms-opened_ms)/1000.
    if reason==1:stop+=1
    elif reason==2:timeout+=1
    else:forced+=1
    balpeak=max(balpeak,cash);max_balance_dd=max(max_balance_dd,balpeak-cash)
    openposition=0;hadpos=True
    if cash<=0 and zero_at_i<0:zero_at_i=i
   continue
  if hadpos:
   hadpos=False;cooldown_s=s+1;microstate=0;statestart=-1;statelevel=0.
   continue
  if pending!=0 or s<cooldown_s or minutetrades>=5:continue
  # Spread gate
  if A-B > spread_max_price:continue
  spreadpass+=1
  # Session ATR, January has UTC winter: London 08-16:30 UTC; NY 13-22 UTC.
  if atr_on:
   if atr_n<14:continue
   minuteutc=(s%86400)//60
   london=480<=minuteutc<990
   ny=780<=minuteutc<1320
   minatr=1.75 if ny else (2.0 if london else 2.5)
   if atr<minatr:continue
  atrpass+=1
  if rcount<20:continue
  upper=-1e99;lower=1e99
  for j in range(20):
   k=(rhead-1-j)%BUFSZ
   upper=max(upper,highs[k]);lower=min(lower,lows[k])
  oldest=(rhead-5)%BUFSZ;prev=closes[oldest];start=prev;travel=0.
  for j in range(3,-1,-1):
   ix=(rhead-1-j)%BUFSZ;c=closes[ix];travel+=abs(c-prev);prev=c
  travel+=abs(B-prev)
  displacement=B-start;efficiency=abs(displacement)/(travel+1e-9)
  velocitypass+=1
  # Exact MQL5 state transition ordering and thresholds from source file.
  if microstate==0:
   if A>=upper+.10: microstate=1;statelevel=upper;statestart=s
   elif B<=lower-.10: microstate=2;statelevel=lower;statestart=s
  action=0;kind=0
  if microstate==1:
   if A<=statelevel-.15:microstate=3;statestart=s
   elif s-statestart>=2 and A>=statelevel+.08 and displacement>=.15 and efficiency>=.30:
    action=1;kind=0
  elif microstate==2:
   if B>=statelevel+.15:microstate=4;statestart=s
   elif s-statestart>=2 and B<=statelevel-.08 and displacement<=-.15 and efficiency>=.30:
    action=-1;kind=1
  elif microstate==3:
   if displacement<=-.15 and efficiency>=.30:action=-1;kind=2
  elif microstate==4:
   if displacement>=.15 and efficiency>=.30:action=1;kind=3
  if action!=0:
   reasons[kind]+=1;signals+=1;pending=action;pending_at=ms+latency_ms;microstate=0;statestart=-1
  elif microstate!=0 and statestart>=0 and s-statestart>20:
   microstate=0;statestart=-1;statelevel=0.
 if openposition!=0:
  # Research mandatory end-of-January liquidation at last observed executable quote.
  B=bid[-1]/1000.;A=ask[-1]/1000.;p=(B if openposition>0 else A)
  net=openposition*(p-openprice)-roundtrip_fee;cash+=net;trades+=1
  if net>0: wins+=1;profits+=net
  else:losses+=1;grossloss+=net
 return np.array([cash,trades,wins,losses,profits,grossloss,equitymin,max_tick_dd,max_balance_dd,max_concurrent,forced,stop,timeout,signals,missed,spreadpass,atrpass,velocitypass,zero_at_i,dur_sum,max_margin]),reasons

def main():
 start=time.time();t,bidask,bid=load();ask=bidask
 assert len(t)==9135062 and np.all(t[1:]>=t[:-1]);print('load',len(t),round(time.time()-start,2),flush=True)
 output={}
 for bound in [.25,.5,.75,1.0,2.0]:
  r,k=execute(t,ask,bid,bound,250,.20,100.,500.,1.,True)
  keys='final_cash trades wins losses gross_profit gross_loss min_tick_equity max_tick_equity_drawdown max_closed_balance_drawdown max_simul forced stop timeout signal_requests denied_requests spreadgate_ticks atrgate_ticks candidate_evals first_nonpositive_tick durations_s max_margin_usd'.split()
  record={key:round(float(value),4) for key,value in zip(keys,r)};record['reason_signals']={name:int(v) for name,v in zip(['CONT_UP','CONT_DN','SWEEP_UP','SWEEP_DN'],k)}
  output[f'spread_max_{bound}']=record
  print('BOUND',bound,record,'elapsed',round(time.time()-start,2),flush=True)
 with open(ROOT/'R8_CAUSAL_DUKAS_JANUARY_RESULTS.json','w') as f:json.dump({'source_implementation':'R8 MQL5 Git blob 6b2460074ed35d04cb9b4f7620194a483df17c2a','scope':'Jan Dukascopy Bid/Ask causal research','variants':output,'contract_assumptions':'point=.01, 0.01 lot=1oz; broker stop level=0, stopout 100% margin, leverage 500, roundtrip fee 0.20, 250ms entry latency; M5 ATR14 Wilder from bid tick; session on actual UTC, not broker server time','limitations':'MQL5 exact broker stop levels, tester mode, terminal tick event and broker fills unavailable; port approximate; no research acceptance'},f,indent=2)
if __name__=='__main__':main()
