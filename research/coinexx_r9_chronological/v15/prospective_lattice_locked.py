"""V15 RESEARCH ONLY: prospective clean continuation and sweep/reclaim.
Consumes original, SHA-verified Coinexx quotes. Signal observed only on a
completed S5 bar; entry at NEXT source quote after its completion becomes
observable. No prior V9 event membership, no winner labels, no passive fills.
One position, exact original source ordinal/quote-side first passage.
Original files are read only, no market data copied or transformed on disk.
"""
from __future__ import annotations
import hashlib,sys,time,json,os,csv,gzip
from dataclasses import dataclass,asdict
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get('COINEXX_DATA_ROOT','/mnt/data'))
OUT=Path(os.environ.get('V15_OUT_DIR',str(HERE)))
OUT.mkdir(parents=True,exist_ok=True)
SOURCE_DIR=HERE.parent/'cfael_v13'
if not (SOURCE_DIR/'research.py').exists():
    SOURCE_DIR=Path('/mnt/data/cfael_v13')
if not (SOURCE_DIR/'research.py').exists():
    raise RuntimeError('Pinned V13 original-source Tape research dependency missing')
sys.path.insert(0,str(SOURCE_DIR))
from research import Tape,SHA_2026

@dataclass(frozen=True)
class Mechanism:
    name:str
    family:str
    target_cash:float=1.5
    stop_c:int=150
    hold_ms:int=120000
    require_parent:bool=True
    fib:float=.382
    min_reclaim_c:int=12
    min_sweep_c:int=15
    max_spread_c:int=25
    min_room_c:int=120
    max_hold_quote_gap_ms:int=2500
    anchor_180s_max_premium_c:int|None=None
    structural_stop:bool=False
    min_stop_c:int=35
    max_stop_c:int=150
    min_completed_5s_range_c:int=0
    wait_confirm_ms:int=0

RULES=(
    Mechanism('C_fib382_costcovered','C',target_cash=1.5,stop_c=150),
    Mechanism('R2_two_sided_stop_run_reclaim','R2',target_cash=1.5,stop_c=150,require_parent=False),
    Mechanism('S_verified_breakout_cascade','S',target_cash=2.0,stop_c=150,hold_ms=180000),
    Mechanism('C_reclaim_250ms_quote_confirmation','C',target_cash=1.5,stop_c=150,wait_confirm_ms=250),
    Mechanism('R2_reversal_250ms_quote_confirmation','R2',target_cash=1.5,stop_c=150,require_parent=False,wait_confirm_ms=250),
)

def candidate_setup(tape:Tape):
    ms=tape.ms;mid=tape.mid
    bucket=ms//5000
    starts=np.r_[0,np.flatnonzero(np.diff(bucket)!=0)+1]
    ends=np.r_[starts[1:]-1,len(ms)-1]
    high=np.maximum.reduceat(mid,starts)
    low=np.minimum.reduceat(mid,starts)
    close=mid[ends]
    maxima=np.maximum.reduceat(np.diff(ms,prepend=ms[0]),starts)
    prior_hi=pd.Series(high).shift(1).rolling(36,min_periods=24).max().to_numpy()
    prior_lo=pd.Series(low).shift(1).rolling(36,min_periods=24).min().to_numpy()
    max_start=np.maximum(0,np.arange(len(starts))-36)
    bar_buckets=bucket[starts]
    valid_span=bar_buckets-bar_buckets[max_start] <= 42
    m1=tape.bars['M1'];m5=tape.bars['M5']
    available_ms=ms[starts[1:]]
    mi=np.searchsorted(m1['available'],available_ms,side='right')-1
    m5i=np.searchsorted(m5['available'],available_ms,side='right')-1
    m1_clipped=np.clip(mi,0,len(m1['EMA20'])-1)
    m5_clipped=np.clip(m5i,0,len(m5['SMA20'])-1)
    trend=np.zeros(len(available_ms),dtype=np.int8)
    mature=(mi>=25)&(m5i>=24)
    ema=m1['EMA20'];sma=m5['SMA20']
    ema2=ema[np.maximum(0,m1_clipped-2)]
    ema_delta=ema[m1_clipped]-ema2
    sma_delta=sma[m5_clipped]-sma[np.maximum(0,m5_clipped-2)]
    s=np.sign(ema_delta)
    trend=np.where(mature & (np.abs(ema_delta)>=8), s, 0).astype(np.int8)
    # M5 SMA is an available structural context; never use current unclosed bar.
    parent=np.where(mature, np.sign(sma_delta), 0).astype(np.int8)
    candidate_indices=np.arange(len(available_ms))
    return dict(ms=ms,mid=mid,starts=starts,ends=ends,bucket=bar_buckets,low=low,high=high,close=close,
        prior_hi=prior_hi,prior_lo=prior_lo,maxima=maxima,valid_span=valid_span,
        signal_indices=candidate_indices,available_ms=available_ms,trend=trend,parent=parent,
        m1i=mi,m5i=m5i)

