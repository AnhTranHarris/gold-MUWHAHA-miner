"""R10 exact-population deliberately hindsight-overfit quote grammar cohorts.

Training AND evaluation on same 100% monthly 250ms candidates = privileged
in-sample oracle-derived cohort table, NOT a causal pretrained signal or OOS.
Fitted cohorts can use future labels; their input feature codes are past-only.
Never use this table to claim foresight or deployable performance.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,pathlib,sys
import numpy as np
from numba import njit
ROOT=pathlib.Path(os.getenv('H1V2_R10_ROOT','/mnt/data'))
H1=ROOT/'h1v2/results';R7=ROOT/'h1v2_r7/results';R8=ROOT/'h1v2_r8/results'
R10=ROOT/'h1v2_r10/results'
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
GRID=('slow_legacy_nested','micro_swing','quote_liquidity','trend_within_trend','full_motif')
MIN_N=(16,64,256)
THRESHOLDS=(.20,.30,.50,.70,.80)

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def group_keys(mon,kind):
 G=np.load(R10/f'R10_GRAMMAR_{mon}.npy',mmap_mode='r')
 R=np.load(R8/f'R8_ASOF_{mon}.npy',mmap_mode='r')
 with np.load(R7/f'R7_FULL_REGIME_{mon}.npz') as z:rg=z['regime'].copy()
 n=len(G)
 if n!=len(R) or n!=len(rg):raise ValueError('mismatched original 250ms event population')
 trend=(rg//240).astype(np.int32)
 t1=trend%3;t15=(trend//3)%3;t5=(trend//9)%3;t60=(trend//27)%3
 sess=(rg//3)%4;rate=(rg//12)%4;sp=(rg//48)%5
 def tri(x):return (np.asarray(x)>0.1).astype(np.int32)+ (np.asarray(x)>-0.1).astype(np.int32)
 def eff(x):return np.searchsorted(np.array([-.65,-.15,.15,.65]),np.asarray(x),side='right').astype(np.int32)
 def spread(x):return np.searchsorted(np.array([.5,.75,1.0,1.5]),np.asarray(x),side='right').astype(np.int32)
 def sign(x):return (np.asarray(x)>0.015).astype(np.int32)+(np.asarray(x)>=-0.015).astype(np.int32)
 # Compact, strictly chronological multiscale grammar fingerprints.
 if kind=='slow_legacy_nested': digits=[t1,t15,t5,t60,rate,sp,sess];bases=[3,3,3,3,4,5,4]
 elif kind=='micro_swing': digits=[eff(G[:,0]),eff(G[:,16]),eff(G[:,32]),G[:,2].astype(np.int32)+1,G[:,18].astype(np.int32)+1,sign(G[:,1]),sp];bases=[5,5,5,3,3,3,5]
 elif kind=='quote_liquidity': digits=[spread(R[:,0]),np.minimum((G[:,7]*6).astype(np.int32),5),np.minimum((G[:,8]*6).astype(np.int32),5),np.minimum((G[:,23]*6).astype(np.int32),5),np.minimum((G[:,22]*6).astype(np.int32),5),np.minimum((G[:,27]*6).astype(np.int32),5),rate,sess];bases=[5,6,6,6,6,6,4,4]
 elif kind=='trend_within_trend':digits=[eff(G[:,0]),eff(G[:,16]),eff(G[:,32]),t1,t15,t5,t60,rate,sess];bases=[5,5,5,3,3,3,3,4,4]
 elif kind=='full_motif':digits=[eff(G[:,0]),eff(G[:,16]),eff(G[:,32]),G[:,18].astype(np.int32)+1,sign(G[:,33]),t1,t15,t5,t60,sp,rate,sess];bases=[5,5,5,3,3,3,3,3,3,5,4,4]
 else:raise ValueError('unknown grid')
 k=np.zeros(n,dtype=np.int64);prod=1
 for d,base in zip(digits,bases):
  d=np.asarray(d,dtype=np.int32)
  if ((d<0)|(d>=base)).any():raise AssertionError((kind,base,d.min(),d.max()))
  k+=prod*d;prod*=base
 return k,prod

@njit(cache=True)
def replay(rows,side,idx,ends,net,c):
 qty=good=bad=neutral=0;profit=0.;last=-1
 for z in range(len(rows)):
  r=rows[z];di=side[r];ent=idx[r];end=ends[r,di]
  if ent<=last or end<=ent or not np.isfinite(net[r,di]):continue
  last=end;qty+=1;profit+=net[r,di]
  if c[r,di]==1:good+=1
  elif c[r,di]==0:neutral+=1
  else:bad+=1
 return qty,good,bad,neutral,profit

def wilson_lower(g,n,z=1.96):
 n=np.asarray(n,dtype=np.float64);g=np.asarray(g,dtype=np.float64)
 den=np.maximum(n,1.);phat=g/den
 return np.maximum(0,(phat+z*z/(2*den)-z*np.sqrt(phat*(1-phat)/den+z*z/(4*den*den)))/(1+z*z/den))

def audit(mon,grid):
 p=H1/f'h1v2_dukascopy_{mon}_oracle_labels.npz'
 ori=json.loads((H1/f'h1v2_dukascopy_{mon}_receipt.json').read_text())
 if sha(p)!=ori['teacher_labels_sha256']:raise ValueError('original H1V2 oracle mutated')
 r8=json.loads((R8/f'R8_ASOF_{mon}_receipt.json').read_text())
 g10=json.loads((R10/f'R10_GRAMMAR_{mon}_receipt.json').read_text())
 if sha(R8/f'R8_ASOF_{mon}.npy')!=r8['features_sha256']:raise ValueError('R8 schema mutated')
 if sha(R10/f'R10_GRAMMAR_{mon}.npy')!=g10['path_sha256']:raise ValueError('R10 grammar mutated')
 key,space=group_keys(mon,grid)
 # Number of possible groups is bounded. Sorted inverse and bincount cover 100%.
 uid,inv=np.unique(key,return_inverse=True)
 with np.load(p,allow_pickle=False) as a:
  c=a['code'].copy();net=a['net'].copy();idx=a['tick_index'].copy();ends=a['exit_tick_index'].copy()
 if len(key)!=len(c):raise ValueError('source event count mismatch')
 sup=np.bincount(inv,minlength=len(uid)).astype(np.int32)
 l=[];pmean=[]
 for d in range(2):
  good=np.bincount(inv,weights=(c[:,d]==1),minlength=len(uid))
  pnl=np.bincount(inv,weights=net[:,d],minlength=len(uid))
  l.append(wilson_lower(good,sup));pmean.append(pnl/np.maximum(1,sup))
 score=np.stack(l,axis=1);mu=np.stack(pmean,axis=1)
 chosen=np.argmax(score,axis=1).astype(np.int8)
 best=score[np.arange(len(uid)),chosen]
 other=score[np.arange(len(uid)),1-chosen]
 expectancy=mu[np.arange(len(uid)),chosen]
 result={'month':mon,'grid':grid,'full_month_candidate_count':len(key),'group_space':space,'observed_groups':len(uid),'groups_support_ge16':int((sup>=16).sum()),'groups_support_ge64':int((sup>=64).sum()),'max_side_wilson_n16':float(best[sup>=16].max()) if (sup>=16).any() else None,'positive_mean_net_groups_n16':int(((expectancy>0)&(sup>=16)).sum()),'status':'IN_SAMPLE_FUTURE_ORACLE_TRAINING_LABELS_NO_FORESIGHT','experiments':{}}
 for economic_required in (False,True):
  for nmin in MIN_N:
   for threshold in THRESHOLDS:
    # Group trained using this very month's future outcomes. Explicit in-sample.
    qualified=(sup>=nmin)&(best>=threshold)&((best-other)>=.05)&((expectancy>0.) if economic_required else np.ones(len(sup),dtype=bool))
    mask=qualified[inv];rows=np.flatnonzero(mask)
    sides=chosen[inv]
    q,ok,bad,neu,value=replay(rows,sides,idx,ends,net,c)
    result['experiments'][f'net{int(economic_required)}_n{nmin}_wilson{threshold:.2f}']={
     'qualified_groups':int(qualified.sum()),'candidate_signals':int(len(rows)),
    'candidate_strict_precision':float(np.mean(c[rows,sides[rows]]==1)) if len(rows) else None,
    'one_position_trade_count':int(q),'replay_correct':int(ok),'replay_wrong':int(bad),'replay_neutral':int(neu),
    'replay_strict_precision':float(ok/q) if q else None,'replay_modeled_net':round(value,2),
    'monthly_80pct_synth_floor':math.ceil(.8*SYNTH[mon]),
    'joint_eighty_pct':bool(q>=math.ceil(.8*SYNTH[mon]) and ok/q>=.8) if q else False}
 result['feature_source']={'h1v2_label_source_sha256':ori['teacher_labels_sha256'],'r8_asof_source_sha256':r8['features_sha256'],'r10_order_path_source_sha256':g10['path_sha256']}
 out=R10/f'R10_COHORT_{mon}_{grid}.json';out.write_text(json.dumps(result,indent=2))
 return {'month':mon,'grid':grid,'groups':len(uid),'n16w30':result['experiments']['net0_n16_wilson0.30']}

if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('--month',required=True,choices=['01','02','06','07']);pa.add_argument('--grid',required=True,choices=GRID);arg=pa.parse_args();print(json.dumps(audit(arg.month,arg.grid)),flush=True)
