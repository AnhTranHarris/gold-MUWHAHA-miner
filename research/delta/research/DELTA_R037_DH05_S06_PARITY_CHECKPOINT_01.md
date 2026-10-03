# DELTA R037 — DH05-S06 Exact Fixture Reconstruction — Parity QA Checkpoint 01

**Status:** IN_PROGRESS / NO PARITY CLAIM  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Current unit:** R037_DH05_S06_EXACT_FIXTURE_RECONSTRUCTION_AND_PARITY  
**Scope:** exact historical specialist reconstruction only; no R037-SORB replay  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Window:** Stage-A [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this checkpoint exists

A message-delivery/foreground timeout occurred while R037 was recovering the exact R032-C03 specialist streams. Durable state already proved:
- R037 SORB source QA PASS;
- exact non-specialist R032 backbone parity PASS;
- official R037 integrated replay NOT STARTED;
- the next required unit is exact DH05-S06 reconstruction.

This checkpoint prevents a retry from repeating the recovery audit or silently accepting an approximate specialist.

## Authoritative historical fixture

R032 preregistration states that the authoritative generator was a transient script named `r013_selective_handoff.py`. That script is not present in the current GitHub tree and was not found in the current Drive source inventory.

Frozen DH05-S06 vector:

```json
{
  "acceptance_disp_atr": 0.217738,
  "acceptance_tf": "S5",
  "boundary_source": "M5 swing",
  "max_failure_age_s": 59.699117,
  "max_probe_age_s": 23.47226,
  "probe_excursion_atr": 0.029179,
  "reclaim_buffer_atr": 0.145085,
  "reversal_disp_atr": 0.041213,
  "reversal_eff_min": 0.673017,
  "reversal_tf": "S1"
}
```

Frozen vector short hash: `086cfeff0e2b`.

Authoritative Stage-A P75 fixture:
- generator signals: **672**
- executed trades: **615**
- wins: **307**
- win rate: **49.918699%**
- gross profit: **+$63.19**
- gross loss: **-$164.27**
- net: **-$101.08**
- max balance DD: **$101.51**
- expectancy: **-$0.164358/trade**
- activity: **3.660496%**
- authoritative fixture SHA-256: `2deb601035d3e460f6de76ab8045b890ba7c5065b00a8815fceaf482916e2eae`

Historical R006 provenance:
- `r005_speedrun.py` SHA-256 `43adbc79bbe95188e3d9ccd452519da6a23a9e58bffa425dc177285cdf054b5a`
- `r005_observers.py` SHA-256 `c1e1b331d1acdff222cbe469d65abf326f89120cefc7de91ec771883506ddb71`
- `r005_specialists.py` SHA-256 `fe1ccb8112f5bf37c83e7ce9e9dd82f782397a7710029716a61c159e4005afe0`
- `secondary_vectors.json` SHA-256 `3687057223837d41a4391a3182d25e8188ce383a3e2496068ca4e15c07ca26fc`
- `dh05_results.jsonl` SHA-256 `38a99c46de7e7613a8732513d33b10ec457872d6e323503eedeb615e1c8234de`

Those original transient Python files are not currently recoverable from GitHub/Drive. Their hashes remain provenance, not executable substitutes.

## Clean-room parity findings completed in this unit

### 1. Permanent boundary consumption is rejected

Treating one confirmed M5 swing boundary as eligible for only one probe forever materially under-produces the historical DH05-S06 signal density.

### 2. Causal same-boundary re-eligibility is required

Allowing the same still-current M5 boundary to become eligible again only after price causally returns to the pre-break side reproduces the historical density region.

One frozen semantic interpretation produced exactly **672 signals** without changing any DH05-S06 numeric parameter. However its downstream ledger was **647 trades / 286 wins / -$140.00**, so signal-count equality alone is NOT parity.

A second exact-672 interpretation produced **650 trades / 284 wins / -$141.97**. It is also rejected.

A near-economic interpretation produced **670 signals / 645 trades / 310 wins / -$120.29**. It remains non-parity.

### 3. Full R9 S1 quality gating is rejected for standalone DH05 admission

Applying the full R9 S1 quality gate to the recovered ~670-signal population collapses the specialist to roughly 200–225 trades, far below the authoritative 615-trade fixture.

Therefore the historical DH05 generator did not simply inherit the full R9 S1 quality gate as its admission rule.

### 4. M5 ATR normalization is the surviving normalization hypothesis

Testing alternative causal ATR-reference clocks showed:
- S15 ATR generally over-produces signals/trades and misses the family fingerprint;
- M1 ATR severely over-produces;
- S5 ATR can approach isolated counts but gives poor economic/family parity;
- **M5 ATR is materially closest to the frozen DH05 family behavior.**

This is not yet a parity PASS, but non-M5 ATR normalization is rejected for the current reconstruction path.

### 5. Current confirmed-micro-pivot reversal implementation is structurally wrong

The original R006 DH05 family provides a cross-vector fingerprint. For the six frozen M5-swing vectors, authoritative trade counts are:
- A03: 306
- S05: 51
- S06: 615
- S09: 119
- S10: 206
- S16: 24

Under the current clean-room implementation that requires a separately confirmed local reversal pivot, S5-reversal vectors collapse to near-zero/tiny counts (representative results: A03 ~51, S05 ~0, S09 ~8, S10 ~6, S16 ~1).

This mismatch is too large to be a tie-breaking or threshold-rounding issue.

**QC conclusion:** the historical generator's reversal re-break/micro-pivot implementation was simpler/different than the present confirmed-pivot interpretation. Do not tune the frozen S06 numeric vector to compensate.

## Explicitly rejected reconstruction shortcuts

- permanent one-event-per-boundary consumption;
- full R9 S1 quality gate as DH05 admission;
- non-M5 ATR normalization for current parity work;
- current separately confirmed reversal-pivot implementation;
- treating exact 672 signal count alone as parity;
- retuning any frozen DH05-S06 numeric parameter to force fixture agreement.

## Next exact bounded substep

`R037_DH05_S06_PARITY_RECONSTRUCT_REVERSAL_REBREAK_SEMANTICS_USING_M5_SWING_SIX_VECTOR_FINGERPRINT`

Test only causal, white-paper-compatible reversal definitions while keeping all frozen vectors unchanged:

1. micro pivot = causal local extreme formed during probe/reclaim, frozen at reclaim;
2. pivot = reclaim/first-reentry completed-bar extreme rather than a future-confirmed swing;
3. reversal re-break = completed reversal-bar displacement + directional efficiency after reclaim, with the pivot check reduced to crossing the reclaim/preceding-bar extreme.

Use the six M5-swing vectors (A03/S05/S06/S09/S10/S16) as a fingerprint before accepting any S06-only match.

Advancement requires:
- exact or explainably deterministic S06 672-signal / 615-trade fixture reproduction;
- family-level count ordering/density materially consistent with the historical six-vector fingerprint;
- historical S06 307 wins / -$101.08 economics reproduced within deterministic implementation tolerance;
- no parameter retuning;
- no August;
- no R037 SORB integration until DH05 parity is PASS.

## Resume rule

On retry/readback:
1. read live `delta/CURRENT_STATE.json`;
2. read this checkpoint;
3. resume only the bounded reversal-rebreak semantics fingerprint unit above;
4. do not repeat the source-recovery audit, ATR sweep, R9-quality test, or permanent-boundary tests unless explicitly auditing this checkpoint.

R037 integrated replay remains blocked.