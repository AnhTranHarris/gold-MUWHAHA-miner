"""R11 exhaustive quote-ordinal one-position replay of MONTH-FITTED causal student.

NEVER substitutes hindsight future labels into prediction. Every fitted model
is self-fitted on the exact month being scored, so results are contaminated
resubstitution, NOT out-of-sample and NOT a deployment eligibility claim.
Known H1V2 original R9 exact 30s counterfactual exit matrix is used only
AFTER a candidate was selected on fitted as-of model outputs.
"""
from __future__ import annotations
import argparse,hashlib,json,math,pathlib,time
import numpy as np
import pandas as pd
from numba import njit
from entry_contract import PINNED,MONTHS,SYNTH,candidate_v5,verify_file_sha
from h1v2_teacher import read_ticks

ROOT=pathlib.Path('/mnt/data/h1v2_r11_lab')
# Separate mandatory strict-gate probe and explicitly NON-QUALIFYING diagnostic cuts.
POLICIES=(
  ('ELIGIBLE_GOOD80_BAD20_EV0_MARGIN08',.80,.20,0.,.08),
  ('DIAGNOSTIC_GOOD50_BAD30_EV0_MARGIN08',.50,.30,0.,.08),
  ('DIAGNOSTIC_GOOD25_BAD40_EV0_MARGIN08',.25,.40,0.,.08),
  ('DIAGNOSTIC_GOOD10_BAD50_EV0_MARGIN08',.10,.50,0.,.08),
)
FRACTIONS=(.01,.05,.25)

@njit(cache=True)
def replay_selected(rows,sides,entry_ix,exit_ix,net,code,first_ms,extra_cost=0.):
    # row ordinal ascending, side=0 BUY or 1 SELL; last exit inclusive.
    sel=np.empty(len(rows),np.int64);ss=np.empty(len(rows),np.int8)
    good=wrong=neutral=unknown=0;count=0;cash=equity=peak=maxdd=0.
    last=-1;first15=0
    for i in range(len(rows)):
        r=rows[i];side=sides[i]
        if side not in (0,1):continue
        entry=entry_ix[r]
        if entry<=last:continue
        end=exit_ix[r,side]
        value=net[r,side]
        if end<=entry or not np.isfinite(value):
            unknown+=1;continue
        last=end
        sel[count]=r;ss[count]=side;count+=1
        pnl=value-extra_cost
        cash+=pnl;equity+=pnl
        if equity>peak:peak=equity
        if peak-equity>maxdd:maxdd=peak-equity
        if code[r,side]==1:
            good+=1
            if first_ms[r,side]<=15000:first15+=1
        elif code[r,side]==-1:wrong+=1
        else:neutral+=1
    return sel[:count],ss[:count],good,wrong,neutral,unknown,cash,maxdd,first15


def _cal(t,r,s,code,net,first,exitix,raw_ix,extra):
    if len(r)==0:return {'utc_day':[],'iso_week':[]}
    idx=raw_ix[r];end=exitix[r,s]
    times=pd.to_datetime(t[idx],unit='ms',utc=True)
    df=pd.DataFrame({'utc_day':times.strftime('%Y-%m-%d'),'iso_week':times.strftime('%G-W%V'),
      'entry_ms':t[idx],'exit_ms':t[end],
      'BUY':s==0,'SELL':s==1,'good':code[r,s]==1,'bad':code[r,s]==-1,
      'first15':(code[r,s]==1)&(first[r,s]>=0)&(first[r,s]<=15000),
      'net':net[r,s].astype(np.float64)-extra})
    result={}
    for dim in ('utc_day','iso_week'):
        rec=[]
        for k,g in df.groupby(dim,sort=True):
            pnl=g.net.to_numpy()
            rec.append({'utc_period':str(k),'real_selected_source_entries':len(g),
              'strict_r9_correct':int(g.good.sum()),'original_bad':int(g.bad.sum()),
              'original_neutral':int(len(g)-g.good.sum()-g.bad.sum()),
              'strict_r9_first15_correct':int(g.first15.sum()),
              'strict_correct_fraction':float(g.good.mean()),
              'first15_correct_fraction':float(g.first15.mean()),
              'net_after_extra_fee':float(pnl.sum()),
              'negative_trade_count':int((pnl<0).sum()),
              'buy_count':int(g.BUY.sum()),'sell_count':int(g.SELL.sum()),
              'median_hold_ms':float(np.median(g.exit_ms-g.entry_ms))})
        result[dim]=rec
    return result


