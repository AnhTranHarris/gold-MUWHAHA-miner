"""R37 four-month SOURCE-EXCLUDED-broker causal pre-entry training.

Historical, previously exposed research. One broker wholly excluded from fit/CAL,
including old fitted R17/R24 score outputs (they are NEVER inputs). The other
broker is scored once after model/threshold freeze and hash. Neither result is
future forward OOS. Source month event IDs and outcome labels are immutable.
"""
import argparse,hashlib,json,os,pathlib,time
import numpy as np
import lightgbm as lgb
from r37_native_pre_t0_features import digest
MONTHS=('01','02','06','07')
SEED=370127

def read_cell(folder,broker,m):
 p=folder/f'R37_{broker}_{m}_ORIGINAL_T0_PREFIX.npz'
 with np.load(p,allow_pickle=False) as z:
  return {k:z[k].copy() for k in z.files}

def metrics(scores,y,valid,cut):
 veto=(valid&np.isfinite(scores)&(scores>=np.float32(cut)))
 return {'incorrect_veto':int(np.count_nonzero(veto&(y!=0))),
 'correct_lost':int(np.count_nonzero(veto&(y==0))),
 'original_wrong':int(np.count_nonzero(y!=0)),
 'original_correct':int(np.count_nonzero(y==0)),
 'neutral_veto':int(np.count_nonzero(veto&(y==2))),
 'opposite_veto':int(np.count_nonzero(veto&(y==1))),
 'valid':int(np.count_nonzero(valid)),
 'wrong_rejection_pct':float(100*np.count_nonzero(veto&(y!=0))/max(1,np.count_nonzero(y!=0))),
 'correct_retention_pct':float(100*(1-np.count_nonzero(veto&(y==0))/max(1,np.count_nonzero(y==0))))}

