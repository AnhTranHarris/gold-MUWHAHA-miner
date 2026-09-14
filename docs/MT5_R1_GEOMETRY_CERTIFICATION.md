# Gold MUWHAHA Miner — R1 Geometry Certification

Status: MT5 certification candidate only. Do not merge into the V8 baseline until the tests below pass.

## Control

- EA: `Experts/GoldMuwahahaMiner_V8_Baseline.mq5`
- Baseline defaults: Gap 50, SL 50, Trail 20, Trail Activation 20
- Frozen baseline branch: `carson/v8-cleanroom-baseline`

## Candidate

- EA: `Experts/GoldMuwahahaMiner_R1_Geometry.mq5`
- Candidate defaults: Gap 100, SL 50, Trail 15, Trail Activation 15
- Lots: 0.01
- Hunter pip price: 0.01
- Daily profit target logic: disabled
- No ATR filter
- No session filter
- No news filter
- No spread filter beyond the existing broker-validity behavior

This candidate intentionally changes only the trading geometry/default metadata. It is the cleanest possible MT5 test of the first Python-screening result.

## Required MT5 test 1 — full 2026 comparison

- Symbol: XAUUSD
- Timeframe: M1
- Model: Every tick based on real ticks
- Start: 2026-01-01
- End: 2026-08-31
- Initial deposit: 100 USD
- Leverage: same as the validated baseline test
- Inputs: leave candidate defaults unchanged

Export the Strategy Tester report after completion.

## Required MT5 test 2 — forward split

Use the same forward-testing split/procedure that produced the validated baseline `b1` / `f1` reports. Do not optimize inputs.

Export both backtest and forward reports.

## Promotion criteria

R1 is promoted to the next research stage only if:

1. It compiles with 0 errors and 0 warnings.
2. It remains profitable in the full-period real-tick MT5 test.
3. Its forward segment remains strongly profitable.
4. Forward win rate / PF / drawdown do not collapse relative to the control.
5. It does not achieve better headline profit by creating materially worse tail losses or startup drawdown.
6. Trade count and average holding time remain plausible for the V8-derived engine.

If R1 passes, the next candidate will add M5 ATR and spread gating in a separate EA. The V8 baseline remains unchanged.