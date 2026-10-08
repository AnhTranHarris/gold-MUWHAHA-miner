"""Bounded Jan V1-prototype L6 native stop overlay (not original 131E).
No future labels used to place orders; parameter sweep on January only, not blind.
"""
from pathlib import Path
import importlib.util, json, os, hashlib, time, sys
import numpy as np, pandas as pd
P=Path('/mnt/data/daa_january_full_execution_024')
ORIGINAL=P/'jan024_reconstructed_full_portfolio.py'
SRC=ORIGINAL.read_text()
assert 'coverage_selected=1,spread_cap_raw=1300):' in SRC
assert 'if src<0:continue\n        attempt[src]+=1' in SRC
modified=SRC.replace('coverage_selected=1,spread_cap_raw=1300):', 'coverage_selected=1,spread_cap_raw=1300,native_stop_raw=0):')
modified=modified.replace('if src<0:continue\n        attempt[src]+=1','if src<0:continue\n        if src==6 and sl==0 and native_stop_raw>0:sl=native_stop_raw\n        attempt[src]+=1')
assert modified!=SRC
OUT_P=P/'jan025_native_stop_overlay_engine.py';OUT_P.write_text(modified)
spec=importlib.util.spec_from_file_location('jan025',OUT_P);M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
raw='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
sha=hashlib.sha256(Path(raw).read_bytes()).hexdigest();assert sha==M.EXPECTED
DF=pd.read_csv(raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
t=DF.timestamp_ms_utc.to_numpy();a=DF.ask_raw.to_numpy();b=DF.bid_raw.to_numpy();del DF
states=[M.completed_tf_state(t,b,k) for k in (14400000,3600000,900000,300000)]
key,starts,ends,rng=M.m5_completed(t,a,b)
rows=[]
for cap in (64,128):
 for stop in (0,500,1000,2000,4000,8000):
  st=time.monotonic();res=M.run(t,a,b,*states,rng,key,ends,0,cap,1,1300,stop)
  entry,exit,pnl,source,dire,reason,wdcell,raw_ent,attempt,skips,*rest=res
  score,rec,daily,weekly=M.summarize(entry,exit,pnl,source,t,res,dire,raw_ent,reason,a,b)
  assert score['max_open']<=cap
  assert score['raw_quote_pnl_parity_max_abs']<1e-9
  r={k:score[k] for k in ['net','trades','gross_profit','gross_loss','profit_factor','win_rate','expectancy','balance_drawdown_exact','full_tick_equity_dd','max_open','raw_quote_pnl_parity_max_abs']};r.update({'cap':cap,'native_stop_raw':stop,'seconds':round(time.monotonic()-st,2),'positive_days':int((daily.net>0).sum()),'negative_days':int((daily.net<0).sum()),'positive_weeks':int((weekly.net>0).sum()),'sources':score['sources'],'single_tick_open':True})
  rows.append(r);tmp=P/'JAN025_NATIVE_STOP_SWEEP.partial.json';tmp.write_text(json.dumps({'rows':rows,'execution':'actual Bid/Ask first touch Jan 2026, 0.01 lot, +$0.02 commission per ticket, source selected Jan024 nonparity prototype'},indent=2));os.replace(tmp,P/'JAN025_NATIVE_STOP_SWEEP.json')
  print(json.dumps({k:r[k] for k in ['cap','native_stop_raw','net','gross_loss','profit_factor','trades','win_rate','full_tick_equity_dd','seconds']}),flush=True)
print('COMPLETE',len(rows),flush=True)