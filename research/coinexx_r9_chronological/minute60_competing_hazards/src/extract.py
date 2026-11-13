"""Source-exact nine-month R9 shadow feature extraction, no R9 EA change."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from event_engine import build_features,barriers,first_passage_actions,FEATURE_NAMES,TREND_N

SOURCE=Path('/mnt/data/r9_m60_expanded')

def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(4*1024*1024),b''):h.update(c)
 return h.hexdigest()

def month(mm,data_root=Path('/mnt/data'),out_root=Path('/mnt/data/r9_m60_competing/derived')):
 out_root.mkdir(parents=True,exist_ok=True)
 receipt=json.loads((SOURCE/'source_receipt.json').read_text());info=receipt['source_months'][mm]
 raw=data_root/f'XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz'
 if sha256(raw)!=info['source_sha256']:raise RuntimeError('raw digest mismatch')
 df=pd.read_csv(raw,usecols=['time_msc','bid','ask'],dtype={'time_msc':np.int64,'bid':np.float64,'ask':np.float64})
 ms=df.time_msc.to_numpy(np.int64,copy=True)
 bid=np.rint(df.bid.to_numpy(copy=True)*100).astype(np.int32)
 ask=np.rint(df.ask.to_numpy(copy=True)*100).astype(np.int32)
 del df
 if len(ms)!=info['rows'] or np.any(np.diff(ms)<0) or np.any(ask<bid):raise RuntimeError('raw chronological validation failed')
 frozen=np.load(SOURCE/'full_derived'/f'full_month_2026_{mm}.npz',allow_pickle=False)
 startordinal=sum(receipt['source_months'][f'{i:02}']['rows'] for i in range(1,int(mm)))
 entry_ix=(frozen['entry_ordinals']-startordinal-1).astype(np.int64)
 if not np.array_equal(ms[entry_ix],frozen['entry_times']):raise RuntimeError('entry timestamps mismatch frozen')
 local,rv1,spread=build_features(ms,bid,ask,entry_ix)
 L,G=barriers(spread,rv1)
 cause,hit,terminal=first_passage_actions(ms,bid,ask,entry_ix,L,G,15000)
 if len(cause)!=len(frozen['side']):raise RuntimeError('opportunity count mismatch')
 out=out_root/f'event_2026_{mm}.npz'
 np.savez_compressed(out,features=local,cause=cause,hit_ms=hit,terminal=terminal,
                    spread=spread,stop=L,target=G,rv1=rv1,
                    entry=frozen['entry_times'],ordinal=frozen['entry_ordinals'],r9_side=frozen['side'],
                    feature_names=np.array(FEATURE_NAMES))
 r={'month':mm,'source_sha256':info['source_sha256'],'rows':len(ms),'entries':len(cause),
    'output_sha256':sha256(out),'feature_count':len(FEATURE_NAMES),
    'adverse_at_entry':int(np.sum((cause==2)&(hit==0))),
    'causes':{p:{str(k):int(np.sum(cause[:,j]==k)) for k in (-1,0,1,2)} for j,p in enumerate(('BUY','SELL'))},
    'stop_cents':{'median':int(np.median(L)),'p95':int(np.quantile(L,.95))},
    'target_cents':{'median':int(np.median(G)),'p95':int(np.quantile(G,.95))},
    'status':'SHADOW_LABEL_AND_ASOF_CONTEXT_NOT_MT5_FILL'}
 (out_root/f'receipt_2026_{mm}.json').write_text(json.dumps(r,indent=2)+'\n')
 print('SOURCE',mm,'ticks',len(ms),'entries',len(cause),'cause BUY',r['causes']['BUY'],'cause SELL',r['causes']['SELL'],flush=True)
 return r

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--months',nargs='+',default=[f'{i:02}' for i in range(1,10)])
 a=p.parse_args();[month(m) for m in a.months]
