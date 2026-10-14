"""Independent full original quote reconciliation of GRID0312 executed funded ledger.
No use of the strategy's book/cache to recreate the independent equity trajectory.
Full Python code + original raw result ledgers preserved; research-only.
"""
from __future__ import annotations
import numpy as np
from pathlib import Path
import json

def reconstruct(t,bid,ask,z,accepted,closed,initial=100.,slippage_per_close=0.):
    n=len(t);accepted=np.asarray(accepted,np.int64)
    book=dict(); first=set()
    for ix,j,cash,reason in closed:
        j=int(j);ix=int(ix)
        assert 0<=j<len(z['entry_idx']) and 0<=ix<n
        assert j not in first,('duplicate closing',j)
        assert j in accepted
        assert int(z['entry_idx'][j])<=ix
        en=int(z['entry_price_raw'][j]);d=int(z['direction'][j]);px=int(bid[ix] if d>0 else ask[ix])
        independent=d*(px-en)/1000.-.20-slippage_per_close
        assert abs(independent-cash)<1e-9,(j,independent,cash)
        first.add(j);book[j]=(ix,float(cash))
    assert len(first)==len(accepted)
    dlo=np.zeros(n+1,dtype=np.int32);dsh=np.zeros(n+1,dtype=np.int32)
    dbasis=np.zeros(n+1,np.float64);dcash=np.zeros(n+1,np.float64);dmarg=np.zeros(n+1,np.float64)
    for j in accepted:
        en=int(z['entry_idx'][j]);ex,p=book[int(j)];px=int(z['entry_price_raw'][j])/1000.;d=int(z['direction'][j])
        if d>0:dlo[en]+=1;dlo[ex]-=1
        else:dsh[en]+=1;dsh[ex]-=1
        dbasis[en]+=d*px;dbasis[ex]-=d*px;dmarg[en]+=px/500.;dmarg[ex]-=px/500.
        dcash[ex]+=p
    lo=np.cumsum(dlo[:-1]);sh=np.cumsum(dsh[:-1]);basis=np.cumsum(dbasis[:-1]);paid=np.cumsum(dcash[:-1]);marg=np.cumsum(dmarg[:-1]);open_count=lo+sh
    eq=initial+paid+(lo.astype(float)*bid-sh.astype(float)*ask)/1000.-basis-.20*open_count
    dd=np.maximum.accumulate(eq)-eq
    hours=t//3600000;boundaries=np.r_[0,np.flatnonzero(np.diff(hours))+1,len(t)]
    worst_hour=float(max((np.maximum.accumulate(eq[boundaries[k]:boundaries[k+1]])-eq[boundaries[k]:boundaries[k+1]]).max() for k in range(len(boundaries)-1)))
    final=float(initial+paid[-1]);assert abs(final-float(eq[-1]))<1e-5
    return dict(min_equity=float(eq.min()),max_equity_dd=float(dd.max()),worst_hour_dd=worst_hour,
                close_cash=final,closed_trades=len(book),max_funded=int(open_count.max()),
                max_margin=float(marg.max()),closed_cash_sum=float(paid[-1]))


def run_one(t,bid,ask,z,kind,owner,pgid,policy):
    import grid0312_tick_stopout_executable as sim
    name,fraction,stop,defense,style,slip=policy
    r=sim.run(t,bid,ask,z,kind,owner,pgid,cash=100.,admission_margin_fraction=fraction,
              stopout_ratio=stop,defensive_ratio=defense,liquidation_style=style,
              defensive_flatten=style=='flatten',max_tick_slippage_usd=slip)
    ledger=r.pop('booked_ledger');approved=r.pop('accepted_indices')
    independent=reconstruct(t,bid,ask,z,approved,ledger,slippage_per_close=slip)
    assert abs(independent['close_cash']-r['final_cash'])<1e-5
    assert abs(independent['min_equity']-r['min_tick_equity'])<1e-5,(name,r['min_tick_equity'],independent['min_equity'])
    assert abs(independent['max_equity_dd']-r['max_tick_drawdown'])<1e-5,(name,r['max_tick_drawdown'],independent['max_equity_dd'])
    # The engine continuously tracks between candidate times; hourly post-fill
    # marks are compared to the fully reconstructed original tick trajectory.
    assert abs(independent['worst_hour_dd']-r['worst_hour_drawdown'])<1e-5,(name,r['worst_hour_drawdown'],independent['worst_hour_dd'])
    return r,independent,approved,ledger
