import json,math,hashlib,zipfile,datetime
from pathlib import Path
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101');R=ROOT/'results';M=('01','02','06','07');S=('coinexx','dukascopy')
ref={'01':27980,'02':33523,'06':31801,'07':24382}
full=json.loads((R/'full_ledger_truth.json').read_text());lines=[]
lines += ['# R9 v2 full-source-month hindsight-teacher / causal-student training','',
'**Status: RESEARCH FAILURE. Zero of eight sources meets the combined 80% daily/weekly/monthly survival + 85% R9 SYNTH monthly volume + positive-net contract. No policy promoted.**','',
'## Complete scope and source provenance','',
'All January, February, June and July 2026 real tick archives from Coinexx and Dukascopy were read without truncation or sampled windows. Exact native timestamp and executable-side price matches were obtained for all 2,481,012 observed entries. The original v2 baseline engine was never overwritten.','',
'Each surviving research candidate had a label = (profit > $0 after $0.02 simulated round-trip fee AND recorded exit within 30,000 wall-clock ms). Positions closed after 30 seconds are censored/not successful, because timeout is evaluated only when a subsequent quote arrives; a weekend-spanning close is not evidence of first-30-second survival. This is a coarse closed-trade proxy, **not** a fully event-ordered first-passage adverse-versus-favorable label.','',
'89 runtime-only feature columns were reconstructed from each trade entry’s matched quote and exclusively earlier raw ticks (250ms, 500ms, 1s, 5s, 15s, 45s, 5m, 15m, 1h, 4h bid/ask displacement, quote revision intensity, spread compression, realized volatility). The SYNTH teacher’s same-minute/side historical positive marker enters only as +5% sample weight for real-tick-positive training examples; no teacher or future label appears in the runtime feature matrix.','',
'## Complete ledger baseline','',
'| Source | Month | Baseline trades | Verified within-30s profitable exits | Source success rate | 85% SYNTH floor |','|---|---|---:|---:|---:|---:|']
for s in S:
 for m in M:
  r=json.loads((ROOT/'checkpoints'/f'{s}_{m}_feature_receipt.json').read_text())
  lines.append(f"| {s} | {m} | {r['rows']:,} | {r['labeled_win']:,} | {100*r['labeled_win']/r['rows']:.2f}% | {math.ceil(.85*ref[m]):,} |")
lines+=['','## Chronological walk-forward student and Neyman–Pearson optimization','',
'For each source separately, train on earlier months and current month through an early calendar cutoff; calibrate on later dates within the current month; evaluate on still-later dates. The entire source-month is used for feature generation; only held-out suffix dates constitute the reported chronological check. Older source-months can be in training but never later calendar months. The +5% SYNTH teacher weight applies only during fitting.','',
'The NP calibration was searched over nine false-class rejection quantiles, 0.50 through 0.999, using calibration dates alone. No candidate calibration policy simultaneously achieved >=80% net-positive within 30 sec and positive expectancy. Therefore runtime policy approval = **FAIL CLOSED / NO TRADING**. The following tiny nonzero selections were forced negative diagnostic choices only and must not be deployed.','',
'| Source | Month | Chronological check selected | Good30 rate | Net diagnostic | Days passing 80% |','|---|---|---:|---:|---:|---:|']
for s in S:
 for m in M:
  o=json.loads((R/f'{s}_{m}_chronological.json').read_text())['evaluation']
  lines.append(f"| {s} | {m} | {o['selected']:,} | {100*(o['win30_rate'] or 0):.2f}% | ${o['net']:,.2f} | {o['daily_pass_count']}/{o['daily_total']} |")
