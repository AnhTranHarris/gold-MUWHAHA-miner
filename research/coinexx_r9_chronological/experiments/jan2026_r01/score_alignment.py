"""Sparse maximum-cardinality R9-to-REAL trade alignment; reference labels NEVER enter replay."""
from __future__ import annotations
import json,sys,os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

REFERENCE=os.environ.get('R9_REFERENCE_MANIFEST',str(Path(__file__).with_name('2026-01_ALL_27980_TRADES_manifest.csv')))

def match_batch(refs, got, tolerance, mode):
  re,rx,rs=refs
  ge,gx,gs,gn=got
  adj=[(np.flatnonzero(gs==side),) for side in (-1,1)]
  lookup={s:np.flatnonzero(gs==s) for s in (-1,1)}
  # GOT is globally sorted by entry time; side-filtered arrays also sorted.
  ranges={s:(lookup[s],ge[lookup[s]]) for s in (-1,1)}
  indptr=[0]; ix=[]
  for j in range(len(re)):
    si=int(rs[j]); indices, entry=ranges[si]
    a=int(np.searchsorted(entry,re[j]-tolerance,'left'))
    b=int(np.searchsorted(entry,re[j]+tolerance,'right'))
    if a<b:
      cand=indices[a:b]
      if mode=='joint':cand=cand[np.abs(gx[cand]-rx[j])<=tolerance]
      elif mode=='hold5':cand=cand[np.abs(gx[cand]-rx[j])<=max(1,int(.05*(rx[j]-re[j])))]
      ix.extend(cand.tolist())
    indptr.append(len(ix))
  mat=csr_matrix((np.ones(len(ix),dtype=np.int8),np.asarray(ix,dtype=np.int32),np.asarray(indptr,dtype=np.int32)),shape=(len(re),len(ge)))
  assigned=maximum_bipartite_matching(mat,perm_type='column')
  valid=assigned[assigned>=0]
  return {'matched':len(valid),'pct_original':round(100*len(valid)/len(re),3),'matched_real_positive':int((gn[valid]>0).sum()),'edges':len(ix)}

def main():
  ref=pd.read_csv(REFERENCE);got=pd.read_csv(sys.argv[1]).sort_values('entry_time_msc').reset_index(drop=True)
  re=ref.entry_sec.to_numpy(dtype=np.int64);rx=ref.exit_sec.to_numpy(dtype=np.int64);rs=np.where(ref.side.to_numpy()=='BUY',1,-1)
  ge=got.entry_time_msc.to_numpy(dtype=np.int64)//1000;gx=got.exit_time_msc.to_numpy(dtype=np.int64)//1000;gs=got.side.to_numpy(dtype=np.int8);gn=got.net_quote_cents.to_numpy(dtype=np.int64)
  summary={'trades':len(got),'real_positive':int((gn>0).sum()),'real_negative':int((gn<0).sum()),'real_flat':int((gn==0).sum()),'real_quote_net_cents':int(gn.sum()),'by_reason':got.groupby('reason').net_quote_cents.agg(['count','sum']).to_dict('index')}
  for sec in (0,1,2,5,30):
    for mode in ('entry','joint'):
      summary[f'{mode}_{sec}s']=match_batch((re,rx,rs),(ge,gx,gs,gn),sec,mode)
  summary['joint_hold5pct']=match_batch((re,rx,rs),(ge,gx,gs,gn),2,'hold5')
  if len(sys.argv)>2:Path(sys.argv[2]).write_text(json.dumps(summary,indent=2))
  print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
