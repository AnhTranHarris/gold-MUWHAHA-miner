"""R21 additive broker-domain / original-quarter-aware hindsight interval exchange.

Original R19/S3 complete future-selected intervals remain unmodified on disk.
This study changes ONLY the post-hoc hindsight SCHEDULER of candidate first-touch
intervals; it does not predict BUY or SELL, does not execute MT5 trades, and does
not prove positive expected economics or meeting a quota on a causal policy.
All candidate admissions are actually observed source quotes after 300s history.
Full executable Bid/Ask, $0.02 quoted-price fee, +$0.10 nominal price net,
opening-liq -$0.10 stop, 100ms true-first-quote fill, 15s censorship and
60s first-touch horizon. Frozen original R19/S3 outcome is kept separately.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,json,sys
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data'); LAB=ROOT/'h1v2_r21_dualbroker'
R20=ROOT/'h1v2_r20_last46';sys.path.insert(0,str(R20/'src'))
import r20_residual_quote_hazard as p
QUARTER=900000


def exact_cardinality(starts:np.ndarray,ends:np.ndarray)->np.ndarray:
    """Max-cardinality for known intervals, strict start>previous exit; true upper only for supplied universe."""
    if len(starts)==0:return np.empty(0,np.int32)
    if np.any(starts>=ends):raise ValueError('INVALID_INTERVAL')
    ords=np.lexsort((np.arange(len(starts)),starts,ends)); picks=[];last=-2**62
    for k in ords:
        if int(starts[k])>last:picks.append(int(k));last=int(ends[k])
    return np.asarray(picks,dtype=np.int32)


def gap_fresh(t:np.ndarray, ids:np.ndarray)->np.ndarray:
    """Fresh 300s as measured only from past observed quote-gap epoch, no reconstructed gap quotes."""
    if len(ids)==0:return np.empty(0,bool)
    g=np.flatnonzero(np.diff(t)>15000)+1
    if len(g)==0:
        anchor=np.zeros(len(ids),dtype=np.int32)
    else:
        pos=np.searchsorted(g,ids,side='right')-1
        anchor=np.where(pos>=0,g[np.maximum(pos,0)],0)
    return t[ids]-t[anchor]>=300000


def candidate_quote_ix(t:np.ndarray, qkeys:np.ndarray, missing:np.ndarray, halo_ms:int=1000):
    """One actually observed quote per distinct ms, including up to halo_ms before a deficient Q."""
    seg=[];raw=0
    for q in missing:
        lo=qkeys[int(q)]*QUARTER-halo_ms;hi=(qkeys[int(q)]+1)*QUARTER
        a=int(np.searchsorted(t,lo,'left'));b=int(np.searchsorted(t,hi,'left'))
        if b>a:seg.append(np.arange(a,b,dtype=np.int32));raw+=b-a
    if not seg:return np.empty(0,np.int32),{'raw':raw,'unique':0,'fresh':0}
    ix=np.unique(np.concatenate(seg))
    ix=ix[(ix==0)|(t[ix]!=t[np.maximum(ix-1,0)])]
    unique=len(ix);ix=ix[gap_fresh(t,ix)]
    return ix,{'raw':raw,'unique':unique,'fresh':len(ix)}


def wins_from_quotes(t,b,a,qkeys,missing,source_cap=4000,fill_cap=4000,delay=100,horizon=60000,halo_ms=1000):
    """All two-sided OFFLINE first TP actions, no future used to propose candidate."""
    if horizon!=60000 or delay!=100:raise ValueError('R21_COUPLED_CONTRACT_REQUIRES_NEW_VERSION')
    signal,counts=candidate_quote_ix(t,qkeys,missing,halo_ms)
    sp=a[signal].astype(np.int64)-b[signal].astype(np.int64)
    signal=signal[(sp>=0)&(sp<=source_cap)]
    if not len(signal):return [np.empty(0,dtype=k) for k in (np.int32,np.int32,np.int8,np.int32)],{**counts,'spread_ok':0,'filled_unique':0,'both_side_winners':0}
    target=t[signal]+delay;f=np.searchsorted(t,target,side='left');safe=np.minimum(f,len(t)-1)
    valid=(f<len(t))&(safe>signal)&(t[safe]>t[signal])&(t[safe]-target<=1000)
    spread=a[safe].astype(np.int64)-b[safe].astype(np.int64)
    valid&=(spread>=0)&(spread<=fill_cap)
    qidx=t[safe]//QUARTER-qkeys[0]
    valid&=(qidx>=0)&(qidx<len(qkeys))
    valid&=np.isin(qidx,missing)
    fills=np.unique(safe[valid]).astype(np.int32)
    if len(fills):
        codes,exits,net=p.independent_both_sides(t,b,a,fills,0,horizon)
        win=np.argwhere(codes==1)
        ff=fills[win[:,0]];ee=exits[win[:,0],win[:,1]]
        side=np.where(win[:,1]==0,1,-1).astype(np.int8)
        nets=net[win[:,0],win[:,1]]
    else:
        ff=np.empty(0,np.int32);ee=ff.copy();side=np.empty(0,np.int8);nets=ff.copy()
    if len(ff) and (np.any(nets<100) or np.any(t[ee]<=t[ff])):raise AssertionError('FALSE_FIRST_TOUCH_WIN')
    return [ff,ee,side,nets],{**counts,'spread_ok':len(signal),'filled_unique':len(fills),'both_side_winners':len(ff)}


def local_capacity(t, old_f,old_e, qkeys,qref, missing, trial_f,trial_e):
    """Independent complete candidate-universe quarter upper and constrained splice.

    Old original R19/S3 winners already represent legitimate offline first-touch
    intervals under matching lag/spread/fee; do not weaken or assume causal side.
    For every failed original quarter, join ALL incumbent in-quarter intervals with
    ALL new candidate first-touch winners, compute optimistic cardinality with
    external intervals ignored and global-feasible count with all external frozen.
    A globally feasible exchanged schedule must maintain old per-quarter count or
    increase it, preserve external fixed intervals, and pass global nonoverlap.
    """
    orig_count=np.bincount(t[old_f]//QUARTER-qkeys[0],minlength=len(qref));
    allf=old_f.copy();alle=old_e.copy();out=[];replaced=[]
    for qi in missing:
        qi=int(qi);q0=qkeys[qi]*QUARTER;q1=q0+QUARTER
        incumbent=(t[old_f]>=q0)&(t[old_f]<q1)
        option=(t[trial_f]>=q0)&(t[trial_f]<q1)
        candf=np.r_[old_f[incumbent],trial_f[option]]
        cande=np.r_[old_e[incumbent],trial_e[option]]
        ub=exact_cardinality(t[candf],t[cande]);isolated=len(ub)
        # Current schedule may have been modified at an earlier quarter.
        inside=(t[allf]>=q0)&(t[allf]<q1)
        outside=~inside;fixed_f=allf[outside];fixed_e=alle[outside]
        past_end=np.max(t[fixed_e[t[fixed_f]<q0]],initial=-2**62)
        future_start=np.min(t[fixed_f[t[fixed_f]>=q1]],initial=2**62)
        legal=(t[candf]>past_end)&(t[cande]<future_start)
        global_ids=exact_cardinality(t[candf[legal]],t[cande[legal]])
        newf=candf[legal][global_ids];newe=cande[legal][global_ids]
        old_n=int(inside.sum());new_n=len(newf)
        changed=False
        if new_n>old_n:
            allf=np.r_[fixed_f,newf];alle=np.r_[fixed_e,newe]
            o=np.lexsort((np.arange(len(allf)),t[allf]));allf=allf[o];alle=alle[o]
            if len(allf)>1 and np.any(t[allf[1:]]<=t[alle[:-1]]):raise AssertionError('GLOBAL_REPLACEMENT_OVERLAP')
            changed=True;replaced.append(qi)
        out.append({'utc_quarter':dt.datetime.fromtimestamp(q0/1000,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
          'index':qi,'ref':int(qref[qi]),'old_selected':int(orig_count[qi]),
          'candidate_future_winners_both_sides':int(np.count_nonzero(option)),
          'isolated_entire_broker_quote_contract_max':int(isolated),
          'isolated_quota_met':int(isolated>=qref[qi]),
          'legal_external_frozen_bound':new_n,
          'global_additive_exchange_count_change':int(new_n-old_n) if changed else 0,
          'global_exchange_applied':int(changed),
          'not_a_universal_source_upper':True,'not_a_causal_policy':True})
    orig_counts=np.bincount(t[old_f]//QUARTER-qkeys[0],minlength=len(qref))
    after_counts=np.bincount(t[allf]//QUARTER-qkeys[0],minlength=len(qref))
    if np.any(after_counts<orig_counts):raise AssertionError('ANY_ORIGINAL_QUOTA_DEGRADED')
    return allf,alle,out,orig_counts,after_counts,replaced


def run(source,mon):
    t,b,a,_,_,_,raw_info=p.get_frozen(source,mon)
    refs=p.r18.refs_for_month(mon,ROOT);qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
    old_f,old_e,oldcounts,missing=p.get_old(source,mon,t,refs)
    [tf,te,ts,net],cc=wins_from_quotes(t,b,a,qkeys,missing)
    f,e,diag,c0,c1,modified=local_capacity(t,old_f,old_e,qkeys,qref,missing,tf,te)
    totalh0=c0.reshape(-1,4).sum(axis=1);totalh1=c1.reshape(-1,4).sum(axis=1)
    assert len(c1)==len(qref) and len(totalh1)==len(href)
    out=LAB/'results';out.mkdir(parents=True,exist_ok=True)
    stem=f'R21_{source}_{mon}';rows=[]
    for row in diag:
        q=row['index'];rows.append({**row,'source':source,'month':mon,'new_selected_count':int(c1[q]),
          'source_R9_quota_met_after':int(c1[q]>=qref[q]),'original_R9_quota_met_before':int(c0[q]>=qref[q])})
    cp=out/(stem+'_ORIGINAL_DEFICIT_QUARTER_FULL_UNIVERSE_FORENSICS.csv')
    with cp.open('w',newline='') as fd:
        writer=csv.DictWriter(fd,fieldnames=list(rows[0])) if rows else None
        if writer:writer.writeheader();writer.writerows(rows)
    npz=out/(stem+'_ALL_NEW_SOURCE_BOTH_SIDE_WINNER_AND_EXCHANGED_ORDINALS.npz')
    np.savez_compressed(npz,original_R19S3_fill=old_f,original_R19S3_exit=old_e,
       new_possible_fill=tf,new_possible_exit=te,new_possible_side_future=ts,
       new_possible_net_raw=net,quota_aware_global_exchanged_fill=f,quota_aware_global_exchanged_exit=e)
    rec={'source':source,'month':mon,'source_raw_sha':p.r18.PINS[source][mon],
      'source_ref_sha':refs['sha256'],'source_quote_rows':len(t),'original_R19S3_selected':len(old_f),
      'original_R19S3_missing_quarters':len(missing),'all_original_quote_calendar_quarters':len(qref),
      'new_asof_quote_candidate_counters':cc,'new_offline_candidate_first_touch_winners':len(tf),
      'source_isolated_quarters_now_feasible':int(sum(x['isolated_quota_met'] for x in diag)),
      'source_isolated_quarters_still_infeasible_for_THIS_COMPLETED_UNIVERSE':int(sum(not x['isolated_quota_met'] for x in diag)),
      'global_exchange_increased_quarters':len(modified),'global_exchange_quarter_indices':modified,
      'original_active_quarters_met':int(np.sum((qref>0)&(c0>=qref))),
      'exchanged_active_quarters_met':int(np.sum((qref>0)&(c1>=qref))),
      'original_active_hours_met':int(np.sum((href>0)&(totalh0>=href))),
      'exchanged_active_hours_met':int(np.sum((href>0)&(totalh1>=href))),
      'no_asof_predictor':True,'source_offline_future_privileged_selection':True,
      'original_r9_EA_unmodified':True,'safety_barrier_full30_NOT_S1':True,
      'actual_cash_broker_fill_unverified':True,'source_info':raw_info,
      'files':{fp.name:{'sha256':p.sha(fp),'bytes':fp.stat().st_size} for fp in (cp,npz)}}
    jp=out/(stem+'_SOURCE_AND_OUTPUT_SHA_RECEIPT.json');jp.write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:rec[k] for k in ('source','month','original_R19S3_missing_quarters','new_offline_candidate_first_touch_winners','source_isolated_quarters_now_feasible','global_exchange_increased_quarters','original_active_quarters_met','exchanged_active_quarters_met','original_active_hours_met','exchanged_active_hours_met')},indent=2),flush=True)
    return rec

if __name__=='__main__':
    pp=argparse.ArgumentParser();pp.add_argument('--source',choices=('DUKASCOPY_RAW','MT5_BROKER_EXPORT'),required=True)
    pp.add_argument('--month',choices=('01','02','06','07'),required=True)
    aa=pp.parse_args();run(aa.source,aa.month)
