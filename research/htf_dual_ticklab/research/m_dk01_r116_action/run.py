"""Source-pinned R116 action-geometry study. No broker connection or orders."""
from __future__ import annotations

import argparse
import gc
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import zipfile

import lightgbm as lgb
import numpy as np
import pandas as pd
from numba import njit

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
sys.path.insert(0, str(ROOT / 'vendor'))
sys.path.insert(0, str(WORK / 'repo/research/htf_dual_ticklab'))
from original_features import raw_features
from reused_structure import structure
from htf_ticklab.source_registry import verify

MONTHS = ('01', '02', '06', '07')
ACTIONS = ('MARKET', 'CONTINUE_015', 'CONTINUE_035', 'RETEST', 'STRUCTURAL_STOP')
LATENCIES = (0, 250, 1000)
ARCHIVE = WORK / 'sources/filter08_recovered.zip'
ARC_SHA = '7edaddf30f3a19cafd364a270333c6f87962960233f9d10ccbfb6e2a3b23b2ad'
START = time.monotonic()


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write_json(path, data):
    p = Path(path); tmp = Path(str(p) + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    os.replace(tmp, p)


def log(*args):
    print(round(time.monotonic() - START, 2), *args, flush=True)


@njit(cache=True)
def ordered_signatures(tm, bid, ask, idx, side):
    """Degree-two Chen accumulation; path order retained in antisymmetric terms."""
    horizons = (8, 16, 32, 64)
    out = np.zeros((len(idx), 104), np.float32)
    for i in range(len(idx)):
        end = idx[i]
        for h, length in enumerate(horizons):
            start = max(0, end - length)
            low = min(bid[start], ask[start]); high = max(bid[start], ask[start])
            for j in range(start, end + 1):
                low = min(low, bid[j], ask[j]); high = max(high, bid[j], ask[j])
            scale = max(.05, high - low)
            duration = max(1., tm[end] - tm[start])
            first = np.zeros(4); second = np.zeros((4, 4))
            changes = np.zeros(6); previous_mark = 0
            for j in range(start + 1, end + 1):
                db = bid[j] - bid[j - 1]; da = ask[j] - ask[j - 1]
                bo = (db != 0) and (da == 0); ao = (da != 0) and (db == 0)
                mark = 1 if bo else (2 if ao else 3)
                step = np.array([side[i]*db/scale, side[i]*da/scale,
                                 (tm[j]-tm[j-1])/duration, (int(bo)-int(ao))/max(1,length)])
                for a in range(4):
                    for b in range(4):
                        second[a,b] += first[a]*step[b] + .5*step[a]*step[b]
                first += step
                changes[0] += bo; changes[1] += ao
                changes[2] += (db != 0) and (da != 0)
                changes[3] += previous_mark == 1 and mark == 2
                changes[4] += previous_mark == 2 and mark == 1
                changes[5] += db * da < 0
                previous_mark = mark
            base = h*26
            out[i,base:base+4] = first
            out[i,base+4:base+20] = second.reshape(16)
            out[i,base+20:base+26] = changes/max(1,end-start)
    return out


def role_geometry(tm, mid, et, idx, side):
    columns = []; structural_distance = np.full(len(et), .35)
    candidates = []
    for width in (60000, 300000, 900000, 3600000):
        keys0 = tm // width
        starts = np.r_[0, np.flatnonzero(np.diff(keys0)) + 1]
        ends = np.r_[starts[1:], len(tm)]
        keys = keys0[starts]
        hi = np.maximum.reduceat(mid, starts); lo = np.minimum.reduceat(mid, starts)
        close = mid[ends - 1]
        last = np.searchsorted(keys, et // width, side='left') - 1
        for n in (3, 5, 9):
            ix = np.maximum(0, last[:, None] - np.arange(n + 1))
            valid = (last >= n) & (keys[ix[:,0]] == et//width-1)
            valid &= keys[ix[:,0]] - keys[ix[:,-1]] == n
            upper = hi[ix[:,:n]].max(axis=1); lower = lo[ix[:,:n]].min(axis=1)
            oldupper = hi[ix[:,1:]].max(axis=1); oldlower = lo[ix[:,1:]].min(axis=1)
            span = np.maximum(.05, upper-lower)
            vals = np.column_stack((side*(upper-oldupper)/span, side*(lower-oldlower)/span,
                (close[ix[:,0]]>oldupper).astype(float), (close[ix[:,0]]<oldlower).astype(float)))
            vals[~valid] = 0; columns.append(vals)
            if width in (60000, 300000) and n == 3:
                dist = np.where(side > 0, upper-mid[idx], mid[idx]-lower)
                dist[~valid | (dist <= 0)] = np.inf
                candidates.append(dist)
    best = np.minimum(candidates[0], candidates[1])
    finite = np.isfinite(best)
    structural_distance[finite] = np.clip(best[finite], .10, .70)
    return np.column_stack(columns).astype('float32'), structural_distance


def features(tm, bid, ask, et, side):
    source_idx = np.searchsorted(tm, et, side='left') - 1
    unsupported = source_idx < 0
    idx = np.maximum(source_idx, 0)
    mid = (bid+ask)/2
    raw, names = raw_features(tm, mid, bid, ask, idx)
    sq = np.r_[0., np.cumsum(np.diff(mid)**2)]
    prev = np.maximum(0, np.searchsorted(tm, et-30000, side='left')-1)
    scale = np.maximum(.05, np.sqrt(np.maximum(0., sq[idx]-sq[prev])))
    geom, gn = structure(tm, mid, et, idx, side, scale)
    roles, distance = role_geometry(tm, mid, et, idx, side)
    sig = ordered_signatures(tm, bid, ask, idx, side)
    signed = raw[:,list(range(9))+[15,16,17]]*side[:,None]
    base = np.column_stack((raw, signed, geom, side, np.log(scale), distance, et-tm[idx]))
    x = np.column_stack((base, roles, sig))
    x = np.nan_to_num(x, nan=0, posinf=0, neginf=0).astype('float32')
    x[unsupported] = 0
    distance[unsupported] = .35
    names += ['signed_'+str(i) for i in range(12)] + gn
    names += ['side','log_scale','structural_distance','quote_age']
    names += [f'role_{j}' for j in range(roles.shape[1])]
    names += [f'signature_{j}' for j in range(sig.shape[1])]
    return x, distance, source_idx, names, base.shape[1]


@njit(cache=True)
def action_paths(tm, bid, ask, et, side, anchor_idx, distances, latency):
    """Full-information quote-bound paths. Future arrays are labels/evaluation only."""
    n = len(et)
    touch = np.full((n,5), -1, np.int64)
    gross = np.full((n,5), np.nan)
    for i in range(n):
        unsupported = anchor_idx[i] < 0
        a = max(0, anchor_idx[i]); s = side[i]
        anchor = ask[a] if s > 0 else bid[a]
        start = np.searchsorted(tm, et[i] + latency, side='left')
        if latency == 0:
            start = np.searchsorted(tm, et[i], side='right')
        phase = 0; peak = 0.; trough = 0.
        for j in range(start, len(tm)):
            if tm[j] > et[i]+16000:
                break
            price = ask[j] if s>0 else bid[j]
            move = s*(price-anchor)
            if touch[i,0] < 0:
                touch[i,0] = j
                if unsupported:
                    touch[i,:] = j
                    break
            if touch[i,1] < 0 and move >= .15: touch[i,1] = j
            if touch[i,2] < 0 and move >= .35: touch[i,2] = j
            if touch[i,4] < 0 and move >= distances[i]: touch[i,4] = j
            if phase == 0:
                if move >= .35: phase = 1; peak = move
            elif phase == 1:
                peak = max(peak, move)
                if move <= peak-.15: phase = 2; trough = move
            elif phase == 2:
                trough = min(trough, move)
                if move >= trough+.05: touch[i,3] = j; phase = 3
        out = np.searchsorted(tm, et[i]+32000, side='left')
        if out < len(tm) and tm[out] < et[i]+34000:
            exit_price = bid[out] if s>0 else ask[out]
            for k in range(5):
                j = touch[i,k]
                if j >= 0:
                    price = ask[j] if s>0 else bid[j]
                    gross[i,k] = s*(exit_price-price)
    return touch, gross


def original(month):
    with zipfile.ZipFile(ARCHIVE) as z:
        with np.load(io.BytesIO(z.read(f'FILTER08/FITTED_CLASSIFIER_SCORES_dukascopy_{month}.npz'))) as a:
            return {k:a[k].copy() for k in ('t','original_side','truth_class','kept')}


def prepare(month):
    receipt_path = ROOT/'cache'/f'{month}.json'
    if receipt_path.exists():
        r = json.loads(receipt_path.read_text())
        if r['run_sha256'] == sha(__file__) and all(sha(ROOT/p)==h for p,h in r['files'].items()):
            log('reuse exact cache',month); return
        raise RuntimeError('Cache conflict; do not overwrite earlier evidence')
    if sha(ARCHIVE) != ARC_SHA: raise ValueError('FILTER08 archive mismatch')
    p = WORK/f'sources/XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
    digest = sha(p); verify(p.name,'dukascopy',digest)
    a = original(month)
    df = pd.read_csv(p,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],
        dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
    tm = df.timestamp_ms_utc.to_numpy()
    bid = df.bid_raw.to_numpy(dtype='float64')/1000
    ask = df.ask_raw.to_numpy(dtype='float64')/1000
    j = np.searchsorted(tm,a['t'],side='left')
    if np.any(j>=len(tm)) or not np.array_equal(tm[j],a['t']): raise ValueError('Event identity')
    if np.any(np.diff(tm)<0) or np.any(ask<bid): raise ValueError('Quote ordering')
    x,dist,idx,names,base_width = features(tm,bid,ask,a['t'],a['original_side'])
    np.save(ROOT/'cache'/f'x_{month}.npy',x)
    payload = dict(a)
    for latency in LATENCIES:
        touch,gross = action_paths(tm,bid,ask,a['t'],a['original_side'],idx,dist,latency)
        payload['touch_'+str(latency)] = touch
        payload['gross_'+str(latency)] = gross
    np.savez_compressed(ROOT/'cache'/f'actions_{month}.npz',**payload)
    files = {f'cache/x_{month}.npy':sha(ROOT/'cache'/f'x_{month}.npy'),
             f'cache/actions_{month}.npz':sha(ROOT/'cache'/f'actions_{month}.npz')}
    write_json(receipt_path,dict(month=month,events=len(x),quotes=len(tm),source_sha256=digest,
        archive_sha256=ARC_SHA,run_sha256=sha(__file__),plan_sha256=sha(ROOT/'PLAN.md'),
        features=names,base_width=base_width,files=files,max_observed_before_t0=True))
    log('prepared',month,x.shape,len(tm))


def splits(t):
    n = len(t); i = np.arange(n)
    b = [int(.6*n),int(.8*n),int(.9*n)]
    return {'FIT':(i<b[0]) & (t+40000<t[b[0]]),
        'CAL':(i>=b[0]) & (i<b[1]) & (t+40000<t[b[1]]),
        'VAL':(i>=b[1]) & (i<b[2]) & (t+40000<t[b[2]]),
        'SHADOW':i>=b[2]}


def fit(view):
    meta = json.loads((ROOT/'cache/01.json').read_text())
    a = np.load(ROOT/'cache/actions_01.npz')
    x = np.load(ROOT/'cache/x_01.npy',mmap_mode='r')
    fitmask = splits(a['t'])['FIT']
    columns = np.arange(meta['base_width'] if view=='ablation' else x.shape[1])
    for action in range(1,5):
        model_path = ROOT/'models'/f'{view}_{action}.txt'
        done = model_path.with_suffix('.json')
        if done.exists():
            state = json.loads(done.read_text())
            if state['rounds']==96 and state['sha256']==sha(model_path):
                log('reuse completed model',view,action); continue
        touch = a['touch_250'][:,action]>=0
        target = np.where(touch,0,np.where(a['truth_class']==0,1,2))
        dataset = lgb.Dataset(x[fitmask][:,columns], label=target[fitmask],free_raw_data=False)
        model = lgb.Booster(model_file=str(model_path)) if model_path.exists() else None
        rounds = model.current_iteration() if model else 0
        params = dict(objective='multiclass',num_class=3,metric='multi_logloss',learning_rate=.06,
            num_leaves=127,min_data_in_leaf=96,max_bin=127,lambda_l2=5.,feature_fraction=.9,
            num_threads=4,verbosity=-1,seed=1162026+action,deterministic=True,force_col_wise=True)
        while rounds<96:
            model = lgb.train(params,dataset,num_boost_round=min(16,96-rounds),init_model=model,
                              keep_training_booster=True)
            rounds = model.current_iteration()
            tmp = model_path.with_suffix('.tmp'); model.save_model(str(tmp)); os.replace(tmp,model_path)
            write_json(done,dict(rounds=rounds,fit_rows=int(fitmask.sum()),action=ACTIONS[action],
                columns=columns.tolist(),sha256=sha(model_path),plan_sha256=sha(ROOT/'PLAN.md')))
            log('fit',view,action,rounds)
        del dataset,model; gc.collect()


def predict(month,view):
    out = ROOT/'results'/f'prob_{view}_{month}.npy'
    if out.exists(): raise RuntimeError('Prediction already exists; do not overwrite')
    x = np.load(ROOT/'cache'/f'x_{month}.npy',mmap_mode='r')
    probs = np.zeros((len(x),5,3),np.float32); probs[:,0,0] = 1
    for action in range(1,5):
        p=ROOT/'models'/f'{view}_{action}.txt'; m=lgb.Booster(model_file=str(p))
        cols=json.loads(p.with_suffix('.json').read_text())['columns']
        for start in range(0,len(x),25000):
            end=min(len(x),start+25000)
            probs[start:end,action]=m.predict(x[start:end][:,cols],num_threads=4)
    np.save(out,probs); log('predicted',month,view)


def choose(probs, multiplier):
    value = probs[:,:,2] - multiplier*probs[:,:,1]
    value[:,0] = 0
    return np.argmax(value,axis=1).astype('int8')


def evaluate(a,actions,mask,latency=250):
    i=np.flatnonzero(mask); y=a['truth_class'][i]
    touched=a['touch_'+str(latency)][i,actions[i]]>=0
    g=a['gross_'+str(latency)][i,actions[i]]
    no=~touched; good=y==0; bad=~good
    # Zero outcome only for NO ENTRY, not for missing exits.
    known=touched & np.isfinite(g)
    return dict(n=len(i),original_correct=int(good.sum()),original_bad=int(bad.sum()),
        incorrect_no_touch=int((no&bad).sum()),correct_no_touch=int((no&good).sum()),
        opposite_no_touch=int((no&(y==1)).sum()),neutral_no_touch=int((no&(y==2)).sum()),
        quote_touches=int(touched.sum()),unknown_exit=int((touched&~np.isfinite(g)).sum()),
        known_gross_sum=float(g[known].sum()),
        gross_per_known_touch=float(g[known].mean()) if known.any() else None,
        known_gross_sum_per_all_intents=float(g[known].sum()/max(1,len(i))),
        selected_action_counts=np.bincount(actions[i],minlength=5).tolist())


def calibrate(view):
    path=ROOT/'results'/f'frozen_{view}.json'
    if path.exists(): raise RuntimeError('Already frozen')
    a=np.load(ROOT/'cache/actions_01.npz'); p=np.load(ROOT/'results'/f'prob_{view}_01.npy')
    mask=splits(a['t'])['CAL']; session=(a['t']//21600000)%4
    trials=[]; feasible=[]
    for power in range(21):
        mult=float(2**power); act=choose(p,mult); score=evaluate(a,act,mask)
        cells=[]
        for s in (-1,1):
            for h in range(4):
                cm=mask&(a['original_side']==s)&(session==h); cs=evaluate(a,act,cm)
                cells.append(dict(side=s,session=h,**cs))
        ok=score['correct_no_touch']<=.01*score['original_correct']
        ok &= all(c['original_correct']<100 or c['correct_no_touch']<=.02*c['original_correct'] for c in cells)
        item=dict(multiplier=mult,feasible=bool(ok),score=score,cells=cells)
        trials.append(item)
        if ok: feasible.append(item)
    if not feasible: raise RuntimeError('Even fallback violates CAL; investigate source missing quotes')
    best=max(feasible,key=lambda d:(d['score']['incorrect_no_touch'],-d['score']['correct_no_touch'],-d['multiplier']))
    write_json(path,dict(selected=best,trials=trials,selection_only='JAN_CAL',plan_sha256=sha(ROOT/'PLAN.md')))
    log('frozen',view,best['multiplier'],best['score'])


def score(month,view):
    a=np.load(ROOT/'cache'/f'actions_{month}.npz')
    src=original(month)
    for key in src:
        if not np.array_equal(a[key],src[key]): raise ValueError('Original event identity mismatch '+key)
    p=np.load(ROOT/'results'/f'prob_{view}_{month}.npy')
    frozen=json.loads((ROOT/'results'/f'frozen_{view}.json').read_text())
    actions=choose(p,frozen['selected']['multiplier'])
    masks=splits(a['t']) if month=='01' else {}
    masks['FULL_MIXED' if month=='01' else 'FULL_EXPOSED']=np.ones(len(actions),bool)
    table=[]
    for name,mask in masks.items():
        for latency in LATENCIES:
            table.append(dict(split=name,latency=latency,**evaluate(a,actions,mask,latency)))
    baseline=np.full(len(actions),2,np.int8)
    own_no=a['touch_250'][np.arange(len(actions)),actions]<0
    base_no=a['touch_250'][:,2]<0; y=a['truth_class']
    diff=dict(correct_rescued=int((base_no&~own_no&(y==0)).sum()),
        bad_readmitted=int((base_no&~own_no&(y!=0)).sum()),
        new_incorrect_no_touch=int((~base_no&own_no&(y!=0)).sum()),
        new_correct_missed=int((~base_no&own_no&(y==0)).sum()))
    # Random action assignment preserving each hour/side's selected action counts.
    key=(a['t']//3600000)*2+(a['original_side']>0)
    _,groups=np.unique(key,return_inverse=True); expected_bad=0.; expected_good=0.
    for group in range(groups.max()+1):
        ix=np.flatnonzero(groups==group)
        counts=np.bincount(actions[ix],minlength=5)/len(ix)
        missing=a['touch_250'][ix]<0
        expected_bad+=float((missing*(y[ix]!=0)[:,None]).sum(axis=0)@counts)
        expected_good+=float((missing*(y[ix]==0)[:,None]).sum(axis=0)@counts)
    cells=[]
    for side in (-1,1):
        for session in range(4):
            mask=(a['original_side']==side)&((a['t']//21600000)%4==session)
            cells.append(dict(side=side,session=session,**evaluate(a,actions,mask)))
    np.savez_compressed(ROOT/'results'/f'decisions_{view}_{month}.npz',t=a['t'],side=a['original_side'],
        truth=y,teacher_kept=a['kept'],action=actions,no_touch=own_no)
    report=dict(month=month,view=view,counts=table,cells=cells,
        baseline=evaluate(a,baseline,np.ones(len(actions),bool)),difference=diff,
        teacher=dict(incorrect_veto=int(((a['kept']==0)&(y!=0)).sum()),correct_lost=int(((a['kept']==0)&(y==0)).sum())),
        placebo_expected=dict(incorrect_no_touch=expected_bad,correct_no_touch=expected_good))
    write_json(ROOT/'results'/f'score_{view}_{month}.json',report)
    log('scored',month,view,table[-2])


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('stage',choices=['prepare','fit','predict','calibrate','score'])
    parser.add_argument('--month',choices=MONTHS); parser.add_argument('--view',choices=['full','ablation'])
    args=parser.parse_args()
    if args.stage=='prepare': prepare(args.month)
    elif args.stage=='fit': fit(args.view)
    elif args.stage=='predict': predict(args.month,args.view)
    elif args.stage=='calibrate': calibrate(args.view)
    elif args.stage=='score': score(args.month,args.view)
