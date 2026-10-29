# F401-R120 — multi-disciplinary native-tick multi-clock trend / session / dynamic-grid geometry
**Date:** 2026-10-28 (source dates), research continuation only. **Status:** IMPLEMENTED / SOURCE-TESTED / ORIGINAL-EVENT ATLAS COMPLETED / **FILTER NOT APPROVED**. No live, native MQL5 or whole-account performance claim.

## User corrective observation addressed
The preceding R118/R119 program incorrectly prioritized generic quote-response/economic entry classifiers and did not maintain explicit **0.25s, 0.5s, 1s, 5s, 15s, 30s** subminute trend candles, **M1/M5/M15/H1** completed-structure anchors, dynamic support/resistance grids and overlapping per-session evolving geometry. R120 is a new independently executable mathematical **STATE PUBLISHER**, not another bad-score LightGBM retune or false breakthrough notice.

## Source-exact causal state contract
- PRIMARY original authorized Dukascopy tick quotes (XAUUSD only), chronological bid/ask raw integer prices and quote-size proxies; four pinned month gz inputs January, February, June, July 2026. Verified SHA256:
  - January `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
  - February `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`
  - June `34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2`
  - July `e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7`
- Original untouched F395 S14 eight-cell artifact supplies **frozen original per-event `t`, side, original index, three-class truth and original historic F392/F395 SHADOW masks**. Read-only; 4 Dukascopy cells evaluated in this branch, not all 8 broker-months. Native **32,290,648 real L1 quote ticks** → **1,266,934 original event IDs**. Jan **344,037**, Feb **324,582**, Jun **297,035**, Jul **301,280**. Original labels unchanged; no event dropping.
- For event timestamp `t0`, micro publisher **consumes only quote ticks with `t_tick < t0`**; every shorter candle has true OHLC over published ticks, and a candle becomes completed only once its end boundary is `<=t0`. Developing candle is only formed from strictly earlier quotes and is marked separately. Empty tick intervals are NOT synthetic candle fills.
- Fixed UTC session windows: Asia 00:00–09:00, London 07:00–16:00, New York 13:00–22:00, with overlap and daily reset independently tracked. These are **explicit UTC proxies**, *not* proven DST-correct exchange-calendar/session data. Session state: anchor displacement, running high/low, S/R distance, signed quote-price revision flow, quote activity. There is no true aggressor traded volume or L2 depth.
- Completed HTF publisher consumes original source raw ticks, groups into M1/M5/M15/H1 OHLC, past-only rolling envelope, directional trend slope/acceleration, normalized path efficiency, trend-side rank, quartile GRID proximity and quote-activity/staleness. **Only bars with observed interval bucket strictly less than `floor(t0/width)` are eligible**: the current HTF candle is NEVER visible. No trade-trigger gating to bar close; every original eligible original signal t0 receives a multi-clock state.
- Total **128 computed features**: six micro resolutions ×11=66, three overlapping session states ×6=18, 8 interscale/clock/spread summary =92; four completed HTF scales ×9=36. Actual dynamic support/resistance grid is **five quartile nodes of each completed observed high–low envelope**. It is a geometric STATE grid, **not** an executed dollar lot ladder or trading-grid order lifecycle.

## Advanced mathematics realized (not merely invoked)
For time scale h, the completed-bar directional slope is `u_h(t0)=side*(C_0-C_{-4}) / max(H_{past16}-L_{past16},tick_floor)`. Acceleration is a second difference `side*(C_0-2*C_{-4}+C_{-8})/range`. Path efficiency `|C_0-C_{-8}|/(sum_recent |ΔC|+1)` separates persistent drift from high-volume oscillation. Dynamic grid distance `|4r-round(4r)|`, where r is directional range position, measures proximity to 0/25/50/75/100% geometry; quote count is activity only. Cross-timescale conflict uses side-aware micro/30s slope disagreement and higher-timeframe squared coherence `(sum u_h)^2/(4 sum u_h^2+ε)` / adjacent gradient shear `sqrt(mean(diff(u_h)^2))`. THESE are actual implemented causal quantities, not claimed predictive alphas. Session anchors evolve independently and can overlap.

**Dual-factor FIT-only structural manifold:** robust-scaled 24-state micro/session MiniBatchKMeans and 12-state completed HTF MiniBatchKMeans; frozen 24×12 **288-state product manifold**. Both codebooks fit **only first 60% of JAN chronology**, excluding 60 s around the segment boundary; no original teacher or event outcome used to fit phase centroids. Retrospective three-class error census for all four source months uses original labels strictly **after** state creation as a scientific diagnostic. These four months have prior research exposure and are **not blind OOS**. Group identifiers have meaning only with archived fitted codebooks and exact frozen feature definitions.

## Measured original-source event structure — not a veto policy
- The 24-state micro-only manifold found **micro phase 11** with original incorrect = **34,452**, original correct = **17,505** across the four months. Months: Jan 5,025/3,156; Feb 11,875/6,110; Jun 5,827/2,786; Jul 11,725/5,453. Within phase, wrong event fraction rises from 61.4% Jan to 68.3% July (historically exposed); no close-to-zero protected correct-loss result.
- The 24×12 product regime **state 141** appears with original incorrect **15,225**, correct **6,662**, and at least **64.8% incorrect** in EACH four month. Individual source-cell counts:

| Dukascopy month | Original wrong | Original correct | Wrong fraction |
|---|---:|---:|---:|
| Jan | 1,871 | 1,016 | 64.81% |
| Feb | 4,750 | 2,052 | 69.83% |
| Jun | 2,630 | 1,103 | 70.45% |
| Jul | 5,974 | 2,491 | 70.57% |
| **Total** | **15,225** | **6,662** | **69.56%** |

**Important:** These are source-class concentration counts, not newly vetoed signals. Choosing this state as a veto would lose 6,662 known originally correct signals; it does NOT meet the owner's highly asymmetric filter acceptance, original January 94,603 wrong/7 right same-month fitted historical teacher, >400,000 target or cooperative 71/90 gate. The concentration is an identifiable *source-native trend geometry phenotype* suitable for multi-phase specialist construction and correct-preservation subclass research, NOT deployment.

## Tests and preservation
- Deterministic synthetic causal tests PASSED: 250ms exact boundary, equal timestamp excluded, future-suffix mutation invariance; completed HTF 60s boundary and forward mutation invariance; Asia/London and London/NY concurrent state and daily UTC reset.
- REAL native JAN test PASSED: original first **80 event** states identical for whole tape versus clipped strictly-before-last-event quote prefix for BOTH short clocks and completed HTF.
- Readback PASSED: all four original event populations and original labels, micro source hashes, HTF cache hashes, finite feature count/shape 92+36, 24-state / 288-state IDs and original-event recount. Full caches stored locally, not duplicated in delivery ZIP; deterministic rebuild scripts and SHA receipts cover all four.
- Source scripts are self-contained on frozen original sources and accepted Python numpy/pandas/numba/sklearn modules. No core engine rebuild. Original F395 archive, past approvals, PRIMARY Drive, G gates, MT5 release all untouched. THIS IS AN UNAPPROVED RESEARCH STATE PUBLISHER ONLY.

## Owner-governed productive next scientific direction
Build an **original-side, joint structural regime / session-specific trend-transition specialist** using the stable 24×12 source-state product. Research high-support *incorrect-concentrated* conditional motifs in a **FIT-only, cross-month, offset-aware** prototype dictionary, e.g. current partial 250ms body × 5s/15s curvature × 30s grid rebound × M5/M15 structural trend × active London/New York session. Learn multi-signal, time-since-regime-switch persistences from native pre-t0 history. Add **independent correct-opportunity rescue** and compare genuinely incremental veto overlap with authentic frozen approved F234 masks when recovered. Use calibrated hard right-loss cap, 40s+ purging, broker-specific parity, 4178 supply windows, and newly timestamped bid/ask action economics if an actual *unsubmitted intent* is used. No 1+1 generic repeated cutoff search. If the new geometry specialist loses good events in a broad state, subdivide using **new independent phase-history information** rather than accepting weak 2:1 selectivity or retuning basic thresholds.

**Community methodology references (reviewed, NOT imported into causal engine):** STUMPY multidimensional motif/subspace matrix profiles https://github.com/stumpy-dev/stumpy ; finlab-ml purged CV/imbalance/run bars and statistical state methods https://github.com/landtml/finlab-ml ; VectorBT published multi-TF resampling explanations https://vectorbt.pro/tutorials/mtf-analysis/. The current experiments do not claim to have imported STUMPY or achieved either library's backtest economics.

**Next cursor:** R120 causal multi-clock/session state-extractor and original source diagnostic done, unapproved; next R121 geometry conditional-specialist / robust constrained veto, not yet fitted/tested. Original M-DK-01 open; original 21/39 owner research-stage approvals and G01–G09 unchanged. All four source-native monthly tick files remain separately pinned in PRIMARY Drive. No unverified Coinexx session/calendar assertions.

## Verified active executable source archive
https://drive.google.com/file/d/1SgTaqCcahybXZx8dvL0tQcX204EseZ-3/view
SHA-256 6deefed410ec1946741c88b21252c103347d2e1ae7f4617e4788dbb54211418f; complete 33-member ZIP; source full and 4-month original-index phase states included.
