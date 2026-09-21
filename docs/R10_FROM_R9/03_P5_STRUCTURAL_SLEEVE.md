# Checkpoint 03 — P5 Structural Trend Sleeve

P5 is now executable code in the R9-derived R10 line.

The implementation uses completed H1/H4 bars only:
- H1: 5-bar Donchian-style structural breakout, relative-volatility ceiling 1.20.
- H4: 6-bar structural breakout, relative-volatility ceiling 2.00.
- ATR(14) lifecycle with 1.5 ATR emergency room, 0.25 ATR activation, 1.0 ATR trail.
- H1 maximum lifecycle 12 hours; H4 maximum lifecycle 24 hours.

At this checkpoint the account is still one-position-at-a-time, matching the earlier integration phase. The later concurrency breakthrough is a separate checkpoint.

These are representative project-preserved P5 parameters and require MT5 real-tick certification.
