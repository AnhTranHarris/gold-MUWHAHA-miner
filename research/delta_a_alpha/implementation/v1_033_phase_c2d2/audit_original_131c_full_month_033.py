"""Read-only full-month original 131C grid ENTRY event parity on genuine Dukascopy quotes.

Source code: JAN032 original tar :: source/general_session_state_discovery_131c.py,
function build_events, imported unchanged. The Python online counterpart is
original_online_sources_033c.Original131CSessionGridL1.

Does NOT trade and does NOT assert complete V1 funded economic parity.
"""
from __future__ import annotations
import argparse, ast, hashlib, json, time
from pathlib import Path
import numpy as np
import pandas as pd
from v1_funded_core_033c import Quote
from original_online_sources_033c import Original131CSessionGridL1

EXPECTED = {
    'jan': 'd2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
    'feb': 'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
}
SOURCE_SHA256 = '3a96a63ea547942ae06a800ebe0a0cd25fed69b618b92f913a6844235b3206a4'
FILES = {'jan': 'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',
         'feb': 'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(2**22), b''):
            h.update(b)
    return h.hexdigest()


def load_verified_original_build_events(source_dir: Path):
    """Extract the untouched original function body from verified JAN032 source.

    Original @numba.njit decorator is omitted for dependency-free fixture CI.
    Function body and constants are not rewritten or substituted.
    """
    path = source_dir / 'general_session_state_discovery_131c.py'
    if digest(path) != SOURCE_SHA256:
        raise ValueError('Original JAN032 131C source-member checksum mismatch')
    tree = ast.parse(path.read_text())
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == 'build_events')
    fn.decorator_list = []
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    environment = {'np': np}
    exec(compile(module, str(path) + ':build_events', 'exec'), environment)
    try:
        from numba import njit
    except ImportError:
        return environment['build_events']
    return njit(cache=False)(environment['build_events'])


def audit(month, root, source_dir, step):
    path = root / FILES[month]
    observed_sha = digest(path)
    if observed_sha != EXPECTED[month]:
        raise ValueError(f'Unverified raw tick input: {month}: {observed_sha}')
    # Source is exact original Python, NOT our re-derived formula.
    build_events = load_verified_original_build_events(source_dir)
    chunks = []
    for chunk in pd.read_csv(path, compression='gzip',
                             usecols=['timestamp_ms_utc', 'ask_raw', 'bid_raw'],
                             dtype={'timestamp_ms_utc': np.int64,
                                    'ask_raw': np.int32, 'bid_raw': np.int32},
                             chunksize=600000):
        chunks.append(chunk)
    arr = pd.concat(chunks, ignore_index=True)
    t = arr.timestamp_ms_utc.to_numpy(dtype=np.int64, copy=False)
    a = arr.ask_raw.to_numpy(dtype=np.int64, copy=True)
    b = arr.bid_raw.to_numpy(dtype=np.int64, copy=True)
    if np.any(np.diff(t) < 0) or np.any(a < b) or np.any(b <= 0):
        raise ValueError('Invalid tick ordering / quote crossing')
    mid = (a + b) // 2
    start = time.monotonic()
    original_idx, original_dir = build_events(t, mid, step)
    run_ref_s = round(time.monotonic() - start, 3)
    model = Original131CSessionGridL1(step_raw=step)
    online_idx, online_dir = [], []
    start = time.monotonic()
    for i, (ms, ask, bid) in enumerate(zip(t, a, b)):
        for ev in model.on_tick(Quote(int(ms), int(ask), int(bid))):
            online_idx.append(i)
            online_dir.append(ev.direction)
    run_online_s = round(time.monotonic() - start, 3)
    out_i = np.asarray(online_idx, dtype=np.int64)
    out_d = np.asarray(online_dir, dtype=np.int8)
    same = bool(np.array_equal(original_idx, out_i) and np.array_equal(original_dir, out_d))
    first = None
    if not same:
        for i in range(min(len(out_i), len(original_idx))):
            if original_idx[i] != out_i[i] or original_dir[i] != out_d[i]:
                first = (i, int(original_idx[i]), int(original_dir[i]), int(out_i[i]), int(out_d[i])); break
    return {'month': month, 'sha256_verified': observed_sha,
            'quotes': len(t), 'first_time_ms': int(t[0]), 'last_time_ms': int(t[-1]),
            'original_reference': 'JAN032/source/general_session_state_discovery_131c.py::build_events',
            'online_adapter': 'original_online_sources_033c.py::Original131CSessionGridL1',
            'step_raw': step, 'original_events': int(len(original_idx)),
            'online_events': len(online_idx), 'event_index_direction_identical': same,
            'first_mismatch': first, 'reference_seconds': run_ref_s, 'online_seconds': run_online_s,
            'economic_claim': 'NONE__L1_EVENT_MANUFACTURE_PARITY_ONLY__NOT_COMPLETE_V1'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='/mnt/data')
    ap.add_argument('--source-dir', default=str(Path(__file__).resolve().parent / 'verified_original_sources'))
    ap.add_argument('--out', default='/mnt/data/C2D3C_ORIGINAL_L1_JAN_FEB_PARITY.json')
    args = ap.parse_args()
    root, src = Path(args.root), Path(args.source_dir)
    result = []
    for month in ['jan', 'feb']:
        for step in [250, 75]:
            item = audit(month, root, src, step)
            print('L1_PARITY', json.dumps(item), flush=True)
            result.append(item)
            if not item['event_index_direction_identical']:
                raise AssertionError(f'Original 131C stream mismatch: {month}:{step}')
    Path(args.out).write_text(json.dumps({'gate':'DAA_033_L1_SOURCE_FUNCTIONAL_PARITY',
                          'results': result, 'parity': 'PASS'}, indent=2)+'\n')
if __name__ == '__main__':main()