def candidate_events(tape,pre,rule):
    ms=tape.ms
    # Bar k is completed at first new-bucket quote starts[k+1].
    k=np.arange(len(pre['available_ms']))
    p_hi=pre['prior_hi'][:-1];p_lo=pre['prior_lo'][:-1]
    span=p_hi-p_lo
    side=pre['trend']
    close=pre['close'][:-1]; b_lo=pre['low'][:-1];b_hi=pre['high'][:-1]
    if rule.family=='S':
        # The alternative to a rejection: a pre-existing range was broken
        # and the completed 5s bar closed near the extreme, consistent with
        # an observed quote-driven stop cascade, NOT proven true stop orders.
        up=(close>=p_hi+25)&((b_hi-close)<=.25*np.maximum(1,b_hi-b_lo))
        dn=(close<=p_lo-25)&((close-b_lo)<=.25*np.maximum(1,b_hi-b_lo))
        side=np.where(up&~dn,1,np.where(dn&~up,-1,0)).astype(np.int8)
        rail=np.where(side>0,p_hi,p_lo)
        ok=(side!=0)&((b_hi-b_lo)>=45)
    elif rule.family=='R2':
        # An independently observed rejection determines direction; the
        # original M1 EMA sign is context only, not a direction oracle.
        sweep_lo=(b_lo<=p_lo-rule.min_sweep_c)&(close>=p_lo+rule.min_reclaim_c)
        sweep_hi=(b_hi>=p_hi+rule.min_sweep_c)&(close<=p_hi-rule.min_reclaim_c)
        side=np.where(sweep_lo & ~sweep_hi,1,np.where(sweep_hi & ~sweep_lo,-1,0)).astype(np.int8)
        rail=np.where(side>0,p_lo,p_hi)
        ok=(side!=0)  # Past observed bar has fully closed.
    elif rule.family=='C':
        rail=np.where(side>0,p_hi-rule.fib*span,p_lo+rule.fib*span)
        # Observed dip into a confirmed historical retracement rail, then closed back across it.
        touched=np.where(side>0,b_lo<=rail-4,b_hi>=rail+4)
        reclaimed=side*(close-rail)>=rule.min_reclaim_c
        close_far=side*(close-rail)<=130
        ok=touched & reclaimed & close_far
    else:
        rail=np.where(side>0,p_lo,p_hi)
        touched=np.where(side>0,b_lo<=rail-rule.min_sweep_c,b_hi>=rail+rule.min_sweep_c)
        reclaimed=side*(close-rail)>=rule.min_reclaim_c
        close_far=side*(close-rail)<=160
        ok=touched & reclaimed & close_far
    # Confirmed/trade timestamp at FIRST quote of next 5s bucket; do not
    # use forward bar information. Quote at signal availability isn't fillable
    # for this research: fill at the subsequent original record.
    signal_tick=pre['starts'][1:]
    fill=signal_tick+1
    validfill=fill<len(tape.ms)
    fill=np.minimum(fill,len(tape.ms)-1)
    signal_time=tape.ms[signal_tick]
    delay=tape.ms[fill]-signal_time
    spread=tape.ask[fill]-tape.bid[fill]
    side=side.astype(np.int8)
    execution=np.where(side>0,tape.ask[fill],tape.bid[fill])
    target_geo=np.where(side>0,p_hi-execution,execution-p_lo)
    if rule.family=='S':
        # In continuation the opposite side of the old range is NOT a
        # forward-profit target. Require a known swing width for payoff room.
        target_geo=span-100
    # For R, the opposite 3-min extreme is the potential range return target.
    # For C, the historical high/low bounds the continuation target.
    trailing=np.r_[True,np.diff(pre['bucket'])[:-1]==1]
    # At the FIRST quote of the next bar, its future max gap is unknown.
    # Only check completed bar history and the already-observed last-to-first gap.
    crossing_gap=ms[signal_tick]-ms[pre['ends'][:-1]]
    clean=(pre['maxima'][:-1]<=rule.max_hold_quote_gap_ms)&(crossing_gap<=rule.max_hold_quote_gap_ms)
    signalokay=(pre['valid_span'][:-1] & (span>=120)&(span<=3500) &
       ((b_hi-b_lo)>=rule.min_completed_5s_range_c) &
       (delay<=1500)&(tape.ms[fill]-tape.ms[signal_tick]<=1500) & validfill &
       (spread>=0)&(spread<=rule.max_spread_c)&(target_geo>=rule.min_room_c)&
       (side!=0)&trailing&clean)
    if rule.require_parent:
        signalokay &= pre['parent']*side>0
    # Quote-duration anchor is formed from *elapsed time* on source-ordered
    # historical midquotes, not from tick counts or unobserved trade volume.
    if rule.anchor_180s_max_premium_c is not None:
        anchor_end=signal_tick
        anchor_start=np.searchsorted(ms,signal_time-180000,side='left')
        denom=tape.total_weight[anchor_end]-tape.total_weight[anchor_start]
        anchor=np.divide(tape.total_quote_value[anchor_end]-tape.total_quote_value[anchor_start],
                         denom,out=np.full(len(denom),np.nan),where=denom>30000)
        price_mid=tape.mid[fill]
        premium=side*(price_mid-anchor)
        signalokay &= np.isfinite(anchor)&(premium<=rule.anchor_180s_max_premium_c)&(premium>=-350)
    if rule.structural_stop:
        stop_boundary=np.where(side>0,b_lo-10,b_hi+10)
        liq_entry=np.where(side>0,tape.bid[fill],tape.ask[fill])
        adaptive_stop=side*(liq_entry-stop_boundary)
        signalokay &= (adaptive_stop>=rule.min_stop_c)&(adaptive_stop<=rule.max_stop_c)
    else:
        adaptive_stop=np.full(len(side),rule.stop_c,dtype=float)
    mask=ok&signalokay
    inds=k[mask]
    selected_fill=fill[mask]; selected_side=side[mask]
    selected_rail=np.asarray(rail)[mask]; selected_stop=adaptive_stop[mask]
    if rule.wait_confirm_ms:
        # Wait for the entire 250 ms landmark *before* a hypothetical order.
        # A favorable event and no adverse first 10c event are known only
        # at that landmark. Use the first quote AFTER it for execution.
        keep_fill=[];keep_side=[];keep_rail=[];keep_stop=[]
        for start_fill,di,r,sd in zip(selected_fill,selected_side,selected_rail,selected_stop):
            t0=int(ms[start_fill]);milestone=t0+rule.wait_confirm_ms
            obs_end=int(np.searchsorted(ms,milestone,side='left'))
            after=obs_end+1
            if after>=len(ms) or ms[obs_end]-milestone>1500 or ms[after]-ms[obs_end]>2500:continue
            q=(tape.bid if di>0 else tape.ask)
            path=q[start_fill:obs_end+1]
            if not len(path):continue
            delta=di*(path.astype(np.int32)-int(q[start_fill]))
            if int(np.max(delta))<10 or int(np.min(delta))<=-10:continue
            ask_price=tape.ask[after] if di>0 else tape.bid[after]
            if tape.ask[after]-tape.bid[after]>rule.max_spread_c:continue
            if rule.family!='S':
                kk=int(np.searchsorted(pre['starts'],start_fill,side='right')-2)
                if kk<0:continue
                # The very same frozen previous structure must still offer
                # prospective payoff room after the delay.
                target_prior=p_hi[kk] if di>0 else p_lo[kk]
                if di*(target_prior-ask_price)<rule.min_room_c:continue
            keep_fill.append(after);keep_side.append(di);keep_rail.append(r);keep_stop.append(sd)
        selected_fill=np.array(keep_fill,dtype=np.int64)
        selected_side=np.array(keep_side,dtype=np.int8)
        selected_rail=np.array(keep_rail,dtype=float)
        selected_stop=np.array(keep_stop,dtype=float)
    return selected_fill, selected_side, selected_rail,selected_stop, {'potential':int(mask.sum()),'raw_pattern':int(ok.sum()), 'microtrend_ready':int(np.count_nonzero(side))}

