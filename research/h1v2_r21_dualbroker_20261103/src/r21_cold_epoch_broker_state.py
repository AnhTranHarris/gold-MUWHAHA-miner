"""R21 Cycle D: distinct REOPEN micro-epoch H1V2 candidate contract.

Controlled research counterfactual: 60/120/180/300s continuous *observed*
quote readiness after >15s gaps; no interpolation or synthetic quotes. This
explicitly CHANGES original v5 300s readiness (except 300s frozen control).
Source-side and delayed-fill quote spread are paid. Independent BUY/SELL
observed 100ms actual fill and first +.10 net before -0.10 adverse <=60s.
ALL candidate outcomes STOP/TIMEOUT/CENSORED and all actual source ordinals
are retained. Offline future-selected winners are NOT predictive or a PnL EA.
"""
from __future__ import annotations
import argparse,csv,json,sys,datetime as dt
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data');HERE=ROOT/'h1v2_r21_dualbroker';sys.path.insert(0,str(HERE/'src'))
import r21_quota_aware_interval_exchange as base
p=base.p
CASES=[('OBSERVED_EPOCH_060_CAP4000',60000,4000),('OBSERVED_EPOCH_120_CAP4000',120000,4000),
       ('OBSERVED_EPOCH_180_CAP4000',180000,4000),('ORIGINAL_EPOCH_300_CAP4000',300000,4000),
       ('OBSERVED_EPOCH_060_CAP8000',60000,8000),('OBSERVED_EPOCH_120_CAP8000',120000,8000),
       ('OBSERVED_EPOCH_180_CAP8000',180000,8000),('ORIGINAL_EPOCH_300_CAP8000',300000,8000)]


def elapsed_since_last_gap(t,ix):
    gaps=np.flatnonzero(np.diff(t)>15000).astype(np.int32)+1
    if len(gaps)==0:
        anchor=np.zeros(len(ix),dtype=np.int32)
    else:
        loc=np.searchsorted(gaps,ix,side='right')-1
        anchor=np.where(loc>=0,gaps[np.maximum(loc,0)],0)
    return t[ix]-t[anchor]


def build_all_trials(t,b,a,qkeys,missing,halo_ms=1000):
    if not len(missing):return None
    ix,metadata=base.candidate_quote_ix(t,qkeys,missing,halo_ms)
    # For this newly defined research class do not filter 300s; instead rescan
    # all observed distinct milliseconds and require >=60 seconds later.
    spans=[]
    for q in missing:
        l=int(np.searchsorted(t,qkeys[q]*base.QUARTER-halo_ms,'left'))
        r=int(np.searchsorted(t,(qkeys[q]+1)*base.QUARTER,'left'))
        if r>l:spans.append(np.arange(l,r,dtype=np.int32))
    if not spans:return None
    ix=np.unique(np.concatenate(spans))
    ix=ix[(ix==0)|(t[ix]!=t[np.maximum(ix-1,0)])]
    age=elapsed_since_last_gap(t,ix)
    sigspread=a[ix].astype(np.int64)-b[ix].astype(np.int64)
    signal_ok=(age>=60000)&(sigspread>=0)&(sigspread<=8000)
    ix=ix[signal_ok];age=age[signal_ok];sigspread=sigspread[signal_ok]
    if not len(ix):return None
    requested=t[ix]+100;f=np.searchsorted(t,requested,'left');jj=np.minimum(f,len(t)-1)
    valid=(f<len(t))&(jj>ix)&(t[jj]>t[ix])&(t[jj]-requested<=1000)
    fillspr=a[jj].astype(np.int64)-b[jj].astype(np.int64)
    valid&=(fillspr>=0)&(fillspr<=8000)
    qidx=t[jj]//base.QUARTER-qkeys[0]
    valid&=(qidx>=0)&(qidx<len(qkeys))&np.isin(qidx,missing)
    sig=ix[valid];fill=jj[valid];age=age[valid]
    sigsp=sigspread[valid];filsp=fillspr[valid]
    if not len(sig):return None
    uniq_fill,inv=np.unique(fill,return_inverse=True)
    codes,exits,net=p.independent_both_sides(t,b,a,uniq_fill.astype(np.int32),0,60000)
    return {'signal':sig,'actual_fill':fill,'epoch_age_ms':age,'source_spread_raw':sigsp,'actual_fill_spread_raw':filsp,
            'unique_fill':uniq_fill,'inverse_fill':inv,'all_side_outcome_code':codes,'all_side_exit':exits,'all_side_net':net,
            'raw_first_candidate_metadata':metadata}


