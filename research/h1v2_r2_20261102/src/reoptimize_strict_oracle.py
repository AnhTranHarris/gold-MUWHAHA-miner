"""Future-privileged H1V2 R2: re-optimize FIRST30 strict fast teacher.
Calls ORIGINAL H1V2 quote-exact schedule_oracle() without modifying it.
Objective max number nonoverlapping HIGH QUALITY first-hits, tie by net.
All future labels used in selection. No live/realtime model or edge claim.
"""
from pathlib import Path
import json,time,hashlib,math,sys,os
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2/src')
from h1v2_teacher import schedule_oracle,read_ticks,digest
from h1v2_freeze import PINNED
OUT=Path('/mnt/data/h1v2_r2/results');OLD=Path('/mnt/data/h1v2/results');RAW=Path('/mnt/data')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
RULES={'FAST3S_NET10_SPR100':dict(ms=3000,net=.10,spread=1.0),
       'FAST5S_NET20_SPR100':dict(ms=5000,net=.20,spread=1.0)}

def run_month(month):
    if month not in SYNTH:raise ValueError(month)
    tic=time.monotonic();p=RAW/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
    if digest(p)!=PINNED[month]:raise ValueError('raw hash drift')
    t,b,a=read_ticks(p)
    out={'month':month,'source_sha256':PINNED[month],'rules':{}}
    with np.load(OLD/f'h1v2_dukascopy_{month}_oracle_labels.npz',allow_pickle=False) as q:
        ix=q['tick_index'];timeq=q['t'];code=q['code'];net=q['net'];first=q['first_event_ms'];exitix=q['exit_tick_index']
        assert np.array_equal(t[ix],timeq)
        spread=a[ix]-b[ix]
        for tag,c in RULES.items():
            qualifying=(code==1)&(first>=0)&(first<=c['ms'])&(net>=c['net'])&(spread[:,None]<=c['spread']+1e-5)
            qualified_code=np.where(qualifying,1,0).astype(np.int8)
            chosen,side,dp=schedule_oracle(ix,qualified_code,net,exitix)
            w=(side==-1).astype(np.int64);entries=ix[chosen];exits=exitix[chosen,w]
            assert np.all(qualifying[chosen,w])
            if len(entries)>1:assert np.all(entries[1:]>exits[:-1])
            assert np.all(t[exits]-t[entries]<=30000)
            trace=OUT/f'H1V2_R2_{tag}_{month}_DP_REOPTIMIZED_SOURCE_EXACT.npz'
            np.savez_compressed(trace,entry_tick_ix=entries,entry_utc_ms=t[entries],side=side,
                entry_bid=b[entries],entry_ask=a[entries],exit_tick_ix=exits,exit_utc_ms=t[exits],
                exit_bid=b[exits],exit_ask=a[exits],first_favorable_elapsed_ms=first[chosen,w],net=net[chosen,w])
            oldn=len(np.load(OUT/f'H1V2_R2_{tag}_{month}_EXACT_SELECTED_TRACE.npz')['side']);n=len(side)
            assert n>=oldn
            out['rules'][tag]={'count':n,'original_schedule_filtered_count':oldn,'gain_over_filtered_count':n-oldn,
               'monthly_floor':math.ceil(.8*SYNTH[month]),'monthly_floor_pass':n>=math.ceil(.8*SYNTH[month]),
               'net_sum_modeled_usd':round(float(net[chosen,w].sum()),3),'output':trace.name,'sha256':digest(trace)}
            print(month,tag,'optimized',n,'vs filtered',oldn,'additional',n-oldn,flush=True)
    out['elapsed_seconds']=round(time.monotonic()-tic,2)
    (OUT/f'H1V2_R2_{month}_DP_REOPTIMIZED_RECEIPT.json').write_text(json.dumps(out,indent=2))
    return out
if __name__=='__main__':
 m=sys.argv[1];print(json.dumps(run_month(m),indent=2),flush=True)
