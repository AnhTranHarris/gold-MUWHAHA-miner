"""Reproduce the selected JAN039 *in-sample* research ledger from pinned artifacts.

This is intentionally NOT an economic-complete V1 or an MT5 execution implementation:
the legacy proposal tape includes precomputed source outcomes. No future data is
used by admission gates but proposal regeneration is not endogenous.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
from numba import njit


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for buf in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(buf)
    return h.hexdigest()


@njit(cache=True)
def first_profitable_exit(ask, bid, entries, original_exits, entry_prices, sides, selected, take_usd):
    """Find first quote-side realized favorable P&L >= threshold; never extend original exit."""
    new_exits = np.empty(len(selected), np.int64)
    new_pnl = np.empty(len(selected), np.float64)
    for j in range(len(selected)):
        i = selected[j]
        st, end, ep, di = entries[i], original_exits[i], entry_prices[i], sides[i]
        chosen = end
        for tick in range(st + 1, end + 1):
            pnl = ((bid[tick] if di > 0 else ask[tick]) - ep) * di / 1000.0 - 0.02
            if pnl >= take_usd:
                chosen = tick
                break
        new_exits[j] = chosen
        new_pnl[j] = ((bid[chosen] if di > 0 else ask[chosen]) - ep) * di / 1000.0 - 0.02
    return new_exits, new_pnl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ticks', type=Path, required=True, help='Original Jan 2026 Dukascopy CSV.GZ')
    parser.add_argument('--jan037-dir', type=Path, required=True, help='JAN037 unpacked source assets')
    parser.add_argument('--jan038-selected', type=Path, required=True, help='JAN038_SELECTED_EXACT.json')
    parser.add_argument('--legacy-equity-dir', type=Path, required=True, help='032/source with exact tick equity helper')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--save-ledger', action='store_true')
    args = parser.parse_args()
    expect = 'd2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
    actual = sha256_file(args.ticks)
    if actual != expect:
        raise SystemExit(f'UNVERIFIED_TICK_SOURCE: got {actual}, expected {expect}')
    os.environ['DAA_JAN039_RESEARCH_DIR'] = str(args.jan037_dir.resolve())
    os.environ['DAA_JAN039_TICKS'] = str(args.ticks.resolve())
    os.environ['DAA_JAN039_EQUITY_HELPERS'] = str(args.legacy_equity_dir.resolve())
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import jan039_legacy_engine as model

    with np.load(args.jan037_dir / 'JAN037_EXPANDED_L3_50MS_PROPOSALS.npz') as z:
        for k in z.files:
            setattr(model, k, z[k].copy())
    model.total = len(model.E)
    original_exits = model.X.copy()
    original_pnl = model.P.copy()
    raw_spread = (model.a[model.E].astype(np.int64) - model.b[model.E]) / 1000.
    idx20 = np.searchsorted(model.t, model.t[model.E] - 20000, side='left')
    model.imp20 = ((model.a[model.E].astype(np.int64) + model.b[model.E]) -
                   (model.a[idx20].astype(np.int64) + model.b[idx20])) / 2000.
    phase = (model.t[model.E] // 600000) % 6
    rules = json.loads(args.jan038_selected.read_text())['signal_gating_source_phase_pairs']
    excluded = np.zeros(model.total, dtype=bool)
    for source, phase_num in rules:
        excluded |= (model.S == source) & (phase == phase_num)
    model.spread = np.where(excluded, np.inf, raw_spread)

    params = json.loads((args.jan037_dir / 'JAN037_WD_EXACT_8.json').read_text())['params']
    params.update(per_second=3, wdcap=8, cap_cell=4, phase5cap=128,
                  phase2cap=512, phase3cap=512, phase4cap=512,
                  phase0cap=224, source26cap=432)
    selected_s27 = np.where((model.S == 27) & ~excluded & (model.spread <= 3.0) & (model.D < 0))[0]
    selected_s26 = np.where((model.S == 26) & (model.spread <= 3.0) & (model.D < 0))[0]
    out_x, out_p = original_exits.copy(), original_pnl.copy()
    for phase_subset, take in [((2, 3), 50.0), ((0,), 60.0), ((4,), 35.0)]:
        ix = selected_s27[np.isin(phase[selected_s27], phase_subset)]
        if len(ix):
            x, p = first_profitable_exit(model.a, model.b, model.E, original_exits,
                                         model.R, model.D, ix, take)
            out_x[ix], out_p[ix] = x, p
    if len(selected_s26):
        x, p = first_profitable_exit(model.a, model.b, model.E, original_exits,
                                     model.R, model.D, selected_s26, 35.0)
        out_x[selected_s26], out_p[selected_s26] = x, p
    model.X, model.P = out_x, out_p
    result, ledger = model.run(**params)
    result = model.daily_and_exact(ledger, result)
    recorded = {'net': 201226.483, 'trades': 12520, 'gl': -5562.307, 'equity_dd': 12640.925}
    comparisons = {k: abs(float(result[k]) - value) < (0.03 if k != 'trades' else 0.1)
                   for k, value in recorded.items()}
    result['source_sha256'] = actual
    result['expected'] = recorded
    result['parity_check'] = comparisons
    result['parity_pass'] = all(comparisons.values())
    result['classification'] = 'IN_SAMPLE_SOURCE_PROPOSAL_ONLY_UNFUNDED_UPSTREAM_GENEALOGY'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True))
    if args.save_ledger:
        np.savez_compressed(args.out.with_suffix('.npz'), **ledger)
    print(json.dumps({'parity_pass': result['parity_pass'], 'net': result['net'],
                      'trades': result['trades'], 'gl': result['gl'],
                      'equity_dd': result['equity_dd']}))
    if not result['parity_pass']:
        raise SystemExit('JAN039_REFERENCE_PARITY_FAILED')


if __name__ == '__main__':
    main()