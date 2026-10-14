"""GRID0300 causal intra-UTC-hour tick equity gate for January source family.

RESEARCH ONLY. Reuses ORIGINAL byte-identical GRID0296 source and original
Dukascopy Bid/Ask; no R9 teacher/date-based permission, no martingale.
This is a *new-entry* hourly equity stop; existing positions close under
preserved causal quote-side trade exits. No claim that an entry stop
can enforce a hard DD limit against already-open inventory. The independent
back.replay evaluates the finally accepted funded ledger all 9,135,062 ticks.
"""
from __future__ import annotations
import json,time,heapq
from pathlib import Path
from collections import deque,Counter
import numpy as np,pandas as pd
from numba import njit
import grid0296_parent_earned_exposure as base

ROOT=Path(__file__).resolve().parent
HOUR=3600000

@njit(cache=True)
def scan_hourly(t,bid,ask,low,high,bal,nlong,nshort,basis,opens,first_hour,peaks,drawdowns,locks,threshold,active):
    """Chronological original executable quotes, book held static between events.
    Mark post-close book at the original exit tick, and post-fill at entry tick.
    A lock can only depend on already-observed quote/position state.
    """
    for i in range(low,high+1):
        hh=int(t[i]//HOUR)-first_hour
        eq=bal+(nlong*float(bid[i])-nshort*float(ask[i]))/1000.-basis-0.20*opens
        if active[hh]==0:
            peaks[hh]=eq;active[hh]=1
        elif eq>peaks[hh]:peaks[hh]=eq
        dd=peaks[hh]-eq
        if dd>drawdowns[hh]:drawdowns[hh]=dd
        if threshold>0.0 and drawdowns[hh]>=threshold:locks[hh]=1

source=base.SOURCE

def patch_one(old,new):
    global source
    n=source.count(old)
    if n!=1:raise AssertionError('expected exactly one source target; count '+str(n)+' for '+str(old[:70]))
    source=source.replace(old,new)

patch_one('parent_edge=0.0):','parent_edge=0.0,hourly_entry_lock_usd=0.0,hourly_soft_parent_usd=0.0,hourly_soft_parent_cap=16):')
patch_one('source_losses={};source_pause_until={};pause_count=0;live_by_source={}', '''source_losses={};source_pause_until={};pause_count=0;live_by_source={}
    FIRST_HOUR=int(t[0]//HOUR);N_HOURS=int(t[-1]//HOUR)-FIRST_HOUR+1
    hour_peak=np.zeros(N_HOURS,np.float64);hour_drawdown=np.zeros(N_HOURS,np.float64)
    hour_lock=np.zeros(N_HOURS,np.int8);hour_active=np.zeros(N_HOURS,np.int8)
    mark_cursor=-1;hourly_block_count=0;soft_parent_reject=0''')
patch_one('            _,prio,j=heapq.heappop(live);d0=int(D[j]);r0=int(R[j])/1000.;net=float(P[j]);balance+=net', '''            close_idx=int(live[0][0])
            if close_idx>mark_cursor+1:
                scan_hourly(t,bid,ask,mark_cursor+1,close_idx-1,balance,netlong,netshort,signed_basis,len(live),FIRST_HOUR,hour_peak,hour_drawdown,hour_lock,hourly_entry_lock_usd,hour_active)
            mark_cursor=max(mark_cursor,close_idx-1)
            _,prio,j=heapq.heappop(live);d0=int(D[j]);r0=int(R[j])/1000.;net=float(P[j]);balance+=net''')
patch_one('        # First gate is allowed for a scout, then only four already actually paid', '''        if ei>mark_cursor:
            scan_hourly(t,bid,ask,mark_cursor+1,ei,balance,netlong,netshort,signed_basis,len(live),FIRST_HOUR,hour_peak,hour_drawdown,hour_lock,hourly_entry_lock_usd,hour_active)
            mark_cursor=ei
        # First gate is allowed for a scout, then only four already actually paid''')
patch_one('        if ei==prev_fill:', '''        hour_index=int(current//HOUR)-FIRST_HOUR
        if hour_lock[hour_index]!=0:
            ledger_events['tick_level_hourly_equity_lock']+=1;hourly_block_count+=1;continue
        if ei==prev_fill:''')
patch_one('        if typ==1 and permitted_parent_cap and parent_live>=permitted_parent_cap:', '''        if typ==1 and hourly_soft_parent_usd>0 and hour_drawdown[hour_index]>=hourly_soft_parent_usd:
            permitted_parent_cap=min(permitted_parent_cap,hourly_soft_parent_cap)
            if permitted_parent_cap and parent_live>=permitted_parent_cap:soft_parent_reject+=1
        if typ==1 and permitted_parent_cap and parent_live>=permitted_parent_cap:''')
patch_one('        peak_live=max(peak_live,len(live))', '''        peak_live=max(peak_live,len(live))
        # Bid/Ask spread + modeled cash round-trip cost apply immediately after fill.
        scan_hourly(t,bid,ask,ei,ei,balance,netlong,netshort,signed_basis,len(live),FIRST_HOUR,hour_peak,hour_drawdown,hour_lock,hourly_entry_lock_usd,hour_active)''')
patch_one('    idx=np.asarray(accepted,np.int64)', '''    # Mark remaining held inventory and its *actual* scheduled close ticks, followed
    # by the final original month quote. No signal or comparison uses future data.
    while live:
        close_idx=int(live[0][0])
        if close_idx>mark_cursor+1:
            scan_hourly(t,bid,ask,mark_cursor+1,close_idx-1,balance,netlong,netshort,signed_basis,len(live),FIRST_HOUR,hour_peak,hour_drawdown,hour_lock,hourly_entry_lock_usd,hour_active)
        mark_cursor=max(mark_cursor,close_idx-1)
        while live and live[0][0]==close_idx:
            _,prio,j=heapq.heappop(live);d0=int(D[j]);r0=int(R[j])/1000.;net=float(P[j]);balance+=net
            used_margin-=r0/500.;signed_basis-=d0*r0
            if d0>0:netlong-=1
            else:netshort-=1
            if kind[j]==1:parent_live-=1
            if kind[j]==2:child_live-=1
            if kind[j]==0:
                close_source=str(z['source'][j]);live_by_source[close_source]=live_by_source.get(close_source,0)-1
        if mark_cursor<close_idx:
            scan_hourly(t,bid,ask,close_idx,close_idx,balance,netlong,netshort,signed_basis,len(live),FIRST_HOUR,hour_peak,hour_drawdown,hour_lock,hourly_entry_lock_usd,hour_active)
            mark_cursor=close_idx
    if mark_cursor<len(t)-1:
        scan_hourly(t,bid,ask,mark_cursor+1,len(t)-1,balance,netlong,netshort,signed_basis,0,FIRST_HOUR,hour_peak,hour_drawdown,hour_lock,hourly_entry_lock_usd,hour_active)
    idx=np.asarray(accepted,np.int64)''')
patch_one('    return r', '''    active_drawdown=hour_drawdown[hour_active==1]
    raw_days=pd.to_datetime((np.arange(N_HOURS)+FIRST_HOUR)*HOUR,unit='ms',utc=True).strftime('%Y-%m-%d')
    worst_day_hour={}
    for di,hval in zip(raw_days,hour_drawdown):
        worst_day_hour[di]=max(float(hval),worst_day_hour.get(di,0.0))
    r.update(hourly_entry_lock_usd=hourly_entry_lock_usd,hourly_soft_parent_usd=hourly_soft_parent_usd,
        hourly_soft_parent_cap=hourly_soft_parent_cap,online_hourly_blocks=hourly_block_count,
        online_soft_parent_trips=soft_parent_reject,hours_locked=int(np.count_nonzero(hour_lock)),
        max_hourly_tick_equity_drawdown_usd=float(np.max(active_drawdown)) if len(active_drawdown) else 0.,
        p95_hourly_tick_equity_drawdown_usd=float(np.percentile(active_drawdown,95)) if len(active_drawdown) else 0.,
        p99_hourly_tick_equity_drawdown_usd=float(np.percentile(active_drawdown,99)) if len(active_drawdown) else 0.,
        daily_worst_hourly_drawdown_usd=worst_day_hour,
        hourly_metric='UTC-hour-reset tick-level peak-minus-equity; original quote-side floating marks after observed closes/fills')
    return r''')

ns={'np':np,'pd':pd,'deque':deque,'Counter':Counter,'heapq':heapq,'back':base.p.ancestor.base.back,'json':json,'Path':Path,'ROOT':base.p.ancestor.base.ROOT,'time':time,'HOUR':HOUR,'scan_hourly':scan_hourly}
exec(source,ns)
physical_replay=ns['physical_replay']

def run(t,bid,ask,z,kind,owner,pgid,r9, name, lock,soft=0.,softcap=16):
    t0=time.perf_counter()
    r=physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,
        loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,
        earned_wins=7,earned_window=10,earned_edge=12,parent_cap=16,
        earned_parent_cap=192,parent_wins=4,parent_window=6,parent_edge=4,
        hourly_entry_lock_usd=lock,hourly_soft_parent_usd=soft,hourly_soft_parent_cap=softcap)
    r['name']=name;r['elapsed_seconds']=time.perf_counter()-t0
    return r

