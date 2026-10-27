# F401-R48T — strict frozen month-forward broker-excluded quote replay, UNAPPROVED (2026-10-27)
Existing XAUUSD FILTER08 M-DK-01 original governor v1.4 + 1.5-A1/A2/A3. No new checklist acceptance, source clock change, engine rebuild, approved filter or live orders.

Follow-on to R48 frozen source training only. Source Coinexx model trained Jan antecedent/Feb scoring, then untouched weights/cutoff applied to Feb, June and July on BOTH Coinexx and **excluded** Dukascopy. Other source Dukascopy January-fitted frozen weights/calibration scored Feb/June/July both broker quote streams. All twelve masks built from genuine original source-native first quote in [t0+15000, t0+16000) for **never submitted and still unfilled pending intents**. Every model trained without target month outcomes or excluded-broker labels; previous matured events at t_prev+33001ms only. Earlier historical 2026 data had been seen by project researchers, not virgin blind. January source scored **last20% only**, not full month.

Frozen model CX→CX Feb 23306 wrong/1215 good, June 13536/340, July 12062/313.
Frozen model CX→DK excluded Feb 8519/238, June **6526/97 (67.3:1)**, July **4195/45 (93.2:1)**.
Frozen model DK→CX excluded Feb 37349/2872, June 24548/1011, July 20094/702.
Frozen model DK→DK Feb 23651/1311, June 16650/542, July 11834/290.

Jan tail + Feb/June/July (partial Jan denominators): CX→CX 53153/2170, CX→DK 20455/414 (49.41:1, STILL <50), DK→CX 88810/5357, DK→DK 56312/2452. None reaches >400000 wrong and >50:1 each four-month broker. Source exact 12 .npz masks, 12 per-hour/side placebo and R40 overlap verified. DK June positive R48 cross has 250 unique bad/7 unique good relative to own R40, DK July 58/1, but huge wrong readmissions. These are **narrow historical positives**, not whole-system synergy nor original M-DK-01 acceptance.

Full immutable source code, frozen-before-transfer plan, 12 original event ID/decision-clock class masks and exact SHA manifest: MT5_EXPAND /01 https://drive.google.com/file/d/11ZcMGt59Y5d4FGZVlPXZz51_mQyeVP-5/view. 36,393,332 bytes, SHA256 188e87f453d9cc778c57bfd6e85a03ceee7247c6d9a6f9065077aa66fda6e8cb, cloud raw readback byte hash and all 20 ZIP CRC / 19 SHA members PASS. Detailed science https://drive.google.com/file/d/102FNXG_GQ_UQ26cH6tcMGk8b6Mo_sry_/view.
R46/R47/R48 parent source exact https://drive.google.com/file/d/1wORdSy_ZrcKZv5yz1w98XoQIlN9RpzHz/view, SHA 942dbbe8ffb809135b271ab187d15838e84cba19622a7b84f979fb8aad4da208.
Actual Python files/weights/masks are inside the authenticated Drive source ZIPs, not separate files committed under GitHub branch. This GitHub document pins original sources exactly.

No MetaEditor compile, Python↔MQL5 parity, 4178 R9 supply quotas, real fill/opportunity test, demo order veto, broker demo forward, or shared-capital aftercost risks established. G01–G09 all OPEN; M-DK-01 OPEN; original checklist 21/39 historical research owner approval unchanged. Next R49 genuinely distinct: source-authorized t0 true pre-OrderSend execution/opportunity-aware classifier and conditional cooperative correct-protection, no target month selection based on DK June/July positives. Owner approval not inferred.