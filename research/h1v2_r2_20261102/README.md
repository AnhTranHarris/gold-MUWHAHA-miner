# H1V2 R2 — In-sample extreme skew teacher (2026-11-02)

Source-exact additive research extension from H1V2 parent `edce573d9c53b743dc5de1b0d741c81370af52c1`.

**Complete authoritative code/model/binary recovery** in primary Google Drive: [H1V2_R2_FOUR_MONTH_EXTREME_SKEW_SOURCE_EXACT_20261102.zip](https://drive.google.com/file/d/11vsLhtdkDUfdEF34Q7zPYqpIJibu-aPV/view). SHA256 `4105f83b7562c36cf9eab94c190bf99ea7b191ee9de713a25daf460e7e7f692e` (38,400,584 bytes, 53 ZIP members including manifest; 52 file hashes). This GitHub branch commits human-readable reproducible scripts and experiment receipts; the full Drive ZIP additionally holds 8 original-ordinal trace sets, 4 hard-negative feature archives, and all fitted model `.txt` files. Original full H1V2 source dependency kit retained at `https://drive.google.com/file/d/14Zqs-PyZ70qr0NTvpJRxpT0XcVc8msUu/view`.

## Scientific outcome

- Hindsight exact original R9 quote-ordinal DP re-optimized under **<=3s first good hit, >= $0.10 final net, <= $1.00 spread**: January 67,124, February 57,710, June 77,943, July 38,682; combined 241,459 nonoverlapping future-confirmed events. Meets all original R9 SYNTH monthly 80% count floors, but NOT an executable predictive policy.
- Alternate **<=5s, >=$0.20, <=$1.00**: 211,096 nonoverlapping future-verified selections.
- Four-month side-specific strict teacher classes: WRONG 99,341; NEUTRAL 4,898; WEAK GOOD 12,517; STRONG GOOD 3,244 among 120,000 paired-action training targets.
- All-four-month trained S1 student **3,219/3,219 strictly correct at 0.30** on the SAME training observations. Jan+Feb+June-only S2 student July held-out **9/252** strictly correct at 0.10. Model transfer FAIL. Neither is authorized for live use.
- 15/15 original + R2 tests passed. All 452,555 re-optimized selected instances across the two configurations reconciled exactly with original frozen quote-ordinal teacher label, first-hit and R9 exit/net. No MQL5 deployment/rollout.

Read the complete `H1V2_R2_RESEARCH_VERIFICATION_20261102.md`, all `src/` code, receipts, and the original parent source, not prose summaries. Keep the 2026-01/02/06/07 Dukascopy raw ticks SHA-pinned, preserve original causal tick engine and original H1V2 baseline. Do not use future `side_class`, `first_ms`, or `net` as model inputs.

## Reproduction

The scripts currently default to `/mnt/data/h1v2` and `/mnt/data/h1v2_r2`; restore both original package and R2 package to these directories (or adjust the source path constants explicitly in an isolated research copy). Run `PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src pytest -q /mnt/data/h1v2/tests/test_h1v2_teacher.py /mnt/data/h1v2/tests/test_h1v2_geometry.py /mnt/data/h1v2_r2/tests/test_h1v2_r2.py`. Re-run source-exact strict DP from original teacher arrays if necessary. Never substitute M1 synthetic candles for ordered bid/ask ticks.

**Research only — no approved model, demonstrated foresight 80% precision, realized trading profits, or live execution claims.**
