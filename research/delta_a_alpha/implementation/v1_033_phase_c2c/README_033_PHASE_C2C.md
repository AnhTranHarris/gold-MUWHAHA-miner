# Delta-A-alpha V1 Gate 033 — Phase C2C: funded 119 multiple-parent causal contract

**Status:** PARTIAL ENGINEERING VALIDATION. **Not complete source parity, funded economic V1, profitable February simulation, nor an MT5 EA release.** All eight owner V1 original layers (L0–L7) remain binding under the entire verbatim whitepaper `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt` (Git blob `1b92b3c89159681a7181508de158af685cf5780c`). This handoff is NOT a substitute for reading the whitepaper.

## Prior C2A/C2B proof carried forward

- Original `049` NY16/17 `001 + 017 + 019` entry-source union on the 1,136,212 real February Dukascopy quote segment: **13,063 / 13,063** identical entry indices, directions and source; 1,305 NY extension, 14 NY17 rebreak, 11,744 120ms heartbeat. Exact source-entry parity, **not final funded 049/051 parent-admission parity**.
- Original realized-only 049/051 surge selection matches archival index selector on synthetic fixtures. Phase C2A and C2B plus C1/B/A produced **47 inherited passing tests**.

## New C2C: actual-closed-child earned parent renewal

- Source: `original_119_multi_parent_033c2c.py` + `v1_funded_core_033c.py` (isolated Phase C kernel copy, no overwrite of owner V1 EA). **Real L3-funded** eligible parents create 119 NY-local macro-cell windows; the *first* in a cell may scout. Subsequent L3 parents in that same cell can open another paid child campaign window **only once four already executed, profitable, sufficiently fast L4 child closes have earned renewal**. A losing or slow L4 child close clears this earned permission and relocks subsequent parents. Each child is linked to an accepted parent window; exit events are quoted Bid/Ask, owned and observed before a new decision. A parent closure schedules reduce-only treatment of funded children in its window. Each L4 child uses an independent fixed 0.01 lot, finite TTL and recorded costs; no orphan/denied/phantom child sponsorship or Martingale.
- Existing kernel had consumed `campaign.earned` at *child entry*; C2C corrects this for original C2C 119 paid child, because a cell's earned state should respond to actually **closed** child outcomes, not simply new admission. A native `ORIGINAL_119` child without a genuine parent ID is now fail-closed; other preexisting distinct L4 sources keep their contract behavior.
- Five new deterministic causal contract tests pass: earned subsequent second parent from four realized success children, losing child relock, rejected parent cannot sponsor, new child entry does not burn earned permission, and no same-quote rearm even when rate budget permits multiple orders. **52/52 combined original and new Python tests pass.**

## February real-Dukascopy diagnostic, NOT monthly strategy performance

The same previously verified *contiguous subset* and authentic January context used by C2B were executed again **after** these safety patches:

| Metric | Phase C2C full source diagnostic |
| --- | ---: |
| February quotes consumed | 1,136,212 |
| Actual Jan prior context quotes | 3,900,880 |
| Original NY16/17 049 entry-source events | 13,063 |
| Accepted first 119 parent windows | 4 |
| Eligible funded 049 parent candidates | 62 |
| Denied unearned later windows | 58 |
| Actually earned later 119 parents | **0 in this segment** |
| Accepted funded 119 children | 19 |
| Closed mock-account trades | 209 |
| Net model P/L | **+$54.602** |
| Gross loss | **−$1,899.091** |
| Exact quote-equity DD | **$2,339.194** |
| Maximum simultaneous funded positions | 32 |
| Combined max orders/second | 4 |

The absence of a second earned actual parent in this sampled segment **means real-tick multi-parent equivalence is not demonstrated**. The controlled fixture demonstrates the causal policy, not the full original-source real-market event distribution. Model capital was $100,000 with idealized quotes, mocked margins, 32 max open and four orders/sec; original full L2 structural-role parity, actual original 075 research parent windows and 084/119 later earned-parent selection, L5/L6 signal generation, and Coinexx physical L7 execution are NOT certified.

## Where Phase C2C is intentionally incomplete

1. Archive `119` uses a precomputed `084` child simulation and a 4-realized-fast-success gating *cell*. The C2C adapter implements this online for **genuinely funded child outcomes** but original full `075/084/119` entry and exit ordering, residual close handling, full source universe, and exact real-data multi-parent admissions are NOT independently matched.
2. `049` original physically admitted parent candidates and `051` live cap remain only proven on controlled selector fixtures, not all real NY16/17 eligible parents after distinct valid fills and quote-side closes.
3. Original L1 separate Asia and other sessions, full role-separated L2 H4/H1/M15/M5, remaining L3 source coverage, L5 native specialist selector, L6 independent failure specialist, broker-verified L7 Coinexx hedging/margin/stopout, five-minute startup readiness and complete January+February funded economic replay remain pending.
4. This checkpoint does not modify approved JAN039 or FEB045/FEB047 historical *research-only* references and does not promise their profit figures will survive reconstruction. The original V1 whitepaper, MT5 observe-only EA and production Delta are untouched. March remains held. August sealed, September reserved.

## Reproduction

From the ZIP contents with the previously SHA-verified Jan/Feb Dukascopy archives and `JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip` mounted at `/mnt/data`:

```bash
cd /mnt/data/DAA_033_phase_c2
python -m unittest -q test_v1_funded_core_033 test_original_heartbeat_parity_033 test_scorecard_033 test_broker_context_safety_033b test_original_online_sources_033c test_original_funded_lineage_033c2 test_original_ny049_union_033c2b test_original_119_multi_parent_033c2c
OPENBLAS_NUM_THREADS=1 python real_integrated_033c2c_smoke.py --max-quotes 1136212
```

The diagnostic uses the original `stmr_janjul` EMA-sign states for source context, NOT the full original H4/H1/M15/M5 role-exact state. It **must not** be labeled an original V1 whole-portfolio result.

**Next:** 033 Phase C2D: source-equivalent 075/084/119 funded event sequencing on sufficiently representative real source streams; then full L1–L6 and broker L7 parity, followed by complete January and February regression before March.