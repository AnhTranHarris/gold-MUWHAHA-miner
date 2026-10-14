"""GRID0312: independent, research-only original Bid/Ask tick stop-out executor.

A new experimental executor, NOT the live FourSessionV1 or broker emulator.
Consumes original historically researched source opportunities; no future exit data
is consulted for admission. Stops/liquidations happen at first observed original
quote, and CLOSES are actually booked / removed from future settlement.

Fixed 0.01 lot = hypothetical 1oz, $0.20/round trip fee, leverage500;
margin modes/hedge relief/stop-out order/slippage must be broker-calibrated.
Day/month/week identities never enter strategy decisions (only offline scoring).
"""
from __future__ import annotations
from collections import deque,Counter
import json,heapq,time
from pathlib import Path
import numpy as np
from numba import njit
import grid0309_earned_cash_capped_100usd_growth as prior
ROOT=Path(__file__).resolve().parent
DAY=86_400_000; HOUR=3_600_000

@njit(cache=True)
def scan_to_first_risk(t,bid,ask,start,end,balance,nlong,nshort,basis,fee_open,used_margin,
                       stop_ratio,peak_hour,hour_key,worst_hour,min_eq,min_ratio,max_equity_dd,
                       peak_total,breach_eq_floor):
    """Run first-tick as-of account marks; return first risk breach or -1.
    Updates local-hour and total DD as state follows chronological quotes.
    No future quote, upcoming scheduled exit or teacher target is ever a feature.
    """
    hit=-1
    for i in range(start,end+1):
        key=t[i]//HOUR
        eq=balance+(nlong*float(bid[i])-nshort*float(ask[i]))/1000.-basis-fee_open
        if key!=hour_key[0]:
            hour_key[0]=key;peak_hour[0]=eq
        elif eq>peak_hour[0]:peak_hour[0]=eq
        hdd=peak_hour[0]-eq
        if hdd>worst_hour[0]:worst_hour[0]=hdd
        if eq<min_eq[0]:min_eq[0]=eq
        if eq>peak_total[0]:peak_total[0]=eq
        tdd=peak_total[0]-eq
        if tdd>max_equity_dd[0]:max_equity_dd[0]=tdd
        if used_margin>0.:
            ratio=eq/used_margin
            if ratio<min_ratio[0]:min_ratio[0]=ratio
            if ratio<stop_ratio or eq<=breach_eq_floor:
                hit=i;break
        elif eq<=breach_eq_floor:
            hit=i;break
    return hit


