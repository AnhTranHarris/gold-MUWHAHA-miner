"""GRID0308: 10-date/20-episode independently reconstructed quote equity + margin level.
Reuses identical original January candidate schedule but is NOT broker stopout executor.
A breached simulated margin floor is a FAIL; no speculative forced-close credits.
"""
from __future__ import annotations
import time,json,hashlib
from pathlib import Path
import numpy as np
import grid0303_causal_coverage_source_caps as g
from grid0307_random_start_lowcapital_original_tick import SEED, COUNT, TICK_SOURCE
ROOT=Path(__file__).resolve().parent
assert g.source.count('    return r')==1
patched=g.source.replace('    return r','    r["_accepted_candidate_rows_internal"] = idx\n    return r')
ns=dict(g.g.ns)
exec(patched,ns)
replay=ns['physical_replay']

def independent_mark(t,bid,ask,z,ix,cash,day_start_ms):
    L=len(t); E=z['entry_idx'][ix].astype(np.int64);X=z['exit_idx'][ix].astype(np.int64)
    D=z['direction'][ix].astype(np.int32)
    R=z['entry_price_raw'][ix].astype(float)/1000.; P=z['net_cash'][ix].astype(float)
    # At quote exit index no open position; after entry index physical fills recorded.
    dcL=np.zeros(L+1,np.int32);dcS=np.zeros(L+1,np.int32);dcB=np.zeros(L+1,np.float64)
    dcM=np.zeros(L+1,np.float64);dcBooked=np.zeros(L+1,np.float64)
    Lmask=D>0;Smask=~Lmask
    np.add.at(dcL,E[Lmask],1);np.add.at(dcL,X[Lmask],-1)
    np.add.at(dcS,E[Smask],1);np.add.at(dcS,X[Smask],-1)
    np.add.at(dcB,E,D*R);np.add.at(dcB,X,-D*R)
    np.add.at(dcM,E,R/500.);np.add.at(dcM,X,-R/500.)
    np.add.at(dcBooked,X,P)
    lon=np.cumsum(dcL[:-1]);sho=np.cumsum(dcS[:-1]);basis=np.cumsum(dcB[:-1]);margin=np.cumsum(dcM[:-1]);booked=np.cumsum(dcBooked[:-1]);opened=lon+sho
    eq=cash+booked+((lon.astype(float)*bid)-(sho.astype(float)*ask))/1000.-basis-opened*0.20
    # Reject impossible margin accounting negative due numerical noise.
    if margin.min()<-1e-5:raise AssertionError('Negative margin')
    active=margin>0.00001
    ratios=np.where(active,eq/np.maximum(margin,1.e-12),np.inf)
    min_ratio=float(np.min(ratios)) if active.any() else None
    first_breach={}
    for threshold in (0.5,1.,2.):
        crossed=np.flatnonzero(active&(ratios<threshold))
        first_breach[str(threshold)]=dict(utc_ms=int(t[crossed[0]]),equity=float(eq[crossed[0]]),margin=float(margin[crossed[0]])) if len(crossed) else None
    horizon=int(day_start_ms+86400000)
    j=max(0,min(L-1,int(np.searchsorted(t,horizon,'left'))-1))
    # Peak and drawdown 24h mark, include all original tick observations.
    time_window=int(np.searchsorted(t,horizon,'left'))
    eqday=eq[:max(1,time_window)];ddday=float(np.max(np.maximum.accumulate(eqday)-eqday))
    return {'min_tick_equity':float(eq.min()),'final_tick_equity':float(eq[-1]),
        'min_margin_level_ratio':min_ratio,'min_free_margin':float((eq-margin).min()),
        'first_margin_breaches':first_breach,
        'utc_first_24h_mark_equity':float(eq[j]),
        'utc_first_24h_drawdown':ddday,
        '24h_target_10000_hit':bool(eq[j]>=10000.),
        'trades':len(ix),'first_24h_booked_cash':float(booked[j]),
        'min_24h_equity':float(eqday.min()),
        'max_margin_usd':float(margin.max())}