def run(source,mon):
    t,b,a,_,_,_,info=p.get_frozen(source,mon)
    refs=p.r18.refs_for_month(mon,ROOT);qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
    oldf,olde,c0,missing=p.get_old(source,mon,t,refs)
    trials=build_all_trials(t,b,a,qkeys,missing)
    out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
    prefix=f'R21D_{source}_{mon}'
    rows=[];calendar=[];hours=[];daily=[];archive={}
    for name,epoch,cap in CASES:
        if trials is None:
            ff=np.empty(0,np.int32);ex=ff.copy();side=np.empty(0,np.int8)
            selected=np.empty(0,np.int64);codes=np.empty((0,2),np.int8)
            side_fail={'GOOD':0,'STOP':0,'TIMEOUT':0,'CENSORED':0}
        else:
            allowed=(trials['epoch_age_ms']>=epoch)&(trials['source_spread_raw']<=cap)&(trials['actual_fill_spread_raw']<=cap)
            # Preserve selected source signals after each differing gate, then
            # deduplicate final fill ordinals WITHOUT looking at future labels.
            ci=np.flatnonzero(allowed)
            fill_sub=trials['actual_fill'][ci]
            uf,first=np.unique(fill_sub,return_index=True)
            chosen=ci[first]
            # Future code is evaluated at already-fixed actual fill quote.
            original_ix=trials['inverse_fill'][chosen]
            codes=trials['all_side_outcome_code'][original_ix]
            exits=trials['all_side_exit'][original_ix]
            nets=trials['all_side_net'][original_ix]
            winners=np.argwhere(codes==1)
            ff=uf[winners[:,0]].astype(np.int32)
            ex=exits[winners[:,0],winners[:,1]].astype(np.int32)
            side=np.where(winners[:,1]==0,1,-1).astype(np.int8)
            chosen_cash=nets[winners[:,0],winners[:,1]]
            if len(ff) and np.any(chosen_cash<100):raise AssertionError('COLD_EPOCH_FALSE_WIN')
            side_fail={str(key):int(np.count_nonzero(codes==v)) for key,v in [('GOOD',1),('STOP',0),('TIMEOUT',2),('CENSORED',-3)]}
        f,e,diag,orig,after,replaced=base.local_capacity(t,oldf,olde,qkeys,qref,missing,ff,ex)
        qgain=after-orig;hbase=orig.reshape(-1,4).sum(axis=1);hnew=after.reshape(-1,4).sum(axis=1)
        active=(qref>0);hractive=(href>0)
        trialrec={'source':source,'month':mon,'case':name,'after_gap_history_ms':epoch,
          'research_spread_max_raw':cap,'historical_300s_gate_unchanged':epoch==300000,
          'observed_actual_fill_lag_ms':100,'horizon_firstTP_ms':60000,'stop_initial_raw':100,
          'candidate_future_good_trial_count':len(ff),'candidate_actual_fill_unique_tested':len(codes),
          **{f'OUTCOME_{k}':v for k,v in side_fail.items()},
          'source_quarters_with_original_reference':int(active.sum()),
          'full_original_R9_SYNTH_reference':int(qref.sum()),
          'quota_meet_quarters_before':int(np.sum(active&(orig>=qref))),
          'quota_meet_quarters_after':int(np.sum(active&(after>=qref))),
          'source_hours_active':int(hractive.sum()),
          'quota_meet_hours_before':int(np.sum(hractive&(hbase>=href))),
          'quota_meet_hours_after':int(np.sum(hractive&(hnew>=href))),
          'oracle_future_side_selected_only':True,'causal_full_EA_not_trained':True,
          'changed_runtime_reopening_gate_unapproved':epoch!=300000,
          'source_broker_real_fill_and_account_net_unverified':True}
        rows.append(trialrec)
        for q in range(len(qref)):
            calendar.append({'source':source,'month':mon,'case':name,'utc_quarter':refs['rows'][q]['utc_quarter'],
              'R9_SYNTH_quarter_ref':int(qref[q]),'original_R19S3_hindsight_count':int(orig[q]),
              'R21_cold_epoch_hindsight_count':int(after[q]),'delta':int(qgain[q]),
              'source_quota_met':int(after[q]>=qref[q]) if active[q] else '',
              'result_future_selected_and_not_causal':True})
        for h in range(len(href)):
            hours.append({'source':source,'month':mon,'case':name,'utc_hour':refs['rows'][h*4]['utc_hour'],
              'R9_SYNTH_hour_ref':int(href[h]),'original_R19S3_hindsight_count':int(hbase[h]),
              'R21_cold_epoch_hindsight_count':int(hnew[h]),'delta':int(hnew[h]-hbase[h]),
              'hour_quota_met':int(hnew[h]>=href[h]) if hractive[h] else '',
              'result_future_selected_and_not_causal':True})
        for d in range(len(qref)//96):
            sl=slice(96*d,96*(d+1));ref=int(qref[sl].sum());count=int(after[sl].sum())
            daily.append({'source':source,'month':mon,'case':name,
              'utc_date':refs['rows'][96*d]['utc_quarter'][:10], 'R9_SYNTH_daily_ref':ref,
              'R21_cold_epoch_day_hindsight_count':count,'day_quota_met':int(count>=ref) if ref else '',
              'active_quarters':int(np.count_nonzero(active[sl])),
              'quarter_quotas_met':int(np.count_nonzero(active[sl]&(after[sl]>=qref[sl]))),
              'result_future_selected_and_not_causal':True})
        archive[name+'__selected_fill']=f.astype(np.int32)
        archive[name+'__selected_exit']=e.astype(np.int32)
        archive[name+'__new_winner_fill']=ff.astype(np.int32)
        archive[name+'__new_winner_exit']=ex.astype(np.int32)
        archive[name+'__new_winner_future_side']=side.astype(np.int8)
        print(source,mon,name,'wins',len(ff),'Q',trialrec['quota_meet_quarters_after'],'H',trialrec['quota_meet_hours_after'],flush=True)
    paths=[]
    for suffix,data in [('ALL_8_SCENARIOS',rows),('ALL_UTC_15MIN_EIGHT_SCENARIOS',calendar),('ALL_UTC_HOURS_EIGHT_SCENARIOS',hours),('ALL_UTC_DAYS_EIGHT_SCENARIOS',daily)]:
        op=out/(prefix+'_'+suffix+'.csv');paths.append(op)
        with op.open('w',newline='') as fh:
            w=csv.DictWriter(fh,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    # Lossless original quote ordinals and BOTH side outcomes for all candidate
    # fills, including STOP, TIMEOUT and CENSOR - not only selected winners.
    if trials is None:trials={'signal':np.empty(0,np.int32),'actual_fill':np.empty(0,np.int32),
        'epoch_age_ms':np.empty(0,np.int64),'source_spread_raw':np.empty(0,np.int32),
        'actual_fill_spread_raw':np.empty(0,np.int32),'unique_fill':np.empty(0,np.int32),
        'inverse_fill':np.empty(0,np.int32),'all_side_outcome_code':np.empty((0,2),np.int8),
        'all_side_exit':np.empty((0,2),np.int32),'all_side_net':np.empty((0,2),np.int32)}
    npz=out/(prefix+'_ALL_TWO_SIDE_SOURCE_ORDINAL_TRIALS_NEGATIVE_AND_GOOD.npz');paths.append(npz)
    np.savez_compressed(npz,**{k:v for k,v in trials.items() if isinstance(v,np.ndarray)},**archive)
    result={'source':source,'month':mon,'source_SHA256':p.r18.PINS[source][mon],
       'source_reference_SHA256':refs['sha256'],'month_quote_rows':len(t),
       'original_unmodified_R19_S3_entry_intervals':len(oldf),
       'original_R19_S3_residual_quarters':len(missing),'all_month_quarters':len(qref),
       'all_month_hours':len(href),'all_month_days':len(qref)//96,
       'scenarios':rows,'origin_quote_receipts':info,'output_files':{path.name:{'bytes':path.stat().st_size,'sha256':p.sha(path)} for path in paths},
       'original_R9_H1V2_300s_admission_never_overwritten':True,
       'COLD_60_120_180_are_changed_research_contracts_ONLY':True,
       'original_15F30S_not_reclassified_as_60s_firstTouch':True,
       'future_side_oracle_only_not_a_tradable_policy':True}
    jp=out/(prefix+'_FULL_SHA_AND_SCIENCE_RECEIPT.json');jp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result

if __name__=='__main__':
    z=argparse.ArgumentParser();z.add_argument('--source',required=True,choices=('DUKASCOPY_RAW','MT5_BROKER_EXPORT'))
    z.add_argument('--month',required=True,choices=('01','02','06','07'));args=z.parse_args()
    run(args.source,args.month)
