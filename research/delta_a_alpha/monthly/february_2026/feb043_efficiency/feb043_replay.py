#!/usr/bin/env python3
"""Reproduce FEB043 February original-source proposal-tape research candidates.

IMPORTANT: This is NOT the full, physically executable owner V1 and not an EA.
JAN/FEB raw quote hashes are pinned. The FEB041 frozen original source-proposal
engine may include non-endogenous hypothetical parent genealogy; do not promote.
Original literal V1 L0-L7 document governs architecture outside this model.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, os, sys
from pathlib import Path
import numpy as np

HASHES={1:'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
        2:'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'}
EXTRA={
 'balanced':{22:(0.,4.),19:(0.,8.),24:(0.,4.)},
 'lower_risk':{22:(0.,4.),19:(0.,4.),24:(0.,4.)},
 'high_velocity':{22:(0.,8.),19:(0.,8.),24:(0.,4.)},
}
EXPECTED={
 ('balanced',1536,10):(209415.695,39270,-56733.545,25651.986),
 ('balanced',1792,10):(218415.334,40155,-56911.591,25651.986),
 ('lower_risk',1792,10):(206234.332,31701,-42068.043,25651.986),
 ('high_velocity',1280,10):(205173.330,47274,-77470.461,29334.313),
 ('high_velocity',1536,10):(224695.205,49619,-78373.742,29831.936),
 ('balanced',1536,8):(200702.888,37780,-54422.414,24957.205),
 ('high_velocity',1536,8):(215712.482,48042,-75869.554,29812.876),
}
def sha256(path):
 with open(path,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--feb041',type=Path,required=True);ap.add_argument('--feb042',type=Path,required=True)
 ap.add_argument('--jan-raw-gz',type=Path,required=True);ap.add_argument('--feb-raw-gz',type=Path,required=True)
 ap.add_argument('--cache-dir',type=Path,default=None,help='Optional verified quote-cache .npy paths: quotes_t,a,b.npy')
 ap.add_argument('--profile',choices=EXTRA,default='balanced');ap.add_argument('--maxopen',type=int,default=1536)
 ap.add_argument('--per-second',type=int,default=10);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--ledger',action='store_true')
 args=ap.parse_args()
 for n,p in [(1,args.jan_raw_gz),(2,args.feb_raw_gz)]:
  got=sha256(p);assert got==HASHES[n],f'month {n} BAD SHA {got}'
 root=args.feb041.resolve();orig=root/'original'/'source';sys.path[:0]=[str(orig),str(root),str(Path(__file__).resolve().parent)]
 os.environ['DAA_JAN039_RESEARCH_DIR']=str(root);os.environ['DAA_JAN039_EQUITY_HELPERS']=str(orig);os.environ['DAA_FEB043_ORIGINAL_SOURCE_DIR']=str(orig)
 import stmr_janjul as j
 j.FILES[1]=str(args.jan_raw_gz.resolve());j.FILES[2]=str(args.feb_raw_gz.resolve())
 if args.cache_dir:
  co=args.cache_dir.resolve()
  T=np.load(co/'quotes_t.npy',mmap_mode='r');A=np.load(co/'quotes_a.npy',mmap_mode='r');B=np.load(co/'quotes_b.npy',mmap_mode='r')
  assert len(T)==11439219 and len(A)==len(B)==len(T)
  bstart=int(np.datetime64('2026-02-01T00:00:00','ms').astype('i8'));bend=int(np.datetime64('2026-03-01T00:00:00','ms').astype('i8'))
  def cached_month(m,wd=10):
   assert m==2 and wd==10
   return T,A,B,bstart,bend
  j.load_month=cached_month
 import engine_dualcaps as m
 w=args.feb042.resolve()
 with np.load(w/'FEB042_JAN039_PREPARED_PROPOSALS.npz') as z:
  raw={k:z[k].copy() for k in 'EXRDPHSCON'};spr=z['spread'].copy();imp=z['imp20'].copy()
 with np.load(w/'FEB042_CAUSAL_ENTRY_FEATURES.npz') as z:prior=z['prior10_range'].copy()
 with np.load(w/'FEB042_FIRSTPASS_GRID.npz') as z:
  sel=z['selected'].copy();th=z['thresholds'].copy();xx=z['X'].copy();pp=z['P'].copy()
 assert raw['E'].shape[0]==234698 and sel.shape[0]==42706
 for k in 'EXRDPHSCON':setattr(m,k,raw[k].copy())
 m.total=len(m.E);m.imp20=imp
 phase=(m.t[m.E]//600000)%6
 mask=np.zeros(m.total,dtype=bool)
 for src,ph in [(25,0),(23,5),(21,0)]:mask|=(m.S==src)&(phase==ph)
 extras=EXTRA[args.profile];valid=np.zeros(m.total,bool)
 for src in [17,21,23,25,27]:valid|=(m.S==src)&((prior>=16)&(prior<32) if src==27 else True)
 for src,(lo,hi) in extras.items():valid|=(m.S==src)&(prior>=lo)&(prior<hi)
 m.spread=np.where(((m.S>=17)&~valid)|mask,np.inf,spr)
 ixmap={float(x):i for i,x in enumerate(th)}
 for src,target in {21:20,23:15,25:25,27:50}.items():
  flags=(raw['S'][sel]==src);ii=sel[flags];rr=np.flatnonzero(flags);ti=ixmap[float(target)]
  m.X[ii]=xx[rr,ti];m.P[ii]=pp[rr,ti]
 # First-profitable-quote exit, executable side of each quote. Only predeclared profit targets.
 flags=(raw['S'][sel]==25);ii=sel[flags];rr=np.flatnonzero(flags)
 for ph,tp in [(1,15),(5,10)]:
  choose=(phase[ii]==ph);idx=ii[choose];r=rr[choose];k=ixmap[float(tp)]
  m.X[idx]=xx[r,k];m.P[idx]=pp[r,k]
 bit=sum(1<<(src-10) for src in range(17,29) if src not in [17,21,23,25,27]+list(extras))
 with open(root/'JAN037_WD_EXACT_8.json') as f:params=json.load(f)['params']
 params.update(maxopen=args.maxopen,sidecap=args.maxopen,per_quote=1,per_second=args.per_second,
               wdcap=8,cap_cell=4,phase5cap=128,phase0cap=224,source26cap=432,
               s25phase1cap=896,s25phase34cap=1024,phase3cap=448,phase4cap=448,l3_excluded_hours=bit)
 score,ledger=m.run(**params);score=m.daily_and_exact(ledger,score)
 key=(args.profile,args.maxopen,args.per_second)
 if key in EXPECTED:
  for value,expected in zip([score['net'],score['trades'],score['gl'],score['equity_dd']],EXPECTED[key]):
   assert abs(value-expected)<.002,('FROZEN_PARITY_FAILURE',key,value,expected)
 score.update(profile=args.profile,source_gate_map={str(k):v for k,v in extras.items()},
   frozen_reference_expected=EXPECTED.get(key),data_sha256={str(k):v for k,v in HASHES.items()},
   policy_type='FEBRUARY_FITTED_FIXED_SOURCE_PROPOSALS_NOT_FULL_OWNER_V1_OR_MT5')
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(score,indent=2))
 if args.ledger:np.savez_compressed(args.out.with_suffix('.npz'),**ledger)
 print(json.dumps({k:score[k] for k in ['net','trades','gl','pf','equity_dd','maxopen_full','profile']},sort_keys=True))

if __name__=='__main__':main()