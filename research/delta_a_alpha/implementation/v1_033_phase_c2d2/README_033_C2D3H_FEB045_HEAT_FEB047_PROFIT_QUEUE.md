# DAA-033 C2D3-H — Source-true FEB045 heat + FEB047 strict profit queue

**Authority is the original complete executable Python sources, not this README.**
Do not reconstruct the modules from this text. Read and compare complete files:

- `verified_original_sources/FEB045/heat_engine.py`
- `verified_original_sources/FEB045/engine_statecaps.py`
- `verified_original_sources/FEB045/run_heat_screens.py`
- `verified_original_sources/FEB047/queued_reduce_only_047.py`
- `verified_original_sources/FEB047/FEB047_STRICT_BEST.json`
- `feb045_source_native_context_033.py` already accepted in journal 0082
- `v1_funded_core_033c.py` existing single physically funded L7 kernel, carefully additive edit

The new adapter `feb045_physical_heat_feb047_queue_033.py` extends **FEB045NativeQualityL3** with existing broker-funded long/down vs short/up stress and per-source financed inventory, *not* a second account. It uses actual funded entry callbacks for original source price gap and cooldown. Original optional heat thresholds are configurable and default source-neutral when the frozen source used inactive caps; profit source is never fabricated. The portfolio stress remains `max(long_directional_loss,short_directional_loss)`; source-stress uses the sum of the separately clamped source long and short losses. No date/month identity is examined.

`FEB047QueuedProfitReduceL7` implements the original `queued_reduce_only_047.py` strict parameters from `FEB047_STRICT_BEST.json`: price retreat 2 USD, 36 observed five-second samples, source S22/S25, dominant side count at least 400, individual net profit at least 7 USD, physical batch up to 32, cooldown 60 seconds, optional account DD 0; original 10 orders/UTC second and one physical order/observed quote. For small deterministic fixtures, thresholds are lowered through explicit test configuration (never a performance claim). Only actually filled positions can be reduced; L7 books the close through executable Bid for longs and Ask for shorts, including the existing 0.02-USD modeled roundtrip fee at fixed 0.01 lot.

**Safety invariant:** An optional FEB047 reduce may be delayed by combined L7 physical order limits. On each actual quote where L7 can execute, `v1_funded_core_033c.py` must re-evaluate the executable position net P/L and CANCEL a once-profitable request that no longer clears the floor. Explicit unconditional emergency `request_reduce`, SL, TP and TTL retain priority and are NEVER prevented or converted into conditional profit orders. All accepted closes invoke the existing downstream `on_funded_close` callbacks; no hypothetical trade affects campaign earning or account cash. Same market state on Jan/Feb/June dates must produce the same funded behavior. The source's selected strict case was fitted on February, so month-blind logic is necessary but not proof of out-of-sample performance.

**Boundary:** The original FEB047 script evaluated an already-frozen FEB045 accepted event ledger and its ~200k PnL is not present in the V1 kernel. This phase only certifies deterministic February source accounting and physically funded contract/unit parity; it does not claim the *source-generated* original complete Jan/Feb profit frontier, broker verification, Dec2025 pre-Jan1 startup, original four-role classifier completion or full year blind outcomes. The original FEB047 selected queue was not a proven drawdown-under-10k solution; original 1536-peak portfolio does not equal current kernel 512 cap. Preserve the original JAN039 and FEB045 research results without copying their P&L into a new engine.

`python -m unittest -v test_feb045_heat_feb047_queue_033` runs the targeted suite. GitHub CI must additionally run the 54 tests from C2D3G plus these tests. `test_original_unmodified_feb047_function_agrees_on_first_real_close` independently executes the unchanged *original* FEB047 run() function on a synthetic accepted tape (using AST extraction solely to bypass its absolute-path research imports) and matches the funded engine's executed quote index, ticket, and net P/L. This is a tiny strict fixture; **not** an actual 11.4m February economic replay.

Expected immediate next scope: verify *full* endogenous original February source generation through L0-L6, exact physical heat/entry/exit monthly replay, Jan/Feb economic parity, actual Coinexx MT5 fills. March HELD. August SEALED. September RESERVED. Production Delta read-only. Fixed 0.01 lot and no Martingale/DCA.