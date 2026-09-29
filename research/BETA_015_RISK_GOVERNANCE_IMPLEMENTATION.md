# BETA 015 — Research risk controls (index)

Implementation status: Python risk policy and funded-run validator saved on the beta branch. These requirements apply to NEW BETA research experiments, not to an approved MetaTrader EA. Legacy BETA014 evidence remains unchanged.

Owner-defined controls: $100,000 initial account; XAUUSD only; 0.01 lot fixed; one aggregate position; $4,000 daily no-entry pause, $5,000 daily hard stop, and permanent $90,000 overall equity floor. New studies must measure mark-to-market equity and correct Bid/Ask, fees, and account shutdown. News blackout remains unevaluated without sourced event times.

Complete source and independent tests: https://drive.google.com/drive/folders/11imx5cE1Pvzr81V0nRJs2MEjBy5mt4nE ; files `BETA_015_RISK_GOVERNANCE_IMPLEMENTATION.md`, `BETA_015_PROP_POLICY_TESTS.py`, and `BETA_015_RUN_GATE_TESTS.py`. The 30 latest tests passed locally, including fail-closed broker-session eligibility.

Any maturity-phase change requires a new explicit owner request, new policy version, and a new governed tick replay. No MQL5 changes without separate authorization.

Related: [policy source](risk/BETA_015_PROP_POLICY_V1.py) | [config](risk/BETA_015_PROP_POLICY_V1.json) | [run-gate source](risk/BETA_015_RESEARCH_RUN_GATE.py) | [MTF hypotheses](BETA_016_REPRODUCIBLE_MTF_REGIME_AND_SPECIALIST_RESEARCH.md).

**Final broker-session safety patch:** the Python guard now defaults `broker_trading_enabled=False`; a caller must supply explicit broker/simulator permission before any new entry. This avoids assuming XAUUSD is open just because it is a weekday. Final source archive: https://drive.google.com/file/d/1tFsG7gUsgFP1ka62hs7As0k-_RU5G3gN/view ; final 22 policy unit tests: https://drive.google.com/file/d/15UG7jmIf8Ujmw1RV4f3-Wbh16koPgVYF/view ; 8 unchanged run-gate tests. **30/30 PASS.**
