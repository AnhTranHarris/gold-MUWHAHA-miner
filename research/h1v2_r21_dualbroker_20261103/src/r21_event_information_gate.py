"""R21 Cycle E: causal AS-OF quote information readiness before independent future labels.

Separate changed micro-epoch admission contract, never original R9 v5 300s.
Historical quote data for two feeds Jan/Feb/Jun/Jul, no OHLC interpolation.
Source observed past >=30s after >15s gap; previous 30s source quote count and
previous 15s bid/ask spread average and coherent bid+ask 3s changes only use
quote ordinals <= decision signal. True +100ms first quote fill, ± executable
Bid/Ask, $0.02 quote-price research fee, +$0.10 first-touch before -$0.10
initial liquidation adverse, actual first TP <=60s. Never assume causal side:
future BUY/SELL outcomes are labels, selected hindsight is not a trained policy.
"""
from __future__ import annotations
import argparse,csv,json,sys,datetime as dt
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data'); LAB=ROOT/'h1v2_r21_dualbroker';sys.path.insert(0,str(LAB/'src'))
import r21_quota_aware_interval_exchange as exch
import r21_cold_epoch_broker_state as cold
p=exch.p;Q=900000
CASES=(
 ('CONTROL_EPOCH060_CAP4000',60000,0,4000,False,False),
 ('EVENT30_8_QUOTES_CAP4000',30000,8,4000,False,False),
 ('EVENT30_30_QUOTES_CAP4000',30000,30,4000,False,False),
 ('EVENT45_8_QUOTES_CAP4000',45000,8,4000,False,False),
 ('EVENT30_8_QUOTES_SPREAD_STABLE_CAP4000',30000,8,4000,True,False),
 ('EVENT30_8_QUOTES_MICRO_FLOW_CAP4000',30000,8,4000,False,True),
 ('EVENT30_8_QUOTES_CAP8000_DIAGNOSTIC',30000,8,8000,False,False),
)


def observed_prefix_metrics(t,b,a,ix):
    """As-of only. Count prior 30s and quote spread mean trailing 15s; bid/ask 3s move."""
    if not len(ix):return tuple(np.empty(0) for _ in range(4))
    x30=np.searchsorted(t,t[ix]-30000,side='left')
    count=ix-x30+1
    x15=np.searchsorted(t,t[ix]-15000,side='left')
    raw=a.astype(np.int64)-b.astype(np.int64)
    cs=np.r_[0,np.cumsum(raw,dtype=np.int64)]
    spread_mean=(cs[ix+1]-cs[x15])/(ix-x15+1)
    prev=np.searchsorted(t,t[ix]-3000,side='right')-1
    prev=np.clip(prev,0,len(t)-1)
    move_bid=b[ix].astype(np.int64)-b[prev].astype(np.int64)
    move_ask=a[ix].astype(np.int64)-a[prev].astype(np.int64)
    coherent=(np.sign(move_bid)==np.sign(move_ask))&(np.minimum(abs(move_bid),abs(move_ask))>=raw[ix]+120)
    return count,spread_mean,coherent,raw[ix]


