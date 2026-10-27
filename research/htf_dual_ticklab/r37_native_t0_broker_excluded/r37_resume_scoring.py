"""Continue frozen broker-excluded R37 score without refit; no original research reruns."""
import argparse,json,pathlib,time
import numpy as np,lightgbm as lgb
from r37_native_pre_t0_features import digest
from r37_train_broker_excluded import metrics
from r37_score_frozen_models import combos,NAMES,MONTHS,read
ap=argparse.ArgumentParser();ap.add_argument('--fit',required=True,choices=['coinexx','dukascopy']);ap.add_argument('--only',default='01,02,06,07');args=ap.parse_args()
root=pathlib.Path('/mnt/data/r37_mdk01_unapproved');out=root/('model_fit_'+args.fit)
policyfile=out/'F401_R37_FREEZE_BEFORE_EXCLUDED_BROKER_READBACK.json';policy=json.loads(policyfile.read_text())
assert policy['source_fit_broker']==args.fit and policy['live_trading_or_demo_orders_permitted'] is False
held=policy['excluded'];mod={k:lgb.Booster(model_file=str(out/f'R37_{args.fit}_NATIVE_T0_{k}.txt')) for k in NAMES}
assert {k:digest(out/f'R37_{args.fit}_NATIVE_T0_{k}.txt') for k in NAMES}==policy['frozen_model_shas']
results={};start=time.monotonic()
for month in args.only.split(','):
 a=read(root/'eight_original_cells'/f'R37_{held}_{month}_ORIGINAL_T0_PREFIX.npz')
 P={n:mod[n].predict(a['X'],num_threads=2).astype(np.float32) for n in NAMES}
 v=combos(P)[policy['chosen']].astype(np.float32);m=metrics(v,a['truth'],a['valid'],policy['cut'])
 n=out/f'R37_{args.fit}_TO_{held}_{month}_EXCLUDED_BROKER_SOURCE_MASK.npz'
 np.savez_compressed(n,t=a['t'],side=a['side'],truth=a['truth'],valid=a['valid'],score=v,veto=a['valid']&(v>=policy['cut']))
 results[month]=m;print('BROKER_EXCLUDED',args.fit,held,month,m,'sec',round(time.monotonic()-start,2),flush=True)
 (out/'F401_R37_EXCLUDED_BROKER_PARTIAL_CHECKPOINT.json').write_text(json.dumps({'policy_sha256':digest(policyfile),'results':results},indent=2))
