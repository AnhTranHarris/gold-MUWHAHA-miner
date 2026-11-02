"""R10 large directly trained in-sample 3-way BUY/SELL/WAIT research learner.

250ms entry rows are exact first-observed raw ticks. R8 and R10 features
are independently precomputed strictly as-of. Future H1V2 labels are target
ONLY. Per-month FULL original candidate populations are scored and EXACT
one-open-position original R9 ActivePath close ordinals replayed (no hindsight
admission). In-sample training explicitly uses those same months, so neither
approval nor blind OOS is implied. R9 models and exit engine untouched.
"""
from __future__ import annotations
import os,json,math,pathlib,hashlib,argparse,time
import numpy as np
import lightgbm as lgb
from r9_side_competing import unpack,_replay_ordinal_selected
ROOT=pathlib.Path(os.getenv('H1V2_R10_ROOT','/mnt/data'))
H1=ROOT/'h1v2/results';R8=ROOT/'h1v2_r8/results';R7=ROOT/'h1v2_r7/results'
R10=ROOT/'h1v2_r10/results';R10.mkdir(parents=True,exist_ok=True)
MONTHS=('01','02','06','07');SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
FRACTIONS=(.0001,.0005,.001,.005,.01,.03,.05,.1,.25)
PER_MONTH=int(os.getenv("R10_SAMPLE_PER_MONTH","180000"))
TREES=int(os.getenv("R10_TREES","72"))
LEAVES=int(os.getenv("R10_LEAVES","47"))

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def load_data(mon):
 x=np.load(R8/f'R8_ASOF_{mon}.npy',mmap_mode='r')
 g=np.load(R10/f'R10_GRAMMAR_{mon}.npy',mmap_mode='r')
 with np.load(R7/f'R7_FULL_REGIME_{mon}.npz',allow_pickle=False) as z:reg=z['regime'].copy();ix=z['ix'].copy()
 if not(len(x)==len(g)==len(reg)==len(ix)):raise ValueError('asof schema mismatch')
 return x,g,reg,ix

def augment(x,g,r):
 return np.column_stack((np.asarray(x,dtype=np.float32),unpack(r),np.asarray(g,dtype=np.float32))).astype(np.float32)

def admission(prob):
 # 0 NONE (BUY and SELL BAD/NEUTRAL),1 BUY_GOOD,2 SELL_GOOD.
 pnone=prob[:,0];pbu=prob[:,1];psel=prob[:,2]
 side=(psel>pbu).astype(np.int8)
 best=np.maximum(pbu,psel);other=np.minimum(pbu,psel)
 distinct=(best-other)/(best+other+1e-9)
 score=best*(1.-pnone)*(.2+.8*np.maximum(0,distinct))
 return score.astype(np.float32),side,distinct.astype(np.float32)

def fit(mode):
 months=MONTHS if mode=='all4' else ('01','02','06')
 started=time.monotonic();Xs=[];Ys=[];integrity=[]
 for m in months:
  r10=json.loads((R10/f'R10_GRAMMAR_{m}_receipt.json').read_text());x,g,reg,ix=load_data(m)
  if sha(R10/f'R10_GRAMMAR_{m}.npy')!=r10['path_sha256']:raise ValueError('grammar mutated')
  rows=np.unique(np.linspace(0,len(x)-1, min(PER_MONTH,len(x)),dtype=np.int64))
  X=augment(x[rows],g[rows],reg[rows]);
  with np.load(H1/f'h1v2_dukascopy_{m}_oracle_labels.npz',allow_pickle=False) as d:
   if not np.array_equal(ix[rows],d['tick_index'][rows]):raise ValueError('teacher ordinal mismatch')
   y=d['code'][rows]
   if ((y[:,0]==1)&(y[:,1]==1)).any():raise ValueError('both strict labels good')
   yy=np.where(y[:,0]==1,1,np.where(y[:,1]==1,2,0)).astype(np.int8)
  Xs.append(X);Ys.append(yy);integrity.append({'month':m,'rows':len(rows),'asof_feature_sha256':r10['path_sha256']})
  print('TRAIN LOAD',mode,m,len(rows),np.bincount(yy,minlength=3).tolist(),flush=True)
 X=np.concatenate(Xs);y=np.concatenate(Ys)
 # Very high-capacity *deliberate in-sample* teacher-fitting probe.
 clf=lgb.LGBMClassifier(objective='multiclass',num_class=3,n_estimators=TREES,num_leaves=LEAVES,
  max_depth=-1,min_child_samples=85,learning_rate=.055,max_bin=63,colsample_bytree=.84,
  reg_lambda=6.,n_jobs=3,random_state=20261102,verbosity=-1,class_weight={0:1.,1:2.5,2:2.5})
 clf.fit(X,y)
 dest=R10/f'R10_{mode}_order_grammar_multiclass.txt';clf.booster_.save_model(str(dest))
 p=clf.predict_proba(X);scores,sides,marg=admission(p)
 thresholds={str(f):float(np.quantile(scores,1.-f)) for f in FRACTIONS}
 rec={'mode':mode,'training_months':list(months),'fitted_training_rows':len(y),'sample_per_month':PER_MONTH,
  'all_four_months_scored_in_full':False,'label_class_counts':np.bincount(y,minlength=3).tolist(),
  'feature_set':'R8 41 asof + R7 12 asof + R10 48 raw-order asof',
  'trees':TREES,'leaves':LEAVES,'class_weight':{'neutral':1,'buy_good':2.5,'sell_good':2.5},
  'frozen_training_only_thresholds':thresholds,
  'model_sha256':sha(dest),'training_sources':integrity,
  'fit_seconds':round(time.monotonic()-started,2),
  'status':'HEAVILY_IN_SAMPLE_FUTURE_TARGETS_TRAINING_NOT_FORESIGHT'}
 (R10/f'R10_{mode}_fit_receipt.json').write_text(json.dumps(rec,indent=2))
 print('FITTED',mode,rec['fit_seconds'],flush=True)
 return rec

