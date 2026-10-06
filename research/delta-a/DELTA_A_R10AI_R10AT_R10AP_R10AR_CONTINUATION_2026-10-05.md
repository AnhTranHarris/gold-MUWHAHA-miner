# DELTA-A — R10AI / R10AT / R10AP / R10AR Continuation — 2026-10-05

**Status:** JANUARY CONTINUATION COMPLETE / EXPERIMENTAL / NOT MT5 AUTHORIZED / AUGUST SEALED

## Bootstrap authority verified

- Frozen parent commit: `ce19815fda0f4d1219f55363df22bc857fb344f4`.
- Frozen snapshot branch: `delta-A-r10aa-r10as-breakthrough-handoff-20261005`.
- At bootstrap, snapshot branch and live `delta-A` were both identical to `ce19815...`.
- The older `9a9d162...` recorded in the native handoff Doc is three commits behind `ce19815...`; it is provenance, not the current frozen head.
- Drive handoff ZIP SHA-256 verified: `181667cda8e63d8f86cffdc17809761838317c218bb8c3d111aec7eebec153f1`.
- Carried archive files verified: **81/81** by size and SHA-256; zero missing, mismatched, or extra carried artifacts.
- Incomplete helper `sa100_build_core_stop_variants.py` remains `INCOMPLETE_ANALYSIS_DO_NOT_RESUME`; it was not resumed.
- August was not accessed. No MQL5 build was created.

Exact continuation bundle:
- Drive: https://drive.google.com/file/d/1OwL8YxIV1SEuohuZ2D9RSfkYkBwc6wd9/view?usp=drivesdk
- SHA-256: `50b4c115a246f246b9716cb16451b42769a7acc05f1b59a0fb395f6c5b9fafa9`
- Contents: 16 files (new helper code, exact result JSONs, forensic output, and final ledgers).

## Starting research parent

`R10AA -> R10AB -> R10AG SEQ45_60 -> R10AH`

January parent:
- net **+$4,824.6145**
- physical GL **-$10,383.6315**
- episode GL **-$8,125.2110**
- min tick equity **$99.51**
- max tick DD **$203.28**

## 1. R10AI capital gate

Exact gates tested: **$150 / $175 / $200 / $250 / $300**. R10AI remains virtually prewarmed below the gate; physical ownership activates only when parent `shadow_balance` has reached the gate.

**Selected gate: $200.**
- 79 R10AI physical episodes
- net **+$5,004.5645** = **+$179.95** versus AG+AH
- physical GL **-$10,304.5615** = **$79.07 less loss**
- episode GL **-$7,959.3710**
- min tick equity **$99.51**
- tick DD **$203.28**
- executed episode success **61.53%**

The gate beats ungated R10AI's +$4,969.7345 because it excludes early harmful failover while retaining later positive ownership.

## 2. Exact $203 DD forensic and targeted ownership specialist

Exact AG+AH worst path:
- peak: **2026-01-29 15:30:47.301 UTC**
- trough: **2026-01-29 15:39:08.939 UTC**
- duration: **501.638 s**
- drawdown: **$203.28**

Critical local contributor: event **26203**. R10Z's +3s close was followed by a 30s reverse-ownership leg of about **-$37.90**, giving about **-$39.21** episode P/L. At the reverse trigger, the proposed short direction was already owned and live portfolio DD was about **$101.04**.

### R10AT — dynamic ownership DD specialist

Do not globally tighten the portfolio. Preserve the R10Z +3s basket close; deny only the subsequent 30s reverse ownership transfer when:

1. the portfolio already owns >=1 position in the proposed reverse direction; and
2. live equity drawdown from peak is >= threshold.

The causal threshold neighborhood **$75 / $90 / $100** all improved the frontier. Carry forward **DD90** because it sits inside the plateau rather than immediately fitting the ~101 critical value.

On top of R10AI gate $200:
- net **+$5,039.8345**
- physical GL **-$10,234.5515**
- episode GL **-$7,896.0510**
- only **11** R10Z reverse transfers blocked
- max tick DD **$181.04**, **10.94% lower**
- min tick equity **$99.51**
- critical event 26203 blocked

## 3. Capital-gated R10AP

R10AP Desk A was integrated from the completed archived 1,043 selected opportunities. One physical 0.01 position is used per selected event; the desk remains virtually prewarmed below the capital gate.

$150/$175/$200/$250/$300 converge because 1,041 of 1,043 opportunities occur after the stabilized core is already above $300.

Carry forward **R10AP gate $300**:
- 1,041 physical AP events
- incremental net **+$446.3190**
- AP success **60.90%**
- incremental AP GL **-$456.8140**
- combined net **+$5,486.1535**
- max tick DD **$181.3015**, only +$0.2615 versus stabilized core
- min tick equity **$99.51**
- max positions 9

AP therefore survives exact incremental physical integration.

## 4. Conditional R10AR

Because R10AP survived, R10AR was tested at **$300 / $500 / $750 / $1,000**.

All tested gates stayed positive and reduced combined tick DD to about **$169.01**.

Pure January net optimum:
- gate **$500**
- incremental R10AR net **+$362.1155**
- combined net **+$5,848.2690**

Project-policy activation candidate:
- gate **$1,000** to respect the no-architecture-handoff-before-$1,000 rule
- 1,587 physical R10AR events
- incremental net **+$351.8480**
- incremental GL **-$653.9300**
- success **57.53%**
- final policy-stack net **+$5,838.0015**
- physical GL **-$11,345.2955**
- PF **1.5146**
- physical legs **7,553**
- max tick DD **$169.01**
- min tick equity **$99.51**
- max positions 9

R10AR remains **conditional** until incremental performance survives a valid non-August cross-month validation surface.

## Hard constraints preserved

- $100 seed.
- Fixed physical lot 0.01.
- No real architecture handoff before $1,000.
- August sealed.
- No MQL5 build.
- No incomplete helper resumed.
- Completed R10AA-R10AS helpers/results consumed from durable Drive/GitHub artifacts rather than reconstructed from chat prose.

## Current January continuation

Core carried forward for validation:

`R10AA -> R10AB -> R10AG SEQ45_60 -> R10AH -> R10AI(G200) -> R10AT(DD90) -> R10AP(G300)`

Conditional desk:

`R10AR(G1000_CONDITIONAL)`

Next scientific gate: cross-month causal validation of the stabilized core/velocity integration on valid non-August data. August remains sealed.