def run_month(mon,raw_root='/mnt/data',teacher_dir=ROOT/'rebuilt_teacher',models=ROOT/'models',output=ROOT/'student_replay'):
    if mon not in MONTHS:raise ValueError(mon)
    start=time.monotonic();raw=pathlib.Path(raw_root)/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
    lab=pathlib.Path(teacher_dir)/f'h1v2_dukascopy_{mon}_oracle_labels.npz'
    ori=json.loads((pathlib.Path(teacher_dir)/f'h1v2_dukascopy_{mon}_receipt.json').read_text())
    verify_file_sha(raw,PINNED[mon]);verify_file_sha(lab,ori['teacher_labels_sha256'])
    model_receipts={}
    probs=[]
    for side in ('BUY','SELL'):
        k=json.loads((pathlib.Path(models)/f'R11_{mon}_{side}_ALLPOP_IN_SAMPLE_FIT_RECEIPT.json').read_text())
        if k['source_raw_sha256']!=PINNED[mon] or k['original_label_sha256']!=ori['teacher_labels_sha256'] or k['exact_month_in_sample_training']!=True:
            raise ValueError('student model/teacher source mismatch')
        p=pathlib.Path(models)/k['full_probability_file'];m=pathlib.Path(models)/k['model_file']
        verify_file_sha(p,k['full_probability_file_sha256']);verify_file_sha(m,k['model_sha256'])
        z=np.load(p,mmap_mode='r')
        probs.append(z)
        model_receipts[side]={'model_sha256':k['model_sha256'],'probability_sha256':k['full_probability_file_sha256'],
                             'causal_feature_sha256':k['causal_feature_sha256'],'trees':k['fitted_boosting_rounds']}
    t,b,a=read_ticks(raw);v5=candidate_v5(t,b,a)
    if len(v5)!=len(probs[0]) or len(v5)!=len(probs[1]):raise ValueError('full month event count mismatch')
    with np.load(lab,allow_pickle=False) as z:
       keep=np.isin(z['tick_index'],v5,assume_unique=True)
       ix=z['tick_index'][keep].copy()
       if not np.array_equal(ix,v5):raise ValueError('teacher ordinal not v5 exact')
       c=z['code'][keep].copy();net=z['net'][keep].copy();exits=z['exit_tick_index'][keep].copy();first=z['first_event_ms'][keep].copy()
    # Reconstruct SIDE-SPECIFIC in-sample economic class means as training
    # metadata; not valid OOS / does not use future outcomes for each decision.
    mus=[]
    for s in (0,1):
        ok=(exits[:,s]>=0)&np.isfinite(net[:,s])
        mus.append([float(net[(c[:,s]==k)&ok,s].mean()) for k in (-1,0,1)])
    means=np.asarray(mus,dtype=np.float64)
    pbu=np.asarray(probs[0],np.float32);psel=np.asarray(probs[1],np.float32)
    if not (np.isfinite(pbu).all() and np.isfinite(psel).all()):raise ValueError('nonfinite frozen model scores')
    EV=np.stack([pbu@means[0],psel@means[1]],axis=1)
    PGOOD=np.stack([pbu[:,2],psel[:,2]],axis=1)
    PBAD=np.stack([pbu[:,0],psel[:,0]],axis=1)
    if np.any(np.abs(pbu.sum(axis=1)-1)>1e-4) or np.any(np.abs(psel.sum(axis=1)-1)>1e-4):raise ValueError('probability mass drift')
    root=pathlib.Path(output)/f'month_{mon}';root.mkdir(parents=True,exist_ok=True)
    result={'month':mon,'full_original_source_quote_count':len(t),'v5_original_candidate_count':len(ix),
       'source_raw_sha256':PINNED[mon],'source_original_teacher_sha256':ori['teacher_labels_sha256'],
       'student_model_receipts':model_receipts,
       'training_only_class_mean_net_by_side':{'BUY':means[0].tolist(),'SELL':means[1].tolist()},
       'fitted_probability_range':{'BUY_GOOD':[float(x) for x in np.quantile(PGOOD[:,0],[0,.25,.5,.75,.95,.99,1])],
                                   'SELL_GOOD':[float(x) for x in np.quantile(PGOOD[:,1],[0,.25,.5,.75,.95,.99,1])]},
       'score_definitions':{'class_order':'0 BAD,1 NEUTRAL,2 STRICT_GOOD',
             'eligibility_first':'per-side p_good lower threshold, p_bad upper threshold, expected_nets > 0; side rivalry only if both eligible',
             'economic_proxy':'training-only class net means weighted by fit-month model posterior, no claim of calibration',
             'strict_min80':'p_good >= .80 and p_bad<=.20; time correlated data => these are NOT Wilson lower/upper confidence bounds; no true strict acceptance proof'},
       'experiments':{},'scientific_status':'FULL_SOURCE_ONE_POSITION_IN_SAMPLE_STUDENT_REPLAY_UNQUALIFIED'}
    for name,pmin,bmax,evmin,margin in POLICIES:
        good=(PGOOD>=pmin)&(PBAD<=bmax)&(EV>evmin)
        both=good[:,0]&good[:,1]
        side=np.full(len(ix),-1,np.int8)
        side[good[:,0]&~good[:,1]]=0
        side[good[:,1]&~good[:,0]]=1
        side[both & (EV[:,0]-EV[:,1]>margin)]=0
        side[both & (EV[:,1]-EV[:,0]>margin)]=1
        rows=np.flatnonzero(side>=0);dirs=side[rows]
        result['experiments'][name]=_write_policy(root,mon,name,rows,dirs,ix,t,exits,net,c,first,
                                 cutoff={'pmin':pmin,'bmax':bmax,'expected_net_min':evmin,'both_eligible_min_usd_margin':margin})
        print(mon,name,result['experiments'][name]['trades'],result['experiments'][name]['strict_precision'],flush=True)
    # Full-population per-month score percentile selection is hindsight-fit
    # RESUBSTITUTION ONLY. Ties and fractions fixed; ignore economic admission
    # to expose whether the model contains any ranking signal at all.
    side=np.argmax(EV,axis=1).astype(np.int8)
    score=EV[np.arange(len(ix)),side]
    for frac in FRACTIONS:
        cut=float(np.quantile(score,1.-frac))
        rows=np.flatnonzero(score>=cut)
        name=f'DIAGNOSTIC_TOP{int(frac*100):02d}PCT_FITMONTH_IN_SAMPLE_NO_ECONOMIC_GATES'
        result['experiments'][name]=_write_policy(root,mon,name,rows,side[rows],ix,t,exits,net,c,first,
                                        cutoff={'top_fitmonth_fraction':frac,'empirical_score_cutoff':cut})
        print(mon,name,result['experiments'][name]['trades'],result['experiments'][name]['strict_precision'],flush=True)
    result['runtime_s']=round(time.monotonic()-start,2)
    (root/f'R11_{mon}_FULLMONTH_STUDENT_IN_SAMPLE_ALLPOLICIES.json').write_text(json.dumps(result,indent=2))
    return result


