# F401-R150 DESIGN AUDIT — Oracle-Residual Causal Jury / Teacher-Fade Foresight

**Date:** 2026-10-30 America/Chicago  
**Status:** RESEARCH DESIGN / AUDIT ONLY — UNAPPROVED  
**Current checklist function:** M-DK-01 OPEN  
**Active decision parent:** F401-R148B  
**R149 status:** trained telemetry-only challenger; override remains disabled  
**G01–G09 remain OPEN. No /02 promotion, no PRIMARY write, no MT5 live order.**

## 1. Audit conclusion

The next breakthrough should **not** be another universal BAD classifier or another period sweep of ATR/RSI/Bollinger/Fibonacci. R149 demonstrated that the new technical/Bayesian features can transfer teacher ordering, but the student still derives most of its fitted teacher signal from the existing parent-score channels. The new student therefore remains too dependent on a compressed representation of what R148B already knows.

The proposed successor is **R150 = ORACLE-RESIDUAL CAUSAL JURY + TEACHER-FADE AUTONOMY**. The teacher remains an offline microscope and grader, but is deliberately prevented from becoming the student's live information source. The new architecture learns only what the hindsight teacher knows **beyond** the parent, while simultaneously learning independent physical/microstructure objectives that do not require the teacher at all.

## 2. Source-exact findings that drive the design

### 2.1 The current hunter is the largest correct-loss consumer

| Four-month environment | Total correct lost | Parent/R24-side correct lost | Residual-hunter correct lost | Hunter bad veto | Hunter bad/right |
|---|---:|---:|---:|---:|---:|
| Coinexx | 9,970 | 4,902 | **5,068** | 59,375 | **11.72:1** |
| Dukascopy | 9,930 | 2,209 | **7,721** | 96,638 | **12.52:1** |

The existing residual hunter is consuming the majority of Dukascopy's correct-loss capital and about half of Coinexx's. This makes **correct-loss recovery / hunter replacement** higher priority than simply increasing veto aggressiveness.

### 2.2 The teacher residual is a treasure map, not a deployable rule

Outside the current R148B forward veto mask, the fitted historical FILTER08 teacher identifies:

| Environment | Opposite | Neutral | Total bad residual | Correct residual |
|---|---:|---:|---:|---:|
| Coinexx | **102,096** | **35,810** | **137,906** | **19** |
| Dukascopy | **73,008** | **47,403** | **120,411** | **39** |

This is hindsight and cannot be used live. It is nevertheless highly informative scientifically: the teacher sees selective structure among events that the causal system currently releases.

Coinexx needs 162,509 additional bad vetoes to reach 90% of all four-month bad events; the teacher residual contains 137,906 of them, or about **84.9% of the remaining gap**. Dukascopy needs 113,532; the teacher residual contains 120,411, which is **6,879 more than the entire 90% gap**. The causal challenge is therefore reconstruction, not lack of a historical signal to learn from.

### 2.3 Late-session residual is unusually persistent

During **21:00–23:59 UTC**, the teacher identifies an additional **17,940 bad / 2 correct** on Coinexx and **20,092 / 5** on Dukascopy outside R148B. The fraction of remaining bad captured by the historical teacher is persistent month by month:

- Coinexx Jan/Feb/Jun/Jul: 79.3%, 77.1%, 80.4%, 79.5%.
- Dukascopy Jan/Feb/Jun/Jul: 89.3%, 88.6%, 89.3%, 93.0%.

This strongly motivates a dedicated **late-NY / rollover transition microstructure specialist**, rather than forcing the universal model to represent this regime.

### 2.4 Opposite and neutral have different causal physics

On current R148B releases using the already-built R149 causal state, the strongest standardized differences versus CORRECT separate cleanly:

**OPPOSITE versus CORRECT:** 1-second side-adjusted trend slope `-0.755`, 1-second direction posterior `-0.744`, 1-second Kalman drift `-0.578`, 5-second Kalman drift `-0.572`. OPPOSITE behaves mainly as a **directional persistence / sign-failure** problem.

**NEUTRAL versus CORRECT:** 1-second ATR proxy `-0.767`, 5-second ATR `-0.734`, 500ms ATR `-0.698`, 15-second ATR `-0.691`, 15-second quote activity `-0.561`. NEUTRAL behaves mainly as a **low-energy / low-information-arrival / no-first-passage** problem.

This is direct evidence against combining OPPOSITE and NEUTRAL into one undifferentiated BAD hunter.

### 2.5 Event-time ordering contains additional candidate information

An exploratory 19,111-event audit sampled teacher-residual bad events outside R148B against R148B-released correct events using only the final 32 native quotes strictly before the decision. The larger standardized differences included side-adjusted event-time midpoint slope `-0.341`, signed revision sum `-0.244`, path efficiency `-0.237`, average spread `-0.215`, spread-opening frequency `-0.212`, and spread-closing frequency `-0.204`.

This is **not a scored filter result**, but it supports a new research direction: R149's midpoint candle summaries discard event ordering, bid-only/ask-only revision patterns, spread transitions and inter-arrival dynamics that may help reconstruct the teacher residual.

