"""JAN-only high-ATR harvest parameter neighborhood with R9-teacher-phase exclusion.
Funded original Dukascopy tick replays; source events fixed & causal; no calendar switching.
"""
from pathlib import Path
import sys,time
import pandas as pd,numpy as np
D=Path(__file__).resolve().parent;P=Path('/mnt/data/jan_new_discovery_20261014');sys.path.insert(0,str(D));sys.path.insert(1,str(P))
from jan_r9_teacher_m1_phase_risk_v1 import replay_phase,COLS
from r9_teacher_informed_dukas_executor import features
SRC=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')

def main():
 st=time.time();d=pd.read_csv(SRC,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'});ms=d.timestamp_ms_utc.to_numpy();b=d.bid_raw.to_numpy();a=d.ask_raw.to_numpy();del d
 z=np.load(P/'jan_parent_causal_squeeze_signals.npz');sec,_,_,_,_,f=features(ms,b);assert np.array_equal(sec,z['sec']);sig=z['signal'];atr=f[300][1];dummy=np.zeros(len(sec),np.int8)
 cases=[]
 for larm,lgap in [(4.,2.),(5.,2.5),(6.,3.)]:
  for harm,hgap in [(5.,2.5),(6.,3.),(7.,3.5),(8.,4.),(9.,4.5)]:
   for hhold in [1200,1500,2100,2700]:
    cases.append((larm,lgap,harm,hgap,hhold))
 rows=[];cand=[]
 for i,(la,lg,ha,hg,hold) in enumerate(cases):
  cfg=np.array([(7.,20.,la,lg,1500.),(7.,40.,ha,hg,hold)],np.float64)
  arr,state=replay_phase(ms,b,a,sec,sig,atr,dummy,dummy,100.,cfg,1,-1,999.,0.,2,59,(1<<24)-1)
  p=arr[:,6] if len(arr) else np.empty(0);gp=float(np.maximum(p,0).sum());gl=float(np.minimum(p,0).sum());net=float(state[0]);
  if len(arr):
   dates=pd.to_datetime(arr[:,2],unit='ms',utc=True);d0=pd.DataFrame({'d':dates.floor('D'),'p':p}).groupby('d').p.sum();pdays=int((d0>0).sum());ndays=int((d0<0).sum());first=float(p[dates.day<=15].sum());second=float(p[dates.day>15].sum());hours=len(set(dates.floor('h')))
  else:pdays=ndays=hours=0;first=second=0.
  rr=dict(id=i,low_arm=la,low_gap=lg,high_arm=ha,high_gap=hg,high_hold=hold,net=round(net,6),trades=len(arr),gp=round(gp,6),gl=round(gl,6),pf=round(gp/-gl,5) if gl<0 else None,max_dd=round(float(state[2]),5),halt=int(state[3]),first_half=round(first,5),second_half=round(second,5),positive_days=pdays,negative_days=ndays,active_hours=hours)
  rows.append(rr)
  if net>0 and not state[3]:cand.append((net,rr,arr.copy()))
  if (i+1)%20==0:print('REPLAY',i+1,len(cases),round(time.time()-st,2),flush=True)
 df=pd.DataFrame(rows);df.to_csv(D/'JAN_PHASE_ATR_JOINT_60_SETTINGS_RESULTS.csv',index=False)
 print('BEST_NET\n',df.sort_values('net',ascending=False).head(18).to_string(index=False),flush=True)
 print('BEST_GROSSLOSS_WITH_NET_ABOVE_240\n',df[(df.net>=240.962)&(df.trades>=160)].sort_values('gl',ascending=False).head(12).to_string(index=False),flush=True)
 cand.sort(key=lambda x:x[0],reverse=True);c2=sorted([x for x in cand if x[1]['net']>=240.962 and x[1]['trades']>=160],key=lambda x:x[1]['gl'],reverse=True)
 seen=set()
 for _,r,t in cand[:8]+c2[:8]:
  if r['id'] not in seen:
   pd.DataFrame(t,columns=COLS).to_csv(D/f'JAN_PHASE_ATR_JOINT_CASE_{r["id"]}_LEDGER.csv',index=False);seen.add(r['id'])
 print('DONE',round(time.time()-st,2),flush=True)
if __name__=='__main__':main()
