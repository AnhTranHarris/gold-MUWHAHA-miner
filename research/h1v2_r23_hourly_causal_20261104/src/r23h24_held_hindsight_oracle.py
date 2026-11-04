"""Future-PRIVILEGED minimum-hold entry SURVIVABILITY opportunity ceiling.

Distinct from ORIGINAL R23 TP-at-first-passage future oracle. This NEW
conditional contract demands both first TARGET before STOP and adverse barrier
not crossed at any observed quote through full H=15/30/60 seconds. It freezes
original 1s signal -> first actual +100ms quote fill, side-dependent bid/ask,
source gaps and quote ordinal; no fabricated fills/hidden future in *causal* models.
This is a pure future-selected optimistic capacity certificate, NEVER a policy.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from numba import njit
from r23h24_competing_hazard import BASE,FEEDS,source_arrays
sys.path.insert(0,str(BASE/'r24_source_archive'/'source'))
import r24_firstpass_engine as upstream

CONTRACTS=('H15_ONLY','H30_ONLY','H60_ONLY','EARLIEST_QUALIFYING_H15_H30_H60')
QUARTER_MS=900_000
@njit(cache=False)
def greedy_intervals(order,fill,ends,group,ts,group_len):
    """Maximum count for known intervals by earliest true exit (interval scheduling)."""
    selected=np.empty(len(order),np.int32);counts=np.zeros(group_len,np.int32)
    last_end_ms=np.int64(-9223372036854775000);last_group=-1;w=0
    for ii in order:
        gg=group[ii]
        if gg<0 or gg>=group_len:continue
        if gg!=last_group:
            last_group=gg;last_end_ms=np.int64(-9223372036854775000)
        # Equal timestamps are NOT a separately executable next quote.
        if fill[ii]<0 or ts[fill[ii]]<=last_end_ms:continue
        selected[w]=ii;w+=1
        counts[gg]+=1;last_end_ms=ts[ends[ii]]
    return selected[:w],counts

def best_lanes(a,contract,ts):
    fill=np.asarray(a['f']);l=np.asarray(a['l']);held=np.asarray(a['held']);end=np.asarray(a['end_ix'])
    n=len(fill);bestend=np.full(n,len(ts),np.int32);side=np.full(n,-1,np.int8);hz=np.full(n,-1,np.int8)
    stages={'H15_ONLY':(0,), 'H30_ONLY':(1,), 'H60_ONLY':(2,), 'EARLIEST_QUALIFYING_H15_H30_H60':(0,1,2)}[contract]
    for k in stages:
        e=end[:,k];valid=(fill>=0)&(e>fill)&(e<len(ts))
        for j in (0,1):
            use=valid&(l[:,j,k]==1)&(held[:,j,k]==1)&(e<bestend)
            bestend[use]=e[use];side[use]=j;hz[use]=k
    ix=np.flatnonzero(side>=0).astype(np.int32)
    assert len(ix) and np.all(ts[bestend[ix]]>ts[fill[ix]])
    return ix,bestend[ix],side[ix],hz[ix]

def source_month(source,mon):
    a=source_arrays(source,mon);ts,_,_=upstream.raw_month(source,mon,verify=True)
    qt,qref=upstream.calendar_reference(mon)
    outdir=BASE/'oracle_held'/source/mon;outdir.mkdir(parents=True,exist_ok=True)
    allcase=[];allfiles={}
    for contract in CONTRACTS:
        ix,ends,side,hz=best_lanes(a,contract,ts);fills=np.asarray(a['f'][ix]);ft=ts[fills]
        # Full source aligned first-filled timestamp quarter ordinal. No inferred ticks.
        qgroup=np.searchsorted(qt,ft//QUARTER_MS*QUARTER_MS).astype(np.int32)
        good=(qgroup<len(qref))&(qt[np.minimum(qgroup,len(qref)-1)]==ft//QUARTER_MS*QUARTER_MS)
        if not np.all(good):raise AssertionError('QUALIFIED_ENTRY_OUTSIDE_SOURCE_MONTH')
        # Globally one-position future-first-end-optimal schedule. Non-overlap
        # includes every cross-quarter/day/hour reservation automatically.
        ordered=np.argsort(ends,kind='stable').astype(np.int32)
        global_selected,global_counts=greedy_intervals(ordered,fills,ends,np.zeros(len(fills),np.int32),ts,1)
        unique_ix=ix[global_selected];sf=fills[global_selected];se=ends[global_selected]
        assert np.all(ts[sf[1:]]>ts[se[:-1]])
        global_q=np.bincount(qgroup[global_selected],minlength=len(qref))
        # Independent local quote-capacity UPPER, not a globally possible schedule:
        # buckets reset past occupancy at their *start* to isolate source geometry.
        bounds={}
        for kind,groups,ref in (
            ('quarter',qgroup,qref),
            ('hour',qgroup//4,qref.reshape(-1,4).sum(axis=1)),
            ('day',qgroup//96,qref.reshape(-1,96).sum(axis=1))):
            order=np.lexsort((ends,groups)).astype(np.int32)
            _,cap=greedy_intervals(order,fills,ends,groups,ts,len(ref))
            chosen=global_q if kind=='quarter' else global_q.reshape(-1,4 if kind=='hour' else 96).sum(axis=1)
            if not np.all(cap>=chosen):raise AssertionError('LOCAL_UPPER_LESS_THAN_GLOBAL_COUNT')
            frame=[]
            for k in range(len(ref)):
                at=qt[k*({'quarter':1,'hour':4,'day':96}[kind])]
                frame.append({'source':source,'month':mon,'contract':contract,'utc_'+kind:datetime.fromtimestamp(int(at)/1000,timezone.utc).isoformat(),
                    'original_R9_SYNTH_exact_reference':int(ref[k]),
                    'FUTURE_KNOWN_independent_bucket_capacity_upper':int(cap[k]),
                    'FUTURE_KNOWN_global_nonoverlap_selected_count':int(chosen[k]),
                    'independent_bound_meets_R9_reference':int(cap[k]>=ref[k]) if ref[k]>0 else '',
                    'global_future_known_meets_R9_reference':int(chosen[k]>=ref[k]) if ref[k]>0 else '',
                    'candidate_universe':'ASOF_R24_ONE_SECOND_DELAYED_ACTUAL_QUOTE; BOTH_SIDE_FUTURE_LABELED',
                    'first_target_before_stop':True,'fullH_adverse_stop_survived':True,
                    'selection_mechanism':'NONCAUSAL_FUTURE_FIRST_TARGET_AND_FULL_HELD',
                    'point_in_time_news':'UNKNOWN','historical_prop_permission':'UNKNOWN'})
            p=outdir/f'{contract}_{kind.upper()}_COMPLETE.csv'
            with p.open('w',newline='',encoding='utf8') as f:
                wr=csv.DictWriter(f,fieldnames=list(frame[0]));wr.writeheader();wr.writerows(frame)
            allfiles[p.name]=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
            bounds[kind]={'calendar_buckets':len(ref),'R9_active_buckets':int((ref>0).sum()),
                'independent_buckets_meeting_reference':int(np.sum((ref>0)&(cap>=ref))),
                'global_buckets_meeting_reference':int(np.sum((ref>0)&(chosen>=ref))),
                'sum_minimum_independent_slot_deficit':int(np.maximum(ref-cap,0).sum()),
                'source_witness_failed_buckets':int(np.sum((ref>0)&(cap<ref)))}
        trace=np.column_stack((unique_ix,side[global_selected],hz[global_selected],sf,se)).astype(np.int64)
        tfile=outdir/f'{contract}_FULL_SOURCE_FUTURE_SELECTED_EXACT_QUOTE_ORDINALS.npy'
        with tfile.open('wb') as f:np.save(f,trace,allow_pickle=False)
        allfiles[tfile.name]=hashlib.file_digest(tfile.open('rb'),'sha256').hexdigest()
        rr={'source':source,'month':mon,'contract':contract,'original_R9_SYNTH_month_volume':int(qref.sum()),
            'future_known_eligible_intervals':len(ix),'global_nonoverlap_future_selected_fullH_winners':len(unique_ix),
            'full_H_quote_at_or_after_minimum_real_ordinal':True,'first_target_before_stop_AND_fullH_no_adverse':True,
            'side_and_signal_selected_with_FUTURE_KNOWN_outcomes':True,'clock':bounds}
        allcase.append(rr)
        print('ORACLE_FULLH',json.dumps(rr),flush=True)
    res={'source':source,'month':mon,'classification':'FUTURE_PRIVILEGED_UPPER_NOT_A_TRAINED_POLICY',
         'source_sha256':upstream.sha(upstream.source_file(source,mon)),
         'no_original_experiment_modified':True,'cases':allcase,'output_sha256':allfiles}
    (outdir/f'R23H24_ORACLE_FULLHELD_{source}_{mon}_ATOMIC_RECEIPT.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
    return res
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,choices=FEEDS);ap.add_argument('--month',required=True,choices=('01','02','06','07'))
    args=ap.parse_args();source_month(args.source,args.month)