## 3. R150 architecture — Orthogonal teacher residual + autonomous causal trunk

### Mechanism A — Cross-fitted orthogonal teacher residual

Let `P` be frozen parent outputs/components and `T` the historical teacher score. Fit a time-blocked, broker-aware nuisance model `g(P)` and create the training target:

`teacher_residual = logit(T) - g(P)`.

The new residual student is then trained on **new causal state Z only**, not on the teacher itself at inference and not allowed to take easy credit for information already contained in R148B. Block cross-fitting prevents a model from manufacturing residual structure from its own in-sample nuisance fit. Neyman-orthogonal / double-ML ideas motivate the robustness principle, but no causal-treatment theorem is claimed for this trading application.

A second optional penalty should explicitly decorrelate the residual student's latent representation from the parent score tensor. The goal is not just teacher fidelity; it is **new information conditional on the parent**.

### Mechanism B — Direct full-state restoration

R149 gives its learner the 179D R149 state plus compressed frozen parent score channels but does not directly expose the full 153D R120/R147 structural state. R150 should reuse the existing published causal state directly: six-clock tick geometry, UTC session anchors, completed M1/M5/M15/H1 structure, path/session interactions and R149 technical/Bayesian state. This is reuse, not an engine rebuild.

### Mechanism C — Autonomous self-supervised market-state encoder

Before teacher supervision, pretrain a causal encoder on tasks that do not require FILTER08 at all:

- next native quote event type and inter-arrival hazard;
- spread widen/close probability;
- next 1s/5s/15s side-adjusted displacement quantiles;
- favorable/adverse first-passage hazard;
- cross-clock trend persistence and volatility-regime transition;
- reconstruction/contrastive agreement between event-time and wall-clock state.

These labels are historical future observations used only during offline forecasting training; live inference still consumes past-only state. This creates a representation that can survive eventual teacher retirement.

### Mechanism D — Marked event-time microstructure intensity engine

Represent native quote events as marks such as bid-up, bid-down, ask-up, ask-down, simultaneous move, spread-widen and spread-narrow. Maintain Hawkes-inspired exponentially decayed intensities and cross-excitation states over the last 8/16/32/64/128/256 real quote revisions. Use source-normalized ratios rather than pretending Coinexx has true aggressor volume or L2.

Key outputs: bid/ask revision imbalance, excitation asymmetry, spread hazard, quote-intensity acceleration, event-run persistence, time-since-last-reversal and source-normalized information time.

### Mechanism E — Low-order lead-lag path signatures / temporal complexity

Compute depth-2 (and only if justified, shallow depth-3) signature features on normalized `[event time, side×mid, spread, bid revision, ask revision]` paths. The purpose is to preserve **ordering and lead/lag geometry** that ATR/RSI/Bollinger collapse. Add permutation/run entropy and path efficiency as complementary low-cost complexity features.

Recent 2026 work on lead-lag signatures in financial forecasting shows that depth-2 signatures can be updated efficiently and retain path-dependent information, but also cautions that gains over simple technical indicators are asset-dependent. R150 should therefore treat signatures as a specialist, not as assumed alpha.

### Mechanism F — Duration-aware Bayesian regime posterior

Replace R149's simple two-state HMM as the primary regime mechanism with a robust online run-length posterior / duration-aware state model over `persistent trend`, `pullback`, `neutral/compression`, `shock`, and `transition`. Outputs should include regime probabilities, probability of an immediate changepoint, posterior run-length quantiles and regime entropy.

The crucial new information is **regime age and uncertainty**, not merely another shock probability.

### Mechanism G — Three-way physical decomposition

Do not train `BAD = OPPOSITE OR NEUTRAL` as one mechanism.

1. **NEUTRAL / energy-survival specialist:** estimates whether the market has enough causal energy/information arrival to achieve a meaningful first passage. Inputs emphasize ATR surface, quote intensity, spread state, path entropy and volatility compression.
2. **OPPOSITE / direction-failure specialist:** conditional on directional movement, estimates whether side-aligned persistence is failing. Inputs emphasize event-time signed flow, path signatures, slope/drift posterior, pullback geometry and HTF conflict.
3. **CORRECT guardian:** specifically models existing R148B/R149 false vetoes and has priority to rescue high-confidence correct events.

### Mechanism H — Correct-loss recycling bank

Treat correct-loss budget as scarce risk capital. The current hunter's 11.7–12.5 bad-per-right ratio becomes the replacement benchmark. R150 should first identify hunter vetoes that can be safely rescued. Every recovered correct event creates budget for a higher-selectivity residual specialist.

This is not literal capital in the trading account; it is a research accounting device for asymmetric classification risk. A new specialist that cannot beat the hunter's bad/right efficiency in broker-transfer testing should not displace it.

### Mechanism I — Mixture-of-experts jury, not a serial AND gate

Use parallel specialists with a regime/session router:

- late-session/rollover microstructure expert;
- neutral-energy expert;
- opposite-direction expert;
- path-signature expert;
- Bayesian transition expert;
- correct guardian.

The router should learn conditional mixture weights by broker/session/side/regime. A specialist may abstain. No single universal threshold and no mandatory all-specialists-AND rule.

