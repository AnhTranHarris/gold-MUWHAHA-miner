# DELTA New-Chat Bootstrap — Fresh R9-Based Research Lineage

**Created:** 2026-10-01  
**GitHub:** `AnhTranHarris/gold-MUWHAHA-miner` branch `delta`  
**Drive:** DELTA_RESEARCH  
**Status:** READY FOR NEW CHAT  
**BETA:** CLOSED / HISTORICAL ONLY  
**August 2026:** SEALED

## Owner decision

BETA is closed because the rebuilt lineage no longer retained enough of the owner's acceptable Entry+Hold edge and trade activity. This is not treated as a total research failure: BETA produced valuable causal, QA, documentation, reconstruction and failure-recovery procedures. Those procedures are carried into DELTA; BETA candidate economics are not.

## Active engineering baseline

DELTA starts from the preserved R9 MT5 implementation:
- `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` — source blob `7eecb5f1947017a01ce85b2520725de54749e523`
- `Experts/GoldMuwahahaMiner_R9_TickLogger.mq5` — source blob `5c7655cd3357f9126e8bffd97c34374dfb29f83e`

R9 itself is a reference baseline/evidence generator, not a claim that its REAL execution is profitable.

## Fast research corpus

Use `research/delta/reference/R9_EVIDENCE_REGISTRY.json` and `R9_REFERENCE_CORPUS_INDEX.json` before touching heavy files.

Canonical roles:
- **REAL:** execution/path/lifecycle benchmark.
- **SYNTH:** teacher/north-star only.
- **OVERFIT/ORACLE:** quarantined hypothesis/capacity source only.
- **Dukascopy Jan-Jul:** causal replay/robustness research; historically inspected.
- **August:** sealed blind holdout.

The Drive registry points to the validated REAL and SYNTH tick indexes, daily manifests, event indexes, paired monthly corpus, MT5 reports and overfit reference.

## Hard DELTA research rules

1. Every scientific unit is preregistered and gets a manifest before compute.
2. Every material helper/candidate generator/cache/model/replay/QA artifact is preserved or exactly regenerable.
3. Candidate/prediction surfaces are preserved before ownership/routing whenever they affect results.
4. RIGHT-edge/as-of timing is mandatory. No future outcome may enter inference.
5. Entry+Hold quality **and trade-count retention are co-primary**. No starving-the-system success.
6. Jan-Jul are nonblind historical research, never relabeled pristine OOS.
7. August stays sealed until a frozen candidate passes rebuild readiness + human QA and the owner explicitly authorizes opening it.
8. UI/tool/runtime failure resumes the same unit from the first incomplete durability step; never restart science from memory.
9. Null/failed results remain durable evidence.
10. No candidate MQL5 coding before owner approval and `mt5_translation_ready=true`.
11. Every MT5-worthy candidate must include Python→MQL5 parity fixtures, state machine, feature timing/order, execution, ownership, session/DST and risk contracts.

## Research objective

Rebuild a high-activity causal Entry+Hold architecture around the R9 evidence base without reproducing SYNTH lookahead or BETA's later trade-count collapse.

Research should use REAL/SYNTH/OVERFIT evidence to answer *where R9's apparent edge came from and why REAL lost it*, then reconstruct only causal mechanisms on ordered REAL/Dukascopy chronology.

Trade velocity is not a cosmetic secondary metric. Any candidate must report:
- opportunity count;
- selected trade count;
- retention versus declared reference;
- winning-trade count;
- entry quality;
- hold persistence/survival;
- net/PF/expectancy;
- gross loss and drawdown.

## Recorded next action: DELTA_001

Run **DELTA_001_R9_SOURCE_EVIDENCE_PARITY_PREFLIGHT**.

It must:
- verify both R9 MQL5 source identities and behavior-critical input defaults;
- verify REAL/SYNTH report availability and roles;
- verify REAL/SYNTH tick index, daily manifest, validation and paired-corpus availability;
- verify Dukascopy Jan-Jul canonical hashes;
- register OVERFIT/ORACLE quarantine;
- verify DELTA Drive + GitHub write/readback;
- freeze the initial data walls and research metric schema;
- produce a complete rebuild-ready DELTA manifest.

DELTA_001 performs no strategy optimization.

## After DELTA_001

The first scientific campaign should decompose R9 into:
- ENTRY/ACTION timing and directional selection;
- HOLD/PERSISTENCE survival;
- EXIT/HARVEST;
- execution friction/path-density transfer REAL↔SYNTH;
- opportunity/trade-count retention.

Use paired REAL/SYNTH evidence to localize the transfer failure, then test reconstructible mechanisms causally on original ordered quotes. Do not simply stack indicators.

## Recovery instruction for the next chat

If the UI times out:
1. inspect `delta/CURRENT_STATE.json`;
2. inspect the active DELTA unit manifest;
3. verify GitHub/Drive artifacts that already exist;
4. resume the same unit at its first missing durability step;
5. do not repeat verified work;
6. do not advance the cursor until readback/hashes pass.

This document is the bootstrap pointer, not a substitute for the repository state.
