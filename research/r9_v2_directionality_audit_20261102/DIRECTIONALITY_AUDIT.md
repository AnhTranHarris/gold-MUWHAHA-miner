# R9 v2 Directionality Audit — 2026-11-02

## Verdict

The current v2 entry-direction mechanism is deterministic but does not probabilistically determine BUY versus SELL. It first selects one side using a hand-weighted continuation/reversion heuristic (`specialist_evidence`), then applies WAIT confirmation and later acceptance models to that already-selected side.

Direct paired-action replay shows that, among entry events where exactly one of the two directions produced the strict favorable-first / positive R9-style outcome, the original v2-selected side matched the hindsight-valid direction only:

- Coinexx: 432,802 / 854,236 = 50.6654%
- Dukascopy: 123,343 / 245,517 = 50.2381%

Approximate 95% confidence intervals are 50.559%–50.771% for Coinexx and 50.040%–50.436% for Dukascopy. The deviations from 50% are statistically measurable because the samples are enormous, but economically they are tiny and nowhere near the project's high-accuracy requirement.

## Structural cause in source

`specialist_evidence(f)` computes two hand-weighted scores:

- continuation = Hawkes quote direction + normalized 1s/5s speed + spread quality + weak HTF context
- reversion = Bollinger overextension + quote flow + 45s displacement + weak HTF context

It chooses the specialist with the largest absolute score and sets direction solely from the sign of that score.

The learned Bayesian/LightGBM models do NOT independently compute P(CORRECT|BUY) and P(CORRECT|SELL) and select the better side. They score the side already nominated by `specialist_evidence`.

The sequential WAIT stage preserves `pending.side`; confirmation may confirm or cancel that side, but it does not simultaneously score and switch to the opposite side.

The 60-second teacher/student is also side-conditional. It is an acceptance/veto model, not a true direction-selection model.

## Paired-action discrimination

Held-out paired-action AUC:
- Coinexx Jan 0.5011
- Coinexx Feb 0.5169
- Coinexx Jun 0.5207
- Coinexx Jul 0.5243
- Dukascopy Jan 0.5527
- Dukascopy Feb 0.5470
- Dukascopy Jun 0.5581
- Dukascopy Jul 0.5983

## Required correction

At every eligible observed quote state, score simultaneous causal BUY and SELL action views:

BUY -> P(correct), P(incorrect), P(neutral), expected net, first-passage hazards
SELL -> P(correct), P(incorrect), P(neutral), expected net, first-passage hazards

Define a directional margin D = P(correct|BUY) - P(correct|SELL). Trade BUY/SELL only when the corresponding posterior, expected value and directional margin all clear calibration; otherwise WAIT. Recompute both sides after every observed WAIT update.

The hindsight teacher should label both BUY and SELL at every eligible event; future labels never become runtime features.

A repaired direction engine fails before exit analysis if its unique-direction match remains near 50%.
