"""Source-exact H1V2 UTC hour / direction / subminute timing oracle atlas.

Pure descriptive counts of completed hindsight-labeled market events.
NO assertion that conditions alone predict future BUY/SELL correctness.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
from h1v2_teacher import MONTHS

def compute(root='/mnt/data/h1v2/results'):
    root=Path(root)
    cand=np.zeros(24,dtype=np.int64);strict=np.zeros(24,dtype=np.int64)
    chosen=np.zeros(24,dtype=np.int64);buy=np.zeros(24,dtype=np.int64)
    elapsed=[];spreads=[]; per_month={}
    bands=[1000,3000,5000,10000,15000,20000,30000]
    for m in MONTHS:
        with np.load(root/f'h1v2_dukascopy_{m}_oracle_labels.npz') as d:
            hours=((d['t']//3600000)%24).astype(np.int8)
            anygood=(d['code']==1).any(axis=1)
            selected=d['selected_row'];sides=d['selected_side']
            cand+=np.bincount(hours,minlength=24)
            strict+=np.bincount(hours[anygood],minlength=24)
            chosen+=np.bincount(hours[selected],minlength=24)
            buy+=np.bincount(hours[selected][sides==1],minlength=24)
        with np.load(root/f'h1v2_dukascopy_{m}_selected_exact_trace.npz') as trace:
            ms=trace['first_favorable_elapsed_ms'];elapsed.extend(np.asarray(ms,dtype=np.int32))
            spreads.extend(np.asarray(trace['entry_ask']-trace['entry_bid'],dtype=np.float32))
            per_month[m]={'oracle_winners':int(len(ms)),
             'first_success_by_ms':{str(x):int((ms<=x).sum()) for x in bands},
             'median_first_favorable_ms':float(np.median(ms))}
    arr=np.array(elapsed,np.int32);sp=np.array(spreads,np.float32)
    hours=[dict(utc_hour=i,candidates=int(cand[i]),one_side_good=int(strict[i]),
                oracle_winners=int(chosen[i]),oracle_winners_per_10000_candidates=round(float(10000*chosen[i]/cand[i]),2) if cand[i] else 0.,
                oracle_buy_share=float(buy[i]/chosen[i]) if chosen[i] else None) for i in range(24)]
    result={'scope':'H1V2 offline future-privileged source-exact oracle by UTC hour; no policy feature of future',
            'month_count':4,'total_winners':len(arr),'utc_hour_summary':hours,'months':per_month,
            'first_favorable_within_elapsed_ms':{str(x):int((arr<=x).sum()) for x in bands},
            'first_favorable_elapsed_ms_p10_p50_p90':[float(np.percentile(arr,x)) for x in (10,50,90)],
            'selected_spread_p10_p50_p90':[float(np.percentile(sp,x)) for x in (10,50,90)],
            'top_hours_by_oracle_density_utc':[int(x) for x in np.argsort(-np.array([r['oracle_winners_per_10000_candidates'] for r in hours]))[:5]],
            'warning':'Hourly density and observed fast first-hit timing are hindsight descriptions, not a production entry rule. Revalidate causally chronologically.'}
    (root/'H1V2_OPPORTUNITY_ATLAS_20261102.json').write_text(json.dumps(result,indent=2))
    return result
if __name__=='__main__':
 o=compute();print(json.dumps({k:o[k] for k in ['total_winners','first_favorable_within_elapsed_ms','first_favorable_elapsed_ms_p10_p50_p90','selected_spread_p10_p50_p90','top_hours_by_oracle_density_utc']},indent=2))
