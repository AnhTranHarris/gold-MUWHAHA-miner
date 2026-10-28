"""R110 source-pinned conditional-distribution research; no broker orders."""
from __future__ import annotations

import argparse
import gc
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import time
import zipfile

import joblib
import numpy as np
import pandas as pd
from numba import njit
from sklearn.tree import ExtraTreeRegressor

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
sys.path.insert(0, str(ROOT / 'vendor'))
sys.path.insert(0, str(WORK / 'repo/research/htf_dual_ticklab'))
from original_features import raw_features
from htf_ticklab.source_registry import verify

OUT = ROOT / 'results'
CACHE = ROOT / 'cache'
MODEL = ROOT / 'models'
for directory in (OUT, CACHE, MODEL):
    directory.mkdir(exist_ok=True)
ARCHIVE = WORK / 'sources/filter08_recovered.zip'
ARC_SHA = '7edaddf30f3a19cafd364a270333c6f87962960233f9d10ccbfb6e2a3b23b2ad'
MONTHS = ('01', '02', '06', '07')
HORIZONS = (5, 15, 30, 60)
START = time.monotonic()


def log(*args):
    print(round(time.monotonic() - START, 2), *args, flush=True)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def atomic_json(path, value):
    temporary = Path(str(path) + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    os.replace(temporary, path)


def structure(tm, mid, et, idx, side, scale):
    """New multi-bar transform. Only strictly completed contiguous bars enter."""
    columns, names = [], []
    for width in (60000, 300000, 900000, 3600000):
        bucket = tm // width
        starts = np.r_[0, np.flatnonzero(np.diff(bucket)) + 1]
        ends = np.r_[starts[1:], len(tm)]
        keys = bucket[starts]
        op, cl = mid[starts], mid[ends - 1]
        high = np.maximum.reduceat(mid, starts)
        low = np.minimum.reduceat(mid, starts)
        last = np.searchsorted(keys, et // width, side='left') - 1
        for n in (3, 5, 9):
            valid = last >= n - 1
            ix = np.maximum(last[:, None] - np.arange(n), 0)
            valid &= (keys[ix[:, 0]] - keys[ix[:, -1]] == n - 1)
            valid &= keys[ix[:, 0]] == et // width - 1
            hi, lo = high[ix].max(axis=1), low[ix].min(axis=1)
            span = np.maximum(hi - lo, .05)
            bodies = cl[ix] - op[ix]
            lastclose = cl[ix[:, 0]]
            vals = np.column_stack((
                side * (lastclose - op[ix[:, -1]]) / span,
                np.abs(bodies).sum(axis=1) / span,
                side * (mid[idx] - hi) / span,
                side * (mid[idx] - lo) / span,
                side * (mid[idx] - lastclose) / scale,
                np.mean(np.sign(bodies) * side[:, None], axis=1),
                np.log1p(span / scale),
                ((mid[idx] - lo) / np.maximum(.1, span / n)) % 1,
                valid.astype(float),
            ))
            vals[~valid, :8] = 0
            columns.append(vals.astype('float32'))
            names.extend(f'structure_{width}_{n}_{j}' for j in range(9))
    return np.column_stack(columns), names


def event_features(tm, bid, ask, et, side):
    # The original source event is the first quote at its timestamp.
    # Later duplicate timestamps remain later source ordinals.
    idx = np.searchsorted(tm, et, side='left')
    if np.any(idx >= len(tm)) or not np.array_equal(tm[idx], et):
        raise ValueError('Original event timestamp does not match a native quote')
    mid = (bid + ask) / 2
    raw, names = raw_features(tm, mid, bid, ask, idx)
    squares = np.r_[0., np.cumsum(np.diff(mid) ** 2)]
    previous = np.maximum(0, np.searchsorted(tm, et - 30000, side='left') - 1)
    scale = np.maximum(.05, np.sqrt(np.maximum(0, squares[idx] - squares[previous])))
    geometry, gn = structure(tm, mid, et, idx, side, scale)
    signed = raw[:, list(range(9)) + [15, 16, 17]] * side[:, None]
    values = np.column_stack((raw, signed, geometry, side, np.log(scale)))
    missing = ~np.isfinite(values)
    values = np.column_stack((np.nan_to_num(values, nan=0, posinf=0, neginf=0), missing))
    names = names + ['signed_' + str(i) for i in range(12)] + gn + ['side', 'log_scale']
    names += ['missing_' + n for n in names]
    return np.clip(values, -1e6, 1e6).astype('float32'), names, scale, idx


def targets(tm, mid, et, idx, side, scale):
    path = np.full((len(et), 4), np.nan)
    valid = np.ones(len(et), bool)
    for k, horizon in enumerate(HORIZONS):
        query = et + 1000 * horizon
        j = np.searchsorted(tm, query, side='left')
        safe = np.minimum(j, len(tm) - 1)
        present = (j < len(tm)) & (tm[safe] < query + 2000)
        path[present, k] = side[present] * (mid[safe[present]] - mid[idx[present]])
        valid &= present
    return path / scale[:, None], valid, path[:, 2]


def prepare(month):
    receipt = CACHE / f'{month}.json'
    arrays = CACHE / f'{month}.npz'
    if receipt.exists() and arrays.exists():
        saved = json.loads(receipt.read_text())
        if saved['cache_sha256'] == digest(arrays) and saved['code_sha256'] == digest(__file__):
            return saved
    source = WORK / f'sources/XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
    sha = digest(source)
    verify(source.name, 'dukascopy', sha)
    with zipfile.ZipFile(ARCHIVE) as z:
        with np.load(io.BytesIO(z.read(f'FILTER08/FITTED_CLASSIFIER_SCORES_dukascopy_{month}.npz'))) as a:
            events = {key: a[key].copy() for key in ('t', 'original_side', 'truth_class', 'kept')}
    df = pd.read_csv(source, usecols=['timestamp_ms_utc', 'bid_raw', 'ask_raw'],
                     dtype={'timestamp_ms_utc': 'int64', 'bid_raw': 'int32', 'ask_raw': 'int32'})
    tm = df.timestamp_ms_utc.to_numpy()
    bid = df.bid_raw.to_numpy().astype('float64') / 1000
    ask = df.ask_raw.to_numpy().astype('float64') / 1000
    if np.any(np.diff(tm) < 0) or np.any(ask < bid) or np.any(bid <= 0):
        raise ValueError('Invalid native quote order/price')
    x, names, scale, idx = event_features(tm, bid, ask, events['t'], events['original_side'])
    trajectory, valid, delta = targets(tm, (bid + ask) / 2, events['t'], idx, events['original_side'], scale)
    derived = np.where(delta > .1, 0, np.where(delta < -.1, 1, 2)).astype('int8')
    mismatch = np.flatnonzero(derived != events['truth_class'])
    # June/July use archived R00-040 labels. Binary floating arithmetic at
    # exactly +/-$0.10 can disagree with their original representation.
    # Preserve originals for EVERY row; never filter or relabel these events.
    boundary_only = np.abs(np.abs(delta[mismatch]) - .1) <= 1e-9
    if len(mismatch) and not np.all(boundary_only):
        raise ValueError(f'{month}: non-boundary original label mismatch; scoring blocked')
    atomic_json(OUT / f'boundary_{month}.json', {
        'count': int(len(mismatch)), 'original_labels_preserved': True,
        'indices': mismatch.tolist(), 'native_delta': delta[mismatch].tolist(),
        'original_class': events['truth_class'][mismatch].tolist(),
        'rederived_class': derived[mismatch].tolist(),
        'policy_uses_boundary_flag': False,
    })
    np.savez_compressed(arrays, x=x, trajectory=trajectory, scale=scale, valid=valid, **events)
    saved = {'month': month, 'events': len(idx), 'quotes': len(tm), 'source_sha256': sha,
             'cache_sha256': digest(arrays), 'code_sha256': digest(__file__),
             'features': names, 'nonboundary_label_mismatches': 0,
             'boundary_representation_disagreements': int(len(mismatch))}
    atomic_json(receipt, saved)
    log('prepared', month, x.shape, 'original labels preserved; boundary differences',len(mismatch))
    return saved


def views(names):
    micro = [i for i, n in enumerate(names) if not n.startswith(('structure_', 'missing_structure_'))
             and not any(tf in n for tf in ('M1_', 'M5_', 'M15_', 'H1_'))]
    macro = [i for i, n in enumerate(names) if n.startswith(('structure_', 'missing_structure_'))
             or any(tf in n for tf in ('M1_', 'M5_', 'M15_', 'H1_'))
             or n in ('side', 'log_scale', 'sin_hour', 'cos_hour', 'weekday')]
    return {'micro': micro, 'macro': macro, 'joint': list(range(len(names)))}


def fit():
    meta = json.loads((CACHE / '01.json').read_text())
    a = np.load(CACHE / '01.npz')
    x, y, t = a['x'], a['trajectory'], a['t']
    boundary = int(.6 * len(t))
    eligible = (np.arange(len(t)) < boundary) & (t + 65000 < t[boundary]) & a['valid']
    halves = (t // 86400000) % 2
    finite = np.isfinite(y).all(axis=1)
    eligible &= finite
    records = []
    for name, columns in views(meta['features']).items():
        for k in range(12):
            filename = MODEL / f'{name}_{k:02d}.joblib'
            if filename.exists():
                records.append({'model': filename.name, 'sha256': digest(filename)})
                continue
            partition = eligible & (halves == k % 2)
            estimation = eligible & (halves != k % 2)
            tree = ExtraTreeRegressor(max_leaf_nodes=1024, min_samples_leaf=96,
                                      max_features=.7, random_state=1102026 + k)
            # Continuous targets shape partitions; original Y and teacher scores never enter.
            tree.fit(x[partition][:, columns], np.clip(y[partition], -30, 30))
            leaf = tree.apply(x[estimation][:, columns])
            residual = y[estimation, 2]
            order = np.lexsort((residual, leaf))
            leaf, residual = leaf[order], residual[order]
            counts = np.bincount(leaf, minlength=tree.tree_.node_count)
            ends = np.cumsum(counts)
            starts = ends - counts
            obj = {'tree': tree, 'columns': columns, 'starts': starts, 'ends': ends,
                   'residual': residual, 'partition_rows': int(partition.sum()),
                   'estimation_rows': int(estimation.sum()), 'plan_sha256': digest(ROOT / 'PLAN.md')}
            tmp = filename.with_suffix('.tmp')
            joblib.dump(obj, tmp, compress=3)
            os.replace(tmp, filename)
            records.append({'model': filename.name, 'sha256': digest(filename)})
            atomic_json(MODEL / 'checkpoint.json', records)
            log('tree', name, k, obj['partition_rows'], obj['estimation_rows'])
    atomic_json(MODEL / 'manifest.json', {'models': records, 'fit_eligible': int(eligible.sum()),
                 'fit_boundary': int(t[boundary]), 'plan_sha256': digest(ROOT / 'PLAN.md')})


@njit
def leaf_cdf(leaf, start, end, residual, cut):
    output = np.empty(len(leaf), np.float64)
    for i in range(len(leaf)):
        lo, hi = start[leaf[i]], end[leaf[i]]
        count = hi - lo
        if count < 16:
            output[i] = .5  # unsupported leaves abstain via neutral prior
        else:
            left, right = lo, hi
            while left < right:
                m = (left + right) // 2
                if residual[m] <= cut[i]:
                    left = m + 1
                else:
                    right = m
            output[i] = (left - lo + .5) / (count + 1.)
    return output


@njit
def prequential(t, y, p, side, active_after):
    success = np.zeros(60)
    total = np.zeros(60)
    seen = np.zeros(60, np.int64)
    key = np.zeros(len(t), np.int64)
    for i in range(len(t)):
        key[i] = (1 if side[i] > 0 else 0) * 30 + int((t[i] // 3600000) % 24 // 6) * 5 + min(4, int(p[i] * 5))
    result = p.copy()
    cursor = 0
    for i in range(len(t)):
        while cursor < i and t[cursor] + 33001 <= t[i]:
            if t[cursor] >= active_after:
                g = key[cursor]
                stamp = t[cursor] + 33001
                decay = math.exp(-max(0, stamp - seen[g]) * math.log(2) / 1800000)
                total[g] = total[g] * decay + 1
                success[g] = success[g] * decay + (1 if y[cursor] == 0 else 0)
                seen[g] = stamp
            cursor += 1
        g = key[i]
        decay = math.exp(-max(0, t[i] - seen[g]) * math.log(2) / 1800000)
        result[i] = (256 * p[i] + decay * success[g]) / (256 + decay * total[g])
    return result


def score(month):
    a = np.load(CACHE / f'{month}.npz')
    x, scale = a['x'], a['scale']
    probabilities = {}
    for name in ('micro', 'macro', 'joint'):
        pc = np.zeros(len(x))
        po = np.zeros(len(x))
        for k in range(12):
            model = joblib.load(MODEL / f'{name}_{k:02d}.joblib')
            for start in range(0, len(x), 25000):
                end = min(start + 25000, len(x))
                leaf = model['tree'].apply(x[start:end, model['columns']])
                kw = (leaf, model['starts'], model['ends'], model['residual'])
                pc[start:end] += 1 - leaf_cdf(*kw, .1 / scale[start:end])
                po[start:end] += leaf_cdf(*kw, -.1 / scale[start:end])
        probabilities[name + '_correct'] = pc / 12
        probabilities[name + '_opposite'] = po / 12
        log('scored', month, name, len(x))
    pc = np.column_stack([probabilities[name + '_correct'] for name in ('micro', 'macro', 'joint')])
    average, guardian = pc.mean(axis=1), pc.max(axis=1)
    t, y, side = a['t'], a['truth_class'], a['original_side']
    active_after = int(t[int(.6 * len(t))]) if month == '01' else int(t[0])
    calibrated = prequential(t, y, average, side, active_after)
    out = dict(t=t, truth_class=y, original_side=side, teacher_kept=a['kept'],
               distribution=1 - average, guardian=1 - guardian,
               prequential=1 - calibrated, protected=1 - np.maximum(guardian, calibrated),
               **probabilities)
    np.savez_compressed(OUT / f'scores_{month}.npz', **out)
    log('score checkpoint', month)


def cutoff(risk, correct, budget):
    values = np.sort(risk[correct])
    allowed = int(math.floor(len(values) * budget))
    if allowed == 0:
        return float('inf')
    # Strict > threshold ensures ties can never overspend the CAL budget.
    return float(values[-allowed - 1])


def counts(y, veto):
    good, opposite, neutral = y == 0, y == 1, y == 2
    return {'n': len(y), 'original_correct': int(good.sum()),
            'correct_lost': int(np.sum(good & veto)), 'opposite_veto': int(np.sum(opposite & veto)),
            'neutral_veto': int(np.sum(neutral & veto)), 'incorrect_veto': int(np.sum(~good & veto))}


def evaluate():
    policies = ('distribution', 'guardian', 'prequential', 'protected')
    jan = np.load(OUT / 'scores_01.npz')
    n = len(jan['t']); a, b, c = int(.6*n), int(.8*n), int(.9*n)
    thresholds = {p: {str(budget): cutoff(jan[p][a:b], jan['truth_class'][a:b] == 0, budget)
                      for budget in (.01, .05)} for p in policies}
    atomic_json(OUT / 'FROZEN_CAL.json', thresholds)
    rows, group_rows, overlaps = [], [], []
    for month in MONTHS:
        data = np.load(OUT / f'scores_{month}.npz')
        y, t, side = data['truth_class'], data['t'], data['original_side']
        selections = {'FULL_MIXED' if month=='01' else 'FULL_EXPOSED': np.arange(len(y))}
        if month == '01':
            selections.update(FIT=np.arange(a), CAL=np.arange(a,b), VAL=np.arange(b,c), SHADOW=np.arange(c,n))
        masks = {}
        for p in policies:
            for budget, threshold in thresholds[p].items():
                mask = data[p] > threshold
                masks[p + '_' + budget] = mask
                for split, idx in selections.items():
                    result = counts(y[idx], mask[idx])
                    # Same original UTC hour/side, fixed group veto count, exact random expectation.
                    groups = (t[idx] // 3600000)*2+(side[idx]>0)
                    _, inverse = np.unique(groups, return_inverse=True)
                    count = np.bincount(inverse)
                    bad = np.bincount(inverse, weights=y[idx]!=0)
                    veto = np.bincount(inverse, weights=mask[idx])
                    result['random_wrong_expectation'] = float(np.sum(veto * bad / count))
                    rows.append({'month':month, 'split':split, 'policy':p, 'budget':budget, **result})
                for session in range(4):
                    for direction in (-1,1):
                        idx = ((t//3600000)%24//6==session)&(side==direction)
                        group_rows.append({'month':month,'session':session,'side':direction,'policy':p,
                                           'budget':budget,**counts(y[idx],mask[idx])})
        for budget in ('.01', '.05'):
            key = str(float(budget))
            base, guarded = masks['distribution_'+key], masks['protected_'+key]
            overlaps.append({'month':month,'budget':key,
               'additional_veto':counts(y,guarded&~base),'rescued':counts(y,base&~guarded)})
        rows.append({'month':month,'split':'FULL_ORACLE','policy':'ORIGINAL_FITTED_TEACHER',
                     'budget':'original',**counts(y,~data['teacher_kept'])})
        np.savez_compressed(OUT / f'masks_{month}.npz', t=t, original_side=side, truth_class=y, **masks)
    atomic_json(OUT / 'RESULTS.json', {'state':'UNAPPROVED', 'rows':rows,'groups':group_rows,
                                     'overlaps':overlaps,'thresholds':thresholds})
    pd.DataFrame(rows).to_csv(OUT / 'SCORECARD.csv',index=False)
    log('evaluation complete',len(rows),'rows')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare','fit','score','evaluate'])
    parser.add_argument('--month', choices=MONTHS)
    args = parser.parse_args()
    if digest(ARCHIVE) != ARC_SHA:
        raise ValueError('FILTER08 archive mismatch')
    if args.stage == 'prepare': prepare(args.month)
    elif args.stage == 'fit': fit()
    elif args.stage == 'score': score(args.month)
    else: evaluate()


if __name__ == '__main__':
    main()
