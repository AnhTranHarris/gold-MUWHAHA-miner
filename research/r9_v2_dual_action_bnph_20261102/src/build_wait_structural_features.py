"""Combine frozen WAIT+fitted-intensity view with full rolling 5m structural state."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from structural_5m_features import STRUCTURAL_5M_VERSION,STRUCTURAL_5M_COUNT

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def main(a):
 st=time.monotonic();base=Path(a.base);struct=Path(a.structural);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);name=f'coinexx_01_{a.day}'
 B=np.load(base/f'{name}_wait_transition_hawkes_X.npy',mmap_mode='r');S=np.load(struct/f'{name}_structural_5m_X.npy',mmap_mode='r')
 if len(B)!=len(S) or S.shape[1]!=STRUCTURAL_5M_COUNT:raise ValueError('combined structural contract')
 Z=np.column_stack((np.asarray(B,np.float32),np.asarray(S,np.float32))).astype(np.float32);p=out/f'{name}_wait_structural_X.npy';np.save(p,Z,allow_pickle=False)
 r=dict(day=a.day,version='r9_v2_wait_plus_fitted_excitation_plus_full5m_structural_v2',rows=len(Z),features=Z.shape[1],base_features=B.shape[1],structural_version=STRUCTURAL_5M_VERSION,structural_features=STRUCTURAL_5M_COUNT,matrix_sha256=sha256(p),base_sha256=sha256(base/f'{name}_wait_transition_hawkes_X.npy'),structural_sha256=sha256(struct/f'{name}_structural_5m_X.npy'),runtime_uses_future=False,elapsed_sec=round(time.monotonic()-st,2))
 (out/f'{name}_receipt.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--structural',required=True);p.add_argument('--day',required=True);p.add_argument('--out',required=True);main(p.parse_args())