def main():
    st=time.time()
    source_sha=hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest()
    assert source_sha=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
    t,bid,ask,z,kind,owner,pgid,r9,origin=g.g.base.p.ancestor.base.materialize()
    dates=sorted(r9['daily']);picked=sorted(np.random.default_rng(SEED).choice(dates,COUNT,replace=False).tolist())
    entries=[]
    for date in picked:
        start=int(np.datetime64(date+'T00:00:00','ms').astype('int64'))
        lo=int(np.searchsorted(t,start,'left'))
        tt=t[lo:];bb=bid[lo:];aa=ask[lo:]
        mask=z['entry_idx']>=lo
        zz={k:v[mask].copy() for k,v in z.items()}
        zz['entry_idx']-=lo;zz['exit_idx']-=lo
        for title,cap in [('GLOBAL_CAP2',2),('GLOBAL_CAP4',4)]:
            out=replay(tt,bb,aa,zz,kind[mask],owner[mask],pgid,r9,cash=100.,cap=cap,
                loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=cap,
                earned_wins=7,earned_window=10,earned_edge=12,parent_cap=cap,
                earned_parent_cap=cap,parent_wins=4,parent_window=6,parent_edge=4,
                hourly_entry_lock_usd=0.,hourly_soft_parent_usd=400.,hourly_soft_parent_cap=cap,
                gc0_cap=cap,gc2_cap=cap)
            ix=out.pop('_accepted_candidate_rows_internal')
            audit=independent_mark(tt,bb,aa,zz,ix,100.,start)
            assert audit['trades']==out['trades']
            assert abs(audit['min_tick_equity']-out['min_actual_tick_equity'])<1.e-6
            assert abs(audit['final_tick_equity']-out['ending_equity'])<1.e-6
            v=dict(start_day_utc=date,config=title,initial_usd=100.,model_ending_usd=out['ending_equity'],modeled_net=out['net'],peak_open=out['peak_open_stream'],**audit)
            v['necessary_margin_level_100pct_pass']=v['first_margin_breaches']['1.0'] is None
            v['necessary_margin_level_50pct_pass']=v['first_margin_breaches']['0.5'] is None
            v['certified_real_broker_survival']=False
            entries.append(v)
            print(date,title,'end',round(v['model_ending_usd'],2),'min',round(audit['min_tick_equity'],2),
                'min.margin/eq',round(audit['min_margin_level_ratio'] or 0,2),
                'necessary100pct',v['necessary_margin_level_100pct_pass'],
                'first24h mark',round(audit['utc_first_24h_mark_equity'],2),flush=True)
    aggregate={}
    for label in ('GLOBAL_CAP2','GLOBAL_CAP4'):
        these=[x for x in entries if x['config']==label]
        aggregate[label]={'episodes':len(these),'necessary_100pct_margin_level_pass_count':sum(x['necessary_margin_level_100pct_pass'] for x in these),
         'necessary_50pct_margin_level_pass_count':sum(x['necessary_margin_level_50pct_pass'] for x in these),
         'ending_at_least_10000_count':sum(x['model_ending_usd']>=10000. for x in these),
         '24h_reached_10000_count':sum(x['24h_target_10000_hit'] for x in these),
         'minimum_tick_equity_across_starts':min(x['min_tick_equity'] for x in these),
         'min_last_mark_usd':min(x['model_ending_usd'] for x in these),
         'max_last_mark_usd':max(x['model_ending_usd'] for x in these),
         'total_trades_across_ten_independent_episodes':sum(x['trades'] for x in these)}
    saved={'id':'GRID0308_INDEPENDENT_BIDASK_10_RANDOM_START_MARGIN_AND_EQUITY_STRESS',
      'status':'RESEARCH_ONLY_LOW_CAPITAL_NOT_CERTIFIED_FOR_COINEXX',
      'source_sha256':source_sha,'seed':SEED,'dates':picked,'sample_count':len(picked),'initial_equity_usd':100.,
      'target_equity_usd':10000.,'test_method':'Ten independently reset $100 accounts, first quote >= UTC sampled trading day start to January last original tick; 24h market-to-market separately; no prior paid ancestors or equity carried',
      'caveats':['Margin leverage 500 is hypothetical; Coinexx dynamic contract/margin schedule and stopout unknown',
         'Margin ratio checks flag a potential broker failure but do not simulate forced liquidation or slippage: necessary, not sufficient survival evidence',
         'Candles and candidate executions inherited from frozen original January research; candidates were historically selected, not production L0-L7 regenerated',
         'For stronger 100% claim one needs all episodes meet real broker stopout and margin rules, after actual independent exit mechanics, without target hindsight, and out-of-sample continuation',
         'No algorithm can guarantee future 100% survival; these ten historical examples are not probabilistic certainty'],
      'aggregate':aggregate,'episodes':entries,'elapsed_s':round(time.time()-st,2)}
    out=ROOT/'grid0308_independent_margin_full_tick_results.json';out.write_text(json.dumps(saved,indent=2))
    print('SAVED',out,'secs',round(time.time()-st,2),flush=True)
if __name__=='__main__':main()
