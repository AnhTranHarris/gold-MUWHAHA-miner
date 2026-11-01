#!/usr/bin/env python3
"""Deterministic one-to-one MT5 trade-entry parity diagnostic for R9."""
import argparse,csv,datetime as dt,json,collections,statistics,bisect
from pathlib import Path

def sec(s):
    return int(dt.datetime.strptime(s,'%Y.%m.%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp())
def run(ref_path,replay_path,out):
    with open(ref_path) as f:
        ref=[{'s':sec(r['A']),'side':1 if r['D']=='buy' else -1,'price':float(r['G'])} for r in csv.DictReader(f) if r['E']=='in']
    with open(replay_path) as f:
        rep=[{'s':int(int(r['time_ms'])/1000),'side':int(r['side']),'price':float(r['price'])} for r in csv.DictReader(f)]
    first_replay=rep[0]['s'] if rep else 0
    warmup_end=max(first_replay,int(dt.datetime(2026,1,2,3,tzinfo=dt.timezone.utc).timestamp()))
    ref=[r for r in ref if r['s']>=warmup_end];rep=[r for r in rep if r['s']>=warmup_end]
    bins=[0,1,2,5,10]
    results={}
    for tolerance in bins:
        # Greedy forward bounded matching with side constraint; each reference and replay used once.
        used=set();match=[];miss=[]
        j=0
        for ri,r in enumerate(ref):
            while j<len(rep) and rep[j]['s']<r['s']-tolerance:j+=1
            # Inspect only nearby replay indices, not full-window search.
            cand=[];k=j
            while k<len(rep) and rep[k]['s']<=r['s']+tolerance:
                p=rep[k]
                if k not in used and p['side']==r['side']:
                    cand.append((abs(p['s']-r['s']),abs(p['price']-r['price']),k))
                k+=1
            if cand:
                _,_,k=min(cand)
                used.add(k)
                match.append((ri,k))
            else:miss.append(ri)
        price=[abs(ref[i]['price']-rep[k]['price']) for i,k in match]
        deltas=[rep[k]['s']-ref[i]['s'] for i,k in match]
        results[str(tolerance)]={'matched':len(match),'reference_total':len(ref),'replay_total':len(rep),
          'reference_recall':len(match)/len(ref) if ref else None,'replay_precision':len(match)/len(rep) if rep else None,
          'mean_abs_entry_price_diff':statistics.fmean(price) if price else None,'median_abs_entry_price_diff':statistics.median(price) if price else None,
          'exact_price_match_count':sum(x<=1e-6 for x in price),
          'median_delta_seconds':statistics.median(deltas) if deltas else None,
          'first_reference_unmatched':[ref[i] for i in miss[:20]],
          'first_replay_unmatched':[p for k,p in enumerate(rep) if k not in used][:20]}
    rc=collections.Counter(dt.datetime.fromtimestamp(x['s'],dt.timezone.utc).strftime('%Y-%m-%d') for x in ref)
    pc=collections.Counter(dt.datetime.fromtimestamp(x['s'],dt.timezone.utc).strftime('%Y-%m-%d') for x in rep)
    payload={'reference_baseline':'Coinexx-Demo MT5 R9 TickLogger REAL Jan-Jul 2026','comparison_january_after_native_atr_warmup':True,
       'warmup_cutoff_utc_naive_server_time':dt.datetime.fromtimestamp(warmup_end,dt.timezone.utc).isoformat(),
       'method':'one-to-one earliest-time-neighbor same direction, bid/ask market fills, time tolerances seconds',
       'by_day':[{'date':x,'reference_entries':rc.get(x,0),'replay_entries':pc.get(x,0),'delta':pc.get(x,0)-rc.get(x,0)} for x in sorted(rc|pc)],
       'tolerance_windows':results}
    Path(out).write_text(json.dumps(payload,indent=2));return payload
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ref',required=True);p.add_argument('--replay',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 r=run(a.ref,a.replay,a.out)
 print(json.dumps({k:{kk:vv for kk,vv in v.items() if not kk.startswith('first_')} for k,v in r['tolerance_windows'].items()},indent=2))
