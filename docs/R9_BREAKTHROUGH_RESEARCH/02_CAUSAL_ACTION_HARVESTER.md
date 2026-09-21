# 02 — Causal Action Harvester

**Status:** project-level causal control reconstructed from source history.

## Core result

The trustworthy pullback/reacceleration control reached approximately **+$24,682 Jan-Jul** with **7/7 positive months**.

A later CONTINUE/FADE action-value result reached roughly **+$40,542 / 181,610 trades**, but is retained as a research ceiling rather than clean OOS certification because Jan-Mar participated in learning.

## Mechanism

R9-style activity is treated as an **auction event**, not a mandatory direction.

A causal state is built from information already known at decision time:
- completed short-horizon displacement;
- directional efficiency;
- range;
- reversal/turn count;
- volatility phase;
- execution cost.

The action layer chooses:
- CONTINUE,
- FADE,
- or ABSTAIN.

Post-entry lifecycle defaults to fast harvesting rather than long fixed targets.

## P2/P3 modifiers carried forward

- **P2 Runner:** promote only after persistence is actually demonstrated after entry.
- **P3 Failed-Ignition:** terminate or selectively convert trades that fail to renew MFE while adverse excursion expands.

Early sandbox work showed runner promotion around 4–5% uplift and failed-ignition around 2–3%; these are modifiers, not standalone master engines.

## Reconstruction rule

Do not reconstruct the invalidated +$102K or ~$43K variants. They contained look-ahead / retrospective scheduling and are permanently excluded.
