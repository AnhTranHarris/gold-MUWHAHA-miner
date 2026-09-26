"""Run unchanged frozen January precompute in a fresh isolated output directory."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import time
import threading
import numpy as np
import pandas as pd
RAW_SHA = 'd2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
CACHE_SHA = '71fc132e208589857dfe5dd6b8b1a204bd626d65c249890e842b6d5647ba65a5'

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

SOURCE_SHA = 'cd761b19617fdd68ec86eb55ab212fd0ecf387750e99f14ec7e00bad57419ab2'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--raw', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    stage = a.out / 'staging'
    stage.mkdir()
    manifest = a.out / 'REGEN_MANIFEST.json'
    source = Path(__file__).with_name('mm_c30_b1b_m01_precompute_opt.py')
    state = {'job_id': 'MM-C30-B1B-M01-CACHE-REGEN', 'status': 'PREFLIGHT',
             'started_unix': time.time(), 'pid': os.getpid(), 'scope': 'January engineering only; no economics',
             'expected_historical_npz_sha256': CACHE_SHA, 'source_sha256': digest(source), 'raw_sha256': digest(a.raw)}
    atomic_json(manifest, state)
    try:
        if state['source_sha256'] != SOURCE_SHA or state['raw_sha256'] != RAW_SHA:
            raise ValueError('Frozen source or January raw hash mismatch')
        tree = ast.parse(source.read_text(), filename=str(source))
        functions = [x for x in tree.body if isinstance(x, ast.FunctionDef)]
        cache = stage / 'MM_C30_B1B_M01_CAUSAL_CACHE.npz'
        result = stage / 'MM_C30_B1B_M01_PRECOMPUTE_RESULT.json'
        ns = dict(json=json, time=time, hashlib=hashlib, Path=Path, np=np, pd=pd,
                  RAW=a.raw, OUT=stage, CACHE=cache, RESULT=result)
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), ns)
        state['status'] = 'RUNNING_VERIFIED'
        atomic_json(manifest, state)
        stopped = threading.Event()
        def heartbeat():
            while not stopped.is_set():
                atomic_json(a.out / 'HEARTBEAT.json', {'status': 'RUNNING_VERIFIED', 'pid': os.getpid(), 'unix_time': time.time()})
                stopped.wait(2)
        worker = threading.Thread(target=heartbeat, daemon=True)
        worker.start()
        try:
            ns['main']()
        finally:
            stopped.set()
            worker.join()
        metadata = json.loads(result.read_text())
        actual = digest(cache)
        arrays = {}
        with np.load(cache, allow_pickle=False) as z:
            for key in z.files:
                v = z[key]
                arrays[key] = {'shape': list(v.shape), 'dtype': str(v.dtype),
                               'sha256_c_order': hashlib.sha256(v.tobytes(order='C')).hexdigest()}
        if metadata['raw_rows'] != 9135062 or metadata['active_seconds'] != 1526214:
            raise ValueError('Frozen January dimensional invariant mismatch')
        state.update(status='COMPLETED_LOCAL' if actual == CACHE_SHA else 'BLOCKED_CACHE_IDENTITY',
                     regenerated_cache_sha256=actual, exact_historical_cache_match=(actual == CACHE_SHA),
                     arrays=arrays, metadata=metadata,
                     elapsed_seconds=time.time()-state['started_unix'])
        os.replace(cache, a.out / cache.name)
        os.replace(result, a.out / result.name)
        atomic_json(manifest, state)
        atomic_json(a.out / 'HEARTBEAT.json', {'status': state['status'], 'pid': os.getpid(), 'unix_time': time.time()})
        print(json.dumps(state, indent=2, sort_keys=True))
        return 0 if actual == CACHE_SHA else 2
    except Exception as exc:
        state.update(status='BLOCKED_ERROR', error_type=type(exc).__name__, error=str(exc))
        atomic_json(manifest, state)
        raise

if __name__ == '__main__':
    raise SystemExit(main())
