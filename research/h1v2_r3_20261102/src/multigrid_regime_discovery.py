"""R3 multi-grid, session, trend, regime, horizon asymmetric BUY/SELL/WAIT motifs.

Intentionally in-sample teacher discovery. Independent future first-passage
labels used exclusively in fit/evaluation; observed as-of geometry only at
inference. No M1 bars, no original EA or label modification, no on-policy claims.
"""
from __future__ import annotations
import json, math, hashlib
from pathlib import Path
from collections import defaultdict
from true_quote_horizons import feat_classes
import numpy as np
import pandas as pd

MONTHS=('01','02','06','07')
DEFAULT_SOURCE=Path('/mnt/data/h1v2_r2/results')
DEFAULT_OUTPUT=Path('/mnt/data/h1v2_r3/results')
STATES=('WRONG','NEUTRAL','WEAK_GOOD','STRONG_GOOD')
Z=1.96

def wilson(s,n):
    if not n: return 0.
    p=s/n; z=Z;zz=z*z
    return (p+zz/(2*n)-z*math.sqrt(max(0.,p*(1-p)/n+zz/(4*n*n))))/(1+zz/n)

def signed(x,scale):
    # Fixed physical threshold in dollars or normalized absolute ratio: no learned bin edges.
    return np.where(x>scale,2,np.where(x<-scale,0,1)).astype(np.int16)

def ternary_ratio(x,low,high):
    return np.where(x>=high,2,np.where(x<=low,0,1)).astype(np.int16)

