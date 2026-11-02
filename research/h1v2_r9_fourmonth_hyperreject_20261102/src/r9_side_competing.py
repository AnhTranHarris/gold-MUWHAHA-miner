"""H1V2 R9 side-independent competing BAD/NEUTRAL/GOOD hindsight study.

Exploratory IN-SAMPLE model deliberately allowed (training uses future outcome
labels); *features* remain strictly as-of quote ordinal. No EA policy approval.
This continuation consumes 100% R8 causal features and 100% R7 causal nested
regime states for each month, replaying original H1V2 30s R9 exits.
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, time, os
import numpy as np
import lightgbm as lgb
from numba import njit

ROOT=pathlib.Path(os.getenv('H1V2_R9_ROOT','/mnt/data')).expanduser().resolve()
R8=ROOT/'h1v2_r8/results';R7=ROOT/'h1v2_r7/results';H1=ROOT/'h1v2/results'
OUT=ROOT/'h1v2_r9_hyperreject/results';OUT.mkdir(parents=True,exist_ok=True)
MONTHS=('01','02','06','07')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
FEATURES=['r7_1s_sign','r7_15s_sign','r7_5min_sign','r7_1h_sign',
          'r7_spread_bucket','r7_quote_rate_bucket','r7_session_bucket','r7_path_eff_bucket',
          'nested_1s_vs_15s','nested_15s_vs_5min','nested_5min_vs_1h','one_s_higher_trend_concordance']
SAMPLE_PER_MONTH=180000
FRACTIONS=(.0001,.0005,.001,.005,.01,.03,.05,.10,.25)

def sha(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def load(month,slice_rows=None):
 rc=json.loads((R8/f'R8_ASOF_{month}_receipt.json').read_text())
 if sha(R8/f'R8_ASOF_{month}.npy')!=rc['features_sha256']:raise ValueError('ASOF source hash mismatch')
 r7=json.loads((R7/f'R7_FULL_MONTH_{month}_receipt.json').read_text())
 if sha(R7/f'R7_FULL_REGIME_{month}.npz')!=r7['regime_record_sha256']:raise ValueError('R7 regime hash mismatch')
 x=np.load(R8/f'R8_ASOF_{month}.npy',mmap_mode='r')
 with np.load(R7/f'R7_FULL_REGIME_{month}.npz') as z:
  rr=z['regime'];ix=z['ix']
 if len(x)!=len(rr):raise ValueError('R7/R8 candidate population mismatch')
 if slice_rows is None: return x,rr,ix
 return x[slice_rows],rr[slice_rows],ix[slice_rows]

def unpack(regime):
 r=np.asarray(regime,dtype=np.int64)
 eff=r%3; sess=(r//3)%4; rate=(r//12)%4; spread=(r//48)%5
 tr=r//240
 one=(tr%3)-1;fifteen=((tr//3)%3)-1;five=((tr//9)%3)-1;hour=((tr//27)%3)-1
 extra=[one,fifteen,five,hour,spread,rate,sess,eff,
        one*fifteen,fifteen*five,five*hour,
        (one==fifteen).astype(np.int8)+(fifteen==five).astype(np.int8)+(five==hour).astype(np.int8)]
 return np.column_stack(extra).astype(np.float32)

def augment(x,regime):
 x=np.asarray(x,dtype=np.float32)
 result=np.column_stack((x,unpack(regime)))
 if result.ndim!=2 or result.shape[1]!=len(FEATURES)+x.shape[1] or not np.isfinite(result).all():
  raise ValueError('nonfinite or wrong H1V2 asof schema')
 return result

def sample_month(month,n=SAMPLE_PER_MONTH):
 x,rr,ix=load(month)
 rows=np.linspace(0,len(x)-1,min(len(x),n),dtype=np.int64)
 rows=np.unique(rows)
 X=augment(x[rows],rr[rows])
 with np.load(H1/f'h1v2_dukascopy_{month}_oracle_labels.npz') as y:
  if not np.array_equal(ix[rows],y['tick_index'][rows]):raise ValueError('candidate exact ordinal mismatch')
  code=y['code'][rows].astype(np.int8)
 if not np.isin(code,[-1,0,1]).all():raise ValueError('label class schema unexpected')
 return X,code

def train(mode,months,trees=130,leaves=93,n=SAMPLE_PER_MONTH):
 start=time.time();X=[];Y=[]
 for m in months:
  x,c=sample_month(m,n);X.append(x);Y.append(c)
  print('TRAIN LOADED',mode,m,len(x),[(v,int((c==v).sum())) for v in (-1,0,1)],flush=True)
 X=np.concatenate(X,axis=0);Y=np.concatenate(Y,axis=0)
 common=dict(objective='multiclass',num_class=3,n_estimators=trees,num_leaves=leaves,
   learning_rate=.07,min_child_samples=120,max_bin=127,colsample_bytree=.85,reg_lambda=10,
   subsample=.85,subsample_freq=1,random_state=20261102,n_jobs=3,verbosity=-1)
 fitted={}
 for side in range(2):
  # 0 BAD, 1 NEUTRAL, 2 GOOD. Always train both sides, including hard negatives.
  mdl=lgb.LGBMClassifier(**common)
  mdl.fit(X,(Y[:,side]+1).astype('int8'))
  fname=OUT/f'R9_{mode}_{"BUY" if side==0 else "SELL"}_competing.txt'
  mdl.booster_.save_model(str(fname));fitted[side]=mdl.booster_
  print('FITTED',mode,side,round(time.time()-start,2),flush=True)
 thresholds={}
 # Fix thresholds from TRAIN prediction before testing. Same four in-sample admitted explicitly.
 probs=np.empty((len(X),2,3),dtype=np.float32)
 for side in range(2):probs[:,side]=fitted[side].predict(X,num_threads=3)
 scores,side,ambiguity=admission(probs)
 for f in FRACTIONS:
  thresholds[str(f)]=float(np.quantile(scores,1-f))
 result={'mode':mode,'training_months':list(months),'sample_rows_per_month_max':n,'n_training_rows':len(X),
   'separate_multiclass_side_models':True,'classes':{'0':'BAD','1':'NEUTRAL','2':'GOOD'},
   'fit_features':['R8_41_FULL_ASOF','R7_12_NESTED_REGIME'],
   'trees':trees,'leaves':leaves,'frozen_thresholds':thresholds,
   'training_selected_correctness':{},'model_sha256':{},'research_status':'HINDSIGHT_TRAINING_FUTURE_TARGETS_ONLY_NO_VALIDATED_POLICY'}
 for f in FRACTIONS:
  mask=scores>=thresholds[str(f)];rows=np.flatnonzero(mask)
  correct=(Y[rows,side[rows]]==1).sum()
  result['training_selected_correctness'][str(f)]={'rows':len(rows),'correct':int(correct),'precision':float(correct/len(rows)) if len(rows) else None}
 for side in range(2):
  path=OUT/f'R9_{mode}_{"BUY" if side==0 else "SELL"}_competing.txt'
  result['model_sha256'][str(side)]=sha(path)
 result['fit_seconds']=round(time.time()-start,2)
 (OUT/f'R9_{mode}_FIT.json').write_text(json.dumps(result,indent=2))
 print('FIT DONE',mode,result['fit_seconds'],flush=True)
 return result

def admission(probs):
 """Neyman Pearson motivated strict GOOD vs dangerous BAD & misleading NEUTRAL odds.

 Downweighting neutral relative to BAD is NOT empirical calibration. These scores
 are deterministic research rankings ONLY, not calibrated probabilities.
 """
 p_good=probs[:,:,2];p_bad=probs[:,:,0];p_neut=probs[:,:,1]
 # Unique-side exclusivity; punish high opposite-side GOOD odds and high neutral
 raw=p_good/(.8*p_bad+.2*p_neut+1e-6)
 side=np.argmax(raw,axis=1).astype(np.int8)
 best=raw[np.arange(len(side)),side]
 other=raw[np.arange(len(side)),1-side]
 margin=np.maximum(0,(best-other)/(best+other+1e-6))
 # Directly penalize no-opportunity and ambiguity rather than default BUY/SELL.
 score=best*(.2+.8*margin)*p_good[np.arange(len(side)),side]
 return score.astype(np.float32),side,margin

@njit(cache=True)
def _replay_ordinal_selected(rows,s,ix,ex,net,c):
 """One live-research position at a time, without selecting future good labels."""
 done=ok=neu=bad=unscored=0
 value=0.0;last_exit=-1
 for k in range(len(rows)):
  row=rows[k];side=s[k];ent=ix[row]
  if ent<=last_exit:continue
  exit_idx=ex[row,side];pnl=net[row,side]
  if exit_idx<=ent or not np.isfinite(pnl):
   unscored+=1;continue
  last_exit=exit_idx;done+=1;value+=pnl
  if c[row,side]==1:ok+=1
  elif c[row,side]==0:neu+=1
  else:bad+=1
 return done,ok,neu,bad,unscored,value

def eval_month(mode,month,chunk=240000):
 meta=json.loads((OUT/f'R9_{mode}_FIT.json').read_text());models=[]
 for side in range(2):
  p=OUT/f'R9_{mode}_{"BUY" if side==0 else "SELL"}_competing.txt'
  if sha(p)!=meta['model_sha256'][str(side)]:raise ValueError('model hash mismatch')
  models.append(lgb.Booster(model_file=str(p)))
 x,r7,ix=load(month);n=len(x)
 scores=np.empty(n,np.float32);choices=np.empty(n,np.int8);margins=np.empty(n,np.float32)
 start=time.time()
 for st in range(0,n,chunk):
  en=min(st+chunk,n);X=augment(x[st:en],r7[st:en])
  p=np.stack([model.predict(X,num_threads=3) for model in models],axis=1)
  scores[st:en],choices[st:en],margins[st:en]=admission(p)
  if st==0 or (en//chunk)%5==0:print('SCORED',mode,month,en,'/',n,flush=True)
 with np.load(H1/f'h1v2_dukascopy_{month}_oracle_labels.npz') as y:
  if not np.array_equal(ix,y['tick_index']):raise ValueError('exact tick-index parity failure')
  c=y['code'].copy();net=y['net'].copy();ex=y['exit_tick_index'].copy()
 result={'mode':mode,'month':month,'in_sample_training_month':month in meta['training_months'],
  'exhaustive_candidate_count':n,'r9_synth_comparator':SYNTH[month],
  'thresholds_source':'frozen TRAIN sample ranking, NO evaluation-month score quantile','experiments':{},
  'warning':'H1V2 in-sample high capacity model, LOMO comparison separate. As-of model features; oracle future labels are training targets; source-exact replay is hypothetical and not broker fills.'}
 for fraction,threshold in meta['frozen_thresholds'].items():
  rows=np.flatnonzero(scores>=threshold);s=choices[rows]
  correct=int(np.count_nonzero(c[rows,s]==1));neutral=int(np.count_nonzero(c[rows,s]==0));wrong=int(np.count_nonzero(c[rows,s]==-1))
  # Rank by time; one position max; rejects are not retrospectively selected with future label
  done,ok,neu,bad,unscored,value=_replay_ordinal_selected(rows,s,ix,ex,net,c)
  assert done==ok+neu+bad
  result['experiments'][fraction]={'frozen_score_cutoff':threshold,'candidate_signals':len(rows),
   'candidate_good':correct,'candidate_bad':wrong,'candidate_neutral':neutral,
   'candidate_precision':correct/len(rows) if len(rows) else None,'replay_trades':done,
   'replay_good':ok,'replay_bad':bad,'replay_neutral':neu,'unscorable':unscored,
   'replay_precision':ok/done if done else None,'replay_modeled_net':round(value,2),
   'replay_count_to_synth':done/SYNTH[month],
   'monthly_floor_count_met':done>=math.ceil(.8*SYNTH[month]),
   'joint_strict_correctness_and_count_met':done>=math.ceil(.8*SYNTH[month]) and ok/done>=.8 if done else False}
  print('REPLAY',mode,month,fraction,'n',done,'strict',round(ok/done,4) if done else 0,'net',round(value),flush=True)
 result['elapsed_seconds']=round(time.time()-start,2)
 (OUT/f'R9_{mode}_{month}_EXHAUSTIVE_REPLAY.json').write_text(json.dumps(result,indent=2))
 print('MONTH FROZEN',mode,month,round(time.time()-start,1),flush=True)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fit',choices=('all4','lomo07'))
 p.add_argument('--evaluate',choices=MONTHS);p.add_argument('--mode',choices=('all4','lomo07'),default='all4')
 p.add_argument('--trees',type=int,default=130);p.add_argument('--leaves',type=int,default=93)
 a=p.parse_args()
 if a.fit:
  train(a.fit,MONTHS if a.fit=='all4' else tuple(x for x in MONTHS if x!='07'),trees=a.trees,leaves=a.leaves)
 elif a.evaluate:eval_month(a.mode,a.evaluate)
 else:p.error('need --fit or --evaluate')
