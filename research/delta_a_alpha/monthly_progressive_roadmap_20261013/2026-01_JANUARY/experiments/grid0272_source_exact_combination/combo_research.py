"""GRID0272 hypothesis-driven combination screening. January full raw Dukascopy ticks.
RESEARCH-ONLY, not original Watchdog replay and not FourSessionV1 integration.
All signals at existing quote times, price Bid/Ask, +250ms pending, no look-ahead.
No win-dependent sizing. No month/date features. Fixed 0.01 lot/1oz, $0.20 round trip.
"""
import json, hashlib, time
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit
ROOT=Path('/mnt/data/GRID0272_JAN_COMBINATIONS');SRC=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
@njit(cache=True)
def simulate(t,ask,bid,step_d,stop_d,tgt_d,hold_ms,cap,spread_max,mode,trend_s,trend_l,
             mom_min,mom_max,renew,session,trail_d,entry_cool_ms,volume_reversal):
 n=len(t)
 # Original tick chronological point-in-time states, no future/last incomplete bar
 pos_dir=np.zeros(cap,np.int8);pos_entry=np.zeros(cap,np.float64);pos_t=np.zeros(cap,np.int64)
 pos_hi=np.zeros(cap,np.float64);pos_parent=np.zeros(cap,np.int32)
 active=0;open_peak=0;signals=0;closed=0;wins=0;gp=0.;gl=0.;float_peak=100000.;float_dd=0.;balance_peak=100000.;balance_dd=0.;cash=100000.
 # continuous as-of grid parent boundary, cooldown, proof only on realized closes
 anchor=(ask[0]+bid[0])/2000.;last_event=t[0]-1000000;last_good_exit=t[0]-1000000
 proof=0;unlocks=0;relocks=0;permitted=0;spread_block=0;cap_block=0;false_mom=0;pending_ms=-1;pending_dir=0;pending_exp=-1
 i_fast=0;i_slow=0
 day_num=np.full(100000,-1,np.int64);day_pnl=np.zeros(100000,np.float64);day_reason=np.zeros(100000,np.int16);j0=0
 for i in range(n):
  now=t[i];mid=(ask[i]+bid[i])/2000.;spr=(ask[i]-bid[i])/1000.
  while i_fast<i and t[i_fast]<now-trend_s:i_fast+=1
  while i_slow<i and t[i_slow]<now-trend_l:i_slow+=1
  fast=(ask[i_fast]+bid[i_fast])/2000.;slow=(ask[i_slow]+bid[i_slow])/2000.
  mom=mid-fast;drift=mid-slow
  # expire/settle all due children at the SAME actually observed tick (no skipped quote path)
  k=0
  while k<active:
   direction=pos_dir[k];px=bid[i]/1000. if direction==1 else ask[i]/1000.
   raw=direction*(px-pos_entry[k]);pos_hi[k]=max(pos_hi[k],raw)
   reason=0
   if raw<=-stop_d:reason=1
   elif raw>=tgt_d:reason=2
   elif trail_d>0 and pos_hi[k]>trail_d*2 and raw<=pos_hi[k]-trail_d:reason=3
   elif now-pos_t[k]>=hold_ms:reason=4
   if reason:
    pnl=raw-.20;cash+=pnl;closed+=1;gp+=max(0.,pnl);gl+=min(0.,pnl);wins+=int(pnl>0)
    if j0<len(day_num):day_num[j0]=now//86400000;day_pnl[j0]=pnl;day_reason[j0]=reason;j0+=1
    # Four already-realized winners + <=60 sec; losing/slow closes relock
    old=proof>=4
    if pnl>0 and now-pos_t[k]<=60000:proof=min(5,proof+1)
    else:proof=0
    if (proof>=4) and not old:unlocks+=1
    if old and proof<4:relocks+=1
    if pnl>0:last_good_exit=now
    active-=1
    if k<active:
     pos_dir[k]=pos_dir[active];pos_entry[k]=pos_entry[active];pos_t[k]=pos_t[active];pos_hi[k]=pos_hi[active];pos_parent[k]=pos_parent[active]
    continue
   k+=1
  eq=cash
  for k in range(active):
   eq+=(pos_dir[k]*((bid[i] if pos_dir[k]==1 else ask[i])/1000.-pos_entry[k])-.20)
  float_peak=max(float_peak,eq);float_dd=max(float_dd,float_peak-eq)
  balance_peak=max(balance_peak,cash);balance_dd=max(balance_dd,balance_peak-cash)
  # strict pending next quote at +250ms, with maximum 2 sec exp
  if pending_ms>=0 and now>=pending_ms:
   if now<=pending_exp and spr<=spread_max and active<cap:
    pos_dir[active]=pending_dir;pos_entry[active]=ask[i]/1000. if pending_dir==1 else bid[i]/1000.;pos_t[active]=now;pos_hi[active]=-1e10;pos_parent[active]=1;active+=1;open_peak=max(open_peak,active);permitted+=1
   pending_ms=-1
   continue
  if pending_ms>=0:continue
  if now-last_event<entry_cool_ms:continue
  diff=mid-anchor
  if abs(diff)<step_d:continue
  movement=1 if diff>0 else -1
  # Current quote crossed step; reset without relying on skipped grid levels
  anchor=mid;last_event=now;signals+=1
  if spr>spread_max:spread_block+=1;continue
  if active>=cap:cap_block+=1;continue
  if session:
   hod=(now//3600000)%24
   if session==1 and not (9<=hod<=21):continue
   if session==2 and not (12<=hod<=21):continue
   if session==3 and not ((hod==2) or (9<=hod<=21)):continue
  # parent scalp directions; fast and long as-of trend alignment
  if mode==0:direction=movement
  elif mode==1:direction=-movement
  elif mode==2:direction=1 if drift>0 else -1
  elif mode==3:direction=movement if drift*movement>0 else 0
  elif mode==4:direction=-movement if drift*movement<0 else 0
  elif mode==5:direction=movement if mom*movement>0 and drift*movement>0 else 0
  elif mode==6:direction=-movement if mom*movement<0 and drift*movement>0 else 0
  elif mode==7:direction=-movement if mom*movement<0 else 0
  elif mode==8:direction=movement if mom*movement>0 else 0
  else:direction=0
  if direction==0:continue
  # momentum gates / source regime; all are strictly point-in-time
  if mom_min>0 and abs(mom)<mom_min:false_mom+=1;continue
  if mom_max>0 and abs(mom)>mom_max:false_mom+=1;continue
  if volume_reversal==1 and mom*drift<=0:continue
  if volume_reversal==2 and mom*drift>=0:continue
  if renew==1 and proof<4: # bounded scout, does not become deadlock
   if (now-last_good_exit)<50000 or (signals%12)!=0:continue
  if renew==2 and proof<4:
   if signals%6!=0:continue
  if renew==3 and proof>=4 and active>=cap//2:continue
  pending_ms=now+250;pending_exp=now+2000;pending_dir=direction
 # At month's last quote, liquidate OPEN exposures using REAL quote, no profit from vanished period
 last=n-1
 for k in range(active):
  raw=pos_dir[k]*((bid[last] if pos_dir[k]==1 else ask[last])/1000.-pos_entry[k]);pnl=raw-.20;cash+=pnl;gp+=max(pnl,0.);gl+=min(pnl,0.);closed+=1;wins+=int(pnl>0)
  if j0<len(day_num):day_num[j0]=t[last]//86400000;day_pnl[j0]=pnl;day_reason[j0]=5;j0+=1
 return np.array([cash-100000.,closed,wins,gp,gl,float_dd,balance_dd,open_peak,signals,permitted,spread_block,cap_block,false_mom,unlocks,relocks,active],np.float64),day_num[:j0],day_pnl[:j0],day_reason[:j0]

def metrics(name,cfg,result,day,pnl,reason,seconds):
 d={};w={}
 for n,v in zip(day,pnl):
  ts=pd.Timestamp(int(n)*86400000,unit='ms',tz='UTC');dd=str(ts.date());iso=ts.isocalendar();wk=f'{iso.year}-W{iso.week:02d}';d[dd]=d.get(dd,0)+float(v);w[wk]=w.get(wk,0)+float(v)
 r=dict(name=name,settings=cfg,net=float(result[0]),closed=int(result[1]),wins=int(result[2]),gross_profit=float(result[3]),gross_loss=float(result[4]),pf=float(result[3]/max(.000001,-result[4])),full_equity_dd=float(result[5]),balance_dd=float(result[6]),max_open=int(result[7]),source_crossings=int(result[8]),filled=int(result[9]),spread_denied=int(result[10]),cap_denied=int(result[11]),momentum_denied=int(result[12]),watchdog_unlocks=int(result[13]),watchdog_relocks=int(result[14]),end_open_liquidated=int(result[15]),positive_days=sum(v>0 for v in d.values()),positive_weeks=sum(v>0 for v in w.values()),week_net={k:round(v,3) for k,v in sorted(w.items())},day_net={k:round(v,3) for k,v in sorted(d.items())},elapsed_s=seconds)
 return r
if __name__=='__main__':
 df=pd.read_csv(SRC,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=df.timestamp_ms_utc.to_numpy();ask=df.ask_raw.to_numpy();bid=df.bid_raw.to_numpy();print('LOADED',len(t),flush=True)
 # targeted combinational scenarios, not individualized month/day rule.
 scenarios=[]
 for mode in [0,1,3,4,5,6,7,8]:
  for step in [.2,.5,1.,1.19]:
   for stop,target in [(1.0,1.8),(1.8,3.2),(2.8,4.8)]:
    scenarios.append((mode,step,stop,target,120000,16,.65,10000,120000,0.,0.,0,1,0,1000,0))
 # compile, run 96 combinations (including price/session/MTF directional rule)
 res=[];start=time.time()
 for ix,cfg in enumerate(scenarios):
  st=time.time();result,day,pnl,reason=simulate(t,ask,bid,cfg[1],cfg[2],cfg[3],cfg[4],cfg[5],cfg[6],cfg[0],cfg[7],cfg[8],cfg[9],cfg[10],cfg[11],cfg[12],cfg[13],cfg[14],cfg[15]);r=metrics('C%03d'%ix,cfg,result,day,pnl,reason,round(time.time()-st,2));res.append(r)
  if (ix+1)%8==0:
   winner=max(res,key=lambda z:z['net']);print('CYCLE',ix+1,'best',round(winner['net'],2),'trades',winner['closed'],'dd',round(winner['full_equity_dd'],2),'elapsed',round(time.time()-start,1),flush=True)
  (ROOT/'combo_results.json').write_text(json.dumps({'data_source_sha':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','trials':res,'max_target_month':41520.82,'scope':'COMBINED_RESEARCH_PROTOTYPES_NOT_APPROVED_V1'},indent=2)) if (ix+1)%8==0 else None
 res.sort(key=lambda x:-x['net']);(ROOT/'combo_results.json').write_text(json.dumps({'data_source_sha':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','trials':res,'max_target_month':41520.82,'scope':'COMBINED_RESEARCH_PROTOTYPES_NOT_APPROVED_V1'},indent=2));print('DONE',len(res),'best',res[0]['net'],'pf',res[0]['pf'])
