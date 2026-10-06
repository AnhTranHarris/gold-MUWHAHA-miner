# BUILD-02 Session/Timeframe Jan-Jul Stress 003

**Unit:** `DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_JANJUL_STRESS_003`  
**Candidate:** `STMR_XMONTH_SUBPHASE_001`  
**Status:** COMPLETE STRONG RESEARCH CANDIDATE — NOT PROMOTED  
**Authoritative parent remains:** `STMR_SLEEVE_PHASE_001`

## Provenance boundary

The accepted January floor remains +$877.78 / 1,518 trades / PF 1.602933. The exact portable replay helper bytes were not recovered from Project, Library, GitHub, or either connected Google Drive account. Therefore this Jan-Jul campaign is a clean-room ordered-tick stress lineage and cannot silently overwrite journal 0024.

## Session/timeframe-only refinement

No new market dimension was introduced.

Funded semantic sleeves:
- ASIA_LOWER_TAKEOVER
- LONDON_M5_TAKEOVER
- OVERLAP_LOWER_TAKEOVER
- LATE_ALIGNED_MOMENTUM
- LATE_MACRO_SPLIT_TRANSFER
- LATE_LOWER_TAKEOVER

Observe-only:
- ASIA_M15_DIVERGE_M5_RECLAIM
- LONDON_M5_RECLAIM
- OVERLAP_ALIGNED_COUNTERCROSS
- NY_LOWER_TRANSFER
- NY_LOWER_COUNTERCROSS
- LATE_M5_REJECTION

Additional bounded subphase rules:
- OVERLAP_LOWER_TAKEOVER: 15:00-16:00 UTC only.
- LATE_LOWER_TAKEOVER: 21:00-22:00 UTC only.

Preserved:
- fixed UTC session windows;
- accepted Asia/London targeted gates;
- completed-bar H4/H1/M15/M5 EMA(8/21);
- sleeve-local first-touch genealogy;
- ordered Bid/Ask;
- fixed 0.01 lot;
- max 3 grid-owned positions;
- no Martingale/loss-dependent sizing;
- August sealed;
- no MQL5.

## Month-by-month clean-room result

| Month | Net |
|---|---:|
| Jan | +$641.58 |
| Feb | +$43.95 |
| Mar | +$4.55 |
| Apr | -$34.51 |
| May | -$19.89 |
| Jun | +$213.13 |
| Jul | -$19.10 |
| **Jan-Jul** | **+$829.71** |

Aggregate:
- gross profit $3,625.77
- gross loss -$2,796.06
- PF 1.296743
- 2,675 trades
- 877 wins
- win rate 32.785%
- expected payoff +$0.310172/trade
- forced final liquidations 0
- max open positions 3
- worst month-local balance DD $78.63
- worst month-local equity DD $79.33
- minimum month-local equity delta -$55.29

Versus `STMR_XMONTH_ADMISSIBILITY_001` (+$780.42, PF 1.1816, worst month -$81.68), this adds +$49.29 and improves the hostile-month tail by +$47.17.

Deleting LATE_LOWER_TAKEOVER entirely produced +$815.56 / PF 1.2956. The 21:00-22:00 subphase is therefore superior to deletion.

## Rejected during stress

- blanket DST remapping;
- removal of accepted Asia/London gates;
- global faster timeframe ownership;
- broad per-sleeve timeframe role maps;
- toxic-sleeve FLIP;
- overlap 15:00-16:00 as a forward-only promotion rule;
- timer-only rearm / generic recrossing.

## Scientific decision

Retain `STMR_XMONTH_SUBPHASE_001` as the strongest clean-room Jan-Jul session/timeframe research child found in this campaign. Do not promote over journal 0024 without exact parity recovery or explicit owner authorization of clean-room cross-month authority.

April, May, and July remain unresolved. Do not calendar-fit them away. Any further repair should come from later orthogonal causal dimensions.

Durable exact bytes are persisted in Library:
`/xauusd-trading-bot/delta-A-alpha/stmr-janjul-stress-2026-10-06/`

Exact hashes:
- helper `stmr_subphase_refine.py`: `0df41a4ece3083129022443daab14687b5a170bb888e879d7352301568f7def5`
- full result JSON: `32f2c80fad10950a51e22d14c37bcc8ad333bae2581078a4f0205ed37b443515`
- report: `2a4ccb9ea8604c7a1bfb07e018432cd040f73d11697b5c5e8fde55d157af2b5a`
