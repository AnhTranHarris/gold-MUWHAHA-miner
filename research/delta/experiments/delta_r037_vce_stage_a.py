"""DELTA R037 volatility-compression/expansion independent entry-source screen.

Bounded Stage-A discovery unit. Four source-grounded candidates are frozen before
compute. No threshold optimization, no post-result retuning, no August, no MQL5.

Candidate sources / semantics:
- ORION core: M5 15-bar box; box height < 2.5 * ATR14; first completed M5 close
  beyond frozen box; stale after 45 M5 bars. C02 adds EMA150 direction alignment.
- BB/KC squeeze: completed M5 BB20/2.0 fully inside KC EMA20 +/- 1.5*ATR20 on
  prior bar; current bar releases and closes beyond current KC. C04 additionally
  requires 12-bar close momentum to agree with breakout direction.

Every proposal enters on the first executable tick at/after the completed signal
bar edge, subject to the frozen <=25-point spread gate. One event is consumed at
its first causal decision; no VCE rearm or deferral.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import delta_r037_sorb_c04_dual30_independent_validation as val

STAGE_A_START_MS = 1_767_225_600_000
STAGE_A_END_MS = 1_768_737_600_000
TF_MS = 300_000
MAX_SPREAD_RAW = 25 * 10

CONFIGS = (
    "R037-VCE-C01_ORION_M5_BOX15",
    "R037-VCE-C02_ORION_M5_BOX15_EMA150",
    "R037-VCE-C03_BBKC_RELEASE",
    "R037-VCE-C04_BBKC_RELEASE_MOM12",
)


@dataclass(frozen=True)
class Proposal:
    decision_index: int
    side: int
    event_kind: str
    event_bar: int
    eligible: bool
    reason: str


def bars(t: np.ndarray, bid: np.ndarray, tf: int = TF_MS):
    bucket = t // tf
    st = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    en = np.r_[st[1:], len(t)]
    return {
        "end_ms": ((bucket[st] + 1) * tf).astype(np.int64),
        "open": bid[st].astype(np.int64),
        "close": bid[en - 1].astype(np.int64),
        "high": np.maximum.reduceat(bid, st).astype(np.int64),
        "low": np.minimum.reduceat(bid, st).astype(np.int64),
    }


def atr(b, period: int) -> np.ndarray:
    h, l, c = b["high"], b["low"], b["close"]
    tr = (h - l).astype(np.float64)
    if len(tr) > 1:
        tr[1:] = np.maximum(tr[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    out = np.full(len(tr), np.nan, np.float64)
    if len(tr) >= period:
        cs = np.r_[0.0, np.cumsum(tr)]
        out[period - 1:] = (cs[period:] - cs[:-period]) / period
    return out


def ema(x: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(x), np.nan, np.float64)
    if len(x) < period:
        return out
    alpha = 2.0 / (period + 1.0)
    seed = float(np.mean(x[:period]))
    out[period - 1] = seed
    for i in range(period, len(x)):
        out[i] = alpha * float(x[i]) + (1.0 - alpha) * out[i - 1]
    return out


def sma_std(x: np.ndarray, period: int):
    mean = np.full(len(x), np.nan, np.float64)
    std = np.full(len(x), np.nan, np.float64)
    if len(x) < period:
        return mean, std
    xf = x.astype(np.float64)
    cs = np.r_[0.0, np.cumsum(xf)]
    cs2 = np.r_[0.0, np.cumsum(xf * xf)]
    for i in range(period - 1, len(x)):
        s = cs[i + 1] - cs[i + 1 - period]
        s2 = cs2[i + 1] - cs2[i + 1 - period]
        m = s / period
        v = max(0.0, s2 / period - m * m)
        mean[i] = m
        std[i] = np.sqrt(v)
    return mean, std


def decision_index(t: np.ndarray, edge_ms: int) -> int:
    return int(np.searchsorted(t, edge_ms, side="left"))


def finalize_proposal(t, ask, bid, edge_ms, side, kind, bar_idx, source_ok=True, source_reason="ELIGIBLE"):
    ii = decision_index(t, int(edge_ms))
    if ii >= len(t) or int(t[ii]) >= STAGE_A_END_MS:
        return Proposal(min(ii, len(t) - 1), side, kind, bar_idx, False, "NO_EXECUTABLE_TICK")
    if not source_ok:
        return Proposal(ii, side, kind, bar_idx, False, source_reason)
    if int(ask[ii] - bid[ii]) > MAX_SPREAD_RAW:
        return Proposal(ii, side, kind, bar_idx, False, "SPREAD_GATE")
    return Proposal(ii, side, kind, bar_idx, True, "ELIGIBLE")


def orion_proposals(t, ask, bid, use_ema: bool):
    b = bars(t, bid)
    a14 = atr(b, 14)
    e150 = ema(b["close"], 150)
    props = []
    active = False
    hi = lo = 0
    expiry = -1

    for k in range(len(b["close"])):
        if int(b["end_ms"][k]) > STAGE_A_END_MS:
            break

        if active:
            if k > expiry:
                active = False
            else:
                c = int(b["close"][k])
                side = 1 if c > hi else (-1 if c < lo else 0)
                if side:
                    source_ok = True
                    reason = "ELIGIBLE"
                    if use_ema:
                        if np.isnan(e150[k]):
                            source_ok = False
                            reason = "EMA_NOT_READY"
                        elif (side > 0 and c <= e150[k]) or (side < 0 and c >= e150[k]):
                            source_ok = False
                            reason = "EMA150_DIRECTION"
                    props.append(finalize_proposal(
                        t, ask, bid, b["end_ms"][k], side,
                        "ORION_BOX15_EMA150" if use_ema else "ORION_BOX15",
                        k, source_ok, reason,
                    ))
                    active = False

        if (not active) and k >= 14 and not np.isnan(a14[k]):
            wh = int(np.max(b["high"][k - 14:k + 1]))
            wl = int(np.min(b["low"][k - 14:k + 1]))
            if float(wh - wl) < 2.5 * float(a14[k]):
                active = True
                hi, lo = wh, wl
                expiry = k + 45

    return props


def bbkc_proposals(t, ask, bid, require_mom12: bool):
    b = bars(t, bid)
    close = b["close"].astype(np.float64)
    mean20, sd20 = sma_std(b["close"], 20)
    atr20 = atr(b, 20)
    ema20 = ema(b["close"], 20)
    bb_u = mean20 + 2.0 * sd20
    bb_l = mean20 - 2.0 * sd20
    kc_u = ema20 + 1.5 * atr20
    kc_l = ema20 - 1.5 * atr20
    squeeze = (bb_u < kc_u) & (bb_l > kc_l)
    props = []
    for k in range(20, len(close)):
        if int(b["end_ms"][k]) > STAGE_A_END_MS:
            break
        if not (bool(squeeze[k - 1]) and not bool(squeeze[k])):
            continue
        side = 1 if close[k] > kc_u[k] else (-1 if close[k] < kc_l[k] else 0)
        if side == 0:
            continue
        source_ok = True
        reason = "ELIGIBLE"
        if require_mom12:
            mom = close[k] - close[k - 12]
            if (side > 0 and mom <= 0) or (side < 0 and mom >= 0):
                source_ok = False
                reason = "MOM12_DIRECTION"
        props.append(finalize_proposal(
            t, ask, bid, b["end_ms"][k], side,
            "BBKC_RELEASE_MOM12" if require_mom12 else "BBKC_RELEASE",
            k, source_ok, reason,
        ))
    return props


def generate_proposals(t, ask, bid, cid: str):
    if cid == CONFIGS[0]:
        return orion_proposals(t, ask, bid, False)
    if cid == CONFIGS[1]:
        return orion_proposals(t, ask, bid, True)
    if cid == CONFIGS[2]:
        return bbkc_proposals(t, ask, bid, False)
    if cid == CONFIGS[3]:
        return bbkc_proposals(t, ask, bid, True)
    raise ValueError(cid)


def supply(props):
    eligible = [p for p in props if p.eligible]
    return {
        "proposals": len(props),
        "source_eligible": len(eligible),
        "distinct_days": 0,
        "proposal_long": sum(p.side > 0 for p in props),
        "proposal_short": sum(p.side < 0 for p in props),
        "source_rejections": {r: sum(p.reason == r for p in props) for r in (
            "EMA_NOT_READY", "EMA150_DIRECTION", "MOM12_DIRECTION", "SPREAD_GATE", "NO_EXECUTABLE_TICK"
        )},
    }


def supply_with_days(props, t):
    s = supply(props)
    s["distinct_days"] = len({int(t[p.decision_index] // 86_400_000) for p in props if 0 <= p.decision_index < len(t)})
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    sha = val.base.sha256_file(a.source)
    if sha != val.base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: " + sha)

    df = pd.read_csv(a.source, compression="gzip", usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"], dtype=np.int64)
    df = df[(df.timestamp_ms_utc >= STAGE_A_START_MS) & (df.timestamp_ms_utc < STAGE_A_END_MS)]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size != 4_205_709 or np.any(t[1:] < t[:-1]):
        raise SystemExit(f"Stage-A chronology mismatch: {t.size}")

    ask, bid = val.base.p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))
    feat = val.parent.build_parent_features(t, ask, bid)
    streams = val.generate_streams(t, ask, bid)
    d3t, d3s = streams["DH03_S06"]
    d5t, d5s = streams["DH05_S06"]
    s11t, s11s = streams["DH02_S11"]
    s08t, s08s = streams["DH02_S08"]
    zi = np.empty(0, np.int64)
    zs = np.empty(0, np.int8)

    parent = val.pack_sorb(val.run_integrated_sorb(
        t, ask, bid, feat["impulse250"], feat["h1_netatr"], feat["m30_netatr"],
        d3t, d3s, d5t, d5s, s11t, s11s, s08t, s08s,
        zi, zs, zs, 1, 1, 1, 1, 1,
    ))
    val.parent_gate(parent)

    results = {}
    ranking = []
    for cid in CONFIGS:
        props = generate_proposals(t, ask, bid, cid)
        sp = supply_with_days(props, t)
        ep = [p for p in props if p.eligible]
        ii = np.asarray([p.decision_index for p in ep], np.int64)
        ss = np.asarray([p.side for p in ep], np.int8)
        sk = np.ones(len(ep), np.int8)
        combined = val.pack_sorb(val.run_integrated_sorb(
            t, ask, bid, feat["impulse250"], feat["h1_netatr"], feat["m30_netatr"],
            d3t, d3s, d5t, d5s, s11t, s11s, s08t, s08s,
            ii, ss, sk, 1, 1, 1, 1, 1,
        ))
        dec = val.decision(parent, combined, sp)
        direct = combined.pop("sorb_session_contribution")
        combined["vce_entries"] = combined.pop("sorb_entries")
        combined["vce_net"] = combined.pop("sorb_net")
        combined["vce_source_contribution"] = direct["LONDON"]
        dec["incremental_net_per_vce_entry"] = dec.pop("incremental_net_per_sorb_entry")
        results[cid] = {"supply": sp, "combined": combined, "decision": dec}
        ranking.append((
            int(dec["strong_screen_pass"]), int(dec["screen_pass"]),
            float(dec["net_delta"]), int(dec["official_win_delta"]),
            int(combined["vce_entries"]), cid,
        ))

    ranking.sort(reverse=True)
    leaders = [{
        "config_id": x[-1],
        "strong_screen_pass": results[x[-1]]["decision"]["strong_screen_pass"],
        "screen_pass": results[x[-1]]["decision"]["screen_pass"],
        "net_delta": results[x[-1]]["decision"]["net_delta"],
        "trade_delta": results[x[-1]]["decision"]["trade_delta"],
        "official_win_delta": results[x[-1]]["decision"]["official_win_delta"],
        "accepted_entries": results[x[-1]]["combined"]["vce_entries"],
        "direct_vce_net": results[x[-1]]["combined"]["vce_net"],
    } for x in ranking]
    strong = [x for x in leaders if x["strong_screen_pass"]]

    out = {
        "schema": "delta-r037-vce-stage-a-screen-17a-v1",
        "status": "COMPLETE_STAGE_A_SCREEN",
        "unit": "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        "family": "R037-VCE-v1",
        "parent_checkpoint": "R037_PLSR_C01_MONTHLY_VALIDATION_CHECKPOINT_16C",
        "surrogate_parent": "14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
        "promotable": False,
        "source_sha256": sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "numeric_retuning": False,
        "post_result_retuning": False,
        "august_accessed": False,
        "parent_control": parent,
        "configs": results,
        "ranking": leaders,
        "finding": {
            "strong_screen_survivors": [x["config_id"] for x in strong],
            "leading_config": leaders[0]["config_id"],
            "next": "R037_VCE_LEADER_INDEPENDENT_LATER_JAN_VALIDATION" if strong else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST",
        },
        "mql5_authorized": False,
    }
    val.base.atomic_write_json(a.output, out)
    print(json.dumps({"ranking": leaders, "finding": out["finding"]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
