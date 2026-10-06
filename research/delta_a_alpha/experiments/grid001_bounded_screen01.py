#!/usr/bin/env python3
"""GRID-001 bounded Stage-A screen 01.

Preregistered 12-variant screen:
- cap per direction: 1, 2, 4
- hard stop: 1.5, 2, 3, 4 grid gaps
- fixed 0.01 lot
- no Martingale
- $1 grid gap / $1 TP
- DELTA Stage-A / DUKAS_COINEXX_LIKE_P75

Imports the durable forensic loader/surface builder so source identity and quote
materialization remain identical to GRID-001-F.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from numba import njit

from grid001_forensic_baseline import (
    DAY_MS,
    ENTRY_COMMISSION,
    EXIT_COMMISSION,
    GAP_RAW,
    H1_MS,
    PRICE_SCALE,
    USD_PER_RAW,
    WINDOW_BARS,
    load_stage_a,
    materialize_p75,
    sha256,
)

CAPS = (1, 2, 4)
STOP_MULTS = (1.5, 2.0, 3.0, 4.0)


@njit(cache=True)
def _remove(entry, tp, sl, opened, half_spread, n, idx):
    for j in range(idx, n - 1):
        entry[j] = entry[j + 1]
        tp[j] = tp[j + 1]
        sl[j] = sl[j + 1]
        opened[j] = opened[j + 1]
        half_spread[j] = half_spread[j + 1]
    return n - 1


@njit(cache=True)
def simulate(t, ask, bid, cap, stop_mult, start_balance=100000.0):
    maxn = 4
    be = np.empty(maxn, np.int32)
    btp = np.empty(maxn, np.int32)
    bsl = np.empty(maxn, np.int32)
    bt = np.empty(maxn, np.int64)
    bhs = np.empty(maxn, np.float64)
    se = np.empty(maxn, np.int32)
    stp = np.empty(maxn, np.int32)
    ssl = np.empty(maxn, np.int32)
    st = np.empty(maxn, np.int64)
    shs = np.empty(maxn, np.float64)
    nb = 0
    ns = 0

    highs = np.empty(WINDOW_BARS - 1, np.int32)
    lows = np.empty(WINDOW_BARS - 1, np.int32)
    completed = 0
    pos = 0
    current_hour = np.int64(-1)
    current_high = np.int32(0)
    current_low = np.int32(0)
    cache_ready = False
    cached_high = np.int32(0)
    cached_low = np.int32(0)

    stop_raw = int(round(GAP_RAW * stop_mult))
    balance = start_balance
    peak_balance = start_balance
    peak_equity = start_balance
    min_equity = start_balance
    max_balance_dd = 0.0
    max_equity_dd = 0.0
    gross_profit = 0.0
    gross_loss = 0.0
    trades = wins = tp_closes = stop_closes = forced = 0
    max_inventory = 0
    sum_hold = max_hold = 0.0
    commission_total = spread_cost = 0.0
    buy_sum = sell_sum = 0.0
    active_days = 0
    last_active_day = np.int64(-1)

    for i in range(t.size):
        ti = np.int64(t[i])
        ai = np.int32(ask[i])
        bi = np.int32(bid[i])
        hour = ti // H1_MS

        if hour != current_hour:
            if current_hour != -1:
                highs[pos] = current_high
                lows[pos] = current_low
                pos = (pos + 1) % (WINDOW_BARS - 1)
                completed = min(completed + 1, WINDOW_BARS - 1)
            current_hour = hour
            current_high = bi
            current_low = bi
            if completed >= WINDOW_BARS - 1:
                hi = bi
                lo = bi
                for j in range(WINDOW_BARS - 1):
                    hi = max(hi, highs[j])
                    lo = min(lo, lows[j])
                cached_high = hi
                cached_low = lo
                cache_ready = True
            else:
                cache_ready = False
        else:
            current_high = max(current_high, bi)
            current_low = min(current_low, bi)

        j = 0
        while j < nb:
            reason = 0
            if bi >= btp[j]:
                reason = 1
            elif bi <= bsl[j]:
                reason = 2
            if reason:
                entry = be[j]
                hold = (ti - bt[j]) / 1000.0
                pnl = (bi - entry) * USD_PER_RAW + EXIT_COMMISSION
                net = pnl + ENTRY_COMMISSION
                balance += pnl
                commission_total += -EXIT_COMMISSION
                buy_sum -= entry
                trades += 1
                wins += int(net > 0)
                sum_hold += hold
                max_hold = max(max_hold, hold)
                if net > 0:
                    gross_profit += net
                elif net < 0:
                    gross_loss += net
                if reason == 1:
                    tp_closes += 1
                else:
                    stop_closes += 1
                spread_cost += bhs[j] + ((ai - bi) / 2.0) * USD_PER_RAW
                nb = _remove(be, btp, bsl, bt, bhs, nb, j)
            else:
                j += 1

        j = 0
        while j < ns:
            reason = 0
            if ai <= stp[j]:
                reason = 1
            elif ai >= ssl[j]:
                reason = 2
            if reason:
                entry = se[j]
                hold = (ti - st[j]) / 1000.0
                pnl = (entry - ai) * USD_PER_RAW + EXIT_COMMISSION
                net = pnl + ENTRY_COMMISSION
                balance += pnl
                commission_total += -EXIT_COMMISSION
                sell_sum -= entry
                trades += 1
                wins += int(net > 0)
                sum_hold += hold
                max_hold = max(max_hold, hold)
                if net > 0:
                    gross_profit += net
                elif net < 0:
                    gross_loss += net
                if reason == 1:
                    tp_closes += 1
                else:
                    stop_closes += 1
                spread_cost += shs[j] + ((ai - bi) / 2.0) * USD_PER_RAW
                ns = _remove(se, stp, ssl, st, shs, ns, j)
            else:
                j += 1

        if cache_ready:
            current = ai  # source-style universal Ask trigger retained
            buy_anchor = be[nb - 1] if nb > 0 else cached_high
            if nb < cap and current <= buy_anchor - GAP_RAW:
                be[nb] = ai
                btp[nb] = ai + GAP_RAW
                bsl[nb] = ai - stop_raw
                bt[nb] = ti
                bhs[nb] = ((ai - bi) / 2.0) * USD_PER_RAW
                nb += 1
                buy_sum += ai
                balance += ENTRY_COMMISSION
                commission_total += -ENTRY_COMMISSION
                day = ti // DAY_MS
                if day != last_active_day:
                    active_days += 1
                    last_active_day = day

            sell_anchor = se[ns - 1] if ns > 0 else cached_low
            if ns < cap and current >= sell_anchor + GAP_RAW:
                se[ns] = bi
                stp[ns] = bi - GAP_RAW
                ssl[ns] = bi + stop_raw
                st[ns] = ti
                shs[ns] = ((ai - bi) / 2.0) * USD_PER_RAW
                ns += 1
                sell_sum += bi
                balance += ENTRY_COMMISSION
                commission_total += -ENTRY_COMMISSION
                day = ti // DAY_MS
                if day != last_active_day:
                    active_days += 1
                    last_active_day = day

        inventory = nb + ns
        max_inventory = max(max_inventory, inventory)
        floating = (
            (nb * bi - buy_sum) * USD_PER_RAW
            + (sell_sum - ns * ai) * USD_PER_RAW
        )
        equity = balance + floating
        peak_balance = max(peak_balance, balance)
        max_balance_dd = max(max_balance_dd, peak_balance - balance)
        peak_equity = max(peak_equity, equity)
        max_equity_dd = max(max_equity_dd, peak_equity - equity)
        min_equity = min(min_equity, equity)

    ti = np.int64(t[-1])
    ai = np.int32(ask[-1])
    bi = np.int32(bid[-1])

    for j in range(nb):
        entry = be[j]
        hold = (ti - bt[j]) / 1000.0
        pnl = (bi - entry) * USD_PER_RAW + EXIT_COMMISSION
        net = pnl + ENTRY_COMMISSION
        balance += pnl
        trades += 1
        forced += 1
        wins += int(net > 0)
        commission_total += -EXIT_COMMISSION
        sum_hold += hold
        max_hold = max(max_hold, hold)
        if net > 0:
            gross_profit += net
        elif net < 0:
            gross_loss += net
        spread_cost += bhs[j] + ((ai - bi) / 2.0) * USD_PER_RAW

    for j in range(ns):
        entry = se[j]
        hold = (ti - st[j]) / 1000.0
        pnl = (entry - ai) * USD_PER_RAW + EXIT_COMMISSION
        net = pnl + ENTRY_COMMISSION
        balance += pnl
        trades += 1
        forced += 1
        wins += int(net > 0)
        commission_total += -EXIT_COMMISSION
        sum_hold += hold
        max_hold = max(max_hold, hold)
        if net > 0:
            gross_profit += net
        elif net < 0:
            gross_loss += net
        spread_cost += shs[j] + ((ai - bi) / 2.0) * USD_PER_RAW

    peak_balance = max(peak_balance, balance)
    max_balance_dd = max(max_balance_dd, peak_balance - balance)
    peak_equity = max(peak_equity, balance)
    max_equity_dd = max(max_equity_dd, peak_equity - balance)
    min_equity = min(min_equity, balance)

    return np.array([
        balance - start_balance,
        gross_profit,
        gross_loss,
        trades,
        wins,
        tp_closes,
        stop_closes,
        forced,
        max_balance_dd,
        max_equity_dd,
        min_equity - start_balance,
        max_inventory,
        commission_total,
        spread_cost,
        sum_hold / max(1, trades),
        max_hold,
        active_days,
    ], dtype=np.float64)


def pack(v, cap, stop_mult):
    (
        net, gp, gl, trades, wins, tp, stop, forced, bdd, edd, min_delta,
        max_inventory, commissions, spread_cost, avg_hold, max_hold, days
    ) = v.tolist()
    return {
        "cap_per_direction": int(cap),
        "stop_grid_gaps": float(stop_mult),
        "net_profit": net,
        "gross_profit": gp,
        "gross_loss": gl,
        "profit_factor": gp / abs(gl) if gl < 0 else None,
        "trades": int(trades),
        "wins": int(wins),
        "win_rate_pct": 100 * wins / max(1, trades),
        "expected_payoff": net / max(1, trades),
        "tp_closes": int(tp),
        "stop_closes": int(stop),
        "forced_closes": int(forced),
        "max_balance_drawdown": bdd,
        "max_equity_drawdown": edd,
        "min_equity_delta": min_delta,
        "max_open_inventory": int(max_inventory),
        "max_total_lots": max_inventory * 0.01,
        "commission_total_abs": commissions,
        "estimated_midpoint_spread_cost": spread_cost,
        "average_hold_seconds": avg_hold,
        "max_hold_seconds": max_hold,
        "active_trading_days": int(days),
        "trades_per_active_day": trades / max(1, days),
        "small_account": {
            "100": {"min_equity": 100 + min_delta, "positive_equity": 100 + min_delta > 0},
            "200": {"min_equity": 200 + min_delta, "positive_equity": 200 + min_delta > 0},
            "300": {"min_equity": 300 + min_delta, "positive_equity": 300 + min_delta > 0},
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    source_hash = sha256(args.source)
    t, src_ask, src_bid = load_stage_a(args.source)
    ask, bid, max_error2 = materialize_p75(t, src_ask, src_bid)

    simulate(t[:1000], ask[:1000], bid[:1000], 1, 1.5)

    rows = []
    for cap in CAPS:
        for stop_mult in STOP_MULTS:
            rows.append(pack(simulate(t, ask, bid, cap, stop_mult), cap, stop_mult))

    result = {
        "schema": "delta-a-alpha-grid001-bounded-stage-a-screen01-v1",
        "unit": "DAA_GRID_001_BOUNDED_STAGE_A_SCREEN_01",
        "source_sha256": source_hash,
        "ticks": int(len(t)),
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "lot": 0.01,
        "martingale": False,
        "grid_gap_price": 1.0,
        "tp_price": 1.0,
        "caps": list(CAPS),
        "stop_grid_gaps": list(STOP_MULTS),
        "max_midpoint_quantization_error_price": max_error2 / (2 * PRICE_SCALE),
        "variants": rows,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
