"""H1V2 R7: exhaustive, as-of raw-quote nested-horizon regime from first-observed 250ms quote.

FUTURE-PRIVILEGED HINDSIGHT STUDY. Future outcomes may be used only as targets.
Do not change the original R9 engine. Do not confuse per-candidate scores with trade fills.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, pathlib, time
import numpy as np
from h1v2_teacher import read_ticks
from h1v2_freeze import PINNED

MONTHS=('01','02','06','07')
RAW=pathlib.Path('/mnt/data'); ORIGINAL=RAW/'h1v2/results'; OUT=RAW/'h1v2_r7/results'
WINDOWS=(1000,15000,300000,3600000)
# 3^4 x 5 spread groups x 4 quote rate groups x 4 UTC sessions x 3 15s efficiency groups
N_BINS=3**4*5*4*4*3
BIN_AXES=('1s / 15s / 5min / 1h standardized signed trend', 'spread', 'quote_arrival_rate_1s', 'UTC_session', '15s_path_efficiency')

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def asof_regime(t,b,a,ix,chunk=250000):
 """Every output at candidate row i depends only on event ordinals <=i, never same-ms later events.

 Return exhaustive categorical regime id for every eligible entry. Displacement/volatility
 normalized against past quadratic variation; fixed bins, no full-month statistics.
 """
 ix=np.asarray(ix,dtype=np.int64)
 if ix.ndim!=1 or (len(ix)>1 and np.any(np.diff(ix)<=0)) or len(ix) and (ix[0]<0 or ix[-1]>=len(t)):
  raise ValueError('invalid candidate ordinal chronology')
 if len(t)>1 and np.any(t[1:]<t[:-1]):raise ValueError('nonchronological raw ticks')
 mid=(b+a)*.5;v=np.diff(mid,prepend=mid[0]);v[0]=0.
 abs_prefix=np.cumsum(np.abs(v),dtype=np.float64)
 sq_prefix=np.cumsum(v*v,dtype=np.float64)
 regimes=np.empty(len(ix),np.int32)
 for st in range(0,len(ix),chunk):
  en=min(st+chunk,len(ix)); cur=ix[st:en]; now=t[cur]; n=len(cur)
  displacement={}; qvariation={}
  efficiency=None; rate=None
  for h in WINDOWS:
   # LAST QUOTE ON/BEFORE now-h. h>=1000, hence STRICTLY HISTORICAL.
   j=np.clip(np.searchsorted(t,now-h,side='right')-1,0,None)
   j=np.minimum(j,cur)
   displacement[h]=mid[cur]-mid[j]
   qvariation[h]=np.maximum(0.,sq_prefix[cur]-sq_prefix[j])
   if h==1000:rate=cur-np.searchsorted(t,now-h,side='left')+1
   if h==15000:
    movement=abs_prefix[cur]-abs_prefix[j]
    efficiency=np.abs(displacement[h])/(movement+1e-12)
  signs=[]
  for h in (1000,15000,300000,3600000):
   limit=np.maximum(.08,.5*np.sqrt(qvariation[h]))
   signs.append(np.where(displacement[h]>limit,2,np.where(displacement[h]<-limit,0,1)))
  trend=signs[0]+3*signs[1]+9*signs[2]+27*signs[3]
  spread=np.searchsorted([.45,.65,.85,1.10],a[cur]-b[cur],side='right')
  arrivals=np.searchsorted([2,5,12],rate,side='right')
  sess=((now//3600000)%24//6).astype(np.int32)
  eff=np.searchsorted([.25,.65],efficiency,side='right')
  r=((((trend*5+spread)*4+arrivals)*4+sess)*3+eff).astype(np.int32)
  assert np.all((r>=0)&(r<N_BINS))
  regimes[st:en]=r
 return regimes

def prepare(month,raw_root=RAW,original=ORIGINAL,out=OUT):
 start=time.monotonic();out.mkdir(parents=True,exist_ok=True)
 raw=pathlib.Path(raw_root)/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
 expected=PINNED[month]
 if sha(raw)!=expected:raise RuntimeError('source raw SHA mismatch')
 src=pathlib.Path(original)/f'h1v2_dukascopy_{month}_oracle_labels.npz'
 receipt=json.loads((pathlib.Path(original)/f'h1v2_dukascopy_{month}_receipt.json').read_text())
 if sha(src)!=receipt['teacher_labels_sha256']:raise RuntimeError('source teacher SHA mismatch')
 with np.load(src,allow_pickle=False) as z:
  ix=z['tick_index'].copy();ts=z['t'].copy();classes=z['code'].copy()
 t,b,a=read_ticks(raw)
 if not np.array_equal(t[ix],ts):raise RuntimeError('row ordinals are not quote timestamps')
 # Source exact R9 label original values code==1 = STRICT_GOOD, 0 neutral, -1 bad
 regime=asof_regime(t,b,a,ix)
 assert len(regime)==len(ix)==len(classes)
 n=np.bincount(regime,minlength=N_BINS)
 wins=np.stack([np.bincount(regime,weights=(classes[:,s]==1),minlength=N_BINS) for s in range(2)],axis=-1).astype(np.int64)
 neut=np.stack([np.bincount(regime,weights=(classes[:,s]==0),minlength=N_BINS) for s in range(2)],axis=-1).astype(np.int64)
 assert int(n.sum())==len(ix) and np.array_equal((wins+neut).sum(axis=0),np.array([(classes[:,s]>=0).sum() for s in range(2)]))
 saved=out/f'R7_FULL_REGIME_{month}.npz'
 np.savez_compressed(saved,regime=regime,ix=ix,ts=ts)
 stats=out/f'R7_FULL_STATS_{month}.npz'
 np.savez_compressed(stats,n=n,win=wins,neutral=neut)
 report={'month':month,'raw_quote_rows':len(t),'all_eligible_250ms_candidates':len(ix),
 'histogram_rows':int(n.sum()),'strict_buy':int(wins[:,0].sum()),'strict_sell':int(wins[:,1].sum()),
 'neutral_buy':int(neut[:,0].sum()),'neutral_sell':int(neut[:,1].sum()),
 'wrong_buy':int(n.sum()-wins[:,0].sum()-neut[:,0].sum()),
 'wrong_sell':int(n.sum()-wins[:,1].sum()-neut[:,1].sum()),
 'regime_count':N_BINS,'nonempty_regimes':int((n>0).sum()),
 'raw_sha256':expected,'h1v2_original_teacher_sha256':receipt['teacher_labels_sha256'],
 'regime_record_sha256':sha(saved),'statistics_sha256':sha(stats),
 'elapsed_seconds':round(time.monotonic()-start,2),
 'status':'ALL_FULL_MONTH_CANDIDATES_HINDSIGHT_LABELS_AS_TARGETS_NOT_AS_FEATURES'}
 (out/f'R7_FULL_MONTH_{month}_receipt.json').write_text(json.dumps(report,indent=2))
 return report

def wilson(success,total,z=1.959963984540054):
 """Vectorized Wilson lower; descriptive on training groups, not a valid iid CI on correlated ticks."""
 n=np.asarray(total,dtype=float);p=np.asarray(success,dtype=float)/np.maximum(n,1.)
 den=1+z*z/np.maximum(n,1.);low=(p+z*z/(2*np.maximum(n,1.))-z*np.sqrt((p*(1-p)+z*z/(4*np.maximum(n,1.)))/np.maximum(n,1.)))/den
 return np.where(n>0,low,0.)

def posterior(w,n,prior_w,prior_n,kappa=64):
 # Empirical Beta prior shrunk toward pooled base rate; genuine target-derived training only
 base=(prior_w+1)/(prior_n+2)
 return (w+kappa*base)/(n+kappa)

def score_cells(train,holdout):
 months=tuple(train)
 nts={};wts={};neuts={}
 for m in MONTHS:
  with np.load(OUT/f'R7_FULL_STATS_{m}.npz') as z:
   nts[m]=z['n'].copy();wts[m]=z['win'].copy();neuts[m]=z['neutral'].copy()
 ntr=sum(nts[m] for m in months)
 wtr=sum((wts[m] for m in months))
 base=wtr.sum(axis=0)/ntr.sum()
 # Side specific posterior, retain NO_GOOD and neutral as explicit rejection quantities.
 scores=np.column_stack([posterior(wtr[:,i],ntr,wtr[:,i].sum(),ntr.sum()) for i in range(2)])
 return scores,ntr,wtr,nts,wts,neuts,base

def examine(hyp,train,valid,cutoffs=(.50,.60,.70,.80,.90),min_regime_counts=(30,100,300)):
 scores,ntr,wtr,ns,ws,neus,base=score_cells(train,valid)
 out={'name':hyp,'train':list(train),'validation':list(valid),'opportunity_base_per_side':base.tolist(),
      'hypothesis':'multivariate past-only signed nested 1s / 15s / 5min / 1h trends, spread, quote burst, UTC sessions, 15s path efficiency',
      'observations_by_month':{m:int(ns[m].sum()) for m in MONTHS},'grid':{}}
 # Per-side selection; ambiguity WAIT, opposite risk requires learned side scores.
 for minimum in min_regime_counts:
  for cut in cutoffs:
   eligible=(scores>=cut)&(ntr[:,None]>=minimum)
   side=np.argmax(scores,axis=1)
   qualified=eligible[np.arange(len(side)),side]
   chosen=np.where(qualified,side,-1)
   key=f'prob>={cut:.2f}_min_training_per_cell_{minimum}'
   months={}
   for m in MONTHS:
    selected=(chosen>=0)
    n=ns[m];wins=ws[m];neu=neus[m]
    # as-of candidate counts, not distinct actual trades!
    count=int(n[selected].sum())
    correct=int(wins[np.arange(len(n))[selected],side[selected]].sum())
    neutral=int(neu[np.arange(len(n))[selected],side[selected]].sum())
    wrong=count-correct-neutral
    months[m]={'eligible_candidates':count,'strict_good':correct,'neutral':neutral,'wrong':wrong,
          'strict_precision':correct/count if count else None,
          'wilson_naive_lower':float(wilson(correct,count)) if count else None,
          'status':'IN_SAMPLE_RESUBSTITUTION' if m in train else 'OUTSIDE_TRAIN_MONTH'}
   out['grid'][key]={'admissible_regimes':int(selected.sum()),'months':months}
 return out

def train_audit(out=OUT):
 out.mkdir(parents=True,exist_ok=True)
 # Full self-fitting diagnostic on all 4 AND month-level leave-one-out; no score trained on holdout labels
 runs=[examine('ALL_4_RESUBSTITUTION',MONTHS,MONTHS)]
 for m in MONTHS:
  runs.append(examine('LEAVE_'+m+'_UNSEEN',tuple(x for x in MONTHS if x!=m),(m,)))
 # Strict 80% check on ALL months each run; admit nothing when statistical/precision fails
 summary={'scope':'FULL 15,401,392 first observed 250ms events, all original raw quote months',
    'bin_axes':list(BIN_AXES),'bins':N_BINS,'runs':runs,
    'causal_note':'Each regime computed from past Bid/Ask quotes, never future, equal-ms later ordinals excluded',
    'statistical_note':'Wilsons on overlapping 250ms candidates are NAIVE and NOT independent confidence intervals',
    'evaluation_note':'Scores trained on all four are deliberately contaminated. LOMO flags month heldout. Scored values use historic future labels only for validation, not model inputs; still no policy on-policy trade stream.',
    'recovery_note':'Raw original source and giant original H1V2 NPZ arrays retained immutably; stored R7 regime record + per month stats + hashes.'}
 path=out/'R7_ALL_FOUR_EXHAUSTIVE_NESTED_REGIME_AUDIT.json'
 path.write_text(json.dumps(summary,indent=2))
 return summary

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--month',choices=MONTHS);ap.add_argument('--audit',action='store_true');args=ap.parse_args()
 if args.month:print(json.dumps(prepare(args.month),indent=2),flush=True)
 if args.audit:
  s=train_audit()
  for run in s['runs']:
   print(run['name'], flush=True)
   for key in ('prob>=0.50_min_training_per_cell_30','prob>=0.60_min_training_per_cell_30','prob>=0.80_min_training_per_cell_30'):
    z=run['grid'][key];print(key,'cells',z['admissible_regimes'],{m:(p['eligible_candidates'],p['strict_precision']) for m,p in z['months'].items()},flush=True)
