"""Independent vectorized acceptance and full-tick equity QA for FEB047 queued, fixed-ledger research."""
from pathlib import Path
import numpy as np,json,datetime,collections,hashlib
O=Path('/mnt/data/feb047');F=Path('/mnt/data/feb045');
t=np.load('/mnt/data/feb044_work/quotes_t.npy',mmap_mode='r');a=np.load('/mnt/data/feb044_work/quotes_a.npy',mmap_mode='r');b=np.load('/mnt/data/feb044_work/quotes_b.npy',mmap_mode='r');N=len(t)
rows=[]
for label,fn,baseline in [
 ('queued_original_reversal','FEB047_QUEUED_reversal_best.npz','pocket_09_no_heat_ledger.npz'),
 ('queued_original_focused','FEB047_QUEUED_focused_best.npz','pocket_09_no_heat_ledger.npz'),
 ('queued_lower_dd_transfer','FEB047_QUEUED_transfer_best.npz','state_cut8_c22512_c25512_ledger.npz'),
 ('queued_focused_scan_best','FEB047_QUEUED_SCREEN_BEST.npz','pocket_09_no_heat_ledger.npz'),
 ('queued_profit_cushion','FEB047_PROFIT_CUSHION_LEDGER.npz','pocket_09_no_heat_ledger.npz')]:
 f=O/fn
 if not f.exists():continue
 with np.load(f) as z:E,X,R,D,P,S=[z[k] for k in ('E','X','R','D','P','S')]
 with np.load(F/baseline) as z:oldX=z['X'];oldP=z['P'];origE=z['E'];oldR=z['R'];oldD=z['D']
 lng=D>0; sh=D<0
 expect=np.where(lng,b[X]-R,R-a[X])/1000.-.02
 err=float(np.max(np.abs(expect-P)))
 changed=X<oldX
 assert np.all(X<=oldX) and np.array_equal(E,origE) and np.array_equal(R,oldR) and np.array_equal(D,oldD)
 assert np.allclose(P[~changed],oldP[~changed])
 assert np.unique(X[changed]).size==changed.sum() # one supplementary close per market tick
 sec=np.r_[t[E]//1000,t[X[changed]]//1000]; counts=np.unique(sec,return_counts=True)[1]
 maxrate=int(counts.max())
 assert len(np.unique(E))==len(E) and err<1e-8
 nl=np.cumsum(np.bincount(E[lng],minlength=N)-np.bincount(X[lng],minlength=N),dtype=np.int64)
 ns=np.cumsum(np.bincount(E[sh],minlength=N)-np.bincount(X[sh],minlength=N),dtype=np.int64)
 pl=np.cumsum(np.bincount(E[lng],weights=R[lng],minlength=N)-np.bincount(X[lng],weights=R[lng],minlength=N))
 ps=np.cumsum(np.bincount(E[sh],weights=R[sh],minlength=N)-np.bincount(X[sh],weights=R[sh],minlength=N))
 realized=np.cumsum(np.bincount(X,weights=P,minlength=N))
 eq=realized+(nl*b.astype(np.float64)-pl+ps-ns*a.astype(np.float64))/1000.-.02*(nl+ns)
 dd=np.maximum.accumulate(eq)-eq;trough=int(np.argmax(dd));peak=int(np.argmax(eq[:trough+1]));maxopen=int(np.max(nl+ns))
 actual=lambda i:datetime.datetime.fromtimestamp(int(t[i])/1000,datetime.timezone.utc).isoformat()
 day=t[X]//86400000
 daily=[]
 for d in np.unique(day):
  q=P[day==d];daily.append({'day':datetime.datetime.fromtimestamp(int(d)*86400,datetime.timezone.utc).date().isoformat(),'pnl':round(float(q.sum()),3),'trades':len(q)})
 rows.append(dict(name=label,reconciled=True,strict_combined_order_rate_pass=bool(maxrate<=10),original_completed_trades=len(P),net=round(float(P.sum()),3),gross_loss=round(float(P[P<0].sum()),3),profit_factor=round(float(P[P>0].sum())/-float(P[P<0].sum()),5),exact_full_tick_dd=round(float(dd.max()),3),drawdown_peak_quote=actual(peak),drawdown_trough_quote=actual(trough),maxopen=maxopen,max_entry_and_repair_orders_in_one_second=maxrate,early_reductions=int(changed.sum()),max_quote_pnl_error=err,positive_active_days=sum(d['pnl']>0 for d in daily),active_days=len(daily),daily=daily))
 print('INDEPENDENT',label,rows[-1]['net'],rows[-1]['gross_loss'],rows[-1]['profit_factor'],rows[-1]['exact_full_tick_dd'],rows[-1]['early_reductions'],flush=True)
(O/'FEB047_INDEPENDENT_QA.json').write_text(json.dumps(rows,indent=2))