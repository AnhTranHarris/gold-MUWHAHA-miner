#!/usr/bin/env python3
"""Risk-governed 85%-volume admission experiment, with thresholds frozen on older dates.
Does not re-label future data, force-fill quota or choose cutoffs on test outcomes.
This is a nonoverlapping SUBSEQUENCE of the already completed single-position v2
entry stream. Dropped entries do not spawn replacement trades.
"""
from pathlib import Path
import argparse, calendar, json, math, time
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from train_student import load, MONTHS, SOURCES, R, FLOORS, stats

def estimate_active_days(month):
    return sum(1 for d in range(1,calendar.monthrange(2026,int(month))[1]+1)
               if calendar.weekday(2026,int(month),d)!=5)

def score_fold(source,month):
    start=time.monotonic();idx=MONTHS.index(month)
    policy=json.loads((R/f'policy_{source}_{month}/POLICY.json').read_text())
    prev=month if idx==0 else MONTHS[idx-1]
    c=load(source,prev)
    cal=c[(c.entry_ms>policy['training_cutoff_utc_ms'])&(c.entry_ms<=policy['calibration_cutoff_utc_ms'])]
    te=c[c.entry_ms>=policy['forecast_from_utc_ms']] if idx==0 else load(source,month)
    assert len(cal)>1000 and len(te)>1000
    assert cal.entry_ms.max()<te.entry_ms.min()
    features=policy['features'];modeldir=R/f'policy_{source}_{month}'
    cls=lgb.Booster(model_file=str(modeldir/'real_success.txt'))
    reg=lgb.Booster(model_file=str(modeldir/'real_expected_net.txt'))
    teacher=lgb.Booster(model_file=str(modeldir/'aux_synth_teacher.txt'))
    a=cls.predict(cal[features],num_threads=2)
    t=cls.predict(te[features],num_threads=2)
    platt=LogisticRegression(C=1.,solver='lbfgs',max_iter=100)
    av=np.clip(a,1e-5,1-1e-5)
    platt.fit(np.log(av/(1-av)).reshape(-1,1),cal.quality)
    def recal(x):
        x=np.clip(x,1e-5,1-1e-5)
        return platt.predict_proba(np.log(x/(1-x)).reshape(-1,1))[:,1]
    a=recal(a);t=recal(t)
    ea=reg.predict(cal[features],num_threads=2)
    et=reg.predict(te[features],num_threads=2)
    ta=teacher.predict(cal[features],num_threads=2)
    tt=teacher.predict(te[features],num_threads=2)
    # Calibrate target acceptance using the known future calendar, NOT future
    # candidate-count or future quality outcomes. January is partial-diagnostic.
    cal_days=int(cal.day_id.nunique());expected_days=estimate_active_days(month)
    if idx==0:
        expected_days=int(te.day_id.nunique()) # chronological time coverage, never P&L
        floor=math.ceil(FLOORS[month]*expected_days/estimate_active_days(month))
    else:floor=FLOORS[month]
    estimated_candidates=max(1.,len(cal)/max(1,cal_days)*expected_days)
    required_accept_frac=min(.95,max(.001,floor/estimated_candidates))
    options=[]
    for wt in (0.,.10):
        s=(1-wt)*a+wt*ta
        bad=s[cal.quality.to_numpy()==0]
        # Strict finite-sample Neyman-Pearson negative selection bound,
        # including ties: never admit >floor(0.10*N_bad) calibration negatives.
        allowed=int(np.floor(.10*len(bad)))
        if allowed<=0:np_cut=float(np.nextafter(np.max(bad),np.inf))
        else:
            boundary=np.partition(bad,len(bad)-allowed-1)[len(bad)-allowed-1]
            np_cut=float(np.nextafter(boundary,np.inf))
        volume_cut=float(np.quantile(s,1-required_accept_frac))
        cutoff=max(np_cut,volume_cut)
        cmask=(s>=cutoff)
        cal_quality=float(cal.quality.to_numpy()[cmask].mean()) if cmask.any() else 0
        cal_avg_net=float(cal.net.to_numpy()[cmask].mean()) if cmask.any() else -1e9
        options.append({'teacher_weight':wt,'np_cutoff':np_cut,'volume_cutoff':volume_cut,'final_cutoff':cutoff,
          'cal_admit_rate':float(cmask.mean()),'cal_quality':cal_quality,'cal_mean_net':cal_avg_net,
          'cal_estimated_month_count':int(cmask.mean()*estimated_candidates),
          'cal_np_bad_acceptance':float((bad>=cutoff).mean())})
    options.sort(key=lambda x:(x['cal_quality']>=.8,x['cal_mean_net']>0,x['cal_quality'],x['cal_mean_net']),reverse=True)
    chosen=options[0]
    s=(1-chosen['teacher_weight'])*t+chosen['teacher_weight']*tt
    mask=s>=chosen['final_cutoff']
    label='partial_january' if idx==0 else 'prospective_month'
    result=stats(te,mask,month,source,label,chosen['final_cutoff'],'LGBM_volume_NP_bad10_no_ev_waiver_research_only')
    result.update({'calibration':chosen,'calibration_variants':options,
        'estimated_test_candidate_count_from_past':int(estimated_candidates),
        'required_accept_fraction_from_past':required_accept_frac,
        'selected_pred_net_positive_fraction':float((et[mask]>0).mean()) if mask.any() else 0,
        'selected_pred_net_mean':float(et[mask].mean()) if mask.any() else None,
        'prospective_threshold':True,'runtime_teacher_flag_used':False,
        'no_future_test_labels_in_policy':True,
        'real_trade_replay_caveat':'Filtered, nonoverlapping existing v2 positions; does not model replacement entries when a position is skipped',
        'elapsed_s':round(time.monotonic()-start,2)})
    (R/f'volume_{source}_{month}_summary.json').write_text(json.dumps(result,indent=2))
    out=te.loc[mask,['entry_ms','exit_ms','side','net','spread','evidence','quality','mfe','mae','day_id','lane']].copy()
    out['p_quality']=t[mask];out['expected_net']=et[mask];out['pred_aux_teacher']=tt[mask]
    out.to_csv(R/f'volume_{source}_{month}_trades.csv.gz',index=False,compression='gzip')
    print(json.dumps({k:result[k] for k in ('source','month','evaluated_candidates','selected_trades','quality_rate','net','volume_pass','daily_80pct_pass','weekly_80pct_pass','monthly_80pct_pass','all_constraints_pass','elapsed_s')}),flush=True)
    return result
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',choices=SOURCES,required=True);a.add_argument('--month',choices=MONTHS,required=True);args=a.parse_args();score_fold(args.source,args.month)
