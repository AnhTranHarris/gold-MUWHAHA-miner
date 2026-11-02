#!/usr/bin/env python3
"""Frozen v2 observed-WAIT policy online evaluation with causal check suffix.

A frozen historical teacher model can score ONLY live-at-time 19-bin features;
future 60s teacher outcome data has no runtime import path. The original exact
FastClock / R9 SL trail close are reused. No quota forcing or retrospective
selection. The model is never approved unless independent calibration passed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import lightgbm as lgb,numpy as np
from sequential_base_exact import SequentialRouter
from router_v2_dataset import iter_ticks

class FrozenPolicy:
    def __init__(self,three,wait):
        self.now=lgb.Booster(model_file=str(three));self.wait=lgb.Booster(model_file=str(wait))
        assert self.now.num_feature()==19 and self.wait.num_feature()==19
    def predict(self,x):
        a=np.asarray(x,dtype=np.float64).reshape(1,-1)
        p=self.now.predict(a,num_threads=1)[0]
        w=float(self.wait.predict(a,num_threads=1)[0])
        return float(p[2]-1.2*p[0]-.45*p[1]-.2*w)

class CheckOnlySequential(SequentialRouter):
    def __init__(self,check_start_ms,policy,score_threshold):
        super().__init__();self.check_start_ms=check_start_ms
        self.policy=policy;self.min_p_correct=score_threshold
        self.precheck_ticks=0
    def on_quote(self,q):
        if q.utc_ms<self.check_start_ms:
            self.precheck_ticks+=1
            self.clock.add(q)
            return
        return super().on_quote(q)

def run(source,month,root,allow_failed_shadow=False):
    root=Path(root);rec=json.loads((root/'models'/f'{source}_{month}'/'FOLD_RECEIPT.json').read_text())
    assert rec['source']==source and rec['month']==month
    threshold=rec['calibrated_threshold']
    if threshold is None:
        return {'source':source,'month':month,'status':'NO_CALIBRATED_ENTRY_POLICY',
             'cause':'none of the earlier calibration variants met 80% strict survival and positive net',
             'on_policy_not_run':True}
    start=rec['time_splits']['cal_until_day']*86400000+60000
    m=rec['frozen_research_model'];folder=root/'models'/f'{source}_{month}'
    policy=FrozenPolicy(folder/f'three_{m}.txt',folder/f'wait_{m}.txt')
    runner=CheckOnlySequential(start,policy,threshold)
    path=Path('/mnt/data')/(f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz' if source=='coinexx' else f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz')
    out=root/'on_policy'/f'{source}_{month}';out.mkdir(exist_ok=True,parents=True)
    rep=runner.run(path,source,out=out);rep['precheck_ticks']=runner.precheck_ticks
    rep['policy_sha']='frozen chronological calibration';rep['status']='ON_POLICY_CHRONOLOGICAL_CHECK_DIAGNOSTIC_NOT_LIVE_APPROVAL'
    (out/'run.json').write_text(json.dumps(rep,indent=2));return rep

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True);p.add_argument('--root',default='/mnt/data/v2_new_research/sixty');a=p.parse_args();print(json.dumps(run(a.source,a.month,a.root),indent=2)[:5000])
