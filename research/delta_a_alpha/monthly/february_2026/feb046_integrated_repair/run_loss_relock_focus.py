"""FEB046 new L7 physical source-campaign re-lock after genuinely accepted closed losses; month-blind inputs.
Patch cloned FEB045 research simulator, never alter original V1 whitepaper/production.
"""
import sys,os,json,time
from pathlib import Path
import numpy as np
F=Path('/mnt/data/feb045');R=Path('/mnt/data/feb044_work');OUT=Path('/mnt/data/feb046')
source=(F/'engine_statecaps.py').read_text();assert 'num_p' in source and 'last_loss_ms' not in source
source=source.replace('s25_range_threshold=64.):','s25_range_threshold=64.,loss_pause_ms=0,loss_pause_sources=0,reopen_confirm_ms=0):')
source=source.replace('    open_heap=[] # (exit_tick, entry_arridx)','    last_loss_ms=np.full(64,-10**15,np.int64)\n    open_heap=[] # (exit_tick, entry_arridx)')
source=source.replace('            acct+=pnl;closing+=1','            acct+=pnl;closing+=1\n            if ss>=17 and pnl<0: last_loss_ms[ss]=int(t[xi])')
needle='''        # Completed prior 10m state conditional cap: never current bucket or future label.'''
ins='''        # Funded-close owned source relock: never use future hypothetical outcome.
        if src>=17 and ((loss_pause_sources>>(src-10))&1) and last_loss_ms[src]>-10**14:
            since=ti-last_loss_ms[src]
            if since<loss_pause_ms:
                allowed=False;denied[14]+=1
            elif reopen_confirm_ms>0 and since<loss_pause_ms+reopen_confirm_ms:
                bucket=int(ti//300000-start_m5_bucket)
                trend=int(m5_completed_trend[bucket]) if bucket>=0 and bucket<len(m5_completed_trend) else 0
                if trend*direction<=0:
                    allowed=False;denied[14]+=1
'''
assert needle in source;source=source.replace(needle,ins+needle)
pth=OUT/'engine_funded_relock_046.py';pth.write_text(source)
# setup pinned source tape, same FEB045 selected quality filter
src=(F/'run_statecaps.py').read_text().split('log=[]')[0];ns={'__file__':str(F/'run_statecaps.py'),'__name__':'feb046_relock'};exec(compile(src,'feb045_pinned','exec'),ns)
h=ns['h'];oldm=ns['m'];base=ns['base'];order=ns['order'];params=ns['params'];den=np.zeros_like(base)
for p in order[:9]:den|=p
# Reimport patched: takes frozen arrays but same signature/execution
sys.path[:0]=[str(OUT)];import engine_funded_relock_046 as m
for k in 'EXRDPHSCON':setattr(m,k,getattr(oldm,k).copy())
m.total=oldm.total;m.imp20=h.imp;m.prior10=h.prior
m.spread=np.where(~(base&~den),np.inf,h.spr)
# completed M5 trend prepared as-of each quote's most recent TWO ALREADY CLOSED M5 bars
T=m.t;A=m.a;B=m.b;tick_bucket=T//300000;uniq,starts=np.unique(tick_bucket,return_index=True);ends=np.r_[starts[1:]-1,len(T)-1];midclose=(A[ends].astype(float)+B[ends])/2000
startb=int(uniq[0]);trend_tab=np.zeros(int(uniq[-1]-uniq[0]+2),np.int8)
for i in range(2,len(uniq)):
 if uniq[i-1]==uniq[i]-1 and uniq[i-2]==uniq[i]-2:trend_tab[int(uniq[i]-startb)]=np.sign(midclose[i-1]-midclose[i-2])
m.start_m5_bucket=startb;m.m5_completed_trend=trend_tab
rows=[]
for srcset in [[17,19],[23,26],[17,19,23,26]]:
 bit=sum(1<<(s-10) for s in srcset)
 for pause,reopen in [(300000,0),(900000,0)]:
  p=dict(params,loss_pause_sources=bit,loss_pause_ms=pause,reopen_confirm_ms=reopen)
  ts=time.time();out,ledger=m.run(**p)
  if out['net']>=200000:m.daily_and_exact(ledger,out)
  o={k:out.get(k) for k in ['net','gl','pf','trades','event_eq_dd_lb','equity_dd','maxopen']};o.update(sources=srcset,pause_ms=pause,reopen_ms=reopen,seconds=round(time.time()-ts,2))
  rows.append(o);print('RELOCK',json.dumps(o),flush=True)
  (OUT/'FUNDED_RELOCK_FOCUS_SCREEN.json').write_text(json.dumps(rows,indent=2))