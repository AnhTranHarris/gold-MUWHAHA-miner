"""H1V2 R11-S1: exact 15s/30s fixed-horizon, future-privileged survival oracle.

NO prospective ability is claimed. Entry is judged without calling R9 stop,
trail or exit; this deliberately uses all FUTURE quotes until each horizon.
Price arithmetic is Dukascopy source 0.001-XAUUSD integer tick geometry.
Per-side/entry zero adverse-barrier breaches must be sustained through the
entire horizon; an earlier favorable touch DOES NOT end surveillance.

Original R11 positive-first-passage experiments and R9 original exits remain
unmodified archival controls. This is an additive, distinct survivability label.
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, time
import numpy as np
import pandas as pd
from numba import njit
from entry_contract import PINNED, MONTHS, SYNTH, candidate_v5, candidate_legacy, verify_file_sha

ROOT = pathlib.Path('/mnt/data/h1v2_r11_lab')
FAV_RAW=120 # +$0.10 net including original research $0.02 fee, from entry ASK/BID
BAD_RAW=100 # -$0.10 relative to executable liquidation quote at entry
MAX_GAP_MS=15000 # stale quote-window gap >15s is censored, NOT winning
HORIZONS_MS=(15000,30000)

@njit(cache=True)
def _rolling_extrema(t,b,a,ix,horizon,max_gap_ms=MAX_GAP_MS):
    """4 one-sided monotone raw-ordinal sliding extrema; each quote O(1) amortized.

    The lookup window is timestamps STRICTLY GREATER than entry timestamp and
    <= entry+H. Later quote ordinals with equal entry millisecond are excluded.
    A horizon is 'observed' only when source extends to end, at least one quote
    after entry, no observed interquote jump >max_gap and no unobserved expiry
    staleness > max_gap. This is source observation, not guaranteed broker fill.
    """
    n=len(t);m=len(ix)
    # Storage O(n), work O(n+m), no sparse table, complete 15s/30s source.
    qminb=np.empty(n,np.int32);qmaxb=np.empty(n,np.int32)
    qmina=np.empty(n,np.int32);qmaxa=np.empty(n,np.int32)
    hb=tb=HB=TB=ha=ta=HA=TA=0
    right=0;left=0
    pref=np.zeros(n,np.int32)
    for j in range(1,n):pref[j]=pref[j-1]+(1 if t[j]-t[j-1]>max_gap_ms else 0)
    mn_b=np.empty(m,np.int32);mx_b=np.empty(m,np.int32)
    mn_a=np.empty(m,np.int32);mx_a=np.empty(m,np.int32)
    count=np.empty(m,np.int32);oldest_age=np.empty(m,np.int32)
    covered=np.zeros(m,np.bool_)
    last=-1
    for k in range(m):
        i=ix[k]
        if i<=last or i<0 or i>=n:raise ValueError('invalid candidate ordinal chronology')
        last=i;now=t[i];end=now+horizon
        # Expand right-hand time boundary (<= target horizon).
        while right<n and t[right]<=end:
            v=right
            while tb>hb and b[qminb[tb-1]]>=b[v]:tb-=1
            qminb[tb]=v;tb+=1
            while TB>HB and b[qmaxb[TB-1]]<=b[v]:TB-=1
            qmaxb[TB]=v;TB+=1
            while ta>ha and a[qmina[ta-1]]>=a[v]:ta-=1
            qmina[ta]=v;ta+=1
            while TA>HA and a[qmaxa[TA-1]]<=a[v]:TA-=1
            qmaxa[TA]=v;TA+=1
            right+=1
        # Remove all quotes at or before entry timestamp (same-ms future
        # ordinal excluded by the frozen H1V2 fill convention).
        while left<n and t[left]<=now:left+=1
        while hb<tb and qminb[hb]<left:hb+=1
        while HB<TB and qmaxb[HB]<left:HB+=1
        while ha<ta and qmina[ha]<left:ha+=1
        while HA<TA and qmaxa[HA]<left:HA+=1
        qn=right-left
        count[k]=qn
        if qn>0:
            mn_b[k]=b[qminb[hb]];mx_b[k]=b[qmaxb[HB]]
            mn_a[k]=a[qmina[ha]];mx_a[k]=a[qmaxa[HA]]
        else:
            mn_b[k]=b[i];mx_b[k]=b[i];mn_a[k]=a[i];mx_a[k]=a[i]
        lastquote=t[right-1] if right>0 else now
        age=end-lastquote
        oldest_age[k]=min(2**31-1,max(0,age))
        # Use timestamp of FIRST event after horizon to verify an uncovered
        # quote gap straddling boundary. Source ending before horizon censored.
        source_complete=(t[n-1]>=end)
        inner_gap=(pref[right-1]-pref[i]>0) if right-1>i else False
        boundary_gap=(right<n and t[right]-t[right-1]>max_gap_ms and t[right-1]<end)
        covered[k]=source_complete and qn>0 and not inner_gap and not boundary_gap and age<=max_gap_ms
    return mn_b,mx_b,mn_a,mx_a,count,oldest_age,covered

@njit(cache=True)
def _dp_count_quality(entry_t, eligible, safety_margin, reservation_ms):
    n=len(entry_t)
    count=np.zeros(n+1,np.int32)
    quality=np.zeros(n+1,np.float64)
    selected=np.full(n,-1,np.int8)
    successors=np.empty(n,np.int32)
    pointer=1
    for i in range(n):
        if pointer<=i:pointer=i+1
        deadline=entry_t[i]+reservation_ms
        while pointer<n and entry_t[pointer]<=deadline:pointer+=1
        successors[i]=pointer
    for i in range(n-1,-1,-1):
        nc=count[i+1];qv=quality[i+1];side=-1
        for s in range(2):
            if not eligible[i,s]:continue
            nxt=successors[i]
            x=count[nxt]+1;v=quality[nxt]+max(0.,float(safety_margin[i,s]))
            if x>nc or (x==nc and v>qv+1e-10):
                nc=x;qv=v;side=s
        count[i]=nc;quality[i]=qv;selected[i]=side
    rows=np.empty(count[0],np.int32);sides=np.empty(count[0],np.int8)
    i=0;k=0
    while i<n:
        s=selected[i]
        if s<0:i+=1
        else:
            rows[k]=i;sides[k]=s;k+=1;i=successors[i]
    if k!=count[0]:raise ValueError('DP trace count mismatch')
    return rows,sides,quality[0]


def read_raw_int(path):
    # The original source raw columns are integer millidollars. Do NOT
    # round observed prices to $0.01; that changes the first-passage barrier.
    frame=pd.read_csv(path, usecols=['timestamp_ms_utc','bid_raw','ask_raw'],
        dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
    t=frame['timestamp_ms_utc'].to_numpy(dtype=np.int64,copy=True)
    b=frame['bid_raw'].to_numpy(dtype=np.int32,copy=True)
    a=frame['ask_raw'].to_numpy(dtype=np.int32,copy=True)
    if not len(t) or np.any(t[1:]<t[:-1]) or np.any(b>a):raise ValueError('invalid source quotes')
    return t,b,a


def _calendar(t,ix,rows,sides,good15,good30,covered15,covered30,margin,active_days):
    dates=pd.to_datetime(t[ix[rows]],unit='ms',utc=True)
    df=pd.DataFrame({'utc_day':dates.strftime('%Y-%m-%d'), 'iso_week':dates.strftime('%G-W%V'),
        'BUY':sides==0,'SELL':sides==1,
        'surv15':good15[rows,sides],'surv30':good30[rows,sides],
        'covered15':covered15[rows],'covered30':covered30[rows],
        'margin_raw':margin[rows,sides]})
    reports={}
    for key in ('utc_day','iso_week'):
        groups={k:g for k,g in df.groupby(key,sort=True)} if len(df) else {}
        labels=active_days if key=='utc_day' else sorted(set(pd.to_datetime(active_days).strftime('%G-W%V')))
        entries=[]
        for period in labels:
            if period in groups:
                g=groups[period];n=len(g)
                entries.append({'period':period,'source_active':True,'entries':n,
                  'BUY':int(g.BUY.sum()),'SELL':int(g.SELL.sum()),
                  'survived_full_15s':int(g.surv15.sum()),'survived_full_30s':int(g.surv30.sum()),
                  'survived_full_15s_rate':float(g.surv15.mean()),'survived_full_30s_rate':float(g.surv30.mean()),
                  'coverage_15s':int(g.covered15.sum()),'coverage_30s':int(g.covered30.sum()),
                  'min_safety_margin_raw':int(g.margin_raw.min()),
                  'median_safety_margin_raw':float(g.margin_raw.median())})
            else:entries.append({'period':period,'source_active':True,'entries':0,'BUY':0,'SELL':0,
                  'survived_full_15s':0,'survived_full_30s':0,'survived_full_15s_rate':None,
                  'survived_full_30s_rate':None,'coverage_15s':0,'coverage_30s':0,
                  'min_safety_margin_raw':None,'median_safety_margin_raw':None})
        reports[key]=entries
    return reports


def month(mon, raw_dir=pathlib.Path('/mnt/data'), out_dir=ROOT/'survival/months'):
    start=time.monotonic();p=pathlib.Path(raw_dir)/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
    verify_file_sha(p,PINNED[mon]);t,b,a=read_raw_int(p)
    # source-exact original/v5 candidate universe, with identical 250ms first
    # observed quote, spread and 15s history-gap reset rules.
    original=candidate_legacy(t,b.astype(np.float64)/1000.,a.astype(np.float64)/1000.)
    ix=candidate_v5(t,b.astype(np.float64)/1000.,a.astype(np.float64)/1000.)
    if len(ix) and (not np.array_equal(ix,original[np.isin(original,ix,assume_unique=True)])):
        raise ValueError('unexpected v5-only candidate ordinals')
    expected={'01':4012834,'02':3076349,'06':4173378,'07':4038891}[mon]
    if len(ix)!=expected:raise ValueError(f'candidate parity mismatch {mon}: {len(ix)} != {expected}')
    out_dir=pathlib.Path(out_dir)/f'month_{mon}';out_dir.mkdir(parents=True,exist_ok=True)
    details={'month':mon,'source_sha256':PINNED[mon], 'source_raw_ticks':len(t),
        'candidate_raw_indices':len(ix), 'horizons_ms':list(HORIZONS_MS),'max_gap_ms':MAX_GAP_MS,
        'favorable_raw_threshold':FAV_RAW,'adverse_raw_threshold':BAD_RAW,
        'fee_research_dollar_units':0.02,
        'disclaimer':'100% future-known selection is tautological hindsight, NOT an as-of learned entry policy',
        'optimizations':{}, 'month_observation':{}}
    raw_obs={}
    for h in HORIZONS_MS:
        tic=time.monotonic()
        minbid,maxbid,minask,maxask,nq,stale,covered=_rolling_extrema(t,b,a,ix,h)
        # No R9 exit dependency. Evaluate the entire fixed quote window.
        buy_margin=minbid.astype(np.int64)-(b[ix].astype(np.int64)-BAD_RAW)
        sell_margin=(a[ix].astype(np.int64)+BAD_RAW)-maxask.astype(np.int64)
        bm=buy_margin>0;sm=sell_margin>0
        buy_fav=maxbid.astype(np.int64)>=(a[ix].astype(np.int64)+FAV_RAW)
        sell_fav=minask.astype(np.int64)<=(b[ix].astype(np.int64)-FAV_RAW)
        surv=np.column_stack((bm,sm))&covered[:,None]
        fav=np.column_stack((buy_fav,sell_fav))&covered[:,None]
        good=surv&fav
        raw_obs[h]=dict(survival=surv,positive=good,coverage=covered,margin=np.column_stack((buy_margin,sell_margin)),quotes=nq,stale=stale)
        details['month_observation'][str(h)]={'covered_candidate_rows':int(covered.sum()),
           'censored_candidate_rows':int((~covered).sum()),'side_survived_no_adverse':[int(x) for x in surv.sum(axis=0)],
           'side_survived_and_favorable':[int(x) for x in good.sum(axis=0)],
           'any_side_survived_and_favorable':int(good.any(axis=1).sum()),
           'both_sides_survived_and_favorable':int(good.all(axis=1).sum()),
           'any_side_survived_without_requiring_favorable':int(surv.any(axis=1).sum()),
           'zero_quote_count':int((nq==0).sum()),'elapsed_s':round(time.monotonic()-tic,3)}
    g15=raw_obs[15000]['positive'];g30=raw_obs[30000]['positive']
    s15=raw_obs[15000]['survival'];s30=raw_obs[30000]['survival']
    c15=raw_obs[15000]['coverage'];c30=raw_obs[30000]['coverage']
    margin30=raw_obs[30000]['margin'];margin15=raw_obs[15000]['margin']
    active_numeric=np.unique(t[ix]//86400000)
    active_days=pd.to_datetime(active_numeric*86400000,unit='ms',utc=True).strftime('%Y-%m-%d').tolist()
    specs=(('SURVIVE15_FAV15_RESERVE15',g15,margin15,15000),
           ('SURVIVE30_FAV30_RESERVE30',g30,margin30,30000),
           ('SURVIVE30_FAV15_RESERVE30',g30&g15,margin30,30000),
           ('SURVIVE15_NOFAV_RESERVE15',s15,margin15,15000),
           ('SURVIVE30_NOFAV_RESERVE30',s30,margin30,30000))
    for name,eligible,margin,reserve in specs:
        tic=time.monotonic()
        rows,sides,q=_dp_count_quality(t[ix],eligible,margin,reserve)
        if len(rows)>1 and np.any(t[ix[rows[1:]]]<=t[ix[rows[:-1]]]+reserve):
            raise ValueError('position reservation overlap')
        if len(rows) and not eligible[rows,sides].all():raise ValueError('invalid future selected action')
        cal=_calendar(t,ix,rows,sides,g15,g30,c15,c30,margin,active_days)
        trace=out_dir/f'R11S_{mon}_{name}_COMPLETE_QUOTE_ORDINALS.npz'
        np.savez_compressed(trace,eligible_row=rows,entry_tick_index=ix[rows],entry_utc_ms=t[ix[rows]],
            side=np.where(sides==0,1,-1).astype(np.int8),
            full_15s_favorable_survival=g15[rows,sides],full_30s_favorable_survival=g30[rows,sides],
            full_15s_no_adverse=s15[rows,sides],full_30s_no_adverse=s30[rows,sides],
            quote_coverage_15s=c15[rows],quote_coverage_30s=c30[rows],
            safety_margin_raw=margin[rows,sides],reservation_ms=np.full(len(rows),reserve,np.int32))
        with trace.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
        for key,cells in cal.items():
            (out_dir/f'R11S_{mon}_{name}_{key.upper()}_FULL_SOURCE_ACTIVE.json').write_text(json.dumps(cells,indent=2))
        rec={'exact_hindsight_eligible_count':len(rows),
             'first15s_survive_and_favorable_rate':float(g15[rows,sides].mean()) if len(rows) else None,
             'first30s_survive_and_favorable_rate':float(g30[rows,sides].mean()) if len(rows) else None,
             'first15s_no_adverse_rate':float(s15[rows,sides].mean()) if len(rows) else None,
             'first30s_no_adverse_rate':float(s30[rows,sides].mean()) if len(rows) else None,
             'monthly_85pct_synth_floor':math.ceil(.85*SYNTH[mon]),
             'monthly_volume_floor_pass':len(rows)>=math.ceil(.85*SYNTH[mon]),
             'source_days':len(active_days),'active_days_with_zero_selected':sum(x['entries']==0 for x in cal['utc_day']),
             'active_weeks_with_zero_selected':sum(x['entries']==0 for x in cal['iso_week']),
             'days_under_80pct_15s':sum(x['entries']>0 and x['survived_full_15s_rate']<.8 for x in cal['utc_day']),
             'days_under_80pct_30s':sum(x['entries']>0 and x['survived_full_30s_rate']<.8 for x in cal['utc_day']),
             'weeks_under_80pct_15s':sum(x['entries']>0 and x['survived_full_15s_rate']<.8 for x in cal['iso_week']),
             'weeks_under_80pct_30s':sum(x['entries']>0 and x['survived_full_30s_rate']<.8 for x in cal['iso_week']),
             'trace_file':trace.name,'trace_sha256':sha,
             'full_calendar_file_names':{k:f'R11S_{mon}_{name}_{k.upper()}_FULL_SOURCE_ACTIVE.json' for k in cal},
             'selector':'FUTURE_OMNISCIENT_COUNT_THEN_MAX_SAFETY_MARGIN',
             'research_status':'HINDSIGHT_SCIENTIFIC_CAPACITY_ONLY_NOT_FORESIGHT'}
        details['optimizations'][name]=rec
        print(mon,name,'n',len(rows),'15survfav',round(rec['first15s_survive_and_favorable_rate'] or 0,4),'30survfav',round(rec['first30s_survive_and_favorable_rate'] or 0,4),'elapsed',round(time.monotonic()-tic,3),flush=True)
    details['total_elapsed_s']=round(time.monotonic()-start,3)
    (out_dir/f'R11S_{mon}_FIXED_HORIZON_ENTRY_SURVIVABILITY_COMPLETE.json').write_text(json.dumps(details,indent=2))
    return details

if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('--month',choices=MONTHS,required=True)
    a=q.parse_args();r=month(a.month)
    print(json.dumps({'month':a.month,'v5_candidates':r['candidate_raw_indices'],
        'survival_observation':r['month_observation'],
        'counts':{k:v['exact_hindsight_eligible_count'] for k,v in r['optimizations'].items()},
        'elapsed_s':r['total_elapsed_s']},indent=2),flush=True)
