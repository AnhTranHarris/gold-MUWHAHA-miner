"""Explicit BUY/SELL asymmetric selective learner of STRICT H1V2-R2 teacher.

Training: actual as-of 100 features, explicit side, directional quote motifs.
Teacher-only four-class future outcomes are targets; not inference features.
Two fits: intentionally all four in-sample, and Jan/Feb/Jun->July falsification.
NEVER use either for live or assume full 15.4M candidate volume.
"""
import time,json,hashlib
from pathlib import Path
import numpy as np
import lightgbm as lgb
from insample_skew_experiments import wilson
ROOT=Path('/mnt/data/h1v2_r2/results');MONTHS=('01','02','06','07')

def dataset():
 xs=[];ys=[];ts=[];cl=[];months=[]
 for m in MONTHS:
  with np.load(ROOT/f'H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz',allow_pickle=False) as z:
   xs.append(z['X'].copy());cl.append(z['side_class'].copy());ts.append(z['ts'].copy());months.extend([m]*len(z['X']))
 x=np.concatenate(xs);classes=np.concatenate(cl);ts=np.concatenate(ts);months=np.array(months)
 a=x[:,:99].reshape(-1,9,11)
 impulse=(a[:,:,4]-a[:,:,5])/(a[:,:,0]+.01)
 position=2*a[:,:,3]-1
 lead=(a[:,:,8]-a[:,:,9])/(a[:,:,8]+a[:,:,9]+1)
 order=a[:,:,1]
 # Same features, symmetric action transformations: row 0=BUY, row 1=SELL.
 # Stack by event, then by side so reshape (60000, 2) is exact.
 n=len(x);side=np.tile(np.array([1.,-1.],np.float32),n)
 X=np.repeat(x,2,axis=0)
 oriented=np.column_stack((side,side[:,None]*np.repeat(impulse,2,axis=0),side[:,None]*np.repeat(position,2,axis=0),
                           side[:,None]*np.repeat(lead,2,axis=0),side[:,None]*np.repeat(order,2,axis=0)))
 z=np.ascontiguousarray(np.column_stack([X,oriented]),dtype=np.float32)
 targets=(classes.reshape(-1)==3).astype(np.uint8)
 status=classes.reshape(-1)
 weights=np.select([status==0,status==1,status==2,status==3],[2.0,3.0,1.2,5.0]).astype(np.float32)
 return z,targets,classes,status,weights,months

def evaluate(p,klass,mon):
 prob=p.reshape(-1,2);which=np.argmax(prob,axis=1);best=prob[np.arange(len(prob)),which];other=prob[np.arange(len(prob)),1-which]
 label=klass[np.arange(len(prob)),which]
 result={}
 for cut in (.03,.05,.10,.15,.20,.30,.4,.5,.7,.8):
  gate=(best>=cut)&(best>=other+.10)
  n=int(gate.sum());strong=int(np.sum(gate&(label==3)))
  item={'n':n,'strong_correct':strong,'weak_good':int(np.sum(gate&(label==2))),'wrong':int(np.sum(gate&(label==0))),'neutral':int(np.sum(gate&(label==1))),
    'precision_strong':strong/n if n else None,'wilson_lower':wilson(strong,n), 'monthly':{}}
  for m in MONTHS:
   f=gate&(mon==m);item['monthly'][m]={'n':int(f.sum()),'strong_correct':int(np.sum(f&(label==3)))}
  result[str(cut)]=item
 for frac in (.01,.05):
  k=int(len(best)*frac);ix=np.argsort(-best)[:k];lab=label[ix]
  result[f'top{int(frac*100)}pct']={'n':k,'strong_correct':int((lab==3).sum()),'wrong':int((lab==0).sum()),'neutral':int((lab==1).sum()),'weak_good':int((lab==2).sum())}
 return result

def run():
 z,y,klass,status,weights,mon=dataset();assert len(klass)==60000 and len(z)==120000
 out={'type':'EXPERIMENTAL_FOUR_CLASS_ACTION_SELECTIVE_TEACHER_STUDENT','dataset_n_market_states':60000,'side_action_rows':120000,
      'strong_label_n':int(y.sum()),'side_class_count_WRONG_NEUTRAL_WEAK_STRONG':np.bincount(status,minlength=4).tolist(),
      'features':int(z.shape[1]),'models':{},'warning':'Student uses only as-of features but resubstitution scores are pure training diagnostics; July held-out is no qualified policy.'}
 for name,mask,rounds,leaves in [('S1_overfit_all_4',np.ones(len(klass),bool),320,63),('S2_leave_july_out',mon!='07',180,31)]:
  tic=time.monotonic();train=np.repeat(mask,2)
  boost=lgb.train(dict(objective='binary',num_leaves=leaves,min_data_in_leaf=8,learning_rate=.075,feature_fraction=1,verbosity=-1,num_threads=4,force_col_wise=True,seed=20261102),lgb.Dataset(z[train],label=y[train],weight=weights[train]),num_boost_round=rounds)
  prob=boost.predict(z,num_threads=4);p_train=evaluate(prob.reshape(-1,2)[mask],klass[mask],mon[mask]);by_month={m:evaluate(prob.reshape(-1,2)[mon==m],klass[mon==m],mon[mon==m]) for m in MONTHS}
  model_path=ROOT/f'H1V2_R2_{name}.txt';boost.save_model(str(model_path))
  with model_path.open('rb') as fh:sha=hashlib.file_digest(fh,'sha256').hexdigest()
  out['models'][name]={'params':{'trees':rounds,'leaves':leaves},'seconds':round(time.monotonic()-tic,2),'sha256':sha,'file':model_path.name,'training':p_train,'by_month':by_month}
  (ROOT/'H1V2_R2_ACTION_SELECTIVITY.json').write_text(json.dumps(out,indent=2))
  print(name,'seconds',out['models'][name]['seconds'],'training @.1',p_train['0.1'],'July @.1',by_month['07']['0.1'],flush=True)
 return out
if __name__=='__main__':run()
