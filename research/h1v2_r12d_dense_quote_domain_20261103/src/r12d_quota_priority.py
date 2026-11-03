"""R12D-Q: exact-source, quota-priority repair for dense as-observed H1V2 hindsight.

Research-only: all accepted entries are FUTURE-LABELED, not predictions.
Every new entry is an original-compatible first15 favorable + full30 no-adverse
quote from separately regenerated dense event labels; it exits at first future
observed executable +$0.10 nominal net quote. Only one position exists at once.

Surgery is additive and reversible. Original R12, R12D dense labels/traces and
R11/S1/S4 evidence are NEVER overwritten. Any quota degradation or ambiguous
source check aborts instead of silently manufacturing volume.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,json
from collections import Counter
from pathlib import Path
import numpy as np
from r12_tp_oracle import read_raw,earliest_finish_schedule,write_csv,sha,quarter_key,hour_key

ROOT=Path('/mnt/data/h1v2_r12/results'); MS15=900_000
VARIANT='ALL_DISTINCT_MS_OBSERVED'

def _quarter_ms(s: str) -> int:
    return int(dt.datetime.strptime(s,'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=dt.timezone.utc).timestamp()*1000)

def _read_csv(path:Path)->list[dict]:
    with path.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def _verify_orig_trace(trace:list[dict], rawt,rawb,rawa):
    if not trace:raise ValueError('empty original source trace')
    starts=np.asarray([int(r['entry_utc_ms']) for r in trace],dtype=np.int64)
    ends=np.asarray([int(r['exit_utc_ms']) for r in trace],dtype=np.int64)
    ei=np.asarray([int(r['entry_tick_ordinal']) for r in trace],dtype=np.int64)
    xi=np.asarray([int(r['exit_tick_ordinal']) for r in trace],dtype=np.int64)
    side=np.asarray([int(r['side']) for r in trace],dtype=np.int64)
    net=np.asarray([int(r['source_nominal_net_after_fee_raw']) for r in trace],dtype=np.int64)
    assert np.all(ends>starts) and np.all(starts[1:]>ends[:-1])
    assert np.all((ei>=0)&(xi<len(rawt))) and np.all(xi>ei)
    assert np.array_equal(rawt[ei],starts) and np.array_equal(rawt[xi],ends)
    assert np.array_equal(rawb[ei],np.asarray([int(r['entry_bid_raw']) for r in trace]))
    assert np.array_equal(rawa[ei],np.asarray([int(r['entry_ask_raw']) for r in trace]))
    liq=np.where(side==1,rawb[xi],rawa[xi]).astype(np.int64)
    ent=np.where(side==1,rawa[ei],rawb[ei]).astype(np.int64)
    assert np.array_equal((liq-ent)*side-20,net) and np.all(net>=100)
    assert all(x['S1_good15_safe30_verified_from_complete_source_quotes']=='True' for x in trace)


def _load_dense(mon):
    path=ROOT/f'R12D_{mon}_ALL_OBSERVED_INTRA250MS_EXACT_H15_H30_LABELS.npz'
    receipt=json.loads((ROOT/f'R12D_{mon}_FULL_COMPLETE_DENSE_REQUOTE_ORACLE_RECEIPT.json').read_text())
    assert sha(path)==receipt['full_source_member_sha256'][path.name]
    with np.load(path,allow_pickle=False) as z:
        allix=z['raw_candidate_tick_ordinal'].copy(); times=z['entry_UTC_ms'].copy()
        gb=z['strict_good15_safe30_BUY'].copy();gs=z['strict_good15_safe30_SELL'].copy()
        good=z['strict_good_row_index_in_all_candidates'].copy(); xix=z['strict_good_firstTP_exit_tick_ordinal'].copy()
        xt=z['strict_good_firstTP_exit_utc_ms'].copy(); flags=z['asof_candidate_clocks_flag'].copy()
    assert np.array_equal(np.flatnonzero(gb|gs),good),('STRICT_GOOD_INDICES_MISMATCH',mon)
    assert not np.any(gb&gs)
    assert np.all(times[good]<xt) and np.all(xt<=times[good]+15000)
    assert len(good)==receipt['all_observed_good15_safe30_count']
    return {'allix':allix,'times':times,'gB':gb,'gS':gs,'good':good,'xix':xix,'xt':xt,'flags':flags,'receipt':receipt}


def _local_entries(d,rt,b,a,indices,mon,variant):
    raw_idx=d['allix'][d['good'][indices]]
    side=np.where(d['gB'][d['good'][indices]],1,-1).astype(np.int8)
    xt=d['xt'][indices]; xi=d['xix'][indices];t=d['times'][d['good'][indices]]
    liq=np.where(side==1,b[xi],a[xi]).astype(np.int64)
    entry=np.where(side==1,a[raw_idx],b[raw_idx]).astype(np.int64)
    net=(liq-entry)*side.astype(np.int64)-20
    assert np.all(net>=100) and np.array_equal(rt[raw_idx],t) and np.array_equal(rt[xi],xt)
    rows=[]
    for k in range(len(t)):
        rows.append({'month':'2026-'+mon,'variant':variant,'entry_utc_ms':str(int(t[k])),
          'entry_tick_ordinal':str(int(raw_idx[k])),'exit_utc_ms':str(int(xt[k])),
          'exit_tick_ordinal':str(int(xi[k])),'entry_UTC_quarter':quarter_key(t[k]),
          'entry_UTC_hour':hour_key(t[k]),'side':str(int(side[k])),
          'entry_bid_raw':str(int(b[raw_idx[k]])),'entry_ask_raw':str(int(a[raw_idx[k]])),
          'exit_liquidation_raw':str(int(liq[k])),
          'source_nominal_net_after_fee_raw':str(int(net[k])),
          'hold_ms':str(int(xt[k]-t[k])),
          'ASOF_event_clock_bit_flags':str(int(d['flags'][d['good'][indices[k]]])),
          'S1_good15_safe30_verified_from_complete_source_quotes':'True',
          'future_selected_not_causal':'True'})
    return rows


def repair(mon:str,variant:str=VARIANT):
    src=ROOT/f'R12D_{mon}_{variant}_FULL_SELECTED_QUOTE_TRACES.csv'
    orig=_read_csv(src)
    d=_load_dense(mon);rt,b,a=read_raw(mon)
    assert d['receipt']['original_first250_exact_source_ordinal_AND_both_sides_S1_label_parity']
    _verify_orig_trace(orig,rt,b,a)
    qpath=ROOT/f'R12D_{mon}_FULL_DENSE_THREE_ASOF_CLOCK_15MIN_MATRIX.csv'
    qrows=[row for row in _read_csv(qpath) if row['variant']==variant]
    assert len(qrows) in (2688,2880,2976)
    assert sum(int(r['r9_SYNTH_original_entry_ref']) for r in qrows)=={'01':27980,'02':33523,'06':31758,'07':24324}[mon]
    now=orig;repairs=[];initial_sha=sha(src)
    missing=[r for r in qrows if int(r['r9_SYNTH_original_entry_ref'])>int(r['hindsight_firstTP_selected']) and int(r['r9_SYNTH_original_entry_ref'])<=int(r['quarter_isolated_optimistic_upper'])]
    # All missing-but-independently-feasible quarter witnesses must be explicitly handled.
    for row in missing:
        target=row['utc_quarter'];q0=_quarter_ms(target);q1=q0+MS15;ref=int(row['r9_SYNTH_original_entry_ref'])
        before=[r for r in now if int(r['entry_utc_ms'])<q0]
        old=[r for r in now if q0<=int(r['entry_utc_ms'])<q1]
        after=[r for r in now if int(r['entry_utc_ms'])>=q1]
        if not before or not after:raise RuntimeError('MISSING_BOUNDARY_GUARD '+target)
        times=d['times'][d['good']]; ends=d['xt']
        eligible=np.flatnonzero((times>=q0)&(times<q1))
        assert len(eligible)==int(row['s1_ORIGINAL_SAFE30_FAV15_QUOTE_EVENT_CANDIDATE_COUNT'])
        best=None
        # One prior quarter surplus interval can be surrendered; never silently
        # delete a reference-satisfying position of an adjacent quarter.
        for remove in (0,1,2):
            if remove>len(before):break
            kept=before[:len(before)-remove]
            oldprev=before[len(before)-remove:]
            if remove and any(x['entry_UTC_quarter']!=oldprev[0]['entry_UTC_quarter'] for x in oldprev):continue
            if remove:
                qr=oldprev[0]['entry_UTC_quarter'];qref=next((int(x['r9_SYNTH_original_entry_ref']) for x in qrows if x['utc_quarter']==qr),None)
                if qref is None or sum(x['entry_UTC_quarter']==qr for x in kept)<qref:continue
            prior=int(kept[-1]['exit_utc_ms']) if kept else -2**62
            following=int(after[0]['entry_utc_ms'])
            elig=eligible[(times[eligible]>prior)&(ends[eligible]<following)]
            if len(elig)==0:continue
            vals=earliest_finish_schedule(times[elig],ends[elig]); local=elig[vals]
            if len(local)<ref:continue
            new=_local_entries(d,rt,b,a,local,mon,variant)
            updated=kept+new+after
            # Prevent count loss; every existing completed feasible quarter stays satisfied.
            if len(updated)<len(now):continue
            curr=Counter(r['entry_UTC_quarter'] for r in now)
            cand=Counter(r['entry_UTC_quarter'] for r in updated)
            if any(curr[z]>=int(x['r9_SYNTH_original_entry_ref']) and cand[z]<int(x['r9_SYNTH_original_entry_ref']) for x in qrows for z in [x['utc_quarter']]):continue
            _verify_orig_trace(updated,rt,b,a)
            best=(updated,{'quarter':target,'quarter_reference':ref,'old_quarter_entries':len(old),
               'new_quarter_entries':len(new),'removed_prior_quarter_trades':remove,
               'total_before':len(now),'total_after':len(updated),'original_candidate_count':len(eligible),
               'new_local_first_entry':new[0]['entry_utc_ms'],'new_local_last_exit':new[-1]['exit_utc_ms']})
            break
        if best is None:raise RuntimeError('FEASIBLE_QUARTER_NOT_REPAIRED '+target)
        now,receipt=best;repairs.append(receipt)
    _verify_orig_trace(now,rt,b,a)
    counts=Counter(r['entry_UTC_quarter'] for r in now)
    outrows=[];impossible=[]
    for r in qrows:
        quota=int(r['r9_SYNTH_original_entry_ref']);chosen=counts[r['utc_quarter']]
        upper=int(r['quarter_isolated_optimistic_upper']);
        rec={**r,'R12DQ_QUOTA_PRIORITY_SELECTED':chosen,
             'R12DQ_QUARTER_REFERENCE_MET':int(chosen>=quota) if quota else '',
             'R12DQ_PROVEN_ISOLATED_IMPOSSIBLE':int(upper<quota) if quota else '',
             'R12DQ_FEASIBLE_BUT_UNMET':int(chosen<quota and upper>=quota) if quota else ''}
        outrows.append(rec)
        if quota>chosen:impossible.append(rec)
    assert all(int(x['R12DQ_PROVEN_ISOLATED_IMPOSSIBLE'])==1 for x in impossible)
    met=sum(int(x['R12DQ_QUARTER_REFERENCE_MET']) for x in outrows if x['R12DQ_QUARTER_REFERENCE_MET']!='')
    assert met+len(impossible)==sum(int(x['r9_SYNTH_original_entry_ref'])>0 for x in qrows)
    p=ROOT/f'R12DQ_{mon}_{variant}_QUOTA_PRIORITY_FULL_SOURCE_TP_TRACE.csv'
    q=ROOT/f'R12DQ_{mon}_{variant}_ALL_SOURCE_15MIN_QUOTAS.csv'
    w=ROOT/f'R12DQ_{mon}_{variant}_ALL_SOURCE_PROVEN_INFEASIBLE_15MIN.csv'
    write_csv(p,now,list(now[0]));write_csv(q,outrows,list(outrows[0]));write_csv(w,impossible,list(outrows[0]))
    receipt={'classification':'SOURCE_EXACT_FUTURE_PRIVILEGED_HINDSIGHT_ONLY_NO_PROSPECTIVE_CLAIM',
             'month':mon,'candidate_variant':variant,'original_R12D_trace_SHA256':initial_sha,
             'original_complete_dense_label_NPZ_SHA256':sha(ROOT/f'R12D_{mon}_ALL_OBSERVED_INTRA250MS_EXACT_H15_H30_LABELS.npz'),
             'parent_git_branch':'carson/h1v2-r12-adaptive-tp-hour-quarter-oracle-20261103',
             'original_month_trade_count':len(orig),'repaired_month_trade_count':len(now),
             'old_quarters_achieved':sum(int(r['reaches_original_quarter_reference']) for r in qrows if r['reaches_original_quarter_reference']!=''),
             'repaired_quarters_achieved':met,'strict_source_proven_isolated_impossible_remaining':len(impossible),
             'feasible_quarters_still_unmet':0,'quota_priority_changes':repairs,
             'original_trade_SOURCE_COMPLETE_QUOTE_ORDINAL_PRICE_PARITY_VERIFIED':True,
             'repaired_one_open_position_no_overlap_SOURCE_VERIFIED':True,
             'each_repaired_entry_favored15_and_no_adverse_FULL30':True,
             'each_selected_exit_source_quoted_net_after_fee_at_least_0p10':True,
             'not_a_causal_model':True,'not_a_broker_filled_or_economically_certified_model':True,
             'sha256_outputs':{f.name:sha(f) for f in (p,q,w)}}
    result=ROOT/f'R12DQ_{mon}_{variant}_COMPLETE_SCIENTIFIC_RECEIPT.json'
    result.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt,indent=2))
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--month',choices=['01','02','06','07'],required=True)
    ap.add_argument('--variant',choices=['ALL_DISTINCT_MS_OBSERVED','FIRST50_OBSERVED','INTRABIN_SPREAD_NARROW'],default=VARIANT)
    args=ap.parse_args();repair(args.month,args.variant)
