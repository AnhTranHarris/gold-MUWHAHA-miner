# R9 v1.90 — CRITICAL ROLLBACK PIN (2026-11-13)

**Owner-authorized classification:** CRITICAL_ROLLBACK_REFERENCE / SOURCE-EXACT / NO LIVE-DEPLOYMENT APPROVAL.

## Immutable identifiers

- Repository: `AnhTranHarris/gold-MUWHAHA-miner`
- Canonical frozen rollback branch: `carson/r9-v190-critical-rollback-20261113`
- Exact rollback commit (not a floating branch name): `8729a6345655a7b4ea31facc81982004ee2b8921`
- Original historical branch: `carson/mt5-r9-hybrid-gate-certification`
- Baseline file: `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`
- Verified Git blob SHA-1 of baseline file: `7eecb5f1947017a01ce85b2520725de54749e523`
- Baseline `#property version`: `1.90`
- Original source URL: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/8729a6345655a7b4ea31facc81982004ee2b8921/Experts/GoldMuwahahaMiner_R9_HybridGate.mq5
- Research development branch (documentation only; do NOT conflate with baseline): `carson/r9-v190-entry-hold-exit-audit-20261113`

## Binding rollback policy

1. **Never edit, force-update, rebase or merge into the frozen rollback branch.** The pinned commit and blob, not any evolving experiment, are the recovery authority.
2. New R9 work must occur on a separate branch. In particular, v1.91/v1.92 QRB/QAF shadow telemetry and R9 M60 model experiments must **not** change the original R9 trade rules unless the owner explicitly authorizes an isolated development patch.
3. Before declaring a rollback completed, fetch the exact pinned commit, verify this source blob SHA, compile for the intended MetaTrader 5 build and account, and run rollback smoke/regression tests with recorded inputs and trade ledgers. **A source rollback is not evidence of economic profitability or live safety.**
4. If a new patch fails code compilation, behavior non-regression, tick-execution parity, trade state reconciliation or risk controls, **stop the patch**, retain diagnostics, and restore a new worktree from this pinned commit; do not delete or mutate the failed research lineage.
5. Reuse existing approved Coinexx/Dukascopy tick data and chronological infrastructure. No source dataset rebuild or large duplicate storage artifacts to prove a rollback pin.
6. All performance claims must distinguish synthetic MT5 Strategy Tester profit, actual-source tick replays, hypothetical paired-action AUC, commission/spread assumptions, and funded-account performance.
7. Research targets are **high-frequency throughput**, **aspirational realized after-cost net $1.75 or greater per completed trade** (not merely TP distance), and **average hold <=30s**, with whole-system risk, daily coverage and operational survivability. These are *not currently certified*.

## Existing source-level risks to audit before approving any deployment

- Tick-only 30-second time-limit check (`ManagePosition`, no independent timer).
- Stop/partial-fill reconciliation and `OnTradeTransaction` absent; request retcodes `PLACED`/`DONE_PARTIAL` can be treated as successful positions.
- `StartMinuteCycle` resets rearm state before position reconciliation across minute boundaries.
- The 10 recorded second-close window can span more than 10 wall-clock seconds; `InpMaxTurns=9` cannot reject the default sequence.
- `InpQuoteUtcOffsetMinutes=0` has not established the Coinexx server timezone; session ATR classification may shift.
- No account-level loss/margin/drawdown protections in original EA.
- `OnTick` event coalescing can suppress intermediate quote revisions; v1.92 telemetry remains observational, not a lossless tick tape.
- No fixed TP; 30s timeout is an EA-requested close rather than a broker-side guarantee.

## Evidence and status

Previously recorded Coinexx Jan–Sep MT5 M1 Strategy Tester audit: 272,352 completed positions, +$360,693.05 tester net, +$1.3244/trade, 17.24s average hold; **not independent real-tick execution certification**. Original 2026-11-13 155-feature R9 M60 research mean pooled ROC-AUC ~0.7385 / original R9 side ~0.7232 on exposed months, with no positive-utility model trades. The owner's preferred AUC 0.75 is a development aspiration, not permission to relabel source data or claim trade profitability from AUC.

**This file is a rollback policy and source identity receipt only. It makes no EA source modification and authorizes no live orders.**
