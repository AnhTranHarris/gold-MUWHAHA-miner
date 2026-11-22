"""Bounded source-pinned screening. W1 research only; no parameter/EA approval."""
from __future__ import annotations
import json,subprocess,time,os,csv,sys
from pathlib import Path
import pandas as pd
from score_alignment import match_batch,REFERENCE
import numpy as np
from scipy.sparse.csgraph import maximum_bipartite_matching

ROOT=Path(__file__).parent
RAW=os.environ.get('R9_REAL_TICKS','/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz')
ref=pd.read_csv(REFERENCE)
re=ref.entry_sec.to_numpy(np.int64);rx=ref.exit_sec.to_numpy(np.int64);rs=np.where(ref.side.to_numpy()=='BUY',1,-1)

GROUPS=[
 ('R9_EXACT',[]),
 ('GAP_20',['--gap=20']),
 ('GAP_40',['--gap=40']),
 ('RANGE_30',['--minrange=30']),
 ('RANGE_70',['--minrange=70']),
 ('EFF_050',['--eff=0.50']),
 ('EFF_085',['--eff=0.85']),
 ('ATR_075',['--atr_multiplier=0.75']),
 ('ATR_125',['--atr_multiplier=1.25']),
 ('SPREAD_40',['--spread=40']),
 ('STOP_60',['--stop=60']),
 ('TRAIL_10',['--trail=10']),
 ('ACTIVATION_30',['--activation=30']),
 ('HOLD_15',['--hold=15']),
 ('HOLD_45',['--hold=45']),
 ('REARM_1',['--rearm=1']),
 ('REARM_5',['--rearm=5']),
 ('EFF_030',['--eff=0.30']),
 ('EFF_040',['--eff=0.40']),
 ('STOP_100',['--stop=100']),
 ('STOP_100_ACT_30',['--stop=100','--activation=30']),
 ('STOP_100_NOTRAIL',['--stop=100','--no_trail']),
 ('GAP_20_EFF_050',['--gap=20','--eff=0.50']),
 ('EFF_000',['--eff=0.0']),
 ('RANGE_30_EFF_000',['--minrange=30','--eff=0.0']),
]

def screen_one(name,options):
    target=ROOT/(name+'.csv');t0=time.monotonic()
    r=subprocess.run([str(ROOT/'r9_real_replay'),RAW,str(target),*options],capture_output=True,text=True,check=True,timeout=30)
    st=json.loads(r.stderr.strip().splitlines()[-1]); t1=time.monotonic()
    got=pd.read_csv(target).sort_values('entry_time_msc').reset_index(drop=True)
    ge=got.entry_time_msc.to_numpy(np.int64)//1000;gx=got.exit_time_msc.to_numpy(np.int64)//1000;gs=got.side.to_numpy(np.int8);gn=got.net_quote_cents.to_numpy(np.int64)
    matched=match_batch((re,rx,rs),(ge,gx,gs,gn),2,'joint');entry=match_batch((re,rx,rs),(ge,gx,gs,gn),2,'entry')
    # Stress proxy: $0.20 price-equivalent per ounce rather than actual trade commission.
    p20=int((gn>20).sum())
    del got
    target.unlink()  # keep only small research metrics, not 2-3 MB * 17 variants
    return {'name':name,'options':' '.join(options),'real_trades':st['entries'],'real_positive':st['positive'],'real_negative':st['negative'],'real_flat':st['flat'],'real_positive_after_20c_per_oz_proxy':p20,'quote_pnl_usd_per_one_oz':round(st['net_quote_cents']/100,2),'matched_entries_2s':entry['matched'],'matched_entry_exit_2s':matched['matched'],'stop_count':st['stop'],'timeout_count':st['timeout'],'gate_spread':st['gate_spread'],'gate_atr':st['gate_low_atr'],'gate_s1':st['gate_s1'],'rearm_count':st['rearmed'],'scan_sec':round(t1-t0,3),'total_sec':round(time.monotonic()-t0,3)}

def main():
    n0=int(sys.argv[1]) if len(sys.argv)>1 else 0
    n1=int(sys.argv[2]) if len(sys.argv)>2 else len(GROUPS)
    out=ROOT/'screen_results.jsonl'
    for i in range(n0,n1):
        name,opts=GROUPS[i]
        o=screen_one(name,opts)
        with out.open('a') as f:f.write(json.dumps(o)+'\n')
        print(json.dumps(o),flush=True)
if __name__=='__main__':main()
