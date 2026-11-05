"""H9 additive hindsight-teacher analysis on frozen H8 source labels + original XAUUSD ticks.

HINDSIGHT ONLY: future event labels drive side/time selection; never feed any of
this file's future outcomes into an online EA. SOURCE PRICE IS NOT CASH PNL.
Original H8 quote gap / actual fill / stop contract is reused unmodified.
"""
from __future__ import annotations
import csv, hashlib, io, json, time, zipfile, datetime, pathlib, sys
import numpy as np
import pandas as pd
from numba import njit

BASE=pathlib.Path('/mnt/data')
ROOT=BASE/'R9V2_H9_CORRECT_SIDE_RESEARCH_20261105'
ORIGINAL=BASE/'XAUUSD_DUKAS_2026_01_ticks.csv.gz'
H8ZIP=BASE/'R28_H8_DUKASCOPY_RAW_01_ALL_SIX_H15_H60_SPREAD_ADAPT_HINDSIGHT_UTC_AND_ORDINALS.zip'
PIN='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
SOURCE='DUKASCOPY_RAW';MONTH='01';EXPECTED_R9=27980

def sha_file(p):
    with open(p,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def load():
    assert sha_file(ORIGINAL)==PIN, 'ORIGINAL SOURCE SHA DRIFT'
    d=pd.read_csv(ORIGINAL,usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    assert list(d.columns)==['timestamp_ms_utc','ask_raw','bid_raw']
    t=d['timestamp_ms_utc'].to_numpy(copy=True);a=d['ask_raw'].to_numpy(copy=True);b=d['bid_raw'].to_numpy(copy=True)
    del d
    assert len(t)==9135062,(len(t),'expected original raw source count')
    assert np.all(t[1:]>=t[:-1]), 'QUOTE ORDER INVALID; NO RESORT'
    assert np.all(a>=b), 'CROSSED SOURCE QUOTE; NO SILENT CLEANING'
    with zipfile.ZipFile(H8ZIP) as z:
        assert z.testzip() is None
        manifest=json.loads(z.read('sha256_member_manifest.json'))
        for k,v in manifest.items():
            assert hashlib.sha256(z.read(k)).hexdigest()==v['sha256'],(k,'member SHA mismatch')
        labels=next(x for x in z.namelist() if x.endswith('_DUAL_SIDE_EARLY_MID_AND_LIQ_SOURCE_ORDINAL_LABELS.npz'))
        with np.load(io.BytesIO(z.read(labels)),allow_pickle=False) as nz:
            signal=nz['signal_ordinal'];fill=nz['fill_ordinal'];events=nz['firstpassage_events'];stop=nz['source_spread_aware_stop_limit_raw'];censor=nz['censor_gap_ordinal']
        csvname=next(x for x in z.namelist() if 'H8_LIQ_NET030_H60_STOP_ADAPT_ALL_UTC_QUARTER_HOUR_DAY' in x)
        rr=list(csv.DictReader(io.StringIO(z.read(csvname).decode())))
        ref=np.asarray([int(row['r9_original_synth_volume_ref']) for row in rr if row['kind']=='quarter'],dtype=np.int32)
        old=next(x for x in z.namelist() if 'H8_LIQ_NET030_H60_STOP_ADAPT_FUTURE_WINNER_SELECTED_QUOTE_ORDINALS' in x)
        with np.load(io.BytesIO(z.read(old)),allow_pickle=False) as nz: previous=nz['selected']
        receipt=json.loads(z.read(next(x for x in z.namelist() if x.endswith('ALL_SCENARIOS_ATOMIC_RECEIPT.json'))))
    assert len(signal)==1512178 and events.shape==(len(signal),2,6)
    assert len(ref)==2976 and int(ref.sum())==EXPECTED_R9
    assert np.all((fill[fill>=0]>signal[fill>=0]))
    ok=fill>=0
    assert np.all(t[fill[ok].astype(np.int64)]>=t[signal[ok].astype(np.int64)]+100), 'FILL NOT +100ms'
    assert np.count_nonzero(ok)==1431033
    assert np.count_nonzero(stop>=0)==1336255
    # Independent original H8 reference reproduction from source ordinals and actual quoted prices.
    j,s,f,e=previous.T.astype(np.int64)
    pnl=np.where(s==0,b[e].astype(np.int64)-a[f]-20,b[f].astype(np.int64)-a[e]-20)
    assert len(j)==97328 and int(pnl.sum())==40788063
    assert np.all(t[e]>t[f])
    assert np.all(t[f][1:]>t[e][:-1])
    q0=int(datetime.datetime(2026,1,1,tzinfo=datetime.timezone.utc).timestamp()*1000)
    q=((t[f]-q0)//900000).astype(int)
    replay=np.bincount(q,minlength=2976)
    oldq=np.asarray([int(row['future_selected_count']) for row in rr if row['kind']=='quarter'])
    assert np.array_equal(replay,oldq),'H8 ORDINAL CALENDAR JOIN FAILED'
    print('SOURCE_VERIFIED',len(t),len(signal),'H8_PRIOR_ORACLE_REPLAY',len(previous),int(pnl.sum()),'R9',int(ref.sum()),flush=True)
    return t,b,a,signal,fill,events,stop,censor,ref,q0

@njit(cache=False)
def strict_asof_teacher_extra_target(t,b,a,fill,events,stop,stage_eligible):
    """H9 ORIGINAL SOURCE EXTENSION: exact first TP3,TP5 observed within <30s.
    Iterate only candidates with original H8 +.50 and first-direction stage eligibility.
    All labels FUTURE: not real-time signals.
    Output ordinal of first TP3/TP5 or -1 plus pre-TP liquidation MAE in raw units.
    """
    n=len(fill)
    out=np.full((n,2,2),-1,np.int32)
    min_before=np.zeros((n,2,2),np.int32)
    for j in range(n):
        f=int(fill[j])
        if f<0 or stop[j]<0:continue
        for side in range(2):
            if not stage_eligible[j,side]:continue
            half=events[j,side,4]
            if half<0 or t[half]-t[f]>=30000:continue
            st=events[j,side,5]
            if st>=0 and st<=half:continue
            minimum=0
            k=f
            while k<len(t):
                if k>f and t[k]-t[k-1]>15000:break
                if t[k]-t[f]>=30000:break
                net=(b[k]-a[f]-20) if side==0 else (b[f]-a[k]-20)
                if net<minimum:minimum=net
                if net<=-stop[j]:break
                if net>=3000 and out[j,side,0]<0:
                    out[j,side,0]=k
                    min_before[j,side,0]=minimum
                if net>=5000:
                    out[j,side,1]=k
                    min_before[j,side,1]=minimum
                    break
                k+=1
    return out,min_before

@njit(cache=False)
def selected_mae(t,b,a,fl,ex,side):
    m=np.empty(len(fl),np.int32)
    for j in range(len(fl)):
        f=int(fl[j]);e=int(ex[j]);s=int(side[j]);v=0
        for k in range(f,e+1):
            net=(b[k]-a[f]-20) if s==0 else (b[f]-a[k]-20)
            if net<v:v=net
        m[j]=v
    return m

def select_teacher(t, b, a, fill, ev, stop, stage, target_index, horizon, q0, ref, name, rearm=0, extra=None, mae_extra=None):
    n=len(fill)
    if extra is None:
        tg=ev[:,:,target_index]
    else:
        tg=extra
    finite=(tg>=0)&(fill[:,None]>=0)&(stop[:,None]>=0)
    rows,side=np.where(finite & stage)
    if len(rows)==0:
        return empty_result(name,ref)
    fr=fill[rows].astype(np.int64);er=tg[rows,side].astype(np.int64)
    valid=(t[er]>t[fr]) & ((t[er]-t[fr])<horizon)
    st=ev[rows,side,5]
    valid &= (st<0)|(er<st)
    rows=rows[valid];side=side[valid];fr=fr[valid];er=er[valid]
    if not len(rows):return empty_result(name,ref)
    order=np.argsort(t[er],kind='stable')
    rows=rows[order];side=side[order];fr=fr[order];er=er[order]
    idx=[]; last=-9223372036854775807
    for k,(f,e) in enumerate(zip(fr,er)):
        if int(t[f])<=last+rearm:continue
        idx.append(k);last=int(t[e])
    idx=np.asarray(idx,dtype=np.int64)
    rows=rows[idx];side=side[idx];fr=fr[idx];er=er[idx]
    assert np.all(t[fr][1:]>t[er][:-1]),'GLOBAL CHRONOLOGY/OVERLAP FAIL'
    net=np.where(side==0,b[er].astype(np.int64)-a[fr]-20,b[fr].astype(np.int64)-a[er]-20)
    min_target={2:100,3:300,4:500}.get(target_index,3000 if 'TP3000' in name else 5000)
    assert np.all(net>=min_target),(name,int(net.min()),min_target)
    assert np.all(t[er]-t[fr]<horizon)
    # Complete UTC original month, every active and reference-zero quarter kept.
    qq=((t[fr]-q0)//900000).astype(np.int32)
    assert np.all((qq>=0)&(qq<len(ref)))
    counts=np.bincount(qq,minlength=len(ref)).astype(np.int32)
    net_q=np.bincount(qq,weights=net,minlength=len(ref)).round().astype(np.int64)
    stat={'scenario':name,'source':SOURCE,'month':MONTH,'future_selected_count':int(len(rows)),'gross_future_selected_before_global_nonoverlap':int(len(valid)),
          'source_quote_net_raw':int(net.sum()),'source_quote_net_price_units':round(int(net.sum())/1000,3),
          'min_selected_net_price_units':float(net.min())/1000,'median_exit_duration_ms':float(np.median(t[er]-t[fr])),
          'p90_exit_duration_ms':float(np.quantile(t[er]-t[fr],.9))}
    for key,k in (('quarter',1),('hour',4),('day',96)):
        r=ref.reshape(-1,k).sum(1);c=counts.reshape(-1,k).sum(1);npnl=net_q.reshape(-1,k).sum(1);active=r>0
        stat[key]={
        'total_periods':int(len(r)),'reference_active_periods':int(active.sum()),'positive_active_periods':int(np.count_nonzero(active & (npnl>0))),
        'positive_active_ratio':round(float(np.mean(npnl[active]>0)),6) if active.any() else None,
        'nonpositive_active_periods':int(np.count_nonzero(active&(npnl<=0))),
        'volume_quota_active_periods':int(np.count_nonzero(active&(c>=r))),
        'positive_AND_volume_quota_active_periods':int(np.count_nonzero(active&(npnl>0)&(c>=r))),
        'positive_full_calendar_periods':int(np.count_nonzero(npnl>0)),
        'reference_target_volume':int(r.sum()),'hindsight_trade_count':int(c.sum()),
        }
    stat['all_active_days_positive']=stat['day']['positive_active_periods']==stat['day']['reference_active_periods']
    stat['at_least_90pct_active_hours_positive']=stat['hour']['positive_active_ratio']>=.9
    stat['at_least_80pct_active_quarters_positive']=stat['quarter']['positive_active_ratio']>=.8
    if mae_extra is not None:
        vals=mae_extra[rows,side]
        stat['mae_quote_price_p50']=float(np.median(vals))/1000
        stat['mae_quote_price_p90_loss']=float(np.quantile(vals,.1))/1000
    sample=np.column_stack((rows,side,fr,er,net)).astype(np.int64)
    # Persist original interval ordinals for exact future audits; full calendar CSV all UTC rows.
    np.savez_compressed(ROOT/'results'/(name+'_DUKASCOPY_01_ORIGINAL_SOURCE_QUOTE_ORDINALS.npz'),selected=sample)
    with open(ROOT/'results'/(name+'_ALL_UTC_QUARTER_HOUR_DAY.csv'),'w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['source','month','scenario','kind','utc_start','r9_original_synth_volume_ref','teacher_selected_count','source_quoted_net_raw','original_R9_active','period_positive','volume_quota_met','future_privileged'])
        for kind,k in (('quarter',1),('hour',4),('day',96)):
            r=ref.reshape(-1,k).sum(1);c=counts.reshape(-1,k).sum(1);nn=net_q.reshape(-1,k).sum(1)
            for period in range(len(r)):
                utc=datetime.datetime.fromtimestamp((q0+period*k*900000)/1000,datetime.timezone.utc).isoformat()
                writer.writerow([SOURCE,MONTH,name,kind,utc,int(r[period]),int(c[period]),int(nn[period]),int(r[period]>0),int(nn[period]>0),int(r[period]>0 and c[period]>=r[period]),True])
    return stat

def empty_result(name,ref):
    x={'scenario':name,'source':SOURCE,'month':MONTH,'future_selected_count':0,'source_quote_net_raw':0}
    for k,n in (('quarter',1),('hour',4),('day',96)):
        r=ref.reshape(-1,n).sum(1);act=int((r>0).sum()); x[k]={'total_periods':len(r),'reference_active_periods':act,'positive_active_periods':0,'positive_active_ratio':0.,'nonpositive_active_periods':act,'volume_quota_active_periods':0,'positive_AND_volume_quota_active_periods':0,'reference_target_volume':int(r.sum()),'hindsight_trade_count':0}
    x.update(all_active_days_positive=False,at_least_90pct_active_hours_positive=False,at_least_80pct_active_quarters_positive=False)
    return x

def run():
    tic=time.monotonic()
    t,b,a,signal,fill,ev,stop,censor,ref,q0=load()
    ok=fill>=0;early=ev[:,:,0];adverse=ev[:,:,1]
    stage=(early>=0)&((adverse<0)|(early<adverse))
    stage &= (fill[:,None]>=0)&(stop[:,None]>=0)
    good_idx=np.maximum(early,0)
    stage &= (t[good_idx]-t[np.maximum(fill[:,None],0)]<=15000)
    # Exclude observations with an earlier quote gap censor, source-end already impossible in H8 labels.
    stage &= (censor[:,None]<0)|(early<censor[:,None])
    decision_population={'eligible_first_second_signals':len(signal),'valid_plus100ms_fills':int(ok.sum()),'spread_adaptive_fills':int((stop>=0).sum()),
       'both_action_side_pairs_considered':int(2*len(signal)),
       'first15_favorable_before_adverse_side_pairs':int(stage.sum()),
       'first15_wrong_adverse_before_favorable_side_pairs':int(((adverse>=0)&((early<0)|(adverse<early))&(stop[:,None]>=0)).sum()),
       'first15_no_decisive_favorable_side_pairs':int(((early<0)&(stop[:,None]>=0)).sum()),
       'source_raw_sha':sha_file(ORIGINAL)}
    print('POPULATION',json.dumps(decision_population),flush=True)
    results=[]
    for label,col in [('TP0100',2),('TP0300',3),('TP0500',4)]:
        name=f'H9_JAN_FIRST15_CORRECT_LIQ_{label}_EXIT_LT30_RISK_ADAPT'
        s=select_teacher(t,b,a,fill,ev,stop,stage,col,30000,q0,ref,name)
        print('CASE',name,json.dumps({k:s[k] for k in ('future_selected_count','quarter','hour','day')}),flush=True)
        results.append(s)
    # Essential null: first .50 TP <30 without early first15 directional purity.
    comparison=select_teacher(t,b,a,fill,ev,stop,np.ones_like(stage,dtype=bool),4,30000,q0,ref,'H9_NEGCTRL_NO_FIRST15_STAGE_TP0500_LT30')
    results.append(comparison)
    # Rapid strict TP3/5: reuses H8 +.50 price-first and source gap-filtered candidates; no re-labeling of old data.
    extreme,mae=strict_asof_teacher_extra_target(t,b,a,fill,ev,stop,stage)
    for k,tag in [(0,'TP3000'),(1,'TP5000')]:
        name=f'H9_JAN_FIRST15_CORRECT_LIQ_{tag}_EXIT_LT30_RISK_ADAPT'
        s=select_teacher(t,b,a,fill,ev,stop,stage,99,30000,q0,ref,name,extra=extreme[:,:,k],mae_extra=mae[:,:,k])
        results.append(s)
        print('CASE',name,json.dumps({k:s[k] for k in ('future_selected_count','quarter','hour','day')}),flush=True)
    data={'classification':'FUTURE_PRIVILEGED_SOURCE_EXACT_ONE_SOURCE_MONTH_HINDSIGHT_ONLY',
         'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'source':SOURCE,'month':MONTH,'future_student_not_trained':True,'no_real_coinexx_cash_or_contract_approval':True,
         'raw_source_sha256':sha_file(ORIGINAL),'h8_zip_sha256':sha_file(H8ZIP),
         'elapsed_s':round(time.monotonic()-tic,2),'source_populations':decision_population,'cases':results}
    p=ROOT/'results'/'H9_JAN_ALL_SIX_CASES_FULL_UTC_AND_FIRST15_CORRECT_SOURCE_REPORT.json';p.write_text(json.dumps(data,indent=2)+'\n')
    print('FINAL',str(p),'elapsed',data['elapsed_s'],flush=True)
    return data

if __name__=='__main__':run()
