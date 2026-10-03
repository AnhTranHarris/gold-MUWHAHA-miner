"""DELTA R037 DH03-S06 pending-attempt causal validity parity — Checkpoint 13E.

Frozen generator and execution mechanics from 13C/13D. This unit changes only the
causal lifetime of one pending specialist ENTRY_ELIGIBLE token while another position
is occupied. No numeric tuning and no generator changes.
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
import delta_r037_dh03_s06_attempt_admission_parity as admission13d
import delta_r037_dh03_s06_pending_validity_engine as lifecycle

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
    "PENDING_UNCONDITIONAL_CONTROL",
    "PENDING_PARENT_VALID",
    "PENDING_PARENT_STRUCTURE_VALID",
    "PENDING_FULL_EVENT_VALID",
)

@njit(cache=True)
def qtick(v,tick=10):
    return ((v+tick//2)//tick)*tick

@njit(cache=True)
def pending_invalid(event,event_end,event_reason,tm,mode):
    if event<=0 or event>=event_end.size:
        return False
    end=int(event_end[event])
    if end<=0 or tm<end:
        return False
    reason=int(event_reason[event])
    if mode==0:
        return False
    if mode==1:
        return reason==1
    if mode==2:
        return reason==1 or reason==2
    return reason==1 or reason==2 or reason==3

@njit(cache=True)
def admit_with_validity(t,ask,bid,sig_t,sig_side,sig_event,event_end,event_reason,mode):
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
    pending_created=0
    pending_admitted=0
    invalid_parent=0
    invalid_structure=0
    invalid_age=0
    signals_while_occupied=0

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
                    ns=qtick(b-TRAIL_DIST if pos==1 else a+TRAIL_DIST)
                    if (pos==1 and ns>stop) or (pos==-1 and ns<stop):
                        stop=ns

        if pending and pending_invalid(pending_event,event_end,event_reason,tm,mode):
            reason=int(event_reason[pending_event])
            if reason==1:
                invalid_parent+=1
            elif reason==2:
                invalid_structure+=1
            elif reason==3:
                invalid_age+=1
            pending=False
            pending_side=0
            pending_event=0

        # Position-observation latch: pending is executable only on a later flat tick.
        if pos==0 and pending and not exited:
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
            occupied_for_admission=(pos!=0) or exited
            if occupied_for_admission:
                if pos!=0:
                    signals_while_occupied+=1
                if not pending:
                    # The signal itself is causal and valid at emission. Its future
                    # admission remains conditional on the original event staying alive.
                    pending=True
                    pending_side=side
                    pending_event=event
                    pending_created+=1
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
        immediate_admissions,pending_created,pending_admitted,
        invalid_parent,invalid_structure,invalid_age,signals_while_occupied,
    )

def pack(x,signals,sigsha):
    a={
        "generator_signals":int(signals),
        "signal_sha256":sigsha,
        "trades":int(x[0]),
        "raw_positive_wins":int(x[1]),
        "official_wins":int(x[2]),
        "gross_profit":float(x[3]),
        "gross_loss":float(x[4]),
        "net_profit":float(x[5]),
        "max_balance_drawdown":float(x[6]),
        "immediate_admissions":int(x[7]),
        "pending_created":int(x[8]),
        "pending_admitted_after_observation":int(x[9]),
        "pending_invalid_parent":int(x[10]),
        "pending_invalid_structure":int(x[11]),
        "pending_invalid_age":int(x[12]),
        "signal_events_while_occupied":int(x[13]),
    }
    a["pending_invalid_total"]=a["pending_invalid_parent"]+a["pending_invalid_structure"]+a["pending_invalid_age"]
    a["unexecuted_generator_signals"]=a["generator_signals"]-a["trades"]
    er={q:abs(a[q]-TARGET[q]) for q in TARGET}
    score=(100.0*er["trades"]+25.0*er["raw_positive_wins"]+
           er["gross_profit"]+er["gross_loss"]+er["net_profit"]+er["max_balance_drawdown"])
    return {"actual":a,"abs_error":er,"parity_score":float(score)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()

    ev=json.loads(a.evidence.read_text(encoding="utf-8"))
    if ev.get("schema")!="delta-r037-dh03-s06-pending-validity-evidence-13e-v1":
        raise SystemExit("13E evidence mismatch")

    sh=base.sha256_file(a.source)
    if sh!=base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch")

    df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
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

    st,ss,se,c,evstart,evend,evreason,evside=lifecycle.detect_with_lifecycle(
        t,mid,b5["end_ms"],b5["close"],e5,
        b15["end_ms"],b15["high"],b15["low"],b15["close"],e15,
        b30["end_ms"],e30,m5["end_ms"],a5,
        pe,ps,li,si,phi,plo,pht,plt,
    )
    sigsha=base.signal_sha(st,ss,se)
    if int(st.size)!=EXPECTED_SIGNALS or sigsha!=EXPECTED_SIGNAL_SHA:
        raise SystemExit(f"13C generator drift signals={st.size} sha={sigsha}")
    if not (int(c[0])==1147 and int(c[1])==2006 and int(c[2])==1632 and int(c[3])==1586):
        raise SystemExit("13C lifecycle funnel drift: "+json.dumps([int(x) for x in c]))

    profiles={}

    # Exact 13D DROP control via the accepted producer helper.
    xd=admission13d.admit_attempt_policy(t,ask,bid,st,ss,se,0)
    ad={
        "generator_signals":int(st.size),"signal_sha256":sigsha,
        "trades":int(xd[0]),"raw_positive_wins":int(xd[1]),"official_wins":int(xd[2]),
        "gross_profit":float(xd[3]),"gross_loss":float(xd[4]),"net_profit":float(xd[5]),
        "max_balance_drawdown":float(xd[6]),
        "immediate_admissions":int(xd[7]),"rejected_while_occupied":int(xd[8]),
        "unexecuted_generator_signals":int(st.size-int(xd[0])),
    }
    er={q:abs(ad[q]-TARGET[q]) for q in TARGET}
    profiles["DROP_OCCUPIED_CONTROL"]={"actual":ad,"abs_error":er,"parity_score":float(100*er["trades"]+25*er["raw_positive_wins"]+er["gross_profit"]+er["gross_loss"]+er["net_profit"]+er["max_balance_drawdown"])}

    mode_names=("PENDING_UNCONDITIONAL_CONTROL","PENDING_PARENT_VALID","PENDING_PARENT_STRUCTURE_VALID","PENDING_FULL_EVENT_VALID")
    for mode,pname in enumerate(mode_names):
        profiles[pname]=pack(admit_with_validity(t,ask,bid,st,ss,se,evend,evreason,mode),st.size,sigsha)

    ctrl=profiles["DROP_OCCUPIED_CONTROL"]["actual"]
    if not (ctrl["trades"]==1513 and ctrl["raw_positive_wins"]==674 and ctrl["official_wins"]==661 and abs(ctrl["net_profit"]+339.14)<1e-8):
        raise SystemExit("13D DROP control drift")

    pu=profiles["PENDING_UNCONDITIONAL_CONTROL"]["actual"]
    if not (
        pu["trades"]==1586 and pu["raw_positive_wins"]==703 and pu["official_wins"]==690
        and abs(pu["gross_profit"]-141.28)<1e-8 and abs(pu["gross_loss"]+499.35)<1e-8
        and abs(pu["net_profit"]+358.07)<1e-8 and pu["pending_created"]==83
        and pu["pending_admitted_after_observation"]==83 and pu["pending_invalid_total"]==0
    ):
        raise SystemExit("13D pending-all control drift: "+json.dumps(pu,sort_keys=True))

    order=sorted(PROFILES,key=lambda z:profiles[z]["parity_score"])
    lead=order[0]
    q=profiles[lead]["actual"]
    exact=(q["trades"]==TARGET["trades"] and q["raw_positive_wins"]==TARGET["raw_positive_wins"] and
           all(abs(q[k]-TARGET[k])<0.011 for k in ("gross_profit","gross_loss","net_profit","max_balance_drawdown")))

    reasons={
        "parent_opposition":int(np.sum(evreason==1)),
        "structural_invalidation":int(np.sum(evreason==2)),
        "max_age_expiry":int(np.sum(evreason==3)),
        "active_at_stage_a_end":int(np.sum(evreason==0))-1,
    }
    out={
        "schema":"delta-r037-dh03-s06-pending-validity-parity-13e-v1",
        "status":"COMPLETE_EXACT_PARITY" if exact else "COMPLETE_PENDING_VALIDITY_QA_PARITY_NOT_YET",
        "unit":"R037_DH03_S06_PENDING_ATTEMPT_VALIDITY_AND_SUPERSESSION_PARITY_RECONSTRUCTION",
        "source_sha256":sh,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint":FP,"numeric_vector_retune":False,"generator_changed":False,"august_accessed":False,
        "generator_control":{"signals":int(st.size),"signal_sha256":sigsha,"pullback_episodes":int(c[0]),"exhaustion":int(c[1]),"reclaim":int(c[2])},
        "episode_end_reasons":reasons,
        "profiles":profiles,"ranking":order,
        "finding":{
            "leading_profile":lead,
            "drop_control_reproduced":True,
            "pending_unconditional_control_reproduced":True,
            "exact_historical_parity":exact,
            "target":TARGET,
            "canonical_profile":"PENDING_FULL_EVENT_VALID",
            "next":ev["next_if_exact"] if exact else (
                ev["next_if_material_nonexact"]
                if profiles["PENDING_FULL_EVENT_VALID"]["parity_score"]<profiles["PENDING_UNCONDITIONAL_CONTROL"]["parity_score"]
                else ev["next_if_negative"]
            ),
        },
        "mql5_authorized":False,
    }
    base.atomic_write_json(a.output,out)
    print(json.dumps(out["finding"],separators=(",",":")))

if __name__=="__main__":
    main()
