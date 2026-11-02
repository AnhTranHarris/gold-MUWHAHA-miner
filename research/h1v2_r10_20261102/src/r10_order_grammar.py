"""H1V2 R10 source-exact past-ordinal quote grammar.

ALWAYS as-of. Each candidate feature only observes raw event indices <= candidate.
No 250ms slot closing knowledge, no future trade labels, no OHLC proxy.
Prior H1V2 and R7-R9 code is external immutable dependency.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, os
import numpy as np
from numba import njit
from h1v2_teacher import read_ticks
from h1v2_freeze import PINNED

ROOT = Path(os.environ.get('H1V2_R10_ROOT','/mnt/data'))
OUT = ROOT/'h1v2_r10/results'
WINDOW_QUOTES=(4,16,48)
FIELDS=('signed_efficiency','signed_delta','extrema_order','extrema_last_age',
        'up_ticks_frac','down_ticks_frac','direction_flip_frac',
        'bid_only_frac','ask_only_frac','joint_frac',
        'spread_widen_frac','mark_turn_frac','last_run_signed',
        'signed_impulse_last3','elapsed_ms','max_single_step')
NAMES=tuple(f'k{k}_{field}' for k in WINDOW_QUOTES for field in FIELDS)

@njit(cache=True)
def _compute(t,b,a,ix):
 n=len(ix);out=np.zeros((n,3*16),dtype=np.float32)
 for row in range(n):
  i=ix[row]
  for kk in range(3):
   K=(4,16,48)[kk];start=max(0,i-K);steps=i-start
   if steps<=0:continue
   s=(b[start]+a[start])*.5;last=s;mx=s;mn=s;mxidx=start;mnidx=start
   abswalk=0.; up=0;down=0;flips=0;bidonly=0;askonly=0;joint=0;widen=0;turns=0
   prevsign=0;prevmark=0;run=0;last_run=0;maxsingle=0.
   for j in range(start+1,i+1):
    m=(b[j]+a[j])*.5;d=m-last;last=m
    sign=1 if d>1e-10 else (-1 if d< -1e-10 else 0)
    if sign>0:up+=1
    if sign<0:down+=1
    if sign!=0:
     if prevsign!=0 and sign!=prevsign:flips+=1;run=0
     run+=1;last_run=sign*run;prevsign=sign
    if m>mx:mx=m;mxidx=j
    if m<mn:mn=m;mnidx=j
    abswalk+=abs(d);maxsingle=max(maxsingle,abs(d))
    db=b[j]-b[j-1];da=a[j]-a[j-1]
    bc=abs(db)>1e-10;ac=abs(da)>1e-10
    mark=0
    if bc and not ac:bidonly+=1;mark=1
    elif ac and not bc:askonly+=1;mark=-1
    elif bc and ac:joint+=1;mark=2 if db+da>0 else -2
    if mark and prevmark and mark!=prevmark:turns+=1
    if mark:prevmark=mark
    if da-db>1e-10:widen+=1
   o=kk*16
   out[row,o+0]=(last-s)/(abswalk+1e-6)
   out[row,o+1]=last-s
   out[row,o+2]=1 if mnidx>mxidx else (-1 if mnidx<mxidx else 0)
   out[row,o+3]=float(i-max(mxidx,mnidx))/steps
   out[row,o+4]=up/steps;out[row,o+5]=down/steps;out[row,o+6]=flips/steps
   out[row,o+7]=bidonly/steps;out[row,o+8]=askonly/steps
   out[row,o+9]=joint/steps;out[row,o+10]=widen/steps;out[row,o+11]=turns/steps
   out[row,o+12]=last_run/steps
   j3=max(start,i-3)
   out[row,o+13]=((b[i]+a[i])-(b[j3]+a[j3]))*.5/(abswalk+1e-6)
   out[row,o+14]=min(60000.,t[i]-t[start])/60000.
   out[row,o+15]=maxsingle
 return out

def grammar(t,b,a,ix,block=180000):
 ix=np.asarray(ix,dtype=np.int64)
 if (np.diff(ix)<=0).any() or (np.diff(t)<0).any():raise ValueError('must be ordered by raw ordinal')
 X=np.empty((len(ix),len(NAMES)),np.float16)
 for lo in range(0,len(ix),block):
  hi=min(lo+block,len(ix));z=_compute(t,b,a,ix[lo:hi]);
  if not np.isfinite(z).all():raise ValueError('bad quote geometry')
  X[lo:hi]=z.astype(np.float16)
 return X

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def build(mon):
 OUT.mkdir(parents=True,exist_ok=True)
 raw=ROOT/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
 if sha(raw)!=PINNED[mon]:raise ValueError('raw feed does not match original H1V2')
 orig=ROOT/f'h1v2/results/h1v2_dukascopy_{mon}_oracle_labels.npz'
 original=json.loads((orig.parent/f'h1v2_dukascopy_{mon}_receipt.json').read_text())
 if sha(orig)!=original['teacher_labels_sha256']:raise ValueError('original complete labels drifted')
 with np.load(orig,allow_pickle=False) as z:ix=z['tick_index'].copy();stamp=z['t'].copy()
 t,b,a=read_ticks(raw)
 if not np.array_equal(t[ix],stamp):raise ValueError('raw tick ordinal timestamps mismatch')
 X=grammar(t,b,a,ix)
 dest=OUT/f'R10_GRAMMAR_{mon}.npy';np.save(dest,X,allow_pickle=False)
 receipt=dict(month=mon,raw_sha256=PINNED[mon],teacher_labels_sha256=original['teacher_labels_sha256'],rows=len(ix),quote_count=len(t),features=list(NAMES),path_sha256=sha(dest),status='FULL_MONTH_SOURCE_EXACT_ASOF_QUOTE_GRAMMAR_NO_HINDSIGHT_FEATURE')
 (OUT/f'R10_GRAMMAR_{mon}_receipt.json').write_text(json.dumps(receipt,indent=2))
 return receipt
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--month',choices=['01','02','06','07'],required=True);args=p.parse_args();print(json.dumps(build(args.month)),flush=True)
