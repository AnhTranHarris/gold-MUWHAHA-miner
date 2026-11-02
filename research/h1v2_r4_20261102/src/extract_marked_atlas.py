"""Four-month exact source-mark as-of feature construction."""
from pathlib import Path
import numpy as np, json, hashlib,sys
from marked_quote_sequences import extract,mark_quotes,NAMES
from h1v2_teacher import read_ticks
from h1v2_freeze import PINNED
MONTHS=('01','02','06','07')

def run(raw_root='/mnt/data',label_root='/mnt/data/h1v2_r2/results',output='/mnt/data/h1v2_r4/results'):
    out=Path(output);out.mkdir(parents=True,exist_ok=True);receipts={}
    for m in MONTHS:
        p=Path(raw_root)/f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz'
        sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==PINNED[m],m
        t,b,a=read_ticks(p)
        with np.load(Path(label_root)/f'H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz',allow_pickle=False) as d:
            idx=d['ix']; assert np.array_equal(t[idx],d['ts'])
            klass=d['side_class'].copy()
        X=extract(t,b,a,idx,mark_quotes(b,a))
        assert np.isfinite(X).all() and X.shape==(15000,92)
        destination=out/f'H1V2_R4_MARKED_ATLAS_{m}.npz'
        np.savez_compressed(destination,ix=idx,ts=t[idx],Xmark=X,side_class=klass)
        sh=hashlib.sha256(destination.read_bytes()).hexdigest()
        receipts[m]={'ticks':len(t),'rows':len(idx),'features':X.shape[1],'raw_sha256':sha,'atlas_sha256':sh,
          'classes':np.bincount(klass.ravel(),minlength=4).tolist()}
        print('FEATURES',m,receipts[m],flush=True)
    (out/'R4_MARKED_SOURCE_RECEIPTS.json').write_text(json.dumps({'provenance':'quote-ordinal past-only, future labels separate','features':list(NAMES),'months':receipts},indent=2))
    return receipts
if __name__=='__main__':run()
