#!/usr/bin/env python3
"""Convert complete as-of datasets to compact disk-backed features, one month per process."""
import os,json,argparse,sys
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
from train_hindsight_teacher_student import read_teacher,feature_names
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101')

def run(source,month):
    df=pd.read_pickle(ROOT/'checkpoints'/f'{source}_{month}_tick_asof.pkl.gz',compression='gzip')
    features=[x for x in feature_names(df) if x!='broker_id']
    X=df[features].to_numpy(dtype=np.float32,copy=True)
    # Important: not a runtime feature. SYNTH teacher only changes training weights.
    teacher=read_teacher();offset=(120 if month in ('01','02') else 180)*60000
    tm=((df.entry_ms.to_numpy(np.int64)+offset)//60000)*60000
    mark=np.fromiter(((int(t),int(s)) in teacher for t,s in zip(tm,df.side.to_numpy(np.int8))),dtype=np.uint8,count=len(df))
    date=pd.to_datetime(df.entry_ms,unit='ms',utc=True)
    dateint=(date.dt.year*10000+date.dt.month*100+date.dt.day).to_numpy(np.int32)
    wk=(date.dt.isocalendar().year.astype('int32')*100+date.dt.isocalendar().week.astype('int32')).to_numpy(np.int32)
    base=ROOT/'checkpoints'/f'{source}_{month}'
    arrays={'X':X,'win':df.label_30s_win.to_numpy(np.uint8),'neutral':df.label_30s_neutral.to_numpy(np.uint8),
        'net':df.net.to_numpy(np.float32),'ts':df.entry_ms.to_numpy(np.int64),'date':dateint,'week':wk,'teacher':mark}
    for k,v in arrays.items():np.save(str(base)+f'_{k}.npy',v,allow_pickle=False)
    (ROOT/'checkpoints'/f'{source}_{month}_mmap.json').write_text(json.dumps({'month':month,'source':source,'n':len(df),'features':features,'arrays':list(arrays)},indent=2))
    print(source,month,len(df),X.shape, 'teacher',int(mark.sum()),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True);a=p.parse_args()
    run(a.source,a.month)