def bound_cut(scores,y,valid,right_cap):
 """CAL-only fixed threshold; ties fully included/fully excluded."""
 s=np.asarray(scores,dtype=np.float32)
 ix=np.flatnonzero(valid&np.isfinite(s))
 rank=ix[np.argsort(-s[ix],kind='stable')]
 good=np.cumsum(y[rank]==0,dtype=np.int32)
 feasible=np.flatnonzero(good<right_cap)
 if len(feasible)==0:return 2.0
 threshold=float(s[rank[feasible[-1]]])
 while np.count_nonzero(valid&(s>=threshold)&(y==0))>=right_cap:
  threshold=float(np.nextafter(np.float32(threshold),np.float32(np.inf)))
 return threshold

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fit',choices=('coinexx','dukascopy'),required=True);ap.add_argument('--root',default='/mnt/data/r37_mdk01_unapproved');ap.add_argument('--threads',type=int,default=2);ap.add_argument('--sample',type=int,default=22000);args=ap.parse_args()
 base=pathlib.Path(args.root);folder=base/'eight_original_cells';out=base/('model_fit_'+args.fit);out.mkdir(exist_ok=True)
 held='dukascopy' if args.fit=='coinexx' else 'coinexx'
 rng=np.random.default_rng(SEED+(0 if args.fit=='coinexx' else 37))
 src={m:read_cell(folder,args.fit,m) for m in MONTHS}
 # Never touch excluded broker original truths until all model SHAs and CAL selector frozen.
 X=[];Y=[];W=[];fit_idx=[];cal_idx=[];offset=0
 for m,a in src.items():
  n=len(a['t']); fit_until=int(.60*n);cal_until=int(.80*n)
  valid=a['valid']; trpool=np.flatnonzero(valid[:fit_until]);rng.shuffle(trpool)
  tr=np.sort(trpool[:min(args.sample,len(trpool))])
  # >=40second chronological event gap at each partition boundary on all months.
  tr=tr[a['t'][tr]<a['t'][fit_until-1]-40000]
  X.append(a['X']);Y.append(a['truth']);W.append(valid)
  fit_idx.extend((tr+offset).tolist())
  cal=np.flatnonzero(valid&(np.arange(n)>=fit_until)&(np.arange(n)<cal_until))
  cal=cal[a['t'][cal]>=a['t'][fit_until]+40000]
  cal_idx.extend((cal+offset).tolist());offset+=n
 X=np.concatenate(X);Y=np.concatenate(Y);W=np.concatenate(W)
 fit_idx=np.array(fit_idx,dtype=np.int64);cal_idx=np.array(cal_idx,dtype=np.int64)
 print('DATA',args.fit,'FIT',len(fit_idx),'CAL',len(cal_idx),'all',len(Y),'features',X.shape[1],flush=True)
 # Four distinct causal mechanisms: multi-class targets, high-capacity generic bad
 # and protecting correct guardian. Distinct architectural frontier, not threshold grid.
 specs=[('BAD',511,96,.065,32,'bad'),('OPPOSITE',255,70,.075,40,'opposite'),('NEUTRAL',255,70,.075,40,'neutral'),('RIGHT',255,80,.065,40,'right')]
 models={};P={};fitrec={};start=time.time()
 for name,leaves,rounds,lr,minleaf,target in specs:
  yy=(Y[fit_idx]!=(0) if target=='bad' else Y[fit_idx]==(0 if target=='right' else 1 if target=='opposite' else 2)).astype(np.int8)
  params={'objective':'binary','num_leaves':leaves,'learning_rate':lr,'min_data_in_leaf':minleaf,
          'feature_fraction':.82,'bagging_fraction':.88,'bagging_freq':1,'lambda_l2':4,
          'max_bin':127,'verbosity':-1,'num_threads':args.threads,'seed':SEED+len(models)*31,
          'force_col_wise':True}
  d=lgb.Dataset(X[fit_idx],label=yy,free_raw_data=True)
  tic=time.time();m=lgb.train(params,d,num_boost_round=rounds)
  path=out/f'R37_{args.fit}_NATIVE_T0_{name}.txt';m.save_model(str(path))
  P[name]=m.predict(X,num_threads=args.threads).astype(np.float32)
  models[name]=m
  fitrec[name]={'model_sha256':digest(path),'rows':len(fit_idx),'positive_rows':int(yy.sum()),'trees':rounds,'leaves':leaves,'fit_seconds':round(time.time()-tic,2),'model_path':path.name}
  print('FITTED',args.fit,name,'seconds',fitrec[name]['fit_seconds'],flush=True)
 # Only CAL chooses between finite distinct mechanisms; no held broker labels seen.
 score={
  'BAD':P['BAD'],
  'BAD_RIGHT_PROTECTED':(P['BAD']*(1-.8*P['RIGHT'])).astype(np.float32),
  'WRONG_CLASS_RIGHT_PROTECTED':(np.maximum(P['OPPOSITE'],P['NEUTRAL'])*(1-.8*P['RIGHT'])).astype(np.float32),
  'MULTIHEAD_CONSENSUS':((P['BAD']*np.maximum(P['OPPOSITE'],P['NEUTRAL']))**.5*(1-.65*P['RIGHT'])).astype(np.float32)}
 cal_rows={};caps=1999
 for name,v in score.items():
  cut=bound_cut(v[cal_idx],Y[cal_idx],W[cal_idx],caps)
  cal_rows[name]={'cut':cut,**metrics(v[cal_idx],Y[cal_idx],W[cal_idx],cut)}
 chosen=max(cal_rows,key=lambda k:(cal_rows[k]['incorrect_veto'],-cal_rows[k]['correct_lost']))
 frozen={'experiment':'F401-R37 broker-excluded native pre-t0','fit_broker':args.fit,'excluded_broker':held,
 'months':list(MONTHS),'fit_selection':'each original month early60 of first registered broker (40s embargo)',
 'cal':'each original month mid20 of first registered broker; maximum 1998 right veto, 1999 budget exclusive',
 'val':'each original month late20 of first registered broker, never calibrate on VAL',
 'fit_pre_t0_only':True,'previously_exposed_historical_months':True,
 'upstream_fitted_score_as_input':False,'target_broker_training_or_calibration':False,
 'source_archived_event_t0_side_identity':'original F401 R17 source-only masks; target only training and evaluation',
 'model_artifacts':fitrec,'cal_selections':cal_rows,'chosen':chosen,'fixed_cut':cal_rows[chosen]['cut'],
 'absolute_source_name_sha_registry':'r37_native_pre_t0_features.py',
 'not_deployable_or_live_authorized':True}
 (out/'F401_R37_FROZEN_POLICY_BEFORE_EXCLUDED_BROKER.json').write_text(json.dumps(frozen,indent=2))
 frozen['frozen_policy_sha256']=digest(out/'F401_R37_FROZEN_POLICY_BEFORE_EXCLUDED_BROKER.json')
 print('FREEZE',args.fit,'chosen',chosen,'cut',frozen['fixed_cut'],'sha',frozen['frozen_policy_sha256'],flush=True)
 # Full source four months are fitted/CAL/VAL, not a pristine OOS. Report each.
 result={'model':args.fit,'freeze':frozen,'fit_months':{},'excluded_broker_months':{},'cal':cal_rows}
 for m,a in src.items():
  s0=sum(len(src[x]['truth']) for x in MONTHS[:MONTHS.index(m)])
  ix=slice(s0,s0+len(a['truth']));v=score[chosen][ix]
  result['fit_months'][m]=metrics(v,a['truth'],a['valid'],frozen['fixed_cut'])
  np.savez_compressed(out/f'R37_{args.fit}_{m}_NATIVE_FITTED_SHADOW_MASK.npz',t=a['t'],side=a['side'],truth=a['truth'],valid=a['valid'],score=v,veto=a['valid']&(v>=frozen['fixed_cut']))
 del X,Y,W,src
 for m in MONTHS:
  a=read_cell(folder,held,m)
  prob={n:model.predict(a['X'],num_threads=args.threads).astype(np.float32) for n,model in models.items()}
  held_scores={'BAD':prob['BAD'],'BAD_RIGHT_PROTECTED':prob['BAD']*(1-.8*prob['RIGHT']),
   'WRONG_CLASS_RIGHT_PROTECTED':np.maximum(prob['OPPOSITE'],prob['NEUTRAL'])*(1-.8*prob['RIGHT']),
   'MULTIHEAD_CONSENSUS':(prob['BAD']*np.maximum(prob['OPPOSITE'],prob['NEUTRAL']))**.5*(1-.65*prob['RIGHT'])}
  v=held_scores[chosen].astype(np.float32)
  result['excluded_broker_months'][m]=metrics(v,a['truth'],a['valid'],frozen['fixed_cut'])
  np.savez_compressed(out/f'R37_{args.fit}_TO_{held}_{m}_BROKER_EXCLUDED_MASK.npz',t=a['t'],side=a['side'],truth=a['truth'],valid=a['valid'],score=v,veto=a['valid']&(v>=frozen['fixed_cut']))
  print('EXCLUDED-BROKER',args.fit,'->',held,m,result['excluded_broker_months'][m],flush=True)
 result['elapsed_seconds']=round(time.time()-start,1)
 result['both_broker_months_all_nonforward_historically_exposed']=True
 (out/'F401_R37_EXCLUDED_BROKER_COMPLETE_RESULT.json').write_text(json.dumps(result,indent=2))
 print('DONE',args.fit,'total sec',result['elapsed_seconds'],flush=True)
if __name__=='__main__':main()
