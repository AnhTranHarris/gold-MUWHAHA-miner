"""R00-076D3: purged original-January expanding OOF index builder only.

Inputs are existing protected original R00-076D2 quote-index-aligned event times.
This does not train/score models or change the event generator and broker reader.
"""
from __future__ import annotations
from pathlib import Path
import json,hashlib
import numpy as np

PURGE_MS=32000

def folds(t,num_validation_folds=5,purge_ms=PURGE_MS):
    t=np.asarray(t,dtype=np.int64)
    if len(t)<(num_validation_folds+1)*100 or np.any(np.diff(t)<0) or purge_ms<32000:
        raise ValueError('chronology/fold/purge invalid')
    n=len(t)
    edges=np.linspace(0,n,num_validation_folds+2,dtype=np.int64)
    result=[]
    for k in range(num_validation_folds):
        a=int(edges[k+1]);end=int(edges[k+2])
        valid=np.arange(a,end,dtype=np.int64)
        first=t[a]
        train_end=int(np.searchsorted(t[:a],first-purge_ms,side='right'))
        train=np.arange(0,train_end,dtype=np.int64)
        assert len(train)>0 and len(valid)>0
        assert t[train[-1]]+purge_ms<=t[valid[0]]
        assert np.intersect1d(train,valid).size==0
        result.append((train,valid))
    return result

def sha(path):
    with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def build_from_existing_original_cache(cache_dir, output_dir):
    cache_dir=Path(cache_dir);output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    results={}
    for b in ('coinexx','dukascopy'):
        original=cache_dir/f'NATIVE_D_{b}_01.npz'
        with np.load(original,allow_pickle=False) as z:
            t=z['ts_ms'].copy();idx=z['quote_index'].copy()
        assert len(t)==len(idx) and np.all(np.diff(idx)>=0)
        dest=output_dir/f'R00_076D3_JAN_PURGED_OOF_{b}.npz'
        save={};details=[]
        for k,(tr,va) in enumerate(folds(t)):
            save[f'train_{k}']=tr;save[f'validation_{k}']=va
            details.append({
                'fold':k,'train_count':len(tr),'valid_count':len(va),
                'train_last_quote_index':int(idx[tr[-1]]),
                'validation_first_quote_index':int(idx[va[0]]),
                'train_last_UTC_ms':int(t[tr[-1]]),
                'validation_first_UTC_ms':int(t[va[0]]),
                'purge_UTC_ms':int(t[va[0]]-t[tr[-1]]),
                'prefix_leakage':False
            })
        np.savez_compressed(dest,**save)
        results[b]={'original_Jan_source_cache_sha256':sha(original),
                    'original_jan_events':len(t),
                    'original_source_quote_indices_preserved':True,
                    'fold_file_sha256':sha(dest),
                    'folds':details,'status':'OOF_INDICES_ONLY_NOT_MODEL_TRAINED'}
    output=output_dir/'R00_076D3_JAN_PURGED_OOF_RECEIPT.json'
    output.write_text(json.dumps({'minimum_purge_ms':PURGE_MS,
        'has_fit_any_models':False,'brokers':results},indent=2)+'\n')
    return output
