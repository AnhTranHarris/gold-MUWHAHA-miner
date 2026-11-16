# Micro180 V10 — causal R9 × Coinexx rebuild, entry-parity checkpoint

**2026-11-16 · Python research fork only · no MT5 orders, no micro180 V9 mutation**

## Source and immutable contract

- Parent commit: ba42a92c59d09f179607b2ab594de65a5705270c of
  carson/r9-v19-real-ticklogger-micro180-cycle-transfer-20261115.
- Original causal entry authority: source-faithful Python R9HybridGateBaseline
  v1.90 (blob a760b843577e53a3fa165273421b0270dba4f35e).
- Micro180 V9 four-lane 5s/15s basket × 15s/30s breakout,
  asymmetric directional_quant and original rolling 180-second quote observations
  remain preserved as evidence. Original V9 code, native R9, native V9, risk
  governors, production and live account settings remain untouched.
- Target historic teacher: existing merged
  r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz
  (SHA-256 9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5).
  Original teacher 272,352 trade references and 192,487 minute-cycles,
  **+$360,693.05 original MT5 net**, $0.01 entry/$0.01 exit commission and
  unchanged recorded swaps. Direct source audit (2026-11-16): all 272,352
  teacher rows include Coinexx quote marks; 271,544 entry marks are within
  the archive's <=2-second next-full-second matching lag, while 270,776
  trade records satisfy the lag rule for BOTH entry and exit; the remaining
  1,576 are out-of-window, not fabricated missing trades. The original
  190,937 complete cycles have both legs fully mapped.
- Research labels: (A) single-leg persistence, (B) favorable first-leg
  capture then developed reversal and opposite capture, (C) adverse initial
  movement followed by rapid opposite recovery. These are EX-POST outcome
  categories, **never an input feature available at the first entry**.
- The existing full-path reconstruction is a useful observed-outcome reference,
  not a claim that its retrospectively positive subsets can be selected in advance.

## Audit of the failed V9 architecture

V9's actual executable_or _process_entries requires:
1. previous completed 15s and 30s Bid/Ask second-close extrema;
2. matured current 5s and/or 15s basket;
3. same-side basket displacement and executable breakout;
4. original R9 S1 quality and position/risk eligibility;
5. V9's separate rearm cooldown and per-minute cap.

Those requirements can exclude an original R9 trade even when the source
R9 M1 bracket, completed-second directional quality, M5 ATR and live spread
would have qualified it. Therefore changing a quant coefficient or adding
a score filter to V9 cannot guarantee original merged-entry coverage.

## V10 architecture (actual new implementation)

- Micro180V10R9Causal INHERITS the frozen R9 tick state machine for the
  first-entry/exit/rearm reference. It does not paste R9 SYNTH future trade
  events into Coinexx replay and does not use a teacher timestamp to place orders.
- Every tick simultaneously updates Micro180 RollingThreeMinute, V9's
  MsQuarterPath, and the original R9 completed-S1 and M5 state.
- When frozen R9 qualifies an actual entry, V10 computes the existing four
  dual-basket lanes and asymmetric directional_quant on the SAME observed quote
  ordinal. Missing/misaligned dual signals are logged, not used to veto entries.
- Entry receipts record native quote ordinal, millisecond, BUY Ask or SELL Bid,
  R9 leg number, aligned/opposite four-lane evidence and quant availability.
- On each observed position update V10 tracks signed liquidation-price MFE/MAE.
  Once a position closes, it retains exit time, side, price move, reason,
  MFE and MAE. A later reverse entry can use the ALREADY OBSERVED first close,
  flat-interval duration and toward-reversal midpoint displacement.
- This immediately supports causal market-state interpretation of A/B/C
  without allowing a post-cycle family label to decide an earlier trade.
- For **entry-parity certification**, the initial V10 exit and rearm behavior
  remain the original causal R9 price-based baseline. This is intentional:
  changing exit management at the same time would change inventory, signals,
  rearms and entry coverage, making it impossible to isolate the entry defect.
- Native MT5 parity, broker fills, and proposed lifecycle redesign are NOT
  certified by this Python-only stage.

## Two distinct acceptance gates; never conflate them