def eval_month(mode,mon,chunk=250000):
 meta=json.loads((R10/f'R10_{mode}_fit_receipt.json').read_text());p=R10/f'R10_{mode}_order_grammar_multiclass.txt'
 if sha(p)!=meta['model_sha256']:raise ValueError('model mutated')
 clf=lgb.Booster(model_file=str(p))
 x,g,reg,ix=load_data(mon);n=len(ix)
 scores=np.empty(n,dtype=np.float32);side=np.empty(n,dtype=np.int8)
 stime=time.monotonic()
 for lo in range(0,n,chunk):
  hi=min(lo+chunk,n);X=augment(x[lo:hi],g[lo:hi],reg[lo:hi]);prob=clf.predict(X,num_threads=3)
  scores[lo:hi],side[lo:hi],_=admission(prob)
  print('SCORE',mode,mon,hi,n,flush=True)
 original=json.loads((H1/f'h1v2_dukascopy_{mon}_receipt.json').read_text())
 if sha(H1/f'h1v2_dukascopy_{mon}_oracle_labels.npz')!=original['teacher_labels_sha256']:raise ValueError('source teacher mutated')
 with np.load(H1/f'h1v2_dukascopy_{mon}_oracle_labels.npz',allow_pickle=False) as y:
  if not np.array_equal(ix,y['tick_index']):raise ValueError('raw source candidate indices drift')
  code=y['code'];net=y['net'];exitix=y['exit_tick_index']
  rec={'month':mon,'mode':mode,'full_eligible_candidates':n,'fit_month':mon in meta['training_months'],'r9_synth':SYNTH[mon],
   'experiments':{},'model_sha':meta['model_sha256'],
   'status':'HEAVILY_IN_SAMPLE_EXACT_R9_ORDINAL_REPLAY_NOT_TRADING'}
  for f,cut in meta['frozen_training_only_thresholds'].items():
   rows=np.flatnonzero(scores>=cut)
   sides=side[rows];cls=code[rows,sides]
   done,ok,neu,bad,unscored,value=_replay_ordinal_selected(rows,sides,ix,exitix,net,code)
   rec['experiments'][f]={'candidate_signals':len(rows),'candidate_strict_good':int((cls==1).sum()),
    'candidate_precision':float((cls==1).mean()) if len(cls) else None,'replay_count':done,'replay_good':ok,'replay_bad':bad,'replay_neutral':neu,
    'replay_precision':float(ok/done) if done else None,'modeled_net':round(value,2),
    'nonoverlap_80pct_synth_floor':math.ceil(.8*SYNTH[mon]),
    'joint_80pct':bool(done>=math.ceil(.8*SYNTH[mon]) and ok/done>=.8) if done else False}
    
   print('REPLAY',mode,mon,f,done,ok,round(ok/max(1,done),4),round(value,2),flush=True)
  rec['scoring_and_replay_seconds']=round(time.monotonic()-stime,2)
  (R10/f'R10_{mode}_{mon}_FULL_REPLAY.json').write_text(json.dumps(rec,indent=2))
  return rec
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['all4','lomo07'],default='all4');p.add_argument('--fit',action='store_true');p.add_argument('--month',choices=MONTHS);args=p.parse_args()
 if args.fit:fit(args.mode)
 elif args.month:eval_month(args.mode,args.month)
 else:p.error('pass --fit or --month')
