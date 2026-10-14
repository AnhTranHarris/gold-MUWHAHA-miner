# 2026-10-13 January crash recovery — exact-source read-only QA (NOT PROMOTED)

**Disposition:** RECOVERED / CHECKPOINT VERIFIED; NO new strategy trial, NO GAMMA switch, NO Numba/STMR completion claim, NO scientific-cursor change. Active branch: `delta-A-alpha`; machine truth: `CURRENT_STATE.json`, J0183, trading OFF, August SEALED.

## Authority and original sources
- Governing V1 whitepaper **full original blob** `1b92b3c89159681a7181508de158af685cf5780c`; full owner-ratified conversation and verbatim Jan–July roadmap are authoritative.
- Owner-locked January handoff: https://docs.google.com/document/d/1b70gn5xkvGJfVdxIvUu_0gSLpnsMJXb-GxmAaU9pPEU/edit (navigation, **not executable authority**).
- Immutable primary source: original January Dukascopy raw Bid/Ask CSV.GZ, Google Drive `1ghF2blUzJwwufFrD-P-1aS3bklGuOSHz`, **68,690,420 compressed bytes**, SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, **9,135,062 quotes**.
- Original GRID0272 complete 61-entry ZIP: Google Drive `1A-k1uK7sUWLNuIAuyR86CeqCVZV0QIc0`, retrieved ZIP 1,090,726 bytes; downloaded archive SHA-256 `0b1fed2144182ac8a2788ff86f399dac923ef630debdecfa702d28af882fbcc6`.
- GRID0271's 63 earlier negative/causal screenings remain frozen and **were not re-executed**.

## Independent QA performed in this recovery turn
1. Extracted the original ZIP without changing preserved code/results; **28/28 original helper SHA-256 values matched its exact-source manifest**. `ORIGINAL/stmr_base.py` and `ORIGINAL/stmr_janjul.py` are present; direct local import references resolve for `combine_original_latency.py`, `original_latency.py`, Watchdog 131A and these STMR helpers. This verifies the preserved GRID0272 import closure, **not** the unpersisted later Numba/STMR crash scratchpad.
2. Independently re-hashed the original source gzip: **SHA matched** the frozen manifest; read **9,135,062** ordered original quote rows.
3. Opened preserved `trades_cap256_hold1.0_interval125.npz` and the corresponding full `original_composite_raw_250ms_fee20_q1190_cap256_hold1.0_interval125.json`. Verified **24,589/24,589** entry and exit indices/timestamps against original ordered quote rows. All entry prices equal the actual BUY Ask / SELL Bid; all realized PnLs equal the exact opposing exit quote minus **$0.20** modeled round-trip fee: maximum absolute difference **0.0**.
4. Independently recomputed **+$66,234.286** modeled net, **+$85,681.125** gross profit, **−$19,446.839** gross loss, PF **4.40591527497**. All **21/21 UTC trading-day** and **5/5 ISO-week** archived net/trade-count/gross-profit/gross-loss aggregates matched.
5. Original report's independent research-only net-positive combinations remain **unpromoted**. The `q1190_cap256_hold1.5` earlier candidate is +$77,139.393 / 24,198 trades, but the 1.5x hold population is not the ledger verified in this step.

## Critical scientific blockers — unchanged
- The original 131A upstream **parent event/funded admission and prior settled-parent proof** were inherited from earlier assumptions. Downstream 250ms Bid/Ask child settlement parity is **not proof** that upstream parent funding/campaign gating is repriced and causally self-consistent end-to-end. Rebuild the actual funded source parent→child recursion using already-closed 0.01-lot after-cost outcomes; no invented broker DEAL_ADD.
- The 125ms coverage interval is an **experiment**, not the original 250ms interval; quote fill latency remains +250ms. Preserve distinct controls and campaign source identity.
- The January full ideal reference is R9 SYNTH **+$41,520.82 / 27,980 completed** plus all 21 trading-day and 5 ISO-week comparisons. This archived research variant has 24,589 trades and only 10/21 target-beating days, 4/5 target-beating weeks; no 100% full-system target.
- Global account capacity/heat, hypothetical equity DD (~$22,780.641 for this variant), initial $100/$200/$300 small-capital overlays, original offline R9 OVERFIT six-dimension 75% per-trade matching, February–July unchanged-regime replay, independent acceptance/owner QC, broker MT5 real-tick certification all **PENDING**.
- Numba/STMR combined-screen crash: available handoff reports “five dependency scripts materialized; mapped STMR imports,” but no NEW saved variant matrix, last process state, or completed sweep output exists in the verified original GRID0272 ZIP or the inspected owner-locked January Drive folders. **UNKNOWN / NOT VERIFIED**, not a completed experiment.

## Next scientific unit — precise continuation, NOT restart
Safely stage the original 131A/131D/WD119 source-parent admissions and previous CLOSED funded trade genealogy against observed actual original quote fills with 250ms request-to-execution delay, $0.20 round-trip cost and strict timestamp priority; ensure parent settlement is factored into unlocking 4 previously closed qualifying winners and immediately relocking after losing/slow renewal. Audit **W01** source and funded positive/negative after-cost population with conserved one-position-per-tick and global-cap exposure; compare the same 125ms/250ms preserved source populations without retroactive parent acceptance. Do not run identical GRID0271 failed screens or repeat GRID0272 candidate sweeps. Advance source code on `delta-A-alpha` **only after** exact regression tests and independently verified improvements. January QC remains PENDING; J0183, frozen accepted GRID0258, August seal, no EA or broker trading remain unchanged.

## Reproducer
Download original preserved ZIP and original canonical January gzip by the exact Drive IDs above; extract without changing byte contents. The independent recovery checker (read-only) verifies frozen original SHA, source import dependencies, original entry/exit quote prices, fees and daily/week aggregate arithmetic. It is a checkpoint integrity test only; it does **not** replace the funded parent/capital test or rerun 63 rejected historical screens.
