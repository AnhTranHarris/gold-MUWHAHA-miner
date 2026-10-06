# GRID-001 January One-Shot Opportunity Recovery 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_ONE_SHOT_RECOVERY_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

When an A10/A15 continuation event fails the frozen early-thesis test, does that failure itself provide enough causal evidence to justify exactly one opposite-direction recovery trade?

## Parent contract

Reuse Early Thesis Failure 001 exactly:

- lattices: A10 and A15;
- initial direction: continuation;
- state starts UNCONFIRMED;
- favorable proof: +0.25 event gap;
- provisional adverse failure: -0.50 event gap;
- after proof, original +1.00 TP / -1.00 hard stop;
- 5-minute event horizon;
- fixed 0.01 economics;
- $0.02 round-trip commission per physical leg;
- no averaging;
- no Martingale.

## Recovery rule

Only events that hit EARLY_THESIS_FAILURE are eligible.

At the executable quote where the initial continuation leg exits:

1. close the failed continuation;
2. immediately open exactly one opposite-direction recovery leg;
3. recovery TP = +1.00 original event gap from recovery entry;
4. recovery SL = -1.00 original event gap from recovery entry;
5. recovery must finish within the **remaining original 5-minute event horizon**;
6. no second flip is allowed;
7. if recovery times out, exit at the last executable quote inside the original horizon.

The event clock is not reset.

## Comparisons

For A10 and A15 measure:

### RETIRE
Initial early-failure state machine only; after early failure, event is retired.

### ONE_SHOT_RECOVERY
Initial early-failure PnL plus the opposite-direction recovery PnL.

### RECOVERY_ORACLE_CEILING
For early-failure events only, compare RETIRE versus one-shot recovery after the fact and keep the better outcome.

This oracle is diagnostic only and cannot be promoted.

## Required metrics

- eligible early-failure count/share;
- recovery trade win rate;
- recovery net/gross profit/gross loss/PF;
- combined event net/PF/expectancy;
- total gross-loss change versus RETIRE;
- total net change versus RETIRE;
- discovery vs validation;
- oracle recoverable-value ceiling;
- percentage of early-failure events where recovery beats retirement.

## Advancement rule

One-shot recovery is interesting only if:
- combined net/PF materially improve over RETIRE;
- improvement survives discovery and validation qualitatively;
- gross loss does not explode;
- no second flip or loss-dependent sizing is required.

If direct recovery is negative but the oracle ceiling is large, the next research problem becomes **recovery admission/classification**, not tuning the flip target/stop.

No threshold sweep is authorized.

August sealed. Main `delta` read-only. MQL5 unauthorized.
