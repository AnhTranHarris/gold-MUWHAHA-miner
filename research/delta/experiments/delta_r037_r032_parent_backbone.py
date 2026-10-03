"""DELTA R037 clean-room reconstruction of the R032 non-specialist parent backbone.

Purpose
-------
Rebuild and parity-check the exact Stage-A P75 sequence:
R9 -> P01 ownership -> M30_KEEP_OWNED -> GLOBAL NO_REARM.

This is research infrastructure for R037. It does not implement the four R032
specialist streams and therefore is not itself R032-C03.

Frozen definitions
------------------
P01:
    I250 <= -0.55 OR H1NetATR > 0.35
    -> flip R9 intended side, own trade, suppress ordinary same-minute rearm.

M30-only:
    M30NetATR > 0.35 AND NOT(P01)
    -> keep intended side, own trade, suppress ordinary same-minute rearm.

GLOBAL NO_REARM:
    suppress ordinary generic same-minute rearms after all unowned exits too.

Later R024/R032 "wins" use exit-deal-positive counting:
    raw_trade_pnl - 0.01 exit commission > 0.
Gross-profit/loss accounting remains the frozen R9 deal accounting.
"""
from __future__ import annotations

import numpy as np
from numba import njit

from research.delta.lab.coinexx_r9_adapter import (
    DAY_MS,
    US_DST_START_2026_MS,
    UK_DST_START_2026_MS,
    _q_half_raw2_to_tick,
    _q_tick_raw,
    _session_2026,
)


def completed_bar_netatr(
    t_ms: np.ndarray,
    ask_raw: np.ndarray,
    bid_raw: np.ndarray,
    tf_ms: int,
    n_net: int = 3,
    atr_n: int = 14,
) -> np.ndarray:
    """Completed-bar DirectionalDisplacement_T(n) on midpoint price.

    Feature at tick i uses only bars whose right edge is <= t_i.
    """
    t = np.asarray(t_ms, dtype=np.int64)
    a = np.asarray(ask_raw, dtype=np.int64)
    b = np.asarray(bid_raw, dtype=np.int64)
    mid2 = a + b

    bucket = t // int(tf_ms)
    starts = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    ends = np.r_[starts[1:], len(t)]
    bar_bucket = bucket[starts]

    close = mid2[ends - 1].astype(np.int64)
    high = np.maximum.reduceat(mid2, starts).astype(np.int64)
    low = np.minimum.reduceat(mid2, starts).astype(np.int64)

    tr = high - low
    if len(tr) > 1:
        tr[1:] = np.maximum(
            tr[1:],
            np.maximum(np.abs(high[1:] - close[:-1]), np.abs(low[1:] - close[:-1])),
        )

    cs = np.concatenate(([0], np.cumsum(tr, dtype=np.int64)))
    feat = np.full(len(close), np.nan, dtype=np.float64)

    first = max(atr_n - 1, n_net)
    for j in range(first, len(close)):
        atr = (cs[j + 1] - cs[j + 1 - atr_n]) / float(atr_n)
        if atr > 0:
            feat[j] = (close[j] - close[j - n_net]) / atr

    bar_end = (bar_bucket + 1) * int(tf_ms)
    idx = np.searchsorted(bar_end, t, side="right") - 1
    out = np.full(len(t), np.nan, dtype=np.float32)
    ok = idx >= 0
    out[ok] = feat[idx[ok]].astype(np.float32)
    return out


def bidask_impulse_250ms(
    t_ms: np.ndarray,
    ask_raw: np.ndarray,
    bid_raw: np.ndarray,
) -> np.ndarray:
    """DH-06 BidAskImpulse over the causal prior 250 ms window."""
    t = np.asarray(t_ms, dtype=np.int64)
    a = np.asarray(ask_raw, dtype=np.int64)
    b = np.asarray(bid_raw, dtype=np.int64)

    step_abs = np.zeros(len(t), dtype=np.int64)
    if len(t) > 1:
        step_abs[1:] = np.abs(np.diff(b)) + np.abs(np.diff(a))
    prefix = np.cumsum(step_abs, dtype=np.int64)

    j = np.searchsorted(t, t - 250, side="left")
    denom = prefix - prefix[j]
    numer = (b - b[j]) + (a - a[j])

    out = np.zeros(len(t), dtype=np.float32)
    ok = denom > 0
    out[ok] = (numer[ok] / denom[ok]).astype(np.float32)
    return out


