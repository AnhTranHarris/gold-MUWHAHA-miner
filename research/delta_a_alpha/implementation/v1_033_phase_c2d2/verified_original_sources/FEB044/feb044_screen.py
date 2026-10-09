"""FEB044 exploratory causal-entry-source gates; legacy proposal tape, no full V1 certification."""
import os,sys,time,json,collections
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/feb044_work'); F=ROOT/'FEB042'; PATH=ROOT
os.environ['DAA_JAN039_RESEARCH_DIR']=str(ROOT);os.environ['DAA_JAN039_EQUITY_HELPERS']=str(ROOT/'original/source');os.environ['DAA_FEB043_ORIGINAL_SOURCE_DIR']=str(ROOT/'original/source')
sys.path[:0]=[str(ROOT/'original/source'),str(ROOT/'FEB043'),str(ROOT)];import stmr_janjul as j
T=np.load(ROOT/'quotes_t.npy',mmap_mode='r');A=np.load(ROOT/'quotes_a.npy',mmap_mode='r');B=np.load(ROOT/'quotes_b.npy',mmap_mode='r');start=int(np.datetime64('2026-02-01','ms').astype('i8'));end=int(np.datetime64('2026-03-01','ms').astype('i8'))
j.load_month=lambda mm,wd=10:(T,A,B,start,end)
import engine_dualcaps as m
with np.load(F/'FEB042_JAN039_PREPARED_PROPOSALS.npz') as z:raw={k:z[k].copy() for k in 'EXRDPHSCON'};spr=z['spread'].copy();imp=z['imp20'].copy()
with np.load(F/'FEB042_CAUSAL_ENTRY_FEATURES.npz') as z:prior=z['prior10_range'].copy()
with np.load(F/'FEB042_FIRSTPASS_GRID.npz') as z:sel=z['selected'].copy();th=z['thresholds'].copy();xx=z['X'].copy();pp=z['P'].copy()
for k in 'EXRDPHSCON':setattr(m,k,raw[k].copy())
m.total=len(m.E);m.imp20=imp
phase=(m.t[m.E]//600000)%6
mask=np.zeros(m.total,bool)
for src,p in [(25,0),(23,5),(21,0)]:mask|=(m.S==src)&(phase==p)
source_set=[17,21,23,25,27];extras={22:(0,4),19:(0,8),24:(0,4)}
allowed=np.zeros(m.total,bool)
for src in source_set: allowed|=(m.S==src)&((prior>=16)&(prior<32) if src==27 else True)
for src,(lo,hi) in extras.items():allowed|=(m.S==src)&(prior>=lo)&(prior<hi)
base_allowed=allowed & ~mask
bit=sum(1<<(s-10) for s in range(17,29) if s not in source_set+list(extras))
ki={float(v):i for i,v in enumerate(th)}
idx={s:sel[raw['S'][sel]==s] for s in [21,23,25,27,17,19,22,24]}
row={s:np.flatnonzero(raw['S'][sel]==s) for s in idx}
def exits(tp=None,phase25=None):
 m.X=raw['X'].copy();m.P=raw['P'].copy()
 for src,target in (tp or {21:20,23:15,25:25,27:50}).items():
  if src not in idx or target not in ki:continue
  m.X[idx[src]]=xx[row[src],ki[float(target)]];m.P[idx[src]]=pp[row[src],ki[float(target)]]
 for ph,target in (phase25 or {1:15,5:10}).items():
  ix=idx[25];rr=row[25];f=phase[ix]==ph;m.X[ix[f]]=xx[rr[f],ki[float(target)]];m.P[ix[f]]=pp[rr[f],ki[float(target)]]
with open(ROOT/'JAN037_WD_EXACT_8.json') as f:params=json.load(f)['params']
params.update(maxopen=1536,sidecap=1536,per_quote=1,per_second=10,wdcap=8,cap_cell=4,phase5cap=128,phase0cap=224,source26cap=432,s25phase1cap=896,s25phase34cap=1024,phase3cap=448,phase4cap=448,l3_excluded_hours=bit)
exits();m.spread=np.where((m.S>=17)&~base_allowed,np.inf,spr)
t0=time.time();r,_=m.run(**params);print('VERIFY_BASELINE',r['net'],r['trades'],r['gl'],r['event_eq_dd_lb'], 'seconds',time.time()-t0,flush=True)
results=[]
def run(name,deny=None,q=None,tp=None,phase25=None):
 if tp is not None or phase25 is not None:exits(tp,phase25)
 f=base_allowed.copy();
 if deny is not None:f &= ~deny
 m.spread=np.where((m.S>=17)&~f,np.inf,spr)
 z,ld=m.run(**(params if q is None else {**params,**q}))
 z1={k:z[k] for k in ['net','gl','trades','pf','maxopen','event_eq_dd_lb']};z1.update(name=name,elapsed=round(time.time()-t0,2));results.append(z1)
 print(json.dumps(z1),flush=True)
 return z,ld

def save(): (ROOT/'FEB044_SCREEN_ROWS.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':
 S=m.S;P=phase;R=prior
 G={
 'a_s19_phase_015':(S==19)&np.isin(P,[0,1,5]),
 'b_s17_phase_15':(S==17)&np.isin(P,[1,5]),
 'c_s25_range_12_16':(S==25)&(R>=12)&(R<16),
 'd_s19_all':(S==19),
 'e_s17_all':(S==17),
 'f_s27_phase3':(S==27)&(P==3),
 'g_s23_phase3':(S==23)&(P==3),
 'h_s25_phase3':(S==25)&(P==3),
 'i_s25_range_8_24':(S==25)&(R>=8)&(R<24),
 'j_s19_phase4':(S==19)&(P==4),
 'k_s25_phase1':(S==25)&(P==1),
 'l_s17_range_4_8':(S==17)&(R>=4)&(R<8),
 'm_s21_range_4_6':(S==21)&(R>=4)&(R<6),
 'n_s23_range_12_16':(S==23)&(R>=12)&(R<16),
 'o_s25_phase2':(S==25)&(P==2),
 }
 for k,v in G.items():run(k,v)
 for ids in [['a','b'],['a','b','c'],['a','b','c','j'],['a','b','c','j','f'],['a','b','c','l'],['d','b','c'],['d','e','c'],['a','b','c','m'],['a','b','c','n'],['a','b','c','f','m'],['a','b','c','n','m'],['a','b','c','m','n','j'],['d','e','c','m','n']]:
  key={k[0]:v for k,v in G.items()};deny=np.logical_or.reduce([key[k] for k in ids]);run('combo_'+''.join(ids),deny)
 save()