def macro_features(X,t):
    """All features depend on quote indices <= candidate; t is event timestamp."""
    a=X[:,:99].reshape(-1,9,11).astype(np.float64)
    rng=a[:,:,0];location=a[:,:,3];favorable=(a[:,:,4]-a[:,:,5]);spread=X[:,99]
    lead=(a[:,:,8]-a[:,:,9])/(a[:,:,8]+a[:,:,9]+1.)
    efficiency=a[:,:,10]
    def trend(i):return signed((location[:,i]-.5)*rng[:,i],.02 if i<=3 else .05)
    raw={
      'session4':((t//3600000)%24//6).astype(np.int16),
      'hour24':((t//3600000)%24).astype(np.int16),
      'week_day':((t//86400000+3)%7).astype(np.int16),
      'spread3':np.digitize(spread,[.7,1.0]).astype(np.int16),
      'spread5':np.digitize(spread,[.6,.7,.8,1.0]).astype(np.int16),
      'trend250':trend(0),'trend1s':trend(2),'trend5s':trend(3),'trend15s':trend(4),
      'trend30s':trend(5),'trend60s':trend(7),'trend300s':trend(8),
      'order250':signed(a[:,0,1],.01),'order5s':signed(a[:,3,1],.01),
      'order60s':signed(a[:,7,1],.01),
      'lead1s':signed(lead[:,2],.03),'lead5s':signed(lead[:,3],.03),
      'lead60s':signed(lead[:,7],.03),
      'eff5s':ternary_ratio(efficiency[:,3],.3,.75),
      'eff60s':ternary_ratio(efficiency[:,7],.3,.75),
      'vol_ratio1s60s':ternary_ratio(rng[:,2]/(rng[:,7]+.01),.025,.25),
      'vol_ratio5s300s':ternary_ratio(rng[:,3]/(rng[:,8]+.01),.035,.35),
      'range60s':np.digitize(rng[:,7],[.5,1.0,2.0]).astype(np.int16),
      'event_density1s':np.digitize(a[:,2,6]+a[:,2,7],[0.5,4.5,20.5]).astype(np.int16),
      'event_density60s':np.digitize(a[:,7,6]+a[:,7,7],[2.5,10.5,40.5]).astype(np.int16),
      'impulse5s':signed(favorable[:,3]/(rng[:,3]+.01),.2),
      'impulse60s':signed(favorable[:,7]/(rng[:,7]+.01),.2)
    }
    # The raw R9-H1V2 feature vector contains 9 overlapping causal windows and
    # is sampled strictly before 30s future labels; no first_ms/net/side_class used.
    return raw

GRID_SPECS={
 'G1_session_macro':['session4','trend60s','trend300s','range60s','spread3'],
 'G2_micro_firstpass':['session4','trend250','trend1s','trend5s','lead1s','spread3'],
 'G3_multihorizon_alignment':['session4','trend1s','trend5s','trend15s','trend60s','trend300s','spread3'],
 'G4_regime_quote_flow':['session4','vol_ratio1s60s','eff5s','eff60s','lead5s','lead60s','event_density1s','spread3'],
 'G5_pivot_rejection':['session4','order250','order5s','order60s','trend5s','trend60s','impulse5s','spread3'],
 'G6_cross_session_regime':['hour24','week_day','trend5s','trend60s','trend300s','range60s','spread5'],
 'G7_dense_full_motif':['hour24','trend250','trend1s','trend5s','trend15s','trend60s','order5s','lead5s','vol_ratio5s300s','spread5'],
 'G8_fast_slow_quoteflow':['session4','trend250','trend1s','trend30s','trend300s','lead1s','lead60s','event_density1s','event_density60s','eff60s','spread3'],
 'G9_true_micro_signed':['session4','true_trend_250ms','true_trend_1s','true_trend_5s','quote_rate_1s','spread3'],
 'G10_true_htf_alignment':['session4','true_trend_5s','true_trend_60s','true_trend_5m','true_trend_15m','true_trend_1h','true_trend_4h','spread3'],
 'G11_true_intraday_regime':['hour24','true_trend_15s','true_trend_30s','true_trend_60s','quote_rate_1s','quote_rate_60s','range60s','spread3'],
 'G12_session_persistent_structure':['hour24','week_day','true_trend_15m','true_trend_1h','true_trend_4h','quote_rate_15m','spread5'],
 'G13_full_true_path':['session4','true_trend_250ms','true_trend_1s','true_trend_5s','true_trend_15s','true_trend_60s','true_trend_5m','true_trend_1h','lead5s','order5s','spread3'],
 'G14_quote_intensity_state':['session4','true_trend_60s','true_trend_5m','true_trend_1h','quote_rate_1s','quote_rate_5s','quote_rate_60s','quote_rate_5m','spread3']
} 

def read_source(root=DEFAULT_SOURCE):
    out=[]
    for m in MONTHS:
        with np.load(root/f'H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz',allow_pickle=False) as z:
            d={k:z[k].copy() for k in ('X','ts','ix','side_class','original_row','y_original')}
        assert d['X'].shape==(15000,100)
        assert d['side_class'].shape==(15000,2)
        assert np.all((d['side_class']>=0)&(d['side_class']<=3))
        assert np.all(np.isfinite(d['X']))
        assert len(np.unique(d['ix']))==len(d['ix'])
        assert np.all(d['ts'][1:]>=d['ts'][:-1])
        out.append((m,d))
    return out

def dataframe(source,extra_root=DEFAULT_OUTPUT):
    blocks=[]
    for m,d in source:
        f=macro_features(d['X'],d['ts']);n=len(d['ts'])
        with np.load(extra_root/f'H1V2_R3_TRUE_PATH_{m}.npz',allow_pickle=False) as real:
            assert np.array_equal(real['ix'],d['ix']) and np.array_equal(real['ts'],d['ts']), 'raw quote ordinal mismatch'
            f.update(feat_classes(real['asof_X']))
        repeat={k:np.repeat(v,2) for k,v in f.items()}
        data={**repeat,'month':np.full(n*2,m),'side':np.tile(np.array([0,1],np.int8),n),
              'event_id':np.arange(n,dtype=np.int32).repeat(2),
              'class':d['side_class'].ravel(),
              'strong':(d['side_class'].ravel()==3).astype(np.int8)}
        assert all(len(v)==n*2 for v in data.values())
        blocks.append(pd.DataFrame(data))
    return pd.concat(blocks,ignore_index=True)

def fit_map(df,features,mask):
    # exact in-sample empirical P(strong), Wilson; does not carry labels into score.
    group=df.loc[mask,features+['strong']].groupby(features,sort=False,observed=True)['strong'].agg(['size','sum']).reset_index()
    return group.rename(columns={'size':'n_fit','sum':'strong_fit'})

def evaluate(df,features,fit_mask,score_mask,min_support,gate,prefix,leave_one_out=False):
    fit=fit_map(df,features,fit_mask)
    view=df.loc[score_mask,list(dict.fromkeys(['month','event_id','side','class']+features))].merge(fit,on=features,how='left',sort=False)
    count=view['n_fit'].fillna(0).to_numpy(dtype=np.int64)
    strong=view['strong_fit'].fillna(0).to_numpy(dtype=np.int64)
    if leave_one_out:
        assert np.array_equal(fit_mask,score_mask),'leave-one-out must score same rows as fitting source'
        # Diagnostic only: train a distinct cell-count model for every held-out row.
        # The scored row's label is EXCLUDED, never passed to prediction.
        count=count-1
        strong=strong-(view['class'].to_numpy()==3).astype(np.int64)
        assert np.all(count>=0) and np.all(strong>=0)
    # Option 'wilson' sharply rejects statistically ambiguous cells.
    if gate.startswith('wilson'):
        z2=Z**2
        p=np.divide(strong,count,out=np.zeros_like(count,dtype=float),where=count>0)
        score=np.where(count>0,(p+z2/(2*np.maximum(count,1))-Z*np.sqrt(p*(1-p)/np.maximum(count,1)+z2/(4*np.maximum(count,1)**2)))/(1+z2/np.maximum(count,1)),0.)
        cutoff=float(gate.split(':')[1])
    else:
        score=np.divide(strong,count,out=np.zeros_like(count,dtype=float),where=count>0)
        cutoff=float(gate.split(':')[1])
    score=np.where(count>=min_support,score,-1.)
    assert len(score)%2==0
    ss=score.reshape(-1,2);cls=view['class'].to_numpy().reshape(-1,2)
    assert np.all(view['side'].to_numpy().reshape(-1,2)==np.array([0,1]))
    best=np.argmax(ss,axis=1)
    top=ss[np.arange(len(best)),best];rival=ss[np.arange(len(best)),1-best]
    accepted=(top>=cutoff)&(top>rival+1e-12) # ambiguous BUY/SELL -> WAIT
    observed=cls[np.arange(len(best)),best]
    n=int(accepted.sum())
    result={'selected_sampled_events':n,'strong_correct':int(np.sum(accepted&(observed==3))),
        'weak_good':int(np.sum(accepted&(observed==2))),'neutral':int(np.sum(accepted&(observed==1))),
        'wrong':int(np.sum(accepted&(observed==0))),'fit_cell_count':len(fit),
        'nonoverlap_not_enforced':True,'window':prefix,'leave_one_out':leave_one_out,
        'min_support':min_support,'gate':gate,'n_scored_state_events':len(best)}
    months=view['month'].to_numpy().reshape(-1,2)[:,0]
    result['monthly']={}
    for month in MONTHS:
        m=accepted&(months==month)
        nm=int(m.sum())
        result['monthly'][month]={'n':nm,
          'strong_correct':int(np.sum(m&(observed==3))),
          'wrong':int(np.sum(m&(observed==0))),
          'neutral':int(np.sum(m&(observed==1))),
          'weak_good':int(np.sum(m&(observed==2)))}
    result['strong_precision']=round(result['strong_correct']/n,6) if n else None
    result['wilson_lower']=round(wilson(result['strong_correct'],n),6) if n else 0.
    return result

def run(root=DEFAULT_SOURCE,out=DEFAULT_OUTPUT):
    out.mkdir(parents=True,exist_ok=True)
    source=read_source(root);df=dataframe(source)
    sha={m:hashlib.sha256((root/f'H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz').read_bytes()).hexdigest() for m,_ in source}
    assert len(df)==120000
    results=[]
    all4=np.ones(len(df),dtype=bool)
    three=(df['month'].to_numpy()!='07')
    july=~three
    # include intentional high-overfit resub + frozen month-out falsification.
    for name,features in GRID_SPECS.items():
        for support in (1,3,10,30):
            for gate in ('mean:0.8','wilson:0.65'):
                res={'motif':name,'n_key_features':len(features)+1,'features':features+['side'],
                     'training':'all_four_in_sample_resubstitution',
                     'all4':evaluate(df,features+['side'],all4,all4,support,gate,'four_month_resubstitution'),
                     'july_heldout':evaluate(df,features+['side'],three,july,support,gate,'july_never_trained')}
                if support==1 and gate=='mean:0.8':
                    res['four_month_leave_one_out']=evaluate(df,features+['side'],all4,all4,support,gate,'four_month_nonchronological_leave_one_out',leave_one_out=True)
                results.append(res)
        print('tested',name,'configs',len(results),flush=True)
    def ranking(col):
        # Favor correctness+sample support over brittle precision from 1-2 samples.
        return sorted(results,key=lambda r: (r[col]['wilson_lower'],r[col]['strong_correct']),reverse=True)[:8]
    report={'lab':'H1V2_R3','source_label_classes':STATES,'sampled_market_states':60000,
        'action_specific_training_labels':120000,'source_sha256':sha,
        'method':'fit categorical multi-horizon session/regime quote-motif conditional strong-good rates; independent side; tie->WAIT; no future labels in inference features',
        'grids':len(GRID_SPECS),'configurations':len(results),'extra_source':'source exact 15k/month raw as-of 250ms through 4hr quote displacement and arrival counts; original 99 terminal range-position is not actual trend','all4_overfit_top':ranking('all4'),
        'july_falsification_top':ranking('july_heldout'),
        'leave_one_out_diagnostic':[{'motif':r['motif'], **r['four_month_leave_one_out']} for r in results if 'four_month_leave_one_out' in r],
        'results':results,
        'limits':['Four-month resubstitution is not prediction','July heldout is not an OOS claim for intentionally in-sample experiment, but diagnoses transfer','sampled 15k/month not 15.4M full event universe','selected candidates may overlap, not a trade ledger','No Coinexx and no live realistic cost stress','R9 original exits and source labels unchanged']}
    path=out/'H1V2_R3_MULTIGRID_ASYMMETRIC_MOTIFS.json'
    path.write_text(json.dumps(report,indent=2))
    print('completed',len(results),'peak4',report['all4_overfit_top'][0]['all4'],'peakjuly',report['july_falsification_top'][0]['july_heldout'],flush=True)
    return report

if __name__=='__main__':run()
