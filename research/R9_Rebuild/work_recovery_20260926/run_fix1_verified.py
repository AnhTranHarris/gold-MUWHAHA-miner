"""Baseline-first FIX1 forensic replay; never imports source module side effects."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import time

import numpy as np
import pandas as pd
from numba import njit

JOB = 'MM-C30-B1B-M01-REPLAY-EQUIV-FIX1'
RAW_SHA = 'd2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
CACHE_SHA = '71fc132e208589857dfe5dd6b8b1a204bd626d65c249890e842b6d5647ba65a5'
SOURCE_SHA = '5f7e82378587898d571b920050fc6ae42480fda648efaa81c832ae1705a639b3'
BASELINE_NET = -6245.249
BASELINE_TOLERANCE = 0.0005  # Historical net reported to 0.001 USD.

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def atomic_json(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)

def load_functions(path):
    # Execute only the three unchanged definitions needed; bypass legacy OUT mkdir/main.
    tree = ast.parse(path.read_text(), filename=str(path))
    names = {'metrics', 'session_for_sec', 'replay'}
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in selected} == names
    namespace = {'np': np, 'njit': njit}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--variants-after-baseline', action='store_true')
    args = parser.parse_args()
    # Refuse overwrite/reuse of an existing run directory.
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.time()
    source = Path(__file__).with_name('mm_c30_b1b_m01_replay_equiv_fix1_UNEXECUTED.py')
    state = {'job_id': JOB, 'status': 'PREFLIGHT', 'started_unix': started,
             'baseline_expected_net': BASELINE_NET, 'baseline_tolerance': BASELINE_TOLERANCE,
             'baseline_equivalent': False, 'source_equivalent': False,
             'scientific_classification': 'SOURCE_EQUIVALENCE_ONLY',
             'oos_access': 'NONE; January only; August sealed', 'metrics': {}}
    manifest = args.out / 'FIX1_MANIFEST.json'
    atomic_json(manifest, state)
    try:
        for label, path, expected in [('source', source, SOURCE_SHA), ('raw', args.raw, RAW_SHA), ('cache', args.cache, CACHE_SHA)]:
            actual = digest(path)
            state[label + '_sha256'] = actual
            if actual != expected:
                raise ValueError(f'{label} SHA mismatch: {actual} != {expected}')
        functions = load_functions(source)
        keys = ['sec_ids', 's1_disp', 's1_eff', 's1_range', 's1_turns', 'm5_atr', 'align_long', 'align_short']
        with np.load(args.cache, allow_pickle=False) as z:
            arrays = [z[key] for key in keys]
        n = len(arrays[0])
        if any(x.ndim != 1 or len(x) != n for x in arrays):
            raise ValueError('Cache columns are not aligned one-dimensional vectors')
        if np.any(arrays[0][1:] <= arrays[0][:-1]):
            raise ValueError('Cache seconds are not strictly increasing')
        frame = pd.read_csv(args.raw, compression='gzip', usecols=['timestamp_ms_utc', 'ask_raw', 'bid_raw'],
                            dtype={'timestamp_ms_utc': 'int64', 'ask_raw': 'int32', 'bid_raw': 'int32'})
        ticks = frame.timestamp_ms_utc.to_numpy(np.int64, copy=False)
        if len(ticks) != 9135062 or np.any(ticks[1:] < ticks[:-1]):
            raise ValueError('Unexpected January tick count/order')
        ask = frame.ask_raw.to_numpy(np.float64) / 1000.
        bid = frame.bid_raw.to_numpy(np.float64) / 1000.
        mid = (ask + bid) * .5
        state.update(status='RUNNING_VERIFIED', pid=os.getpid(), ticks=len(ticks), active_seconds=n)
        atomic_json(manifest, state)
        pnl, hold, promoted = functions['replay'](ticks, mid, *arrays, 0)
        state['metrics']['baseline'] = functions['metrics'](pnl, hold, promoted)
        error = state['metrics']['baseline']['net'] - BASELINE_NET
        state.update(baseline_error=error, baseline_equivalent=bool(abs(error) <= BASELINE_TOLERANCE))
        atomic_json(args.out / 'FIX1_BASELINE.json', state)
        if not state['baseline_equivalent']:
            state.update(status='BLOCKED_SOURCE_EQUIVALENCE', exact_next_task='Source archaeology; no variant interpretation')
        elif not args.variants_after_baseline:
            state.update(status='COMPLETED_LOCAL_BASELINE_ONLY', exact_next_task='Persist baseline then evaluate frozen Rule10 variants')
        else:
            for mode, name in [(1, 'promote_preserve_stop'), (2, 'promote_reset_stop')]:
                pnl, hold, promoted = functions['replay'](ticks, mid, *arrays, mode)
                row = functions['metrics'](pnl, hold, promoted)
                row['delta_vs_baseline'] = row['net'] - state['metrics']['baseline']['net']
                row['target_delta_error'] = row['delta_vs_baseline'] - 63.60
                state['metrics'][name] = row
                atomic_json(args.out / (name + '.json'), row)
            errors = {name: abs(row['target_delta_error']) for name, row in state['metrics'].items() if name != 'baseline'}
            closest = min(errors, key=errors.get)
            state.update(closest_semantic=closest, closest_abs_target_error=errors[closest],
                         source_equivalent=bool(errors[closest] <= .50),
                         status='COMPLETED_LOCAL', checksum_tolerance=.50)
        state['elapsed_seconds'] = time.time() - started
        atomic_json(args.out / 'FIX1_RESULT.json', state)
        state['result_sha256'] = digest(args.out / 'FIX1_RESULT.json')
        atomic_json(manifest, state)
        print(json.dumps(state, indent=2, sort_keys=True, allow_nan=False))
        return 0 if state['baseline_equivalent'] else 2
    except Exception as exc:
        state.update(status='BLOCKED_ERROR', error_type=type(exc).__name__, error=str(exc), elapsed_seconds=time.time() - started)
        atomic_json(manifest, state)
        raise

if __name__ == '__main__':
    raise SystemExit(main())
