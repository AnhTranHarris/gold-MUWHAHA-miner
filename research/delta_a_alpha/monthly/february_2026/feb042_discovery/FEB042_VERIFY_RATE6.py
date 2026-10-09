import os,sys,json,time,hashlib
import numpy as np
from pathlib import Path
b=Path('/mnt/data/feb041');w=Path('/mnt/data/feb042')
os.environ['DAA_JAN039_RESEARCH_DIR']=str(b);os.environ['DAA_JAN039_EQUITY_HELPERS']=str(b/'original/source')
sys.path[:0]=[str(b),str(b/'original/source')]
import feb041_legacy_engine as m
with np.load(w/'FEB042_JAN039_PREPARED_PROPOSALS.npz') as z:raw={k:z[k].copy() for k in 'EXRDPHSCON'};ex=z['excluded'].copy();spr=z['spread'].copy();imp=z['imp20'].copy()
with np.load(w/'FEB042_CAUSAL_ENTRY_FEATURES.npz') as z:prior=z['prior10_range'].copy()
with np.load(w/'FEB042_FIRSTPASS_GRID.npz') as z:sel=z['selected'].copy();ths=z['thresholds'].copy();xx=z['X'].copy();pp=z['P'].copy()
for k in 'EXRDPHSCON':setattr(m,k,raw[k]);m.total=len(m.E)
m.imp20=imp
params=json.load(open(b/'JAN037_WD_EXACT_8.json'))['params'];params.update(maxopen=512,sidecap=512,per_second=6,wdcap=8,cap_cell=4,phase5cap=128,phase0cap=224,source26cap=432)
gates={17:(0,1e6),21:(0,1e6),23:(0,1e6),25:(0,1e6),27:(16,32)};allowed=np.zeros(m.total,bool)
for s,(lo,hi) in gates.items():allowed|=(m.S==s)&(prior>=lo)&(prior<hi)
params['l3_excluded_hours']=sum(1<<(s-10) for s in range(17,29) if s not in gates)
m.spread=np.where(ex|((m.S>=17)&~allowed),np.inf,spr)
for s,target in {21:20,23:15,25:20,27:30}.items():
 ix=ths.tolist().index(float(target));mask=(raw['S'][sel]==s);inds=sel[mask];m.X[inds]=xx[mask,ix];m.P[inds]=pp[mask,ix]
z,L=m.run(**params)
print('SIM',json.dumps({k:z[k] for k in ['net','trades','gl','pf','event_eq_dd_lb','maxopen']}),flush=True)
a=m.daily_and_exact(L,z)
print('EXACT',json.dumps({k:a[k] for k in ['net','trades','gl','pf','equity_dd','balance_dd' if 'balance_dd' in a else 'bal_dd','maxopen_full']}),flush=True)
# quote-side PnL rechecked independently
recon=((np.where(L['D']>0,m.b[L['X']],m.a[L['X']])-L['R'])*L['D']/1000.-.02)
max_diff=float(np.max(np.abs(recon-L['P'])))
source={int(s):{'trades':int((L['S']==s).sum()),'net':float(L['P'][L['S']==s].sum()),'gross_loss':float(L['P'][(L['S']==s)&(L['P']<0)].sum())} for s in np.unique(L['S'])}
monthly={'metric':{k:z[k] for k in ['net','trades','gp','gl','pf','event_eq_dd_lb','bal_dd','maxopen','wd_trades']},'exact_tick_equity_dd':a['equity_dd'],'maxopen_exact':a['maxopen_full'],'pnl_max_discrepancy':max_diff,'daily':a['daily'],'weekly':a['weekly'],'by_source':source,'params':params,'state_gates':gates,'entry_known_first_touch_take':{21:20,23:15,25:20,27:30},'provenance':'FEB042 2026-02 Duke raw quote/source original 131E + preserved JAN039 proposal model; February-fitted, no genuine broker parity'}
(w/'FEB042_RATE6_EXACT.json').write_text(json.dumps(monthly,indent=2))
np.savez_compressed(w/'FEB042_RATE6_LEDGER.npz',**L)
print('QA','max_pnl_discrepancy',max_diff,'sources',json.dumps(source),'days',len(a['daily']),'weeks',len(a['weekly']),flush=True)