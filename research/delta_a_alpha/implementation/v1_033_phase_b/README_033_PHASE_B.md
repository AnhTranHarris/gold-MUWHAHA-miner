# Original V1 funded kernel 033 — Phase B (context-safe exits + real original 019 parity)

**Status: engineering partial / NOT full original eight-layer V1, NOT broker certified.**
Owner-frozen full and literal whitepaper `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt` remains unchanged (Git blob `1b92b3c89159681a7181508de158af685cf5780c`). This Phase B is an incremental repair of Phase A under existing owner V1 requirements; no strategy changes and no Jan/Feb historical research promotion.

## What was recovered from the chat timeout

Phase A had been completed, tested and journaled as **0066** (23 tests). Phase A includes an actual-fill event-state ledger, non-shadow Watchdog earned credit, a bounded conditional-recovery eligibility gate, common order/heat/position capacities and original archived 019 hourly candidate adapter. It is intentionally incomplete for original L1/2/3 breadth, true full L4/5/6 generators, and Coinexx L7 parity.

## V1 safety flaw corrected (without changing trading policy)

Original Phase A `process_quote()` returned early whenever `s is None` or `Structure.valid_at()` failed. It therefore could **skip protective TP/SL/expiry and queued risk exits**, and would only mark floating equity without attempting liquidation. The Phase B kernel executes and evaluates actual close requests on every real Bid/Ask tick **before** deciding whether an authentic completed HTF state permits *new* opportunities. No missing history creates a fabricated entry. A failed order due to the shared rate budget remains funded, floating and queued.

`FundedEngine.enter()` now requires a quote that matches the active execution-loop quote/time; a direct out-of-sequence order is rejected. This is a boundary hardening—not MT5 broker certification.

## Independently verified tests and real data

```
cd /mnt/data/DAA_033_implementation_phase_b
python -m unittest -q test_v1_funded_core_033.py test_original_heartbeat_parity_033.py test_scorecard_033.py test_broker_context_safety_033b.py
python real_original019_entry_parity_033b.py --root /mnt/data --max-events 1136212 --out REAL_019_PARITY_033B.json
python real_dukas_event_smoke_033.py --root /mnt/data --max-events 1136212 --out REAL_DUKAS_SMOKE_033B.json
```

- **31 contract tests passed** (original 23 + eight Phase B safety regressions).
- **43,105 of 43,105** original 019 source-UTC heartbeat **candidate-entry records matched exactly** on **1,136,212 consecutive February raw quotes** and 3,900,880 real January warmup quotes. This validates only the *original 019 candidate generation* with the original diagnostic completed EMA-sign states, not all L2 role semantics, full grid, funded results, or complete V1.
- Same real February **L3-only diagnostic** portfolio reproduced the previous Phase A score **exactly**: net `-$583.745`, 836 complete trades, PF `0.72462261`, max all-quote DD `$1,158.88` with diagnostic $100K balance, max 16 open, 3 orders/second. This is NOT February-month strategy profitability or the accepted FEB047 policy.
- The February raw compressed file and JAN037 source bundle SHA-256 are reverified in parity scripts; no March, August or September signals accessed.

## Research history preserved, not overwritten

JAN039 historical research result +$201,226.483/12,520/PF37.1768/GL−$5,562.307/DD$12,640.925; FEB047 highest-profit +$206,303.048/PF28.09/GL−$7,615.393/DD$17,183.829 and lower DD +$200,329.84/PF23.97/GL−$8,721.152/DD$15,741.936. These remain immutable **source-proposal research**, not proven fully funded broker outcomes. Original V1 whitepaper, `Experts` MQL5 observe-only v1.05, and production `delta` branch are untouched.

## Gate 033 still open (Phase C next)

The remaining work is source equivalence for original L1 session/Asia grid, complete L2 role semantics, all original L3 generators, fully endogenous native L4 campaigns `049→051→075→084→119→131D/E`, L5 native specialist, L6 bounded failure-owned entry/exit generator, physical L7 Coinexx symbol/margin/stopout/order-rejection reality, and *then* full JAN+FEB 16.67m quote regressions with actual funded descendant recomputation, MT5 parity and small-account certification. See `PHASE_B_QA_033.json`.

**Do not start March until full owner V1 funded execution parity is established.** Original 5-minute ready-from-first-valid-quote startup and genuine pre-T0 H4/H1/M15/M5 history remain mandatory; no month-name settings. August sealed, September reserved.