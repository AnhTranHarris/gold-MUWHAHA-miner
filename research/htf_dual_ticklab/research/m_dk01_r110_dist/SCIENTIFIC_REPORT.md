# F401-R110-DIST: conditional trajectory distributions and matured calibration

Date: 2026-10-28. Status: UNAPPROVED; exact configurations parked. No replacement accepted.

## Decision and preserved research cursor

Executed one predeclared four-month batch over all 1,266,934 original Dukascopy
events and 32,290,648 source quotes. Neither the distribution model nor its
online calibration produces the required asymmetric incorrect rejection. Do not
retune this configuration after its frozen validation failure. This is evidence
against these configurations, not a conclusion that the overall goal is impossible.

This experiment was designed from R109 (43b70af4fa60f5b7418751fdc39b3f3bdc997224).
The final continuity check found the separate, newer R110/R111 action-space report
at ad4b551d224233d889c4c897e57d23bf027b587a, a direct child of R109. This evidence
is therefore named **R110-DIST**, not a replacement for that report. Publication
descends from the newer commit; **R112 remains the shared next cursor**.

The objective is incorrect rejection maximized under a correct-retention
constraint; balanced accuracy was not optimized. A 1% January CAL correct-loss
budget was the main frozen calibration, and 5% was a predeclared diagnostic.
Those CAL budgets are not guaranteed future-month limits. All realized counts
and loss rates are reported below, including violations outside CAL.

Original individual M-DK-01 reference: January 344,037 events, 178,642 original
correct and 165,395 incorrect, with 94,603 teacher incorrect vetoes and 7 correct
losses. The four fitted monthly teachers reject 448,187 incorrect and lose 41
correct. The requested >400,000 incorrect four-month target remains unmet by
this executable t0 score experiment. G06 eight-cell 71%/90% gates belong to the
combined filter; they do not replace the individual predecessor comparison.

## Original teacher evidence used to choose the mechanism

The original FILTER08 archive was recovered byte-exact, its ZIP CRC checked,
and all 50 listed member digests verified. `ORIGINAL_TEACHER_FAMILY_GAINS.json`
is copied unchanged from the archive. Dukascopy teacher gain shares include
ordered quote response 14.457%, side-relative returns 12.805%, multihorizon
returns 11.888%, matured outcomes 9.271%, completed M1/M5/M15/H1 geometry
8.584%/7.274%/6.258%/5.452%, session 5.155%, and quote arrival intensity 2.166%.
These identified the families to reconstruct and interact. They are original
descriptive gain shares, not per-family veto counts or new correlation estimates.

The separate newer R110/R111 report contains a 197-probe cross-month correlation
atlas and action-space experiment. Its reported 415,345 incorrect no-touch
opportunities come with 148,458 correct no-touches and negative quote-bound
markout; they are not executable vetoes. This run does not claim to have reproduced
that report's unpublished binary archive. R94 teacher-tree traversal is retained
as existing work, not repeated here. The exact original FILTER05 ordered vector
remains unavailable, so this is a custom source-native feature system rather than
93-column parity.

## New implemented mechanisms

**A: conditional multihorizon distribution.** Original authorized bid/ask tapes
feed the unchanged archived native feature producer. New structure uses 3/5/9
contiguous, fully completed M1/M5/M15/H1 bars: directional displacement, path/body
efficiency, high/low distance, close deviation, body agreement, range, and grid
phase. Micro, macro and joint views comprise 330 dimensions including missingness.
Past returns cover seconds through H1; side, session and quote activity are
context. Quote counts are not traded volume or depth. No economic-event feed or
real-volume state was available; the user-requested axes are not all implemented.

Continuous signed 5/15/30/60-second price trajectories are divided by the
contemporaneous 30-second realized increment scale (floor $0.05). Each of three
views has twelve ExtraTree partitions with at most 1,024 leaves, minimum 96
partition examples, max_features=.7, deterministic seeds. Every eligible row of
January's first 60% participates: 171,833 rows after missing trajectory windows
and a 65-second boundary purge. Alternating UTC-day halves split partition fitting
from leaf-distribution estimation; paired trees swap the halves. This construction
does not make adjacent trading days statistically independent.

The opposite half supplies the complete empirical normalized 30-second leaf
distribution. Event-specific +/-$0.10 cutoffs yield tail probabilities; the four
horizons shape the partition, but inference does not estimate a full joint
four-horizon distribution. The distribution policy uses 1 minus mean correct
probability; guardian uses 1 minus the maximum across views. A leaf with fewer
than 16 estimating examples uses a neutral probability, not a guaranteed abstention.

**B: matured online reliability.** The model updates a side x six-hour session x
predicted-probability-quintile state only when an earlier outcome has matured
at event time +33.001 seconds. Half-life is 30 minutes with prior mass 256. January
FIT outcomes do not enter the online calibrator; later months start with empty
state. The protected policy takes the larger correct probability from the
max-view guardian and calibrated estimate. Each policy has its own CAL threshold;
therefore protected masks need not be nested within distribution masks.