**Gate 1 — exact same Coinexx chronological source R9 parity.**
Given identical source ticks, config and event ordering, R9HybridGateBaseline
and Micro180V10R9Causal must produce identical time_msc, side, quote-side
entry cents, initial SL, source minute, rearm number, close order/price/reason.
This is an executable reference *algorithm equivalence*, not teacher SYNTH match.

**Gate 2 — merged R9 SYNTH mapped-entry concordance (corrected source contract).**
With the **existing merged file**, measure EVERY reference row:
(a) next-full-second entry quote mapping lag <=2,000ms AND full-trade
entry+exit mapping eligibility (distinct denominators); (b) same cycle minute,
leg and direction; (c) candidate original R9 teacher SECOND agreement,
separately from the mapped quote time; (d) exact candidate BUY Ask/SELL Bid
price cents compared with the existing mapped quote reference, reporting
exact-millisecond and timestamp-tolerance results separately. Report complete-population recall AND the
exact price fraction. Unmatched rows remain in the 272,352 denominator, with
their original net unchanged. No alternate commission scenario.

**Crucial:** a synthetic original entry and an independently generated real
quote entry need not have the same timestamp or executable price. Source-price
equivalence is a measurable gate, not a promise. 100% source parity against
the real-tick Python R9 is achievable by construction if implementation is
correct; 100% SYNTH-to-real merged entry concordance remains an empirical
question and must not be declared achieved without the full file.

## Run without any raw-data warehouse rebuild

From research/coinexx_r9_chronological, after ensuring the original files
are already accessible:

    PYTHONPATH=src:variable_cash_horizon_20261114:dual_basket_20261114:micro180_20261114 \
      python micro180_20261114/run_v10_r9_merged_concordance.py \
      --ticks /path/to/original/coinexx/month1.csv.gz /path/to/original/coinexx/month2.csv.gz \
      --merged /path/to/EXISTING/r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz \
      --clock-offset-minutes VERIFIED_OFFSET \
      --out-json v10_compact_concordance.json

The offset is **required** and must be source-verified (broker/server clock
versus source epoch). For all nine months, supply the existing source files
in chronological order and add --require-full-272352. No new tick archives,
M1/OHLC rebuild, duplicate combined datasets, hyperparameter sweep or extra
fee scenarios are authorized. Result is one compact metrics JSON.

## Confirmed actual merged-file source audit and remaining boundaries

- Original file copied to primary Google Drive TRADING_RESEARCH:
  https://drive.google.com/file/d/1CC30szLw0_R9UpaRScPJZamgasqGjEsm/view
- SHA-256 confirmed: 9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5.
- 272,352 original rows, 192,487 first legs, 79,865 opposite second legs,
  unique (source minute, leg, side) keys in every case.
- 271,544 entry quote lag <=2s; 271,523 exit quote lag <=2s;
  270,776 records satisfy BOTH; 808 entry lags >2s, 829 exit lags >2s,
  61 fail both; the union totals 1,576 out-of-window records.
- Every entry and exit quote timestamp agrees exactly with its archived
  next-full-second anchor plus recorded lag, across all nine months.
- Original all-row R9 net retained: +$360,693.05, no fee replacement.
- The merged file contains teacher-selected event marks, not an unlabelled
  complete real-tick event stream or independent micro180/V10 entry observations.
  Therefore exact entry/price coverage remains a **not-yet-measured gate**, not a
  value that can truthfully be forced or asserted from marks alone.

## What we have NOT established yet

- FULL 272,352-row merged R9 entry recall or same-price concordance on Coinexx.
  The 11.23MB exact merged CSV HAS been reopened and source-integrity-verified
  in the current research environment; the independent 71.8M-tick source replay
  and new V10 candidate-entry ledger remain unavailable in GitHub CI. Fixture tests do not supply this evidence.
- Newly profitable independent complete-cycle system performance. The previous
  R9-on-real quote positive subsets were retrospective; new causal V10
  lifecycle families must be scored over the whole source and full accounting.
- Micro180 native EA compilations, signal parity, stop-modification latency
  or live/demo order authorization.

**Promotion condition:** first establish Gate 1 and Gate 2 with full actual
source records. Only then evolve a separate V10 quote-path lifecycle manager
for the three market families; all its decisions must use as-of information,
with full-system original-cost and drawdown accounting.
