"""MICRO180-RB1: positive-R9-teacher-entry-only reconstruction.

Training consumes only original positive-leg R9 target seconds / side / family.
Inference consumes only a frozen positive prototype policy and real Coinexx
causal prefix features, NEVER target times/labels, synthetic R9 fills or exits.
Entry-intent policy is shadow-only; there is no holding or exiting.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import sys
import zipfile
import gzip
import numpy as np
from sklearn.cluster import KMeans

BASE = Path(__file__).resolve().parents[1]
ENGINE = BASE / 'src' / 'causal_quote_engine'
SRC = Path('/mnt/data')
TARGET_ZIP = SRC / 'R9_POSITIVE_TARGET_ATLAS_2026-01.zip'
FAMILY_PREFIXES = ('A1__','B1__','B2__','C2__','D1__','N1__','N2__')
# 30 genuinely as-of market dimensions, excluding any source R9 state fields.
FEATURE_KEYS = (
 'ret5','ret15','ret60','ret180','ret300','eff10','eff60','eff180',
 'vwap1','vwap3','vwap5','ema3_dist','ema3_8','ema8_21',
 'lastbar_close','channel3','channel5','basket5','basket15','minute_disp',
 'break15','break30','disp15','disp30','s1_eff','s1_travel',
 'rv60','rv_ratio','quote_intensity','contraction','spread','spread_shock',
 'atr_ratio','di_spread14','adx14','band15','band30','phase_sin','phase_cos','hour_sin','hour_cos',
)
SIGNED = {'ret5','ret15','ret60','ret180','ret300','eff10','eff60','eff180',
'vwap1','vwap3','vwap5','ema3_dist','ema3_8','ema8_21','lastbar_close',
'basket5','basket15','minute_disp','disp15','disp30','s1_eff','di_spread14','band15','band30'}


def sha256_file(path:Path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()


def load_targets(path:Path=TARGET_ZIP):
 out=[]
 with zipfile.ZipFile(path) as z:
  name=next(n for n in z.namelist() if 'WINNING_LEG_TARGETS' in n)
  with z.open(name) as fh, gzip.GzipFile(fileobj=fh) as fh2:
   for r in csv.DictReader(io.TextIOWrapper(fh2,encoding='utf8')):
    sec_exact=int(r['equote_ms'])-int(r['elag_ms'])-1000
    assert sec_exact%1000==0,(r['target_uid'],sec_exact)
    # This is the true original SYNTH whole-second CLOCK, not +1s mapped quote.
    teacher_sec=sec_exact//1000
    asserted=dt.datetime.strptime(r['entry_time_broker'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
    assert teacher_sec==int(asserted.timestamp()),(r['target_uid'],teacher_sec,asserted)
    family=r['atomic_family']; assert family.startswith(FAMILY_PREFIXES),family
    side=1 if r['side'].lower()=='buy' else -1
    out.append(dict(uid=r['target_uid'],sec=teacher_sec,side=side,leg=int(r['leg']),family=family,
      original_cents=int(r['original_positive_net_cents']),day=r['broker_entry_day'],
      source_row=int(r['original_r9_source_row']),mapped_ms=int(r['equote_ms']),
      mapped_price_u=int(r['q_entry_u']),minute=teacher_sec//60))
 return out


def features(raw:dict,side:int):
 """From quote engine only. No target content can enter this function."""
 def val(k):return float(raw[k])
 mid=(val('bid')+val('ask'))/2
 atr=max(.1,val('atr_used'))
 phase=val('phase');hour=val('hour')
 x={k:val(k) for k in (
  'ret5','ret15','ret60','ret180','ret300','eff10','eff60','eff180',
  'vwap1','vwap3','vwap5','ema3_dist','ema3_8','ema8_21','lastbar_close',
  'basket5','basket15','minute_disp','disp15','disp30','s1_eff','s1_travel',
  'rv60','rv_ratio','quote_intensity','contraction','spread','spread_shock',
  'atr_ratio','di_spread14','adx14','band15','band30')}
 x['channel3']=val('channel3_hi') if side>0 else -val('channel3_lo')
 x['channel5']=val('channel5_hi') if side>0 else -val('channel5_lo')
 x['break15']=val('buy_break15') if side>0 else val('sell_break15')
 x['break30']=val('buy_break30') if side>0 else val('sell_break30')
 x['phase_sin']=math.sin(2*math.pi*phase/60)
 x['phase_cos']=math.cos(2*math.pi*phase/60)
 x['hour_sin']=math.sin(2*math.pi*hour/24)
 x['hour_cos']=math.cos(2*math.pi*hour/24)
 for k in SIGNED:x[k]*=side
 x['spread']/=atr
 return np.array([x[k] for k in FEATURE_KEYS],dtype=np.float64)


def role(family:str)->str:
 return family.partition('__')[0]


def regime(row:dict,side:int):
 r15=side*float(row['ret15']);r60=side*float(row['ret60']);r300=side*float(row['ret300'])
 b=float(row['buy_break15'] if side>0 else row['sell_break15'])
 ef=side*float(row['eff60']);cont=float(row['contraction'])
 if b>.01 or (b>-.08 and cont>1.25):return 'breakout'
 if r60*r300<0 and abs(r60)>.10 and abs(r300)>.10:return 'reversal'
 if r15*r60>0 and r60*r300>0 and abs(ef)>.3:return 'nested_trend'
 if abs(ef)>.16 and abs(r300)>.20:return 'trend'
 if abs(ef)<.13 and abs(r300)<.15 and cont<.68:return 'consolidation'
 return 'transition'


def causal_rows(files:list[Path],only_seconds=None):
 for f in files:
  assert f.exists(),f
 timelist=None
 if only_seconds is not None:
  timelist=tempfile.NamedTemporaryFile(mode='w',prefix='micro180_target_seconds_',suffix='.txt',delete=False)
  timelist.write('\n'.join(str(t) for t in sorted(only_seconds))+'\n');timelist.close()
 cmd=[str(ENGINE)]+(['--only-seconds',timelist.name] if timelist is not None else [])+[str(x) for x in files]
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1024*1024)
 try:
  for row in csv.DictReader(p.stdout):yield row
 finally:
  if p.stdout:p.stdout.close()
  msg=p.stderr.read() if p.stderr else ''
  status=p.wait()
  if status!=0:raise RuntimeError(f'C++ source extraction failed {status}: {msg[-1300:]}')
  if timelist is not None:Path(timelist.name).unlink(missing_ok=True)
  print(msg.strip(),file=sys.stderr)


def input_files(days):
 out=[]
 for day in days:
  p=SRC/f'R9_REAL_{day}_ticks.csv.gz'
  if not p.exists():raise FileNotFoundError(p)
  out.append(p)
 return out


def snap_training(targets,train_days):
 bysec=collections.defaultdict(list)
 for t in targets:
  if t['day'] in train_days:bysec[t['sec']].append(t)
 counts=collections.Counter();obs=[];found=set()
 for row in causal_rows(input_files(train_days),only_seconds=set(bysec)):
  sec=int(row['second'])
  if sec not in bysec:continue
  for t in bysec[sec]:
   obs.append((t,features(row,t['side']),regime(row,t['side'])))
   counts[t['family']]+=1;found.add(t['uid'])
 return obs,found,counts


def train_positive_model(obs,train_days,source_hashes,source_zip_hash):
 if not obs:raise ValueError('No target-aligned causal snapshots')
 X=np.stack([r[1] for r in obs]);median=np.median(X,axis=0)
 scale=np.maximum(.05,np.percentile(X,75,axis=0)-np.percentile(X,25,axis=0))
 Z=np.clip((X-median)/scale,-7.,7.)
 models=[]
 group=collections.defaultdict(list)
 for i,(t,_,state) in enumerate(obs):group[(t['family'],t['side'])].append(i)
 for (family,side),idxs in sorted(group.items()):
  xx=Z[idxs];n=len(xx)
  if n<3:continue
  clusters=min(4,max(1,n//90))
  km=KMeans(n_clusters=clusters,n_init=3,random_state=47).fit(xx)
  nearest=np.min(np.mean((xx[:,None,:]-km.cluster_centers_[None,:,:])**2,axis=2),axis=1)
  threshold=float(np.quantile(nearest,.90))+1e-7
  phase=np.zeros(60,dtype=np.float64);hours=np.zeros(24,dtype=np.float64)
  states=collections.Counter()
  for i in idxs:
   t,_,state=obs[i];phase[t['sec']%60]+=1;hours[(t['sec']//3600)%24]+=1;states[state]+=1
  # Laplace-smoothed CLOCK intensity; no future-month data.
  ph=(phase+1)/(n+60);hr=(hours+1)/(n+24)
  models.append({'family':family,'role':role(family),'side':side,'training_count':n,
   'centers':km.cluster_centers_.round(7).tolist(),
   'threshold':threshold,'phase':ph.round(8).tolist(),'hour':hr.round(8).tolist(),
   'regimes':dict(states)})
 return {'version':'micro180-rb1-positive-coinexx','method':'positive-teacher-only causal prototype hazard',
 'date_window':sorted(train_days),'source_zip_sha256':source_zip_hash,
 'source_real_daily_sha256':source_hashes,'input_features':list(FEATURE_KEYS),
 'median':median.round(8).tolist(),'scale':scale.round(8).tolist(),
 'models':models,'positive_aligned_training_examples':len(obs),
 'uses_R9_entry_timestamp_at_inference':False,'uses_R9_profit_at_inference':False,
 'uses_R9_exit_at_inference':False,'emits_orders':False}


def evaluate_intents(intents,targets,days):
 selected=[t for t in targets if t['day'] in days]
 # Validate against target clock ONLY AFTER inference, never inside policy.
 bucket=collections.defaultdict(list)
 for p in intents:bucket[(p['minute'],p['leg'],p['side'])].append(p)
 total=0;matched=0;same=0;matched_pnl_cents=0;byfamily=collections.defaultdict(lambda:dict(n=0,same=0,within2=0,cents=0))
 for t in selected:
  f=byfamily[t['family']];f['n']+=1;f['cents']+=t['original_cents'];total+=1
  opts=bucket.get((t['minute'],t['leg'],t['side']),[])
  # R9 historical comparisons are exact source teacher seconds.
  if opts:
   mind=min(abs(p['sec']-t['sec']) for p in opts)
   if mind==0:same+=1;f['same']+=1
   if mind<=2:matched+=1;matched_pnl_cents+=t['original_cents'];f['within2']+=1
 return dict(target_count=total,matched_exact_second=same,matched_2second=matched,
  exact_second_recall=round(same/max(1,total),6),two_second_recall=round(matched/max(1,total),6),
  target_original_SYNTH_cents=sum(x['original_cents'] for x in selected),
  target_original_SYNTH_cents_in_2second_matches=matched_pnl_cents,
  per_atomic_family=dict(sorted(byfamily.items())))


def replay(model, days):
 profiles={}
 specialists=model.get('specialists',[model])
 for expert in specialists:
  if expert['input_features']!=list(FEATURE_KEYS):raise ValueError('incompatible causal feature schema')
  med=np.asarray(expert['median']);scale=np.asarray(expert['scale'])
  for p in expert['models']:
   profiles.setdefault((p['side'],p['role']),[]).append((p,med,scale))
 fast_ix=[i for i,k in enumerate(FEATURE_KEYS) if k in {'ret5','ret15','eff10','basket5','basket15','break15','break30','minute_disp','spread_shock','quote_intensity'}]
 # Literal data does not contain target times, labels, exits or R9 event flags.
 out=[];current_minute=None;first=None;second=False;rows=0;eligible_rows=0
 for row in causal_rows(input_files(days)):
  rows+=1;sec=int(row['second']);minute=int(row['minute']);phase=sec%60;hour=(sec//3600)%24
  if current_minute!=minute:current_minute=minute;first=None;second=False
  if first is not None and second:continue
  best=None
  for side in (1,-1):
   rawx=features(row,side)
   # Model selector gets *only* causal quote features and already-issued intent.
   for role_name in ('A1','B1','D1','N1','B2','C2','N2'):
    leg=1 if role_name in ('A1','B1','D1','N1') else 2
    if leg==1 and first is not None:continue
    if leg==2:
     if first is None:
      # C2 recovery is historically preceded by a losing first leg that
      # is intentionally absent from the +379k winner-only supervision.
      # Its entry may be emitted as an unlinked shadow SECOND intent;
      # external position-flat verification is compulsory.
      if role_name!='C2' or phase<18:continue
     elif second or side==first['side'] or phase<first['phase']+7:continue
    for p,med,scale in profiles.get((side,role_name),[]):
     x=np.clip((rawx-med)/scale,-7,7)
     centers=np.asarray(p['centers'])
     # Multiple independent 5/15 baskets and historical 15/30 breakouts
     # are features, not hard vetoes.
     nearest=np.min(np.mean((centers-x)**2,axis=1))
     # Learned positive-only distance + time-of-minute hazard priors.
     scaled=nearest/max(0.08,p['threshold'])
     clock=math.log(max(1e-7,p['phase'][phase]*60))
     hours=math.log(max(1e-7,p['hour'][hour]*24))
     score=1.0-scaled+.24*clock+.07*hours
     # Consistent predeclared event threshold; not tuned to evaluation labels.
     if score<-.05:continue
     if best is None or score>best['score']:
      best=dict(sec=sec,ms=int(row['time_msc']),minute=minute,leg=leg,side=side,
        role=role_name,pattern_hypothesis=p['family'],score=round(score,5),
        price_u=int(round(float(row['ask' if side>0 else 'bid'])*100)),
        phase=phase,regime=regime(row,side),
        conditional_on_flat=leg==2,
        first_leg_observed=first is not None)
  if best is None:continue
  eligible_rows+=1
  if best['leg']==1 and first is None:first=best
  elif best['leg']==2 and not second:second=True
  else:continue
  out.append(best)
 return out,dict(scored_seconds=rows,qualifying_seconds=eligible_rows,independent_shadow_intents=len(out),
    first_intents=sum(p['leg']==1 for p in out),second_intents=sum(p['leg']==2 for p in out))


def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--month',default='2026-01',help='source target month YYYY-MM')
 ap.add_argument('--train-days',type=int,default=5,help='earliest N trading days of month, training only')
 ap.add_argument('--eval-days',type=int,default=2,help='next K January trading days; 0 freezes a complete month without same-month replay')
 ap.add_argument('--outdir',type=Path,default=BASE/'results')
 a=ap.parse_args()
 a.outdir.mkdir(parents=True,exist_ok=True)
 month_target=SRC/f'R9_POSITIVE_TARGET_ATLAS_{a.month}.zip'
 t=load_targets(month_target)
 days=sorted(set(x['day'] for x in t))
 assert a.train_days>0 and a.eval_days>=0 and a.train_days+a.eval_days<=len(days)
 tr=days[:a.train_days];te=days[a.train_days:a.train_days+a.eval_days]
 h={p.name:sha256_file(p) for p in input_files(tr+te)}
 obs,found,counts=snap_training(t,tr)
 m=train_positive_model(obs,tr,h,sha256_file(month_target))
 model_path=a.outdir/f'micro180_rb1_{a.month}_positive_model.json'
 model_path.write_text(json.dumps(m,separators=(',',':'),sort_keys=True))
 intents,trace=replay(m,te) if te else ([],dict(scored_seconds=0,qualifying_seconds=0,independent_shadow_intents=0,first_intents=0,second_intents=0))
 match=evaluate_intents(intents,t,te)
 out={'project':'MICRO180 NEW BUILD','stage':a.month+' positive R9 teacher-entry reconstruction',
   'train_days':tr,'evaluation_days':te,'model_sha256':sha256_file(model_path),
   'training_targets':sum(x['day'] in tr for x in t),'training_target_snapshots':len(obs),
   'training_snapshot_recall':round(len(found)/max(1,sum(x['day'] in tr for x in t)),6),
   'trained_atomic_side_models':len(m['models']),
   'causal_features':len(FEATURE_KEYS),'per_family_positive_examples':dict(sorted(counts.items())),
   'replay':trace,'entry_concordance':match,
   'grading':'R9 SYNTH original entry time/side/leg only; no hold or exit',
   'not_a_Coinexx_profit_backtest':True,
   'frozen_model_data_ends_before_evaluation':True,
   'model_file':model_path.name}
 receipt=a.outdir/f'micro180_rb1_{a.month}_entry_concordance.json'
 receipt.write_text(json.dumps(out,indent=2,sort_keys=True))
 # Sparse derived candidate-only ledger; original ticks untouched.
 with gzip.open(a.outdir/f'micro180_rb1_{a.month}_shadow_intents.csv.gz','wt',newline='') as fh:
  writer=csv.DictWriter(fh,fieldnames=list(intents[0]) if intents else ['sec']);writer.writeheader();writer.writerows(intents)
 print(json.dumps({k:v for k,v in out.items() if k not in ('per_family_positive_examples','entry_concordance')},indent=2))
 print('CONCORDANCE:',json.dumps({k:v for k,v in match.items() if k!='per_atomic_family'}))

if __name__=='__main__':main()
