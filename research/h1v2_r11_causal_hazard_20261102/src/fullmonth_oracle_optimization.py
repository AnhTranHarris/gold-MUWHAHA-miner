"""R11 source-exact, whole-month FUTURE-PRIVILEGED hindsight entry optimization.

The oracle is deliberately omniscient. These experiments train/optimize a
hindsight teacher's selected interval schedule, never a predictive student.
Each original quote ordinal and all source H1V2 teacher labels remain frozen.
Explicit experiment names are immutable; no post-hoc quota tuning.
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, time
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from numba import njit
from h1v2_teacher import read_ticks, schedule_oracle
from entry_contract import PINNED, MONTHS, SYNTH, candidate_legacy, candidate_v5, verify_file_sha

@dataclass(frozen=True)
class Experiment:
    id: str
    objective: str  # MAX_COUNT or MAX_NET
    first_ms_max: int = 30000
    net_min: float = 0.
    spread_max: float = 1.5
    extra_cost: float = 0.

EXPERIMENTS = (
    Experiment('V5_BASE_30SEC_COUNT','MAX_COUNT'),
    Experiment('V5_FIRST15SEC_COUNT','MAX_COUNT',first_ms_max=15000),
    Experiment('V5_FIRST5SEC_COUNT','MAX_COUNT',first_ms_max=5000),
    Experiment('V5_FIRST3SEC_NET10_SP100_COUNT','MAX_COUNT',first_ms_max=3000,net_min=.10,spread_max=1.0),
    Experiment('V5_FIRST5SEC_NET20_SP100_COUNT','MAX_COUNT',first_ms_max=5000,net_min=.20,spread_max=1.0),
    Experiment('V5_NET25_COUNT','MAX_COUNT',net_min=.25),
    Experiment('V5_NET50_COUNT','MAX_COUNT',net_min=.50),
    Experiment('V5_BASE_NET_MAX','MAX_NET'),
    Experiment('V5_FIRST15SEC_NET_MAX','MAX_NET',first_ms_max=15000),
    Experiment('V5_COST_PLUS_005_MAX_NET','MAX_NET',extra_cost=.05),
    Experiment('V5_COST_PLUS_010_MAX_NET','MAX_NET',extra_cost=.10),
)

@njit(cache=True)
def _dp(entries, next_rows, accepted, money, objective):
    n = len(entries)
    score = np.zeros(n+1, dtype=np.float64)
    num = np.zeros(n+1, dtype=np.int32)
    take = np.full(n, -1, dtype=np.int8)
    for i in range(n-1,-1,-1):
        best_v = score[i+1]
        best_n = num[i+1]
        best_s = -1
        for side in range(2):
            if not accepted[i,side]:
                continue
            nxt = next_rows[i,side]
            if nxt <= i or nxt>n:
                raise ValueError('invalid nonoverlap successor')
            reward = money[i,side]
            k = num[nxt]+1
            p = score[nxt]+reward
            if objective==0:
                better = (k>best_n) or (k==best_n and p>best_v+1e-9)
            else:
                better = (p>best_v+1e-9) or (abs(p-best_v)<=1e-9 and k>best_n)
            if better:
                best_v=p
                best_n=k
                best_s=side
        score[i]=best_v;num[i]=best_n;take[i]=best_s
    row = np.empty(num[0],np.int64)
    sides = np.empty(num[0],np.int8)
    cursor=0;i=0
    while i<n:
        s=take[i]
        if s<0:
            i+=1
        else:
            row[cursor]=i;sides[cursor]=s;cursor+=1
            i=next_rows[i,s]
    if cursor!=num[0]:raise ValueError('DP traceback mismatch')
    return row,sides,score[0]


def choose(entries, codes, net, exits, first_ms, spread, spec):
    """Future-privileged teacher DP only; an action at timestamp cannot see net."""
    entries=np.asarray(entries,np.int64)
    n=len(entries)
    if any(z.shape!=(n,2) for z in (codes,net,exits,first_ms)) or spread.shape!=(n,):
        raise ValueError('source label shapes')
    if n>1 and np.any(np.diff(entries)<=0):raise ValueError('source ordinals unsorted')
    if spec.objective not in ('MAX_COUNT','MAX_NET') or spec.extra_cost<0 or spec.spread_max<0:
        raise ValueError('invalid fixed oracle experiment')
    reward=net.astype(np.float64)-spec.extra_cost
    enough= (codes==1)&np.isfinite(reward)&(reward>0)&(reward>=spec.net_min-1e-8)&(first_ms>=0)&(first_ms<=spec.first_ms_max)&(exits>entries[:,None])&(spread[:,None]<=spec.spread_max+1e-8)
    successor=np.searchsorted(entries,exits,side='right').astype(np.int64)
    selected,dirs,total=_dp(entries,successor,enough,reward,0 if spec.objective=='MAX_COUNT' else 1)
    if len(selected):
        si=dirs.astype(np.int64)
        assert np.all(enough[selected,si])
        if len(selected)>1:assert np.all(entries[selected[1:]]>exits[selected[:-1],si[:-1]])
        assert np.all(reward[selected,si]>0)
    return selected,dirs,total, enough


def _distribution(x):
    a=np.asarray(x)
    return {'n':int(len(a)),'min':float(a.min()) if len(a) else None,
            'p05':float(np.quantile(a,.05)) if len(a) else None,
            'p25':float(np.quantile(a,.25)) if len(a) else None,
            'p50':float(np.median(a)) if len(a) else None,
            'p75':float(np.quantile(a,.75)) if len(a) else None,
            'p95':float(np.quantile(a,.95)) if len(a) else None,
            'max':float(a.max()) if len(a) else None}


def detailed_calendar(t_entry,tm_exit,sides,first_ms,model_net,entry_spread):
    dates=pd.to_datetime(t_entry,unit='ms',utc=True)
    frame=pd.DataFrame({'utc_day':dates.strftime('%Y-%m-%d'),
        'iso_week':dates.strftime('%G-W%V'),
        'side':sides,'first_ms':first_ms,'net':model_net,'spread':entry_spread,
        'duration_ms':tm_exit-t_entry})
    out={}
    for dim in ('utc_day','iso_week'):
        cells=[]
        for label,grp in frame.groupby(dim,sort=True):
            v=grp.net.to_numpy()
            cells.append({'period':str(label),'positions':len(grp),'BUY':int((grp.side==1).sum()),
                'SELL':int((grp.side==-1).sum()),'strict_first15_seconds':int((grp.first_ms<=15000).sum()),
                'strict_first15_rate':float((grp.first_ms<=15000).mean()),
                'strict_first5_seconds':int((grp.first_ms<=5000).sum()),
                'strict_first5_rate':float((grp.first_ms<=5000).mean()),
                'strict_first30_rate':1.,'modeled_net_after_spec_cost':round(float(v.sum()),5),
                'first_ms_distribution':_distribution(grp.first_ms.to_numpy()),
                'net_distribution':_distribution(v),'spread_distribution':_distribution(grp.spread.to_numpy()),
                'duration_ms_distribution':_distribution(grp.duration_ms.to_numpy())})
        out[dim] = cells
    return out


def run_month(mon,raw_dir,teacher_dir,out_dir,*,experiments=EXPERIMENTS):
    if mon not in MONTHS:raise ValueError(mon)
    clock=time.monotonic();src=pathlib.Path(raw_dir)/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
    labels=pathlib.Path(teacher_dir)/f'h1v2_dukascopy_{mon}_oracle_labels.npz'
    original=json.loads((pathlib.Path(teacher_dir)/f'h1v2_dukascopy_{mon}_receipt.json').read_text())
    verify_file_sha(src,PINNED[mon]);verify_file_sha(labels,original['teacher_labels_sha256'])
    t,b,a=read_ticks(src)
    out=pathlib.Path(out_dir)/f'month_{mon}';out.mkdir(parents=True,exist_ok=True)
    with np.load(labels,allow_pickle=False) as z:
        ix=z['tick_index'].copy()
        if not np.array_equal(t[ix],z['t']):raise ValueError('original quote timestamp join mismatch')
        candidate_original=candidate_legacy(t,b,a)
        if not np.array_equal(candidate_original,ix):raise ValueError('original teacher candidate parity mismatch')
        v5=candidate_v5(t,b,a)
        pres=np.isin(ix,v5,assume_unique=True)
        if not np.array_equal(v5,ix[pres]):raise ValueError('new v5 candidate not a subset')
        e=ix[pres]; c=z['code'][pres].copy();net=z['net'][pres].copy()
        first=z['first_event_ms'][pres].copy();exits=z['exit_tick_index'][pres].copy()
    spread=(a[e]-b[e]).astype(np.float32)
    details={'month':mon,'raw_source_sha256':PINNED[mon],
             'original_teacher_labels_sha256':original['teacher_labels_sha256'],
             'source_original_candidates':len(ix),'source_r11_v5_gap_candidates':len(e),
             'exclusion_candidates':int((~pres).sum()),
             'source_r11_v5_good_candidates':int((c==1).any(axis=1).sum()),
             'source_r11_v5_good_BUY':int((c[:,0]==1).sum()),'source_r11_v5_good_SELL':int((c[:,1]==1).sum()),
             'source_r11_v5_wrong_BUY':int((c[:,0]==-1).sum()),'source_r11_v5_wrong_SELL':int((c[:,1]==-1).sum()),
             'source_r11_v5_neutral_BUY':int((c[:,0]==0).sum()),'source_r11_v5_neutral_SELL':int((c[:,1]==0).sum()),
             'source_r11_v5_censored_BUY':int((exits[:,0]<0).sum()),
             'source_r11_v5_censored_SELL':int((exits[:,1]<0).sum()),
             'source_r9_synth_month_count':SYNTH[mon],
             'owner_v2_85pct_reference_floor':math.ceil(.85*SYNTH[mon]),
             'original_source_hindsight_winners':original['oracle_nonoverlapping'],
             'run_mode':'FULL_SOURCE_MONTH_NONOVERLAP_FUTURE_PRIVILEGED_HINDSIGHT_ONLY',
             'experiment_ids':[x.id for x in experiments],
             'experiments':{}}
    for spec in experiments:
        t0=time.monotonic();rows,directions,objective,elig=choose(e,c,net,exits,first,spread,spec)
        s=directions.astype(np.int64);position_entry=e[rows]
        position_exit=exits[rows,s]
        n=float(len(rows));netpay=net[rows,s].astype(np.float64)-spec.extra_cost
        selection_trace=out/f'{spec.id}_SELECTED_FULL_SOURCE_TRACE.npz'
        np.savez_compressed(selection_trace,
            source_eligible_row=rows,source_raw_entry_tick=position_entry,
            source_raw_exit_tick=position_exit,entry_utc_ms=t[position_entry],
            exit_utc_ms=t[position_exit],side=np.where(s==0,1,-1).astype(np.int8),
            first_favorable_elapsed_ms=first[rows,s],original_r9_net=net[rows,s],
            research_incremental_cost=np.full(len(rows),spec.extra_cost,np.float32),
            research_net_after_incremental_cost=netpay.astype(np.float32),entry_spread=spread[rows])
        with selection_trace.open('rb') as fh:hash_trace=hashlib.file_digest(fh,'sha256').hexdigest()
        cal=detailed_calendar(t[position_entry],t[position_exit],np.where(s==0,1,-1),first[rows,s],netpay,spread[rows]) if len(rows) else {'utc_day':[],'iso_week':[]}
        for dim,cells in cal.items():
            (out/f'{spec.id}_COMPLETE_{dim.upper()}_UTC.json').write_text(json.dumps({'source_month':mon,'experiment_id':spec.id,'period_dimension':dim,'cells':cells},indent=2))
        receipt={**asdict(spec),
            'eligible_candidate_side_actions':int(elig.sum()),
            'eligible_candidate_unique_timestamps':int(elig.any(axis=1).sum()),
            'strict_known_successful_selected':int(len(rows)),
            'nonoverlap_verified':True,
            'simulated_research_net_after_incremental_cost':round(float(netpay.sum()),5),
            'simulated_research_source_r9_net':round(float(net[rows,s].astype(np.float64).sum()),5),
            'priority_objective_dp_score':round(float(objective),5),
            'positive_source_net_rate':float((netpay>0).mean()) if len(rows) else None,
            'first15s_strict_rate':float((first[rows,s]<=15000).mean()) if len(rows) else None,
            'first5s_strict_rate':float((first[rows,s]<=5000).mean()) if len(rows) else None,
            'first3s_strict_rate':float((first[rows,s]<=3000).mean()) if len(rows) else None,
            'selected_BUY':int((s==0).sum()),'selected_SELL':int((s==1).sum()),
            'reference_month_count_85pct':math.ceil(.85*SYNTH[mon]),
            'reference_month_volume_floor_pass':len(rows)>=math.ceil(.85*SYNTH[mon]),
            'reference_first15s_80pct_pass':bool(len(rows) and (first[rows,s]<=15000).mean()>=.8),
            'strict_original_positive_r9_label_rate':1. if len(rows) else None,
            'median_first_favorable_ms':float(np.median(first[rows,s])) if len(rows) else None,
            'median_net_after_incremental_cost':float(np.median(netpay)) if len(rows) else None,
            'all_positions_trace':selection_trace.name,
            'all_positions_trace_sha256':hash_trace,
            'full_daily_record':f'{spec.id}_COMPLETE_UTC_DAY_UTC.json',
            'full_weekly_record':f'{spec.id}_COMPLETE_ISO_WEEK_UTC.json',
            'elapsed_run_s':round(time.monotonic()-t0,2),
            'scientific_boundary':'100percent strict only because future oracle selected already-known winners; not a trained forecasting policy; cost stress is posthoc net adjustment not a recalc of latency-sensitive stop paths'}
        details['experiments'][spec.id]=receipt
        (out/f'{spec.id}_COMPLETE_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
        print(mon,spec.id,'selected',len(rows),'modeled_net',receipt['simulated_research_net_after_incremental_cost'],'first15',receipt['first15s_strict_rate'],'s',receipt['elapsed_run_s'],flush=True)
    base=details['experiments']['V5_BASE_30SEC_COUNT'] if 'V5_BASE_30SEC_COUNT' in details['experiments'] else None
    if base:
        expected={'01':137164,'02':124439,'06':148958,'07':100559}[mon]
        if base['strict_known_successful_selected']!=expected:raise ValueError('original R11 v5 DP not source exact')
    details['elapsed_total_s']=round(time.monotonic()-clock,2)
    details['status']='FOUR_MONTH_FULL_SOURCE_MONTH_HINDSIGHT_RESEARCH_NOT_PREDICTIVE_TRAINING'
    (out/f'R11_FULL_MONTH_EXPERIMENT_STAGE_{experiments[0].id}_{mon}.json').write_text(json.dumps(details,indent=2))
    return details

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--month',choices=MONTHS,required=True)
    ap.add_argument('--raw-dir',default='/mnt/data')
    ap.add_argument('--teacher-dir',default='/mnt/data/h1v2_r11_lab/rebuilt_teacher')
    ap.add_argument('--out-dir',default='/mnt/data/h1v2_r11_lab/optimization')
    ap.add_argument('--ids',default=None,help='comma-separated frozen experiment ids; execute a finite stage without changing the pre-registered grid')
    args=ap.parse_args()
    specs=EXPERIMENTS if args.ids is None else tuple(x for x in EXPERIMENTS if x.id in args.ids.split(','))
    if not specs or (args.ids and len(specs)!=len(set(args.ids.split(',')))):raise ValueError('unknown/duplicate experiment ID')
    r=run_month(args.month,args.raw_dir,args.teacher_dir,args.out_dir,experiments=specs)
    print(json.dumps({'month':args.month,'elapsed_s':r['elapsed_total_s'],'total_experiments':len(r['experiments'])},indent=2),flush=True)