def main():
    start=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=base.p.ancestor.base.materialize()
    print('GRID0300 original source recovered',len(t),'quotes;',len(z['entry_idx']),'candidates',origin,flush=True)
    variants=[('EXACT_GRID0297_PARENT192_BASE',0.,0.,16),
              ('HOUR_LOCK_150',150.,0.,16),('HOUR_LOCK_300',300.,0.,16),
              ('HOUR_LOCK_600',600.,0.,16),('HOUR_SOFT_PARENT_150',0.,150.,16),
              ('HOUR_SOFT_PARENT_300',0.,300.,16),
              ('HOUR_COMBINED_SOFT150_LOCK600',600.,150.,16),
              ('HOUR_COMBINED_SOFT300_LOCK900',900.,300.,32)]
    outputs=[]
    for name,lock,soft,softcap in variants:
        r=run(t,bid,ask,z,kind,owner,pgid,r9,name,lock,soft,softcap)
        outputs.append(r)
        print(name,'net',round(r['net'],2),'N',r['trades'],'grossloss',round(r['gross_loss'],2),
            'fullDD',round(r['max_all_tick_floating_equity_dd'],2),'maxHourDD',round(r['max_hourly_tick_equity_drawdown_usd'],2),
            'p95HourDD',round(r['p95_hourly_tick_equity_drawdown_usd'],2),
            'positive',sum(d['net']>0 for d in r['daily'].values()),sum(d['net']>0 for d in r['weekly'].values()),
            'R9targets',r['r9_synth_days_net_met'],r['r9_synth_weeks_net_met'],
            'blocks',r['online_hourly_blocks'], 'secs',round(r['elapsed_seconds'],1),flush=True)
    out=ROOT/'grid0300_hourly_equity_governor_jan_results.json'
    out.write_text(json.dumps({'id':'GRID0300_JAN_QUOTE_HOURLY_MARK_TO_MARKET_RESTRICTED_ENTRY_RESEARCH',
        'source_sha256':base.p.ancestor.base.back.SRC_SHA,
        'status':'RESEARCH_ONLY_NOT_ACCEPTED','baseline_source':'GRID0297_PARENT192_4of6_4',
        'cautions':['Existing positions are not liquidated by a new-entry lock. Hard DD threshold may be overshot.',
                    'Hypothetical 100K account, not suitable for 100-300 bankroll without independent survival tests.',
                    'Original candidate opportunity universe inherited historical selection, not fully endogenous V1.'],
        'variants':outputs,'seconds_total':time.perf_counter()-start},indent=2))
    print('SAVED',out,'seconds',round(time.perf_counter()-start,1))
if __name__=='__main__':main()