lines+=['','## Chronological check: generous volume-constrained score ranking','',
'As a deliberately optimistic *ranking diagnostic* only, the full-month 85%-of-SYNTH quota was prorated to each later chronological check window and the best scores selected ex post. Even with this retrospective threshold, no source-month approaches 80% survival; this is not a replay of changed entries.','',
'| Source | Month | Check AUC | Target check entries | Survival of best-scored entries | Net outcome |','|---|---|---:|---:|---:|---:|']
for s in S:
 for m in M:
  o=json.loads((R/f'{s}_{m}_heldout_volume_ranking.json').read_text())
  lines.append(f"| {s} | {m} | {o['auc']:.3f} | {o['heldout_check_prorated_quota']:,} | {100*o['score_rank_topK_survival_rate']:.2f}% | ${o['score_rank_topK_net']:,.2f} |")
lines+=['','## Full-month optimistic *in-sample* volume constrained model','',
'The final source-specific students were fitted using **all four real-tick months**. These are training artifacts only, **not** backtests or OOS. For a generous *upper bound on these fitted students*, the top exactly 85%-of-SYNTH count was picked retroactively from each full month. This uses future score distribution for the threshold and does not simulate newly available entries when earlier ones are rejected.','',
'| Source | Month | Quota selected | In-sample survivor rate | Modeled net | Days at 80% | Weeks at 80% |','|---|---|---:|---:|---:|---:|---:|']
for s in S:
 a=json.loads((R/f'{s}_in_sample_full_volume_boundary.json').read_text())
 for m in M:
  o=a[m]
  lines.append(f"| {s} | {m} | {o['quota_trades']:,} | {100*o['30s_survival_rate']:.2f}% | ${o['net']:,.2f} | {o['days_passing_80']}/{o['total_days']} | {o['weeks_passing_80']}/{o['total_weeks']} |")
lines+=['','## Perfect hindsight teacher supply ceiling (NOT EXECUTABLE)','',
'An unrealizable oracle that selects only trades whose future realized net was already known can find enough winners to meet the monthly volume floor in every source-month and at least one on every baseline-active day/week. This proves that the *recorded candidate supply* is not empty; it does **not** prove that a causal student can distinguish those trades. We must not convert this oracle into runtime entries, add its future labels as features, or present its ideal P&L as achievable.','',
'## Exact failure mechanism','',
'1. Win-prediction information from top-of-book quotes is weak: held-out AUC across source-months ranges about 0.52–0.60, far from the accuracy needed for 80% high-volume first-30s survivability.','2. Dukascopy spread and quote-side execution lead to adverse net outcomes much more often; a universal filter is not sufficiently broker-calibrated.','3. Each baseline trade occupies a position and suppresses other signals; selecting a subset of a fixed baseline ledger changes subsequent available opportunities. A fresh streaming filtered re-simulation is mandatory before calling any optimized model a real EA baseline.','4. The original high-volume lane does not use the trained BNP governor. The fitted student is an additive research artifact only, and cannot be described as an updated live/MT5 EA.','5. The current research still lacks exact *ordered* first favourable vs adverse barrier timestamps in the massive baseline ledgers. The strict within-30s close classification is necessary but not sufficient for path-survivability certification.','',
'## Next architecture-scientific action (not automatic deployment)','',
'Build a true quote-event/action counterfactual **BUY, SELL, WAIT, DELAY** router for each source, with fill-aware first-passage labels and no reliance on fixed baseline position availability. The 250ms to 4h causal feature bank and Hawkes signals remain, but trade timing/side must become the predicted action, not a mere veto after the old high-volume runner chooses direction. Then run real-tick chronological stream and grade EVERY source-day/week/month, +85% SYNTH volume and positive P&L. Otherwise fail closed.','',
'## Preservation law','',
'All feature data and model weights are stored in source-month recovery checkpoints; independent raw ticks and R9 SYNTH references remain pinned. The full scripts and output JSONs are preserved. **Do not replace originals with a summary, do not reclassify this training experiment as deployable profit, and do not delete unsuccessful experiments.**']
text='\n'.join(lines)+'\n';(ROOT/'docs'/'FULL_EXACT_TRAINING_AUDIT.md').write_text(text)
print('wrote',len(text),'chars')
