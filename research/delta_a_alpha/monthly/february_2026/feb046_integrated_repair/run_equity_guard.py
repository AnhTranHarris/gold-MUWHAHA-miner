"""FEB046 equity-aware *funded within original-source tape* L7 gate. Before order approval evaluate observed account equity at that actual quote; no future bars, no prospective loss credit. Full-tick equity independently recomputed for viable finals. Research only.
"""
from pathlib import Path
import os,sys,json,time
import numpy as np
F=Path('/mnt/data/feb045');OUT=Path('/mnt/data/feb046');src=(F/'engine_statecaps.py').read_text()
assert 'equity_guard' not in src
src=src.replace('s25_range_threshold=64.):','s25_range_threshold=64.,equity_guard=1e12):')
src=src.replace('    open_heap=[] # (exit_tick, entry_arridx)','    peak_equity=initial_balance\n    open_heap=[] # (exit_tick, entry_arridx)')
needle='''        # Completed prior 10m state conditional cap: never current bucket or future label.'''
ins='''        # Causal cross-source peak-equity guard, evaluated BEFORE committing new risk.
        current_eq=acct+(nl*int(b[ei])-sumlong+sumshort-ns*int(a[ei]))/1000.-0.02*(nl+ns)
        if current_eq>peak_equity:peak_equity=current_eq
        if peak_equity-current_eq>=equity_guard:
            allowed=False;denied[14]+=1
'''
assert needle in src;src=src.replace(needle,ins+needle)
(OUT/'engine_equity_guard_046.py').write_text(src)
raw=(F/'run_statecaps.py').read_text().split('log=[]')[0]
ns={'__file__':str(F/'run_statecaps.py'),'__name__':'feb046_eq'};exec(compile(raw,'feb045_pinned','exec'),ns)
h=ns['h'];original=ns['m'];base=ns['base'];order=ns['order'];params=ns['params'];s=original.S
sys.path[:0]=[str(OUT)];import engine_equity_guard_046 as m
for k in 'EXRDPHSCON':setattr(m,k,getattr(original,k).copy())
m.total=original.total;m.imp20=h.imp;m.prior10=h.prior
rows=[]
for cut in [9,8]:
 den=np.zeros_like(base)
 for p in order[:cut]:den|=p
 m.spread=np.where(~(base&~den),np.inf,h.spr)
 for limit in [7000,9500,12000,14500,17000,20000]:
  ts=time.time();z,ld=m.run(**dict(params,equity_guard=limit))
  if z['net']>=198500:m.daily_and_exact(ld,z)
  row={k:z.get(k) for k in ['net','gl','pf','trades','event_eq_dd_lb','equity_dd','maxopen']};row.update(cut=cut,limit=limit,seconds=round(time.time()-ts,2))
  rows.append(row);print('EQ_GUARD',json.dumps(row),flush=True)
  (OUT/'EQUITY_GUARD_SCREEN.json').write_text(json.dumps(rows,indent=2))