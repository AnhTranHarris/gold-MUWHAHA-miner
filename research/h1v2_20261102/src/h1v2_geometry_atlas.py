"""H1V2 offline geometry atlas: raw-causal 99-feature quote state + oracle labels.

Atlas is sampled, not an exhaustive policy backtest; it is NOT an accepted
trading student. All lookahead appears only in y and optional oracle flags.
"""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import numpy as np
from h1v2_teacher import read_ticks,MONTHS,digest
from h1v2_geometry import extract_raw_geometry,NAMES

def build(month,raw_root='/mnt/data',results='/mnt/data/h1v2/results',sample_size=20000,seed=20261102):
    if month not in MONTHS:raise ValueError(month)
    raw=Path(raw_root)/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
    teacher=Path(results)/f'h1v2_dukascopy_{month}_oracle_labels.npz'
    if not teacher.is_file():raise FileNotFoundError(teacher)
    t,b,a=read_ticks(raw)
    with np.load(teacher,allow_pickle=False) as d:
        ix=d['tick_index'];y=d['code'];oracle=d['selected_row']
        assert np.all(t[ix]==d['t'])
        if len(y)!=len(ix):raise ValueError('teacher length inconsistency')
        n=min(len(ix),sample_size)
        rng=np.random.default_rng(seed+int(month))
        rows=np.sort(rng.choice(len(ix),size=n,replace=False)).astype(np.int64)
        label=np.where(y[rows,0]==1,1,np.where(y[rows,1]==1,2,0)).astype(np.int8)
        idx=ix[rows]
        geometry=extract_raw_geometry(t,b,a,idx)
        spread=np.asarray(a[idx]-b[idx],dtype=np.float32)[:,None]
        X=np.hstack((geometry,spread))
        assert np.isfinite(X).all()
        selection=np.isin(rows,oracle,assume_unique=True).astype(np.int8)
        p=Path(results)/f'h1v2_{month}_causal_geometry_atlas.npz'
        np.savez(p,X=X,y=label,ts=t[idx],ix=idx,original_row=rows,oracle_selected=selection)
        report={'month':month,'raw_sha256':digest(raw),'oracle_teacher_sha256':digest(teacher),
                'atlas_sha256':digest(p),'source_rows':len(ix),'sample_rows':len(rows),
                'labels':{key:int((label==k).sum()) for k,key in enumerate(('NO_GOOD','BUY_GOOD','SELL_GOOD'))},
                'feature_names':list(NAMES)+['spread'],'geometry_provenance':'repaired OrderedQuoteGeometry parity 16 Jan raw samples',
                'status':'CAUSAL_FEATURES_HINDSIGHT_LABELS_OFFLINE_ONLY'}
        (Path(results)/f'h1v2_{month}_atlas_receipt.json').write_text(json.dumps(report,indent=2))
        return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--month',choices=MONTHS,required=True)
    ap.add_argument('--raw-root',default='/mnt/data');ap.add_argument('--results',default='/mnt/data/h1v2/results')
    ap.add_argument('--sample-size',type=int,default=20000)
    args=ap.parse_args();print(json.dumps(build(args.month,args.raw_root,args.results,args.sample_size),indent=2))
if __name__=='__main__':main()
