#!/usr/bin/env python3
"""Hindsight-only inverse investigation across all exact quote-event action times.
Not an entry strategy. No threshold fitting or future-feature leakage.
"""
from pathlib import Path
from src_three_class_student import load_label_chunks
import numpy as np,json
ROOT=Path('/mnt/data/next_action_timing')
FLOOR={'01':23783,'02':28495,'06':27031,'07':20725}

def analyze(src,mon):
    n=0;labels=np.zeros((4,2,3),np.int64);g15=np.zeros((4,2),np.int64)
    anynow=0;anylater=0;anyall=0;delayrescue=0;late_from_badnow=0
    days={}
    for fn in sorted((ROOT/'results'/f'{src}_{mon}_full').glob('*_action_events_*.npz')):
        with np.load(fn) as x:
            y=x['label'];ft=x['first_cause_dt'];f=x['first_cause'];tt=x['decision_time'];net=x['net']
        n+=len(tt)
        for k in range(4):
            for s in range(2):
                for v,j in ((-1,0),(0,1),(1,2)):
                    labels[k,s,j]+=int(np.sum(y[:,k,s]==v))
                g15[k,s]+=int(np.sum((y[:,k,s]==1)&(ft[:,k,s]<=15000)&(f[:,k,s]==1)))
        good=(y==1)
        gnow=np.any(good[:,0,:],axis=1)
        glater=np.any(good[:,1:,:],axis=(1,2))
        anynow+=int(gnow.sum());anylater+=int(glater.sum());anyall+=int((gnow|glater).sum());delayrescue+=int((~gnow&glater).sum())
        late_from_badnow+=int((np.all(y[:,0,:]==-1,axis=1)&glater).sum())
        d=(tt//86400000).astype(np.int64)
        for day in np.unique(d):
            mask=d==day;st=days.setdefault(str(int(day)),[0,0,0])
            st[0]+=int(mask.sum());st[1]+=int(gnow[mask].sum());st[2]+=int((gnow[mask]|glater[mask]).sum())
    assert n==sum(v[0] for v in days.values())
    out={'source':src,'month':mon,'decision_events':n,'counterfactual_actions':n*8,
        'strict_good15_and_net':g15.tolist(), 'three_class_counts_per_delay_side':labels.tolist(),
        'now_any_side_correct':anynow,'later_any_side_correct':anylater,'any_of_eight_correct':anyall,
        'delay_only_rescue':delayrescue,'delay_rescue_from_both_wrong_now':late_from_badnow,
        'teacher_ceiling_fraction':anyall/n,'strict_correct_15rate_per_delay_side':(g15/n).tolist(),
        'correct_30rate_per_delay_side':(labels[:,:,2]/n).tolist(),
        'per_day_hindsight_supply':days,
        'synth_85pct_floor':FLOOR[mon],
        'scientific_boundary':'ORACLE uses future on both side and delayed action choice, not learnable or a real on-policy trade count.'}
    outp=ROOT/'results'/f'{src}_{mon}_NEW_TIMING_HINDSIGHT_ORACLE.json'
    outp.write_text(json.dumps(out,indent=2));return out
if __name__=='__main__':
    import sys
    for src in ('coinexx','dukascopy'):
        for mon in ('01','02','06','07'):
            z=analyze(src,mon)
            print(src,mon,'decisions',z['decision_events'],'now_any',round(z['now_any_side_correct']/z['decision_events'],4),
               'all eight',round(z['teacher_ceiling_fraction'],4),'delay rescue',round(z['delay_only_rescue']/z['decision_events'],4),flush=True)
