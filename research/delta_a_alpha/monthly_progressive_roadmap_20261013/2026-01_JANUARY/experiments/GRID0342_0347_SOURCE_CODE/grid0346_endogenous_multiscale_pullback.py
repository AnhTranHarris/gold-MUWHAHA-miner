"""GRID0346 -- January standalone original Bid/Ask, NO historical candidate tape.
Build physical 0.01-lot candidates on first observed quote of a second with
completed-second 60s virtual pullback and trends from strictly previous 15/30/60m.
Research only. All signs/entry features are known when submitted.
"""
import json,hashlib,datetime,sys,os,time
from pathlib import Path
import numpy as np
import pandas as pd
SRC=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH'); ROOT=Path(__file__).parent
DAYS=['2026-01-05','2026-01-08','2026-01-09','2026-01-12','2026-01-13','2026-01-14','2026-01-15','2026-01-16','2026-01-19','2026-01-20']
# frozen a priori cohort for reproducibility; separately randomized cohort below using seed 20261014
HORIZON=604800000

def raw():
 t=np.load(SRC/'ticks_t.npy',mmap_mode='r');b=np.load(SRC/'ticks_bid.npy',mmap_mode='r');a=np.load(SRC/'ticks_ask.npy',mmap_mode='r');return t,b,a

def signals(t,b,a,config):
 # Never inspect price from the current second except first tick, and never inspect a future bar.
 s=t//1000;begins=np.r_[0,np.nonzero(np.diff(s))[0]+1]
 seconds=s[begins];last=np.r_[begins[1:]-1,len(s)-1]
 close=b[last].astype('float64')/1000
 prevclose=np.r_[np.nan,close[:-1]];nowb=b[begins]/1000.;nowa=a[begins]/1000.
 # rolling levels are exclusively from completed seconds (pandas shift1)
 high60=pd.Series(close).rolling(60,min_periods=60).max().shift(1).to_numpy()
 low60=pd.Series(close).rolling(60,min_periods=60).min().shift(1).to_numpy()
 def past(sec):
  j=np.searchsorted(seconds,seconds-sec,side='left')-1
  return np.where(j>=0,close[np.maximum(j,0)],np.nan)
 nowprev=prevclose; p5=past(5);p900=past(900);p1800=past(1800);p3600=past(3600)
 # ALL trend comparison price is LAST completed second, not current quote.
 slopes=np.vstack([nowprev-p900,nowprev-p1800,nowprev-p3600])
 thresholds=np.array(config['slope_thresholds'])[:,None]
 voteup=np.sum(slopes>thresholds,axis=0);votedown=np.sum(slopes< -thresholds,axis=0)
 mom5=nowb-p5;midsp=nowa-nowb;maxspr=config['max_spread']
 # breakout already occurred in some earlier bar; signal is *pullback then reacceleration*
 pullback_up=(high60-nowprev>=config['pullback'])&(nowprev-low60>=config['range_min'])
 pullback_dn=(nowprev-low60>=config['pullback'])&(high60-nowprev>=config['range_min'])
 enabled=np.isfinite(p3600)&np.isfinite(high60)&(midsp<=maxspr)
 direction=np.zeros(len(begins),dtype=np.int8)
 buy=enabled&(voteup>=2)&pullback_up&(mom5>=config['momentum'])
 sell=enabled&(votedown>=2)&pullback_dn&(mom5<=-config['momentum'])
 direction[buy]=1;direction[sell]=-1
 keep=np.flatnonzero(direction)
 return begins[keep],direction[keep],{'seconds':len(seconds),'preliminary':len(keep),'eligible_spread':int(np.sum(midsp<=maxspr))}

