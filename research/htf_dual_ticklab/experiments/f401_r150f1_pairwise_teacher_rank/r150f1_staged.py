"""Memory-bounded exact source replay for R150F1; subprocess-per-cell, no fit/eval leak."""
from __future__ import annotations
import sys,json,zipfile,os,gc,time
from pathlib import Path
import numpy as np
from r150f1_pairwise_rescue import (P,R,ORACLE,getcell,teacher,matchpairs,fit_rank,fit_binary,predictions,metrics,calibrate,sha)
import lightgbm as lgb
D=R/'stages';D.mkdir(exist_ok=True)

def prepare(b,m):
 d=getcell(b,m)
 with zipfile.ZipFile(ORACLE) as z: t=teacher(b,m,d,z)
 a,c=matchpairs(d,limit_correct=2300,nneg=2,seed=15061+int(m)+(500 if b=='dukascopy' else 0))
 idx=np.empty(len(a)*2,dtype=np.int64);idx[::2]=a;idx[1::2]=c
 y0=np.zeros(len(idx),np.int8);y0[::2]=1
 y1=np.zeros(len(idx),np.int8);y1[::2]=t[a]>=t[c];y1[1::2]=t[c]>t[a]
 # explicit privilege split: only y1 is ever teacher-derived
 path=D/f'{b}_{m}_MATCHED_PAIRS.npz'
 np.savez_compressed(path,X=d['X'][idx],T0_original_correct_pair=y0,T1_privileged_teacher_order=y1,
  pair_positive_original_idx=a,pair_negative_original_idx=c,source_t=d['t'][idx],side=d['side'][idx],
  teacher_score_delta=t[a]-t[c])
 rec=dict(broker=b,month=m,n=len(d['t']),valid=int(d['valid'].sum()),pairs=int(len(a)),
  original_correct_pairs=int(len(a)),teacher_correct_higher=float(np.mean(t[a]>t[c])),sources=d['provenance'],hash=sha(path))
 (D/f'{b}_{m}_PAIRS_RECEIPT.json').write_text(json.dumps(rec,indent=2))
 print(json.dumps(rec),flush=True)

def train(b):
 XX=[];Y0=[];Y1=[]
 for m in ('01','02'):
  with np.load(D/f'{b}_{m}_MATCHED_PAIRS.npz') as z:
   XX.append(z['X']);Y0.append(z['T0_original_correct_pair']);Y1.append(z['T1_privileged_teacher_order'])
 x=np.concatenate(XX);a=np.concatenate(Y0);t=np.concatenate(Y1)
 print(json.dumps(dict(stage='train',broker=b,x=x.shape,teacher_rank_agreement=float(np.mean(t[::2])))),flush=True)
 for tag,kind,y,seed,rounds in [('T1_OFFLINE_TEACHER_RANK','rank',t,15011,95),('T0_ORIGINAL_PAIR_RANK','rank',a,15021,125),('T0_ORIGINAL_CLASS','binary',a,15031,140)]:
  model=fit_rank(x,y,seed,rounds) if kind=='rank' else fit_binary(x,y,seed,rounds)
  out=R/'models'/f'{b}_{tag}.txt';model.save_model(str(out));print(json.dumps(dict(broker=b,model=tag,size=out.stat().st_size,sha256=sha(out))),flush=True)
  del model;gc.collect()

def score(b,m):
 d=getcell(b,m)
 models={n:lgb.Booster(model_file=str(R/'models'/f'{b}_{n}.txt')) for n in ['T1_OFFLINE_TEACHER_RANK','T0_ORIGINAL_PAIR_RANK','T0_ORIGINAL_CLASS']}
 sc={}
 for name,mdls in [('T1_ORACLE_TRAINED',[models['T1_OFFLINE_TEACHER_RANK']]),('T0_RANK',[models['T0_ORIGINAL_PAIR_RANK']]),('T0_BINARY',[models['T0_ORIGINAL_CLASS']]),('T0_FUSION',[models['T0_ORIGINAL_PAIR_RANK'],models['T0_ORIGINAL_CLASS']])]:
  sc[name]=predictions(mdls,d)
 out=D/f'{b}_{m}_SCORED_SHADOW.npz'
 np.savez_compressed(out,t=d['t'],side=d['side'],truth=d['truth'],valid=d['valid'],veto=d['veto'],
  **{f'score_{k}':v for k,v in sc.items()})
 print(json.dumps(dict(stage='score',broker=b,month=m,sha256=sha(out),count=len(d['t']),eligible=int((d['valid']&d['veto']).sum()))),flush=True)

def recount(b):
 with np.load(D/f'{b}_06_SCORED_SHADOW.npz') as z:
  q6={k:z[k] for k in z.files}
 with np.load(D/f'{b}_07_SCORED_SHADOW.npz') as z:
  q7={k:z[k] for k in z.files}
 def asd(d):return dict(truth=d['truth'],veto=d['veto'],valid=d['valid'])
 results={}
 for tag in ['T1_ORACLE_TRAINED','T0_RANK','T0_BINARY','T0_FUSION']:
  v6=q6['score_'+tag];v7=q7['score_'+tag]
  cut,grid,selected=calibrate(asd(q6),v6,max_bad_per_good=1.0,min_good=30)
  cal=metrics(asd(q6),v6,cut);ev=metrics(asd(q7),v7,cut)
  results[tag]=dict(calibration=cal,evaluation=ev,selected=selected,grid=grid,teacher_in_fit=tag.startswith('T1'))
  if not tag.startswith('T1'):
   mask=np.zeros(len(v7),bool) if not np.isfinite(cut) else q7['valid']&q7['veto']&(v7>=cut)
   out=R/'masks'/f'{b}_{tag}_JULY_SHADOW.npz'
   np.savez_compressed(out,t=q7['t'],side=q7['side'],truth=q7['truth'],valid=q7['valid'],r148_veto=q7['veto'],
    proposal_score=v7,proposed_rescue=mask,approved_override=np.array([False]))
 out=dict(broker=b,training=['01','02'],calibration='06',test='07',models=results,
  teacher_inference=False,decision_parent='R148B unchanged',new_order_submitted=False,
  interpretation='July held out for R150F1 but exposed to frozen R148B and original same-month teacher; not full-stack OOS or executable action outcomes')
 file=R/'results'/f'{b}_R150F1_RESEARCH.json';file.write_text(json.dumps(out,indent=2,allow_nan=False))
 print(json.dumps({k:{'july_auc':v['evaluation']['auc'],'top25':v['evaluation']['recall_0.25'],
  'calibrated_june':v['selected'],'july_fixed_cut':v['evaluation'].get('frozen_threshold')} for k,v in results.items()},indent=2),flush=True)

if __name__=='__main__':
 task=sys.argv[1];b=sys.argv[2]
 if task=='prepare':prepare(b,sys.argv[3])
 elif task=='train':train(b)
 elif task=='score':score(b,sys.argv[3])
 elif task=='recount':recount(b)
 else:raise SystemExit(task)
