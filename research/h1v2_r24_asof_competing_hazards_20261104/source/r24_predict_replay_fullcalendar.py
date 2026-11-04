"""R24 complete-month frozen AS-OF LightGBM inference and one-position replay.

Five competing outcomes (STOP,TP,TIMEOUT,CENSOR,UNFILLED), 3 horizons and 2
independent sides, separate future-opportunity WAIT. Inference reads only
historically observed features, never a teacher label/side. Hindsight labels
are read ONLY by post-decision replay. Heavy IN-SAMPLE fitting and policy
threshold selection remain exposed and not independently predictive.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,time,os
from pathlib import Path
from datetime import datetime,timezone
import lightgbm as lgb
import numpy as np
from numba import njit
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r24_firstpass_engine as r

@njit(cache=False)
def replay_one_position(pr,wait,truth,signal_t,fill_t,event_t,timeout_t,qfirst,nq,
                        minp,maxstop,wait_penalty,horizon_penalty):
 n=len(signal_t)
 qfills=np.zeros(nq,np.int32);qtp=np.zeros(nq,np.int32);qstop=np.zeros(nq,np.int32)
 qtime=np.zeros(nq,np.int32);qcen=np.zeros(nq,np.int32)
 ids=np.empty(n,np.int32);sides=np.empty(n,np.int8);horizons=np.empty(n,np.int8)
 results=np.empty(n,np.int8);chosen_probability=np.empty(n,np.float32)
 filledtime=np.empty(n,np.int64);exittime=np.empty(n,np.int64)
 lastbusy=np.int64(-9223372036854775807);ns=0
 for i in range(n):
  if signal_t[i]<=lastbusy:continue
  best=-1.e9;chosen_s=-1;chosen_h=-1;pchosen=0.
  for si in range(2):
   for h in range(3):
    p=float(pr[i,si,h,1]);risk=float(pr[i,si,h,0]);censor=float(pr[i,si,h,3]);unfill=float(pr[i,si,h,4])
    if p<minp or risk>maxstop:continue
    # Explicit WAIT opportunity cost and holding-time opportunity consumption.
    score=p-0.4*risk-0.15*censor-0.12*unfill-wait_penalty*float(wait[i])-horizon_penalty*h
    if score>best:
     best=score;chosen_s=si;chosen_h=h;pchosen=p
  if chosen_s<0 or best<=0.:continue
  f=fill_t[i]
  if f<0 or f<=lastbusy:continue
  q=int(f//900000-qfirst)
  if q<0 or q>=nq:continue
  outcome=int(truth[i,chosen_s,chosen_h]);end=f
  if outcome==4:continue
  if outcome==1 or outcome==0:
   end=event_t[i,chosen_s]
   if end<f:
    raise ValueError('SOURCE_FIRST_BARRIER_TIME_MISSING')
  elif outcome==2:
   end=timeout_t[i,chosen_h]
   if end<f:
    raise ValueError('SOURCE_TIMEOUT_ACTUAL_QUOTE_MISSING')
  else:
   end=f+(15000 if chosen_h==0 else 30000 if chosen_h==1 else 60000)
  if end<=lastbusy:continue
  lastbusy=end
  ids[ns]=i;sides[ns]=1 if chosen_s==0 else -1;horizons[ns]=chosen_h
  results[ns]=outcome;chosen_probability[ns]=pchosen;filledtime[ns]=f;exittime[ns]=end;ns+=1
  qfills[q]+=1
  if outcome==1:qtp[q]+=1
  elif outcome==0:qstop[q]+=1
  elif outcome==2:qtime[q]+=1
  else:qcen[q]+=1
 return qfills,qtp,qstop,qtime,qcen,ids[:ns],sides[:ns],horizons[:ns],results[:ns],chosen_probability[:ns],filledtime[:ns],exittime[:ns]


def pfx(src,mon):return r.R24/'results'/src/mon/f'R24_{src}_{mon}_1000MS'

def predict_source(src,mon,boost,waitboost,chunk=65536):
 root=r.R24/'results'/src/mon
 X=np.load(str(pfx(src,mon))+'_features.npy',mmap_mode='r');n=len(X)
 pr_path=root/f'R24_{src}_{mon}_FROZEN_ASOF_FIVE_CAUSE_PROBABILITIES.npy'
 w_path=root/f'R24_{src}_{mon}_FROZEN_ASOF_WAIT10S_PROBABILITY.npy'
 marker=root/f'R24_{src}_{mon}_FROZEN_ASOF_INFERENCE_ATOMIC_COMPLETION.json'
 input_sha=r.sha(r.source_file(src,mon))
 boost_file=r.R24/'models'/mon/'R24_FROZEN_BROKER_CONDITIONED_MULTISCALE_FIRSTPASS_5_CAUSE_LGBM.txt'
 wait_file=r.R24/'models'/mon/'R24_FROZEN_OPPORTUNITY_WAIT10S_LGBM.txt'
 model_sha=r.sha(boost_file);wait_sha=r.sha(wait_file)
 if pr_path.exists() and w_path.exists() and marker.exists():
  receipt=json.loads(marker.read_text())
  if receipt.get('status')=='ATOMIC_FROZEN_PROBABILITIES_COMPLETE' and receipt.get('source_sha')==input_sha and receipt.get('hazard_model_sha')==model_sha and receipt.get('wait_model_sha')==wait_sha and receipt.get('n_asof_decisions')==n and receipt.get('probabilities_sha')==r.sha(pr_path) and receipt.get('wait_probabilities_sha')==r.sha(w_path):
   P=np.load(pr_path,mmap_mode='r');W=np.load(w_path,mmap_mode='r')
   if P.shape==(n,2,3,5) and W.shape==(n,):return P,W
 # A valid .npy header cannot certify a fully computed matrix. Never resume it.
 for old in (pr_path,w_path,marker):
  if old.exists():
   quarantine=old.with_name(old.name+'.INCOMPLETE_QUARANTINED')
   if quarantine.exists(): quarantine.unlink()
   os.replace(old,quarantine)
 P=np.lib.format.open_memmap(pr_path,mode='w+',dtype=np.float32,shape=(n,2,3,5))
 W=np.lib.format.open_memmap(w_path,mode='w+',dtype=np.float32,shape=(n,))
 fcount=X.shape[1]
 import gc
 for start in range(0,n,chunk):
  end=min(n,start+chunk);base=np.asarray(X[start:end],dtype=np.float32)
  W[start:end]=waitboost.predict(base,num_threads=2)
  M=np.empty((len(base),fcount+2),np.float32)
  M[:,:fcount]=base
  for si in range(2):
   M[:,fcount]=1 if si==0 else -1
   for h,hh in enumerate((15,30,60)):
    M[:,fcount+1]=hh
    vals=boost.predict(M,num_threads=2)
    if vals.shape!=(len(base),5):raise ValueError('CAUSAL_FIVE_CLASS_PROBABILITY_SHAPE')
    if not np.isfinite(vals).all():raise ValueError('NONFINITE_HAZARD_INFERENCE')
    P[start:end,si,h,:]=vals
  if start%524288==0:print('PREDICTION_PROGRESS',src,mon,start,'of',n,flush=True)
 P.flush();W.flush()
 if not np.isfinite(P).all() or not np.isfinite(W).all():raise RuntimeError('INCOMPLETE_NONFINITE_HAZARD_OUTPUT')
 if not np.allclose(np.asarray(P[::max(1,n//1000)]).sum(axis=-1),1.0,atol=2e-4):raise RuntimeError('INVALID_MULTICLASS_PROBABILITY_SUM')
 marker.write_text(json.dumps({'status':'ATOMIC_FROZEN_PROBABILITIES_COMPLETE','source':src,'month':mon,'n_asof_decisions':n,'source_sha':input_sha,'hazard_model_sha':model_sha,'wait_model_sha':wait_sha,'probabilities_sha':r.sha(pr_path),'wait_probabilities_sha':r.sha(w_path)},indent=2)+'\n')
 return P,W


def writecsv(p,rows):
 if not rows:raise RuntimeError('EMPTY_CSV')
 with Path(p).open('w',newline='',encoding='utf-8') as file:
  w=csv.DictWriter(file,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def group_metric(ref,filled,good,stop,timeout,censored):
 out=[]
 for i in range(len(ref)):
  completed=int(good[i]+stop[i]+timeout[i]);acc=float(good[i]/completed) if completed else None
  r0=int(ref[i]);cnt=int(filled[i]);win=int(good[i])
  out.append({'original_R9_SYNTH_source_reference':r0,'asof_positions_filled':cnt,
    'asof_TARGET_before_STOP':win,'asof_STOP_first':int(stop[i]),'asof_TIMEOUT':int(timeout[i]),
    'asof_RIGHT_CENSORED':int(censored[i]),'asof_completed_target_fraction':acc,
    'position_count_meets_source_quota':int(cnt>=r0) if r0 else None,
    'correct_positions_meet_R9_SYNTH_source_quota':int(win>=r0) if r0 else None,
    'joint_completed_accuracy80_and_filled_volume':int(cnt>=r0 and acc is not None and acc>=0.8) if r0 else None,
    'joint_correct_volume_and_completed_accuracy80':int(win>=r0 and acc is not None and acc>=0.8) if r0 else None,
    'source_is_active':int(r0>0)})
 return out


def replay_source(src,mon,model,waitmodel):
 start=time.monotonic();dest=r.R24/'results'/src/mon
 P,W=predict_source(src,mon,model,waitmodel)
 labels=np.load(str(pfx(src,mon))+'_labels_2SIDE_3HORIZON.npy',mmap_mode='r')
 T=np.load(str(pfx(src,mon))+'_signal_utc_ms.npy',mmap_mode='r')
 F=np.load(str(pfx(src,mon))+'_actual_fill_utc_ms.npy',mmap_mode='r')
 EVT=np.load(str(pfx(src,mon))+'_first_barrier_2SIDE_utc_ms.npy',mmap_mode='r')
 TO=np.load(str(pfx(src,mon))+'_true_timeout_first_observed_utc_ms.npy',mmap_mode='r')
 qr,qref=r.calendar_reference(mon);qfirst=int(qr[0]//900000);nq=len(qr)
 history=[];snapshots=[];best=None;bestkey=None
 thresholds=(0.30,0.40,0.50,0.60,0.70,0.80)
 maxstop=(0.50,0.70)
 waitweight=(0.0,0.12)
 lengthpenalty=(0.02,0.08)
 for thr in thresholds:
  for stopcap in maxstop:
   for wp in waitweight:
    for lp in lengthpenalty:
     res=replay_one_position(P,W,labels,T,F,EVT,TO,qfirst,nq,thr,stopcap,wp,lp)
     fc,tp,st,tmo,cen=res[:5]
     hourref=qref.reshape(-1,4).sum(axis=1);dayref=qref.reshape(-1,96).sum(axis=1)
     fh=fc.reshape(-1,4).sum(axis=1);th=tp.reshape(-1,4).sum(axis=1);sh=st.reshape(-1,4).sum(axis=1);tmh=tmo.reshape(-1,4).sum(axis=1);ch=cen.reshape(-1,4).sum(axis=1)
     fd=fc.reshape(-1,96).sum(axis=1);td=tp.reshape(-1,96).sum(axis=1);sd=st.reshape(-1,96).sum(axis=1);tmd=tmo.reshape(-1,96).sum(axis=1);cd=cen.reshape(-1,96).sum(axis=1)
     validq=qref>0;validh=hourref>0;validd=dayref>0
     done=tp+st+tmo;qh=th+sh+tmh;qd=td+sd+tmd
     prec=np.divide(tp,done,out=np.zeros(len(done),np.float64),where=done>0)
     prech=np.divide(th,qh,out=np.zeros(len(qh),np.float64),where=qh>0)
     precd=np.divide(td,qd,out=np.zeros(len(qd),np.float64),where=qd>0)
     joint_q=int(np.sum(validq&(tp>=qref)&(prec>=0.8)))
     joint_h=int(np.sum(validh&(th>=hourref)&(prech>=0.8)))
     joint_d=int(np.sum(validd&(td>=dayref)&(precd>=0.8)))
     qgood=int(tp.sum());qbad=int(st.sum()+tmo.sum());a=qgood/(qgood+qbad) if qgood+qbad else 0.0
     rec={'source':src,'month':mon,'min_target_probability':thr,'max_stop_probability':stopcap,'WAIT_opportunity_penalty':wp,'horizon_penalty_15s_per_bin':lp,
      'model_fitted_and_policy_selected_on_same_month_IN_SAMPLE':True,
      'R9_SYNTH_exact_original_source_month_volume':int(qref.sum()),'R9_SYNTH_month_active_hours':int(validh.sum()),'R9_SYNTH_month_active_15min':int(validq.sum()),
      'asof_filled_total':int(fc.sum()),'asof_TARGET_first_correct':qgood,'asof_STOP_first':int(st.sum()),'asof_TIMEOUT':int(tmo.sum()),'asof_CENSORED':int(cen.sum()),
      'asof_completed_TARGET_fraction':float(a),
      'active_15min_source_correct_quota_met':int(np.sum(validq&(tp>=qref))),
      'active_hour_source_correct_quota_met':int(np.sum(validh&(th>=hourref))),
      'active_days_source_correct_quota_met':int(np.sum(validd&(td>=dayref))),
      'active_15min_source_filled_quota_met':int(np.sum(validq&(fc>=qref))),
      'active_hour_source_filled_quota_met':int(np.sum(validh&(fh>=hourref))),
      'active_days_source_filled_quota_met':int(np.sum(validd&(fd>=dayref))),
      'joint_80pct_and_correct_quota_15min':joint_q,'joint_80pct_and_correct_quota_hours':joint_h,'joint_80pct_and_correct_quota_days':joint_d,
      'month_TARGET_meets_85pct_R9_volume':bool(qgood>=0.85*qref.sum()),
      'not_live_execution_or_independent_OOS':True}
     history.append(rec)
     # Pre-registered hyperoptimization on exposed labels, never input to signal inference.
     key=(joint_q,joint_h,joint_d,int(np.sum(validq&(tp>=qref))),int(np.sum(validh&(th>=hourref))),qgood,-qbad)
     if bestkey is None or key>bestkey:
      bestkey=key;best=(rec,res,fc,tp,st,tmo,cen,fh,th,sh,tmh,ch,fd,td,sd,tmd,cd)
 print('REPLAY_48_FULL_MONTH_POLICY_THRESHOLDS_COMPLETED',src,mon,flush=True)
 writecsv(dest/f'R24_{src}_{mon}_ALL_48_EXPOSED_INSAMPLE_POLICY_OPTIMIZATION_CASES.csv',history)
 rec,res,fc,tp,st,tmo,cen,fh,th,sh,tmh,ch,fd,td,sd,tmd,cd=best
 qgroups=group_metric(qref,fc,tp,st,tmo,cen)
 hgroups=group_metric(qref.reshape(-1,4).sum(axis=1),fh,th,sh,tmh,ch)
 dgroups=group_metric(qref.reshape(-1,96).sum(axis=1),fd,td,sd,tmd,cd)
 rowsq=[{'source':src,'month':mon,'utc_quarter':datetime.fromtimestamp(int(qr[i])/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),**qgroups[i]} for i in range(nq)]
 rowsh=[{'source':src,'month':mon,'utc_hour':rowsq[i*4]['utc_quarter'],**hgroups[i]} for i in range(nq//4)]
 rowsd=[{'source':src,'month':mon,'utc_day':rowsq[i*96]['utc_quarter'][:10],**dgroups[i]} for i in range(nq//96)]
 for suffix,arr in [('COMPLETE_15MIN',rowsq),('COMPLETE_HOURS',rowsh),('COMPLETE_UTC_DAYS',rowsd)]:
  writecsv(dest/f'R24_{src}_{mon}_BEST_ASOF_MONTH_POLICY_{suffix}.csv',arr)
 names=('observed_source_signal_row','side_buy1_sellminus1','horizon_bin_0_15s_1_30s_2_60s','source_firstpass_outcome','asof_target_probability','actual_fill_utc_ms','exit_utc_ms')
 np.savez_compressed(dest/f'R24_{src}_{mon}_ALL_BEST_ASOF_SELECTED_POSITIVE_AND_NEGATIVE_SOURCE_ORDINALS.npz',**dict(zip(names,res[5:])))
 sourcepath=r.source_file(src,mon)
 rec['policy_rank_lexicographic']=['joint80_goodquota_15min','joint80_goodquota_hour','joint80_goodquota_day','goodquota_15min','goodquota_hour','total_target','minus_bad']
 rec['replay_all_48_cases_includes_negative_asof_results']=True
 rec['source_original_raw_file_sha256']=r.source_pin(src,mon)
 rec['source_calendar_complete_hour_and_quarter_row_count']=[len(rowsh),len(rowsq)]
 rec['elapsed_seconds']=round(time.monotonic()-start,3)
 namesfiles=list(dest.glob(f'R24_{src}_{mon}_*ASOF*'))+list(dest.glob(f'R24_{src}_{mon}_ALL_48*'))
 rec['output_sha256']={f.name:hashlib.file_digest(open(f,'rb'),'sha256').hexdigest() for f in namesfiles}
 (dest/f'R24_{src}_{mon}_COMPLETE_FROZEN_CAUSAL_INSAMPLE_POLICY_RECEIPT.json').write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
 print('REPLAY_FULL_MONTH_FINAL',json.dumps({k:v for k,v in rec.items() if k not in ('output_sha256','policy_rank_lexicographic')},indent=2),flush=True)
 return rec

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',choices=r.SOURCE_NAMES,required=True);a.add_argument('--month',choices=('01','02','06','07'),required=True)
 x=a.parse_args();modeldir=r.R24/'models'/x.month
 m=lgb.Booster(model_file=str(modeldir/'R24_FROZEN_BROKER_CONDITIONED_MULTISCALE_FIRSTPASS_5_CAUSE_LGBM.txt'))
 w=lgb.Booster(model_file=str(modeldir/'R24_FROZEN_OPPORTUNITY_WAIT10S_LGBM.txt'))
 replay_source(x.source,x.month,m,w)
