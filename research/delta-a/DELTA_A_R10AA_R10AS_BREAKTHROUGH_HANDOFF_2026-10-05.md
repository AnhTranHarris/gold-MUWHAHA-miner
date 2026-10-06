# DELTA-A — R10AA through R10AS Breakthrough Handoff — 2026-10-05

**Status:** HANDOFF READY / EXPERIMENTAL / NOT MT5 AUTHORIZED / AUGUST SEALED

This file is the canonical restart point for the breakthrough chain discovered after R10Z30. It exists to prevent a Gamma-style loss of state when a ChatGPT conversation reaches its maximum length.

## 1. New-chat bootstrap

Read, in order:

1. Master protocol Google Doc: `1ycB5bQ3P24w7BZz54RwgJbc5CX5aRcqgr0KiI0Iidkw`.
2. GitHub branch `delta-A`.
3. `research/delta-a/DELTA_A_GRID_HF_STATE.json`.
4. `research/delta-a/DELTA_A_SA100_HELPER_STATUS_2026-10-05.json`.
5. This handoff.
6. Native Google Doc master handoff: https://docs.google.com/document/d/1EHXx6sVU3VnbcGSkkISM4M407JJdSJncOVKrKAARQXs/edit?usp=drivesdk\n7. Drive handoff folder: https://drive.google.com/drive/folders/1_j8CaAwOvcD5S6OQkRf5bn-oXTgnayBB
8. Drive archive: `DELTA_A_R10AA_R10AS_HANDOFF_2026-10-05.zip`, SHA-256 `181667cda8e63d8f86cffdc17809761838317c218bb8c3d111aec7eebec153f1`.
9. Drive `MANIFEST.csv` contains SHA-256 for all **81** carried-forward helper/artifact files.

Do not reconstruct this stack from chat prose alone.

## 2. Research objective

Starting account remains **$100**, fixed physical lot **0.01**, with no real architecture handoff before **$1,000**.

The research objective is no longer survival alone. Preserve small-account survival while converging toward or beating **R9 SYNTH January** simultaneously on:

- physical trade count / velocity;
- net profit;
- gross loss;
- true floating-equity drawdown.

Human soft target for new specialists: preferably **>50% causal success**, provided they improve economic outcomes. Hit rate alone is not a promotion metric.

August 2026 remains SEALED.

## 3. Current promoted supermodel parent

The current research parent is:

`R10AA -> R10AB -> R10AG SEQ45_60 -> R10AH`

This is the strongest combined parent because the specialists attack different residual failure states while preserving the $100 seed floor.

| Stack | Jan net | Physical GL | Episode GL | Tick DD | Min tick equity | Executed episode success |
|---|---:|---:|---:|---:|---:|---:|
| R10AB | +$4,470.41 | -$11,566.18 | -$9,300.01 | ~$203.28 | $87.17 | 60.04% |
| + R10AG SEQ45_60 | +$4,700.42 | -$10,482.89 | -$8,244.58 | ~$203.28 | **$99.51** | — |
| + R10AH | **+$4,824.61** | **-$10,383.63** | **-$8,125.21** | ~$203.28 | **$99.51** | **61.15%** |
| + R10AI ungated | +$4,969.73 | -$10,321.74 | -$7,975.16 | ~$203.28 | $81.37 | 61.47% |

Compared with R10AB alone, AG+AH adds about **+$354 net**, removes about **$1,183 physical gross loss**, removes about **$1,175 episode gross loss**, and raises minimum tick equity from **$87.17 to $99.51**.

## 4. Breakthrough mechanics

### R10AA — residual CONT/180 profit-stall close

Status: `COMPLETE_EXACT_MINOR_BREAKTHROUGH`.

Rule at +30 seconds on residual HOLD/CONT/180:
- current primary PnL > +$0.06;
- MFE <= +$2.07;
- close current basket/cancel future legs;
- keep shadow slot frozen to original episode end.

Selected 84 episodes. Specialist success ~95.24%. Result: +$4,231.60 net, physical GL -$11,825.38.

### R10AB — REVERT/900 loss conversion

Status: `COMPLETE_EXACT_BREAKTHROUGH`.

At +90 seconds on residual HOLD/REVERT/900:
- primary PnL > +$0.24;
- path efficiency > 0.03;
- MAE <= -$0.48;
- close current basket/cancel future legs;
- transfer ownership to one opposite 0.01 trade for 30 seconds;
- keep shadow slot frozen to original end.

Selected 148 episodes; specialist success ~92.57%; 56 converted losses.
Result: +$4,470.41 net, physical GL -$11,566.18, episode GL -$9,300.01, executed episode success ~60.04%.

### R10AG — sequential REVERT/900 failure-owner supermodel

Status: `COMPLETE_EXACT_SEQUENTIAL_COMPARE`.

Promoted variant: **SEQ45_60**.

This is preferred over a single-stage REVERT/900 rule because it gives the trade two causal opportunities to reveal failed ownership.

Selected 372 episodes; specialist success ~56.72%; **118 losses converted**.

Result:
- +$4,700.42 net;
- physical GL -$10,482.89;
- episode GL -$8,244.58;
- min balance $100;
- min tick equity **$99.51**;
- tick DD ~$203.28.

R10AF remains useful provenance, but R10AG is the preferred sequential parent.

### R10AH — residual REVERT/600 failure owner

Status: `COMPLETE_EXACT_STACK_TEST`.

