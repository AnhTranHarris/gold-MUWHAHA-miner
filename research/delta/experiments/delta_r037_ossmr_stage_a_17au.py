"""DELTA R037 one-sided spread-shock mean-reversion Stage-A screen — 17AU.

Source-grounded BBO state-transition family:
- detect a native Dukascopy spread widening caused by exactly one quote side moving outward
  while the opposite side is unchanged;
- SELL when ask alone moves outward/up; BUY when bid alone moves outward/down;
- consecutive outward moves on that same side remain one episode;
- the episode ends on first spread narrowing or any opposite-side quote change.

Preregistered profiles:
C01_IMMEDIATE_FADE: enter at shock start.
C02_FIRST_NARROW_CONFIRM: enter only when moved quote first moves inward, with opposite
quote still unchanged.
C03_FULL_SPREAD_RESTORE_CONFIRM: enter only when native spread returns to or below
the pre-shock spread before an opposite-side move invalidates the episode.

No shock-size threshold, percentile/ATR filter, session/side rescue, exit retuning,
QIM overlay, August access, or MQL5 build.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

DAY_MS=86_400_000
TICK_RAW=10
SCALE=1000
STAGE_A_END_MS=1_768_737_600_000
US_DST_START_2026_MS=1_772_953_200_000
UK_DST_START_2026_MS=1_774_746_000_000
P75_POINTS=np.asarray([20,20,21,21],dtype=np.int64)
CANONICAL_JAN_SHA256="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT="1c2896ff2d5602282c25c88a62d9e528eb69d15b"

MAX_SPREAD_RAW=25*TICK_RAW
STOP_RAW=300
TRAIL_ACTIVATION_RAW=100
TRAIL_DISTANCE_RAW=30
MAX_HOLD_SECONDS=30
PROFILES=("C01_IMMEDIATE_FADE","C02_FIRST_NARROW_CONFIRM","C03_FULL_SPREAD_RESTORE_CONFIRM")

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def atomic_write_json(path:Path,payload:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp_name=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",
                                         prefix=f".{path.name}.",suffix=".tmp",
                                         dir=path.parent,delete=False) as f:
            tmp_name=f.name
            json.dump(payload,f,indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name,path)
        tmp_name=None
    finally:
        if tmp_name is not None:
            try: os.unlink(tmp_name)
            except FileNotFoundError: pass

def session_code(t):
    tod=t%DAY_MS
    ls=np.where(t>=UK_DST_START_2026_MS,7,8)*3_600_000
    le=ls+8*3_600_000+30*60_000
    ns=np.where(t>=US_DST_START_2026_MS,12,13)*3_600_000
    ne=ns+9*3_600_000
    il=(tod>=ls)&(tod<le); iny=(tod>=ns)&(tod<ne)
    return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75(t,ask_raw,bid_raw):
    s=session_code(t)
    spread=P75_POINTS[s]*TICK_RAW
    mid2=ask_raw.astype(np.int64)+bid_raw.astype(np.int64)
    bid=((mid2-spread+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
    return (bid+spread).astype(np.int64),bid.astype(np.int64)

@njit(cache=True)
def q_tick(x):
    return ((int(x)+TICK_RAW//2)//TICK_RAW)*TICK_RAW

@njit(cache=True)
def detect_episodes(t,ask,bid):
    n=t.size
    starts=np.empty(n,np.int64)
    sides=np.empty(n,np.int8)
    confirms=np.empty(n,np.int64)
    restores=np.empty(n,np.int64)
    pre_spreads=np.empty(n,np.int64)
    peak_expansions=np.empty(n,np.int64)
    first_narrow_ms=np.empty(n,np.int64)
    count=0

    active=False
    side=0
    start=0
    base_ask=0
    base_bid=0
    pre_spread=0
    extreme=0
    confirm=-1
    restore=-1
    max_expand=0

    for i in range(1,n):
        a0=int(ask[i-1]); b0=int(bid[i-1])
        a=int(ask[i]); b=int(bid[i])
        da=a-a0; db=b-b0

        if active:
            invalid=False
            narrowed=False
            if side<0:  # ask-outward shock -> SELL
                if b!=base_bid:
                    invalid=True
                elif a<extreme:
                    narrowed=True
                    if confirm<0: confirm=i
                    if a-b<=pre_spread and restore<0: restore=i
                elif a>extreme:
                    extreme=a
                expand=(a-b)-pre_spread
            else:       # bid-outward shock -> BUY
                if a!=base_ask:
                    invalid=True
                elif b>extreme:
                    narrowed=True
                    if confirm<0: confirm=i
                    if a-b<=pre_spread and restore<0: restore=i
                elif b<extreme:
                    extreme=b
                expand=(a-b)-pre_spread
            if expand>max_expand: max_expand=expand

            if narrowed or invalid:
                starts[count]=start
                sides[count]=side
                confirms[count]=confirm
                restores[count]=restore
                pre_spreads[count]=pre_spread
                peak_expansions[count]=max_expand
                first_narrow_ms[count]=(int(t[confirm])-int(t[start])) if confirm>=0 else -1
                count+=1
                active=False

                # Current snapshot can seed a new independent episode only from its
                # direct transition relative to i-1.
                ask_out=(da>0 and db==0)
                bid_out=(db<0 and da==0)
                if ask_out or bid_out:
                    active=True
                    side=-1 if ask_out else 1
                    start=i
                    base_ask=a0; base_bid=b0
                    pre_spread=a0-b0
                    extreme=a if ask_out else b
                    max_expand=(a-b)-pre_spread
                    confirm=-1; restore=-1
                continue

        if not active:
            ask_out=(da>0 and db==0)
            bid_out=(db<0 and da==0)
            if ask_out or bid_out:
                active=True
                side=-1 if ask_out else 1
                start=i
                base_ask=a0; base_bid=b0
                pre_spread=a0-b0
                extreme=a if ask_out else b
                max_expand=(a-b)-pre_spread
                confirm=-1; restore=-1

    if active:
        starts[count]=start; sides[count]=side
        confirms[count]=confirm; restores[count]=restore
        pre_spreads[count]=pre_spread; peak_expansions[count]=max_expand
        first_narrow_ms[count]=(int(t[confirm])-int(t[start])) if confirm>=0 else -1
        count+=1

    return (starts[:count],sides[:count],confirms[:count],restores[:count],
            pre_spreads[:count],peak_expansions[:count],first_narrow_ms[:count])

@njit(cache=True)
def evaluate(event_idx,event_side,t,ask,bid):
    busy=-1;trades=0;busy_skips=0;spread_rejects=0;wins=0;longs=0;shorts=0
    gp=0.;gl=0.;net=0.;stop_count=0;hold_count=0;end_count=0
    days=np.empty(event_idx.size,np.int64);dn=0
    for z in range(event_idx.size):
        i=int(event_idx[z]); side=int(event_side[z])
        if i<0: continue
        if i<=busy:
            busy_skips+=1;continue
        if int(ask[i]-bid[i])>MAX_SPREAD_RAW:
            spread_rejects+=1;continue
        trades+=1
        if side>0: longs+=1
        else: shorts+=1
        days[dn]=int(t[i]//DAY_MS);dn+=1
        entry=int(ask[i]) if side>0 else int(bid[i])
        stop=q_tick(int(bid[i])-STOP_RAW if side>0 else int(ask[i])+STOP_RAW)
        entry_sec=int(t[i])//1000
        raw=0.;reason=2;last=i
        for k in range(i+1,t.size):
            aa=int(ask[k]);bb=int(bid[k]);sec=int(t[k])//1000;last=k
            if side>0 and bb<=stop:
                raw=(bb-entry)/SCALE;reason=0;break
            if side<0 and aa>=stop:
                raw=(entry-aa)/SCALE;reason=0;break
            if sec-entry_sec>=MAX_HOLD_SECONDS:
                raw=((bb-entry) if side>0 else (entry-aa))/SCALE;reason=1;break
            fav=(bb-entry) if side>0 else (entry-aa)
            if fav>=TRAIL_ACTIVATION_RAW:
                ns=q_tick(bb-TRAIL_DISTANCE_RAW if side>0 else aa+TRAIL_DISTANCE_RAW)
                if (side>0 and ns>stop) or (side<0 and ns<stop): stop=ns
        else:
            aa=int(ask[last]);bb=int(bid[last])
            raw=((bb-entry) if side>0 else (entry-aa))/SCALE
        exit_deal=raw-0.01
        trade_net=-0.01+exit_deal
        net+=trade_net
        if exit_deal>1e-12:wins+=1
        if raw>0:gp+=exit_deal
        else:gl+=exit_deal
        if reason==0:stop_count+=1
        elif reason==1:hold_count+=1
        else:end_count+=1
        busy=last
    distinct=0
    if dn>0:
        d=np.sort(days[:dn]);distinct=1
        for k in range(1,d.size):
            if d[k]!=d[k-1]:distinct+=1
    return trades,busy_skips,spread_rejects,distinct,longs,shorts,wins,gp,gl,net,stop_count,hold_count,end_count

def quantiles(x):
    x=np.asarray(x)
    x=x[x>=0]
    if len(x)==0:return {}
    q=np.quantile(x,[.1,.25,.5,.75,.9,.99])
    return {"p10":float(q[0]),"p25":float(q[1]),"p50":float(q[2]),"p75":float(q[3]),"p90":float(q[4]),"p99":float(q[5])}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    source_sha=sha256_file(args.source)
    if source_sha!=CANONICAL_JAN_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")
    df=pd.read_csv(args.source,compression="gzip",
                   usecols=["timestamp_ms_utc","ask_raw","bid_raw"],
                   dtype=np.int64)
    df=df[df.timestamp_ms_utc<STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709: raise SystemExit(f"Stage-A tick-count mismatch: {len(t)}")
    if np.any(t[1:]<t[:-1]): raise SystemExit("Stage-A chronology mismatch")
    ar=df.ask_raw.to_numpy(np.int64); br=df.bid_raw.to_numpy(np.int64)
    p75ask,p75bid=p75(t,ar,br)

    starts,sides,confirms,restores,pre_spreads,peaks,narrow_ms=detect_episodes(t,ar,br)
    signal_map={
        "C01_IMMEDIATE_FADE":starts,
        "C02_FIRST_NARROW_CONFIRM":confirms,
        "C03_FULL_SPREAD_RESTORE_CONFIRM":restores,
    }
    configs={}
    ordinary=[];strong=[]
    for name in PROFILES:
        idx=signal_map[name]
        ok=idx>=0
        e=idx[ok].astype(np.int64); s=sides[ok].astype(np.int8)
        vals=evaluate(e,s,t,p75ask,p75bid)
        trades,busy,sprej,days,longs,shorts,wins,gp,gl,net,stops,holds,ends=vals
        m={
            "signals":int(e.size),"busy_skips":int(busy),"spread_rejects":int(sprej),
            "trades":int(trades),"distinct_days":int(days),"long":int(longs),"short":int(shorts),
            "official_wins":int(wins),"gross_profit":round(float(gp),2),
            "gross_loss":round(float(gl),2),"direct_net_usd":round(float(net),2),
            "exit_reasons":{"STOP":int(stops),"MAX_HOLD":int(holds),"END":int(ends)}
        }
        gate={"minimum_trades_50":m["trades"]>=50,
              "minimum_distinct_days_6":m["distinct_days"]>=6,
              "direct_net_min_minus_1":m["direct_net_usd"]>=-1.0}
        gate["screen_pass"]=all(gate.values())
        gate["strong_pass"]=gate["screen_pass"] and m["direct_net_usd"]>=0.0
        configs[name]={"metrics":m,"gate":gate}
        if gate["screen_pass"]:ordinary.append(name)
        if gate["strong_pass"]:strong.append(name)

    def rk(n):
        m=configs[n]["metrics"]
        return (m["direct_net_usd"],m["official_wins"],m["trades"])
    ordinary.sort(key=rk,reverse=True);strong.sort(key=rk,reverse=True)
    if strong:
        leader=strong[0];decision="ADVANCE_STRONG_OSSMR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_OSSMR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    elif ordinary:
        leader=ordinary[0];decision="ADVANCE_ORDINARY_OSSMR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
        nxt="R037_OSSMR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION"
    else:
        leader=None;decision="RETIRE_OSSMR_STAGE_A_NO_EXECUTABLE_SURVIVOR"
        nxt="R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"

    valid_narrow=narrow_ms[narrow_ms>=0]
    diag={
        "shock_episodes":int(starts.size),
        "sell_shocks":int(np.sum(sides<0)),
        "buy_shocks":int(np.sum(sides>0)),
        "first_narrow_confirmations":int(np.sum(confirms>=0)),
        "full_restore_confirmations":int(np.sum(restores>=0)),
        "first_narrow_confirmation_rate":float(np.mean(confirms>=0)) if starts.size else 0.0,
        "full_restore_confirmation_rate":float(np.mean(restores>=0)) if starts.size else 0.0,
        "pre_shock_native_spread_quantiles_raw":quantiles(pre_spreads),
        "peak_native_spread_expansion_quantiles_raw":quantiles(peaks),
        "time_to_first_narrow_ms_quantiles":quantiles(valid_narrow),
    }
    out={
        "schema":"delta-r037-ossmr-stage-a-screen-17au-v1",
        "status":"COMPLETE_STAGE_A_SCREEN",
        "unit":"R037_ONE_SIDED_SPREAD_SHOCK_MEAN_REVERSION_STAGE_A_SCREEN",
        "family":"R037-OSSMR-v1",
        "parent_checkpoint":"R037_QIM_STAGE_A_SCREEN_CHECKPOINT_17AT",
        "prereg_commit":PREREG_COMMIT,
        "source_sha256":source_sha,"stage_a_ticks":int(len(t)),
        "signal_surface":"NATIVE_DUKASCOPY_BBO",
        "execution_surface":"DUKAS_COINEXX_LIKE_P75",
        "numeric_retuning":False,"august_accessed":False,
        "diagnostics":diag,"configs":configs,
        "finding":{"leading_config":leader,"ordinary_survivors":ordinary,
                   "strong_survivors":strong,"decision":decision,"next":nxt},
        "mql5_authorized":False
    }
    atomic_write_json(args.output,out)
    print(json.dumps({"diagnostics":diag,"finding":out["finding"],
                      "metrics":{k:v["metrics"] for k,v in configs.items()}},
                     separators=(",",":")))

if __name__=="__main__":
    main()
