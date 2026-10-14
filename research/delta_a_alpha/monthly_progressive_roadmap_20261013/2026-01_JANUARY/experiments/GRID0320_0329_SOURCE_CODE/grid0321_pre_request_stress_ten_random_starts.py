"""GRID0321 seeded ten 7-day original-tick pre-request quote quality sweeps.
No month/day label used as a trading decision. Complete 7-calendar-day horizon.
Never assert broker survivability or 100x success without explicit replay.
"""
from __future__ import annotations
import json,time,hashlib
from pathlib import Path
import numpy as np
import grid0320_causal_pre_request_microstructure_admission as sim
import grid0313_seven_day_ten_start_stopout_frontier as sample
from grid0307_random_start_lowcapital_original_tick import TICK_SOURCE
ROOT=Path(__file__).resolve().parent
POLICIES=[
 ('GRID0316_CONTROL',0.,0.,0.,.20),
 ('PRE_SPREAD_LE_0P40',.40,0.,0.,.20),
 ('PRE_SPREAD_LE_0P25',.25,0.,0.,.20),
 ('PRE_SHOCK5_LE_1P5',0.,1.5,0.,.20),
 ('PRE_SHOCK5_LE_3P0',0.,3.0,0.,.20),
 ('SPREAD_LE_0P40_SHOCK_LE_3',.40,3.0,0.,.20),
 ('SHOCK5_GE_0P25',0.,0.,.25,.20),
 ('SHOCK5_GE_0P5',0.,0.,.5,.20),
]

def main():
    tick_start=time.time()
    assert hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest()=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
    t,bid,ask,z,kind,owner,pgid,r9,origin=sample.sim.prior.g.g.base.p.ancestor.base.materialize()
    eligible,dates=sample.select_days(r9,t)
    out=[]
    for d in dates:
        day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=int(np.searchsorted(t,day,'left'));hi=int(np.searchsorted(t,day+7*86400000,'left'))
        et=t[lo:hi];eb=bid[lo:hi];ea=ask[lo:hi]
        mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
        zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
        zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
        keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
        for j in np.flatnonzero(trunc):
            ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(eb[ix] if dr>0 else ea[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
        pre,shock=sim.features(et,eb,ea)
        for name,spreadmax,shockmax,shockmin,budget in POLICIES:
            x=sim.run(et,eb,ea,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=budget,stopout_ratio=.5,
                      screen_quote_idx=pre,pre_request_shock_5s=shock,max_observed_spread=spreadmax,
                      max_observed_5s_shock=shockmax,min_observed_5s_shock=shockmin)
            deals=x.pop('booked_ledger');adm=x.pop('accepted_indices')
            out.append(dict(date=d,policy=name,final_cash=x['final_cash'],net=x['net_cash'],trades=x['trades_closed'],
                            min_equity=x['min_tick_equity'],worst_hour_drawdown=x['worst_hour_drawdown'],
                            min_margin_ratio=x['min_margin_ratio_observed'],forced_events=x['forced_events'],
                            accepted=len(adm),blocked=x['denied'].get('pre_request_microstructure',0),
                            max_open=x['peak_open'],target100x=x['final_cash']>=10000.))
        print('done',d,'seconds',round(time.time()-tick_start,1),flush=True)
    score={}
    for name,*_ in POLICIES:
        rs=[q for q in out if q['policy']==name]
        score[name]=dict(n=len(rs),nonruin=sum(q['min_equity']>0 for q in rs),broker_stopout_free=sum(q['forced_events']==0 for q in rs),
            positive_7day=sum(q['final_cash']>100 for q in rs),hit_10000=sum(q['target100x'] for q in rs),
            total_trades=sum(q['trades'] for q in rs),min_end=min(q['final_cash'] for q in rs),
            max_end=max(q['final_cash'] for q in rs),worst_hour=max(q['worst_hour_drawdown'] for q in rs),
            min_equity=min(q['min_equity'] for q in rs),median_end=float(np.median([q['final_cash'] for q in rs])),
            skipped=sum(q['blocked'] for q in rs))
        print(name,score[name],flush=True)
    result=dict(id='GRID0321_ORIGINAL_JAN_10_START_PRE_REQUEST_ASOF_MICROSTRUCTURE',status='UNPROMOTED_NOT_ENDOGENOUS_SOURCE',
         date_seed=sample.SEED,dates=dates,policies=POLICIES,score=score,episodes=out,
         model_limits=['Historical precomputed January signals and exit times; read as hypothesis controls only',
            'No real Coinexx request-to-fill order state or hedged margin; 500x hypothetical leverage',
            'At least 1 sec prior observed quote quality may not match actual signal timestamp',
            'No future teacher or date labels used by screen; historical January selection bias still applies'],
         source_sha=hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest(),elapsed_s=round(time.time()-tick_start,2))
    path=ROOT/'grid0321_ten_start_pre_request_microstructure_results.json';path.write_text(json.dumps(result,indent=2))
    print('SAVED',path,flush=True)

if __name__=='__main__': main()
