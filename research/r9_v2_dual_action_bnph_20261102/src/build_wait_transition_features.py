"""Build causal WAIT transition feature shards from repaired v5 candidate matrices."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from timing_transition_features import build_timing_features,wait_improves_target,TIMING_FEATURE_VERSION,TIMING_FEATURE_COUNT

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def main(a):
 t0=time.monotonic();root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);base=f'coinexx_01_{a.day}'
 src=root/f'{base}_250ms_v5_X.npy';teacher=root/f'{base}_250ms_universe.npz';X=np.load(src,mmap_mode='r');d=np.load(teacher)
 z=build_timing_features(X,d['ts']);p=out/f'{base}_wait_transition_X.npy';np.save(p,z,allow_pickle=False);y,valid=wait_improves_target(d,a.max_wait_ms)
 r=dict(day=a.day,version=TIMING_FEATURE_VERSION,rows=len(z),features=TIMING_FEATURE_COUNT,positive=int(y.sum()),positive_rate=float(y.mean()),next_within_wait=int(valid.sum()),matrix_sha256=sha256(p),source_v5_matrix_sha256=sha256(src),teacher_sha256=sha256(teacher),runtime_uses_future=False,elapsed_sec=round(time.monotonic()-t0,2))
 (out/f'{base}_wait_transition_receipt.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--day',required=True);p.add_argument('--out',required=True);p.add_argument('--max-wait-ms',type=int,default=1000);main(p.parse_args())
