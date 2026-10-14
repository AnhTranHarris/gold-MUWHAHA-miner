"""Read-only original candidate source materialization accelerated solely by cached byte-equivalent original tick arrays."""
import sys, json, time, numpy as np
from pathlib import Path
sys.path.insert(0,'/mnt/data/jan_work/engine')
import grid0274_quote_funded_admission_replay as raw
import grid0290_funded_portfolio_source_heat_cap as orig
P=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH')
Z=Path('/mnt/data/jan_recovery_20261013/trades_cap256_hold1.0_interval125.npz')
R=Path('/mnt/data/jan_recovery_20261013/ORIGINAL/r9_synth_jan_daily_weekly.json')
def cached_load():
 t=np.load(P/'ticks_t.npy',mmap_mode='r');b=np.load(P/'ticks_bid.npy',mmap_mode='r');a=np.load(P/'ticks_ask.npy',mmap_mode='r');z=np.load(Z);r9=json.loads(R.read_text());assert len(t)==9135062
 return t,b,a,z,r9
raw.load=cached_load
print('PREPARING source',flush=True);start=time.time()
t,b,a,z,kind,owner,pgid,r9,origin=orig.materialize()
print('MATERIALIZED',len(t),len(z['entry_idx']),len(pgid),round(time.time()-start,2),origin,flush=True)
output=Path('/mnt/data/r8_followup_20261014')/'original_research_candidate_unfiltered_cache.npz'
np.savez(output,**z,kind=kind,owner=owner,pgid=pgid)
print('SAVED',output,output.stat().st_size,round(time.time()-start,2),flush=True)
