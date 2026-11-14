"""Original-source-day bootstrap, model fits held frozen, no retraining."""
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
import json,argparse

def run(pred_dir:Path,out:Path,nboot=250):
    rng=np.random.default_rng(20261114)
    results={}
    for age in (1,3):
        months=[]
        for m in range(6,10):
            with np.load(pred_dir/f'pred_{m:02d}_{age}s.npz',allow_pickle=False) as z:
                d={k:z[k] for k in z.files}
                dates=d['entry_day'];days=np.unique(dates)
                groups=[np.flatnonzero(dates==day) for day in days]
                months.append((m,d,groups))
        sample=np.zeros((nboot,2),dtype=float)
        for b in range(nboot):
            averages=[];aucs=[]
            for m,d,groups in months:
                picked=rng.integers(0,len(groups),len(groups))
                ind=np.concatenate([groups[j] for j in picked])
                y=d['delta'][ind]
                averages.append(float(np.mean(y)))
                if len(np.unique(y>0))<2:
                    aucs.append(np.nan)
                else:
                    labels=(y>0)
                    aucs.append(float(roc_auc_score(labels,d['pred_plus_p5'][ind])-
                                      roc_auc_score(labels,d['pred_context'][ind])))
            sample[b]=[np.mean(averages),np.nanmean(aucs)]
        orig_mean=float(np.mean([d['delta'].mean() for _,d,_ in months]))
        orig_auc=float(np.mean([roc_auc_score(d['delta']>0,d['pred_plus_p5'])-
                                 roc_auc_score(d['delta']>0,d['pred_context']) for _,d,_ in months]))
        results[f'{age}s']={
          'replicates':nboot,
          'original_equal_month_mean_observed_hold_delta':orig_mean,
          '95pc_day_resampling_interval_for_hold_delta':np.quantile(sample[:,0],[.025,.975]).tolist(),
          'original_equal_month_mean_p5_rank_auc_delta':orig_auc,
          '95pc_day_resampling_interval_for_p5_rank_auc_delta':np.quantile(sample[:,1],[.025,.975]).tolist(),
          'limitations':'Historical source days resampled within original evaluation month. Conditional on frozen trained models and previous research exposure. Does not model changed trade sequence, account broker fills or rearm.'}
    out.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    return results

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pred-dir',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--bootstrap',type=int,default=200)
 a=p.parse_args();print(json.dumps(run(a.pred_dir,a.output,a.bootstrap),indent=2))