def execute(tape,entry_idx,side,rule,stop_override=None):
    ms=tape.ms;bi=tape.bid;as_=tape.ask
    start=ms[entry_idx]
    execution=int(as_[entry_idx] if side>0 else bi[entry_idx]);initial_liq=int(bi[entry_idx] if side>0 else as_[entry_idx])
    end=int(np.searchsorted(ms,start+rule.hold_ms,side='right'))
    if end<=entry_idx+1:return None
    exit_liq=(bi[entry_idx+1:end] if side>0 else as_[entry_idx+1:end]).astype(np.int32)
    cash=side*(exit_liq-execution)/100.-.20
    stop_c=(float(stop_override) if stop_override is not None else rule.stop_c)
    adverse=side*(exit_liq-initial_liq)<=-stop_c
    target=cash>=rule.target_cash
    dt=np.diff(ms[entry_idx:end])
    gap=dt>rule.max_hold_quote_gap_ms
    where=np.flatnonzero(adverse|target|gap)
    if len(where):
        row=int(where[0]);j=entry_idx+1+row
        reason='GAP' if gap[row] else ('STOP' if adverse[row] else 'TARGET')
    else:
        j=end-1;row=j-entry_idx-1;reason='TIME'
    return (j,float(round(float(cash[row]),4)),reason,int(start),int(ms[j]),int(execution),int(exit_liq[row]))

