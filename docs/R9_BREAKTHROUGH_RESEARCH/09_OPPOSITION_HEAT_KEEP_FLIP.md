# 09 — Opposition Heat + KEEP/FLIP

**Status:** validated portfolio research; exact original score coefficients are not preserved, so implementation must be re-fit/re-certified rather than guessed.

## Opposition-aware portfolio heat

The decisive finding was that **opposite-direction concurrent exposure**, not raw concurrency, drove much of the catastrophic-loss probability.

Same-direction stacking remained productive. As opposite-direction positions accumulated, expectancy deteriorated and catastrophic-stop probability roughly doubled.

The governor therefore becomes more selective only when the portfolio already carries meaningful exposure in the opposite direction.

## KEEP-vs-FLIP after catastrophe

After a fresh catastrophic stop, the next same-scale opportunity is not treated as an independent event.

A selective router chooses:
- KEEP the new opportunity's thesis,
- FLIP to the opposite auction state,
- or abstain.

On the May-Jul post-catastrophe subset, the original same-direction policy was about -$744. The KEEP/FLIP treatment produced roughly +$5,041 while gross loss improved from about -$4,215 to -$1,789.

## Loss-priority champion

The combined opposition-aware governor + KEEP/FLIP research champion produced approximately:
- +$309,239 Jan-Jul
- -$185,043 gross loss
- max 5-second DD ≈ $189.78
- ~525,466 trades
- PF ≈ 2.67

It preserved approximately the R9 SYNTH net benchmark while cutting gross loss materially versus the previous +$313K champion.

Portfolio cross-check:
https://www.mql5.com/en/articles/21955

Implementation note: re-fit any numeric score thresholds from Jan-Apr data. Do **not** invent missing coefficients from the summary.
