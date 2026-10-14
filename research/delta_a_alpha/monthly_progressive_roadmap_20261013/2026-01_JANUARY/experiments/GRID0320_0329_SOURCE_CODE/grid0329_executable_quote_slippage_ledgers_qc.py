"""GRID0329 exact independently priced full source-conditional portfolio deal evidence.
Replays 40 account episodes (10 seeded dates * 4 modeled cost scenarios) and
persists each accepted/closed chronological trade with raw quote-side prices,
quote index and timestamps. Verifies independently against all original quotes.
Neither a profit claim about R9 OVERFIT nor a broker stopout certification.
"""
from __future__ import annotations
import json,gzip,hashlib,time
from pathlib import Path
import numpy as np
import grid0328_conservative_source_slippage_stress as p
import grid0315_independent_7day_margin_liquidation_qc as qc
from grid0307_random_start_lowcapital_original_tick import TICK_SOURCE
ROOT=Path(__file__).resolve().parent

def independent_two_phase_hourly(t,bid,ask,z,accepted,closed,initial=100.):
    """Independent intraquote mark: before new admission and after new admission.

    A risk-governed fill must record the equity mark BEFORE placing the new
    position, then record the spread/fee debit AFTER that same-tick fill.
    A once-per-quote after-bookings sampler can underestimate an hourly peak
    by an intraquote entry commission/spread step. This reconciles both marks.
    """
    n=len(t)
    dlo=np.zeros(n+1,np.int32);dsh=np.zeros(n+1,np.int32)
    dbasis=np.zeros(n+1,float);dcash=np.zeros(n+1,float)
    entry_mtm=np.zeros(n,float)
    done={int(j):(int(ix),float(net)) for ix,j,net,_ in closed}
    assert len(done)==len(closed)==len(accepted)
    for j in accepted:
        j=int(j);ei=int(z['entry_idx'][j]);xi,net=done[j]
        direction=int(z['direction'][j]);px=int(z['entry_price_raw'][j])/1000.
        assert px==int(ask[ei] if direction>0 else bid[ei])/1000.
        if direction>0:dlo[ei]+=1;dlo[xi]-=1
        else:dsh[ei]+=1;dsh[xi]-=1
        dbasis[ei]+=direction*px;dbasis[xi]-=direction*px;dcash[xi]+=net
        entry_mtm[ei]+=direction*(int(bid[ei] if direction>0 else ask[ei])/1000.-px)-.20
    lo=np.cumsum(dlo[:-1]);sh=np.cumsum(dsh[:-1]);cash=np.cumsum(dcash[:-1]);basis=np.cumsum(dbasis[:-1]);opened=lo+sh
    post=initial+cash+(lo*bid-sh*ask)/1000.-basis-.20*opened
    pre=post-entry_mtm
    hours=t//3600000;bounds=np.r_[0,np.flatnonzero(np.diff(hours))+1,n]
    worst=0.
    for a,b in zip(bounds[:-1],bounds[1:]):
        two=np.empty(2*(b-a),float);two[0::2]=pre[a:b];two[1::2]=post[a:b]
        d=np.max(np.maximum.accumulate(two)-two)
        if d>worst:worst=float(d)
    return worst

