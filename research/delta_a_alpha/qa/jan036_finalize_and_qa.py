"""Atomic 036 state QC/report using ONLY completed scenario outputs and reruns.
Not full original V1 funded parent/child parity. Does not change original candidate stream.
"""
import sys,json,hashlib,tarfile,csv,os
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,pandas as pd
ROOT=Path('/mnt/data/daa_jan_lattice_036');sys.path.insert(0,str(ROOT))
from jan036_adaptive_cell_governor import engine as adaptive,load
from jan036_adverse_direction_lattice import engine as baseengine
from jan036_trend_transfer_runner import engine as runner
from jan036_pricecell_cohort import engine as cells
src_files=['jan036_adverse_direction_lattice.py','jan036_pricecell_cohort.py','jan036_adaptive_cell_governor.py','jan036_high_velocity_combo.py','jan036_trend_transfer_runner.py', 'jan036_finalize_and_qa.py']
main_cases=['lattice_base384','lock_12_90s','inverse_24_trail','runner_c0_sh10000_tp30000','dyn_w1000_n128_spr1500_disp8000','dyn_w2000_n256_spr1500_lock12000','highvel_q384_w1000_n256_sp1500_lock12','highvel_q384_w1000_n384_sp2500_lock12']

def main():
 t,a,b,E,X,R,D,S=load();zlist=[];seen=set()
 for p in ROOT.glob('*.json'):
  try:r=json.loads(p.read_text())
  except Exception:continue
  if isinstance(r,dict) and 'params' in r and 'net' in r and 'gross_loss' in r:
   assert r['name'] not in seen,r['name']; seen.add(r['name'])
   zlist.append({k:r[k] for k in ('name','net','trades','gross_profit','gross_loss','PF','win_pct','equity_dd','maxopen','wd_max','lock_events','wd_rejected','recovery_trades','recovery_net','hourly_net')})
 assert len(zlist)>=100,len(zlist)
 pd.DataFrame(zlist).sort_values('name').to_csv(ROOT/'JAN036_ALL_CASES.csv',index=False)
 raw=pd.read_csv('/mnt/data/daa_jan_combined_035/JAN035_FINAL_MONTHLY_COMPARISON.csv')
 scores=[]; QA=[]; tape_dir=ROOT/'selected_tapes';tape_dir.mkdir(exist_ok=True)
 for name in main_cases:
  orig=json.loads((ROOT/(name+'.json')).read_text());params=orig['params'];
  if name.startswith('highvel_') or name.startswith('dyn_'): ret=adaptive(t,a,b,E,X,R,D,S,*params)
  elif name.startswith('runner_'):
   from stmr_base import bar_states
   mid=(a.astype(np.int64)+b.astype(np.int64))//2
   m5=bar_states(t,mid,300000);m15=bar_states(t,mid,900000)
   ret=runner(t,a,b,E,X,R,D,S,m5,m15,*params)
  else:ret=baseengine(t,a,b,E,X,R,D,S,*params)
  p,s,x,entry=ret[:4]
  assert np.all(x>=entry),name
  assert np.all(a[x]>=b[x]),name
  assert abs(p.sum()-orig['net'])<.012, (name,p.sum(),orig['net'])
  assert abs(p[p<0].sum()-orig['gross_loss'])<.012,(name,'gross',p[p<0].sum(),orig['gross_loss'])
  assert abs(ret[4]-orig['equity_dd'])<.012,(name,ret[4],orig['equity_dd'])
  assert np.sum(s==1)>0
  assert abs(p[s==1].sum()-60197.326)<.01
  # Integrity: any retained source trade is an original known candidate with exact source PnL.
  # The originally funded parent chain is NOT recomputed: do not certify it here.
  source_mask=s!=7
  if np.any(source_mask):
   original_by_key={(int(E[j]),int(X[j]),int(S[j])):int(j) for j in range(len(E))}
   for ti,xi,si,pi in zip(entry[source_mask],x[source_mask],s[source_mask],p[source_mask]):
    idx=original_by_key.get((int(ti),int(xi),int(si)))
    assert idx is not None,(name,ti,xi,si)
    close=int(b[xi] if D[idx]>0 else a[xi]);exp=int(D[idx])*(close-int(R[idx]))/1000.-.02
    assert abs(pi-exp)<1e-9,(name,exp,pi)
  dts=pd.to_datetime(t[x],unit='ms',utc=True)
  daily=pd.DataFrame({'date':dts.strftime('%Y-%m-%d'),'net':p,'trades':1}).groupby('date',as_index=False).agg({'net':'sum','trades':'sum'})
  weekly=pd.DataFrame({'week':dts.strftime('%G-W%V'),'net':p,'trades':1}).groupby('week',as_index=False).agg({'net':'sum','trades':'sum'})
  assert abs(daily.net.sum()-p.sum())<1e-7 and abs(weekly.net.sum()-p.sum())<1e-7
  daily['scenario']=name;weekly['scenario']=name
  scores.append((daily,weekly))
  file=tape_dir/(name+'_tape.npz')
  np.savez_compressed(file,p=p,s=s,x=x,e=entry)
  QA.append({'scenario':name,'reconciled':True,'ticks':len(t),'tickets':len(p),'original_candidate_source_deals':int(source_mask.sum()),'independent_recovery_deals':int(np.sum(s==7)),'hourly_immutable_net':round(float(p[s==1].sum()),3),'equity_dd':round(float(ret[4]),2),'max_open':int(ret[5]),'daily_weekly_reconcile':True,'source_original_bidask_match':True,'full_funded_genealogy_recomputed':False})
 pd.concat([x[0] for x in scores],ignore_index=True).to_csv(ROOT/'JAN036_SELECTED_DAILY.csv',index=False)
 pd.concat([x[1] for x in scores],ignore_index=True).to_csv(ROOT/'JAN036_SELECTED_WEEKLY.csv',index=False)
 sel=pd.DataFrame([x for x in zlist if x['name'] in main_cases]);sel.to_csv(ROOT/'JAN036_SELECTED_MONTHLY.csv',index=False)
 result={'status':'SOURCE_CANDIDATE_SCREEN_PASS__NOT_WATCHDOG_FUNDED_PARITY','original_quote_source_ticks':int(len(t)),'original_candidate_deals':len(E),'experiment_scenarios':len(zlist),'detailed_source_reconciled_replays':len(QA),'all_checks_passed':True,'selected':QA,'caveats':['Source Watchdog admission proposals NOT regenerated after rejected or early exited children','Current trade confirmations are from tick-derived completed EMAs, not exact historical native 134K pipeline','Recovery microgrid 0.01 each, independent and loses money in all tested cases','Coinexx broker simultaneous 384-order acceptance and margin NOT certified','January already used to select params; no independent deployment validation','August/september never opened']}
 (ROOT/'JAN036_QA_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 print('QA',json.dumps({'status':result['status'],'scenarios':len(zlist),'replay_checks':len(QA),'all_pass':True}))
if __name__=='__main__':main()