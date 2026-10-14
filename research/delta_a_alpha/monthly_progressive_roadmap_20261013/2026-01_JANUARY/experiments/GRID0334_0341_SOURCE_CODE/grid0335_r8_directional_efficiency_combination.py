"""GRID0335: Independent R8 5-completed-second path-efficiency + as-of source routing.
UNPROMOTED hypothesis test. Original MQL5 R8 lookback from Git blob 6b246...
Original Dukascopy bid/ask; no R8 tester prices, no historical R8 deal times as signals.
The parent candidate population is historically selected GRID0283: NOT a new endogenous producer.
"""
from __future__ import annotations
import sys,json,time,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,'/mnt/data/jan_work/engine')
import grid0324_source_conditioned_pre_request_routing as sim
import grid0313_seven_day_ten_start_stopout_frontier as cohort
from grid0330_initial_capacity_survival_sweep import ALL_ORD
DAY=86400000


def r8_asof_micro(t,bid,ask,entry_idx):
    """For each candidate entry, only original quotes observed >=1s BEFORE entry.
    Replicate R8 MicroVelocity's 5 last completed Bid-second CLOSES + current Bid.
    Unfilled seconds are NOT invented; current second is omitted.
    """
    E=np.asarray(entry_idx,dtype=np.int64)
    pre=np.maximum(0,np.searchsorted(t,t[E]-1000,side='right')-1)
    sec=t//1000
    changes=np.flatnonzero(np.diff(sec)!=0)
    ends=np.r_[changes,len(t)-1]
    uniq=sec[ends]
    k=np.searchsorted(uniq,sec[pre],side='left')-1
    valid=k>=4
    k=np.maximum(k,4)
    close_bid=np.asarray(bid[ends],dtype=np.float64)*.001
    current=np.asarray(bid[pre],dtype=np.float64)*.001
    p0=close_bid[k-4];p1=close_bid[k-3];p2=close_bid[k-2];p3=close_bid[k-1];p4=close_bid[k]
    disp=current-p0
    travel=np.abs(p1-p0)+np.abs(p2-p1)+np.abs(p3-p2)+np.abs(p4-p3)+np.abs(current-p4)
    eff=np.where(valid,np.abs(disp)/(travel+1.e-9),0.)
    assert np.all(eff>=0) and np.all(eff<=1.00000001)
    assert np.all(t[pre]<=t[E]-1000) or np.all(E[t[pre]>t[E]-1000]==0)
    return pre,disp,eff

