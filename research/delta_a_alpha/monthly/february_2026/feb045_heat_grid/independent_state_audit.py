"""Independent first-party quote-side tick-equity audit of saved FEB045 accepted ledgers."""
from pathlib import Path
from datetime import datetime, timezone
import numpy as np, json, gc
R=Path('/mnt/data/feb045')
t=np.load('/mnt/data/feb044_work/quotes_t.npy',mmap_mode='r')
a=np.load('/mnt/data/feb044_work/quotes_a.npy',mmap_mode='r')
b=np.load('/mnt/data/feb044_work/quotes_b.npy',mmap_mode='r')
N=len(t); output=[]
for name in ['pocket_09_no_heat','state_cut8_c22512_c25512','state_cut9_c22512_c25512']:
    f=R/(name+'_ledger.npz');z=np.load(f); E,X,price,D,P=(z[k] for k in ['E','X','R','D','P']); loc=D>0;short=D<0
    px=np.where(loc,(b[X]-price)/1000.,(price-a[X])/1000.)-.02
    error=float(np.max(np.abs(P-px)))
    nL=np.cumsum(np.bincount(E[loc],minlength=N)-np.bincount(X[loc],minlength=N))
    nS=np.cumsum(np.bincount(E[short],minlength=N)-np.bincount(X[short],minlength=N))
    pL=np.cumsum(np.bincount(E[loc],weights=price[loc],minlength=N)-np.bincount(X[loc],weights=price[loc],minlength=N))
    pS=np.cumsum(np.bincount(E[short],weights=price[short],minlength=N)-np.bincount(X[short],weights=price[short],minlength=N))
    realized=np.cumsum(np.bincount(X,weights=P,minlength=N))
    equity=realized+(nL*b-pL+pS-nS*a)/1000.-.02*(nL+nS)
    dd=np.maximum.accumulate(equity)-equity
    trough=int(np.argmax(dd));peak=int(np.argmax(equity[:trough+1])); maxopen=int((nL+nS).max())
    net=float(P.sum());gl=float(P[P<0].sum());gp=float(P[P>0].sum()); trades=len(P);pf=gp/(-gl)
    per_second=int(np.unique(t[E]//1000,return_counts=True)[1].max())
    utc_day=np.array(t[X]//86400000,dtype=np.int64)
    days=np.unique(utc_day)
    daily=[]
    for d in days:
        q=P[utc_day==d]
        daily.append({'date':datetime.fromtimestamp(int(d)*86400,timezone.utc).date().isoformat(),'net':round(float(q.sum()),3),'trades':len(q)})
    obj={'name':name,'qa_pass':error<1e-9 and maxopen<=1536 and per_second<=10 and len(np.unique(E))==len(E),'trades':trades,'net':round(net,3),'gross_loss':round(gl,3),'profit_factor':round(pf,6),'exact_full_tick_equity_dd':round(float(dd[trough]),3),'max_positions':maxopen,'quote_count':N,'max_first_passage_pnl_error':error,'max_entries_per_utc_second':per_second,'peak_time_utc':datetime.fromtimestamp(int(t[peak])/1000,timezone.utc).isoformat(),'trough_time_utc':datetime.fromtimestamp(int(t[trough])/1000,timezone.utc).isoformat(),'positive_active_days':sum(x['net']>0 for x in daily),'active_days':len(daily),'daily':daily}
    output.append(obj);print('INDEPENDENT',name,'net',obj['net'],'GL',obj['gross_loss'],'PF',obj['profit_factor'],'trades',trades,'exactDD',obj['exact_full_tick_equity_dd'],'maxopen',maxopen,'max/sec',per_second,'qa',obj['qa_pass'],flush=True)
    if not obj['qa_pass']:raise ValueError('Independent QA failed')
    del nL,nS,pL,pS,realized,equity,dd;gc.collect()
(R/'FEB045_INDEPENDENT_EQUITY_AUDIT.json').write_text(json.dumps(output,indent=2))