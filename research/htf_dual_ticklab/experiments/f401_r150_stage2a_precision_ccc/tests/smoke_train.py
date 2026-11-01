"""Synthetic engineering smoke only; NOT XAUUSD or R150Q measured alpha."""
import json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from r150ccc.fit import fit_three_experts,calibrate_three_experts
from r150ccc.schema import feature_groups
rng=np.random.default_rng(1502)
x=rng.standard_normal((6200,193)).astype('float32');y=(rng.uniform(size=6200)<.125).astype(np.int8)
x[y==1,0]+=.6;x[y==1,145]+=.8;x[y==1,176]+=.4
start=time.time();models=fit_three_experts(x[:5000],y[:5000],feature_groups=feature_groups())
cal=calibrate_three_experts(models,x[5000:],y[5000:])
s={k:{'n_source_features':int(len(v.columns)),'score_min':float(v.predict_proba(x[-100:])[:,1].min()),
      'score_max':float(v.predict_proba(x[-100:])[:,1].max())} for k,v in cal.items()}
print(json.dumps({'status':'SYNTHETIC_ONLY_NOT_R150Q','fit_seconds':round(time.time()-start,2),'models':s},indent=2))
