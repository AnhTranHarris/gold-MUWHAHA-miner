"""DELTA R037 Session-Owned Opening-Range Breakout (SORB).

Research-only producing source. This module generates causal first-entry proposals
and can run a standalone lifecycle QA. Official R037 promotion metrics require
chronological integration with the exact R032-C03 control ledger.

Hard invariants:
- ordered tick stream is chronology;
- Bid defines opening-range and completed-S5 confirmation geometry;
- BUY executes Ask / exits Bid; SELL executes Bid / exits Ask;
- first confirmation attempt consumes the named session even if rejected;
- no post-exit rearm or deferred retry;
- no August access.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
import numpy as np

DAY_MS = 86_400_000
S5_MS = 5_000
PRICE_SCALE = 1000
TICK_RAW = 10
US_DST_START_2026_MS = 1_772_953_200_000  # 2026-03-08 07:00 UTC
UK_DST_START_2026_MS = 1_774_746_000_000  # 2026-03-29 01:00 UTC
STAGE_A_START_MS = 1_767_225_600_000
STAGE_A_END_MS = 1_768_737_600_000

P75_POINTS = (20, 20, 21, 21)  # OFF, LONDON, OVERLAP, NEW_YORK

CONFIGS: Dict[str, dict] = {
    "R037-C01_LONDON_15": dict(sessions=("LONDON",), range_minutes=15, confirm_closes=1, expiry_minutes=120),
    "R037-C02_COMEX_15": dict(sessions=("COMEX_GOLD",), range_minutes=15, confirm_closes=1, expiry_minutes=120),
    "R037-C03_DUAL_15": dict(sessions=("LONDON","COMEX_GOLD"), range_minutes=15, confirm_closes=1, expiry_minutes=120),
    "R037-C04_DUAL_30": dict(sessions=("LONDON","COMEX_GOLD"), range_minutes=30, confirm_closes=1, expiry_minutes=120),
    "R037-C05_DUAL_15_CONFIRM2": dict(sessions=("LONDON","COMEX_GOLD"), range_minutes=15, confirm_closes=2, expiry_minutes=120),
}

@dataclass(frozen=True)
class Proposal:
    config_id: str
    session: str
    utc_day_ms: int
    range_start_ms: int
    range_end_ms: int
    expiry_ms: int
    or_high_raw: int
    or_low_raw: int
    confirm_bar_end_ms: int
    decision_index: int
    decision_ms: int
    side: int
    bid_raw: int
    ask_raw: int
    spread_points: int
    eligible: bool
    reason: str

def _session_code_2026(t_ms: np.ndarray) -> np.ndarray:
    """Vectorized DELTA/Coinexx session code: 0 OFF,1 LONDON,2 OVERLAP,3 NY."""
    t = np.asarray(t_ms, dtype=np.int64)
    tod = t % DAY_MS
    london_start = np.where(t >= UK_DST_START_2026_MS, 7, 8) * 3_600_000
    london_end = london_start + 8 * 3_600_000 + 30 * 60_000
    ny_start = np.where(t >= US_DST_START_2026_MS, 12, 13) * 3_600_000
    ny_end = ny_start + 9 * 3_600_000
    il = (tod >= london_start) & (tod < london_end)
    iny = (tod >= ny_start) & (tod < ny_end)
    return np.where(il & iny, 2, np.where(il, 1, np.where(iny, 3, 0))).astype(np.int8)

def materialize_p75(t_ms: np.ndarray, src_ask_raw: np.ndarray, src_bid_raw: np.ndarray) -> Tuple[np.ndarray,np.ndarray]:
    """Mirror DELTA_004 Coinexx-like P75 midpoint-preserving quote transform."""
    t = np.asarray(t_ms, dtype=np.int64)
    sa = np.asarray(src_ask_raw, dtype=np.int64)
    sb = np.asarray(src_bid_raw, dtype=np.int64)
    session = _session_code_2026(t)
    spread = np.take(np.asarray(P75_POINTS, dtype=np.int64), session) * TICK_RAW
    mid2 = sa + sb
    # Existing DELTA half-up tick quantizer.
    bid = ((mid2 - spread + TICK_RAW) // (2 * TICK_RAW)) * TICK_RAW
    ask = bid + spread
    return ask.astype(np.int32), bid.astype(np.int32)

def _session_start_utc(day_ms: int, session: str) -> int:
    # Noon probe correctly resolves 2026 DST-transition days for these morning sessions.
    probe = day_ms + 12 * 3_600_000
    if session == "LONDON":
        mins = 420 if probe >= UK_DST_START_2026_MS else 480
    elif session == "COMEX_GOLD":
        mins = 740 if probe >= US_DST_START_2026_MS else 800
    else:
        raise KeyError(session)
    return int(day_ms + mins * 60_000)

def _first_confirmation(
    t: np.ndarray, ask: np.ndarray, bid: np.ndarray,
    start_i: int, end_i: int, or_high: int, or_low: int, need: int
) -> Tuple[int,int,int]:
    """Return (decision_index, side, confirm_bar_end_ms), or (-1,0,0).

    Only observed S5 bars count. The prior completed observed bar is evaluated at
    the first tick of a later S5 bucket, so decision chronology is causal.
    """
    if start_i >= end_i:
        return -1, 0, 0
    bucket = int(t[start_i] // S5_MS)
    close = int(bid[start_i])
    consec_side = 0
    consec_n = 0
    for i in range(start_i + 1, end_i):
        b = int(t[i] // S5_MS)
        if b == bucket:
            close = int(bid[i])
            continue
        side = 1 if close > or_high else -1 if close < or_low else 0
        if side == 0:
            consec_side, consec_n = 0, 0
        elif side == consec_side:
            consec_n += 1
        else:
            consec_side, consec_n = side, 1
        if consec_n >= need:
            return i, side, (bucket + 1) * S5_MS
        bucket = b
        close = int(bid[i])
    return -1, 0, 0

def generate_proposals(
    t_ms: np.ndarray, ask_raw: np.ndarray, bid_raw: np.ndarray, config_id: str,
    start_ms: int = STAGE_A_START_MS, end_ms: int = STAGE_A_END_MS
) -> List[Proposal]:
    if config_id not in CONFIGS:
        raise KeyError(config_id)
    t = np.asarray(t_ms, dtype=np.int64)
    ask = np.asarray(ask_raw, dtype=np.int64)
    bid = np.asarray(bid_raw, dtype=np.int64)
    if not (len(t) == len(ask) == len(bid)):
        raise ValueError("tick arrays length mismatch")
    if len(t) and np.any(t[1:] < t[:-1]):
        raise ValueError("tick chronology not monotonic")
    cfg = CONFIGS[config_id]
    first_day = (start_ms // DAY_MS) * DAY_MS
    last_day = ((end_ms - 1) // DAY_MS) * DAY_MS
    out: List[Proposal] = []
    for day in range(int(first_day), int(last_day) + 1, DAY_MS):
        for session in cfg["sessions"]:
            rs = _session_start_utc(day, session)
            re = rs + int(cfg["range_minutes"]) * 60_000
            ex = re + int(cfg["expiry_minutes"]) * 60_000
            if re <= start_ms or rs >= end_ms:
                continue
            rs = max(rs, start_ms)
            ex = min(ex, end_ms)
            i0 = int(np.searchsorted(t, rs, side="left"))
            i1 = int(np.searchsorted(t, re, side="left"))
            ix = int(np.searchsorted(t, ex, side="left"))
            if i1 <= i0 or ix <= i1:
                continue
            hi = int(np.max(bid[i0:i1]))
            lo = int(np.min(bid[i0:i1]))
            di, side, bend = _first_confirmation(t, ask, bid, i1, ix, hi, lo, int(cfg["confirm_closes"]))
            if di < 0:
                continue
            spread_points = int((int(ask[di]) - int(bid[di])) // TICK_RAW)
            still_out = int(bid[di]) > hi if side > 0 else int(bid[di]) < lo
            spread_ok = spread_points <= 25
            eligible = bool(still_out and spread_ok)
            reason = "ELIGIBLE" if eligible else ("REENTERED_RANGE" if not still_out else "SPREAD_GATE")
            out.append(Proposal(
                config_id, session, day, rs, re, ex, hi, lo, bend,
                di, int(t[di]), side, int(bid[di]), int(ask[di]),
                spread_points, eligible, reason
            ))
    out.sort(key=lambda x: (x.decision_ms, x.session))
    return out

def _q_tick(raw: int) -> int:
    return ((int(raw) + TICK_RAW // 2) // TICK_RAW) * TICK_RAW

def standalone_lifecycle_qa(
    t_ms: np.ndarray, ask_raw: np.ndarray, bid_raw: np.ndarray,
    proposals: Iterable[Proposal], end_ms: int = STAGE_A_END_MS
) -> dict:
    """Frozen R9 lifecycle on eligible SORB proposals only.

    This is a code/source QA surface, NOT an integrated R037 candidate result.
    """
    t = np.asarray(t_ms, dtype=np.int64)
    ask = np.asarray(ask_raw, dtype=np.int64)
    bid = np.asarray(bid_raw, dtype=np.int64)
    ledger = []
    gp = 0.0
    gl = 0.0
    balance = 100000.0
    bpeak = balance
    max_bdd = 0.0
    wins = losses = 0
    last_exit_i = -1

    for p in proposals:
        if not p.eligible or p.decision_index <= last_exit_i:
            continue
        i0 = p.decision_index
        side = p.side
        entry = int(ask[i0]) if side > 0 else int(bid[i0])
        stop = _q_tick((int(bid[i0]) - 300) if side > 0 else (int(ask[i0]) + 300))
        entry_sec = int(t[i0] // 1000)
        gl -= 0.01
        balance -= 0.01
        exit_i = -1
        exit_raw = 0
        exit_reason = ""
        raw_pnl = 0.0
        for i in range(i0 + 1, len(t)):
            if int(t[i]) >= end_ms:
                break
            if side > 0 and int(bid[i]) <= stop:
                exit_i = i; exit_raw = int(bid[i]); exit_reason = "STOP"; break
            if side < 0 and int(ask[i]) >= stop:
                exit_i = i; exit_raw = int(ask[i]); exit_reason = "STOP"; break
            sec = int(t[i] // 1000)
            if sec - entry_sec >= 30:
                exit_i = i; exit_raw = int(bid[i]) if side > 0 else int(ask[i]); exit_reason = "MAX_HOLD"; break
            fav = (int(bid[i]) - entry) if side > 0 else (entry - int(ask[i]))
            if fav >= 100:
                ns = _q_tick(int(bid[i]) - 30 if side > 0 else int(ask[i]) + 30)
                if (side > 0 and ns > stop) or (side < 0 and ns < stop):
                    stop = ns
        if exit_i < 0:
            j = min(len(t)-1, max(i0, int(np.searchsorted(t, end_ms, side="left"))-1))
            exit_i = j; exit_raw = int(bid[j]) if side > 0 else int(ask[j]); exit_reason = "FORCE_END"
        raw_pnl = ((exit_raw-entry) if side > 0 else (entry-exit_raw)) / PRICE_SCALE
        exit_deal = raw_pnl - 0.01
        if raw_pnl > 0:
            wins += 1; gp += exit_deal
        else:
            losses += 1; gl += exit_deal
        balance += exit_deal
        bpeak = max(bpeak, balance)
        max_bdd = max(max_bdd, bpeak - balance)
        last_exit_i = exit_i
        ledger.append({
            "session":p.session, "entry_ms":p.decision_ms, "side":side,
            "entry_price":entry/PRICE_SCALE, "exit_ms":int(t[exit_i]),
            "exit_price":exit_raw/PRICE_SCALE, "raw_pnl":raw_pnl,
            "net_after_exit_commission":exit_deal-0.01,
            "reason":exit_reason
        })
    return {
        "status":"CODE_QA_SOURCE_SCREEN_ONLY_NOT_R037_REPLAY",
        "trades":len(ledger), "wins":wins, "losses":losses,
        "gross_profit":round(gp, 10), "gross_loss":round(gl, 10),
        "net_profit":round(gp+gl, 10), "max_balance_dd":round(max_bdd, 10),
        "ledger":ledger
    }
