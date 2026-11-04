"""R24S4 ADDITIVE as-of dual-cause/horizon specialist, heavily in-sample.

Freeze original R24 source and raw quote labels. All inference inputs derive only from
quote-prefix features at original source decision ordinal. A new source-specific
five-CAUSE multiclass competing first-passage head (STOP, TARGET, TIMEOUT,
CENSORED, UNFILLED) and a distinct WAIT opportunity head are trained. No R9
reference or future labels enter inference; labels are training/evaluation only.

All original 15/30/60 results, including losing source positions and zero-target
calendar periods, are preserved. NOT an OOS or deployable MT5 strategy.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,time,os
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import lightgbm as lgb
sys.path[:0]=['/mnt/data/h1v2_r24_asof/source']
import r24_firstpass_engine as e
import r24_fit_hazard_month as oldfit
import r24_predict_replay_V2_highthroughput as oldreplay

ROOT=Path('/mnt/data/h1v2_r24s4_entry_specialists')
EXTRA_NAMES=('flow_coherence_3v15','bidask_spread_strain_3s','quote_rate_accel','spread_relief_pressure',
 'direction_persistence_3_60','spread_arrival_3_60','spread_volatility_60','mtf_15m_h1_consensus',
 'mtf_4h_conflict','near_zero_3s_move','relative_spread_shock_15_300','stable_flow_vs_fee',
 'min_of_bidask_move_normalized','interquote_age_to_count','epoch_age_to_session','quarter_phase_sin','quarter_phase_cos')
HORIZONS=(15,30,60)


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()


def enhanced_prefix(x):
 """As-of deterministic cross-scale spread/flow/quote-arrival interactions.

 Does not accept labels, future tick columns, R9 quota, or original future oracle.
 Caller must provide frozen R24 past/now-only 47-float feature matrix.
 """
 x=np.asarray(x,dtype=np.float32)
 if x.ndim!=2 or x.shape[1]!=len(e.FEATURE_NAMES):raise ValueError('R24_FEATURE_SCHEMA_FAIL')
 if not np.isfinite(x).all():raise ValueError('NONFINITE_SOURCE_PREFIX_FEATURE')
 f={k:i for i,k in enumerate(e.FEATURE_NAMES)}
 v=lambda k:x[:,f[k]]
 s=v('spread_raw');s=np.maximum(s,0.0)
 b3=v('bid_move_3s');a3=v('ask_move_3s')
 b15=v('bid_move_15s');a15=v('ask_move_15s')
 b60=v('bid_move_60s');a60=v('ask_move_60s')
 q3=v('quotes_3s');q15=v('quotes_15s');q60=v('quotes_60s')
 i15=v('spread_ema15s');i300=v('spread_ema300s')
 den=120.+s
 out=np.column_stack([
  np.sign(b3)*np.sign(a3)*np.sign(b15)*np.sign(a15),
  (np.abs(b3)+np.abs(a3))/den,
  np.log1p(np.maximum(q3,0))/np.log1p(np.maximum(q15,0)+1),
  (i300-i15)/(1+np.abs(i300)),
  np.sign(b3+a3)*np.sign(b60+a60),
  (q3+1)/(q60+1),
  (np.abs(b60)+np.abs(a60))/(s+120),
  (np.sign(v('mtf_15m_closed_slope'))==np.sign(v('mtf_h1_closed_slope'))).astype(np.float32)*v('mtf_15m_valid')*v('mtf_h1_valid'),
  (np.sign(v('mtf_h1_closed_slope'))!=np.sign(v('mtf_h4_closed_slope'))).astype(np.float32)*v('mtf_h1_valid')*v('mtf_h4_valid'),
  (np.abs(b3)+np.abs(a3)<den).astype(np.float32),
  (i15-i300)/(120.+np.abs(i300)),
  np.minimum(np.abs(b3),np.abs(a3))/den,
  np.minimum(np.abs(b60),np.abs(a60))/(s+120),
  np.log1p(np.maximum(v('lagged_quote_age_ms'),0))/(1+q3),
  np.log1p(np.maximum(v('epoch_age_s'),0))*np.log1p(q60+1),
  np.sin((v('minute_in_hour')%15)*(2*np.pi/15)),
  np.cos((v('minute_in_hour')%15)*(2*np.pi/15))
 ]).astype(np.float32,copy=False)
 if out.shape[1]!=len(EXTRA_NAMES):raise AssertionError('EXTRA_COUNT')
 if not np.isfinite(out).all():raise ValueError('NONFINITE_ADDITIVE_FEATURE')
 return np.clip(out,-1.e5,1.e5)


def inputpaths(source,mon):
 return e.R24/'results'/source/mon/f'R24_{source}_{mon}_1000MS'


def train_one(source,mon,sample_n=160000,rounds=80):
 tick=time.monotonic();dst=ROOT/'results'/source/mon;dst.mkdir(parents=True,exist_ok=True)
 p=inputpaths(source,mon)
 x=np.load(str(p)+'_features.npy',mmap_mode='r')
 labels=np.load(str(p)+'_labels_2SIDE_3HORIZON.npy',mmap_mode='r')
 t=np.load(str(p)+'_signal_utc_ms.npy',mmap_mode='r')
 n=len(x);sample=min(sample_n,n)
 ids=np.unique(np.linspace(0,n-1,sample,dtype=np.int64))
 if len(ids)<1000:raise ValueError('INSUFFICIENT_POPULATION')
 src_pin=e.source_pin(source,mon)
 if sha(e.source_file(source,mon))!=src_pin:raise ValueError('ORIGINAL_RAW_SHA_MISMATCH')
 ori=e.R24/'results'/source/mon/f'R24_{source}_{mon}_SOURCE_PREPARATION_ATOMIC_receipt.json'
 receipt=json.loads(ori.read_text());assert receipt['source_sha256']==src_pin
 nfeature=len(e.FEATURE_NAMES)+len(EXTRA_NAMES)+2
 xt=np.empty((len(ids)*6,nfeature),dtype=np.float32)
 y=np.empty(len(ids)*6,dtype=np.int32)
 b=np.concatenate((np.asarray(x[ids],np.float32),enhanced_prefix(x[ids])),axis=1)
 for si in range(2):
  for hi,h in enumerate(HORIZONS):
   off=(si*3+hi)*len(ids);loc=xt[off:off+len(ids)]
   loc[:,:-2]=b;loc[:,-2]=(1 if si==0 else -1);loc[:,-1]=h
   y[off:off+len(ids)]=labels[ids,si,hi]
 classes=np.bincount(y,minlength=5)
 if not np.all(classes>0):raise ValueError('MISSING_COMPETING_CLASS')
 names=list(e.FEATURE_NAMES)+list(EXTRA_NAMES)+['side_buy1_sellminus1','horizon_seconds']
 print('R24S4_START_FIT',source,mon,'training_rows',len(y),'classes',classes.tolist(),flush=True)
 par={'objective':'multiclass','num_class':5,'metric':'multi_logloss','learning_rate':0.075,
      'num_leaves':79,'max_bin':127,'min_data_in_leaf':85,'lambda_l2':8.,'feature_fraction':.92,
      'bagging_fraction':.82,'bagging_freq':1,'num_threads':3,'verbosity':-1,'seed':240104}
 m=lgb.train(par,lgb.Dataset(xt,label=y,feature_name=names,free_raw_data=True),num_boost_round=rounds)
 model=dst/f'R24S4_{source}_{mon}_BROKER_ONLY_MULTISCALE_CROSS_PRODUCT_5_CAUSE_LGBM.txt';m.save_model(str(model))
 del xt,y
 wait_y=oldfit.future_wait_label(labels,t)
 wx=b.copy()
 wpar={'objective':'binary','learning_rate':.075,'num_leaves':47,'min_data_in_leaf':75,
      'lambda_l2':8.,'max_bin':127,'num_threads':3,'verbosity':-1,'seed':240105}
 w=lgb.train(wpar,lgb.Dataset(wx,label=wait_y[ids],feature_name=names[:-2],free_raw_data=True),num_boost_round=max(42,rounds//2))
 wfile=dst/f'R24S4_{source}_{mon}_BROKER_ONLY_WAIT10_HAZARD.txt';w.save_model(str(wfile))
 np.save(dst/f'R24S4_{source}_{mon}_TRAINING_ROW_INDICES.npy',ids,allow_pickle=False)
 fmt=dst/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_HAZARD_PROBABILITIES.npy'
 wp=dst/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_WAIT_PROBABILITIES.npy'
 # Incomplete *.PARTIAL files are never accepted or re-used.
 pp=Path(str(fmt)+'.PARTIAL');ww=Path(str(wp)+'.PARTIAL')
 P=np.lib.format.open_memmap(pp,mode='w+',dtype='float32',shape=(n,2,3,5))
 W=np.lib.format.open_memmap(ww,mode='w+',dtype='float32',shape=(n,))
 batch=32768
 for left in range(0,n,batch):
  right=min(n,left+batch)
  bx=np.concatenate((np.asarray(x[left:right],np.float32),enhanced_prefix(x[left:right])),axis=1)
  W[left:right]=w.predict(bx,num_threads=3)
  tmp=np.empty((len(bx),nfeature),np.float32)
  tmp[:,:-2]=bx
  for si in range(2):
   tmp[:,-2]=1 if si==0 else -1
   for hi,h in enumerate(HORIZONS):
    tmp[:,-1]=h
    P[left:right,si,hi,:]=m.predict(tmp,num_threads=3)
  if left%(32768*10)==0:print('R24S4_INFERENCE_PROGRESS',source,mon,left,'/',n,flush=True)
 P.flush();W.flush()
 if not np.isfinite(P).all() or not np.isfinite(W).all():raise ValueError('NONFINITE_AFTER_FULL_INFERENCE')
 if not np.allclose(P[::max(1,n//3000)].sum(axis=-1),1.0,atol=1e-4):raise ValueError('COMPETING_HAZARDS_NOT_NORMALIZED')
 del P,W
 os.replace(pp,fmt);os.replace(ww,wp)
 rec={'status':'R24S4_MONTH_ATOMIC_MODEL_AND_ALL_DECISION_INFERENCE_COMPLETE',
      'source':source,'month':mon,'raw_sha':src_pin,'source_decision_count':n,
      'fully_exposed_same_month_training_indices':len(ids),'training_rows_side_horizon':len(ids)*6,
      'training_histogram_stop_target_timeout_censor_unfilled':classes.tolist(),
      'independent_wait_trained':True,'same_month_full_decision_predictions':n,
      'horizon_seconds':list(HORIZONS),'feature_names':names,
      'source_original_R9_quota_NOT_used_in_training_or_inference':True,
      'past_only_asof_original_prefix_in_features':True,'future_targets_only_for_training':True,
      'no_new_news_or_broker_permission_data':True,'not_deployable_or_blind_OOS':True,
      'source_SHA':src_pin,'seconds':round(time.monotonic()-tick,2),
      'outputs':{q.name:{'bytes':q.stat().st_size,'sha256':sha(q)} for q in [model,wfile,dst/f'R24S4_{source}_{mon}_TRAINING_ROW_INDICES.npy',fmt,wp]}}
 (dst/f'R24S4_{source}_{mon}_FULL_INFERENCE_ATOMIC_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
 print('R24S4_MODEL_AND_FROZEN_INFERENCE_COMPLETE',source,mon,'seconds',rec['seconds'],flush=True)
 return rec


def rows_writer(path,rows):
 if not rows:raise ValueError('NO_ROWS')
 with open(path,'w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)


def replay_one(source,mon):
 dst=ROOT/'results'/source/mon
 p=inputpaths(source,mon)
 original=np.load(str(p)+'_labels_2SIDE_3HORIZON.npy',mmap_mode='r')
 tim=np.load(str(p)+'_signal_utc_ms.npy',mmap_mode='r')
 src_ordinal=np.load(str(p)+'_source_quote_ordinal.npy',mmap_mode='r')
 ft=np.load(str(p)+'_actual_fill_utc_ms.npy',mmap_mode='r')
 ev=np.load(str(p)+'_first_barrier_2SIDE_utc_ms.npy',mmap_mode='r')
 timeout=np.load(str(p)+'_true_timeout_first_observed_utc_ms.npy',mmap_mode='r')
 P=np.load(dst/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_HAZARD_PROBABILITIES.npy',mmap_mode='r')
 W=np.load(dst/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_WAIT_PROBABILITIES.npy',mmap_mode='r')
 qr,qref=e.calendar_reference(mon)
 nq=len(qref);first=int(qr[0]//900000)
 out=[];all_q=[];all_h=[];all_d=[];by_case={}
 thr=(.06,.12,.20,.35,.50);stopcap=(.65,.85,.99);wait_penalty=(0.,.15);hpenalty=(0.,.07)
 # 5*3*2*2=60 source-complete in-sample policies, no posthoc winners-only censor.
 for tp in thr:
  for risk in stopcap:
   for wp in wait_penalty:
    for hp in hpenalty:
     res=oldreplay.replay_one_position(P,W,original,tim,ft,ev,timeout,first,nq,tp,risk,wp,hp)
     f,g,st,to,ce=res[:5]
     dayrefs=qref.reshape(-1,96).sum(axis=1);hrefs=qref.reshape(-1,4).sum(axis=1)
     def agg(ref,F,G,S,TO,C,step,keys):
      for pos in range(len(ref)):
       k=pos*step;l=k+step
       z=int(ref[pos]);a=int(F[k:l].sum());good=int(G[k:l].sum());bad=int(S[k:l].sum());timed=int(TO[k:l].sum());c=int(C[k:l].sum())
       denom=good+bad+timed
       acc=good/denom if denom else None
       key=keys[pos]
       yield {'case':case,'source':source,'month':mon,'utc_start':key,'r9_SYNTH_original_ref':z,'asof_fills':a,
         'TARGET_first_correct':good,'STOP_first_wrong':bad,'TIMEOUT_initially_survived_without_target':timed,
         'QUOTE_CENSORED_unknown':c,'completed_correctness_target_fraction':acc,
         'source_count_quota_met':int(a>=z) if z else None,
         'correct_trade_count_quota_met':int(good>=z) if z else None,
         'joint_80pct_TARGET_and_R9_filled_quota':int(a>=z and acc is not None and acc>=.8) if z else None,
         'joint_80pct_TARGET_and_R9_correct_quota':int(good>=z and acc is not None and acc>=.8) if z else None,
         'initial_noSTOP_first_fraction':(good+timed)/denom if denom else None,
         'no_news_impact_claim':True}
     case=f'P{tp:.2f}_STOP{risk:.2f}_WAIT{wp:.2f}_H{hp:.2f}'
     qkeys=[datetime.fromtimestamp(int(t)/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') for t in qr]
     hkeys=qkeys[::4];dkeys=qkeys[::96]
     qs=list(agg(qref,f,g,st,to,ce,1,qkeys));hs=list(agg(hrefs,f,g,st,to,ce,4,hkeys));ds=list(agg(dayrefs,f,g,st,to,ce,96,dkeys))
     all_q.extend(qs);all_h.extend(hs);all_d.extend(ds)
     gsum=int(g.sum());bad=int(st.sum());timeouts=int(to.sum());fill=int(f.sum());den=gsum+bad+timeouts
     out.append({'case':case,'source':source,'month':mon,'pTARGET_threshold':tp,'pSTOP_maximum':risk,
       'wait_opportunity_penalty':wp,'horizon_penalty':hp,'raw_quote_source_sha':e.source_pin(source,mon),
       'r9_SYNTH_original_source_month_reference':int(qref.sum()),'original_active_15m':int(np.sum(qref>0)),
       'original_active_hours':int(np.sum(hrefs>0)),
       'source_month_fills':fill,'TARGET_first_correct':gsum,'STOP_first_wrong':bad,'TIMEOUT':timeouts,
       'CENSORED_unknown':int(ce.sum()),'TARGET_first_fraction':gsum/den if den else None,
       'initial_no_STOP_first_fraction':(gsum+timeouts)/den if den else None,
       'quarters_target_count_met':sum(x['correct_trade_count_quota_met']==1 for x in qs),
       'quarters_joint80_target_and_quota':sum(x['joint_80pct_TARGET_and_R9_correct_quota']==1 for x in qs),
       'hours_target_count_met':sum(x['correct_trade_count_quota_met']==1 for x in hs),
       'hours_joint80_target_and_quota':sum(x['joint_80pct_TARGET_and_R9_correct_quota']==1 for x in hs),
       'days_joint80_target_and_quota':sum(x['joint_80pct_TARGET_and_R9_correct_quota']==1 for x in ds),
       'admitted_trades_not_all_profitable':True,'fully_training_month_IN_SAMPLE':True})
     z=dict(zip(['signal_row','chosen_side','horizon_index','observed_cause','predicted_pTARGET','actual_fill_ms','actual_exit_ms'],res[5:]))
     # Preserve source-exact original quote ordinal and true event paths for ALL
     # selected wins and losses; do not collapse class or omit zero-quota hours.
     z['source_signal_quote_ordinal']=src_ordinal[res[5]]
     path=dst/f'R24S4_{source}_{mon}_{case}_ALL_SELECTIONS_POSITIVE_AND_NEGATIVE.npz'
     np.savez_compressed(path,**z)
     by_case[case]={'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path)}
     if len(out)%12==0:print('R24S4_FULL_POLICY_REPLAY',source,mon,len(out),'/',60,flush=True)
 rows_writer(dst/f'R24S4_{source}_{mon}_ALL_60_HAZARD_POLICY_MONTH_CASES.csv',out)
 rows_writer(dst/f'R24S4_{source}_{mon}_ALL_60_CASES_COMPLETE_QUARTERS.csv',all_q)
 rows_writer(dst/f'R24S4_{source}_{mon}_ALL_60_CASES_COMPLETE_HOURS.csv',all_h)
 rows_writer(dst/f'R24S4_{source}_{mon}_ALL_60_CASES_COMPLETE_DAYS.csv',all_d)
 best=sorted(out,key=lambda x:(x['quarters_joint80_target_and_quota'],x['hours_joint80_target_and_quota'],x['quarters_target_count_met'],x['TARGET_first_correct'],-x['STOP_first_wrong']),reverse=True)[0]
 rec={'status':'R24S4_FULL_60_IN_SAMPLE_SOURCE_REPLAY_ATOMIC_COMPLETE',
      'source':source,'month':mon,'raw_sha':e.source_pin(source,mon),'reference':int(qref.sum()),
      'calendar_rows':{'quarters':len(all_q),'hours':len(all_h),'days':len(all_d)},
      'best_policy_lexicographic_research_only':best,'all60_selected_source_trade_traces':by_case,
      'all_cases_have_complete_15min_hour_day_reference_even_at_zero':True,
      'negative_source_outcomes_preserved':True,'no_future_labels_used_by_inference':True,
      'no_independent_OOS_or_realtime_broker_fill':True,
      'source_files':{f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(dst.glob('R24S4_*ALL_60*csv'))}}
 (dst/f'R24S4_{source}_{mon}_FULL_60_CASES_ATOMIC_RECEIPT.json').write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
 print('R24S4_REPLAY_COMPLETE',source,mon,json.dumps(best),flush=True)
 return rec

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=e.SOURCE_NAMES,required=True)
 p.add_argument('--month',choices=('01','02','06','07'),required=True)
 p.add_argument('--sample-count',type=int,default=160000);p.add_argument('--rounds',type=int,default=80)
 args=p.parse_args()
 train_one(args.source,args.month,args.sample_count,args.rounds)
 replay_one(args.source,args.month)
