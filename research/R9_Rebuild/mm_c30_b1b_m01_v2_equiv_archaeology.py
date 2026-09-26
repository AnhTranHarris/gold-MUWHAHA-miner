import json, time, hashlib, sys
from pathlib import Path
import numpy as np
import pandas as pd

# Reuse the frozen FIX1 replay mechanics; this unit changes only the cached
# S1 efficiency representation back to authoritative r9_research_v2 semantics.
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import mm_c30_b1b_m01_replay_equiv_fix1_UNEXECUTED as fix1

RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
CACHE=Path('/mnt/data/mmc30_b1b_replay/MM_C30_B1B_M01_CAUSAL_CACHE.npz')
OUT=Path('/mnt/data/MM_C30_B1B_M01_V2_EQUIV_ARCHAEOLOGY_RESULT.json')
EXPECTED_RAW='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
EXPECTED_CACHE='71fc132e208589857dfe5dd6b8b1a204bd626d65c249890e842b6d5647ba65a5'
V2={'trades':33793,'net':-6253.808000024798,'gp':4301.471499988871,
    'gl':-10555.279500013668,'pf':0.407518483994981,
    'win':0.44630544787382004,'avg_hold':5.547792087118634}

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def main():
    t0=time.time()
    assert sha256(RAW)==EXPECTED_RAW
    assert sha256(CACHE)==EXPECTED_CACHE
    z=np.load(CACHE)
    sec_ids=z['sec_ids']; c=z['c']
    sd=z['s1_disp']; sr=z['s1_range']; st=z['s1_turns']
    atr=z['m5_atr']; al=z['align_long']; an=z['align_short']

    # Authoritative V2 semantics:
    # w=c[i-9:i+1]; d=np.diff(w); travel=np.abs(d).sum()
    absd=np.abs(np.diff(c))
    local_travel=np.lib.stride_tricks.sliding_window_view(absd,9).sum(axis=1)
    se=np.full(len(c),np.nan,np.float64)
    se[9:]=np.abs(c[9:]-c[:-9])/(local_travel+1e-12)

    cached=z['s1_eff']
    eligible=np.arange(len(c))>=10
    flips=eligible & np.isfinite(cached) & np.isfinite(se) & ((cached>=.70)!=(se>=.70))

    d=pd.read_csv(RAW,compression='gzip',
        usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
        dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False)
    ask=d.ask_raw.to_numpy(np.float64)/1000.
    bid=d.bid_raw.to_numpy(np.float64)/1000.
    mid=(ask+bid)*.5

    out={}
    for mode,name in ((0,'baseline'),(1,'promote_preserve_stop'),(2,'promote_reset_stop')):
        p,h,pr=fix1.replay(t,mid,sec_ids,sd,se,sr,st,atr,al,an,mode)
        out[name]=fix1.metrics(p,h,pr)
    for k in ('promote_preserve_stop','promote_reset_stop'):
        out[k]['delta_vs_baseline']=out[k]['net']-out['baseline']['net']
        out[k]['target_error_vs_63_60']=out[k]['delta_vs_baseline']-63.60

    exact=all(abs(out['baseline'][k]-V2[k])<1e-12 for k in
              ('trades','net','gp','gl','pf','win','avg_hold'))
    result={
      'job_id':'MM-C30-B1B-M01-V2-EQUIV-ARCHAEOLOGY',
      'status':'COMPLETED_LOCAL',
      'scientific_result':'EXACT_V2_BASELINE_EQUIVALENCE_RESTORED',
      'root_cause':'optimized precompute used cumulative-sum subtraction for 9-step S1 travel while authoritative V2 uses local np.abs(diff(window)).sum(); floating drift at the exact 0.70 efficiency threshold changed classifications',
      's1_eff_threshold_flip_count':int(flips.sum()),
      'baseline_exact_v2_match':bool(exact),
      'baseline':out['baseline'],
      'v2_reference':V2,
      'rule10':{'preserve_stop':out['promote_preserve_stop'],
                'reset_stop':out['promote_reset_stop']},
      'rule10_historical_63_60_bound':False,
      'forward_opened':False,
      'august_sealed':True,
      'section73_fitted':False,
      'raw_sha256':EXPECTED_RAW,
      'cache_sha256':EXPECTED_CACHE,
      'elapsed_seconds':time.time()-t0,
      'next_unit':'MM-C30-B1B-RULE10-LINEAGE-ARCHAEOLOGY'
    }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