@njit(cache=True)
def run_parent_backbone(
    t,
    ask,
    bid,
    impulse250,
    h1_netatr,
    m30_netatr,
    mode,
    global_no_rearm=False,
    price_scale=1000,
    trade_start_ms=0,
):
    """Run P01 (mode=1) or M30_KEEP_OWNED (mode=2)."""
    tick = max(1, int(round(0.01 * price_scale)))
    half = int(round(0.15 * price_scale))
    stopd = int(round(0.30 * price_scale))
    trail_activation = int(round(0.10 * price_scale))
    trail_distance = int(round(0.03 * price_scale))
    min_range = int(round(0.50 * price_scale))
    min_disp = int(round(0.15 * price_scale))

    # Completed-S1 R9 quality ring.
    h = np.zeros(10, np.int64)
    l = np.zeros(10, np.int64)
    c = np.zeros(10, np.int64)
    scount = 0
    sptr = 0
    cursec = -1
    sh = sl = sclose = 0

    # Completed-M5 ATR(14).
    trs = np.zeros(14, np.int64)
    tcount = 0
    tptr = 0
    curm5 = -1
    mh = ml = mclose = 0
    prevclose = 0
    haveprev = False

    minute = -1
    cycle_buy = cycle_sell = 0
    pending = 0
    rearm = 0

    pos = 0
    entry = stop = 0
    entrysec = 0
    had_position = False
    last_side = 0
    pos_owned = False
    last_owned = False

    trades = 0
    raw_positive_wins = 0
    official_wins = 0
    losses = 0
    p01_hits = 0
    m30_only_hits = 0
    suppressed_rearms = 0

    gp = 0.0
    gl = 0.0
    balance = 100000.0
    balance_peak = balance
    equity_peak = balance
    max_balance_dd = 0.0
    max_equity_dd = 0.0
    hold_sum = 0.0

    for i in range(t.size):
        tm = np.int64(t[i])
        a = np.int64(ask[i])
        b = np.int64(bid[i])
        sec = tm // 1000

        # Broker protective stop first.
        if pos == 1 and b <= stop:
            raw = (b - entry) / price_scale
            exit_deal = raw - 0.01
            if raw - 0.01 > 1e-12:
                official_wins += 1
            if raw > 0:
                gp += exit_deal
                raw_positive_wins += 1
            else:
                gl += exit_deal
                losses += 1
            balance += exit_deal
            trades += 1
            hold_sum += sec - entrysec
            pos = 0
            entry = stop = 0
        elif pos == -1 and a >= stop:
            raw = (entry - a) / price_scale
            exit_deal = raw - 0.01
            if raw - 0.01 > 1e-12:
                official_wins += 1
            if raw > 0:
                gp += exit_deal
                raw_positive_wins += 1
            else:
                gl += exit_deal
                losses += 1
            balance += exit_deal
            trades += 1
            hold_sum += sec - entrysec
            pos = 0
            entry = stop = 0

        # Completed-second state update.
        if cursec < 0:
            cursec = sec
            sh = sl = sclose = b
        elif sec != cursec:
            h[sptr] = sh
            l[sptr] = sl
            c[sptr] = sclose
            sptr = (sptr + 1) % 10
            scount = min(10, scount + 1)
            cursec = sec
            sh = sl = sclose = b
        else:
            if b > sh:
                sh = b
            if b < sl:
                sl = b
            sclose = b

        disp = travel = rng = turns = 0
        if scount == 10:
            first = sptr
            disp = c[(sptr + 9) % 10] - c[first]
            maxh = h[first]
            minl = l[first]
            prev = c[first]
            prevsign = 0
            for k in range(1, 10):
                idx = (first + k) % 10
                if h[idx] > maxh:
                    maxh = h[idx]
                if l[idx] < minl:
                    minl = l[idx]
                d = c[idx] - prev
                travel += abs(d)
                sign = 1 if d > 0 else -1 if d < 0 else 0
                if sign != 0:
                    if prevsign != 0 and sign != prevsign:
                        turns += 1
                    prevsign = sign
                prev = c[idx]
            rng = maxh - minl
        eff = abs(disp) / travel if travel > 0 else 0.0

        # Completed-M5 ATR update.
        m5 = tm // 300000
        if curm5 < 0:
            curm5 = m5
            mh = ml = mclose = b
        elif m5 != curm5:
            tr = mh - ml
            if haveprev:
                tr = max(tr, abs(mh - prevclose), abs(ml - prevclose))
            trs[tptr] = tr
            tptr = (tptr + 1) % 14
            tcount = min(14, tcount + 1)
            prevclose = mclose
            haveprev = True
            curm5 = m5
            mh = ml = mclose = b
        else:
            if b > mh:
                mh = b
            if b < ml:
                ml = b
            mclose = b

        atrsum = 0
        if tcount == 14:
            for k in range(14):
                atrsum += trs[k]

        sess = _session_2026(tm)
        floor_price = 2.5 if sess == 0 else 2.0 if sess == 1 else 1.75
        floor_raw = int(round(floor_price * price_scale))
        gate = (
            tcount == 14
            and (a - b) <= 25 * tick
            and atrsum >= 14 * floor_raw
        )

        # New-minute reset and original R9 cycle brackets.
        mi = tm // 60000
        if mi != minute:
            minute = mi
            pending = 2
            rearm = 0
            cycle_buy = _q_half_raw2_to_tick(b + a + 2 * half, tick)
            cycle_sell = _q_half_raw2_to_tick(b + a - 2 * half, tick)

        # Existing-position management.
        if pos != 0:
            had_position = True
            last_side = pos
            last_owned = pos_owned
            if sec - entrysec >= 30:
                raw = ((b - entry) if pos == 1 else (entry - a)) / price_scale
                exit_deal = raw - 0.01
                if raw - 0.01 > 1e-12:
                    official_wins += 1
                if raw > 0:
                    gp += exit_deal
                    raw_positive_wins += 1
                else:
                    gl += exit_deal
                    losses += 1
                balance += exit_deal
                trades += 1
                hold_sum += sec - entrysec
                pos = 0
                entry = stop = 0
            else:
                fav = (b - entry) if pos == 1 else (entry - a)
                if fav >= trail_activation:
                    new_stop = _q_tick_raw(
                        b - trail_distance if pos == 1 else a + trail_distance,
                        tick,
                    )
                    improve = new_stop > stop if pos == 1 else new_stop < stop
                    if improve:
                        stop = new_stop

        # Position-observation latch -> rearm/ownership action.
        elif had_position:
            if last_owned or global_no_rearm:
                pending = 0
                if last_owned:
                    suppressed_rearms += 1
            elif rearm < 3:
                rearm += 1
                pending = -last_side
            else:
                pending = 0
            had_position = False
            last_side = 0
            last_owned = False

        # Fresh R9 opportunity + ownership action.
        elif tm >= trade_start_ms and gate:
            common = eff > 0.70 and rng >= min_range and turns <= 9
            intended = 0
            if pending in (1, 2) and a >= cycle_buy and common and disp >= min_disp:
                intended = 1
            elif pending in (-1, 2) and b <= cycle_sell and common and disp <= -min_disp:
                intended = -1

            if intended != 0:
                i250 = float(impulse250[i]) * intended
                h1 = float(h1_netatr[i]) * intended
                m30 = float(m30_netatr[i]) * intended

                p01 = (i250 <= -0.55) or (not np.isnan(h1) and h1 > 0.35)
                m30_only = (
                    mode == 2
                    and (not p01)
                    and (not np.isnan(m30))
                    and m30 > 0.35
                )

                actual = -intended if p01 else intended
                owned = p01 or m30_only
                if p01:
                    p01_hits += 1
                if m30_only:
                    m30_only_hits += 1

                if actual == 1:
                    pos = 1
                    entry = a
                    entrysec = sec
                    stop = _q_tick_raw(b - stopd, tick)
                else:
                    pos = -1
                    entry = b
                    entrysec = sec
                    stop = _q_tick_raw(a + stopd, tick)

                pos_owned = owned
                pending = 0
                balance -= 0.01
                gl -= 0.01

        balance_peak = max(balance_peak, balance)
        max_balance_dd = max(max_balance_dd, balance_peak - balance)
        equity = (
            balance + (b - entry) / price_scale
            if pos == 1
            else balance + (entry - a) / price_scale
            if pos == -1
            else balance
        )
        equity_peak = max(equity_peak, equity)
        max_equity_dd = max(max_equity_dd, equity_peak - equity)

    return (
        np.array(
            [
                trades,
                raw_positive_wins,
                official_wins,
                losses,
                p01_hits,
                m30_only_hits,
                suppressed_rearms,
            ],
            dtype=np.int64,
        ),
        np.array(
            [
                gp,
                gl,
                gp + gl,
                max_balance_dd,
                max_equity_dd,
                hold_sum / trades if trades else 0.0,
            ],
            dtype=np.float64,
        ),
    )


def parity_result_dict(ints: np.ndarray, floats: np.ndarray) -> dict:
    return {
        "trades": int(ints[0]),
        "raw_positive_wins": int(ints[1]),
        "official_wins": int(ints[2]),
        "losses": int(ints[3]),
        "p01_hits": int(ints[4]),
        "m30_only_hits": int(ints[5]),
        "owned_exit_suppressed_rearms": int(ints[6]),
        "gross_profit": float(floats[0]),
        "gross_loss": float(floats[1]),
        "net_profit": float(floats[2]),
        "max_balance_drawdown": float(floats[3]),
        "max_equity_drawdown": float(floats[4]),
        "average_hold_seconds": float(floats[5]),
    }


def build_parent_features(t_ms, ask_raw, bid_raw):
    return {
        "impulse250": bidask_impulse_250ms(t_ms, ask_raw, bid_raw),
        "h1_netatr": completed_bar_netatr(t_ms, ask_raw, bid_raw, 3_600_000, 3, 14),
        "m30_netatr": completed_bar_netatr(t_ms, ask_raw, bid_raw, 1_800_000, 3, 14),
    }
