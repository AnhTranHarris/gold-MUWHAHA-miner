"""DELTA candidate template.

Keep strategy state inside run_month(). The raw arrays are immutable memmaps and are the
execution truth. Use completed-bar caches only when bar_end_ms <= current tick time.
"""
from __future__ import annotations
import numpy as np
from numba import njit

@njit(cache=True)
def _run(t_ms: np.ndarray, ask: np.ndarray, bid: np.ndarray):
    # Replace this no-op with candidate logic. Never use future rows.
    opportunities = 0
    trades = 0
    wins = 0
    gross_profit = 0.0
    gross_loss = 0.0
    max_balance_dd = 0.0
    max_equity_dd = 0.0
    return opportunities,trades,wins,gross_profit,gross_loss,max_balance_dd,max_equity_dd

def run_month(t_ms, ask_raw, bid_raw, config):
    v=_run(t_ms,ask_raw,bid_raw)
    return {
        "opportunities": int(v[0]), "trades": int(v[1]), "wins": int(v[2]),
        "gross_profit": float(v[3]), "gross_loss": float(v[4]),
        "net_profit": float(v[3]+v[4]), "max_balance_dd": float(v[5]),
        "max_equity_dd": float(v[6]), "avg_hold_ms": 0.0,
    }
