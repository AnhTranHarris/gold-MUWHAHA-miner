"""F401 R150F-1 paired ranking foresight research, NO TRADE EXECUTION.
Owner-scoped original 2026 Jan/Feb FIT, June calibration, July frozen evaluation.
T1 offline teacher-ranked pair oracle *not at inference*, T0 original-class-only.
R148B immutable. Existing original causal publishers reused verbatim.
"""
import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import io,json,zipfile,hashlib,pathlib,time,gc,sys
import numpy as np
import lightgbm as lgb
from sklearn.metrics import roc_auc_score
P=pathlib.Path('/mnt/data');R=P/'R150F1'
for folder in ('source','models','results','masks'):(R/folder).mkdir(exist_ok=True,parents=True)
ORACLE=P/'R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip'
CONT=['path_signed_ret_15000ms','path_efficiency_signed','path_final_signed','path_signed_ret_1000ms','path_step_signed_1000_2000ms']
QUALITY=['r149::quote_completed_1000ms_time_coverage','r149::quote_completed_500ms_time_coverage','r149::quote_completed_15000ms_bb_width_atr','r149::quote_completed_5000ms_bb_width_atr','r149::quote_completed_60000ms_bb_width_atr','r149rec::hmm_shock_60000ms']
MATURE=['matured_all_count_log_60m','matured_r148_veto_count_log_60m','matured_all_count_log_10m']

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while x:=f.read(4<<20):h.update(x)
 return h.hexdigest()

def getcell(b,m):
 p0=P/'R150C/features'/f'R150C_{b}_{m}_WORLD_STATE.npz'
 p1=P/'R150D/path'/f'R150D_{b}_{m}_R147_STRICT_PATH.npz'
 p2=P/'R150E/features'/f'R150E_{b}_{m}_R147_DIRECT_HTF_INTER36.npz'
 p3=P/f'F401_R150F_{b}_{m}_MATURED_FEEDBACK_AUDIT.npz'
 with np.load(p0) as a,np.load(p1) as q,np.load(p2) as h,np.load(p3) as k:
  assert np.array_equal(a['t'],q['t']) and np.array_equal(a['t'],h['t']) and np.array_equal(a['t'],k['t'])
  assert np.array_equal(a['decision'],k['decision'])
  names0=list(a['source_names']);names1=list(q['source_names']);names2=list(k['names'])
  cont=np.column_stack([q['X'][:,names1.index(x)] for x in CONT]).astype('float32')
  qual=np.column_stack([a['X_source'][:,names0.index(x)] for x in QUALITY]).astype('float32')
  mature=np.column_stack([k['X'][:,names2.index(x)] for x in MATURE]).astype('float32')
  # fixed architecture cross-axis interactions: continuation * quality, plus shock*quote coverage
  interaction=np.column_stack([cont[:,i]*qual[:,j] for i in range(4) for j in range(4)]+[cont[:,2]*mature[:,i] for i in range(3)]).astype('float32')
  base=np.concatenate([a['X_source'],q['X'],h['X'],a['X_parent'],mature,cont,qual,interaction],axis=1)
  valid=a['valid']&q['available']&h['valid']
  x=np.nan_to_num(base,nan=0.0,posinf=0.0,neginf=0.0).astype('float32')
  d=dict(X=x,valid=valid,veto=a['r148_veto'],truth=a['truth'],t=a['t'],decision=a['decision'],side=a['side'],parent=a['X_parent'],
    provenance={str(v):sha(p) for v,p in [('world',p0),('path',p1),('htf',p2),('matured',p3)]})
  return d

def teacher(b,m,d,opened_zip):
 with np.load(io.BytesIO(opened_zip.read(f'FILTER08/FITTED_CLASSIFIER_SCORES_{b}_{m}.npz'))) as z:
  assert np.array_equal(z['t'],d['t']) and np.array_equal(z['original_side'],d['side']) and np.array_equal(z['truth_class'],d['truth'])
  return np.asarray(z['score'],dtype='float32')

