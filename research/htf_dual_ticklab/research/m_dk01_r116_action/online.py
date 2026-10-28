"""Past-matured action-response correction; no current event labels at inference."""
from pathlib import Path
import argparse
import json
import numpy as np
from numba import njit
from run import ROOT, MONTHS, splits, calibrate, score, write_json, sha, log


@njit(cache=True)
def correct(t, side, regime, original_y, touch, probs, eligible_update):
    observed=np.zeros((24,5,3)); expected=np.zeros((24,5,3)); stamp=np.full(24,-1,np.int64)
    out=np.empty_like(probs); cursor=0
    groups=(side>0).astype(np.int64)*12+((t//21600000)%4)*3+regime
    for i in range(len(t)):
        while cursor<i and t[cursor]+33001<t[i]:
            if eligible_update[cursor]:
                g=groups[cursor]
                if stamp[g]>=0:
                    decay=2.**(-(t[i]-stamp[g])/1800000.)
                    observed[g]*=decay; expected[g]*=decay
                stamp[g]=t[i]
                for action in range(1,5):
                    label=0 if touch[cursor,action]>=0 else (1 if original_y[cursor]==0 else 2)
                    observed[g,action,label]+=1.
                    expected[g,action]+=probs[cursor,action]
            cursor+=1
        g=groups[i]
        if stamp[g]>=0:
            decay=2.**(-(t[i]-stamp[g])/1800000.)
            observed[g]*=decay; expected[g]*=decay
        stamp[g]=t[i]
        out[i,0]=probs[i,0]
        for action in range(1,5):
            total=0.
            for c in range(3):
                ratio=(observed[g,action,c]+32.)/(expected[g,action,c]+32.)
                ratio=min(4.,max(.25,ratio))
                out[i,action,c]=probs[i,action,c]*ratio;total+=out[i,action,c]
            out[i,action]/=max(1e-12,total)
    return out


def run(month):
    a=np.load(ROOT/'cache'/f'actions_{month}.npz')
    x=np.load(ROOT/'cache'/f'x_{month}.npy',mmap_mode='r')
    names=json.loads((ROOT/'cache'/f'{month}.json').read_text())['features']
    m1=x[:,names.index('structure_60000_3_5')]
    m15=x[:,names.index('structure_900000_3_5')]
    regime=np.where((m1>.3)&(m15>.3),0,np.where((m1<-.3)&(m15<-.3),1,2)).astype('int64')
    eligible=np.ones(len(x),bool)
    if month=='01': eligible=np.arange(len(x))>=int(.6*len(x))
    probs=np.load(ROOT/'results'/f'prob_full_{month}.npy')
    out=correct(a['t'],a['original_side'],regime,a['truth_class'],a['touch_250'],probs,eligible)
    path=ROOT/'results'/f'prob_online_{month}.npy'
    if path.exists(): raise RuntimeError('Online evidence exists; do not overwrite')
    np.save(path,out)
    write_json(ROOT/'results'/f'online_{month}.json',dict(plan_sha256=sha(ROOT/'ONLINE_PLAN.md'),
        code_sha256=sha(__file__),events=len(x),update_eligible=int(eligible.sum()),
        output_sha256=sha(path)))
    if month=='01': calibrate('online')
    score(month,'online')
    log('online complete',month)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--month',choices=MONTHS,required=True)
    run(p.parse_args().month)