def generate_trials(t,b,a,qkeys,missing):
    seg=[]
    for q in missing:
        lo=int(np.searchsorted(t,qkeys[q]*Q-1000,'left'));hi=int(np.searchsorted(t,(qkeys[q]+1)*Q,'left'))
        if hi>lo:seg.append(np.arange(lo,hi,dtype=np.int32))
    if not seg:return None
    signal=np.unique(np.concatenate(seg))
    signal=signal[(signal==0)|(t[signal]!=t[np.maximum(signal-1,0)])]
    age=cold.elapsed_since_last_gap(t,signal)
    spread=a[signal].astype(np.int64)-b[signal].astype(np.int64)
    valid=(age>=30000)&(spread>=0)&(spread<=8000)
    signal=signal[valid];age=age[valid];spread=spread[valid]
    if not len(signal):return None
    count,mean15,coherent,rawspread=observed_prefix_metrics(t,b,a,signal)
    target=t[signal]+100;f=np.searchsorted(t,target,'left');safe=np.minimum(f,len(t)-1)
    allowed=(f<len(t))&(safe>signal)&(t[safe]>t[signal])&(t[safe]-target<=1000)
    actual_spread=a[safe].astype(np.int64)-b[safe].astype(np.int64)
    fillq=t[safe]//Q-qkeys[0]
    allowed&=(actual_spread>=0)&(actual_spread<=8000)
    allowed&=(fillq>=0)&(fillq<len(qkeys))&np.isin(fillq,missing)
    signal=signal[allowed];age=age[allowed];spread=spread[allowed]
    count=count[allowed];mean15=mean15[allowed];coherent=coherent[allowed]
    actual_spread=actual_spread[allowed];f=safe[allowed]
    if not len(signal):return None
    u,inv=np.unique(f,return_inverse=True)
    codes,exits,net=p.independent_both_sides(t,b,a,u.astype(np.int32),0,60000)
    return {'source_signal':signal,'epoch_age':age,'current_spread':spread,'last30_quote_count':count,
     'past15_spread_mean':mean15,'coherent3s_bidask':coherent,'fill_spread':actual_spread,
     'fill':f,'unique_fill':u,'inverse_fill':inv,'code':codes,'exit':exits,'net':net}


