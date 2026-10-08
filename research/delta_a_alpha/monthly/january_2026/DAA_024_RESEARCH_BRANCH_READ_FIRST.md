# 024 — January Funded-Execution Tick Reconstruction (Fidelity-Gated)

**Complete: eight quote-first execution scenarios for the disclosed reconstructed strategy.**
**Not complete: exact original 131E full V1 funded-execution parity.**
Owner May 137 pause remains; August sealed and September reserved as future blind holdouts.

## Canonical exact-byte reproducible archive

ChatGPT Project Library: `/xauusd-trading-bot/delta-A-alpha/monthly/january_2026/adaptive-funded-reconstruction-024/`

- `DAA_JANUARY_RECONSTRUCTED_FUNDED_REPLAY_024.tar.gz` SHA256 `40c42786ee0c2cb25e0d080b71b201bc5d9adfd8b59e97eb84985a87d4314a98`, 54 source/result/checksum/log files, **does not include the raw tick gzip**
- `DAA_JANUARY_FUNDED_TICK_RECONSTRUCTION_024.md`, mandatory scientific caveat and methodology
- `jan024_reconstructed_full_portfolio.py` exact Python source, `build_checkpoint_024.py`, `SHA256SUMS_024.txt`, eight complete JSON/CSV tick-exit trade tapes and month/day/week results

Source raw input, separately mounted: `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz` SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. 9,135,062 actual chronologically ordered Bid/Ask quotes. Model lot 0.01; $0.02/ticket research commission, original recorded spread incorporated, assumption 0.01 lot=1 XAU ounce P/L.

## Acceptance-grade result classification
- **PASS:** reproducible raw executable quotes at every new entry / tick-exit, exact quote/P&L reconstruction (0 max error), one physical new position per market tick, strict shared cap (16,64,128,256), completed-only MTF and M5 range awareness, funded closed child events, UTC day/week/month scorecards, eight inspected atomic JSONs.
- **NOT PASS / NOT PROVEN:** perfect original Gamma January 131E portfolio parity. The new Watchdog feeder uses first-seen UTC17 parent campaigns rather than exact legacy causal 049→051→075 parent funding and therefore produces tens, not thousands, of renewed children. Other missing exact layer: 131D supplemental coverage V3 / cold-start and original funded conditional recovery, original cap permissions. January starts Jan1 23:00 UTC with no December historical bootstrap; five-minute arbitrary-start readiness unproven. No broker-specific spread/commission/swap/slippage/margin/stopout or $1K-to-$100 tier qualification.
- **NOT PROMOTED:** experimental April-like quote-friction/competed M5 tail renewal gate; its incremental improvement about **+$12.41** while cutting 10 funded tickets is too small to show stable added alpha.
- **NO CHANGE:** production EA, permanent L0→L8 V1 architecture, frozen 131E January achievements, May scientific cursor, August seal.

## January cap sensitivity — raw Dukascopy reconstructed strategy only

| Cap | Model | Net | Trades | Gross loss | PF | Win | Equity DD |
|---:|---|---:|---:|---:|---:|---:|---:|
|16|Control|+$3,848.77|1,995|-$2,055.99|2.87|63.9%|$452.56|
|16|Aware|+$3,861.19|1,985|-$2,036.94|2.90|63.9%|$452.56|
|64|Control|+$12,496.98|5,240|-$6,098.86|3.05|66.2%|$1,761.11|
|64|Aware|+$12,509.40|5,230|-$6,079.81|3.06|66.2%|$1,761.11|
|128|Control|+$20,469.05|7,213|-$7,883.05|3.60|69.1%|$3,246.53|
|128|Aware|+$20,481.46|7,203|-$7,864.00|3.60|69.1%|$3,246.53|
|256|Control|+$34,944.45|9,914|-$10,410.51|4.36|72.1%|$5,574.91|
|256|Aware|+$34,956.86|9,904|-$10,391.46|4.36|72.1%|$5,574.91|

**The original January 131E +$194,425.92/80,929 ticket/PF54 result is separate, normalized spread and exceptionally high 640 simultaneous positions with ~$57K equity DD. Never conflate.**

## Resume exact economic parity, no substitutions

Recover the January Gamma original helper dependency chain using immutable GitHub source commits before modifying entries:
`019 → 024 → 049 → 051 → 075 → 084 → 119 → 131A/B → 131D → 131E`.
Then run identical full-system actual raw Bid/Ask per-tick economic replay with funded exits and appropriate global cap/portfolio attribution. Only after a source-parity control is available, independently qualify adaptive knobs and evaluate daily/weekly/monthly across January–July, and 100k→1k→500→300→100 equity/margin. Any implementation gap needs named numerical diagnostics; no replacement by broad indicator signals.

**GitHub parity evidence:** `research/delta_a_alpha/helpers/jan024_reconstructed_full_portfolio.py`, `research/delta_a_alpha/qa/build_checkpoint_024.py`, `research/delta_a_alpha/monthly/january_2026/DAA_JANUARY_FUNDED_TICK_RECONSTRUCTION_024.md`.