### Mechanism J — Groupwise Neyman–Pearson + online selective abstention

Allocate the false-veto budget separately by broker × session × side × regime instead of globally. Use matured past outcomes only to update subsequent group risk estimates. If uncertainty, domain shift or a correct-loss confidence bound breaches the envelope, the group abstains to frozen R148B.

Online/selective conformal methods and recent time-series distribution-shift calibration provide useful design inspiration for abstention and risk monitoring. Because market data are dependent/nonexchangeable, R150 must not claim distribution-free trading guarantees merely by adding conformal machinery.

## 4. Teacher-fade autonomy curriculum

The explicit objective is to **use the teacher to discover structure, then make the teacher unnecessary**.

**Phase 1 — Teacher microscope.** Cross-fitted teacher residual is a strong auxiliary target. The student must learn new conditional structure, not the parent's already-known score surface.

**Phase 2 — Teacher dropout.** Reduce teacher-residual loss weight while increasing original-class, self-supervised event-dynamics and first-passage objectives. Randomly omit the teacher auxiliary loss from batches so the causal trunk cannot depend on always receiving privileged supervision.

**Phase 3 — Teacher-free clone.** Train a new student from the frozen autonomous representation using only original labels and physical/self-supervised objectives. The teacher is used only afterward to explain missed clusters.

**Phase 4 — Teacher retirement gate.** The teacher-free model must preserve most of the teacher-assisted incremental frontier on month-block and broker-transfer tests at no greater correct-loss budget. Only then can the teacher cease being a routine training target and remain solely a forensic grader.

A useful autonomy metric is `teacher-free incremental gain / teacher-assisted incremental gain`, reported separately by broker-month and class. R150 should not be called autonomous if this ratio collapses when privileged training is removed.

## 5. Research success criteria

R150 should be judged in this order:

1. **Correct recovery first:** recover 1,500–3,000 current correct losses per broker while surrendering as few existing bad vetoes as possible.
2. **Replace the low-quality hunter:** new residual vetoes must materially exceed the current 11.7–12.5 bad/right efficiency and preferably exceed 25–30 bad/right in transfer diagnostics.
3. **Neutral specialist:** increase neutral rejection substantially without using opposite-class directional thresholds as a proxy.
4. **Late-session specialist:** determine whether the 21–23 UTC teacher residual can be reconstructed with native event-time/spread features across all four months and both brokers.
5. **Teacher autonomy:** demonstrate that a teacher-free student retains most of the teacher-assisted incremental gain.
6. **Broker transfer:** no universal specialist is promoted unless both transfer directions respect the correct-loss envelope; otherwise retain broker-native experts with R148B fallback.
7. **True forward proof:** Jan/Feb/Jun/Jul remain exposed mechanism-development months. G08 requires a genuinely new chronological month/demo stream with labels hidden until maturity.

## 6. Why this is more promising than another indicator optimization

The data already show that the neutral and opposite classes differ in their causal geometry. The missing information is more likely to live in **event ordering, microstructure intensity, spread transitions, regime duration, path topology, full direct multi-timeframe context, and class-specific physics** than in another optimization of RSI period or Bollinger width.

ATR, RSI, Bollinger and Fibonacci remain useful coordinates, but R150 should make them supporting features. The new primary mechanisms are orthogonal teacher-residual learning, event-time marked intensity, path signatures, duration-aware Bayesian regime inference, correct-loss recycling and a groupwise NP mixture-of-experts router.

## 7. External mechanism inspiration

- Chernozhukov et al., Double/Debiased Machine Learning: Neyman orthogonality and cross-fitting as an inspiration for isolating residual information while reducing nuisance-model leakage.
- Laub et al., 2025, *Hawkes Models and Their Applications*: self-exciting marked event intensities, including finance applications.
- Choi, 2026, *Efficient Computation of Lead-Lag Signature Features for Financial Time-Series Forecasting*: efficient depth-2 signature features and explicit evidence that usefulness is asset-dependent.
- Altamirano, Briol & Knoblauch, 2023, *Robust and Scalable Bayesian Online Changepoint Detection*: causal robust run-length inference.
- Gibbs & Candès, 2024, and Bao et al., 2025: online conformal/selective calibration under changing distributions, used only as abstention/risk-control inspiration.
- Huang, Ma & Michailidis, 2026: online calibration under temporal dependence and distribution shift with a fixed backbone and gated residual correction, conceptually close to R148B + R150 fallback architecture.

## 8. Exact next action

**Do not change R148B decisions yet. Freeze R149 telemetry. Build R150 as an orthogonal research challenger.** Reuse the existing R120/R147 publisher and raw tapes. Start with two experiments that directly attack the audit findings: (1) cross-fitted teacher-residual student with direct full-state access and parent-information orthogonalization; (2) event-time late-session microstructure + separate NEUTRAL/OPPOSITE/CORRECT specialists. Only if these create incremental unique vetoes at materially better bad/right efficiency should the path-signature, full BOCPD/HSMM and groupwise risk-router layers be activated.

No checklist acceptance or live/demo approval is inferred by this audit.
