"""Bounded source-preserving January prediction partitions (no original labels loaded)."""
from pathlib import Path
import sys,json
import pandas as pd,numpy as np,lightgbm as lgb
R=Path(__file__).parent
start=int(sys.argv[1]);stop=int(sys.argv[2]);out=R/f'r03_hazard_part_{start}_{stop}.csv.gz'
cols=json.loads((R/'r03_hazard_fit.json').read_text())['feature_columns']
first=lgb.Booster(model_file=str(R/'r03_hazard_leg1.txt'));second=lgb.Booster(model_file=str(R/'r03_hazard_leg2.txt'))
num=0;rows=0
for i,df in enumerate(pd.read_csv(R/'r03_phase_seconds.csv.gz',chunksize=140000)):
 if i<start:continue
 if i>=stop:break
 x=df[cols].to_numpy('float32')
 p=first.predict(x,num_threads=4);q=second.predict(x,num_threads=4)
 mask=df.phase.to_numpy()<=47
 res=df.loc[mask,['sec','ms','bid_c','ask_c','phase','spread_c']].copy()
 for name,z in [('f_b',p[:,1]),('f_s',p[:,2]),('s_b',q[:,1]),('s_s',q[:,2])]:res[name]=np.round(z[mask].astype('float32'),5)
 res.to_csv(out,index=False,header=num==0,mode='wt' if num==0 else 'at',compression={'method':'gzip','compresslevel':1})
 num+=1;rows+=len(res)
print(json.dumps({'chunk_start':start,'chunk_stop':stop,'input_chunks_scored':num,'output_rows':rows,'size_MB':round(out.stat().st_size/1e6,2)}),flush=True)
