# DB001A — 100K Canonical January Real-Tick Smoke Report

Status: **MECHANICS DIAGNOSTIC ONLY — NOT PROFITABILITY EVIDENCE**

## Source

Canonical January Dukascopy XAUUSD quote source:

- SHA256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- first 100,000 ordered quotes only
- observed range: 2026-01-01 23:00:00.596 UTC through 2026-01-02 07:37:32.214 UTC
- smoke loader used `ask_raw / 1000` and `bid_raw / 1000`; formal producer must preserve/verify canonical source scaling before economic promotion

August was not opened.

## Exact Kernel QA Before Smoke

After the event-driven reclaim correction:

- kernel Git blob SHA1: `479a60a01b996ab0e2850bb3871d325a857e021c`
- QA Git blob SHA1: `abb04218ef0c8e51ed0865fc310dd93c4917cd37`
- exact local bytes match committed Git blob IDs
- unit suite: **9/9 PASS**

New regression guard proves that RECLAIM appears on the L0 transition and does not persist merely because L0 and higher scales continue to disagree afterward.

## 100K Smoke Metrics

Runtime on the original first-pass exact-byte kernel was approximately:

- 100,000 ticks
- ~5.85 seconds
- ~17,100 ticks/sec in pure Python diagnostic execution

Observed quote friction in the smoke window:

- minimum spread: ~$0.197
- median spread: ~$0.830
- 95th percentile spread: ~$1.160
- maximum spread: ~$5.580

Adaptive Q before session/news overlays:

- median base Q: ~$1.1205
- 95th percentile base Q: ~$1.566
- maximum base Q: ~$11.40

Context Q:

- median: ~$1.1205
- 95th percentile: ~$1.6585
- maximum: ~$11.40

Intrinsic directional-change events:

- L0 / 1Q: 133
- L1 / 2Q: 31
- L2 / 4Q: 1
- L3 / 8Q: 0

The first 100k quotes are dominated by ASIA and the London-open transition, so this is not representative of the full day or Jan-Jul.

## State Classifier Defect Found and Corrected

### Initial classifier

The first implementation treated any persistent L0-vs-higher-scale disagreement as FAILED_ESCAPE_RECLAIM.

Initial 100k state counts:

- ROTATION: 29,554
- CHURN_SHOCK: 8,829
- FAILED_ESCAPE_RECLAIM: 48,538
- TRANSIT: 13,064
- ESCAPE: 15

This was rejected as semantically wrong. A reclaim is an event transition, not a permanent disagreement regime.

### Corrected event-driven classifier

RECLAIM now requires:

- a new L0 directional-change event;
- a genuine L0 sign flip;
- nonzero higher-scale prior context.

Corrected state counts on the same 100k quotes:

- ROTATION: 78,025
- CHURN_SHOCK: 8,829
- FAILED_ESCAPE_RECLAIM: 76
- TRANSIT: 13,064
- ESCAPE: 6

Directional-change event counts did not change:

- L0: 133
- L1: 31
- L2: 1
- L3: 0

Therefore the correction changed classification semantics rather than manufacturing/deleting underlying grid events.

## Important Diagnostic Findings

1. **Q is already economically anchored.** In this early Asian-heavy window median Q is modestly above median quoted spread, rather than collapsing into microscopic line-cross noise.

2. **The lattice is not firing on every tick.** 133 L0 events across ~8.6 hours provides a selective event stream while the underlying kernel remains tick-reactive.

3. **The reclaim bug demonstrates why Layer 1 must be frozen before Volume Profile.** A higher layer would otherwise learn from a mislabeled lower-layer regime and create permanent architectural confusion.

4. **Path-noise ratios are highly skewed in rotation.** This requires separate analysis before path-noise may become a strong shock or direction feature. It must not be treated as a simple Gaussian-like variable.

5. **No medium/high historical calendar cache was supplied to this smoke run.** Every scheduled event phase remained NORMAL. Therefore this run validates only the machinery, session labeling and observable quote-shock logic; it does NOT validate news/event adaptation economics.

## Next Scientific Gate

Before tuning for profit:

- run exact Q/state traces over broader January session coverage;
- produce a frozen historical MEDIUM/HIGH event cache and hash it;
- verify event/session state chronology against UTC/server-time mapping;
- compare event density and state attribution by session/event phase;
- only then attach an executable scalp lifecycle and evaluate gross loss / drawdown / opportunity retention.

No Volume Profile or RSI layer should be added yet.
