"""Streaming January in-sample as-of REAL quote meta-prediction; no outcome manifest in scorer."""
import os
import gzip,json,time,itertools,io
from pathlib import Path
import pandas as pd,numpy as np,lightgbm as lgb
O=Path(__file__).parent;R=Path(os.environ.get('R9_R03_FOLDER','/mnt/data/r9_jan_r03'))
feat=json.loads((O/'r04_fit_receipt.json').read_text())['feat'][2:]
model=lgb.Booster(model_file=str(O/'r04_prob_feeprofit_lgb.txt'))
inputcols=['sec','ms','bid_c','ask_c','phase','spread_c','f_b','f_s','s_b','s_s']
start=time.time();allrows=0
with gzip.open(R/'r03_hazard_predictions.csv.gz','rt') as pin,gzip.open(O/'r04_scores.csv.gz','wt',compresslevel=1) as out:
 assert pin.readline().strip().split(',')==inputcols
 out.write(','.join(inputcols+['risk1','risk2'])+'\n')
 for df in pd.read_csv(R/'r03_phase_seconds.csv.gz',chunksize=110000):
  df=df[df.phase<=47]
  if not len(df):continue
  orig=pd.read_csv(io.StringIO(''.join(itertools.islice(pin,len(df)))),header=None,names=inputcols)
  if len(orig)!=len(df) or not np.array_equal(orig.ms.to_numpy('int64'),df.ms.to_numpy('int64')):raise RuntimeError('original predictions vs feature rows drift')
  sf=np.where(orig.f_b.to_numpy()>=orig.f_s.to_numpy(),1.,-1.)
  ss=np.where(orig.s_b.to_numpy()>=orig.s_s.to_numpy(),1.,-1.)
  arr=df[feat].to_numpy('float32'); A=np.empty((len(df),arr.shape[1]+2),dtype='float32');A[:,2:]=arr
  A[:,0]=sf;A[:,1]=1;p1=model.predict(A,num_threads=4)
  A[:,0]=ss;A[:,1]=2;p2=model.predict(A,num_threads=4)
  orig['risk1']=np.round(p1,5);orig['risk2']=np.round(p2,5)
  orig.to_csv(out,header=False,index=False,float_format='%.5f')
  allrows+=len(df)
 assert not pin.readline(), 'unconsumed original predictions'
print(json.dumps({'source_seconds_scored':allrows,'seconds_predicted':allrows,'output_mb':round((O/'r04_scores.csv.gz').stat().st_size/1e6,2),'elapsed_s':round(time.time()-start,2)}),flush=True)
