# R9B_Gamma_<ORDER>_<BREAKTHROUGH_NAME> — Public Technical White Paper

## Status
- Canonical breakthrough ID: `R9B_Gamma_<ORDER>_<BREAKTHROUGH_NAME>`
- Promotion state: FORMALLY_PROMOTED
- Parent integrated baseline:
- Promotion commit/tag:
- Source/result hashes:
- Public implementation lineage:
- Research period:
- Evidence authority:
- Authors/maintainers:

## 1. Executive Summary
Explain in plain language what the breakthrough is, what problem it solves, why it matters, and where it is used in the R9B Gamma system.

## 2. Problem Definition
Describe the specific R9 REAL failure population or missing system function that motivated the research. Quantify the baseline problem using the canonical R9 REAL/SYNTH reference index.

## 3. Discovery History
Document the chronological research path that led to the breakthrough:
- prior failed or partial approaches;
- project-source clues;
- community/research mechanisms consulted;
- why each source was reconstructible enough to test;
- key falsification steps;
- the observation that caused the final hypothesis to be tested.

Do not rewrite failed research as success. Preserve the actual discovery lineage.

## 4. Reconstructible Mechanism
Describe the mechanism in sufficient detail for independent implementation:
- state variables;
- formulas;
- thresholds;
- timing rules;
- entry/hold/exit ownership;
- event ordering;
- completed-vs-partial bar semantics;
- bid/ask execution basis;
- stop/target/trailing behavior;
- session/regime logic;
- state transitions;
- duplicate-event/rearm rules;
- pseudocode/state-machine diagram in text form where useful.

No opaque black-box dependency may be required to reproduce the mechanism.

## 5. Data and Causal Contract
Record:
- raw source corpus and hashes/manifests;
- certified cache/index versions;
- exact chronology rules;
- feature contract;
- label contract;
- discovery/calibration/forward partitions;
- transaction-cost/spread assumptions;
- leakage controls;
- sealed data status.

Explain why no future information is available to the execution decision.

## 6. Quantitative Validation
Report the formally promoted evidence.

### Jan–Jul aggregate
- Trades/events:
- Net profit:
- Gross profit:
- Gross loss:
- Profit factor:
- Win rate:
- Expected payoff:
- Max drawdown:
- Average/median hold:
- MFE/MAE and favorable-excursion capture:
- REAL→SYNTH gap closed:
- Incremental value versus prior best integrated baseline:

### Monthly breakdown
| Month | Net | Gross Loss | Max DD | Trades | Notes |
|---|---:|---:|---:|---:|---|
| Jan | | | | | |
| Feb | | | | | |
| Mar | | | | | |
| Apr | | | | | |
| May | | | | | |
| Jun | | | | | |
| Jul | | | | | |

## 7. Economic Function and System Value
State exactly which function(s) the breakthrough owns:
- ENTRY/ACTION;
- HOLD/PERSISTENCE;
- EXIT/HARVEST;
- STRUCTURAL/REGIME;
- FAILED-IGNITION/REVERSAL;
- GROSS-LOSS/TAIL CONTAINMENT;
- OPPORTUNITY/DENSITY;
- PORTFOLIO DIVERSIFICATION.

Show why the breakthrough adds incremental system value rather than merely filling a theoretical gap.

## 8. Interaction With Existing Breakthroughs
List constituent/parent R9B_Gamma IDs and document:
- overlap;
- conflict;
- priority;
- capital/position ownership;
- correlation;
- drawdown interaction;
- chronology;
- why the combination is complementary.

If this paper describes a combined breakthrough, explain why arithmetic addition of standalone PnL is insufficient and show the integrated chronological result.

## 9. Optimization and Robustness
Document:
- parameter neighborhoods;
- plateau/stability behavior;
- spread/cost stress;
- execution perturbations;
- day/hour/session/regime attribution;
- capital-survivability checks;
- sensitivity to data/cache implementation;
- source-equivalence checks.

Separate frozen promotion parameters from exploratory alternatives.

## 10. Failure Modes and Boundaries
Explain when the mechanism fails, abstains, degrades, conflicts with another sleeve, or should not be used. Include known adverse regimes and any unresolved risks.

## 11. Where It Is Used
Specify the exact location in the integrated R9B Gamma architecture:
- upstream/downstream dependencies;
- decision stage;
- timeframe/state inputs;
- routing priority;
- lifecycle ownership;
- implementation module/file/function;
- enabled/disabled conditions.

## 12. Python Reference Implementation
Identify the canonical Python source, commit, result manifest, cache schema, hashes, and minimal reproduction command/process.

## 13. MT5 / MQL5 Translation Contract
When MT5 implementation is authorized, document the deterministic mapping from the certified Python mechanism to MQL5:
- tick chronology;
- bucket semantics;
- state variables;
- exact thresholds;
- numeric precision;
- order/position handling;
- expected parity checks.

Python discovery evidence does not become MT5-certified evidence until real-tick Strategy Tester validation passes.

## 14. Refinement Starting Point
This is the mandatory restart section for future work on this breakthrough.

Record:
- current best version;
- frozen assumptions;
- known bottleneck;
- strongest rejected alternatives;
- highest-value unresolved questions;
- safe next experiments;
- parameters that may be optimized;
- parameters/semantics that must not change without reopening certification;
- upstream/downstream breakthroughs affected by changes.

A future researcher should be able to resume refinement from this section without reconstructing the project from chat history.

## 15. Provenance and Artifact Index
List all durable references:
- GitHub commits/tags/paths;
- public result manifests;
- Google Drive research records where applicable;
- source hashes;
- cache hashes;
- MT5 report identifiers;
- community/public references used for mechanism reconstruction.

Do not expose private Drive identifiers or sensitive/private data in the public paper.

## 16. Revision History
| Revision | Change | Validation impact |
|---|---|---|
| 1.0 | Initial promoted white paper | Formal promotion baseline |

---
This paper is a public technical research record. It documents evidence and mechanism behavior; it is not a promise of future trading performance.