This is a distributional trajectory target and conditional reliability mechanism,
not another R109 fixed-barrier class blend or R105 conditional mean regression.
Nevertheless the observed failure does not justify running another nearby
leaf/threshold sweep. The next lead changes the decision target and information.

Method references, not borrowed performance or third-party strategy code:
Meinshausen's conditional quantile forests
(https://www.jmlr.org/papers/v7/meinshausen06a.html), Zillow's implementation
(https://github.com/zillow/quantile-forest), and native quote semantics
(https://www.mql5.com/en/docs/constants/structures/mqltick).

## Frozen evaluation

January rows 0–60% are FIT; 60–80% CAL; 80–90% VAL; 90–100% shadow.
Thresholds are chosen once from CAL and applied strictly greater-than, preserving
ties conservatively. All full January counts include FIT/CAL; February, June and
July are historically exposed transfer periods. No month here is prospective.
Full-month figures must never be described as wholly out-of-sample.

### Four-month totals, including mixed January

| policy | budget | incorrect_veto | correct_lost | random_wrong_expectation |
| --- | --- | --- | --- | --- |
| distribution | 0.01 | 18512 | 8710 | 16959.063 |
| distribution | 0.05 | 75760 | 44119 | 70911.496 |
| guardian | 0.01 | 17610 | 8449 | 16123.331 |
| guardian | 0.05 | 73986 | 43622 | 69281.435 |
| prequential | 0.01 | 31257 | 15685 | 31387.772 |
| prequential | 0.05 | 161372 | 106612 | 163824.595 |
| protected | 0.01 | 19806 | 9623 | 18148.249 |
| protected | 0.05 | 80919 | 48354 | 76039.632 |

Random expectation fixes each policy's veto count within original UTC-hour x
side cells. It is a diagnostic selectivity control, not the frozen accepted F234
cascade. F234 composition is not scored because its exact event masks were not
recovered here. The online policy's larger rejection count at 1% CAL budget is
accompanied by 15,685 correct losses and no gain over this matched random
expectation. It is not a capacity breakthrough.

### Per-month main calibration, with actual correct-loss rates

| month | policy | n | original_correct | incorrect_veto | correct_lost | correct_loss_pct | incorrect_rejection_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | distribution | 344037 | 178642 | 6994 | 3474 | 1.945 | 4.229 |
| 1 | guardian | 344037 | 178642 | 6627 | 3373 | 1.888 | 4.007 |
| 1 | prequential | 344037 | 178642 | 1320 | 680 | 0.381 | 0.798 |
| 1 | protected | 344037 | 178642 | 7431 | 3772 | 2.111 | 4.493 |
| 2 | distribution | 324582 | 143923 | 3346 | 1391 | 0.966 | 1.852 |
| 2 | guardian | 324582 | 143923 | 3203 | 1323 | 0.919 | 1.773 |
| 2 | prequential | 324582 | 143923 | 15077 | 7733 | 5.373 | 8.346 |
| 2 | protected | 324582 | 143923 | 3511 | 1498 | 1.041 | 1.943 |
| 6 | distribution | 297035 | 132105 | 3850 | 1766 | 1.337 | 2.334 |
| 6 | guardian | 297035 | 132105 | 3679 | 1764 | 1.335 | 2.231 |
| 6 | prequential | 297035 | 132105 | 6179 | 3038 | 2.300 | 3.746 |
| 6 | protected | 297035 | 132105 | 4166 | 2026 | 1.534 | 2.526 |
| 7 | distribution | 301280 | 130408 | 4322 | 2079 | 1.594 | 2.529 |
| 7 | guardian | 301280 | 130408 | 4101 | 1989 | 1.525 | 2.400 |
| 7 | prequential | 301280 | 130408 | 8681 | 4234 | 3.247 | 5.080 |
| 7 | protected | 301280 | 130408 | 4698 | 2327 | 1.784 | 2.749 |

### January independent validation and shadow

| split | policy | budget | n | original_correct | incorrect_veto | correct_lost | random_wrong_expectation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VAL | distribution | 0.01 | 34404 | 18970 | 7 | 13 | 9.606 |
| SHADOW | distribution | 0.01 | 34404 | 20925 | 0 | 0 | 0.000 |
| VAL | distribution | 0.05 | 34404 | 18970 | 157 | 144 | 148.416 |
| SHADOW | distribution | 0.05 | 34404 | 20925 | 1 | 0 | 0.415 |
| VAL | guardian | 0.01 | 34404 | 18970 | 8 | 21 | 14.215 |
| SHADOW | guardian | 0.01 | 34404 | 20925 | 0 | 0 | 0.000 |
| VAL | guardian | 0.05 | 34404 | 18970 | 182 | 181 | 178.550 |
| SHADOW | guardian | 0.05 | 34404 | 20925 | 4 | 1 | 2.064 |
| VAL | prequential | 0.01 | 34404 | 18970 | 0 | 0 | 0.000 |
| SHADOW | prequential | 0.01 | 34404 | 20925 | 0 | 0 | 0.000 |
| VAL | prequential | 0.05 | 34404 | 18970 | 41 | 52 | 49.901 |
| SHADOW | prequential | 0.05 | 34404 | 20925 | 0 | 0 | 0.000 |
| VAL | protected | 0.01 | 34404 | 18970 | 8 | 13 | 10.445 |
| SHADOW | protected | 0.01 | 34404 | 20925 | 0 | 0 | 0.000 |
| VAL | protected | 0.05 | 34404 | 18970 | 175 | 173 | 172.943 |
| SHADOW | protected | 0.05 | 34404 | 20925 | 3 | 1 | 1.661 |

`RESULTS.json` also contains side/session counts, neutral/opposite split,
teacher masks, and exact additional-veto/rescue overlaps. Counts called
`correct_lost` within a `rescued` intersection describe correct events rescued,
not losses; consult the containing intersection's definition. Independent
per-event recount confirms score thresholds, masks and original t/side/truth/
teacher identity for every original event. No rows were removed from scoring.

## Integrity, causality and bounded numerical discrepancy

Seven targeted tests pass: future tick mutation, later equal-timestamp quote
exclusion, incomplete-bar exclusion, maturity boundary, future-label prefix
invariance, frozen threshold ties and CDF monotonicity. These tests substantiate
the implemented as-of contracts; they do not establish live MQL5 or broker parity.
The original 11 reused engine files match their pinned Git blobs; no engine,
feed, clock or bar implementation was rebuilt.

January/February native rederived labels matched the original labels. June
preparation stopped on 184 discrepancies, and July has 308, all within 1e-9 of
exact +/-$0.10 boundaries. An equivalent midpoint arithmetic diagnostic produced
481/630 differences within 5.46e-13. `BOUNDARY_RECEIPT.md` records the guard
amendment made before June/July scoring: retain every original archived label,
record every discrepancy, and abort on any non-boundary mismatch. No discrepancy
flag enters a policy. Weights and January CAL rule were not retuned. January and
February cache receipts precede this guard amendment, explaining their earlier
run.py hash; feature calculations did not change. The online arm relies on the
archived matured-label numerical convention; its native runtime parity is open.

The source verification and complete original texts were retrieved, and governing
rules, current acceptance, active objective and recent receipts were inspected.
This run does not certify a word-for-word reread of every historical appended
audit/checklist paragraph. It therefore must not be used as an unrestricted
bootstrap approval for a new objective. Missing F234 composition, missing original
FILTER05 parity, and the original R9 intent-stage dependency remain explicit.

## Constructive continuation without repeating the failed configurations

Preserve R112 from the newer R110/R111 source report: learn **action-specific
correct-opportunity rescue**, using completed multichannel quote-order motifs
and cross-timeframe support/resistance role changes. Its objective is unique
incorrect avoidance under correct-missed constraints; its targets are conditional
action benefit, not another global Y score. The existing $0.35 quote-touch
primitive is a diagnostic capacity lead, not a trading result.

Three distinguishable hypotheses remain to test, not claims of measured success:
(1) asynchronous bid-versus-ask motifs identify beneficial rescue from the fixed
primitive; (2) a sparse state-specific action expert changes strike/cadence when
completed HTF structure and quote renewal disagree; (3) a two-stage unsubmitted
intent observes a new published quote prefix before selecting a contingent action.
The third requires genuine pre-OrderSend intent evidence before R9 parity claims.
Do not repeat R104 nearest-episode lookup, R109 global hazards, R111's inherited
guardian, or this distribution/calibration sweep under a new label.

The next implementation must use complete authorized populations, frozen temporal
selection, original-event identities, correct rescue versus bad re-admission,
unique marginal masks against the accepted parent, and class/session/side controls.
Full eight source cells, 4,178 quota checks, MQL5 parity and twelve shared-capital
after-cost scenarios are downstream open gates. No trading deployment, model
promotion, checklist tick, /02 change or profitability claim follows this result.

## Reproduction and evidence

`README.md` gives exact archive layout and commands. `SOURCE_CONTRACT.json`
contains original hashes and lineage. The archive preserves all 36 trained model
binaries and full score/mask arrays; no signed download URLs or credentials are
included. The source ZIP/market tapes stay at their authorized existing sources.
`ARCHIVE_MANIFEST.json` lists every included member's SHA256; the outer archive
receipt is separately generated after packaging. Reproduction uses the supplied
frozen models; a fresh fit must use an empty model directory.
