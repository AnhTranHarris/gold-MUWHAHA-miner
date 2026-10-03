"""R037 DH05 clean-room parity reconstruction candidate 01.

Research-only diagnostic source. It reconstructs the frozen DH-05 M5-swing
family from durable DELTA rules and the public SwingBars=3 symmetric swing
construction cited by the DH-05 research provenance.

This file MUST be committed before its outputs are used scientifically.
It does not implement SORB integration, parameter retuning, August access,
or MQL5 logic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

DAY_MS = 86_400_000
TICK_RAW = 10
PRICE_SCALE = 1000
STAGE_A_END_MS = 1_768_737_600_000
US_DST_START_2026_MS = 1_772_953_200_000
UK_DST_START_2026_MS = 1_774_746_000_000
P75_POINTS = np.asarray([20, 20, 21, 21], dtype=np.int64)
SWING_BARS = 3


@dataclass(frozen=True)
class Vector:
    name: str
    acceptance_disp_atr: float
    acceptance_tf_s: int
    max_failure_age_s: float
    max_probe_age_s: float
    probe_excursion_atr: float
    reclaim_buffer_atr: float
    reversal_disp_atr: float
    reversal_eff_min: float
    reversal_tf_s: int
    historical_trades: int


VECTORS = (
    Vector("A03", 0.300000, 15, 40.000000, 20.000000, 0.150000, 0.080000, 0.120000, 0.500000, 5, 306),
    Vector("S05", 0.374062, 15, 9.099416, 6.468982, 0.244588, 0.093793, 0.217011, 0.062661, 5, 51),
    Vector("S06", 0.217738, 5, 59.699117, 23.472260, 0.029179, 0.145085, 0.041213, 0.673017, 1, 615),
    Vector("S09", 0.329294, 15, 41.910749, 10.844137, 0.335024, 0.127350, 0.272984, 0.126644, 1, 119),
    Vector("S10", 0.264160, 5, 20.537168, 19.210606, 0.108825, 0.077129, 0.088265, 0.644213, 5, 206),
    Vector("S16", 0.186080, 5, 31.219954, 3.711492, 0.279091, 0.121753, 0.206212, 0.746067, 5, 24),
)

CHECKPOINT03 = {"A03":187,"S05":9,"S06":617,"S09":9,"S10":206,"S16":8}
CHECKPOINT08 = {
    "onebar_m5": {"A03":187,"S05":9,"S06":617,"S09":9,"S10":206,"S16":8},
    "onebar_rev_atr": {"A03":258,"S05":14,"S06":691,"S09":41,"S10":251,"S16":14},
    "threebar_m5": {"A03":145,"S05":5,"S06":558,"S09":9,"S10":151,"S16":6},
    "threebar_rev_atr": {"A03":247,"S05":10,"S06":672,"S09":41,"S10":225,"S16":14},
}
CHECKPOINT09 = {
    "neutral_current": CHECKPOINT03,
    "neutral_wait_reentry": {"A03":282,"S05":54,"S06":653,"S09":11,"S10":317,"S16":22},
    "stage_current": CHECKPOINT08["threebar_rev_atr"],
    "stage_wait_reentry": {"A03":393,"S05":86,"S06":717,"S09":89,"S10":383,"S16":38},
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def session_code_2026(t: np.ndarray) -> np.ndarray:
    tod = t % DAY_MS
    london_start = np.where(t >= UK_DST_START_2026_MS, 7, 8) * 3_600_000
    london_end = london_start + 8 * 3_600_000 + 30 * 60_000
    ny_start = np.where(t >= US_DST_START_2026_MS, 12, 13) * 3_600_000
    ny_end = ny_start + 9 * 3_600_000
    il = (tod >= london_start) & (tod < london_end)
    iny = (tod >= ny_start) & (tod < ny_end)
    return np.where(il & iny, 2, np.where(il, 1, np.where(iny, 3, 0))).astype(np.int8)


def materialize_p75(t: np.ndarray, src_ask: np.ndarray, src_bid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    session = session_code_2026(t)
    spread = P75_POINTS[session] * TICK_RAW
    mid2 = src_ask.astype(np.int64) + src_bid.astype(np.int64)
    bid = ((mid2 - spread + TICK_RAW) // (2 * TICK_RAW)) * TICK_RAW
    ask = bid + spread
    return ask.astype(np.int64), bid.astype(np.int64)


def load_stage_a(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    df = pd.read_csv(
        path,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        dtype={"timestamp_ms_utc":"int64", "ask_raw":"int64", "bid_raw":"int64"},
    )
    df = df.loc[df["timestamp_ms_utc"] < STAGE_A_END_MS]
    t = df["timestamp_ms_utc"].to_numpy(np.int64)
    if len(t) and np.any(t[1:] < t[:-1]):
        raise ValueError("non-monotonic source ticks")
    ask, bid = materialize_p75(
        t,
        df["ask_raw"].to_numpy(np.int64),
        df["bid_raw"].to_numpy(np.int64),
    )
    return t, ask, bid


def make_bars(t: np.ndarray, mid2: np.ndarray, tf_ms: int) -> dict[str, np.ndarray]:
    bucket = t // int(tf_ms)
    starts = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    ends = np.r_[starts[1:], len(t)]
    open_ = mid2[starts].astype(np.int64)
    close = mid2[ends - 1].astype(np.int64)
    high = np.maximum.reduceat(mid2, starts).astype(np.int64)
    low = np.minimum.reduceat(mid2, starts).astype(np.int64)
    end_ms = ((bucket[starts] + 1) * int(tf_ms)).astype(np.int64)
    return {"start":starts,"end":ends,"end_ms":end_ms,"open":open_,"high":high,"low":low,"close":close}


def atr14(bars: dict[str,np.ndarray]) -> np.ndarray:
    h, l, c = bars["high"], bars["low"], bars["close"]
    tr = (h - l).astype(np.int64)
    if len(tr) > 1:
        tr[1:] = np.maximum(tr[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    cs = np.r_[0, np.cumsum(tr, dtype=np.int64)]
    out = np.zeros(len(tr), dtype=np.float64)
    for i in range(13, len(tr)):
        out[i] = (cs[i+1] - cs[i-13]) / 14.0
    return out


def confirmed_swing_events(m5: dict[str,np.ndarray], width: int = SWING_BARS) -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    """Symmetric swing rule, causally revealed after width right-hand bars complete."""
    hi, lo, end = m5["high"], m5["low"], m5["end_ms"]
    reveal=[]; side=[]; level=[]
    for k in range(width, len(hi)-width):
        h=hi[k]; l=lo[k]
        is_hi=True; is_lo=True
        for j in range(1,width+1):
            if h <= hi[k-j] or h <= hi[k+j]: is_hi=False
            if l >= lo[k-j] or l >= lo[k+j]: is_lo=False
        r = int(end[k+width])
        if is_hi:
            reveal.append(r); side.append(1); level.append(int(h))
        if is_lo:
            reveal.append(r); side.append(-1); level.append(int(l))
    order=np.argsort(np.asarray(reveal,dtype=np.int64),kind="stable")
    return np.asarray(reveal,dtype=np.int64)[order], np.asarray(side,dtype=np.int8)[order], np.asarray(level,dtype=np.int64)[order]


@njit(cache=True)
def _bar_idx(end_ms: np.ndarray, tm: int) -> int:
    return np.searchsorted(end_ms, tm, side="right") - 1


@njit(cache=True)
def detect_vector(
    t, mid2,
    swing_t, swing_side, swing_level,
    m5_end, m5_atr,
    s1_end, s1_open, s1_close, s1_atr,
    s5_end, s5_open, s5_close, s5_atr,
    s15_end, s15_open, s15_close,
    acceptance_disp_atr, acceptance_tf_s,
    max_failure_ms, max_probe_ms, probe_exc_atr, reclaim_atr,
    rev_disp_atr, rev_eff_min, reversal_tf_s,
    eff_bars, rev_atr_mode, wait_reentry_clock,
):
    stage=0; original_side=0; L=0; event_atr=0.0; probe_start=0; failure_start=0
    reentry_seen=False
    latest_hi=0; latest_lo=0; swing_i=0
    hi_eligible=True; lo_eligible=True
    last_acc_bar=-1; last_rev_bar=-1
    counts=np.zeros(8,np.int64)
    sig_i=np.empty(20000,np.int64); sig_side=np.empty(20000,np.int8); sig_event=np.empty(20000,np.int64)
    nsig=0; event_id=0

    for i in range(t.size):
        tm=int(t[i]); px=int(mid2[i])
        while swing_i < swing_t.size and swing_t[swing_i] <= tm:
            if swing_side[swing_i] > 0: latest_hi=int(swing_level[swing_i])
            else: latest_lo=int(swing_level[swing_i])
            swing_i += 1

        jm=_bar_idx(m5_end,tm)
        if jm < 13: continue
        atr_event=float(m5_atr[jm])
        if atr_event <= 0: continue

        if stage == 0:
            if latest_hi and px < latest_hi: hi_eligible=True
            if latest_lo and px > latest_lo: lo_eligible=True
            if latest_hi and hi_eligible and px >= latest_hi:
                stage=1; original_side=1; L=latest_hi; event_atr=atr_event; probe_start=tm
                hi_eligible=False; event_id+=1; counts[0]+=1
            elif latest_lo and lo_eligible and px <= latest_lo:
                stage=1; original_side=-1; L=latest_lo; event_atr=atr_event; probe_start=tm
                lo_eligible=False; event_id+=1; counts[0]+=1
        if stage == 0: continue

        j1=_bar_idx(s1_end,tm); j5=_bar_idx(s5_end,tm); j15=_bar_idx(s15_end,tm)
        jacc=j5 if acceptance_tf_s==5 else j15
        acc_close=s5_close[j5] if acceptance_tf_s==5 and j5>=0 else s15_close[j15] if j15>=0 else 0

        if stage == 1:
            if original_side*(px-L) >= probe_exc_atr*event_atr:
                stage=2; counts[1]+=1
            elif tm-probe_start > max_probe_ms:
                stage=0; original_side=0
                continue
        if stage < 2: continue

        if jacc >= 0 and jacc != last_acc_bar:
            last_acc_bar=jacc
            if original_side*(acc_close-L) >= acceptance_disp_atr*event_atr:
                counts[2]+=1; stage=0; original_side=0
                continue

        recross = original_side*(px-L) < 0
        if stage == 2:
            if tm-probe_start >= max_probe_ms:
                stage=3; counts[3]+=1
                failure_start=0 if wait_reentry_clock else tm
            elif recross:
                stage=3; counts[3]+=1
                failure_start=0 if wait_reentry_clock else tm

        if stage == 3:
            if recross and not reentry_seen:
                reentry_seen=True; counts[4]+=1
                if wait_reentry_clock: failure_start=tm
                stage=4
            elif failure_start and tm-failure_start > max_failure_ms:
                stage=0; original_side=0; reentry_seen=False
                continue
        elif stage >= 4 and failure_start and tm-failure_start > max_failure_ms:
            stage=0; original_side=0; reentry_seen=False
            continue

        if stage < 4: continue

        jrev=j1 if reversal_tf_s==1 else j5
        rev_close=s1_close[j1] if reversal_tf_s==1 and j1>=0 else s5_close[j5] if j5>=0 else 0
        new_rev_bar = jrev >= 0 and jrev != last_rev_bar
        if stage == 4 and new_rev_bar:
            if (-original_side)*(rev_close-L) >= reclaim_atr*event_atr:
                counts[5]+=1; stage=5

        if stage < 5 or not new_rev_bar:
            if new_rev_bar: last_rev_bar=jrev
            continue

        ro = s1_open[j1] if reversal_tf_s==1 else s5_open[j5]
        rc = rev_close
        rev_atr = event_atr
        if rev_atr_mode == 1:
            rev_atr = float(s1_atr[j1]) if reversal_tf_s==1 else float(s5_atr[j5])
        rside=-original_side
        disp=rside*(rc-ro)
        eff=0.0
        if eff_bars <= 1:
            denom=abs(rc-ro)
            eff=1.0 if denom>0 else 0.0
        else:
            starts=jrev-eff_bars+1
            if starts>=0:
                closes=s1_close if reversal_tf_s==1 else s5_close
                net=rside*(closes[jrev]-closes[starts])
                travel=0
                for z in range(starts+1,jrev+1): travel += abs(closes[z]-closes[z-1])
                eff=net/travel if travel>0 else 0.0
        if rev_atr>0 and disp >= rev_disp_atr*rev_atr and eff >= rev_eff_min:
            counts[6]+=1; counts[7]+=1
            if nsig < sig_i.size:
                sig_i[nsig]=i; sig_side[nsig]=rside; sig_event[nsig]=event_id; nsig+=1
            stage=0; original_side=0; reentry_seen=False
        last_rev_bar=jrev

    return counts, sig_i[:nsig], sig_side[:nsig], sig_event[:nsig]


def parity_score(actual: dict[str,int], expected: dict[str,int]) -> dict:
    diffs={k:int(actual[k]-expected[k]) for k in expected}
    return {"exact":all(v==0 for v in diffs.values()),"abs_error":int(sum(abs(v) for v in diffs.values())),"diffs":diffs}


def run(path: Path) -> dict:
    t, ask, bid = load_stage_a(path)
    mid2=ask+bid
    bars={s:make_bars(t,mid2,s*1000) for s in (1,5,15,300)}
    atr={s:atr14(bars[s]) for s in (1,5,300)}
    sw_t,sw_side,sw_level=confirmed_swing_events(bars[300],SWING_BARS)
    profiles={
        "onebar_m5":(1,0,False),
        "onebar_rev_atr":(1,1,False),
        "threebar_m5":(3,0,False),
        "threebar_rev_atr":(3,1,False),
        "neutral_wait_reentry":(1,0,True),
        "stage_wait_reentry":(3,1,True),
    }
    out={"source_file":str(path),"source_sha256":sha256_file(path),"ticks":int(len(t)),"swing_bars":SWING_BARS,"profiles":{}}
    for profile,(eff_bars,rev_atr_mode,wait_reentry) in profiles.items():
        got={}; stages={}
        for v in VECTORS:
            c,si,ss,se=detect_vector(
                t,mid2,sw_t,sw_side,sw_level,
                bars[300]["end_ms"],atr[300],
                bars[1]["end_ms"],bars[1]["open"],bars[1]["close"],atr[1],
                bars[5]["end_ms"],bars[5]["open"],bars[5]["close"],atr[5],
                bars[15]["end_ms"],bars[15]["open"],bars[15]["close"],
                v.acceptance_disp_atr,v.acceptance_tf_s,int(v.max_failure_age_s*1000),int(v.max_probe_age_s*1000),
                v.probe_excursion_atr,v.reclaim_buffer_atr,v.reversal_disp_atr,v.reversal_eff_min,v.reversal_tf_s,
                eff_bars,rev_atr_mode,wait_reentry,
            )
            got[v.name]=int(c[7]); stages[v.name]=[int(x) for x in c]
        expected=(CHECKPOINT09[profile] if profile in CHECKPOINT09 else CHECKPOINT08[profile])
        out["profiles"][profile]={"signals":got,"stages":stages,"expected":expected,"parity":parity_score(got,expected)}
    return out


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    result=run(args.source)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v["parity"] for k,v in result["profiles"].items()},indent=2))


if __name__=="__main__":
    main()
