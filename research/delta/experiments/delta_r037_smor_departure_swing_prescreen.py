"""DELTA R037 SMOR departure-swing prescreen — Checkpoint 17W.

Frozen before official compute:
- exact R037-SMOR-C02 M1 midpoint lifecycle from checkpoint 17H;
- additionally require a causally confirmed same-direction width-2 M1 swing
  after MSS/departure and revealed no later than the first OB midpoint retest;
- first OB interaction still consumes the zone whether or not the new swing
  requirement is satisfied;
- no swing-width, distance, delay, side/session, exit, August, or MQL5 tuning.

This is a source-only causal prescreen under the frozen 30-second execution
contract. It reproduces the 17H C02 proposal fingerprint before evaluating 17W.
Outputs are written atomically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

DAY_MS = 86_400_000
TICK_RAW = 10
PRICE_SCALE = 1000
STAGE_A_START_MS = 1_767_225_600_000
STAGE_A_END_MS = 1_768_737_600_000
US_DST_START_2026_MS = 1_772_953_200_000
UK_DST_START_2026_MS = 1_774_746_000_000
P75_POINTS = np.asarray([20, 20, 21, 21], dtype=np.int64)
CANONICAL_JAN_SHA256 = "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
MAX_SPREAD_RAW = 25 * TICK_RAW
STOP_RAW = int(round(0.30 * PRICE_SCALE))
TRAIL_ACT_RAW = int(round(0.10 * PRICE_SCALE))
TRAIL_DIST_RAW = int(round(0.03 * PRICE_SCALE))
MAX_HOLD_SECONDS = 30


@dataclass(frozen=True)
class Proposal:
    decision_index: int
    side: int
    eligible: bool
    reason: str
    event_bar: int


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent,
            delete=False,
        ) as tmp:
            tmp_name = tmp.name
            json.dump(payload, tmp, indent=2)
            tmp.write("\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass


def session_code(t: np.ndarray) -> np.ndarray:
    tod = t % DAY_MS
    ls = np.where(t >= UK_DST_START_2026_MS, 7, 8) * 3_600_000
    le = ls + 8 * 3_600_000 + 30 * 60_000
    ns = np.where(t >= US_DST_START_2026_MS, 12, 13) * 3_600_000
    ne = ns + 9 * 3_600_000
    il = (tod >= ls) & (tod < le)
    iny = (tod >= ns) & (tod < ne)
    return np.where(il & iny, 2, np.where(il, 1, np.where(iny, 3, 0))).astype(np.int8)


def p75(t: np.ndarray, ask_raw: np.ndarray, bid_raw: np.ndarray):
    sess = session_code(t)
    spread = P75_POINTS[sess] * TICK_RAW
    mid2 = ask_raw.astype(np.int64) + bid_raw.astype(np.int64)
    bid = ((mid2 - spread + TICK_RAW) // (2 * TICK_RAW)) * TICK_RAW
    ask = bid + spread
    return ask.astype(np.int64), bid.astype(np.int64)


def bars(t: np.ndarray, bid: np.ndarray, tf_ms: int = 60_000):
    bucket = t // tf_ms
    st = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    en = np.r_[st[1:], len(t)]
    return {
        "end_ms": ((bucket[st] + 1) * tf_ms).astype(np.int64),
        "open": bid[st].astype(np.int64),
        "close": bid[en - 1].astype(np.int64),
        "high": np.maximum.reduceat(bid, st).astype(np.int64),
        "low": np.minimum.reduceat(bid, st).astype(np.int64),
    }


def swing_high(h: np.ndarray, k: int, w: int = 2) -> bool:
    if k < w or k + w >= len(h):
        return False
    x = h[k]
    return all(x > h[k-j] and x > h[k+j] for j in range(1, w + 1))


def swing_low(l: np.ndarray, k: int, w: int = 2) -> bool:
    if k < w or k + w >= len(l):
        return False
    x = l[k]
    return all(x < l[k-j] and x < l[k+j] for j in range(1, w + 1))


def last_opposite_bar(o, c, lo_exclusive: int, hi_exclusive: int, shift_side: int) -> int:
    for j in range(hi_exclusive - 1, lo_exclusive, -1):
        if shift_side > 0 and int(c[j]) < int(o[j]):
            return j
        if shift_side < 0 and int(c[j]) > int(o[j]):
            return j
    return -1


def finalize_proposal(t, ask, bid, edge_ms: int, side: int, bar_idx: int) -> Proposal:
    ii = int(np.searchsorted(t, int(edge_ms), side="left"))
    if ii >= len(t) or int(t[ii]) >= STAGE_A_END_MS:
        return Proposal(min(ii, len(t) - 1), side, False, "NO_EXECUTABLE_TICK", bar_idx)
    if int(ask[ii] - bid[ii]) > MAX_SPREAD_RAW:
        return Proposal(ii, side, False, "SPREAD_GATE", bar_idx)
    return Proposal(ii, side, True, "ELIGIBLE", bar_idx)


def smor_midpoint_proposals(t, ask, bid, require_departure_swing: bool):
    b = bars(t, bid, 60_000)
    o, h, l, c, e = b["open"], b["high"], b["low"], b["close"], b["end_ms"]

    latest_hi = 0
    latest_lo = 0
    latest_hi_id = -1
    latest_lo_id = -1

    pending_bear = None
    pending_bull = None
    # [mss_index, ob_index, body_low, body_high, departure_swing_confirmed]
    zone_bear = None
    zone_bull = None
    props = []

    for i in range(len(c)):
        edge = int(e[i])
        if edge > STAGE_A_END_MS:
            break

        # Width-2 swings become visible only when the second right bar completes.
        p = i - 2
        new_hi = False
        new_lo = False
        if p >= 2:
            if swing_high(h, p, 2):
                latest_hi = int(h[p])
                latest_hi_id = p
                new_hi = True
            if swing_low(l, p, 2):
                latest_lo = int(l[p])
                latest_lo_id = p
                new_lo = True

        # Departure swing is event-relative and must pivot strictly after MSS.
        if zone_bear is not None and new_lo and p > int(zone_bear[0]):
            zone_bear[4] = True
        if zone_bull is not None and new_hi and p > int(zone_bull[0]):
            zone_bull[4] = True

        candidates = []

        # Existing zones own the first later body interaction. The interaction
        # consumes the zone even if the departure-swing requirement is absent.
        if zone_bear is not None and i > zone_bear[0]:
            _, ob_idx, zlo, zhi, dep_ok = zone_bear
            mid = (zlo + zhi) / 2.0
            touch = int(h[i]) >= zlo and int(l[i]) <= zhi
            if touch:
                valid = int(c[i]) <= mid and int(c[i]) >= zlo
                valid = valid and int(l[i]) <= mid <= int(h[i])
                if require_departure_swing:
                    valid = valid and bool(dep_ok)
                if valid:
                    candidates.append((-1, ob_idx))
                zone_bear = None

        if zone_bull is not None and i > zone_bull[0]:
            _, ob_idx, zlo, zhi, dep_ok = zone_bull
            mid = (zlo + zhi) / 2.0
            touch = int(h[i]) >= zlo and int(l[i]) <= zhi
            if touch:
                valid = int(c[i]) >= mid and int(c[i]) <= zhi
                valid = valid and int(l[i]) <= mid <= int(h[i])
                if require_departure_swing:
                    valid = valid and bool(dep_ok)
                if valid:
                    candidates.append((1, ob_idx))
                zone_bull = None

        # Pending sweep -> first causal MSS -> last opposite-colour body OB.
        if pending_bear is not None and zone_bear is None:
            sw_idx, mss_level, _ = pending_bear
            if i > sw_idx and int(c[i]) < mss_level:
                ob = last_opposite_bar(o, c, sw_idx, i, -1)
                if ob >= 0:
                    zlo = min(int(o[ob]), int(c[ob]))
                    zhi = max(int(o[ob]), int(c[ob]))
                    if zhi > zlo:
                        zone_bear = [i, ob, zlo, zhi, False]
                pending_bear = None

        if pending_bull is not None and zone_bull is None:
            sw_idx, mss_level, _ = pending_bull
            if i > sw_idx and int(c[i]) > mss_level:
                ob = last_opposite_bar(o, c, sw_idx, i, 1)
                if ob >= 0:
                    zlo = min(int(o[ob]), int(c[ob]))
                    zhi = max(int(o[ob]), int(c[ob]))
                    if zhi > zlo:
                        zone_bull = [i, ob, zlo, zhi, False]
                pending_bull = None

        bear_sweep = (
            zone_bear is None and latest_hi_id >= 0 and latest_lo_id >= 0
            and int(h[i]) > latest_hi and int(c[i]) < latest_hi
        )
        bull_sweep = (
            zone_bull is None and latest_lo_id >= 0 and latest_hi_id >= 0
            and int(l[i]) < latest_lo and int(c[i]) > latest_lo
        )

        if bear_sweep and bull_sweep:
            pending_bear = None
            pending_bull = None
        else:
            if bear_sweep:
                pending_bear = (i, latest_lo, latest_lo_id)
            if bull_sweep:
                pending_bull = (i, latest_hi, latest_hi_id)

        if len(candidates) == 1:
            side, ob_idx = candidates[0]
            props.append(finalize_proposal(t, ask, bid, edge, side, ob_idx))

    return props


def q_tick_raw(raw: int, tick: int = TICK_RAW) -> int:
    return ((int(raw) + tick // 2) // tick) * tick


def simulate_source(props, t, ask, bid):
    by_index = {}
    for p in props:
        if p.eligible:
            by_index.setdefault(int(p.decision_index), []).append(p)

    pos = 0
    entry = 0
    stop = 0
    entry_sec = 0
    trades = 0
    official_wins = 0
    raw_positive_wins = 0
    gross_profit = 0.0
    gross_loss = 0.0
    net = 0.0
    blocked_position = 0
    accepted = 0
    long_entries = 0
    short_entries = 0

    for i in range(len(t)):
        tm = int(t[i]); a = int(ask[i]); b = int(bid[i]); sec = tm // 1000
        occupied_start = pos != 0

        # Protective stop first.
        if pos == 1 and b <= stop:
            raw = (b - entry) / PRICE_SCALE
            deal = raw - 0.01
            if deal > 1e-12:
                official_wins += 1
            if raw > 0:
                raw_positive_wins += 1; gross_profit += deal
            else:
                gross_loss += deal
            net += deal
            trades += 1
            pos = 0; entry = 0; stop = 0; entry_sec = 0
        elif pos == -1 and a >= stop:
            raw = (entry - a) / PRICE_SCALE
            deal = raw - 0.01
            if deal > 1e-12:
                official_wins += 1
            if raw > 0:
                raw_positive_wins += 1; gross_profit += deal
            else:
                gross_loss += deal
            net += deal
            trades += 1
            pos = 0; entry = 0; stop = 0; entry_sec = 0

        if pos != 0:
            if sec - entry_sec >= MAX_HOLD_SECONDS:
                raw = ((b - entry) if pos == 1 else (entry - a)) / PRICE_SCALE
                deal = raw - 0.01
                if deal > 1e-12:
                    official_wins += 1
                if raw > 0:
                    raw_positive_wins += 1; gross_profit += deal
                else:
                    gross_loss += deal
                net += deal
                trades += 1
                pos = 0; entry = 0; stop = 0; entry_sec = 0
            else:
                fav = (b - entry) if pos == 1 else (entry - a)
                if fav >= TRAIL_ACT_RAW:
                    ns = q_tick_raw(b - TRAIL_DIST_RAW if pos == 1 else a + TRAIL_DIST_RAW)
                    if (pos == 1 and ns > stop) or (pos == -1 and ns < stop):
                        stop = ns

        evs = by_index.get(i)
        if evs:
            # SMOR generator emits at most one direction per completed bar.
            for p in evs:
                if occupied_start or pos != 0:
                    blocked_position += 1
                    continue
                pos = int(p.side)
                entry = a if pos == 1 else b
                entry_sec = sec
                stop = q_tick_raw(b - STOP_RAW if pos == 1 else a + STOP_RAW)
                net -= 0.01
                gross_loss -= 0.01
                accepted += 1
                if pos == 1: long_entries += 1
                else: short_entries += 1

    if pos != 0 and len(t):
        a = int(ask[-1]); b = int(bid[-1])
        raw = ((b - entry) if pos == 1 else (entry - a)) / PRICE_SCALE
        deal = raw - 0.01
        if deal > 1e-12: official_wins += 1
        if raw > 0:
            raw_positive_wins += 1; gross_profit += deal
        else:
            gross_loss += deal
        net += deal; trades += 1

    return {
        "accepted_entries": int(accepted),
        "blocked_position": int(blocked_position),
        "trades": int(trades),
        "official_wins": int(official_wins),
        "raw_positive_wins": int(raw_positive_wins),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "direct_net_usd": round(net, 2),
        "long_entries": int(long_entries),
        "short_entries": int(short_entries),
    }


def supply(props, t):
    eligible = [p for p in props if p.eligible]
    return {
        "proposals": len(props),
        "eligible": len(eligible),
        "distinct_days": len({int(t[p.decision_index] // DAY_MS) for p in eligible}),
        "long": sum(p.side > 0 for p in eligible),
        "short": sum(p.side < 0 for p in eligible),
        "spread_rejected": sum(p.reason == "SPREAD_GATE" for p in props),
        "no_tick_rejected": sum(p.reason == "NO_EXECUTABLE_TICK" for p in props),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    sha = sha256_file(a.source)
    if sha != CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: " + sha)

    df = pd.read_csv(
        a.source, compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"], dtype=np.int64,
    )
    df = df[(df.timestamp_ms_utc >= STAGE_A_START_MS) & (df.timestamp_ms_utc < STAGE_A_END_MS)]
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size != 4_205_709 or np.any(t[1:] < t[:-1]):
        raise SystemExit(f"Stage-A chronology mismatch: {t.size}")

    ask, bid = p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))

    control_props = smor_midpoint_proposals(t, ask, bid, False)
    control_supply = supply(control_props, t)
    expected_control = {"proposals": 11, "eligible": 11, "distinct_days": 6, "long": 1, "short": 10}
    for k, v in expected_control.items():
        if control_supply[k] != v:
            raise SystemExit(f"17H C02 control mismatch {k}: {control_supply[k]} != {v}")
    control_exec = simulate_source(control_props, t, ask, bid)

    candidate_props = smor_midpoint_proposals(t, ask, bid, True)
    candidate_supply = supply(candidate_props, t)
    candidate_exec = simulate_source(candidate_props, t, ask, bid)

    gate = {
        "minimum_proposals_8": candidate_supply["proposals"] >= 8,
        "minimum_distinct_days_4": candidate_supply["distinct_days"] >= 4,
        "direct_net_min_minus_2": candidate_exec["direct_net_usd"] >= -2.0,
    }
    gate["prescreen_pass"] = all(gate.values())
    strong = gate["prescreen_pass"] and candidate_exec["direct_net_usd"] >= 0.0

    out = {
        "schema": "delta-r037-smor-departure-swing-prescreen-17w-v1",
        "status": "COMPLETE_PRESCREEN",
        "unit": "R037_SMOR_DEPARTURE_SWING_PRESCREEN_CHECKPOINT_17W",
        "family": "R037-SMOR-DS-v1",
        "source_sha256": sha,
        "stage_a_ticks": int(t.size),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "parent_clue": "R037-SMOR-C02_M1_MIDPOINT",
        "numeric_retuning": False,
        "post_result_retuning": False,
        "august_accessed": False,
        "control_17h_c02": {"supply": control_supply, "source_only_execution": control_exec},
        "candidate_17w": {"supply": candidate_supply, "source_only_execution": candidate_exec},
        "gate": gate,
        "strong_prescreen_pass": bool(strong),
        "finding": {
            "interpretation": "Require a causally confirmed same-direction width-2 M1 swing after MSS/departure and before the first OB midpoint retest.",
            "decision": "ADVANCE_TO_INDEPENDENT_VALIDATION" if strong else ("KEEP_AS_SCREEN_SURVIVOR" if gate["prescreen_pass"] else "RETIRE_NO_RETUNE"),
        },
        "mql5_authorized": False,
    }
    atomic_write_json(a.output, out)
    print(json.dumps({"control": out["control_17h_c02"], "candidate": out["candidate_17w"], "gate": gate, "strong": strong}, separators=(",", ":")))


if __name__ == "__main__":
    main()