def main():
 started=time.time();saved=json.load(open(ROOT/'grid0328_conservative_slippage_original_tick_results.json'))
 t,bid,ask,z,kind,owner,pgid,r9,origin=p.p.p.cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 _,days=p.p.p.cohort.select_days(r9,t);assert days==saved['days']
 sha=hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest();assert sha=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
 checks=0;count=0;mismatches=[];outrows=[];file=ROOT/'grid0329_full_40_portfolios_original_quote_booked_deal_ledger.ndjson.gz'
 with gzip.open(file,'wt',encoding='utf8',compresslevel=7) as f:
  for d in days:
   day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
   tt=t[lo:hi];b=bid[lo:hi];a=ask[lo:hi]
   mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
   zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
   zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
   keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
   for j in np.flatnonzero(trunc):
    ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
   pre,shock=p.p.p.sim.features(tt,b,a)
   for name,slip in p.POLICIES:
    x=p.p.p.sim.run(tt,b,a,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=.20,stopout_ratio=.5,
       screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,
       screen_sources=p.p.ORD,max_tick_slippage_usd=slip)
    deals=x.pop('booked_ledger');ad=x.pop('accepted_indices')
    y=qc.reconstruct(tt,b,a,zz,ad,deals,slippage_per_close=slip)
    hourly_two_stage=independent_two_phase_hourly(tt,b,a,zz,ad,deals)
    sr=next(k for k in saved['episodes'] if k['date']==d and k['policy']==name)
    for metric,(c,d2) in enumerate([(x['final_cash'],sr['final']),(x['final_cash'],y['close_cash']),
                 (x['min_tick_equity'],y['min_equity']),(x['worst_hour_drawdown'],hourly_two_stage),
                 (x['max_tick_drawdown'],y['max_equity_dd']),
                 (x['trades_closed'],y['closed_trades'])]):
      if abs(c-d2)>=1e-5:
       mismatches.append((d,name,metric,c,d2))
      else: checks+=1
    trade_ledger=[]
    for ix,j,net,reason in deals:
      ei=int(zz['entry_idx'][j]);dr=int(zz['direction'][j]);price=int(zz['entry_price_raw'][j]);closing=int(b[ix] if dr>0 else a[ix]);
      trade_ledger.append(dict(candidate_index=int(j),entry_quote_idx=ei,exit_quote_idx=int(ix),
       original_entry_quote_idx=int(ei+lo),original_exit_quote_idx=int(ix+lo),entry_ms=int(tt[ei]),exit_ms=int(tt[ix]),
       direction=int(dr),source=str(zz['source'][j]),entry_price_usd=price/1000.,
       exit_price_usd=closing/1000.,modeled_net_cash=float(net),reason=reason))
    # keep model evidence and original per-trade ledger; independent QC already validates pricing.
    r=dict(start_day=d,policy=name,slippage_usd_per_close=slip,initial_cash=100.,
      final_cash=x['final_cash'],original_tick_sha256=sha,accepted_count=len(ad),
      booked_count=len(deals),independent_hourly_two_stage_dd=hourly_two_stage,independent_after_booking_only_dd=y['worst_hour_dd'],risk=x['min_tick_equity'],modeled_forced_stopouts=x['forced_events'],
      booked_deals=trade_ledger)
    f.write(json.dumps(r,separators=(',',':'))+'\n');count+=len(deals)
    outrows.append(dict(day=d,name=name,trades=len(deals),net=x['net_cash'],cash=x['final_cash'],min_eq=y['min_equity'],
                        worst_hour=y['worst_hour_dd'],forced=x['forced_events']))
   print('Full source exact ledger independently certified',d,round(time.time()-started,2),flush=True)
 print('MISMATCHES',mismatches,flush=True);assert len(outrows)==40
 out=dict(id='GRID0329_INDEPENDENT_QUOTE_AND_LEDGER_PARITY_FOR_40_PORTFOLIOS',mismatches=mismatches,status='UNPROMOTED',
     source_sha256=sha,quote_rows=len(t),sampled_dates=days,assertions=checks,portfolios=40,total_closed_deals=count,
     exact_full_deals_file=file.name,records=outrows,
     broker_unverified=['leverage 500, margin stopout, slippage fill model, request-time state, hedging rules'],
     parent_candidate_not_endogenous=True,r9_overfit_offline_per_trade_scores='NOT_YET_AVAILABLE',elapsed_s=time.time()-started)
 dest=ROOT/'grid0329_source_quote_independent_qc_summary.json';dest.write_text(json.dumps(out,indent=2))
 print('GRID0329',checks,'INDEPENDENT CHECKS PASS',count,'MODELED BOOKINGS',flush=True)
if __name__=='__main__':main()
