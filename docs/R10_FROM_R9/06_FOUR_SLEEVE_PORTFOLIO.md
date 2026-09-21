# Checkpoint 06 — Four-Sleeve Portfolio Knee

This checkpoint converts the earlier one-position integration into the later portfolio architecture.

Rules implemented:
- maximum 4 simultaneous Gold positions by default;
- one live position per temporal scale;
- same-direction stacking is allowed;
- opposite-direction exposure is capped (default one opposing sleeve);
- core R9-derived one-minute sleeve remains independent;
- 1m/3m/5m/10m/20m boundary sleeves use separate magics;
- H1/H4 P5 sleeves use separate magics;
- all positions are managed as one account risk book;
- hedging account mode is required when concurrency > 1.

This implements the portfolio structure that captured roughly 95% of the unrestricted research profit at four concurrent sleeves. It is a compile/test candidate and still requires Coinexx MT5 real-tick certification.
