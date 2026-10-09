"""Full original genuine Feb quotes vs source FEB041 completed 10m-range oracle.

Original source archived FEB041_COMPLETED_10M_CONTEXT.csv; compares actual
quote-by-quote midpoint high-low, no artificial bar smoothing, no market labels.
"""
from pathlib import Path
import pandas as pd, numpy as np, hashlib, json
RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_02_ticks.csv(3).gz')
ORIG=Path('/mnt/data/feb_source_phase/FEB041/FEB041_COMPLETED_10M_CONTEXT.csv')
OUT=Path(__file__).parent/'FEB041_COMPLETED_10M_RANGE_FULL_QUOTE_PARITY.json'
EXPECTED_RAW='ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'

def run():
    with RAW.open('rb') as f: sha=hashlib.file_digest(f,'sha256').hexdigest()
    assert sha==EXPECTED_RAW,sha
    complete={}; count=0;prev_t=-1
    for chunk in pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],chunksize=240000,dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'}):
        t=chunk.timestamp_ms_utc.to_numpy()
        assert np.all(t[1:]>=t[:-1]) and t[0]>=prev_t
        prev_t=int(t[-1]);count+=len(t)
        ends=(t//600000+1)*600000
        twice_mid=(chunk.ask_raw.to_numpy()+chunk.bid_raw.to_numpy())
        order=np.flatnonzero(np.r_[True,np.diff(ends)!=0])
        stops=np.r_[order[1:],len(t)]
        for a,b in zip(order,stops):
            end=int(ends[a]);mid=twice_mid[a:b]
            if end not in complete:complete[end]=[len(mid),int(mid.min()),int(mid.max())]
            else:
                p=complete[end];p[0]+=len(mid);p[1]=min(p[1],int(mid.min()));p[2]=max(p[2],int(mid.max()))
    saved=pd.read_csv(ORIG)
    mismatches=[]
    for rec in saved.itertuples():
        e=int(rec.bucket_end_ms)
        c=complete.get(e)
        if c is None: mismatches.append({'bucket':e,'reason':'missing'})
        elif c[0]!=rec.quote_count or abs((c[2]-c[1])/2000-float(rec.range_usd))>1e-5:
            mismatches.append({'bucket':e,'source':(int(rec.quote_count),float(rec.range_usd)),'actual':(c[0],(c[2]-c[1])/2000)})
    missing=[x for x in complete if x not in set(saved.bucket_end_ms)]
    result={'original_data_quote_sha256':sha,'real_quotes':count,'source_completed_buckets':len(saved),
    'recomputed_completed_buckets':len(complete),'exact_range_and_quote_count_mismatches':len(mismatches),
    'unmatched_new_buckets':len(missing),'first_mismatch':mismatches[:3],
    'classification':'FEB041_ORIGINAL_QUOTE_RANGE_FEATURE_RECON_ONLY_NOT_PORTFOLIO_ECONOMICS'}
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    assert not mismatches and not missing,result
    return result

if __name__=='__main__': print(json.dumps(run(),indent=2))
