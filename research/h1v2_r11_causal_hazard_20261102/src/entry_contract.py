"""R11 additive H1V2 entry-contract reconciliation; NEVER rewrites original teacher.

Scientific inputs: immutable raw Dukascopy ordered quote stream, immutable
original 250ms teacher labels, frozen R9 v2 v5 gap/warmup contract.
Produces a new *eligible subset* and reoptimizes the same future-only H1V2
oracle solely for hindsight-capacity comparison, not for forecasting.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from numba import njit

MONTHS = ('01', '02', '06', '07')
PINNED = {
    '01': 'd2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
    '02': 'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
    '06': '34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
    '07': 'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7',
}
SYNTH = {'01': 27980, '02': 33523, '06': 31801, '07': 24382}

@njit(cache=True)
def candidate_quotes(t, bid, ask, gap_reset_ms=15000,
                     warmup_ms=300000, max_spread=1.50, reset_on_equal=False):
    """First observed quote per occupied 250ms bin; complete past only.

    Compare > 15s for repaired v5, >=300s for original H1V2. Substitutes
    strictly for *candidate admission*, not for original outcome labels.
    """
    n = len(t)
    out = np.empty(n, dtype=np.int64)
    if not n:
        return out[:0]
    if gap_reset_ms <= 0 or warmup_ms < 0 or max_spread < 0:
        raise ValueError('invalid admission contract')
    epoch = t[0]
    k = 0
    for i in range(n):
        if i:
            gap = t[i] - t[i - 1]
            if gap < 0:
                raise ValueError('nonchronological raw quotes')
            if gap > gap_reset_ms or (reset_on_equal and gap == gap_reset_ms):
                epoch = t[i]
        if i and t[i] // 250 == t[i-1] // 250:
            continue
        if t[i] - epoch < warmup_ms:
            continue
        spread = ask[i] - bid[i]
        if not np.isfinite(spread) or spread < 0. or spread > max_spread:
            continue
        out[k] = i
        k += 1
    return out[:k]


def candidate_legacy(t, bid, ask):
    return candidate_quotes(t, bid, ask, gap_reset_ms=300000,
                            reset_on_equal=True, warmup_ms=300000,
                            max_spread=1.50)


def candidate_v5(t, bid, ask, max_spread=1.50):
    return candidate_quotes(t, bid, ask, gap_reset_ms=15000,
                            reset_on_equal=False, warmup_ms=300000,
                            max_spread=max_spread)


def reconcile(t, bid, ask, original_ix, code, net, exit_ix,
              *, max_spread=1.50, oracle_scheduler=None):
    """Source-exact candidate intersection with fail-closed parity invariants.

    This does not infer missing counterfactual labels for a v5-only position:
    unexpected v5-only candidates raise instead of fabricating outcomes.
    """
    t = np.asarray(t, dtype=np.int64)
    bid = np.asarray(bid, dtype=np.float64)
    ask = np.asarray(ask, dtype=np.float64)
    original_ix = np.asarray(original_ix, dtype=np.int64)
    if not (len(t) == len(bid) == len(ask)):
        raise ValueError('quote length mismatch')
    if np.any(t[1:] < t[:-1]) or np.any(ask < bid) or not (np.isfinite(bid).all() and np.isfinite(ask).all()):
        raise ValueError('invalid source quotes')
    if np.any(np.diff(original_ix) <= 0) or (len(original_ix) and (original_ix[0]<0 or original_ix[-1]>=len(t))):
        raise ValueError('bad original teacher ordinals')
    if code.shape != (len(original_ix), 2) or net.shape != code.shape or exit_ix.shape != code.shape:
        raise ValueError('bad original teacher labels')
    recreated = candidate_legacy(t, bid, ask)
    if not np.array_equal(original_ix, recreated):
        raise ValueError('original H1V2 candidate universe not source exact; FAIL CLOSED')
    proposed = candidate_v5(t, bid, ask, max_spread=max_spread)
    in_teacher = np.isin(proposed, original_ix, assume_unique=True)
    if not in_teacher.all():
        raise ValueError('v5 has unknown teacher candidate ordinals; need new source exact labels')
    present = np.isin(original_ix, proposed, assume_unique=True)
    included_rows = np.flatnonzero(present)
    known_good = (code == 1).any(axis=1)
    result = {
        'original_candidates': int(len(original_ix)),
        'v5_candidates': int(len(proposed)),
        'excluded_original_candidates': int((~present).sum()),
        'original_any_good_candidates': int(known_good.sum()),
        'v5_any_good_candidates': int(known_good[present].sum()),
        'excluded_any_good_candidates': int(known_good[~present].sum()),
        'eligibility_intersection_exact': True,
        'source_original_candidate_contract': 'first observed 250ms, gap>=300000ms, warmup300000ms, spread<=1.50',
        'research_v5_candidate_contract': f'first observed 250ms, gap>15000ms, warmup300000ms, spread<={max_spread}',
        'scientific_status': 'POST_GAP_ELIGIBILITY_DIAGNOSTIC_HINDSIGHT_ONLY',
    }
    if oracle_scheduler is not None:
        kept, sides, sched = oracle_scheduler(original_ix[included_rows], code[present], net[present], exit_ix[present])
        result['v5_filtered_oracle_trades'] = int(sched['trades'])
        result['v5_filtered_oracle_modeled_net'] = float(sched['sum_net'])
        result['v5_filtered_oracle_original_rows'] = included_rows[kept].tolist() if len(kept) < 1000 else 'stored outside JSON; too many indices'
        result['v5_filtered_oracle_sides_count'] = {'BUY': int((sides==1).sum()), 'SELL': int((sides==-1).sum())}
    return result


def verify_file_sha(path, expected):
    with Path(path).open('rb') as f:
        actual = hashlib.file_digest(f, 'sha256').hexdigest()
    if actual != expected:
        raise ValueError(f'raw SHA256 mismatch: {path}: {actual} != {expected}')
    return actual


def run_original_month(month, raw_dir, teacher_dir, out_dir):
    """Reconstruct a full-month eligibility receipt, WITHOUT refitting policy."""
    from h1v2_teacher import read_ticks, schedule_oracle
    if month not in MONTHS:
        raise ValueError(month)
    raw = Path(raw_dir) / f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
    lab = Path(teacher_dir) / f'h1v2_dukascopy_{month}_oracle_labels.npz'
    verify_file_sha(raw, PINNED[month])
    receipt = json.loads((lab.parent / f'h1v2_dukascopy_{month}_receipt.json').read_text())
    verify_file_sha(lab, receipt['teacher_labels_sha256'])
    t, b, a = read_ticks(raw)
    with np.load(lab, allow_pickle=False) as z:
        ix = z['tick_index'].copy()
        if not np.array_equal(t[ix], z['t']):
            raise ValueError('original timestamp/ordinal mismatch')
        report = reconcile(t, b, a, ix, z['code'], z['net'], z['exit_tick_index'], oracle_scheduler=schedule_oracle)
    report.update(month=month, raw_sha256=PINNED[month], label_sha256=receipt['teacher_labels_sha256'],
                  original_oracle_count=receipt['oracle_nonoverlapping']['trades'],
                  original_oracle_modeled_net=receipt['oracle_nonoverlapping']['sum_net'],
                  r9_synth_month_count=SYNTH[month],
                  original_research_80pct_floor=math.ceil(.8*SYNTH[month]),
                  current_v2_85pct_floor=math.ceil(.85*SYNTH[month]))
    target = Path(out_dir)
    target.mkdir(parents=True,exist_ok=True)
    (target / f'R11_ENTRY_CONTRACT_{month}.json').write_text(json.dumps(report,indent=2))
    return report

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--month',choices=MONTHS,required=True)
    p.add_argument('--raw-dir',required=True)
    p.add_argument('--teacher-dir',required=True)
    p.add_argument('--output-dir',required=True)
    x=p.parse_args()
    print(json.dumps(run_original_month(x.month,x.raw_dir,x.teacher_dir,x.output_dir),indent=2))