def prepare_window(t,bid,ask,z,kinds,owner,hi):
    """Preserve original absolute chronology of candidate source. Reprice truncation at last quote."""
    mask=(z['entry_idx']>=0)&(z['entry_idx']<hi)
    zz={k:v[mask].copy() for k,v in z.items()};kk=kinds[mask];oo=owner[mask]
    truncated=zz['exit_idx']>=hi
    zz['exit_idx']=np.minimum(zz['exit_idx'],hi-1)
    keep=zz['entry_idx']<zz['exit_idx']
    zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];truncated=truncated[keep]
    for j in np.flatnonzero(truncated):
        ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);
        zz['net_cash'][j]=dr*(int(bid[ix] if dr>0 else ask[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
    return zz,kk,oo


def one_policy(t,bid,ask,zz,kk,oo,pgid,pre,shock,eff,disp,mode):
    keep=np.ones(len(kk),dtype=bool)
    ordinary=(kk==0)&np.isin(zz['source'],list(ALL_ORD))
    if mode in ('EFF30','EFF60','R8_DIR30','R8_DIR60','R8_DIR30_ONE'):
        threshold=.6 if '60' in mode else .3
        keep[ordinary] &= eff[ordinary]>=threshold
        if mode.startswith('R8_DIR'):
            dr=zz['direction'].astype(np.int8)
            keep[ordinary] &= disp[ordinary]*dr[ordinary]>0.
    # Leave original parent/child records and their unmodified owner IDs intact.
    zf={key:v[keep] for key,v in zz.items()};kf=kk[keep];of=oo[keep]
    cap=mode=='R8_ONE' or mode=='R8_DIR30_ONE'
    tiers=((100.,1),(150.,2),(300.,4),(500.,8),(1000.,16),(2000.,64)) if cap else ((100.,2),(150.,4),(300.,8),(500.,16),(1000.,32),(2000.,64))
    return sim.run(t,bid,ask,zf,kf,of,pgid,cash=100.,initial_cap=1 if cap else 2,earned_cash_tiers=tiers,
                   admission_margin_fraction=.20,stopout_ratio=.5,
                   screen_quote_idx=pre,pre_request_shock_5s=shock,
                   min_observed_5s_shock=.5,screen_sources=ALL_ORD),int(np.sum(ordinary &~keep)),len(zf)

def main():
  start=time.time();P=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH');Z=ROOT/'original_research_candidate_unfiltered_cache.npz'
  t=np.load(P/'ticks_t.npy',mmap_mode='r');bid=np.load(P/'ticks_bid.npy',mmap_mode='r');ask=np.load(P/'ticks_ask.npy',mmap_mode='r')
  with np.load(Z) as q:
   keys=('entry_idx','exit_idx','entry_price_raw','direction','net_cash','source')
   z={name:q[name] for name in keys};kind=q['kind'];owner=q['owner'];pgid=q['pgid']
  r9=json.loads(Path('/mnt/data/jan_recovery_20261013/ORIGINAL/r9_synth_jan_daily_weekly.json').read_text())
  eligible,days=cohort.select_days(r9,t)
  policies=['CONTROL','R8_ONE','EFF30','EFF60','R8_DIR30','R8_DIR60','R8_DIR30_ONE']
  rows=[]
  for day in days:
    ds=int(np.datetime64(day+'T00:00:00','ms').astype('int64'));lo=int(np.searchsorted(t,ds));hi=int(np.searchsorted(t,ds+7*DAY))
    tt=np.asarray(t[lo:hi]);b=np.asarray(bid[lo:hi]);a=np.asarray(ask[lo:hi])
    mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
    sub={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
    sub['entry_idx']-=lo; truncated=sub['exit_idx']>=hi;sub['exit_idx']=np.minimum(sub['exit_idx']-lo,hi-lo-1)
    valid=sub['entry_idx']<sub['exit_idx'];sub={k:v[valid] for k,v in sub.items()};kk=kk[valid];oo=oo[valid];truncated=truncated[valid]
    for j in np.flatnonzero(truncated):
        ix=int(sub['exit_idx'][j]);dr=int(sub['direction'][j]);sub['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(sub['entry_price_raw'][j]))/1000.-.20
    pre,shock=sim.features(tt,b,a)
    qidx,disp,eff=r8_asof_micro(tt,b,a,sub['entry_idx'])
    # R8 original MQL5 directional efficiency compared with 5 completed second closes.
    src_ord=(kk==0)&np.isin(sub['source'],list(ALL_ORD))
    for policy in policies:
        result,removed,offered=one_policy(tt,b,a,sub,kk,oo,pgid,pre,shock,eff,disp,policy)
        booked=result.pop('booked_ledger');accepted=result.pop('accepted_indices')
        record={key:result[key] for key in ['final_cash','trades_closed','min_tick_equity','max_tick_drawdown','worst_hour_drawdown','forced_events','min_margin_ratio_observed','peak_open','net_cash']}
        record.update(date=day,policy=policy,r8_prefilter_removed=removed,r8_candidates=offered,modeled_10000=bool(result['final_cash']>=10000.),positive=bool(result['final_cash']>100.),nonruin=bool(result['min_tick_equity']>0),no_stopout=bool(result['forced_events']==0))
        rows.append(record)
        print('DONE',day,policy,'net',round(result['net_cash'],2),'trades',result['trades_closed'],'worst_hour',round(result['worst_hour_drawdown'],2),'removed',removed,'time',round(time.time()-start,1),flush=True)
  summary={}
  for p in policies:
    xs=[x for x in rows if x['policy']==p]
    summary[p]={'10_starts':len(xs),'no_stopout':sum(x['no_stopout'] for x in xs),'nonruin':sum(x['nonruin'] for x in xs),'positive':sum(x['positive'] for x in xs),'10000_7day':sum(x['modeled_10000'] for x in xs),'final_min':min(x['final_cash'] for x in xs),'final_max':max(x['final_cash'] for x in xs),'trades':sum(x['trades_closed'] for x in xs),'worst_hour_dd':max(x['worst_hour_drawdown'] for x in xs),'max_tick_dd':max(x['max_tick_drawdown'] for x in xs)}
  report={'status':'UNPROMOTED_IN_SAMPLE_HISTORICAL_CANDIDATE_SOURCE','seed':cohort.SEED,'date_cohort':days,'source_r8_git_blob':'6b2460074ed35d04cb9b4f7620194a483df17c2a','spine':'preserved GRID0324 source conditional admission & GRID0312 physically booked stopout','limitations':['Candidate universe and scheduled exits were preselected during January in-sample research, not runtime endogenous','As-of feature is one-second before inherited fill; original request time is not available','1oz per 0.01 lot and 500x leverage assumed, not Coinexx verified','Ten historical samples overlap; 10/10 is not future account survival guarantee','R8 filter tests are merely confluence hypotheses, not reproductions of R8 over source-generated entries'], 'summary':summary,'episodes':rows,'seconds':round(time.time()-start,2)}
  (ROOT/'grid0335_r8_efficiency_source_confluence_results.json').write_text(json.dumps(report,indent=2))
  print('SUMMARY',json.dumps(summary),flush=True)
if __name__=='__main__':main()