def physical_replay(t,b,a,idx,side,startdate,config):
 start=int(np.datetime64(startdate+'T00:00:00','ms').astype('int64'));stop=start+HORIZON
 lo=int(np.searchsorted(t,start));hi=int(np.searchsorted(t,stop));m=(idx>=lo)&(idx<hi);events=idx[m];sides=side[m]
 cash=100.;mine=100.;highest=100.;maxdd=0.;hour_peak=100.;last_hour=None;worsthour=0.;last_exit=-10**20
 grossprofit=0.;grossloss=0.;trades=0;wins=0;stopout=0;skipped=0;max_margin=0.;entries=[];exits=[];dirs=[];pnls=[];byday={};loss_run=0;pause_until=-1;earliest_5k=None
 fee=config.get('fee',.2);lat=int(config.get('latency_ms',250));lev=500.;p=config['profit'];r=config['stop'];maxdur=int(config['maxhold']*1000)
 budget=config.get('budget',.20);riskbudget=config.get('riskbudget',.045)
 for i,d in zip(events,sides):
  ti=int(t[i]);d=int(d)
  if ti < pause_until or ti-last_exit<int(config['cooldown']*1000):continue
  ei=int(np.searchsorted(t,ti+lat,side='left'))
  if ei>=hi:break
  if int(t[ei])-ti>2000:skipped+=1;continue
  B=int(b[ei])/1000.;A=int(a[ei])/1000.;spread=A-B;price=A if d==1 else B;mar=price/lev
  # physical quote executable fundability, veto if risk+spread+fees > cash-budget; fixed 0.01=1 oz
  if cash<=0 or spread>config['max_spread'] or mar>(cash-spread-fee)*budget or cash-spread-fee<=2*mar or r+spread+fee>cash*riskbudget:
   skipped+=1;continue
  end=int(np.searchsorted(t,int(t[ei])+maxdur,side='right'));end=max(ei+1,min(end,hi))
  # each original quote between entry and exit; NO pre-known exit, first quote hitting stop/target/stopout
  exit_prices=(b[ei:end] if d==1 else a[ei:end]).astype('float64')/1000
  floating=cash + d*(exit_prices-price)-fee
  eligible=np.flatnonzero((floating<=.50*mar)|(floating<=0)|(floating-cash>=p)|(floating-cash<=-r))
  xi=ei+int(eligible[0]) if len(eligible) else end-1
  eq=floating[:xi-ei+1];minq=float(eq.min());mine=min(mine,minq)
  # chronological full-tick account equity path, equity peak from BEFORE current position
  runpeak=np.maximum.accumulate(np.r_[highest,eq])[1:];maxdd=max(maxdd,float(np.max(runpeak-eq)));highest=max(highest,float(eq.max()))
  hrs=t[ei:xi+1]//3600000
  splits=np.r_[0,np.flatnonzero(np.diff(hrs))+1,len(hrs)]
  for l,j in zip(splits[:-1],splits[1:]):
   h=int(hrs[l]);e=eq[l:j]
   if h!=last_hour:last_hour=h;hour_peak=float(e[0])
   peak=np.maximum.accumulate(np.r_[hour_peak,e])[1:];worsthour=max(worsthour,float(np.max(peak-e)));hour_peak=max(hour_peak,float(e.max()))
  net=float(eq[-1]-cash);cash+=net;trades+=1;wins+=int(net>0)
  grossprofit+=max(0,net);grossloss+=min(0,net)
  entries.append(ei);exits.append(xi);dirs.append(d);pnls.append(net)
  dt=str(np.datetime64(int(t[xi]),'ms').astype('datetime64[D]'))
  byday[dt]=round(byday.get(dt,0.)+net,6)
  if cash>=5000 and earliest_5k is None:earliest_5k=int(t[xi])
  if len(eligible) and eq[-1]<=.5*mar:stopout+=1
  last_exit=int(t[xi]);max_margin=max(max_margin,mar)
  loss_run=loss_run+1 if net<=0 else 0
  if loss_run>=2:pause_until=last_exit+5*60*1000;loss_run=0
  if cash<=0:break
 # no re-use future PNL for new trading permission; ordered independent settlements.
 return dict(date=startdate,final_cash=round(cash,4),trades=trades,wins=wins,grossprofit=round(grossprofit,4),grossloss=round(grossloss,4),min_equity=round(mine,4),max_tick_dd=round(maxdd,4),worst_hour_dd=round(worsthour,4),stopouts=stopout,skipped=skipped,first_5k_tick=earliest_5k,max_used_margin=round(max_margin,4),day_net=byday),np.array(entries,dtype=np.int64),np.array(exits,dtype=np.int64),np.array(dirs,dtype=np.int8),np.array(pnls)

