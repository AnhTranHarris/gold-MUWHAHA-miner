#!/usr/bin/env python3
"""GRID-001 forensic Stage-A replay.

Reconstructs the supplied source tutorial's physical grid mechanics on DELTA's
ordered DUKAS_COINEXX_LIKE_P75 surface. This is a forensic lane only: fixed
0.01 lot, no Martingale, source-style no-stop inventory, and forced boundary
liquidation. It is not a production strategy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

PRICE_SCALE = 1000
POINT_RAW = 10  # $0.01 for Coinexx-style XAUUSD
DAY_MS = 86_400_000
US_DST_START_2026_MS = np.int64(1772953200000)
UK_DST_START_2026_MS = np.int64(1774746000000)
P75_POINTS = np.array([20, 20, 21, 21], dtype=np.int64)
STAGE_A_START = np.int64(1767225600000)
STAGE_A_END = np.int64(1768737600000)
H1_MS = np.int64(3_600_000)
WINDOW_BARS = 48
GAP_POINTS = 100
GAP_RAW = GAP_POINTS * POINT_RAW
ENTRY_COMMISSION = -0.01
EXIT_COMMISSION = -0.01
USD_PER_RAW = 1.0 / PRICE_SCALE
MAX_SIDE_POS = 20_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_stage_a(path: Path, chunksize: int = 1_000_000):
    times, asks, bids = [], [], []
    use = ["timestamp_ms_utc", "ask_raw", "bid_raw"]
    dtypes = {"timestamp_ms_utc": "i8", "ask_raw": "i4", "bid_raw": "i4"}
    for df in pd.read_csv(
        path, compression="gzip", usecols=use, dtype=dtypes, chunksize=chunksize
    ):
        t = df["timestamp_ms_utc"].to_numpy(copy=False)
        if t[-1] < STAGE_A_START:
            continue
        mask = (t >= STAGE_A_START) & (t < STAGE_A_END)
        if mask.any():
            times.append(t[mask].copy())
            asks.append(df["ask_raw"].to_numpy(copy=False)[mask].copy())
            bids.append(df["bid_raw"].to_numpy(copy=False)[mask].copy())
        if t[-1] >= STAGE_A_END:
            break
    if not times:
        raise RuntimeError("No Stage-A ticks found")
    return np.concatenate(times), np.concatenate(asks), np.concatenate(bids)


@njit(cache=True)
def session_code_2026(t):
    tod = t % DAY_MS
    london_start = 7 * 3_600_000 if t >= UK_DST_START_2026_MS else 8 * 3_600_000
    london_end = london_start + 8 * 3_600_000 + 30 * 60_000
    ny_start = 12 * 3_600_000 if t >= US_DST_START_2026_MS else 13 * 3_600_000
    ny_end = ny_start + 9 * 3_600_000
    in_london = london_start <= tod < london_end
    in_ny = ny_start <= tod < ny_end
    if in_london and in_ny:
        return 2
    if in_london:
        return 1
    if in_ny:
        return 3
    return 0


@njit(cache=True)
def q_half_raw2_to_tick(target2, tick):
    return ((target2 + tick) // (2 * tick)) * tick


@njit(cache=True)
def materialize_p75(t, src_ask, src_bid):
    n = t.size
    ask = np.empty(n, np.int32)
    bid = np.empty(n, np.int32)
    max_error2 = 0
    for i in range(n):
        spread = P75_POINTS[session_code_2026(np.int64(t[i]))] * POINT_RAW
        mid2 = np.int64(src_ask[i]) + np.int64(src_bid[i])
        b = q_half_raw2_to_tick(mid2 - spread, POINT_RAW)
        a = b + spread
        bid[i] = b
        ask[i] = a
        error2 = abs((2 * b + spread) - mid2)
        if error2 > max_error2:
            max_error2 = error2
    return ask, bid, max_error2


@njit(cache=True)
def simulate(t, ask, bid, start_balance=100_000.0, max_side_pos=MAX_SIDE_POS):
    buy_entry = np.empty(max_side_pos, np.int32)
    buy_tp = np.empty(max_side_pos, np.int32)
    buy_time = np.empty(max_side_pos, np.int64)
    buy_half_spread = np.empty(max_side_pos, np.float64)

    sell_entry = np.empty(max_side_pos, np.int32)
    sell_tp = np.empty(max_side_pos, np.int32)
    sell_time = np.empty(max_side_pos, np.int64)
    sell_half_spread = np.empty(max_side_pos, np.float64)

    nb = ns = 0

    completed_hi = np.empty(WINDOW_BARS - 1, np.int32)
    completed_lo = np.empty(WINDOW_BARS - 1, np.int32)
    completed_count = completed_pos = 0
    current_hour = np.int64(-1)
    current_hi = current_lo = np.int32(0)
    cache_ready = False
    cached_high = cached_low = np.int32(0)

    balance = start_balance
    peak_balance = start_balance
    peak_equity = start_balance
    min_equity = start_balance
    max_balance_dd = max_equity_dd = 0.0

    gross_profit = gross_loss = 0.0
    trade_count = wins = tp_closes = forced_closes = 0
    sum_hold = max_hold = 0.0
    max_inventory = 0
    commission_total = spread_cost = 0.0
    buy_entry_sum = sell_entry_sum = 0.0

    active_days = np.empty(64, np.int64)
    active_day_count = 0
    last_active_day = np.int64(-1)

    in_episode = False
    episode_start = np.int64(0)
    episode_min_float = episode_max_float = 0.0
    episodes = 0
    sum_episode_seconds = max_episode_seconds = 0.0
    worst_episode_mae = 0.0
    best_episode_mfe = -1e18

    for i in range(t.size):
        ti = np.int64(t[i])
        ai = np.int32(ask[i])
        bi = np.int32(bid[i])
        hour = ti // H1_MS

        if hour != current_hour:
            if current_hour != -1:
                completed_hi[completed_pos] = current_hi
                completed_lo[completed_pos] = current_lo
                completed_pos = (completed_pos + 1) % (WINDOW_BARS - 1)
                completed_count = min(completed_count + 1, WINDOW_BARS - 1)

            current_hour = hour
            current_hi = current_lo = bi

            if completed_count >= WINDOW_BARS - 1:
                hi = lo = bi
                for j in range(WINDOW_BARS - 1):
                    hi = max(hi, completed_hi[j])
                    lo = min(lo, completed_lo[j])
                cached_high = hi
                cached_low = lo
                cache_ready = True
            else:
                cache_ready = False
        else:
            current_hi = max(current_hi, bi)
            current_lo = min(current_lo, bi)

        while nb > 0 and bi >= buy_tp[nb - 1]:
            entry = buy_entry[nb - 1]
            hold = (ti - buy_time[nb - 1]) / 1000.0
            pnl_at_exit = (bi - entry) * USD_PER_RAW + EXIT_COMMISSION
            trade_net = pnl_at_exit + ENTRY_COMMISSION
            balance += pnl_at_exit
            commission_total += -EXIT_COMMISSION
            buy_entry_sum -= entry
            sum_hold += hold
            max_hold = max(max_hold, hold)
            trade_count += 1
            tp_closes += 1
            wins += int(trade_net > 0)
            if trade_net > 0:
                gross_profit += trade_net
            elif trade_net < 0:
                gross_loss += trade_net
            spread_cost += buy_half_spread[nb - 1] + ((ai - bi) / 2.0) * USD_PER_RAW
            nb -= 1

        while ns > 0 and ai <= sell_tp[ns - 1]:
            entry = sell_entry[ns - 1]
            hold = (ti - sell_time[ns - 1]) / 1000.0
            pnl_at_exit = (entry - ai) * USD_PER_RAW + EXIT_COMMISSION
            trade_net = pnl_at_exit + ENTRY_COMMISSION
            balance += pnl_at_exit
            commission_total += -EXIT_COMMISSION
            sell_entry_sum -= entry
            sum_hold += hold
            max_hold = max(max_hold, hold)
            trade_count += 1
            tp_closes += 1
            wins += int(trade_net > 0)
            if trade_net > 0:
                gross_profit += trade_net
            elif trade_net < 0:
                gross_loss += trade_net
            spread_cost += sell_half_spread[ns - 1] + ((ai - bi) / 2.0) * USD_PER_RAW
            ns -= 1

        if cache_ready:
            current = ai  # tutorial uses Ask universally for both signal checks

            buy_anchor = buy_entry[nb - 1] if nb > 0 else cached_high
            if current <= buy_anchor - GAP_RAW:
                if nb >= max_side_pos:
                    return np.array([-999999.0])
                buy_entry[nb] = ai
                buy_tp[nb] = ai + GAP_RAW
                buy_time[nb] = ti
                buy_half_spread[nb] = ((ai - bi) / 2.0) * USD_PER_RAW
                nb += 1
                buy_entry_sum += ai
                balance += ENTRY_COMMISSION
                commission_total += -ENTRY_COMMISSION
                day = ti // DAY_MS
                if day != last_active_day:
                    active_days[active_day_count] = day
                    active_day_count += 1
                    last_active_day = day

            sell_anchor = sell_entry[ns - 1] if ns > 0 else cached_low
            if current >= sell_anchor + GAP_RAW:
                if ns >= max_side_pos:
                    return np.array([-999999.0])
                sell_entry[ns] = bi
                sell_tp[ns] = bi - GAP_RAW
                sell_time[ns] = ti
                sell_half_spread[ns] = ((ai - bi) / 2.0) * USD_PER_RAW
                ns += 1
                sell_entry_sum += bi
                balance += ENTRY_COMMISSION
                commission_total += -ENTRY_COMMISSION
                day = ti // DAY_MS
                if day != last_active_day:
                    active_days[active_day_count] = day
                    active_day_count += 1
                    last_active_day = day

        inventory = nb + ns
        max_inventory = max(max_inventory, inventory)
        floating = (
            (nb * bi - buy_entry_sum) * USD_PER_RAW
            + (sell_entry_sum - ns * ai) * USD_PER_RAW
        )
        equity = balance + floating

        peak_balance = max(peak_balance, balance)
        max_balance_dd = max(max_balance_dd, peak_balance - balance)
        peak_equity = max(peak_equity, equity)
        max_equity_dd = max(max_equity_dd, peak_equity - equity)
        min_equity = min(min_equity, equity)

        if inventory > 0:
            if not in_episode:
                in_episode = True
                episode_start = ti
                episode_min_float = episode_max_float = floating
            else:
                episode_min_float = min(episode_min_float, floating)
                episode_max_float = max(episode_max_float, floating)
        elif in_episode:
            duration = (ti - episode_start) / 1000.0
            episodes += 1
            sum_episode_seconds += duration
            max_episode_seconds = max(max_episode_seconds, duration)
            worst_episode_mae = min(worst_episode_mae, episode_min_float)
            best_episode_mfe = max(best_episode_mfe, episode_max_float)
            in_episode = False

    ti = np.int64(t[-1])
    ai = np.int32(ask[-1])
    bi = np.int32(bid[-1])

    while nb > 0:
        entry = buy_entry[nb - 1]
        hold = (ti - buy_time[nb - 1]) / 1000.0
        pnl_at_exit = (bi - entry) * USD_PER_RAW + EXIT_COMMISSION
        trade_net = pnl_at_exit + ENTRY_COMMISSION
        balance += pnl_at_exit
        commission_total += -EXIT_COMMISSION
        buy_entry_sum -= entry
        sum_hold += hold
        max_hold = max(max_hold, hold)
        trade_count += 1
        forced_closes += 1
        wins += int(trade_net > 0)
        if trade_net > 0:
            gross_profit += trade_net
        elif trade_net < 0:
            gross_loss += trade_net
        spread_cost += buy_half_spread[nb - 1] + ((ai - bi) / 2.0) * USD_PER_RAW
        nb -= 1

    while ns > 0:
        entry = sell_entry[ns - 1]
        hold = (ti - sell_time[ns - 1]) / 1000.0
        pnl_at_exit = (entry - ai) * USD_PER_RAW + EXIT_COMMISSION
        trade_net = pnl_at_exit + ENTRY_COMMISSION
        balance += pnl_at_exit
        commission_total += -EXIT_COMMISSION
        sell_entry_sum -= entry
        sum_hold += hold
        max_hold = max(max_hold, hold)
        trade_count += 1
        forced_closes += 1
        wins += int(trade_net > 0)
        if trade_net > 0:
            gross_profit += trade_net
        elif trade_net < 0:
            gross_loss += trade_net
        spread_cost += sell_half_spread[ns - 1] + ((ai - bi) / 2.0) * USD_PER_RAW
        ns -= 1

    if in_episode:
        duration = (ti - episode_start) / 1000.0
        episodes += 1
        sum_episode_seconds += duration
        max_episode_seconds = max(max_episode_seconds, duration)
        worst_episode_mae = min(worst_episode_mae, episode_min_float)
        best_episode_mfe = max(best_episode_mfe, episode_max_float)

    peak_balance = max(peak_balance, balance)
    max_balance_dd = max(max_balance_dd, peak_balance - balance)
    peak_equity = max(peak_equity, balance)
    max_equity_dd = max(max_equity_dd, peak_equity - balance)
    min_equity = min(min_equity, balance)

    return np.array(
        [
            balance - start_balance,
            gross_profit,
            gross_loss,
            trade_count,
            wins,
            tp_closes,
            forced_closes,
            max_balance_dd,
            max_equity_dd,
            min_equity - start_balance,
            max_inventory,
            commission_total,
            spread_cost,
            sum_hold / max(1, trade_count),
            max_hold,
            active_day_count,
            episodes,
            sum_episode_seconds / max(1, episodes),
            max_episode_seconds,
            worst_episode_mae,
            best_episode_mfe,
        ],
        dtype=np.float64,
    )


def result_dict(v, ticks: int, max_midpoint_error: float):
    if len(v) == 1 and v[0] < -1e5:
        return {"status": "FAIL_RESOURCE_CAP"}

    (
        net,
        gp,
        gl,
        trades,
        wins,
        tp,
        forced,
        balance_dd,
        equity_dd,
        min_delta,
        max_inventory,
        commissions,
        spread_cost,
        avg_hold,
        max_hold,
        active_days,
        episodes,
        avg_episode,
        max_episode,
        worst_mae,
        best_mfe,
    ) = v.tolist()

    return {
        "status": "COMPLETE",
        "schema": "delta-a-alpha-grid001-forensic-stage-a-v1",
        "unit": "DAA_GRID_001_CAUSAL_FORENSIC_BASELINE",
        "lane": "GRID-001-F",
        "window": "2026-01-01T00:00:00Z..2026-01-18T12:00:00Z exclusive",
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "ticks": int(ticks),
        "lot": 0.01,
        "martingale": False,
        "gap_points": GAP_POINTS,
        "gap_price": GAP_RAW / PRICE_SCALE,
        "h1_window_bars": WINDOW_BARS,
        "source_signal_semantics": (
            "H1 bid bars; cache at first tick of hour; current Ask used for both "
            "triggers; chained latest same-side entry anchors"
        ),
        "execution": (
            "BUY Ask/Bid; SELL Bid/Ask; $0.01 entry + $0.01 exit commission; "
            "zero slippage; forced window-end liquidation"
        ),
        "net_profit": net,
        "gross_profit": gp,
        "gross_loss": gl,
        "profit_factor": gp / abs(gl) if gl < 0 else None,
        "trades": int(trades),
        "wins_net_after_commission": int(wins),
        "closed_win_rate_pct": 100 * wins / max(1, trades),
        "tp_closes": int(tp),
        "forced_liquidation_closes": int(forced),
        "forced_liquidation_share_pct": 100 * forced / max(1, trades),
        "expected_payoff": net / max(1, trades),
        "active_trading_days": int(active_days),
        "trades_per_active_day": trades / max(1, active_days),
        "max_balance_drawdown": balance_dd,
        "max_equity_drawdown": equity_dd,
        "min_equity_delta_from_start": min_delta,
        "max_open_inventory": int(max_inventory),
        "max_total_lots": max_inventory * 0.01,
        "commission_total_abs": commissions,
        "estimated_midpoint_spread_cost": spread_cost,
        "average_hold_seconds": avg_hold,
        "max_hold_seconds": max_hold,
        "inventory_episodes": int(episodes),
        "average_inventory_episode_seconds": avg_episode,
        "max_inventory_episode_seconds": max_episode,
        "worst_inventory_episode_floating_mae": worst_mae,
        "best_inventory_episode_floating_mfe": best_mfe,
        "small_account_survivability_unconstrained": {
            "100": {
                "min_equity": 100 + min_delta,
                "survives_positive_equity": 100 + min_delta > 0,
            },
            "200": {
                "min_equity": 200 + min_delta,
                "survives_positive_equity": 200 + min_delta > 0,
            },
            "300": {
                "min_equity": 300 + min_delta,
                "survives_positive_equity": 300 + min_delta > 0,
            },
        },
        "max_midpoint_quantization_error_price": max_midpoint_error,
        "promotion_eligible": False,
        "notes": [
            "forensic source lane only",
            "no margin constraint in this lane",
            "small-account figures are equity-path diagnostics, not broker margin certification",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    started = time.time()
    source_hash = sha256(args.source)

    t0 = time.time()
    t, source_ask, source_bid = load_stage_a(args.source)
    load_seconds = time.time() - t0

    t0 = time.time()
    ask, bid, max_error2 = materialize_p75(t, source_ask, source_bid)
    materialize_seconds = time.time() - t0

    simulate(t[:1000], ask[:1000], bid[:1000], 100_000.0, MAX_SIDE_POS)

    t0 = time.time()
    values = simulate(t, ask, bid, 100_000.0, MAX_SIDE_POS)
    simulate_seconds = time.time() - t0

    result = result_dict(values, len(t), max_error2 / (2 * PRICE_SCALE))
    result["source_file"] = args.source.name
    result["source_sha256"] = source_hash
    result["timing_seconds"] = {
        "load": load_seconds,
        "materialize_p75": materialize_seconds,
        "simulate": simulate_seconds,
        "total": time.time() - started,
    }

    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