def backtest_month(month:str,rules=RULES,source_dir=ROOT):
    path=Path(source_dir)/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
    with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    assert sha==SHA_2026[month],f'Wrong original Coinexx source {month}'
    t0=time.monotonic();tape=Tape(path);pre=candidate_setup(tape)
    tape._bar(900000,'M15')  # completed M15 only; diagnostics never gate trading
    m15=tape.bars['M15']
    m15_ema=pd.Series(m15['close']).ewm(span=20,adjust=False).mean().to_numpy()
    results={}
    for rule in rules:
        fills,sides,rails,stops,counters=candidate_events(tape,pre,rule)
        last_exit=-1;last_ms=-10**18;minute_counts={};logs=[]
        for index,side,rail,stop_dist in zip(fills,sides,rails,stops):
            ms=int(tape.ms[index]); minute=ms//60000
            if index<=last_exit or ms-last_ms<1500 or minute_counts.get(minute,0)>=4:continue
            x=execute(tape,int(index),int(side),rule,float(stop_dist))
            if x is None:continue
            j,net,reason,t_entry,t_exit,ex,liquid=x
            last_exit=j;last_ms=t_exit
            minute_counts[minute]=minute_counts.get(minute,0)+1
            logs.append((t_entry,t_exit,int(side),net,reason,int(index)+1,int(j)+1,int(rail),ex,liquid,float(stop_dist)))
        nets=np.array([a[3] for a in logs],dtype=float)
        eq=np.r_[0,np.cumsum(nets)]
        dd=float(np.max(np.maximum.accumulate(eq)-eq)) if len(nets) else 0
        events_name=None
        if rule.name in ('C_fib382_costcovered', 'R2_two_sided_stop_run_reclaim','S_verified_breakout_cascade', 'C_reclaim_250ms_quote_confirmation', 'R2_reversal_250ms_quote_confirmation'):
            events_name=f'V15_{month}_{rule.name}_all_events.csv.gz'
            path_out=OUT/events_name
            fields=('entry_time_msc','exit_time_msc','side','modeled_net_cash','exit_reason',
                    'entry_ordinal','exit_ordinal','rail_c','entry_exec_c','exit_liquid_c',
                    'stop_dist_c','entry_spread_c','completed_5s_quotes','completed_5s_range_c',
                    'm15_ema20_slope_1h_dir','m15_ema20_slope_align','session_twap_premium_c',
                    'pre_1s_quote_count')
            with gzip.open(path_out,'wt',newline='') as fd:
                writer=csv.DictWriter(fd,fieldnames=fields);writer.writeheader()
                for row in logs:
                    en,ex,side,profit,reason,entry_ord,exit_ord,rail,exec_price,liq_price,stop_dist=row
                    fi=entry_ord-1
                    bar_k=int(np.searchsorted(pre['starts'],fi,side='right')-2)
                    bar_k=max(0,bar_k)
                    signal_t=int(tape.ms[fi]);j=int(np.searchsorted(m15['available'],signal_t,side='right')-1)
                    htf=int(np.sign(m15_ema[j]-m15_ema[j-4])) if j>=24 else 0
                    from_1s=int(np.searchsorted(tape.ms,signal_t-1000,side='left'))
                    writer.writerow(dict(entry_time_msc=en,exit_time_msc=ex,side=side,
                        modeled_net_cash=profit,exit_reason=reason,entry_ordinal=entry_ord,
                        exit_ordinal=exit_ord,rail_c=rail,entry_exec_c=exec_price,
                        exit_liquid_c=liq_price,stop_dist_c=stop_dist,
                        entry_spread_c=int(tape.ask[fi]-tape.bid[fi]),
                        completed_5s_quotes=int(pre['ends'][bar_k]-pre['starts'][bar_k]+1),
                        completed_5s_range_c=round(float(pre['high'][bar_k]-pre['low'][bar_k]),2),
                        m15_ema20_slope_1h_dir=htf,m15_ema20_slope_align=htf==side,
                        session_twap_premium_c=round(float(side*(tape.mid[fi]-tape.twap[fi])),2) if np.isfinite(tape.twap[fi]) else '',
                        pre_1s_quote_count=fi-from_1s))
        results[rule.name]=dict(config=asdict(rule),signals_before_position_limit=counters,
            independent_events_file=events_name,
            trades=len(logs),wins=int((nets>0).sum()),win_rate=float(np.mean(nets>0)) if len(nets) else None,
            mean_net=float(np.mean(nets)) if len(nets) else None,net_cash=float(round(nets.sum(),2)),
            max_closed_trade_drawdown=float(round(dd,2)),
            exit_reasons={v:sum(x[4]==v for x in logs) for v in ('TARGET','STOP','TIME','GAP')},
            sample=logs[:12],last_trades=logs[-5:],
            real_broker_fill_certified=False,source_sha256=sha,unmodified_original_source=True)
        print(month,rule.name,'candidate',counters['potential'],'trades',len(logs),'winners',int((nets>0).sum()),'net',round(float(nets.sum()),2),flush=True)
    return dict(month=month,source_sha256=sha,quotes=len(tape.ms),runtime_s=round(time.monotonic()-t0,1),models=results)

if __name__=='__main__':
    months=sys.argv[1:] or ['01','05']
    for month in months:
        z=backtest_month(month)
        (OUT/f'V15_{month}_DEVELOPMENT.json').write_text(json.dumps(z,indent=2))
        print('RUN_SECONDS',month,z['runtime_s'],flush=True)