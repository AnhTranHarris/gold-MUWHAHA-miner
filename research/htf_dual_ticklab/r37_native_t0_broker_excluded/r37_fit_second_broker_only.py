"""F401-R37 reverse broker-exclusive causal t0 model fit; four months, single-source labels."""
import json,pathlib,time
import numpy as np,lightgbm as lgb
from r37_native_pre_t0_features import digest
base=pathlib.Path('/mnt/data/r37_mdk01_unapproved');root=base/'eight_original_cells';out=base/'model_fit_dukascopy';out.mkdir(exist_ok=True)
rng=np.random.default_rng(370127+37)
XX=[];YY=[]
for month in ('01','02','06','07'):
 with np.load(root/f'R37_dukascopy_{month}_ORIGINAL_T0_PREFIX.npz',allow_pickle=False) as z:
  n=len(z['t']);end=int(n*.60);elig=np.flatnonzero(z['valid'][:end]);rng.shuffle(elig)
  chosen=np.sort(elig[:min(22000,len(elig))]);chosen=chosen[z['t'][chosen]<z['t'][end-1]-40000]
  XX.append(z['X'][chosen]);YY.append(z['truth'][chosen]);print('FIT_INPUT',month,len(chosen),flush=True)
X=np.concatenate(XX);Y=np.concatenate(YY)
specs=[('BAD',511,96,.065,32,'bad'),('OPPOSITE',255,70,.075,40,'opposite'),('NEUTRAL',255,70,.075,40,'neutral'),('RIGHT',255,80,.065,40,'right')]
record={'fit_broker':'dukascopy','excluded_broker':'coinexx','months':['01','02','06','07'],'rows':len(Y),'original_t0_source':'strictly pre-t0 native bid ask; original R17 mask t/side/label only','models':{},'not_blind_forward':True,'no_OrderSend':True}
for num,(name,leaves,rounds,lr,minleaf,target) in enumerate(specs):
 yy=(Y!=0 if target=='bad' else Y==(0 if target=='right' else 1 if target=='opposite' else 2)).astype(np.int8)
 params={'objective':'binary','num_leaves':leaves,'learning_rate':lr,'min_data_in_leaf':minleaf,'feature_fraction':.82,'bagging_fraction':.88,'bagging_freq':1,'lambda_l2':4,'max_bin':127,'verbosity':-1,'num_threads':2,'seed':370127+num*31,'force_col_wise':True}
 t=time.monotonic();m=lgb.train(params,lgb.Dataset(X,label=yy),num_boost_round=rounds)
 dest=out/f'R37_dukascopy_NATIVE_T0_{name}.txt';m.save_model(str(dest))
 record['models'][name]={'sha256':digest(dest),'fit_seconds':round(time.monotonic()-t,1),'positive_count':int(yy.sum()),'trees':rounds,'leaves':leaves}
 (out/'R37_DK_FOURMONTH_FIT_RECEIPT.json').write_text(json.dumps(record,indent=2))
 print('FIT_COMPLETE',name,record['models'][name],flush=True)
