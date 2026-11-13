"""Source-locked 9-month Coinexx as-of screened indicators."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np,pandas as pd
from signal_features import sequential_state,FEATURE_NAMES

ROOT=Path('/mnt/data/r9_m60_priority_screen')
RAW=Path('/mnt/data')
RECEIPT=json.loads(Path('/mnt/data/r9_m60_expanded/source_receipt.json').read_text())['source_months']

def hash_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def run_month(mm):
    src=RAW/f'XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz'
    expected=RECEIPT[mm]
    sha=hash_file(src)
    if sha!=expected['source_sha256']:raise ValueError(f'SOURCE HASH mismatch: {mm}')
    df=pd.read_csv(src,usecols=['time_msc','bid','ask'],dtype={'time_msc':np.int64,'bid':np.float64,'ask':np.float64})
    t=df.time_msc.to_numpy(np.int64,copy=True)
    bid=np.rint(df.bid.to_numpy(np.float64)*100).astype(np.int32)
    ask=np.rint(df.ask.to_numpy(np.float64)*100).astype(np.int32)
    del df
    if len(t)!=expected['rows'] or (np.diff(t)<0).any() or (ask<bid).any():raise ValueError('source chronology/quote invalid')
    old=np.load(f'/mnt/data/r9_m60_competing/derived/event_2026_{mm}.npz',allow_pickle=False)
    ordinal0=sum(RECEIPT[f'{i:02}']['rows'] for i in range(1,int(mm)))
    entry=(old['ordinal']-ordinal0-1).astype(np.int64)
    if not np.array_equal(t[entry],old['entry']):raise ValueError('frozen ordinal mismatch')
    if (np.diff(entry)<=0).any():raise ValueError('entry ordering invalid')
    features=sequential_state(t,bid,ask,entry)
    if not np.isfinite(features).all():raise ValueError('nonfinite features')
    out=ROOT/'derived'/f'priority_2026_{mm}.npz'
    np.savez_compressed(out,features=features,entry=old['entry'],ordinal=old['ordinal'],feature_names=np.array(FEATURE_NAMES))
    result={'month':mm,'source_sha256':sha,'source_ticks':len(t),'frozen_entries':len(entry),'output_sha256':hash_file(out),
            'nonzero_cusum':int(np.count_nonzero(features[:,2])),
            'signed_250ms_activity_nonzero':int(np.count_nonzero(features[:,6]))}
    (ROOT/'derived'/f'receipt_2026_{mm}.json').write_text(json.dumps(result,indent=2)+'\n')
    print('EXTRACTED',mm,'rows',len(t),'entries',len(entry),'nonzero_CUSUM',result['nonzero_cusum'],flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--months',nargs='+',default=[f'{i:02}' for i in range(1,10)])
    args=p.parse_args();[run_month(mm) for mm in args.months]
