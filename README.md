# BETA — Independent XAUUSD Quant Research

This is the independent BETA research line. It does not adopt R9, Alpha, Gamma, or R10 trading code, settings, model weights, or claims.

## Evidence and workflow

- **BETA 000:** clean research lineage and immutable historical source map.
- **BETA 001:** R9 REAL/SYNTH original tester and tick-log historical audit; neither is a BETA strategy.
- **BETA 002:** fresh Dukascopy tick-first Python backtest laboratory; **17 resolution layers**: original tick events plus 250 ms, 1s, 5s, 15s, 30s, 45s, M1, M5, M7, M15, M30, M45, H1, H4, H12, D1. The tick is the execution source; bars are derived context.
- **BETA 003:** research groups ENTRY, HOLD, EXIT, PROFIT; >10% preregistered KPI improvement is only a *candidate* gate, not approval. Owner review before MQL5 code, owner Coinexx MT5 M1 report using 'Every tick based on real ticks' before final acceptance.

Complete verified BETA 000–003 artifacts, scripts and evidence are in the [owner's BETA_RESEARCH Drive folder](https://drive.google.com/drive/folders/11imx5cE1Pvzr81V0nRJs2MEjBy5mt4nE). Large original tick data remain in the existing source folders, never in GitHub.

## Guardrails

- XAUUSD only, January–July 2026; August sealed.
- Strictly causal tick chronology, Bid/Ask costs, completed-bar timing, monthly and aggregate diagnostics.
- R9 REAL and SYNTH are historical comparators; R9 OVERFIT is a future-aware retrospective diagnostic, never live knowledge.
- No approved BETA EA; do not invent one or inherit an old EA.
- Preserve failed tests; develop reconstructible mechanisms independently; no unapproved MQL5 coding or live trading.

**Branch creation:** This root is intended to be an orphan (no parents). If that cannot be verified, do not treat an inherited branch as an independent BETA root.
