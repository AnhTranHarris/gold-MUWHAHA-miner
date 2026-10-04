# DELTA R037 — Volatility Compression/Expansion Stage-A Screen — Checkpoint 17A

**Status:** COMPLETE / NO STRONG SURVIVOR / RESERVE CLUE ONLY
**Unit:** R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST
**Family:** R037-VCE-v1
**Parent:** R037_PLSR_C01_MONTHLY_VALIDATION_CHECKPOINT_16C
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A
**August:** SEALED
**MQL5:** NOT AUTHORIZED

## Frozen basket

Four source-grounded variants were committed before official replay:
- C01: M5 15-bar compression box, box height < 2.5×ATR14, first later completed M5 close outside, 45-bar expiry.
- C02: C01 plus EMA150 directional alignment.
- C03: prior completed-bar BB20/2.0 inside KC EMA20 ±1.5×ATR20, followed by release and completed close beyond KC.
- C04: C03 plus 12-bar close momentum agreement.

All variants used the frozen parent-priority scheduler, <=25-point spread gate, 0.01 lot, $0.30 stop, +$0.10 trail arm, $0.03 trail, and 30-second max hold. No threshold search or post-result tuning occurred.

## Official compute

Final clean-room producer:
- path: research/delta/experiments/delta_r037_vce_stage_a.py
- commit: 057dbd9200feb40c2fae289fba675080c55fccd3
- blob: 1f9cbed1480fe35916b3f26f733f65f87979a8be
- SHA-256: d52630b39bf0bd048e57b9e148773c8f67767dcc7ba8e9e94e9b67112432136c

Canonical January Stage-A: 4,205,709 ticks.
Bounded runner exit 0 in 20.117 seconds.
Official raw result SHA-256: 045b537be38674b3e834bfd42d0207eb24891a9f9db3c79afd625bd7448c518e.

The prior pre-patch diagnostic produced the same numeric fingerprint but is not used as the official producer because the clean-room gate rejected a reserved lineage token in a local EMA coefficient variable name. The source was patched without changing the formula, recommitted, gate-checked, and officially rerun.

## Results

Parent control: 14,034 trades / 6,349 official wins / -$2,944.94 net.

- C01 ORION box: +36 trades / +20 official wins / -$5.10 net delta; FAIL.
- C02 ORION + EMA150: +27 trades / +16 official wins / -$3.14; FAIL.
- C03 BB/KC release: +27 trades / +20 official wins / -$0.13; ordinary screen PASS, strong PASS false; direct VCE net +$0.71.
- C04 BB/KC + momentum12: identical to C03; +27 / +20 / -$0.13; ordinary screen PASS, strong PASS false; direct VCE net +$0.71. Momentum12 rejected zero events and therefore supplied no incremental information in Stage-A.

## Decision

No preregistered configuration achieved the required strong Stage-A screen. C03/C04 are preserved as a near-threshold forensic clue, but are not promoted or retuned.

**Next:** R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST.

The next family should be structurally independent of session opening ranges, previous-day sweep/reclaim, and this volatility-compression family.
