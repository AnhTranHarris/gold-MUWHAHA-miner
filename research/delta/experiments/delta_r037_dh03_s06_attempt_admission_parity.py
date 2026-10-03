"""DELTA R037 DH03-S06 attempt admission / execution parity — Checkpoint 13D.

Frozen generator = exact 13C POST_PULLBACK_REARM_FRESH_EXHAUSTION stream.
This unit changes only one-position admission semantics for already-causal specialist
ENTRY_ELIGIBLE attempts that arrive while occupied. No generator or threshold changes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

import delta_r037_dh02_s08_cleanroom_parity as base
import delta_r037_dh03_s06_structure as structure
import delta_r037_dh03_s06_event_multiplicity_engine as generator

FP="a3a086b7344c"
EXPECTED_SIGNALS=1586
EXPECTED_SIGNAL_SHA="261b6ad5a1cab4dd4378ec40af7fdde4e5178e82694089b3bf2a28bc6bebfdea"
TARGET={
    "trades":1563,
    "raw_positive_wins":690,
    "gross_profit":151.82,
    "gross_loss":-490.75,
    "net_profit":-338.93,
    "max_balance_drawdown":339.25,
}
PROFILES=(
    "DROP_OCCUPIED_CONTROL",
    "EXIT_TICK_LATCH_DROP",
    "PENDING_FIRST_AFTER_OBSERVATION",
    "PENDING_LATEST_AFTER_OBSERVATION",
)

@njit(cache=True)
def qtick(v,tick=10):
    return ((v+tick//2)//tick)*tick

@njit(cache=True)
def admit_attempt_policy(t,ask,bid,sig_t,sig_side,sig_event,policy):
    STOP=300
    TRAIL_ACT=100
    TRAIL_DIST=30

    pos=0
    entry=0
    stop=0
    entrysec=0
    sp=0

    pending=False
    pending_side=0
    pending_event=0

    trades=0
    raw_wins=0
    official_wins=0
    gp=0.0
    gl=0.0
    balance=100000.0
    peak=balance
    maxdd=0.0

    immediate_admissions=0
    rejected_occupied=0
    exit_tick_latch_drops=0
    pending_created=0
    pending_replaced=0
    pending_admitted=0
    pending_side_changes=0
    signal_events_while_occupied=0

    for i in range(t.size):
        tm=int(t[i])
        sec=tm//1000
        a=int(ask[i])
        b=int(bid[i])
        exited=False

        if pos==1 and b<=stop:
            raw=(b-entry)/1000.0
            deal=raw-0.01
            if raw>0:
                raw_wins+=1
                gp+=deal
            else:
                gl+=deal
            if deal>0:
                official_wins+=1
            balance+=deal
            trades+=1
            pos=0
            entry=0
            stop=0
            exited=True
        elif pos==-1 and a>=stop:
            raw=(entry-a)/1000.0
            deal=raw-0.01
            if raw>0:
                raw_wins+=1
                gp+=deal
            else:
                gl+=deal
            if deal>0:
                official_wins+=1
            balance+=deal
            trades+=1
            pos=0
            entry=0
            stop=0
            exited=True

        if pos!=0:
            if sec-entrysec>=30:
                raw=((b-entry) if pos==1 else (entry-a))/1000.0
                deal=raw-0.01
                if raw>0:
                    raw_wins+=1
                    gp+=deal
                else:
                    gl+=deal
                if deal>0:
                    official_wins+=1
                balance+=deal
                trades+=1
                pos=0
                entry=0
                stop=0
                exited=True
            else:
                fav=(b-entry) if pos==1 else (entry-a)
                if fav>=TRAIL_ACT:
                    new_stop=qtick(b-TRAIL_DIST if pos==1 else a+TRAIL_DIST)
                    if (pos==1 and new_stop>stop) or (pos==-1 and new_stop<stop):
                        stop=new_stop

        # Position-observation semantics for pending profiles:
        # a pending attempt is admitted only on a later tick that observes flatness.
        if policy>=2 and pos==0 and pending and not exited:
            pos=pending_side
            entry=a if pos==1 else b
            stop=qtick(b-STOP if pos==1 else a+STOP)
            entrysec=sec
            balance-=0.01
            gl-=0.01
            pending=False
            pending_side=0
            pending_event=0
            pending_admitted+=1

        while sp<sig_t.size and int(sig_t[sp])<=tm:
            side=int(sig_side[sp])
            event=int(sig_event[sp])

            if policy==0:
                if pos==0:
                    pos=side
                    entry=a if pos==1 else b
                    stop=qtick(b-STOP if pos==1 else a+STOP)
                    entrysec=sec
                    balance-=0.01
                    gl-=0.01
                    immediate_admissions+=1
                else:
                    rejected_occupied+=1
                    signal_events_while_occupied+=1

            elif policy==1:
                if pos!=0:
                    rejected_occupied+=1
                    signal_events_while_occupied+=1
                elif exited:
                    exit_tick_latch_drops+=1
                else:
                    pos=side
                    entry=a if pos==1 else b
                    stop=qtick(b-STOP if pos==1 else a+STOP)
                    entrysec=sec
                    balance-=0.01
                    gl-=0.01
                    immediate_admissions+=1

            else:
                # After an exit on this same tick, flatness is not yet considered
                # observed. The attempt therefore enters the one-token pending slot.
                occupied_for_admission=(pos!=0) or exited
                if occupied_for_admission:
                    if pos!=0:
                        signal_events_while_occupied+=1
                    if not pending:
                        pending=True
                        pending_side=side
                        pending_event=event
                        pending_created+=1
                    elif policy==3:
                        if pending_side!=side:
                            pending_side_changes+=1
                        pending_side=side
                        pending_event=event
                        pending_replaced+=1
                    else:
                        rejected_occupied+=1
                else:
                    pos=side
                    entry=a if pos==1 else b
                    stop=qtick(b-STOP if pos==1 else a+STOP)
                    entrysec=sec
                    balance-=0.01
                    gl-=0.01
                    immediate_admissions+=1

            sp+=1

        if balance>peak:
            peak=balance
        dd=peak-balance
        if dd>maxdd:
            maxdd=dd

    return (
        trades,raw_wins,official_wins,gp,gl,gp+gl,maxdd,
        immediate_admissions,rejected_occupied,exit_tick_latch_drops,
        pending_created,pending_replaced,pending_admitted,pending_side_changes,
        signal_events_while_occupied,
    )

def score(actual):
    er={q:abs(actual[q]-TARGET[q]) for q in TARGET}
    sc=(100.0*er["trades"]+25.0*er["raw_positive_wins"]+
        er["gross_profit"]+er["gross_loss"]+er["net_profit"]+er["max_balance_drawdown"])
    return er,float(sc)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()

    ev=json.loads(a.evidence.read_text(encoding="utf-8"))
    if ev.get("schema")!="delta-r037-dh03-s06-event-attempt-admission-evidence-13d-v1":
        raise SystemExit("13D evidence schema mismatch")
    if ev["frozen_generator"]["vector"]!="DH03-S06 / "+FP:
        raise SystemExit("13D vector fingerprint mismatch")

    sh=base.sha256_file(a.source)
    if sh!=base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch")

    df=pd.read_csv(
        a.source,compression="gzip",
        usecols=["timestamp_ms_utc","ask_raw","bid_raw"],
        dtype=np.int64,
    )
    df=df[df.timestamp_ms_utc<base.STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709:
        raise SystemExit(f"Stage-A tick mismatch: {len(t)}")

    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    mid=ask+bid
    b5=base.bars(t,mid,5_000)
    b15=base.bars(t,mid,15_000)
    b30=base.bars(t,mid,30_000)
    m5=base.bars(t,mid,300_000)
    m15=base.bars(t,mid,900_000)
    m30=base.bars(t,mid,1_800_000)
    e5=base.signed_eff(b5,4)
    e15=base.signed_eff(b15,4)
    e30=base.signed_eff(b30,4)
    a5=base.atr14(m5)
    pe,ps,pdir,li,si=structure.parent_series(m15,m30)
    phi,plo,pht,plt=structure.latest_fast_pivots(b15)

    st,ss,se,c=generator.detect(
        t,mid,
        b5["end_ms"],b5["close"],e5,
        b15["end_ms"],b15["high"],b15["low"],b15["close"],e15,
        b30["end_ms"],e30,
        m5["end_ms"],a5,
        pe,ps,li,si,
        phi,plo,pht,plt,
        0,1,
    )
    sigsha=base.signal_sha(st,ss,se)
    if int(st.size)!=EXPECTED_SIGNALS or sigsha!=EXPECTED_SIGNAL_SHA:
        raise SystemExit(f"13C generator drift signals={st.size} sha={sigsha}")

    profiles={}
    for pi,pname in enumerate(PROFILES):
        x=admit_attempt_policy(t,ask,bid,st,ss,se,pi)
        actual={
            "generator_signals":int(st.size),
            "signal_sha256":sigsha,
            "trades":int(x[0]),
            "raw_positive_wins":int(x[1]),
            "official_wins":int(x[2]),
            "gross_profit":float(x[3]),
            "gross_loss":float(x[4]),
            "net_profit":float(x[5]),
            "max_balance_drawdown":float(x[6]),
            "immediate_admissions":int(x[7]),
            "rejected_while_occupied":int(x[8]),
            "exit_tick_latch_drops":int(x[9]),
            "pending_created":int(x[10]),
            "pending_replaced":int(x[11]),
            "pending_admitted_after_observation":int(x[12]),
            "pending_side_changes":int(x[13]),
            "signal_events_while_occupied":int(x[14]),
        }
        actual["unexecuted_generator_signals"]=int(actual["generator_signals"]-actual["trades"])
        er,sc=score(actual)
        profiles[pname]={"actual":actual,"abs_error":er,"parity_score":sc}

    ctrl=profiles["DROP_OCCUPIED_CONTROL"]["actual"]
    if not (
        ctrl["trades"]==1513
        and ctrl["raw_positive_wins"]==674
        and ctrl["official_wins"]==661
        and abs(ctrl["gross_profit"]-137.12)<1e-8
        and abs(ctrl["gross_loss"]+476.26)<1e-8
        and abs(ctrl["net_profit"]+339.14)<1e-8
        and abs(ctrl["max_balance_drawdown"]-339.1399999917485)<1e-6
        and ctrl["rejected_while_occupied"]==73
    ):
        raise SystemExit("CONTROL_13C admission drift: "+json.dumps(ctrl,sort_keys=True))

    order=sorted(PROFILES,key=lambda z:profiles[z]["parity_score"])
    lead=order[0]
    q=profiles[lead]["actual"]
    exact=(
        q["trades"]==TARGET["trades"]
        and q["raw_positive_wins"]==TARGET["raw_positive_wins"]
        and all(abs(q[k]-TARGET[k])<0.011 for k in ("gross_profit","gross_loss","net_profit","max_balance_drawdown"))
    )

    out={
        "schema":"delta-r037-dh03-s06-event-attempt-admission-parity-13d-v1",
        "status":"COMPLETE_EXACT_PARITY" if exact else "COMPLETE_ADMISSION_QA_PARITY_NOT_YET",
        "unit":"R037_DH03_S06_EVENT_ATTEMPT_ADMISSION_AND_EXECUTION_PARITY_RECONSTRUCTION",
        "source_sha256":sh,
        "stage_a_ticks":int(len(t)),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint":FP,
        "numeric_vector_retune":False,
        "generator_changed":False,
        "august_accessed":False,
        "generator_control":{
            "signals":int(st.size),
            "signal_sha256":sigsha,
            "pullback_episodes":int(c[0]),
            "exhaustion":int(c[1]),
            "reclaim":int(c[2]),
        },
        "profiles":profiles,
        "ranking":order,
        "finding":{
            "leading_profile":lead,
            "control_13c_reproduced":True,
            "exact_historical_parity":exact,
            "target":TARGET,
            "next":ev["next_if_exact"] if exact else (
                ev["next_if_material_nonexact"]
                if profiles[lead]["actual"]["trades"]>ctrl["trades"]
                else ev["next_if_negative"]
            ),
        },
        "mql5_authorized":False,
    }
    base.atomic_write_json(a.output,out)
    print(json.dumps(out["finding"],separators=(",",":")))

if __name__=="__main__":
    main()
