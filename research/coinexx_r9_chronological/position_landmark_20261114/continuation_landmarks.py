"""R9 Coinexx 1s / 3s position landmark and original-policy continuation research.

Only existing original Coinexx source gzip and frozen original R9 ledger/model
archives are used. Read-only inputs; one bounded JSON scorecard, no tick copies.
P5 model is original-side and exact source-ordinal, as-of ENTRY, not refreshed at
landmarks. Outcomes are realized ONLY under unchanged original R9 stops, NOT
counterfactual strategy execution. K/C are explicit, hypothetical account cash.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import warnings
import zipfile
import zipimport
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

MONTHS = (5,6,7,8,9)
PIN_MODELS = {
 5:'48c3e3898aab1a78cc5f3b0fec45137af23f2267a4ef665a73eb1e1c431ed661',
 6:'bdeb8c4ccc8b6523c3c2cf1185104162c5bf2e3f45271c42c521e50e660ec121',
 7:'bd4c886a470cecac663f5cb71889f195148fa2ef3da932cfce02c361c873e1c5',
 8:'b23e84ed6d9d34b68e5496c71304b76c5db8be8b81be85975ea5dcd1f4df830f',
 9:'8d6bb3c41741a2223494a8ec87314e9e8d7ea93634ab83498dd133fe7a187d06',
}
FULL=(
 'R9_M60_FullUniverse_DerivedCache_Part1_Months01-02-03_20261113.zip',
 'R9_M60_FullUniverse_DerivedCache_Part2_Months04-05-06_20261113.zip',
 'R9_M60_FullUniverse_DerivedCache_Part3_Months07-08-09_20261113.zip',
)
EVENT=(
 'R9_M60_Hazard_ExactEvent_Derived_2026_Part1_01to03_20261113.zip',
 'R9_M60_Hazard_ExactEvent_Derived_2026_Part2_04to06_20261113.zip',
 'R9_M60_Hazard_ExactEvent_Derived_2026_Part3_07to09_20261113.zip',
)
PRIORITY='R9_M60_Coinexx_CUSUM_QuoteIntensity_Cache_JanSep_20261113.zip'
LEDGER='R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip'
TRAIN='R9_M60_JanSep_FullTraining_155Features_20261113.zip'
IDX=list(range(14))+list(range(14,117,6))+list(range(117,145,4))+list(range(145,145+77))
FEATURE_COLS=['net_now','sl_distance_cents','spread_now_cents',
              'spread_change_cents','mfe_net','mae_net',
              'signed_1s_mid_move_cents','noise_1s_cents',
              'quote_updates_last_1s','price_path_efficiency',
              'quote_staleness_ms','r9_m5_atr_cents',
              'r9_s1_eff','entry_spread_cents','session','side',
              'rearm','original_entry_model_p5']
CONTEXT_N=len(FEATURE_COLS)-1


def sha256_file(file:Path)->str:
    h=hashlib.sha256()
    with file.open('rb') as f:
        for chunk in iter(lambda:f.read(2**22),b''):h.update(chunk)
    return h.hexdigest()


def load_p5(root:Path, mm:int, old_archive, event_archive, priority_archive,
            train_archive, analytic, ledger:pd.DataFrame) -> np.ndarray:
    m=f'{mm:02d}'
    with np.load(io.BytesIO(old_archive.read(f'full_derived/full_month_2026_{m}.npz')),allow_pickle=False) as old, \
         np.load(io.BytesIO(event_archive.read(f'event_2026_{m}.npz')),allow_pickle=False) as ev, \
         np.load(io.BytesIO(priority_archive.read(f'derived/priority_2026_{m}.npz')),allow_pickle=False) as pr:
        orig=old['entry_ordinals'];t=old['entry_times'];side=old['side'];n=len(side)
        if not (np.array_equal(orig,ev['ordinal']) and np.array_equal(orig,pr['ordinal'])
                and np.array_equal(t,ev['entry']) and np.array_equal(t,pr['entry'])
                and np.array_equal(side,ev['r9_side'])):raise ValueError('Frozen feature ordinal/time/side mismatch '+m)
        if not (np.array_equal(ledger.entry_ordinal.to_numpy(),orig) and
                np.array_equal(ledger.entry_time_msc.to_numpy(),t) and
                np.array_equal(ledger.side.to_numpy(),side)):
            raise ValueError('Ledger entry source ordinal/time/side mismatch '+m)
        joined=np.concatenate((old['features'],ev['features']),axis=1).astype('f4')
        b=joined[:,IDX]
        analytical=analytic(ev['features'],ev['spread'],ev['stop'],ev['target'],side)
        meta=np.stack((side.astype('f4'),np.ones(n,'f4'),ev['stop'],ev['target'],ev['spread']),axis=1)
        features=np.concatenate((b,pr['features'],analytical,meta),axis=1).astype('f4')
        cause=ev['cause'][np.arange(n),np.where(side>0,0,1)]
        hit=ev['hit_ms'][np.arange(n),np.where(side>0,0,1)]
        good=cause!=-1
        y=(cause==1)&(hit>=0)&(hit<=5000)
    if features.shape!=(len(ledger),155):raise ValueError('Wrong source exact 155 dimensions')
    filename=f'models/direct_test_{m}_shadow.joblib'
    raw=train_archive.read(filename)
    if hashlib.sha256(raw).hexdigest()!=PIN_MODELS[mm]:raise ValueError('Frozen classifier SHA tampered '+m)
    model=joblib.load(io.BytesIO(raw))['model']
    if model.n_features_in_!=155:raise ValueError('Wrong model input dimensions')
    p5=model.predict_proba(features)[:,1]
    original=json.loads(train_archive.read(f'outputs/fold_{m}.json'))['models']['direct_5sec']['r9_direction_auc5']
    actual=roc_auc_score(y[good],p5[good])
    if abs(actual-original)>1e-6:raise ValueError(f'Original P5 fold AUC parity broken {m}: {actual} vs {original}')
    return p5


def load_ledger(archive, mm:int) -> pd.DataFrame:
    cols=['entry_ordinal','exit_ordinal','entry_time_msc','exit_time_msc','side',
          'entry_price_u','exit_price_u','net_price_u','reason','spread_u',
          'r9_atr_u','r9_eff','session','rearm']
    df=pd.read_csv(io.BytesIO(archive.read(f'candidate_closes_2026_{mm:02d}.csv.gz')),
            compression='gzip',usecols=cols)
    if not (np.all(np.diff(df.entry_ordinal)>0) and
            np.all(df.exit_ordinal>df.entry_ordinal) and
            np.all(df.exit_time_msc>=df.entry_time_msc)):
        raise ValueError('Ledger time/ordinal violates chronology')
    x=(df.exit_price_u-df.entry_price_u)*df.side
    if not np.array_equal(x.to_numpy(),df.net_price_u.to_numpy()):
        raise ValueError('Ledger cash quote-side result inconsistent')
    return df


def calculate_snapshot(tm:np.ndarray,bid:np.ndarray,ask:np.ndarray,
                       a:int,j:int,side:int,entry:int,initial_sl:int,
                       k:float,c:float)->tuple[float,...]:
    """Only original received quotes at/before index j, never future observations."""
    if not a<j or not 0<bid[j]<=ask[j]:raise ValueError('Invalid alive landmark')
    prices=bid[a:j+1] if side>0 else ask[a:j+1]
    available=int(prices[-1])
    net_now=side*(available-entry)*k/100-c
    gains=side*(prices.astype('int64')-entry)*k/100-c
    best_bid_or_ask=int(prices.max() if side>0 else prices.min())
    if side>0:
        sl=max(initial_sl,best_bid_or_ask-3) if best_bid_or_ask-entry>=10 else initial_sl
        stop_distance=available-sl
    else:
        sl=min(initial_sl,best_bid_or_ask+3) if entry-best_bid_or_ask>=10 else initial_sl
        stop_distance=sl-available
    if stop_distance < 0:raise ValueError('Alive landmark crossed reconstructed R9 protective stop')
    spread=int(ask[j]-bid[j]);spr_change=spread-int(ask[a]-bid[a])
    window=np.searchsorted(tm,tm[j]-1000,side='left')
    window=max(a,int(window))
    mid=(bid[window:j+1].astype('float64')+ask[window:j+1])/2
    midmove=float(side*(mid[-1]-mid[0])) if len(mid)>1 else 0.
    steps=np.diff(mid)
    realized=float(np.sqrt(np.mean(steps**2))) if len(steps) else 0.
    effort=float(abs(mid[-1]-mid[0])/(np.abs(steps).sum()+1e-9)) if len(steps) else 0.
    staleness=int(tm[j]-tm[j-1])
    return (float(net_now),float(stop_distance),float(spread),float(spr_change),
            float(np.max(gains)),float(np.min(gains)),midmove,realized,
            float(max(0,len(mid)-1)),effort,float(staleness))


def capture_landmarks(mm:int,root:Path,monthly_receipt:dict):
    """One input month loaded read-only into three arrays; no tick copy written."""
    path=root/f'XAUUSD_MT5_BROKER_2026_{mm:02d}_ticks_ALL.csv.gz'
    digest=sha256_file(path)
    if digest!=monthly_receipt['source_sha256']:
        raise ValueError(f'Original Coinexx monthly source hash changed month {mm}: {digest}')
    df=pd.read_csv(path,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
    n=len(df)
    if n!=monthly_receipt['rows']:raise ValueError('Coinexx quote row count mismatch')
    tm=df.time_msc.to_numpy(copy=False)
    if np.any(np.diff(tm)<0):raise ValueError('Raw timestamp order corrupted')
    bid=np.rint(df.bid.to_numpy()*100).astype('i4')
    ask=np.rint(df.ask.to_numpy()*100).astype('i4')
    del df
    return tm,bid,ask,digest


def month_rows(mm,ledger,tm,bid,ask,p5,first_global_ordinal,k,c,max_lateness,max_gap):
    n=len(ledger)
    a=ledger.entry_ordinal.to_numpy('int64')-first_global_ordinal
    e=ledger.exit_ordinal.to_numpy('int64')-first_global_ordinal
    if np.any(a<0) or np.any(e>=len(tm)):raise ValueError('Source ordinal index outside original month')
    if not (np.array_equal(tm[a],ledger.entry_time_msc.to_numpy('int64')) and
            np.array_equal(tm[e],ledger.exit_time_msc.to_numpy('int64'))):
        raise ValueError('R9 source-order entry/exit quote timestamp mismatch')
    sides=ledger.side.to_numpy('int32');inprice=ledger.entry_price_u.to_numpy('int32')
    outprice=ledger.exit_price_u.to_numpy('int32')
    if not (np.array_equal(np.where(sides>0,ask[a],bid[a]),inprice) and
            np.array_equal(np.where(sides>0,bid[e],ask[e]),outprice)):
        raise ValueError('R9 source-order executable price mismatch')
    outcomes=ledger.net_price_u.to_numpy('float64')*k/100-c
    result={}
    for lag in (1000,3000):
        target=tm[a]+lag
        j=np.searchsorted(tm,target,'left')
        eligible=(j<e)&(j>a)&(j<len(tm))
        j=np.minimum(j,len(tm)-1)
        lateness=tm[j]-target
        gap=tm[j]-tm[np.maximum(j-1,0)]
        eligible &= (lateness>=0)&(lateness<=max_lateness)&(gap<=max_gap)
        picks=np.flatnonzero(eligible)
        X=np.empty((len(picks),len(FEATURE_COLS)),dtype='f4')
        for ii,r in enumerate(picks):
            ar=int(a[r]);jr=int(j[r]);s=int(sides[r]);entry=int(inprice[r]);sl=(int(bid[ar])-30 if s>0 else int(ask[ar])+30)
            value=calculate_snapshot(tm,bid,ask,ar,jr,s,entry,sl,k,c)
            X[ii,:11]=value
            X[ii,11:]=[float(ledger.r9_atr_u.iloc[r]),float(ledger.r9_eff.iloc[r]),
                       float(ledger.spread_u.iloc[r]),float(ledger.session.iloc[r]),
                       float(s),float(ledger.rearm.iloc[r]),float(p5[r])]
        qcash=X[:,0].astype('float64')
        held_cash=outcomes[picks]
        delta=held_cash-qcash
        result[lag//1000]=dict(X=X,delta=delta,now=qcash,hold=held_cash,
             entry_index=picks,entry_ordinal=ledger.entry_ordinal.to_numpy('int64')[picks],
             entry_time=ledger.entry_time_msc.to_numpy('int64')[picks],
             obs_time=tm[j[picks]],source_ordinal=first_global_ordinal+j[picks],
             total_positions=n,available=int(len(picks)),still_open_at_age=int(np.sum((tm[e]-tm[a])>lag)),
             dropped_stale=int(np.sum((j<e)&(lateness>max_lateness))),
             dropped_gap=int(np.sum((j<e)&(gap>max_gap))))
    return result


def execute(root:Path,output:Path,months=MONTHS,k=1.,c=.20,max_lateness=500,max_gap=2500,cache_dir=None):
    if k<=0 or c<0 or not np.isfinite(k+c):raise ValueError('Invalid cash assumptions')
    with zipfile.ZipFile(root/LEDGER) as led,zipfile.ZipFile(root/PRIORITY) as pr,zipfile.ZipFile(root/TRAIN) as tr:
        receipt=json.loads(led.read('source_receipt.json'))['source_months']
        src=tr.read('frozen_priority/src/signal_features.py')
        if hashlib.sha256(src).hexdigest()!='30ef24f0d8aea3dc21fcd13fec434cee86e80bac9783c454bc95c43be642096c':
            raise ValueError('Original analytic frozen feature source SHA changed')
        analytic=zipimport.zipimporter(str((root/TRAIN).resolve())+'/frozen_priority/src').load_module('signal_features').action_barrier_features
        summaries={};source_checks={}
        for mm in months:
            with zipfile.ZipFile(root/FULL[(mm-1)//3]) as fu,zipfile.ZipFile(root/EVENT[(mm-1)//3]) as ev:
                ledger=load_ledger(led,mm)
                if len(ledger)!=receipt[f'{mm:02d}']['entries']:
                    raise ValueError('Frozen monthly R9 trade count changed')
                p5=load_p5(root,mm,fu,ev,pr,tr,analytic,ledger)
                tm,bid,ask,digest=capture_landmarks(mm,root,receipt[f'{mm:02d}'])
                first=1+sum(receipt[f'{i:02d}']['rows'] for i in range(1,mm))
                data=month_rows(mm,ledger,tm,bid,ask,p5,first,
                                k,c,max_lateness,max_gap)
                if cache_dir is not None:
                    cache_dir.mkdir(parents=True,exist_ok=True)
                    for lag,subset in data.items():
                        np.savez_compressed(cache_dir/f'landmark_{mm:02d}_{lag}s.npz',
                            X=subset['X'],delta=subset['delta'],now=subset['now'],
                            hold=subset['hold'],entry_time=subset['entry_time'],
                            entry_ordinal=subset['entry_ordinal'],source_ordinal=subset['source_ordinal'],
                            total_positions=np.int64(subset['total_positions']))
                summaries[str(mm)]={str(lag):dict(original_positions=d['total_positions'],
                            still_open_at_target=d['still_open_at_age'],
                            measured=d['available'],
                            mean_immediate_cash=float(d['now'].mean()),
                            mean_eventual_original_cash=float(d['hold'].mean()),
                            mean_hold_minus_exit_cash=float(d['delta'].mean()),
                            fraction_hold_better=float(np.mean(d['delta']>0)),
                            mean_stop_distance_cents=float(d['X'][:,1].mean()),
                            med_stop_distance_cents=float(np.median(d['X'][:,1])))
                            for lag,d in data.items()}
                source_checks[f'{mm:02d}']={'sha256':digest,'original_rows':receipt[f'{mm:02d}']['rows'],'positions':len(ledger)}
                print(f"verified month {mm:02d} SHA={digest[:10]} positions={len(ledger)} " +
                      ' '.join(f'{age}s={d["available"]}' for age,d in data.items()),flush=True)
                del ledger,tm,bid,ask,p5
        rows=[]  # separate bounded linear trainer reads compact checked snapshots
    result=dict(status='ORIGINAL_R9_POSITION_SURVIVOR_OBSERVATIONAL_ONLY_NO_POLICY_PNL',
           source='Original Coinexx month gz + source-ordinal R9 completion ledger + 155-feature fold models',
           source_receipt_pinned=True,
           broker_cash_conversion_verified=False,
           source_native_broker_clock_timezone_verified=False,
           K_cash_per_XAU_dollar_assumed=k,extra_roundtrip_cost_assumed=c,
           note='HOLD payoff is factual original R9 exit cash, not action-conditional optimal stop. Exit now marks first exact available quote >= age, with max quote delay. All scored positions are original-policy survivors; selection bias. Missing real MT5 broker fills, fees, governor and rearm effects.',
           max_quote_lateness_ms=max_lateness,max_observed_quote_gap_ms=max_gap,
           by_month=summaries,source_verified=source_checks,walk_forward=rows)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path('/mnt/data'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--months',type=int,nargs='+',default=list(MONTHS))
    p.add_argument('--max-quote-lateness-ms',type=int,default=500)
    p.add_argument('--max-quote-gap-ms',type=int,default=2500)
    p.add_argument('--cache-dir',type=Path)
    p.add_argument('--cash-per-one-xau-dollar',type=float,default=1.)
    p.add_argument('--extra-roundtrip-cost',type=float,default=.20)
    a=p.parse_args()
    execute(a.root,a.output,a.months,a.cash_per_one_xau_dollar,
            a.extra_roundtrip_cost,a.max_quote_lateness_ms,a.max_quote_gap_ms,a.cache_dir)

if __name__=='__main__':main()