def run(source,mon):
    t,b,a,_,_,_,input_rec=p.get_frozen(source,mon)
    refs=p.r18.refs_for_month(mon,ROOT);keys=refs['qkeys'];qref=refs['qref'];href=refs['href']
    oldf,olde,orig,missing=p.get_old(source,mon,t,refs)
    trial=generate_trials(t,b,a,keys,missing)
    outcomes=[];quarters=[];hours=[];days=[];npzfields={};active=qref>0
    for name,age,count,cap,stable,flow in CASES:
        if trial is None:
            ff=np.empty(0,np.int32);ex=ff.copy();sd=np.empty(0,np.int8)
            allcodes=np.empty((0,2),np.int8)
        else:
            permitted=(trial['epoch_age']>=age)&(trial['last30_quote_count']>=count)&(trial['current_spread']<=cap)&(trial['fill_spread']<=cap)
            if stable:permitted&=(trial['current_spread']<=1.2*trial['past15_spread_mean'])
            if flow:permitted&=trial['coherent3s_bidask']
            z=np.flatnonzero(permitted);f=trial['fill'][z]
            uf,first=np.unique(f,return_index=True);chosen=z[first]
            j=trial['inverse_fill'][chosen]
            allcodes=trial['code'][j];exit=trial['exit'][j];net=trial['net'][j]
            win=np.argwhere(allcodes==1)
            ff=uf[win[:,0]].astype(np.int32);ex=exit[win[:,0],win[:,1]].astype(np.int32)
            sd=np.where(win[:,1]==0,1,-1).astype(np.int8)
            if len(ff) and (np.any(t[ex]<=t[ff]) or np.any(net[win[:,0],win[:,1]]<100)):
                raise AssertionError('NOT_GENUINE_OBSERVED_PROFIT')
        futuref,futuree,diag,c0,c1,changes=exch.local_capacity(t,oldf,olde,keys,qref,missing,ff,ex)
        h0=c0.reshape(-1,4).sum(axis=1);h1=c1.reshape(-1,4).sum(axis=1)
        info={'source':source,'month':mon,'case':name,'source_age_min_ms':age,'source_min_observed_30s_quotes':count,
            'max_source_and_fill_spread_raw':cap,'spread<=1p2_past15s_mean':stable,'past_bid_ask_coherent3s':flow,
            'historical_v5_300s_warmup_UNCHANGED':False,
            'actual_lag_ms':100,'source_future_action_winners':len(ff),'candidate_both_side_tested':len(allcodes),
            'tested_nonwinning_stop':int((allcodes==0).sum()),'tested_nonwinning_timeout':int((allcodes==2).sum()),
            'source_censored':int((allcodes==-3).sum()),
            'R9_SYNTH_monthly_reference':int(qref.sum()),'future_selected_monthly_trade_count':len(futuref),
            'quarter_active_total':int(active.sum()),'quarter_quota_met_before':int(((c0>=qref)&active).sum()),
            'quarter_quota_met_after':int(((c1>=qref)&active).sum()),
            'hour_active_total':int((href>0).sum()),'hour_quota_met_before':int(((h0>=href)&(href>0)).sum()),
            'hour_quota_met_after':int(((h1>=href)&(href>0)).sum()),
            'blind_OOS_and_cash_PNL_unverified':True,'future_privileged_not_asof_side_policy':True}
        outcomes.append(info)
        for i,row in enumerate(refs['rows']):
            quarters.append({'source':source,'month':mon,'case':name,'utc_quarter':row['utc_quarter'],
              'R9_SYNTH_source_quarter_reference':int(qref[i]),'old_future_oracle_count':int(c0[i]),
              'new_future_oracle_count':int(c1[i]),'quarter_pass':int(c1[i]>=qref[i]) if active[i] else '',
              'experimental_cold_history_not_original':True})
        for i in range(len(href)):
            hours.append({'source':source,'month':mon,'case':name,'utc_hour':refs['rows'][4*i]['utc_hour'],
              'R9_SYNTH_source_hour_ref':int(href[i]),'R21_future_oracle_hour_count':int(h1[i]),
              'hour_pass':int(h1[i]>=href[i]) if href[i] else ''})
        for i in range(len(qref)//96):
            sl=slice(i*96,(i+1)*96);ref=int(qref[sl].sum());v=int(c1[sl].sum())
            days.append({'source':source,'month':mon,'case':name,'utc_date':refs['rows'][i*96]['utc_quarter'][:10],
              'R9_SYNTH_source_day_ref':ref,'R21_future_oracle_day_count':v,'day_pass':int(v>=ref) if ref else '',
              'quarter_active':int(active[sl].sum()),'quarter_pass':int((active[sl]&(c1[sl]>=qref[sl])).sum())})
        npzfields[name+'__new_future_winner_fill']=ff
        npzfields[name+'__new_future_winner_exit']=ex
        npzfields[name+'__new_future_winner_SIDE_OFFLINE']=sd
        npzfields[name+'__exchanged_global_full_schedule_fill']=futuref
        npzfields[name+'__exchanged_global_full_schedule_exit']=futuree
        print(source,mon,name,'future winners',len(ff),'Q',info['quarter_quota_met_after'],'H',info['hour_quota_met_after'],flush=True)
    out=LAB/'results';out.mkdir(parents=True,exist_ok=True);head=f'R21E_{source}_{mon}'
    csvpaths=[]
    for title,rs in [('SCENARIOS',outcomes),('FULL_UTC_QUARTERS',quarters),('FULL_UTC_HOURS',hours),('FULL_UTC_DAYS',days)]:
        dst=out/(head+'_'+title+'.csv');csvpaths.append(dst)
        with dst.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
    if trial is None:trial={}
    npzp=out/(head+'_ALL_BIDASK_SIDE_SOURCE_ORDINALS_WIN_STOP_TIMEOUT_CENSOR.npz')
    np.savez_compressed(npzp,**{k:v for k,v in trial.items() if isinstance(v,np.ndarray)},**npzfields)
    rec={'source':source,'month':mon,'source_SHA256':p.r18.PINS[source][mon],
        'original_R9_SYNTH_ref_SHA256':refs['sha256'],'all_source_quote_rows':len(t),
        'source_R19S3_original_missing_quarters':len(missing),'full_month_utc_quarters':len(qref),
        'experiments':outcomes,'actual_source_candidate_all_side_lossless_member':npzp.name,
        'outputs':{x.name:{'sha256':p.sha(x),'bytes':x.stat().st_size} for x in [*csvpaths,npzp]},
        'no_fabricated_fills':True,'all_full_source_hour_day_quarters':True,
        'no_asof_pnl_or_skill_claim':True,'source_verified':input_rec}
    (out/(head+'_FULL_RECEIPT.json')).write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
    return rec

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--source',required=True,choices=('DUKASCOPY_RAW','MT5_BROKER_EXPORT'))
    pa.add_argument('--month',required=True,choices=('01','02','06','07'));n=pa.parse_args();run(n.source,n.month)
