"""Append fitted strict-prior-slot intensities to frozen WAIT transition features."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from build_repaired_matrix import load_raw
from fitted_intensity_features import candidate_fitted_intensities,FITTED_INTENSITY_COUNT
from timing_transition_features import TIMING_FEATURE_COUNT
def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def main(a):
 t0=time.monotonic();root=Path(a.root);tim=Path(a.timing);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);base=f'coinexx_01_{a.day}';d=np.load(root/f'{base}_250ms_universe.npz');T=np.load(tim/f'{base}_wait_transition_X.npy',mmap_mode='r');t,bid,ask=load_raw(Path(a.raw),'coinexx','01');F=candidate_fitted_intensities(t,bid,ask,a.day,d['ts'],a.model);Z=np.column_stack((np.asarray(T,np.float32),F)).astype(np.float32);p=out/f'{base}_wait_transition_hawkes_X.npy';np.save(p,Z,allow_pickle=False)
 r=dict(day=a.day,version='r9_v2_wait_transition_plus_fitted_excitation_v1',rows=len(Z),features=Z.shape[1],base_timing_features=TIMING_FEATURE_COUNT,fitted_intensity_features=FITTED_INTENSITY_COUNT,matrix_sha256=sha256(p),fitted_excitation_model_sha256=sha256(Path(a.model)),runtime_uses_future=False,strict_prior_slot_intensity=True,elapsed_sec=round(time.monotonic()-t0,2));(out/f'{base}_receipt.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--timing',required=True);p.add_argument('--raw',required=True);p.add_argument('--model',required=True);p.add_argument('--day',required=True);p.add_argument('--out',required=True);main(p.parse_args())
