# BETA 011 — 0.01-lot P&L / commission / $100k-capital audit of R09_BETA_001

Status: CORRECTION. This audit supersedes the monetary interpretation and formal-breakthrough classification in the original R09_BETA_001 scorecard. It does not reject the entry mechanism.

## Historical MT5 calibration

Direct inspection of `ReportTester-871471_jan2026_jul2026_R9_ticklog_real(4).xlsx` establishes:
- EA input lot size = 0.01.
- Initial deposit = $100,000.
- Historical REAL net = -$50,285.28; gross profit = $30,180.23; gross loss = -$80,465.51; maximal balance/equity DD about $50,285.
- First observed XAUUSD position: buy 0.01 at 4332.34, exit 4331.68, position profit -$0.66. Therefore for this 0.01-lot Coinexx XAUUSD test, a $1.00/oz price move corresponds numerically to approximately $1.00 position P&L.
- Commission shown on each deal is -$0.01, so a normal two-deal round trip costs $0.02, not $0.20.

## Error found in BETA 009/010 simulator

The simulator used raw XAUUSD price difference directly as USD P&L (which is consistent with the observed 0.01-lot Coinexx contract scaling), BUT subtracted `COMM=0.20` per closed position. That was 10x the commission visible in the historical R9 REAL tester report.

Thus lot scaling itself was not the large P&L error. Commission was overstated by $0.18/trade. More importantly, the Dukascopy Bid/Ask spread path remains materially different from Coinexx, so same-feed Dukascopy dollars are not directly comparable to historical R9 Coinexx dollars.

## Corrected direct-tick rerun

Re-ran the same feed-normalized R9 control and R09_BETA_001 entry candidate on Jan-Jul Dukascopy ticks with:
- lot-equivalent P&L: 0.01 Coinexx lot -> price delta x 1 USD per $1/oz move;
- roundtrip commission = $0.02;
- actual Dukascopy Bid/Ask fills;
- same R9 stop $0.30, trail activation $0.10, trail $0.03, max hold 30s;
- $100,000 starting equity tracked sequentially.

### Aggregate counterfactual continuation (allows equity below zero; NOT broker-executable after insolvency)

| Metric | R9 same-feed control | R09_BETA_001 corrected |
|---|---:|---:|
| Trades | 246,404 | 226,696 |
| Winning trades | 58,279 | 61,650 |
| Win rate | 23.6518% | 27.1950% |
| Net P&L | -$191,813.12 | -$157,216.35 |
| Gross profit | $16,701.11 | $18,776.18 |
| Gross loss | -$208,514.22 | -$175,992.53 |
| Counterfactual max DD from $100k peak | $191,813.12 | $157,216.35 |

Candidate changes vs same-feed control:
- winning-trade count: +5.7842%
- relative win rate: +14.9807%
- net-loss reduction: +18.0367%
- gross-loss reduction: +15.5978%

The winner-count improvement is BELOW the owner's >10% entry winner-count goal; therefore the prior formal breakthrough classification is withdrawn pending a replacement/expanded entry candidate.

### Candidate monthly corrected values

| Month | Trades | Wins | Win rate | Net P&L | Gross Profit | Gross Loss | Sequential ending equity |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jan | 31,250 | 8,606 | 27.5392% | -$21,026.53 | $2,469.96 | -$23,496.48 | $78,973.47 |
| Feb | 27,117 | 7,278 | 26.8393% | -$21,488.91 | $2,949.16 | -$24,438.06 | $57,484.57 |
| Mar | 49,444 | 13,607 | 27.5200% | -$37,586.67 | $4,994.66 | -$42,581.33 | $19,897.90 |
| Apr | 30,134 | 8,032 | 26.6543% | -$21,198.48 | $2,335.74 | -$23,534.21 | -$1,300.58 |
| May | 31,178 | 8,787 | 28.1833% | -$18,993.58 | $2,238.10 | -$21,231.68 | -$20,294.16 |
| Jun | 34,522 | 9,763 | 28.2805% | -$21,400.43 | $2,509.44 | -$23,909.88 | -$41,694.59 |
| Jul | 23,051 | 5,577 | 24.1942% | -$15,521.76 | $1,279.13 | -$16,800.89 | -$57,216.35 |

## $100k account feasibility correction

A real $100,000 account cannot continue the above counterfactual replay after equity is exhausted. The candidate ends March at about $19,897.90, then loses another $21,198.48 during April and crosses zero during April under this Dukascopy execution model. Therefore:
- `-$157,216.35 Jan-Jul net` is a counterfactual research-account continuation, NOT a feasible realized result from one $100k funded account.
- `$157,216.35 max DD` is likewise not a valid funded-account DD; the capital-constrained path reaches approximately 100% drawdown / insolvency in April (and actual broker stop-out could occur before zero depending margin/stop-out rules).
- Any future scorecard must report both `counterfactual research continuation` and `capital-feasible $100k account result`, never mix them.

## Scientific interpretation

The candidate remains worth researching because it increases wins, increases entry win rate, and reduces losses materially versus the same-feed control. But it does not yet satisfy the owner's >10% winning-trade-count target after correcting commission, and it is not $100k-survivable on raw Dukascopy cost conditions. The R09_BETA_001 formal-breakthrough label is therefore RETRACTED / RESEARCH-CANDIDATE ONLY until a corrected candidate passes the gate.
