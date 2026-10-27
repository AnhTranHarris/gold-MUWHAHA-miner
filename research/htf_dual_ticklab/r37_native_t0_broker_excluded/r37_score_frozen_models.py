"""Resume EXACT locally trained R37 weights without repeating fitting; score four original months.
Protect crossbroker blind exclusion: score fit broker first, freeze CAL policy before opening
any held-broker feature/label files. All 2026 months historically exposed to research.
"""
import argparse,json,pathlib,time
import numpy as np, lightgbm as lgb
from r37_native_pre_t0_features import digest
from r37_train_broker_excluded import metrics,bound_cut
MONTHS=('01','02','06','07');NAMES=('BAD','OPPOSITE','NEUTRAL','RIGHT')
def read(f):
 with np.load(f,allow_pickle=False) as z:return {k:z[k] for k in z.files}
def combos(P):
 b=P['BAD'];r=P['RIGHT'];o=P['OPPOSITE'];n=P['NEUTRAL']
 return {'BAD':b,'BAD_RIGHT_PROTECTED':(b*(1-.8*r)).astype(np.float32),
 'WRONG_CLASS_RIGHT_PROTECTED':(np.maximum(o,n)*(1-.8*r)).astype(np.float32),
 'MULTIHEAD_CONSENSUS':((b*np.maximum(o,n))**.5*(1-.65*r)).astype(np.float32)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fit',choices=('coinexx','dukascopy'),required=True);ap.add_argument('--root',default='/mnt/data/r37_mdk01_unapproved');args=ap.parse_args()
 root=pathlib.Path(args.root);out=root/('model_fit_'+args.fit)
 models={n:lgb.Booster(model_file=str(out/f'R37_{args.fit}_NATIVE_T0_{n}.txt')) for n in NAMES}
 if not all((out/f'R37_{args.fit}_NATIVE_T0_{n}.txt').exists() for n in NAMES):raise ValueError('incomplete weights')
 frozen={'source_fit_broker':args.fit,'excluded':('dukascopy' if args.fit=='coinexx' else 'coinexx'),
 'frozen_model_shas':{n:digest(out/f'R37_{args.fit}_NATIVE_T0_{n}.txt') for n in NAMES},
 'fit_scheme':'4 months source only, each month early60 indexed sample; 40s purge, CAL next20, VAL final20',
 'raw_source_asof':'strict quote timestamp < t0','historical_exposure_notice':'ALL source periods previously seen by researchers; not prospective blind OOS',
 'never_uses_prior_dual_broker_fitted_R17_scores':True,'live_trading_or_demo_orders_permitted':False}
 output={'frozen':frozen,'CAL_by_composition':{},'train_broker_full_months':{},'excluded_broker_full_months':{}}
 pool={name:[] for name in ('y','valid','BAD','OPPOSITE','NEUTRAL','RIGHT')}
 tic=time.monotonic()
 for m in MONTHS:
  a=read(root/'eight_original_cells'/f'R37_{args.fit}_{m}_ORIGINAL_T0_PREFIX.npz')
  P={n:models[n].predict(a['X'],num_threads=2).astype(np.float32) for n in NAMES}
  n=len(a['t']);j=np.arange(n);cal=(j>=int(n*.60))&(j<int(n*.80))&(a['t']>=a['t'][int(n*.60)]+40000)&a['valid']
  pool['y'].append(a['truth'][cal]);pool['valid'].append(a['valid'][cal]);
  for key in NAMES:pool[key].append(P[key][cal])
  np.savez_compressed(out/f'R37_{args.fit}_{m}_ALL_COMPOSITIONS_FOR_LATE_AUDIT.npz',t=a['t'],side=a['side'],truth=a['truth'],valid=a['valid'],**combos(P))
  print('SOURCE_SCORE',args.fit,m,'cal',int(cal.sum()),'elapsed',round(time.monotonic()-tic,1),flush=True)
  del P,a
 YY=np.concatenate(pool['y']);VV=np.concatenate(pool['valid']); PP={k:np.concatenate(pool[k]) for k in NAMES}
 r=combos(PP);caps=1999
 for name,s in r.items():
  cut=bound_cut(s,YY,VV,caps)
  output['CAL_by_composition'][name]={'cut':cut,**metrics(s,YY,VV,cut)}
 chosen=max(output['CAL_by_composition'],key=lambda q:(output['CAL_by_composition'][q]['incorrect_veto'],-output['CAL_by_composition'][q]['correct_lost']))
 frozen.update({'chosen':chosen,'cut':output['CAL_by_composition'][chosen]['cut'],'cal_correct_budget_exclusive':1999,'cal_policy_count':len(r),'source_fit_cell_events':1307317 if args.fit=='coinexx' else 1266934})
 policy=out/'F401_R37_FREEZE_BEFORE_EXCLUDED_BROKER_READBACK.json';policy.write_text(json.dumps(frozen,indent=2));frozen['policy_sha256']=digest(policy)
 print('FROZEN',args.fit,chosen,frozen['cut'],'sha',frozen['policy_sha256'],flush=True)
 # Fit broker scores after sealing policy; entirely new excluded broker read later.
 for m in MONTHS:
  a=read(out/f'R37_{args.fit}_{m}_ALL_COMPOSITIONS_FOR_LATE_AUDIT.npz')
  output['train_broker_full_months'][m]=metrics(a[chosen],a['truth'],a['valid'],frozen['cut'])
  print('IN-SAMPLE',args.fit,m,output['train_broker_full_months'][m],flush=True)
 excluded=frozen['excluded']
 for m in MONTHS:
  a=read(root/'eight_original_cells'/f'R37_{excluded}_{m}_ORIGINAL_T0_PREFIX.npz')
  P={n:models[n].predict(a['X'],num_threads=2).astype(np.float32) for n in NAMES}
  s=combos(P)[chosen]
  output['excluded_broker_full_months'][m]=metrics(s,a['truth'],a['valid'],frozen['cut'])
  np.savez_compressed(out/f'R37_{args.fit}_TO_{excluded}_{m}_EXCLUDED_BROKER_SOURCE_MASK.npz',t=a['t'],side=a['side'],truth=a['truth'],valid=a['valid'],score=s,veto=(a['valid']&(s>=frozen['cut'])))
  print('EXCLUDED-BROKER',args.fit,excluded,m,output['excluded_broker_full_months'][m],flush=True)
  del a,P
 output['elapsed_seconds']=round(time.monotonic()-tic,1)
 (out/'F401_R37_COMPLETE_SOURCE_BROKER_EXCLUDED_RESULT.json').write_text(json.dumps(output,indent=2))
 print('DONE',args.fit,output['elapsed_seconds'],flush=True)
if __name__=='__main__':main()
