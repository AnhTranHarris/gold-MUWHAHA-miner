# DAA 033 — C2D3G / FEB045 Native Quality and Completed Auction-State Gate

**Authority**: [Unabridged owner V1](../../whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt), original [Jan-1 hardlock](../../governance/DAA_V1_WHITEPAPER_HARDLOCK_STARTUP_JAN1_031.md), live `CURRENT_STATE.json` journal 0081, original JAN039 and FEB041/042/044/045/047 source files. **Do not replace FEB045 with a summary.** This gate adds *one tested L3 source-selection layer only* to the already cumulative V1 funded kernel; it does not replace sources, first touches, multi-timeframe classifiers or global L7.

## Original source and exact selection

The unchanged source code bodies, preserved byte-for-byte under `verified_original_sources/{FEB042,FEB044,FEB045,FEB047}` here, are the executable authorities. Further original archives in the persistent Project Library:
- `FEB042_ITERATIVE_FEBRUARY_RESEARCH_BUNDLE.zip` SHA-256 `708e81a8f8ed103b6e552ff597ef9048e3191d6f00cce59374df9e1607f56500`
- `FEB045_UNIFIED_HEAT_GRID_RESEARCH_BUNDLE.zip` SHA-256 `9248646bf099b954b5661c765ce50316a61c015b595ad61128a0c02b115a33df`
- `FEB047_PORTFOLIO_REPAIR_RESEARCH_BUNDLE.zip` SHA-256 `e45987edf986fa7b5827c503afbf824d90d47593c59dc2f2955f2a0d41aa5f42`
- Original `feb044_screen.py` from Library, SHA-256 `2d2d04d6910d61d6b88b9549ecbcb0962ab67955e625a3f91f1cdefee34ea434`.
- Original source member byte hashes are recorded in `FEB045_SOURCE_GATE_033_MANIFEST.json`. Original full owner V1 Git blob `1b92b3c89159681a7181508de158af685cf5780c`; original core Git blob `931fb6f9e6a73af8036572292e53f550a6873f07`. Both frozen.

`feb045_source_native_context_033.py` implements literal Boolean selection, no extrapolation: FEB044 `base_allowed`, original FEB045 six `reject` terms, exact added S22/S24/S26 source-range permissions, source-ID exclusions, and first **nine** ordered FEB045 quality exclusions from `run_pocket_screens.py`. The 10-minute subphase is UTC `(time_ms // 600000) % 6`; observed completed 10-minute range is prior `max(raw midpoint)-min(raw midpoint)`; source entry-side impulse is prior observed-quote midpoint displacement from the earliest available tick at or after `entry_ms-20000`. This follows original FEB041 source output and FEB042 `feature_attribution.py`/`prepare.py` data semantics, but must not invent unavailable prehistory. The first arbitrarily truncated 10-minute bucket is disallowed as a trusted feature.

Original source S17-S27 labels are mapped **only** when an *actual upstream source adapter* emits `ORIGINAL_F045_S{int}` on L3. This label identifies strategy provenance, not market month. Matching proposals are then filtered; all other original January, L4, L5, L6 specialists pass through untouched. Missing completed causal 10-minute context denies S17-S27 original-family physical proposals but does not delete their upstream shadow candidate count. The gate never generates a new opportunity and never counts future P/L as realized.

Source capacity uses `engine.positions` (genuinely physically filled, one shared account), not frozen accepted tape. FEB045 default quality research cap `cut=9`; original fixed chosen S22/S25 state caps = 512/512, thresholds 32/64 USD and original source caps S22 768, S26 432, S25 4096. S25 phase1 cap 896 / phases3-4 cap1024. The existing L7 global/broker constraints have final authority; no port unilaterally boosts its cap to the exploratory FEB045 1536 high-risk positions. FEB045's native source exits, complete original L5/L6 and eventual FEB047 queued reduce-only remain separate source-reconstruction gates.

## Evidence, run offline without March

**Exact original FEB042 source proposal archive**: 234,698 original entries, where independent vector reconstruction of raw original FEB044/FEB045 code approves **34,063**; native candidate-by-candidate Python policy approves **34,063**, with **zero disagreement**, same 234,698-bit source mask SHA256 `4d8a1dd6a5d97812edd9fe97eaa2c876871a84e1097c2e96c42e33e8fd87936f`. The frozen arrays used are `FEB042_JAN039_PREPARED_PROPOSALS.npz` and `FEB042_CAUSAL_ENTRY_FEATURES.npz`; `audit_feb045_exact_original_masks_033.py` exactly reproduces this source-stage oracle, no future outcome stream included. This audit does not simulate funded descendants, physical portfolios or optimized future exits.

**Original FEB041 quote context**: complete actual source `XAUUSD_DUKAS_2026_02_ticks.csv(3).gz` SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`, exactly **7,538,339** quotes, exactly **2,745** previous-completed 10-minute bucket records vs the original `FEB041_COMPLETED_10M_CONTEXT.csv`: zero mismatches in quote count and range. Uses `audit_feb041_completed_10m_ranges_033.py`; no synthetic bar or month-based execution input.

CI runs all inherited Python contracts plus the new February gate and frozen-source SHA contracts on Python 3.11. The raw February quote and prepared source arrays are external Library dependencies; CI **does not pretend to rerun these multi-million-quote audits**. Their byte checks and offline replay results are recorded in JSON.

## Scientific boundaries — not accepted full February V1 economics

Original FEB045 research had 25,443 trades and +$206,528.578 at $19,308.087 full-quote DD for a **frozen, February-fitted source tape**; both this archive and FEB047's +$206,303.048 / DD $17,183.829 were in-sample experiments, not integrated causal funded V1 with true endogenous source regeneration and Coinexx MT5 fills. All original L0–L7 layers must remain operational together. This unit implements exact *candidate mask semantics*, not original FEB045/47 trade volume, realized economics, native Watchdog genealogy or source-specific portfolio profit. January optimized 039 (and FEB source state) never chosen by calendar month. March remains **HELD**, August **SEALED**, September **RESERVED**. This is one bounded engineering chunk toward the owner gate 033.

**Next**: implement FEB045 original source/heat constraints and FEB047 actual L7 queued profitable reduce-only state using the exact full original `queued_reduce_only_047.py` and independent reference, with all orders costed across one physical broker account; derive full original FEB045 source proposals causally before claiming Jan/Feb parity. Fail close if original L2 classifiers are absent. MT5 EA and production Delta untouched.
