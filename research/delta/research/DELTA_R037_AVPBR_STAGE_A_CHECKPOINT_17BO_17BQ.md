# DELTA R037 — AVPBR Feasibility Checkpoint 17BO–17BQ

**Status:** COMPLETE / FIXTURE FEASIBILITY FAIL / ECONOMICS NOT TESTED

The exact committed producer ran successfully on canonical Stage-A under the 120-second hard timeout and atomic-output contract, but all three profiles produced **zero accumulation starts and zero trades**.

This does **not** falsify the source mechanism. The indexed TradingView page exposes the compression rule but not its numeric default. The preregistered project fixture `20-bar range <= 1.5 x ATR14` is outside the observed XAUUSD scale.

A supply-only diagnostic, performed without inspecting forward returns or P&L, found the 20-bar range / ATR14 ratio:
- M1: minimum 1.867; p10 3.264; p25 **3.799**; median 4.508.
- M5: minimum 2.356; p10 3.283; p25 **3.799**; median 4.497.

Therefore checkpoint 17BO–17BQ is recorded as a **feasibility failure**, not a negative economic strategy result.

Producer commit: `9bc6a2fcb62933e47c55e4c188a1ff7be3b2924c`  
Producer blob: `341993896387fba6e19c6f72547fdf0c959087a6`  
Producer SHA-256: `d831ccf6ffd9467130c68778435942d1cbfc6fe0c985d08cf3d0b1f83dffe70b`  
Raw result SHA-256: `997756c5d1373eb4e19ae1106f6c825f13bc44901549412f68e2c0c30c5bc685`

**Next:** preregister one supply-calibrated AVPBR fixture using the p25 compression scale, without economic tuning.