def run(t,bid,ask,z,kind,owner,pgid,*,cash=100.,initial_cap=2,cap=64,
        earned_cash_tiers=((100.,2),(150.,4),(300.,8),(500.,16),(1000.,32),(2000.,64)),
        admission_margin_fraction=.20,stopout_ratio=1.,liquidation_style='worst_first',
        defensive_ratio=0.,defensive_flatten=False,loss_pause_n=2,pause_ms=300000,
        native16_cap=2,gc0_cap=64,gc2_cap=64,parent_cap=16,earned_parent_cap=64,
        max_observed_risk_fraction=0.,max_tick_slippage_usd=0.,
        fees_per_roundtrip=.20, leverage=500., require_four=True):
    assert 0<=admission_margin_fraction<=.85 and stopout_ratio>=.5
    assert liquidation_style in ('worst_first','flatten')
    E=z['entry_idx'];X=z['exit_idx'];R=z['entry_price_raw'];D=z['direction'];P=z['net_cash'];N=len(E)
    assert len(kind)==N and np.all(np.diff(E)>=0)
    # Source-parent genealogy is exact for admitted funding; forced closes cannot grant credit.
    paid_parent=np.zeros(len(pgid),bool);parent_open=np.zeros(len(pgid),bool)
    groups=np.zeros(int(np.max(pgid))+1,bool);streak=np.zeros(len(groups),np.int16);gate=np.zeros(len(groups),bool)
    live={};heap=[];accepted=[];booked=[];counts=Counter();denied=Counter();src_open=Counter();source_streak=Counter();source_pause={}
    balance=float(cash);used_margin=0.;nlong=nshort=0;basis=0.;open_fee=0.
    last_i=0;prior_fill=-1;parent_live=0;child_live=0;max_open=0;pending_parent=deque(maxlen=6);native_recent=deque(maxlen=10)
    winner_child=0;unlocks=0;relocks=0;forced_events=0;forced_positions=0;defensive_events=0
    peak_hour=np.asarray([cash],float);h_key=np.asarray([-10**12],np.int64)
    worst_hour=np.asarray([0.],float);min_eq=np.asarray([cash],float);min_ratio=np.asarray([np.inf],float);peak_total=np.asarray([cash],float);max_eq_dd=np.asarray([0.],float)
    fee_half=fees_per_roundtrip*.5
    # floating equity marks subtract the remaining exit fee plus entry fee already booked;
    # the open_fee is the entire fee in unrealized equity (balance has no entry debit).

    def quote_equity(i):
        return balance+(nlong*int(bid[i])-nshort*int(ask[i]))/1000.-basis-open_fee

    def close(j,ix,reason):
        nonlocal balance,used_margin,nlong,nshort,basis,open_fee,parent_live,child_live,winner_child,unlocks,relocks,forced_positions
        if j not in live:return False
        k=live.pop(j)
        dr=int(D[j]);en=int(R[j])/1000.;out=int(bid[ix] if dr>0 else ask[ix])/1000.
        # Original research trade economics, signed, with explicit round-trip fees.
        cash_net=dr*(out-en)-fees_per_roundtrip-max_tick_slippage_usd
        if reason=='scheduled':
            expected=float(P[j]);assert abs(cash_net-(expected+.20-fees_per_roundtrip-max_tick_slippage_usd))<1e-6,(j,cash_net,expected)
        balance+=cash_net;basis-=dr*en;used_margin-=en/leverage;open_fee-=fees_per_roundtrip
        if dr>0:nlong-=1
        else:nshort-=1
        typ=int(kind[j]);s=str(z['source'][j])
        if typ==0:
            src_open[s]-=1
            if s=='NATIVE_NY16':native_recent.append(cash_net)
            source_streak[s]=(source_streak[s]+1) if cash_net<=0 else 0
            if loss_pause_n and source_streak[s]>=loss_pause_n:
                source_pause[s]=int(t[ix])+pause_ms;source_streak[s]=0;counts['pause_triggered']+=1
        elif typ==1:
            parent_live-=1;pending_parent.append(cash_net);parent_open[int(owner[j])]=False
        else:
            child_live-=1
            g=int(pgid[int(owner[j])]);is_good=cash_net>0 and (int(t[ix])-int(t[int(E[j])]))<=60000
            winner_child+=int(is_good);prev=bool(gate[g]);streak[g]=streak[g]+1 if is_good else 0;gate[g]=streak[g]>=4
            if gate[g] and not prev:unlocks+=1
            if prev and not gate[g]:relocks+=1
        booked.append((int(ix),int(j),float(cash_net),reason))
        counts['closed_'+reason]+=1
        if reason!='scheduled':forced_positions+=1
        return True

    def liquidation(ix,is_defensive):
        nonlocal forced_events,defensive_events
        if not live:return
        if is_defensive:defensive_events+=1
        else:forced_events+=1
        if liquidation_style=='flatten' or (is_defensive and defensive_flatten):
            to_close=list(live.keys())
        else:
            # Worst current equity contributor first; no knowledge of future winners.
            j=min(live,key=lambda j:int(D[j])*(int(bid[ix] if D[j]>0 else ask[ix])-int(R[j]))/1000.)
            to_close=[j]
        for j in to_close:close(j,ix,'defensive' if is_defensive else 'forced')

    def scan_and_apply(left,right):
        nonlocal last_i
        left=max(left,last_i+1)
        if left>right:return
        x=left
        while x<=right:
            ratio=defensive_ratio if defensive_ratio else stopout_ratio
            hit=scan_to_first_risk(t,bid,ask,x,right,balance,nlong,nshort,basis,open_fee,used_margin,ratio,
                         peak_hour,h_key,worst_hour,min_eq,min_ratio,max_eq_dd,peak_total,-1e12)
            if hit<0:break
            # The observed unsafe mark is part of the actual risk record; flatten or
            # partial liquidation uses THIS quote, not the previous one.
            liquidation(hit,defensive_ratio>stopout_ratio)
            if not live: x=hit+1;continue
            # When partial liquidation didn't restore >= threshold, rescan same tick
            # so the next at-risk position closes at this exact tick.
            x=hit
            if x==last_i and len(live)==0:break
        last_i=right

    # Note: forced closes must update the realized-cash admission state BEFORE
    # processing other candidates later on the same or following quote.
    for k in range(N):
        ei=int(E[k]);current=int(t[ei]);typ=int(kind[k]);dr=int(D[k]);pidx=int(owner[k]);src=str(z['source'][k]); px=int(R[k])/1000.
        while heap and heap[0][0]<=ei:
            end=int(heap[0][0]);scan_and_apply(last_i+1,end-1)
            # The heap may include future closures of positions already forcibly closed.
            while heap and heap[0][0]==end:
                _,j=heapq.heappop(heap)
                if j in live:close(j,end,'scheduled')
            scan_and_apply(last_i+1,end)
        scan_and_apply(last_i+1,ei)
        if balance<=0:
            denied['bankrupt']+=1;continue
        if ei==prior_fill:denied['same_quote_collision']+=1;continue
        if typ==0:
            if src_open[src]>= (native16_cap if src=='NATIVE_NY16' else gc0_cap if src=='coverage_gc0' else gc2_cap if src=='coverage_gc2' else cap):
                denied['source_cap']+=1;continue
            if current<source_pause.get(src,-1):denied['online_pause']+=1;continue
        if typ==1:
            gi=int(pgid[pidx]);
            if groups[gi] and require_four and not gate[gi]:denied['parent_prior_child_gate']+=1;continue
            permit=parent_cap
            if len(pending_parent)>=6 and sum(v>0 for v in pending_parent)>=4 and sum(pending_parent)>=4.:
                permit=earned_parent_cap
            if parent_live>=permit:denied['parent_cap']+=1;continue
        if typ==2:
            if not paid_parent[pidx]:denied['unfunded_parent']+=1;continue
            # If parent was forced closed, descendants cannot create new child entries.
            if not parent_open[pidx]:denied['parent_closed_or_liquidated']+=1;continue
        earned=initial_cap
        for bal_thresh,slots in earned_cash_tiers:
            if balance>=bal_thresh:earned=max(earned,int(slots))
        if len(live)>=min(cap,earned):denied['earned_capacity_cap']+=1;continue
        if int(R[k])!=int(ask[ei] if dr>0 else bid[ei]):raise AssertionError('Quote fill mismatch')
        eq=quote_equity(ei);post=eq+(int(bid[ei])-int(ask[ei]))/1000.-fees_per_roundtrip
        need=px/leverage
        if post<=0 or used_margin+need>post*admission_margin_fraction:denied['margin_admission']+=1;continue
        if max_observed_risk_fraction:
            # Session-agnostic conservative reserve: live Mark-to-Market protection
            if post-used_margin-need<max_observed_risk_fraction*balance:
                denied['risk_cushion']+=1;continue
        # All gating above reads only booked balance and observed quote.
        if typ==1:groups[gi]=True;paid_parent[pidx]=True;parent_open[pidx]=True;parent_live+=1
        elif typ==2:child_live+=1
        else:src_open[src]+=1
        live[k]=k;heapq.heappush(heap,(int(X[k]),int(k)));accepted.append(k)
        prior_fill=ei;used_margin+=need;basis+=dr*px;open_fee+=fees_per_roundtrip
        if dr>0:nlong+=1
        else:nshort+=1
        max_open=max(max_open,len(live))
        # The entry spread cost and commission are paid as an immediate mark-down.
        qeq=quote_equity(ei); min_eq[0]=min(min_eq[0],qeq)
        if qeq>peak_total[0]:peak_total[0]=qeq
        if qeq/used_margin<min_ratio[0]:min_ratio[0]=qeq/used_margin
        if peak_total[0]-qeq>max_eq_dd[0]:max_eq_dd[0]=peak_total[0]-qeq
        if h_key[0]!=current//HOUR:
            h_key[0]=current//HOUR;peak_hour[0]=qeq
        if peak_hour[0]-qeq>worst_hour[0]:worst_hour[0]=peak_hour[0]-qeq
    while heap:
        end=int(heap[0][0]);scan_and_apply(last_i+1,end-1)
        while heap and heap[0][0]==end:
            _,j=heapq.heappop(heap)
            if j in live:close(j,end,'scheduled')
        scan_and_apply(last_i+1,end)
    scan_and_apply(last_i+1,len(t)-1)
    # Include end-of-window mandatory liquidation before evaluating seven-day cash.
    if live:
        for j in list(live):close(j,len(t)-1,'window_end')
    assert not live
    eq=float(balance); net=eq-cash
    res={'start_cash':cash,'final_cash':eq,'net_cash':net,'trades_closed':len(booked),'candidate_entries':len(accepted),
        'min_tick_equity':float(min_eq[0]),'min_margin_ratio_observed':float(min_ratio[0]) if np.isfinite(min_ratio[0]) else None,
        'max_tick_drawdown':float(max_eq_dd[0]),'worst_hour_drawdown':float(worst_hour[0]),
        'peak_open':max_open,'forced_events':forced_events,'forced_positions':forced_positions,'defensive_events':defensive_events,
        'risk_breaches':bool(forced_events), 'target_10000_met':bool(eq>=10000.),
        'counts':dict(counts),'denied':dict(denied),'booked_ledger':booked,'accepted_indices':accepted,
        'modeled_stopout_threshold_ratio':stopout_ratio,'defensive_ratio':defensive_ratio,
        'margin_admission_fraction':admission_margin_fraction,'liquidation_style':liquidation_style,
        'model_limitations':['Research 500:1 hypothetical margin, no hedged margin credit, synthetic fee, no broker slippage calibration',
        'Original source candidates/exits previously selected in-sample; producer not month-blind runtime',
        'Margin percentages and position close ordering are scenarios, not verified Coinexx actual STOP_OUT',
        'Forced liquidation closes are actual booked independent ledger; no post-stopout ghost settlement or unrealized funding']}
    return res
