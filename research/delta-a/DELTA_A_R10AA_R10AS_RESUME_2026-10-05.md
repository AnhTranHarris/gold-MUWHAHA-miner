# DELTA-A R10AA-R10AS Resume — January Continuation — 2026-10-05

**Status:** JANUARY CONTINUATION COMPLETE / EXPERIMENTAL / NOT MT5 AUTHORIZED / AUGUST SEALED

## Custody/bootstrap verification

- Master protocol read first.
- Drive handoff master read from `DELTA-A R10AA-R10AS Breakthrough Handoff`.
- ZIP SHA-256 verified exactly: `181667cda8e63d8f86cffdc17809761838317c218bb8c3d111aec7eebec153f1`.
- Archive carried files: **81**; manifest verification **81/81 size+SHA256 matched**, zero missing, zero mismatched, zero extra carried files.
- Frozen GitHub authority: `ce19815fda0f4d1219f55363df22bc857fb344f4`.
- `delta-A-r10aa-r10as-breakthrough-handoff-20261005` and live `delta-A` were both identical to that commit at bootstrap.
- Incomplete `sa100_build_core_stop_variants.py` remains `INCOMPLETE_ANALYSIS_DO_NOT_RESUME`; it was not resumed.

## Starting parent

`R10AA -> R10AB -> R10AG SEQ45_60 -> R10AH`

Parent January metrics: +$4,824.6145 net; physical GL -$10,383.6315; episode GL -$8,125.2110; min tick equity $99.51; max tick DD $203.28.

## Unit 1 — R10AI capital gate

Exact gates tested: $150 / $175 / $200 / $250 / $300, with R10AI virtually prewarmed below gate and physical ownership allowed only at/above parent shadow balance.

**Selected: $200.**

- Net: **+$5,004.5645** (+$179.95 vs AG+AH parent).
- Physical GL: **-$10,304.5615** (better by $79.07).
- Episode GL: **-$7,959.3710** (better by $165.84).
- Min tick equity: **$99.51**.
- Max tick DD: **$203.28**.
- 79 R10AI episodes physically activated.

## Unit 2 — exact $203 DD forensic + targeted ownership specialist

Exact AG+AH worst drawdown path:

- Peak: **2026-01-29 15:30:47.301 UTC**.
- Trough: **2026-01-29 15:39:08.939 UTC**.
- Duration: **501.638 s**.
- Parent tick DD: **$203.28**.

A narrow causal rule was tested:

> Preserve the R10Z +3s basket close. Deny only the subsequent 30s reverse ownership transfer when the portfolio already owns >=1 position in the proposed reverse direction and live equity DD from peak is >= threshold.

Threshold neighborhood **$75 / $90 / $100** all improved the frontier. Carry-forward research setting: **$90**.

On top of R10AI gate $200:

- Net: **+$5,039.8345**.
- Physical GL: **-$10,234.5515**.
- Episode GL: **-$7,896.0510**.
- Max tick DD: **$181.04**, a **10.94% reduction**.
- Min tick equity: **$99.51**.
- 11 R10Z reverse transfers blocked.
- Critical event 26203 blocked.

Provisionally named **R10AT dynamic ownership DD90**.

## Unit 3 — capital-gated velocity integration

### R10AP Desk A

Policy setting carried forward: **R10AP gate $300**.

- Physical AP events: **1,041**.
- Incremental net: **+$446.3190**.
- Incremental AP GL: **-$456.8140**.
- AP success: **60.90%**.
- Combined net: **+$5,486.1535**.
- Combined max tick DD: **$181.3015**.
- Min tick equity: **$99.51**.
- Max positions: 9.

### R10AR second-wave desk

At **R10AR gate $1,000**:

- Physical AR events: **1,587**.
- Incremental net: **+$351.8480**.
- Incremental AR GL: **-$653.9300**.
- AR success: **57.53%**.
- Final policy-stack net: **+$5,838.0015**.
- Physical GL: **-$11,345.2955**.
- PF: **1.5146**.
- Physical legs: **7,553**.
- Max tick DD: **$169.01**.
- Min tick equity: **$99.51**.
- Max positions: 9.

R10AR remains conditional on cross-month validation rather than automatically promoted as a universal desk.

## Hard constraints preserved

- Starting balance $100.
- Fixed physical lot 0.01.
- No architecture handoff before $1,000.
- August not accessed.
- No MQL5 build or production authorization.
- No incomplete helper resumed.
- Completed R10AA-R10AS artifacts were consumed from Drive/GitHub bytes rather than reconstructed from chat prose.

## Next scientific gate

Cross-month causal validation should start from:

`R10AA -> R10AB -> R10AG SEQ45_60 -> R10AH -> R10AI(G200) -> R10AT(DD90) -> R10AP(G300)`

R10AR remains `G1000_CONDITIONAL` until its incremental benefit survives the next valid non-August validation surface. August remains sealed.