def matchpairs(d,limit_correct=2300,nneg=2,seed=1):
  # Class-only pairing: teacher scores do not control pair eligibility or membership.
  # Parent score is known before decision; coarse clock/side/group used as matching covariates.
  rng=np.random.default_rng(seed)
  elig=d['valid']&d['veto'];pos=np.flatnonzero(elig&(d['truth']==0));bad=np.flatnonzero(elig&(d['truth']!=0))
  if len(pos)>limit_correct:pos=np.sort(rng.choice(pos,limit_correct,replace=False))
  # bucket only causal parent risk, side, UTC hour sector (4h), and present 1s quote coverage band
  risk=d['parent'][:,0]
  # parent risk may be constant zero if unavailable; still deterministic
  q=np.nanquantile(risk[bad],[.2,.4,.6,.8]); rb=np.searchsorted(q,risk)
  hr=((d['decision']//3600000)%24)//4
  cov=d['X'][:,-(19+0)] if False else d['X'][:,0] # no dependence on next values, just fallback
  groups={}
  for i in bad:
   key=(int(rb[i]),int(d['side'][i]),int(hr[i]))
   groups.setdefault(key,[]).append(i)
  x1=[];x0=[]
  for i in pos:
   key=(int(rb[i]),int(d['side'][i]),int(hr[i]))
   candidates=groups.get(key)
   if not candidates: candidates=groups.get((int(rb[i]),int(d['side'][i]),(int(hr[i])+1)%6))
   if not candidates:continue
   for j in rng.choice(candidates,size=nneg,replace=len(candidates)<nneg):
    x1.append(int(i));x0.append(int(j))
  a=np.asarray(x1,dtype='int64');b=np.asarray(x0,dtype='int64')
  # pair order is arbitrary, alternating across pairs; teacher T1 may reverse the label.
  return a,b

def pairdata(ds,teach,b,seed):
 X=[];y0=[];y1=[];spans=[]
 for m,d in ds:
  a,c=matchpairs(d,seed=seed+int(m)+(500 if b=='dukascopy' else 0))
  n=len(a);idx=np.empty(n*2,np.int64);idx[::2]=a;idx[1::2]=c
  yy=np.zeros(n*2,np.int8);yy[::2]=1
  sc=teach[m];te=np.zeros(n*2,np.int8);te[::2]=sc[a]>=sc[c];te[1::2]=sc[c]>sc[a]
  X.append(d['X'][idx]);y0.append(yy);y1.append(te);spans.append(dict(month=m,pairs=n,teacher_pair_correct_win=float(np.mean(sc[a]>sc[c]))))
 return np.concatenate(X),np.concatenate(y0),np.concatenate(y1),spans

def fit_rank(x,y,seed,rounds=125):
  group=np.full(len(y)//2,2,dtype=np.int32)
  ds=lgb.Dataset(x,label=y,group=group,free_raw_data=True)
  opts=dict(objective='lambdarank',metric='ndcg',label_gain=[0,1],verbosity=-1,learning_rate=.035,num_leaves=19,min_data_in_leaf=95,
        lambda_l2=12.,feature_fraction=.8,max_bin=63,seed=seed,num_threads=2,deterministic=True,force_col_wise=True)
  return lgb.train(opts,ds,num_boost_round=rounds)

def fit_binary(x,y,seed,rounds=160):
 ds=lgb.Dataset(x,label=y,free_raw_data=True)
 return lgb.train(dict(objective='binary',verbosity=-1,learning_rate=.04,num_leaves=21,min_data_in_leaf=100,lambda_l2=13.,feature_fraction=.8,
  max_bin=63,seed=seed,num_threads=2,deterministic=True,force_col_wise=True),ds,num_boost_round=rounds)

def predictions(models,d):
 ix=np.flatnonzero(d['veto']&d['valid']);v=np.zeros(len(d['truth']),np.float32)
 for s in range(0,len(ix),40000):
  ii=ix[s:s+40000];v[ii]=np.mean([m.predict(d['X'][ii],num_threads=2).astype(np.float32) for m in models],axis=0)
 return v

def metrics(d,s,threshold=None,recalls=(.1,.25,.5)):
 ix=np.flatnonzero(d['veto']&d['valid']);yy=(d['truth'][ix]==0)
 results=dict(n=int(len(ix)),correct=int(yy.sum()),bad=int((~yy).sum()),auc=float(roc_auc_score(yy,s[ix])))
 for t in recalls:
  target=int(np.ceil(t*int(yy.sum())))
  cut=np.sort(s[ix[yy]])[-target] if target else float('inf')
  picked=ix[s[ix]>=cut];rc=int(np.count_nonzero(d['truth'][picked]==0));bb=len(picked)-rc
  results['recall_'+str(t)]=dict(correct=rc,bad=bb,bad_per_correct=float(bb/max(1,rc)),precision=float(rc/len(picked)) if len(picked) else None)
 if threshold is not None:
  chosen=ix[s[ix]>=threshold];rc=int(np.count_nonzero(d['truth'][chosen]==0));opp=int(np.count_nonzero(d['truth'][chosen]==1));neu=int(np.count_nonzero(d['truth'][chosen]==2))
  results['frozen_threshold']=dict(cut=(float(threshold) if np.isfinite(threshold) else None),rescued_correct=rc,re_admitted_opposite=opp,re_admitted_neutral=neu,bad=opp+neu,
    bad_per_correct=float((opp+neu)/rc) if rc else None,correct_lost_remaining=int(np.count_nonzero(d['veto']&(d['truth']==0)))-rc)
 return results

def calibrate(d,score,max_bad_per_good=1.0,min_good=30):
 ix=np.flatnonzero(d['veto']&d['valid']);s=score[ix];y=(d['truth'][ix]==0)
 cuts=np.unique(np.quantile(s,[.990,.992,.994,.995,.996,.997,.998,.9985,.999,.9993,.9995,.9997,.9998,.9999,1]))
 rows=[]
 for cut in cuts:
  m=(s>=cut);g=int(np.count_nonzero(m&y));b=int(np.count_nonzero(m&~y))
  rows.append(dict(cut=float(cut),correct=g,bad=b,ratio=float(b/g) if g else None))
 viable=[r for r in rows if r['correct']>=min_good and r['bad']<=max_bad_per_good*r['correct']]
 best=max(viable,key=lambda r:(r['correct'],-r['bad'])) if viable else None
 return (best['cut'] if best is not None else float('inf')),rows,best

def execute(b):
 start=time.time();audit={'broker':b,'fit':['01','02'],'cal':'06','test':'07','parent':'R148B IMMUTABLE','approval':'UNAPPROVED_SHADOW','source_exact':{}}
 X_all=[];Y0_all=[];Y1_all=[];spans=[]
 with zipfile.ZipFile(ORACLE) as z:
  for m in ['01','02']:
   print(f'[{b}] loading {m}',flush=True)
   d=getcell(b,m);print(f'[{b}] loaded {m}',flush=True)
   t=teacher(b,m,d,z);print(f'[{b}] teacher read {m}',flush=True);audit['source_exact'][m]=d['provenance']
   x,y0,y1,sp=pairdata([(m,d)],{m:t},b,15061);print(f'[{b}] paired {m} count={len(y0)//2}',flush=True)
   X_all.append(x);Y0_all.append(y0);Y1_all.append(y1);spans.extend(sp)
   del d,t,x,y0,y1;gc.collect()
 x=np.concatenate(X_all);y0=np.concatenate(Y0_all);y1=np.concatenate(Y1_all)
 del X_all,Y0_all,Y1_all;gc.collect()
 audit['pair_sample']=spans;audit['dimensions']=int(x.shape[1]);audit['pairs']=int(len(y0)//2)
 print(f'[{b}] training {audit["pairs"]} pairs with {audit["dimensions"]} features',flush=True)
 t1=fit_rank(x,y1,15011)
 t0=fit_rank(x,y0,15021)
 t0b=fit_binary(x,y0,15031)
 for nm,mod in [('T1_OFFLINE_TEACHER_RANK',t1),('T0_ORIGINAL_PAIR_RANK',t0),('T0_ORIGINAL_CLASS',t0b)]:
  mod.save_model(str(R/'models'/f'{b}_{nm}.txt'))
 del x,y0,y1;gc.collect()
 candidate=[('T1_TEACHER_ONLY',[t1]),('T0_RANK',[t0]),('T0_BINARY',[t0b]),('T0_FUSION',[t0,t0b])]
 scores={};d6=getcell(b,'06');audit['source_exact']['06']=d6['provenance']
 for name,mods in candidate:
  sc6=predictions(mods,d6);cut,grid,sel=calibrate(d6,sc6,max_bad_per_good=1.0,min_good=30)
  scores[name]=dict(calibration=metrics(d6,sc6,cut),selected=sel,grid=grid,teacher_in_fit=(name=='T1_TEACHER_ONLY'),threshold=cut)
  print(f'[{b}] June {name} cut={cut} selected={sel}',flush=True)
 del d6,sc6;gc.collect()
 d7=getcell(b,'07');audit['source_exact']['07']=d7['provenance']
 for name,mods in candidate:
  sc7=predictions(mods,d7);cut=scores[name].pop('threshold')
  scores[name]['evaluation']=metrics(d7,sc7,cut)
  if name!='T1_TEACHER_ONLY':
   np.savez_compressed(R/'masks'/f'{b}_{name}_JULY_SHADOW.npz',t=d7['t'],side=d7['side'],truth=d7['truth'],valid=d7['valid'],r148_veto=d7['veto'],proposal_score=sc7,
     proposed_rescue=(d7['veto']&d7['valid']&(sc7>=cut)) if np.isfinite(cut) else np.zeros(len(sc7),bool),approved_override=np.array([False]))
  print(f'[{b}] July {name} AUC {scores[name]["evaluation"]["auc"]:.5f}, top25 {scores[name]["evaluation"]["recall_0.25"]}',flush=True)
  del sc7;gc.collect()
 audit['models']=scores
 audit['holdout_caveat']='July not used to fit R150F1 but R148B parent and FITTED_CLASSIFIER teacher historically exposed to it; NOT full-stack OOS.'
 audit['teacher_in_runtime']=False;audit['time_sec']=round(time.time()-start,1)
 (R/'results'/f'{b}_R150F1_RESEARCH.json').write_text(json.dumps(audit,indent=2,allow_nan=False))
 print(json.dumps({"broker":b,"dims":audit['dimensions'],"pairs":audit['pairs'],"july":{k:{"auc":round(v['evaluation']['auc'],5),"top25":v['evaluation']['recall_0.25'],"chosen":v['evaluation'].get('frozen_threshold'),"jun_cal":v['selected']} for k,v in scores.items()},"seconds":audit['time_sec']},indent=2),flush=True)
 return audit

if __name__=='__main__':execute(sys.argv[1])