def _write_policy(root,mon,name,rows,dirs,ix,t,exits,net,c,first,cutoff):
    selected,sides,good,bad,neu,unsc,pnl,dd,n15=replay_selected(rows.astype(np.int64),dirs.astype(np.int8),ix,exits,net,c,first)
    out={'name':name,'selection_conditions':cutoff,
      'candidate_signals':int(len(rows)),'replayed_nonoverlapping_original_r9_exits':int(len(selected)),
      'unscored_source_end_entries':int(unsc),'trades':int(len(selected)),'strict_good':int(good),
      'wrong':int(bad),'neutral':int(neu),'strict_first15_good':int(n15),
      'strict_precision':float(good/len(selected)) if len(selected) else None,
      'strict_first15_precision':float(n15/len(selected)) if len(selected) else None,
      'modeled_net_original_fees':round(float(pnl),4),'closed_equity_max_drawdown':round(float(dd),4),
      'monthly_85pct_reference':int(math.ceil(.85*SYNTH[mon])),
      'volume_floor_pass':len(selected)>=math.ceil(.85*SYNTH[mon]),
      '80pct_first15_and_30_aggregate':bool(len(selected) and good/len(selected)>=.8 and n15/len(selected)>=.8),
      'status':'IN_SAMPLE_STUDENT_DIAGNOSTIC_NOT_CAUSALLY_VALIDATED'}
    source=ix[selected];end=exits[selected,sides] if len(selected) else np.zeros(0,np.int64)
    dest=root/f'{name}_FULL_SELECTED_TRADES.npz'
    np.savez_compressed(dest,
       eligible_row=selected,source_entry_tick_ix=source,source_exit_tick_ix=end,
       entry_utc_ms=t[source],exit_utc_ms=t[end],side=np.where(sides==0,1,-1),
       code=c[selected,sides] if len(selected) else np.zeros(0,np.int8),
       net=net[selected,sides] if len(selected) else np.zeros(0,np.float32),
       first_favorable_ms=first[selected,sides] if len(selected) else np.zeros(0,np.int32))
    with dest.open('rb') as f:out['exact_trace_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
    out['exact_trace_file']=dest.name
    cal=_cal(t,selected,sides,c,net,first,exits,ix,0.)
    for dim,p in cal.items():
        cp=root/f'{name}_EXACT_{dim.upper()}_HOLDOUT_NOTE.json'
        cp.write_text(json.dumps({'month':mon,'policy':name,'in_sample':True,'period':dim,'cells':p},indent=2))
        out[f'complete_{dim}_file']=cp.name
    (root/f'{name}_COMPLETE_RECEIPT.json').write_text(json.dumps(out,indent=2))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--month',required=True,choices=MONTHS)
    a=p.parse_args();r=run_month(a.month)
    print(json.dumps({'month':a.month,'science':r['scientific_status'],'experiments':{k:{'count':v['trades'],'precision':v['strict_precision'],'net':v['modeled_net_original_fees']} for k,v in r['experiments'].items()},'runtime_s':r['runtime_s']},indent=2),flush=True)