def main():
 from random import Random
 t,b,a=raw()
 assert len(t)==9135062 and len(b)==len(t) and len(a)==len(t)
 # Select only actual trading days, and only windows with a full 7 calendar days inside January.
 tick_day,counts=np.unique(t//86400000,return_counts=True)
 latest=int(np.datetime64('2026-01-24T00:00:00','ms').astype('int64')//86400000)
 possible=[str(np.datetime64(int(d),'D')) for d,n in zip(tick_day,counts) if n>1000 and int(d)<latest and int(d)>=int(np.datetime64('2026-01-02','D').astype(int)) and int(np.datetime64(int(d),'D').astype(object).weekday())<5]
 assert len(possible)>=10
 # Frozen deterministic, ACTUAL quote-bearing January trading dates.
 days=sorted(Random(20261014).sample(possible,10))
 print('FROZEN_10_TRADING_STARTS',days,flush=True)
 variants={
  'STRUCT_A':dict(slope_thresholds=[2.5,3.5,5.],max_spread=1.00,pullback=1.20,range_min=1.5,momentum=.30,stop=1.4,profit=3.5,maxhold=140,cooldown=2,riskbudget=.05),
  'STRUCT_B':dict(slope_thresholds=[3.5,5.0,7.],max_spread=1.00,pullback=1.50,range_min=2.0,momentum=.45,stop=1.0,profit=4.5,maxhold=180,cooldown=5,riskbudget=.05),
  'STRUCT_C':dict(slope_thresholds=[1.5,2.5,4.],max_spread=1.15,pullback=1.30,range_min=1.8,momentum=.5,stop=1.5,profit=5.0,maxhold=210,cooldown=3,riskbudget=.05),
  'STRUCT_D':dict(slope_thresholds=[3.0,4.,5.],max_spread=.85,pullback=1.00,range_min=1.2,momentum=.7,stop=.9,profit=3.0,maxhold=105,cooldown=3,riskbudget=.04),
 }
 output={'seed':20261014,'cohort':days,'config_assumptions':'0.01 lot=1 oz, 500:1, 250 ms, $0.20 roundtrip, strict Bid Ask fills, 1 physical position','variants':{},'unpromoted':True}
 target=os.environ.get('GRID0346_ONLY','')
 if target:
  assert target in variants
  current=ROOT/'GRID0346_JANUARY_STRUCTURAL_MICRO_CAPITAL_RESULTS.json'
  if current.exists():
   old=json.loads(current.read_text())
   if old.get('cohort')==days:output['variants']=old['variants']
  variants={target:variants[target]}
 for name,cfg in variants.items():
  st=time.time();ei,side,meta=signals(t,b,a,cfg);results=[];ledger=[]
  for date in days:
   summary,x,y,d,p=physical_replay(t,b,a,ei,side,date,cfg)
   if len(p):
    calculated=np.where(d>0,b[y].astype('float64')-a[x].astype('float64'),b[x].astype('float64')-a[y].astype('float64'))/1000.-.2
    assert np.max(np.abs(calculated-p))<1e-8,(name,date)
   ledger.extend(zip([date]*len(p),x.tolist(),y.tolist(),d.tolist(),p.tolist()));results.append(summary)
  stat={'test_count':len(days),'profitable_count':sum(x['final_cash']>100 for x in results),'nonruin':sum(x['min_equity']>0 for x in results),'no_stopout':sum(x['stopouts']==0 for x in results),'reached_5000':sum(x['first_5k_tick'] is not None for x in results),'trades':sum(x['trades'] for x in results),'ending_min':min(x['final_cash'] for x in results),'ending_max':max(x['final_cash'] for x in results),'worst_hour_dd':max(x['worst_hour_dd'] for x in results),'config':cfg,'signals_meta':meta,'results':results,'duration_s':round(time.time()-st,2)}
  output['variants'][name]=stat
  np.savez_compressed(ROOT/(name+'_original_quote_deals.npz'),entry_idx=np.array([x[1] for x in ledger],np.int64),exit_idx=np.array([x[2] for x in ledger],np.int64),side=np.array([x[3] for x in ledger],np.int8),net=np.array([x[4] for x in ledger],np.float64))
  print(name,{k:v for k,v in stat.items() if k not in ['results','config','signals_meta']},flush=True)
 (ROOT/'GRID0346_JANUARY_STRUCTURAL_MICRO_CAPITAL_RESULTS.json').write_text(json.dumps(output,indent=2));print('COMPLETE',flush=True)
if __name__=='__main__': main()
