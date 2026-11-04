"""R23H NEW conditional quote-event grammar / independent competing hazard DAY PILOT.

This is NOT another R24S7 threshold sweep. New features count ordered mark runs,
paired BID/ASK leadership, same-ms revision dynamics and asymmetric intensity
of source quotes. Calibrated final model, multi-day training and month/full
calendar replay are NOT implemented/certified here. This is an atomic one-day
engineering experiment with all wrong outcomes. Depends on frozen R24 source
engine extracted from previously SHA-pinned R24 archive (never edits original).

Daily run is source exact quote order with 8h historical halo and >=60s future
halo, R9 clock reference is read from immutable original R23 quarter archive.
All four 2026 months were previously exposed; no claims of OOS. No broker fill.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,time
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np
import lightgbm as lgb
from numba import njit
from r23_hourly_reconciliation import sha,actual_session

SOURCE=Path(__file__).resolve().parents[1]/'frozen_r24_archive'/'source'
sys.path.insert(0,str(SOURCE))
import r24_firstpass_engine as old

HORIZONS=(15000,30000,60000)
FEATURES=tuple(old.FEATURE_NAMES)+(
 'revision_mark_run16','revision_mark_imbalance16','revision_bid_only16',
 'revision_ask_only16','revision_dual16','revision_same_ms16',
 'revision_spread_widen16','revision_quote_acceleration16',
 'revision_signed_bid_flow16','revision_signed_ask_flow16',
 'relative_signed_bid_16_spread','spread_to_favorable_velocity_15s',
 'past_bin_persistence_3s_60s')

@njit(cache=False)
def ordered_grammar(t,b,a,signals,epoch_starts):
    """STRICT PREFIX quote-ordinal features, never advances beyond signals[i]."""
    x=np.zeros((len(signals),13),np.float32)
    for k in range(len(signals)):
        s=signals[k]; ep=epoch_starts[np.searchsorted(epoch_starts,s,side='right')-1]
        d=0;run=0;bidonly=0;askonly=0;dual=0;samems=0;wide=0;bd=0;ad=0
        span=0
        for q in range(s,max(ep+1,s-16),-1):
            db=b[q]-b[q-1];da=a[q]-a[q-1]
            mark=1 if db+da>0 else (-1 if db+da<0 else 0)
            if q==s:d=mark
            if run==s-q and mark==d and mark!=0:run+=1
            if db!=0 and da==0:bidonly+=1
            elif da!=0 and db==0:askonly+=1
            elif db!=0 and da!=0:dual+=1
            if t[q]==t[q-1]:samems+=1
            if a[q]-b[q]>a[q-1]-b[q-1]:wide+=1
            bd+=db;ad+=da
            span+=1
        denom=max(span,1);spread=max(a[s]-b[s],1)
        age_ms=max(t[s]-t[max(ep,s-16)],1)
        x[k,0]=run
        x[k,1]=np.sign(bd+ad)
        x[k,2]=bidonly/denom;x[k,3]=askonly/denom;x[k,4]=dual/denom
        x[k,5]=samems/denom;x[k,6]=wide/denom
        x[k,7]=span*1000/age_ms
        x[k,8]=bd/denom;x[k,9]=ad/denom;x[k,10]=bd/spread
        # last two columns calculated from first-party *past-only* features
    return x

def future_gap(t,fill,hh):
    """Offline only: true future observed gap crosses holding horizon."""
    gapidx=np.flatnonzero(np.diff(t)>15000)+1
    f=np.maximum(fill,0)
    ht=t[f]+hh
    j=np.searchsorted(t,ht,side='left')
    nxt=np.searchsorted(gapidx,f+1)
    g=np.full(len(f),len(t),np.int64)
    has=nxt<len(gapidx);g[has]=gapidx[nxt[has]]
    # A >15s missing-quote interval crosses horizon even if its ending quote is afterward.
    gi=np.minimum(g,len(t)-1)
    crosses=(g<len(t))&(t[gi-1]<ht)&(t[gi]-t[gi-1]>15000)
    occurs=(g<len(t))&(t[gi]<=ht)
    return (fill>=0)&(crosses|occurs)

@njit(cache=False)
def query_minmax(size,bmin,amax,left,right):
    """Inclusive min(BID) and max(ASK) over actual observed source ordinals."""
    low=2147483647; high=-2147483647
    l=left+size;r=right+size
    while l<r:
        if l&1:
            low=min(low,bmin[l]);high=max(high,amax[l]);l+=1
        if r&1:
            r-=1;low=min(low,bmin[r]);high=max(high,amax[r])
        l//=2;r//=2
    return low,high

def full_held_labels(t,b,a,fill,horizon):
    """Separate NO ADVERSE STOP through full H, unlike TP first labels."""
    size,_,bmin,amax,_=old.build_tree(b,a)
    f=np.maximum(fill,0)
    end=np.searchsorted(t,t[f]+horizon,side='left')
    gap=future_gap(t,fill,horizon)
    known=(fill>=0)&(end<len(t))&(~gap)
    ei=np.minimum(end,len(t)-1)
    known &= (t[ei]-(t[f]+horizon)<=15000)
    held=np.full((len(fill),2),-1,np.int8)
    for k in np.flatnonzero(known):
        # Include actual fill quote as reference; monitor following ticks through first >= H.
        v,w=query_minmax(size,bmin,amax,int(fill[k]+1),int(ei[k]+1))
        held[k,0]=int(v>int(b[fill[k]])-100)
        held[k,1]=int(w<int(a[fill[k]])+100)
    return held

def wait10_labels(t0,labels):
    """Offline future opportunity ahead within 10 s, never online feature."""
    good=np.any(labels[:,:,0]==old.CLASS_NAMES.index('TARGET'),axis=1)
    # Next distinct favorable signal, not current signal.
    ix=np.flatnonzero(good)
    out=np.zeros(len(t0),np.int8)
    if len(ix):
        p=np.searchsorted(ix,np.arange(len(t0))+1)
        v=p<len(ix)
        ixnext=ix[np.minimum(p,len(ix)-1)]
        out[v]=((t0[ixnext[v]]-t0[v])<=10000).astype(np.int8)
    return out

def model_rows(y,p):
    return {'positive':int(np.sum(y==1)),'negative':int(np.sum(y==0)),
      'prob_mean':float(np.mean(p)),'prob_min':float(np.min(p)),'prob_max':float(np.max(p))}

def fit_binary(X,y,rounds=24):
    classes=np.bincount(y.astype(np.int32),minlength=2)
    if classes.min()<30:raise RuntimeError('BINARY_HEAD_TOO_FEW_CLASSES '+str(classes))
    d=lgb.Dataset(X,label=y,feature_name=FEATURES,free_raw_data=True)
    params=dict(objective='binary',metric='binary_logloss',learning_rate=.06,num_leaves=15,
      min_data_in_leaf=80,lambda_l2=12,feature_fraction=.95,max_bin=127,
      num_threads=2,verbosity=-1,seed=20261104,deterministic=True)
    m=lgb.train(params,d,num_boost_round=rounds)
    return m

def run_jan02(source,output,iterations=24):
    if source not in old.SOURCE_NAMES:raise ValueError(source)
    start=time.monotonic();out=Path(output)/source/'01'/'2026-01-02';out.mkdir(parents=True,exist_ok=True)
    # Only January original raw source is mounted in this session. Original source SHA is fixed.
    raw=old.source_file(source,'01')
    expected={'DUKASCOPY_RAW':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
              'MT5_BROKER_EXPORT':'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8'}[source]
    if sha(raw)!=expected:raise RuntimeError('JANUARY_RAW_SHA_MISMATCH')
    t,b,a=old.raw_month(source,'01',verify=False)
    day0=int(datetime(2026,1,2,tzinfo=timezone.utc).timestamp()*1000);day1=day0+86400000
    # 8h left prefix for completed H4, >=60s actual forward on original source.
    l=np.searchsorted(t,day0-8*3600000,'left')
    r=np.searchsorted(t,day1+90000,'right')
    ts=t[l:r];bs=b[l:r];asks=a[l:r]
    if len(ts)<10000:raise RuntimeError('DAY_RAW_INSUFFICIENT')
    sig,gapstarts=old.candidates(ts,bs,asks,decision_ms=1000,cap=4000)
    sig=sig[(ts[sig]>=day0)&(ts[sig]<day1)]
    fill=old.fill_after(ts,bs,asks,sig,lag=100,fillcap=4000,stale=1000)
    labels,events,fillvalid=old.generate_labels(ts,bs,asks,sig,fill)
    X0=old.extract_features(ts,bs,asks,sig,gapstarts,source)
    X1=ordered_grammar(ts,bs,asks,sig,gapstarts)
    ix={n:i for i,n in enumerate(old.FEATURE_NAMES)}
    X1[:,11]=np.abs(X0[:,ix['bid_move_15s']])/(1+X0[:,ix['spread_raw']])
    X1[:,12]=np.sign(X0[:,ix['bid_move_3s']]*X0[:,ix['bid_move_60s']])
    X=np.hstack([X0,X1]).astype(np.float32)
    # Old archived code sets news_available=0 and operations_permission_verified=0.
    # Explicitly exclude these two unverified features by encoding UNKNOWN=-1.
    for name in ('news_verified_available','operations_permission_verified'):
        X[:,ix[name]]=-1.0
    if not np.isfinite(X).all():raise RuntimeError('NONFINITE_PREFIX')
    if X.shape[1]!=len(FEATURES):raise RuntimeError('FEATURE_SCHEMA_MISMATCH')
    n=len(sig)
    held15=full_held_labels(ts,bs,asks,fill,15000)
    gap15=future_gap(ts,fill,15000)
    w=wait10_labels(ts[sig],labels)
    # Deterministic label-independent uniform sample for atomic day pilot.
    s=np.linspace(0,max(n-1,0),min(n,25000),dtype=np.int64)
    models={};scores={};bins={}
    for side in (0,1):
        for name,y in (
            ('target_first',labels[:,side,0]==1),
            ('adverse_stop_first',labels[:,side,0]==0),
            ('quote_gap_within_15',gap15),
            ('full_15_no_stop',held15[:,side]==1)):
            key=('BUY' if side==0 else 'SELL')+'_'+name
            y=y.astype(np.int8)
            try:m=fit_binary(X[s],y[s],rounds=iterations)
            except RuntimeError as exc:scores[key]={'status':'HEAD_NOT_TRAINED','reason':str(exc)};continue
            pred=m.predict(X,num_threads=2)
            models[key]=m
            bins[key]=pred
            scores[key]={'status':'TRAINED_HEAVILY_IN_SAMPLE_SOURCE_DAY','feature_count':len(FEATURES),
             'sample_n':len(s),'histogram':np.bincount(y[s],minlength=2).tolist(),
             'all_day_observed_training_feature_probability':model_rows(y,pred)}
            m.save_model(str(out/(key+'.lightgbm.txt')))
    mw=fit_binary(X[s],w[s],rounds=iterations)
    bins['WAIT10']=mw.predict(X,num_threads=2)
    scores['WAIT10']={'status':'TRAINED_HEAVILY_IN_SAMPLE_SOURCE_DAY','sample_n':len(s),
     'histogram':np.bincount(w[s],minlength=2).tolist(),
     'all_day_probability':model_rows(w,bins['WAIT10'])}
    mw.save_model(str(out/'WAIT10.lightgbm.txt'))
    # PROTOTYPE one-position policy only if both sides have all three probabilities.
    need=('BUY_target_first','SELL_target_first','BUY_adverse_stop_first','SELL_adverse_stop_first',
          'BUY_quote_gap_within_15','SELL_quote_gap_within_15','BUY_full_15_no_stop','SELL_full_15_no_stop')
    missing=[k for k in need if k not in bins]
    # No fake rare-event P; when a required head is missing, all actions WAIT.
    for key in missing:bins[key]=np.full(n,np.nan,np.float64)
    targets=np.c_[bins['BUY_target_first'],bins['SELL_target_first']]
    stops=np.c_[bins['BUY_adverse_stop_first'],bins['SELL_adverse_stop_first']]
    gaps=np.c_[bins['BUY_quote_gap_within_15'],bins['SELL_quote_gap_within_15']]
    holds=np.c_[bins['BUY_full_15_no_stop'],bins['SELL_full_15_no_stop']]
    # Independent heads need not sum to 1. Rank expected direction by target-stop-gap,
    # only after individual eligibility; calibration and risk gates not yet certified.
    util=targets-stops-0.5*gaps+0.15*holds-0.05*bins['WAIT10'][:,None]
    # Prototype decision: no arbitrary high threshold; willingness to WAIT is explicit.
    eligible=(fill>=0)&np.isfinite(util).all(axis=1)
    position_end=-1;selected=[]
    for k in range(n):
        if not eligible[k] or ts[fill[k]]<=position_end:continue
        side=int(np.argmax(util[k]))
        if util[k,side]<=0:continue
        position_end=int(ts[fill[k]])+15000
        selected.append((k,side))
    refday=0;refs=[];dirq=Path(__file__).resolve().parents[1]/'results'/'DUKASCOPY_RAW'/'01'/'DUKASCOPY_RAW_01_original_quarters.csv'
    with open(dirq,newline='') as f:
        rdr=csv.DictReader(f)
        refs=[r for r in rdr if r['scenario']=='A1_TP050_STOP100_H60_CAP4000_Q8' and r['utc_quarter'].startswith('2026-01-02')]
    if len(refs)!=96:raise RuntimeError('MISSING_REFERENCE_DAY_QUARTERS')
    ref=np.array([int(r['original_R9_SYNTH_reference']) for r in refs])
    qcounts=np.zeros(96,np.int32);qcorrect=np.zeros(96,np.int32);qheld=np.zeros(96,np.int32)
    details=[]
    # Keep the COMPLETE source-day label universe, even with zero selected trades.
    np.savez_compressed(out/'ALL_FIRST_DAY_CANDIDATE_LABELS_AND_QUOTE_ORDINALS.npz',
       asof_signal_source_quote_ordinal=sig.astype(np.int32)+int(l),
       true_first_plus100ms_fill_source_quote_ordinal=np.where(fill>=0,fill+int(l),-1).astype(np.int32),
       signal_utc_ms=ts[sig].astype(np.int64),
       future_two_side_three_horizon_five_cause_label=labels.astype(np.int8),
       future_first_event_quote_ordinal=np.where(events>=0,events+int(l),-1).astype(np.int32),
       future_fullhold15_label=held15.astype(np.int8),
       future_true_quote_gap15=gap15.astype(np.uint8),
       future_wait10=w.astype(np.int8),
       asof_prefix_feature_names=np.asarray(FEATURES),
       asof_prefix_features=X.astype(np.float32))
    for k,side in selected:
        q=int((ts[fill[k]]-day0)//900000)
        if not 0<=q<96:continue
        qcounts[q]+=1;qcorrect[q]+=(labels[k,side,0]==1);qheld[q]+=(held15[k,side]==1)
        details.append({'signal_global_original_ordinal':int(l+sig[k]),'fill_global_original_ordinal':int(l+fill[k]),
          'utc_signal_ms':int(ts[sig[k]]),'utc_fill_ms':int(ts[fill[k]]),'side':'BUY' if side==0 else 'SELL',
          'future_label_first15':old.CLASS_NAMES[labels[k,side,0]],
          'future_full15_survival':int(held15[k,side]),
          'future_quote_gap15':bool(gap15[k]),
          'pred_target_first':float(targets[k,side]),'pred_stop_first':float(stops[k,side]),
          'pred_quote_gap':float(gaps[k,side]),'pred_fullhold15':float(holds[k,side]),
          'pred_wait10':float(bins['WAIT10'][k]),'utility':float(util[k,side]),
          'research_source_only':True})
    def write_csv(file,rows):
        if not rows:return
        with open(file,'w',newline='') as f:
            w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
    perq=[];perh=[]
    for j in range(96):
        when=datetime.fromtimestamp((day0+j*900000)/1000,tz=timezone.utc).isoformat()
        perq.append({'utc_quarter':when,'r9_SYNTH_UTC_reference':int(ref[j]),
          'causal_prototype_positions':int(qcounts[j]),
          'initial15_target_first':int(qcorrect[j]),'initial15_full_h_survived':int(qheld[j]),
          'simulated_observed_quote_fill_not_broker_fill':True,
          'historically_exposed_day_fit_and_evaluation':True,
          'news_vintage':'UNKNOWN','broker_operation':'UNKNOWN'})
    for j in range(24):
        k=j*4;slice_=perq[k:k+4]
        perh.append({'utc_hour':slice_[0]['utc_quarter'],'r9_SYNTH_UTC_reference':sum(x['r9_SYNTH_UTC_reference'] for x in slice_),
          'causal_prototype_positions':sum(x['causal_prototype_positions'] for x in slice_),
          'initial15_target_first':sum(x['initial15_target_first'] for x in slice_),
          'initial15_full_h_survived':sum(x['initial15_full_h_survived'] for x in slice_),
          'news_vintage':'UNKNOWN','broker_operation':'UNKNOWN'})
    write_csv(out/'ALL_ORIGINAL_24_UTC_HOURS.csv',perh)
    write_csv(out/'ALL_ORIGINAL_96_UTC_QUARTERS.csv',perq)
    write_csv(out/'COMPLETE_SELECTED_QUOTES_AND_WRONG_CASES.csv',details)
    rec={'status':'ONE_DAY_ENGINEERING_PILOT_HEAVY_IN_SAMPLE_NOT_DEPLOYABLE','source':source,
     'month':'01','utc_day':'2026-01-02','full_month_input_sha256':expected,
     'daily_raw_slice_start_global_quote_ordinal':int(l),'daily_raw_slice_stop_global_quote_ordinal':int(r),
     'daily_historical_slice_prefix_8h_forward_90s':True,
     'signal_n':int(n),'actual_quote_first_plus100ms_filled':int((fill>=0).sum()),
     'full_horizon_15_known':int((held15>=0).sum()),
     'training_25k_deterministic_sample_only':int(len(s)),
     'feature_names':FEATURES,'separate_heads':scores,
     'missing_rare_event_heads':missing,'all_actions_fail_closed_on_missing_head':bool(missing),
     'reference_day_original_R9_SYNTH':int(ref.sum()),
     'prototype_selected_one_position_conservative_15sec':int(len(selected)),
     'prototype_first_target_count':int(qcorrect.sum()),
     'prototype_hold_full_15_count':int(qheld.sum()),
     'reference_active_quarters':int((ref>0).sum()),
     'quarter_joint80_and_reference_count':sum(int(qcounts[j]>=ref[j] and qcorrect[j]>=.8*qcounts[j]) for j in range(96) if ref[j]>0),
     'hour_joint80_and_reference_count':sum(int(row['causal_prototype_positions']>=row['r9_SYNTH_UTC_reference'] and row['initial15_target_first']>=.8*row['causal_prototype_positions']) for row in perh if row['r9_SYNTH_UTC_reference']>0),
     'no_real_Coinexx_dealer_fill':True,'news_and_prop_permission':'UNKNOWN',
     'not_OOS':True,'not_model_calibrated':True,'no_cash_PNL':True,
     'elapsed_sec':time.monotonic()-start,
     'files_sha256':{p.name:sha(p) for p in out.glob('*') if p.is_file()}}
    (out/'ATOMIC_DAY_CAUSAL_HAZARD_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
    print('DAY_CAUSAL_PILOT',source,'signal',n,'sample',len(s),'selected',len(selected),'target',qcorrect.sum(),'held',qheld.sum(),'reference',ref.sum(),'MISSING_HEADS',missing,flush=True)
    return rec

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',choices=old.SOURCE_NAMES,required=True)
    p.add_argument('--out',required=True);p.add_argument('--iterations',type=int,default=24)
    a=p.parse_args();run_jan02(a.source,a.out,a.iterations)
