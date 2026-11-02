"""Attach source-exact v4 causal features to a corrected 250 ms teacher shard."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from build_repaired_matrix import load_raw
from raw_repaired_features import build_repaired_raw_features
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT,REPAIRED_FEATURE_NAMES

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()

def main(a):
    start=time.monotonic();raw=Path(a.raw);teacher=Path(a.teacher);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    with np.load(teacher) as d:idx=d['idx'].copy();ts=d['ts'].copy()
    t,bid,ask=load_raw(raw,a.source,a.month)
    if not np.array_equal(t[idx],ts):raise ValueError('teacher/raw index mismatch')
    X=build_repaired_raw_features(t,bid,ask,idx,a.chunk_rows)
    dest=out/(teacher.stem.replace('_250ms_universe','_250ms_v4_X')+'.npy');np.save(dest,X,allow_pickle=False)
    receipt=dict(source=a.source,month=a.month,teacher=teacher.name,feature_version=FEATURE_VERSION,rows=len(X),features=REPAIRED_FEATURE_COUNT,
        raw_tick_sha256=sha256(raw),teacher_sha256=sha256(teacher),feature_matrix_sha256=sha256(dest),feature_names=list(REPAIRED_FEATURE_NAMES),
        all_feature_names_unique=len(REPAIRED_FEATURE_NAMES)==len(set(REPAIRED_FEATURE_NAMES)),runtime_uses_future=False,
        old_specialist_direction_nomination_used=False,status='250MS_CAUSAL_FEATURE_SHARD_NOT_POLICY',elapsed_sec=round(time.monotonic()-start,2))
    rp=out/(dest.stem+'_receipt.json');rp.write_text(json.dumps(receipt,indent=2));print(json.dumps({k:v for k,v in receipt.items() if k!='feature_names'},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',choices=('coinexx','dukascopy'),required=True);p.add_argument('--month',required=True);p.add_argument('--raw',required=True);p.add_argument('--teacher',required=True);p.add_argument('--out',required=True);p.add_argument('--chunk-rows',type=int,default=25000);main(p.parse_args())