At +30 seconds on residual HOLD/REVERT/600:
- observed tick intensity > ~4.2 ticks/sec;
- terminate failed basket/cancel future legs;
- give opposite side one 0.01 / 180-second ownership opportunity;
- shadow slot remains frozen.

Selected 55 episodes; specialist success **63.64%**; 25 converted losses.

On top of AG:
- +$4,824.61 net;
- physical GL -$10,383.63;
- episode GL -$8,125.21;
- min tick equity **$99.51**;
- executed success **61.15%**.

This is the current promoted research parent.

### R10AI — long-horizon failover

Status: `COMPLETE_EXACT_STACK_TEST__CAPITAL_GATE_REQUIRED`.

Rules:
- CONT/1200: at +60s, turns > 200 -> terminate basket and reverse one 0.01 for 180s.
- REVERT/1200: at +450s, MAE > -$3.655 -> terminate basket and reverse one 0.01 for 180s.

Selected 83 episodes; specialist success ~65.06%.

Ungated result:
- +$4,969.73 net;
- physical GL -$10,321.74;
- episode GL -$7,975.16;
- executed success 61.47%.

But minimum tick equity falls to **$81.37**. Therefore **do not enable R10AI unconditionally from $100**.

Next experiment: physical activation at **$150 / $175 / $200 / $250 / $300**, while R10AI remains virtual/prewarmed below the gate.

## 5. Velocity specialists

These are positive-expectancy opportunity desks. They should not be attached physically at $100 until the loss/DD core is stable.

### R10AP — expansion meta-label desk

Chosen desk A:
- selected opportunities: 1,043;
- success: **60.88%**;
- net: **+$445.02**;
- GL: -$458.31;
- discovery success 62.57%;
- holdout success 57.77%.

Candidate for capital-gated physical activation after core stabilization.

### R10AR — second-wave meta-label desk

- selected opportunities: 1,704;
- success: **57.63%**;
- net: **+$360.13**;
- GL: -$699.42;
- discovery success 60.47%;
- holdout success 52.22%.

Second velocity desk; test only after AP or in a separately budgeted capital band.

## 6. Important non-promotions

### R10AC
R10AC raises net to roughly +$4,583 but worsens physical GL to about -$11,958 and worsens balance DD. Do not stack it for the current loss-efficiency objective.

### R10AF
R10AF contains useful REVERT/900 early-direction mechanics; its V15_R45 variant reaches about +$4,786 / -$10,838 physical GL. R10AG is preferred because it forms the cleaner sequential failure-owner parent and gives better gross-loss containment in the promoted chain.

### Historical Transparent S1 router
Recovered concept remains useful only as generic causal features. Literal CONTINUE/FADE transfer to Delta-A was falsified. Do not resurrect the old headline metrics as proof.

## 7. Current unresolved bottleneck

Maximum tick DD remains around **$203** across AB -> AG -> AH.

Do **not** globally tighten the system to cure this.

Required next DD unit:
- identify the exact episode/path causing the ~$203 drawdown under **AG+AH**;
- reconstruct only information causally available before/during that episode;
- build one targeted ownership/recovery specialist;
- require improvement in DD without materially worsening net, GL, velocity or the ~$100 seed floor.

## 8. Immediate continuation units

Run only these three first:

1. **R10AI capital-gate speedrun** at $150/$175/$200/$250/$300.
   - Goal: capture most of AI's +$145 incremental net / GL improvement while retaining AG+AH's ~$99.51 minimum-equity behavior.
2. **AG+AH exact DD forensic specialist** for the ~$203 maximum tick-DD path.
3. **R10AP capital-gated velocity desk**, after #1 and #2 stabilize.
   - R10AR is the next velocity candidate only after AP.

Continue using fast falsification:
- cheap causal screen first;
- expensive exact tick/capital replay only for candidates that improve the frontier;
- no month-name fitting;
- no broad abstention that simply starves velocity.

## 9. Complete artifact custody

The Drive archive contains **81 files** covering:
- parent R10Y/R10Z30;
- R10AA through R10AS;
- every helper Python source present in the runtime;
- every exact JSON result;
- every CSV candidate/event/episode/leg artifact;
- manifest with sizes and SHA-256 hashes.

Drive folder:
https://drive.google.com/drive/folders/1_j8CaAwOvcD5S6OQkRf5bn-oXTgnayBB

ZIP:
https://drive.google.com/file/d/1esLKLdsc3VempopiUz1hBqkgxbfyAgCw/view

README:
https://drive.google.com/file/d/1God58y8HGbeHEjom_0S1EripXw5yn95b/view

Manifest:
https://drive.google.com/file/d/1dexMGtGg_KFEF1kxTeKa6wbjGE__iyUc/view

ZIP SHA-256:
`181667cda8e63d8f86cffdc17809761838317c218bb8c3d111aec7eebec153f1`

If GitHub and Drive ever disagree about helper bytes, use the manifest hashes and frozen snapshot branch to establish what this handoff contained.

## 10. New-chat instruction

Use this prompt:

> Bootstrap DELTA-A from GitHub branch delta-A and the R10AA-R10AS breakthrough Drive handoff. Verify helper status and archive manifest. Use R10AA -> R10AB -> R10AG SEQ45_60 -> R10AH as the current research parent. First test capital-gated R10AI, then forensic the ~$203 AG+AH tick-DD path, then test capital-gated R10AP. Preserve $100 fixed 0.01 survivability, no handoff before $1,000, August sealed, and no MQL5 build.
