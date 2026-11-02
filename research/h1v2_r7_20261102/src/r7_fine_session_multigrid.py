"""H1V2 R7B higher-capacity 24 UTC-hour nested state regime, ALL four full-month events.

Hindsight labels used for training bins; reconstructs 24-hour finer grid from
previous source-exact R7 coarse regime and quote timestamp WITHOUT future tick.
LOMO external comparison; all-four resubstitution is self-contaminated.
"""
from __future__ import annotations
import json, pathlib,numpy as np
from full_population_nested_regime import MONTHS,OUT,ORIGINAL,sha,posterior,N_BINS
from r7_ranked_tick_replay import replay_month

N_FINE=N_BINS//4*24
FRACTIONS=(.0001,.001,.01)

def fine_from_coarse(r,ts):
 r=np.asarray(r,np.int32);ts=np.asarray(ts,np.int64)
 if r.shape!=ts.shape:raise ValueError('axis mismatch')
 hour=((ts//3600000)%24).astype(np.int32)
 assert np.array_equal((r//3)%4,hour//6),'source 6hour classification mismatched'
 # discard original 4-session part and replace it with the observed UTC hour.
 fine=(r//(3*4)*24+hour)*3+(r%3)
 assert np.all((fine>=0)&(fine<N_FINE))
 return fine

def prepare(mon):
 with np.load(OUT/f'R7_FULL_REGIME_{mon}.npz') as d:
  r=fine_from_coarse(d['regime'],d['ts']);ix=d['ix']
 with np.load(ORIGINAL/f'h1v2_dukascopy_{mon}_oracle_labels.npz') as z:
  if not np.array_equal(ix,z['tick_index']):raise ValueError('source ordinal mismatch')
  y=z['code'].copy()
 n=np.bincount(r,minlength=N_FINE)
 win=np.stack([np.bincount(r,weights=(y[:,s]==1),minlength=N_FINE) for s in range(2)],axis=1).astype(np.int64)
 neutral=np.stack([np.bincount(r,weights=(y[:,s]==0),minlength=N_FINE) for s in range(2)],axis=1).astype(np.int64)
 assert n.sum()==len(r)
 out=OUT/f'R7_FINE_UTC24_{mon}.npz';np.savez_compressed(out,regime=r,ix=ix)
 stats=OUT/f'R7_FINE_UTC24_{mon}_STATS.npz';np.savez_compressed(stats,n=n,win=win,neutral=neutral)
 receipt={'month':mon,'full_eligible_candidates':len(r),'bin_count':N_FINE,'nonempty':int((n>0).sum()),'strict_good_buy':int(win[:,0].sum()),'strict_good_sell':int(win[:,1].sum()),'verified_full_ordinal_match':True,'fine_regime_sha256':sha(out),'fine_stats_sha256':sha(stats)}
 (OUT/f'R7_FINE_UTC24_{mon}_receipt.json').write_text(json.dumps(receipt,indent=2))
 return receipt

def train(train,frac,min_n=10,kappa=8):
 ns=[];wins=[]
 for m in train:
  with np.load(OUT/f'R7_FINE_UTC24_{m}_STATS.npz') as d:
   ns.append(d['n'].copy());wins.append(d['win'].copy())
 n=np.sum(ns,axis=0);w=np.sum(wins,axis=0)
 scores=np.column_stack([posterior(w[:,s],n,w[:,s].sum(),n.sum(),kappa=kappa) for s in range(2)])
 side=np.argmax(scores,axis=1);probs=scores[np.arange(len(side)),side]
 valid=n>=min_n
 order=np.argsort(-probs,kind='stable');order=order[valid[order]]
 if len(order)==0:return np.zeros(N_FINE,bool),side,0.,0
 cum=np.cumsum(n[order]);k=min(len(order)-1,int(np.searchsorted(cum,int(n.sum()*frac))))
 elig=np.zeros(N_FINE,bool);elig[order[:k+1]]=True
 return elig,side,float(probs[order[k]]),int(n[elig].sum())

def audit():
 out={'status':'INTENTIONAL_HINDSIGHT_FIT_FULL_15_4M_CANDIDATE_MULTIGRID','grid_bins':N_FINE,
 'four_month_self_fit':'HIGHLY LEAKED IN SAMPLE','definitions':'same R7 nested trend-quote rate-spread-efficiency, finer UTC hour instead of 6h session',
 'experiments':[]}
 configs=[('ALL4_IN_SAMPLE',MONTHS,MONTHS)]+[(f'LOMO_{m}',tuple(x for x in MONTHS if x!=m),(m,)) for m in MONTHS]
 for name,fit,evals in configs:
  for mn in (10,30):
   for frac in FRACTIONS:
    mask,side,cut,trained_count=train(fit,frac,mn)
    cell={'experiment':name,'train':list(fit),'evaluation':list(evals),'min_cell':mn,'training_target_fraction':frac,'eligible_cells':int(mask.sum()),'train_events_total':trained_count,'lowest_selected_posterior':cut,'months':{}}
    for m in evals:
     cell['months'][m]=replay_month(m,mask,side,regime_path=OUT/f'R7_FINE_UTC24_{m}.npz')
    out['experiments'].append(cell)
    print('FINE',name,'n>=',mn,'frac',frac,'cells',cell['eligible_cells'],[(m,v['replayed_trades'],round(v['precision'] or 0,4)) for m,v in cell['months'].items()],flush=True)
 (OUT/'R7_FINE_UTC24_EXHAUSTIVE_TRAIN_AUDIT.json').write_text(json.dumps(out,indent=2))
 return out

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--month',choices=MONTHS);p.add_argument('--audit',action='store_true');args=p.parse_args()
 if args.month:print(json.dumps(prepare(args.month),indent=2),flush=True)
 if args.audit:audit()
