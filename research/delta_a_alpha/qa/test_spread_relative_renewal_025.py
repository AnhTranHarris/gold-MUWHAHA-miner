"""Original-024 *prototype* Watchdog spread-relative quantum stress, NOT original 131E parity.
Causal, quote-known (entry current spread). Original q at 1.10/1.19, new floor k*spread.
"""
import json,os,importlib.util,hashlib,time
from pathlib import Path
import numpy as np, pandas as pd
P=Path('/mnt/data/daa_january_full_execution_024')
s=(P/'jan024_reconstructed_full_portfolio.py').read_text()
s=s.replace('coverage_selected=1,spread_cap_raw=1300):','coverage_selected=1,spread_cap_raw=1300,wd_spread_mult=0.):')
s=s.replace('if src<0:continue\n        attempt[src]+=1','if src<0:continue\n        if src==5 and wd_spread_mult>0:tp=max(tp,int(spread*wd_spread_mult))\n        attempt[src]+=1')
assert 'wd_spread_mult' in s
f=P/'jan025_spread_relative_renewal_engine.py';f.write_text(s)
spec=importlib.util.spec_from_file_location('renewal025',f);M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
assert hashlib.sha256(M.ROOT.read_bytes()).hexdigest()==M.EXPECTED
D=pd.read_csv(M.ROOT,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
t=D.timestamp_ms_utc.to_numpy();a=D.ask_raw.to_numpy();b=D.bid_raw.to_numpy();del D
st=[M.completed_tf_state(t,b,k) for k in (14400000,3600000,900000,300000)]
key,starts,ends,rng=M.m5_completed(t,a,b)
rows=[]
for cap in (64,128):
 for k in (0.,1.,1.5,2.,3.):
  tic=time.monotonic();res=M.run(t,a,b,*st,rng,key,ends,0,cap,1,1300,k)
  entry,exit,pnl,source,dire,reason,wdcell,raw_ent,attempt,skips,*rest=res
  sc,rec,day,week=M.summarize(entry,exit,pnl,source,t,res,dire,raw_ent,reason,a,b)
  wd=rec[rec.source==5]
  row={'cap':cap,'spread_floor_multiple':k,'net':sc['net'],'trades':sc['trades'],'gross_loss':sc['gross_loss'],'PF':sc['profit_factor'],'win':sc['win_rate'],'equity_dd':sc['full_tick_equity_dd'],'watchdog_net':float(wd.net.sum()),'watchdog_trades':len(wd),'watchdog_gross_loss':float(wd.loc[wd.net<0,'net'].sum()),'runtime_seconds':round(time.monotonic()-tic,2)}
  rows.append(row);tmp=P/'JAN025_CAUSAL_SPREAD_QUANTUM.partial.json';tmp.write_text(json.dumps({'rows':rows,'source':'DAA January 024 prototype, not original Gamma parent scheduler, January-only development'},indent=2));os.replace(tmp,P/'JAN025_CAUSAL_SPREAD_QUANTUM.json')
  print(json.dumps(row),flush=True)
print('COMPLETE',len(rows),flush=True)