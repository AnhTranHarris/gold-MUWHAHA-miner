"""Build exactly 8 original R00 events x causal PRE-t0 authorized native quote prefixes.
Raw source SHA fail closed; archived t/side/truth immutable; output derivatives unapproved.
"""
import argparse, io, json, pathlib, sys, time, zipfile
import numpy as np
from r37_native_pre_t0_features import read_native_ticks,feature_matrix,digest
SOURCE_SHA='c993a258987387737b6c909d3f18699633f9159fa077be653c93ad5afa506e8f'

def main():
 a=argparse.ArgumentParser();a.add_argument('--raw',default='/mnt/data');a.add_argument('--out',default='/mnt/data/r37_mdk01_unapproved/eight_original_cells');a.add_argument('--months',default='01,02,06,07');a.add_argument('--brokers',default='coinexx,dukascopy');args=a.parse_args()
 raw=pathlib.Path(args.raw);out=pathlib.Path(args.out);out.mkdir(exist_ok=True,parents=True)
 parent=raw/'F401_R17_VERIFIED_FULL_ORIGINAL_REASSEMBLED_20261027.zip'
 if digest(parent)!=SOURCE_SHA:raise ValueError('R17 original SHA mismatch')
 z=zipfile.ZipFile(parent);manifest=json.loads(z.read('F401_R17_FULL_MEMBER_SHA256_MANIFEST.json'))['archive_contents']
 import hashlib
 manifestfile=out/'R37_EIGHTCELL_PREFIX_MANIFEST.json'
 results=json.loads(manifestfile.read_text()) if manifestfile.exists() else []
 for broker in args.brokers.split(','):
  for mo in args.months.split(','):
   start=time.time();n=f'F401_R17_{broker}_{mo}_SOURCE_ONLY_FROZEN_2POLICY_ORIGINAL_MASK.npz';payload=z.read(n)
   if hashlib.sha256(payload).hexdigest()!=manifest[n]['sha256']:raise ValueError('event source payload SHA mismatch')
   src=np.load(io.BytesIO(payload),allow_pickle=False)
   t0=src['t'].copy();side=src['side'].copy();truth=src['truth'].copy()
   name=(f'XAUUSD_MT5_BROKER_2026_{mo}_ticks_ALL.csv.gz' if broker=='coinexx' else f'XAUUSD_DUKAS_2026_{mo}_ticks.csv.gz')
   t,bid,ask,sha=read_native_ticks(raw/name,broker,mo)
   X,features,valid=feature_matrix(t,bid,ask,t0,side)
   nout=out/f'R37_{broker}_{mo}_ORIGINAL_T0_PREFIX.npz'
   np.savez_compressed(nout,t=t0,side=side,truth=truth,valid=valid,X=X)
   rec={'broker':broker,'month':mo,'source_sha256':sha,'original_R17_payload_sha256':manifest[n]['sha256'],'event_count':len(t0),'source_tick_count':len(t),'source_event_t0_strictly_before':True,'native_prefix_valid':int(valid.sum()),'original_correct':int((truth==0).sum()),'original_wrong':int((truth!=0).sum()),'feature_count':len(features),'feature_names':features,'derivative_file':nout.name,'derivative_sha256':digest(nout),'elapsed_seconds':round(time.time()-start,1)}
   results=[r for r in results if (r['broker'],r['month'])!=(broker,mo)]+[rec]
   manifestfile.write_text(json.dumps(sorted(results,key=lambda r:(r['broker'],r['month'])),indent=2))
   print('PREFIX',broker,mo,'events',len(t0),'quotes',len(t),'valid',valid.sum(),'sec',rec['elapsed_seconds'],flush=True)
   del t,bid,ask,X,src
 z.close()
 print('COMPLETE',len(results),'cells',sum(x['event_count'] for x in results),flush=True)
if __name__=='__main__':main()
