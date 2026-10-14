# GRID0290 research only. Preserved GRID0283 unchanged, no month identity.
# GRID0288 RESEARCH ONLY; GRID0283 original preserved unchanged.
"""GRID0283 experimental source-exact original WD119 child kernel + NEW physical parent/child custody.

Raw Jan 2026 Dukascopy original ordered Bid/Ask, quote fills >= request+250ms,
$0.20 cash fee, 0.01 lot research 1oz. Preserve unmodified source helpers.
Unlike GRID0272, EVERY renewal child must have an actually booked physical
parent in this model; four prior physically funded CLOSED profitable children
(hold <=60s) must unlock subsequent non-scout parent renewals.

DO NOT confuse with original complete 131A behavior, the current V1 integrated
Python engine, or MT5 DEAL_ADD. Initial parent candidates and child futures
are precomputed from original *chronologically observed* prices; only already
closed physical child outcome enters the causal admission/Watchdog decision.
"""
from __future__ import annotations
import sys,json,time,heapq,hashlib
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,'/mnt/data/jan_recovery_20261013');sys.path.insert(0,'/mnt/data/jan_recovery_20261013/ORIGINAL')
from original_latency import renewal_owned_delayed
import grid0274_quote_funded_admission_replay as back


def materialize():
    t,bid,ask,z,r9=back.load();pz=np.load(ROOT/'grid0276_raw_repriced_NY_source_parent_unfiltered.npz')
    # Existing preserved independent same-day session event sources: WD candidates are
    # NOT granted without a newly proven raw physical parent. Parent source 16
    # remains native L3; original WD source 17 is replaced with a gated parent.
    ordinary=z['source']!='WD119'
    ordinary_src={k:z[k][ordinary] for k in ('entry_idx','exit_idx','entry_price_raw','direction','net_cash','source')}
    parent_l3=(pz['source']==16)
    src16=dict(entry_idx=pz['entry_idx'][parent_l3],exit_idx=pz['exit_idx'][parent_l3],
        entry_price_raw=pz['entry_raw'][parent_l3],direction=pz['direction'][parent_l3],
        net_cash=pz['net'][parent_l3],source=np.full(parent_l3.sum(),'NATIVE_NY16',dtype='U24'))
    # Original owner-vetted HTF/macro and 12–13 local subphase only.
    mask=pz['wd_original_geo'];parents={k:pz[k][mask] for k in pz.files}
    # Same-quote parent collision is resolved by original source sequence, BEFORE
    # considering future outcomes. Children use original 131A qmap by completed bin.
    unique=np.lexsort((parents['source_idx'],parents['entry_idx']));ii=parents['entry_idx'][unique]
    unique=unique[np.r_[True,ii[1:]!=ii[:-1]]]
    parents={k:v[unique] for k,v in parents.items()};nparent=len(unique)
    parts=[]
    for binid,q in enumerate([1190,1190,1190,1190,1190,1100]):
        pp=np.flatnonzero(parents['local_min_bin']==binid)
        if not len(pp):continue
        A=renewal_owned_delayed(t,ask,bid,parents['entry_idx'][pp],parents['exit_idx'][pp],parents['direction'][pp],q,0,0,2,250,.20)
        E,X,R,D,P,H,owner=A[:7]
        if len(E):parts.append((E,X,R,D,P,H,pp[owner]))
    children=tuple(np.concatenate([x[j] for x in parts]) for j in range(7))
    E,X,R,D,P,H,owner=children
    assert np.array_equal(np.where(D>0,ask[E],bid[E]),R)
    err=(np.where(D>0,bid[X],ask[X]).astype(np.int64)-R)*D/1000.-.20-P
    assert np.max(np.abs(err))<1.e-9
    # Index-sorted chronological physical request population: context/source gene is unambiguous.
    fields=('entry_idx','exit_idx','entry_price_raw','direction','net_cash','source')
    ordinary={k:np.r_[ordinary_src[k],src16[k]] for k in fields}
    parentrows={k:np.asarray(parents[v]) if k!='source' else np.full(nparent,'WD_PHYSICAL_PARENT',dtype='U24') for k,v in {'entry_idx':'entry_idx','exit_idx':'exit_idx','entry_price_raw':'entry_raw','direction':'direction','net_cash':'net','source':'source'}.items()}
    childrows={'entry_idx':E,'exit_idx':X,'entry_price_raw':R,'direction':D,'net_cash':P,'source':np.full(len(E),'WD_FUNDED_CHILD',dtype='U24')}
    arr={k:np.r_[ordinary[k],parentrows[k],childrows[k]] for k in fields}
    n_ordinary=len(ordinary['entry_idx']);n_child=len(E)
    kind=np.r_[np.zeros(n_ordinary,np.int8),np.ones(nparent,np.int8),np.full(n_child,2,np.int8)]
    origin=np.r_[np.full(n_ordinary,-1,np.int32),np.arange(nparent,dtype=np.int32),owner.astype(np.int32)]
    # Original L3 coverage first, parent second, physical child third for conflicts.
    order=np.lexsort((np.arange(len(kind)),kind,arr['entry_idx']))
    arr={k:v[order] for k,v in arr.items()};kind=kind[order];origin=origin[order]
    # Runtime partitions based ONLY on observed session interval + currently observed HTF signature,
    # not keyed to historical date target labels or source PnL.
    group={(int(t[parents['entry_idx'][i]]//86400000),int(parents['source'][i]),int(parents['local_min_bin'][i]),int(parents['cell_sig'][i])) for i in range(nparent)}
    gids={v:j for j,v in enumerate(sorted(group))}
    pgid=np.asarray([gids[(int(t[parents['entry_idx'][i]]//86400000),int(parents['source'][i]),int(parents['local_min_bin'][i]),int(parents['cell_sig'][i]))] for i in range(nparent)],dtype=np.int32)
    assert len(children[0]) and len(pgid)==nparent
    return t,bid,ask,arr,kind,origin,pgid,r9,{'parents_raw':nparent,'children_raw':n_child,'native_coverage_raw':n_ordinary,'cell_count':len(gids),'child_quote_error':float(np.max(np.abs(err)))}


def physical_replay(t,bid,ask,z,kind,owner,pgid,r9,*,cash,cap,require_four=True,loss_pause_n=0,pause_ms=0,native16_cap=0,other_source_cap=0):
    EI=z['entry_idx'];XI=z['exit_idx'];R=z['entry_price_raw'];D=z['direction'];P=z['net_cash']
    n=len(EI);live=[];accepted=[];paid_parent=np.zeros(len(pgid),np.bool_)
    initial=np.zeros(int(pgid.max())+1,np.bool_);streak=np.zeros(len(initial),np.int16);gate=np.zeros(len(initial),np.bool_)
    ledger_events=Counter();balance=float(cash);used_margin=0.;netlong=netshort=0;signed_basis=0.
    source_losses={};source_pause_until={};pause_count=0;live_by_source={}
    has_prev=False;prev_fill=-1;peak_live=0;unlock=0;relock=0;winning_child=0;poor_child=0;physical_parent=0;physical_child=0
    for k in range(n):
        ei=int(EI[k]);dr=int(D[k]);current=int(t[ei]);px=int(R[k])/1000.
        while live and live[0][0]<=ei:
            _,prio,j=heapq.heappop(live);d0=int(D[j]);r0=int(R[j])/1000.;net=float(P[j]);balance+=net
            used_margin-=r0/500.;signed_basis-=d0*r0
            if d0>0:netlong-=1
            else:netshort-=1
            if kind[j]==0:
                close_source=str(z['source'][j]);live_by_source[close_source]=live_by_source.get(close_source,0)-1
            if kind[j]==0 and loss_pause_n>0:
                src=str(z['source'][j])
                source_losses[src]=source_losses.get(src,0)+1 if net<=0 else 0
                if source_losses[src]>=loss_pause_n:
                    source_pause_until[src]=int(t[int(XI[j])])+pause_ms;source_losses[src]=0;pause_count+=1
            if kind[j]==2:
                g=int(pgid[int(owner[j])]);good=net>0 and (t[int(XI[j])]-t[int(EI[j])])<=60_000
                winning_child+=int(good);poor_child+=int(not good)
                old=bool(gate[g]);streak[g]=streak[g]+1 if good else 0;gate[g]=streak[g]>=4
                if gate[g] and not old:unlock+=1
                elif old and not gate[g]:relock+=1
        # First gate is allowed for a scout, then only four already actually paid
        # closed qualifying child wins. No shadow WD119 original self-credit.
        typ=int(kind[k]);pidx=int(owner[k]);
        if typ==0 and (native16_cap>0 or other_source_cap>0):
            source=str(z['source'][k])
            limit=native16_cap if source=='NATIVE_NY16' else other_source_cap
            if limit>0 and live_by_source.get(source,0)>=limit:
                ledger_events['asof_source_simultaneous_cap']+=1;continue
        if typ==0 and loss_pause_n>0 and current<source_pause_until.get(str(z['source'][k]),-1):
            ledger_events['online_source_loss_pause']+=1;continue
        if ei==prev_fill:
            ledger_events['same_original_market_quote_collision']+=1;continue
        if typ==1:
            g=int(pgid[pidx]);
            if initial[g] and require_four and not gate[g]:
                ledger_events['parent_unearned_four_closed_winners']+=1;continue
        if typ==2:
            if not paid_parent[pidx]:
                ledger_events['child_parent_unfunded']+=1;continue
            # This child's request is not permitted if its funded physical parent
            # was already closed. The original kernel bounds child exit at parent exit.
        if len(live)>=cap:
            ledger_events['shared_open_cap']+=1;continue
        qpx=int(ask[ei] if dr>0 else bid[ei])
        if int(R[k])!=qpx:raise RuntimeError('Original quote mismatch')
        eq=balance+(netlong*float(bid[ei])-netshort*float(ask[ei]))/1000.-signed_basis-.20*len(live)
        post=eq+(float(bid[ei])-float(ask[ei]))/1000.-.20
        new_margin=px/500.
        if post<=0 or used_margin+new_margin>max(0.,post)*.65:
            ledger_events['physical_liquidity_and_margin_reject']+=1;continue
        if typ==1:
            initial[int(pgid[pidx])]=True;paid_parent[pidx]=True;physical_parent+=1
        elif typ==2:physical_child+=1
        if typ==0:
            source=str(z['source'][k]);live_by_source[source]=live_by_source.get(source,0)+1
        accepted.append(k);prev_fill=ei;used_margin+=new_margin;signed_basis+=dr*px
        if dr>0:netlong+=1
        else:netshort+=1
        heapq.heappush(live,(int(XI[k]),2 if typ==1 else 1 if typ==2 else 0,k))
        peak_live=max(peak_live,len(live))
    idx=np.asarray(accepted,np.int64)
    # Independent portfolio replay with current accepted source. One shared account,
    # all 9,135,062 original ticks marked for actual funded net/equity DD.
    sub={k:v[idx] for k,v in z.items()}
    r=back.replay(t,bid,ask,sub,r9,cash=cash,max_open=cap,max_source_open=cap,allow_unverified_wd=True)
    assert r['trades']==len(idx), 'Independent funding verifier disagreed'
    r.update(native16_cap=native16_cap,other_source_cap=other_source_cap)
    r.update(source_loss_pause_n=loss_pause_n,online_source_pause_ms=pause_ms,online_source_pause_activations=pause_count)
    r.update(verified_parent=physical_parent,verified_child=physical_child,child_closed_win60=winning_child,
        child_closed_poor=poor_child,unlock_count=unlock,relock_count=relock,
        cell_groups=len(initial),peak_open_stream=peak_live,request_denials=dict(ledger_events),
        original_children_total=int(np.sum(kind==2)), original_parents_total=int(np.sum(kind==1)),
        execution_parent_child_interaction='fully funded simulated quote-side, NOT real MT5 broker acknowledgement')
    return r


def main():
    ts=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=materialize()
    print('SOURCE',origin,'seconds',round(time.perf_counter()-ts,1),flush=True)
    rows=[]
    for title,cash,cap in [('CAUSAL_WD_PAID4_CAP256_CASH100K',100000.,256),('CAUSAL_WD_PAID4_CAP16_CASH300',300.,16)]:
        r=physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=cash,cap=cap)
        r['name']=title;rows.append(r)
        print(title,'net',round(r['net'],2),'n',r['trades'],'grossloss',round(r['gross_loss'],2),'dd',round(r['max_all_tick_floating_equity_dd'],2),'parents',r['verified_parent'],'children',r['verified_child'],'unlocks',r['unlock_count'],'daily',r['r9_synth_days_net_met'],'weekly',r['r9_synth_weeks_net_met'],flush=True)
    dest=ROOT/'grid0283_raw_funded_watchdog_combined_results.json'
    dest.write_text(json.dumps({'id':'GRID0283_INTEGRATED_RAW_FUNDED_WD_PARENT_CHILD_REPLAY',
        'original_tick_sha256':back.SRC_SHA,'source_parent':'GRID0276 original raw NY16/17 plus 131A complete as-of same-macro and actual raw quote source parents',
        'source_child':'ORIGINAL/renewal_owned_delayed direct original bid/ask source only (Q1190 except final bin Q1100)',
        'origin_count':origin,'status':'RESEARCH_ONLY_NEEDS_INDEPENDENT_SOURCE_CUSTODY_AND_L0_L7_REAL_ENGINE_QC',
        'limitations':['Parent funding modeled as a physical position at the original already delayed entry; child kernel models new independent delayed entry and original quote exit path.',
            'Four consecutive already closed physically funded good children allow renewed non-scout parents. No unverified hypothetical broker DEAL_ADD.',
            'Original parent event candidate universe inherited source f.build with original 120-minute/quote source windows. This is not original 131A normalized parent selection parity.',
            'Original non-WD supplementary frozen January candidate population remains reconstructed archived research, not one integrated production source stream.',
            'One position per original quote and margin are modeled; news, slippage, actual Coinexx contract/margin/commission still unverified.',
            'No month-blind Feb-Jul nor separate R9 OVERFIT per-trade teacher scoring. No owner acceptance or engine promotion.'],
        'results':rows,'elapsed_seconds':time.perf_counter()-ts},indent=2))
    print('SAVED',dest, 'seconds',round(time.perf_counter()-ts,1))
if __name__=='__main__':main()
