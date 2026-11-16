# Micro180 V11 — independent dual-basket entry reconstruction

**2026-11-16 | research fork | actual merged CSV inspected | native/demo/live unchanged**

## Source-exact scope

The **existing** 11,233,746-byte R9-SYNTH→original Coinexx TickLogger merged
CSV in primary TRADING_RESEARCH was opened and its gzip SHA-256 verified:

- SHA-256: 9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5
- Original R9 teacher: 272,352 trade rows; 192,487 first legs,
  79,865 opposite second legs; 192,487 unique minute-cycles
- Source entries mapped <=2 seconds after NEXT full-second mark: 271,544
- Trade windows with entry AND exit both within original lag rule: 270,776
- Original historic SYNTH net: +$360,693.05 (unchanged)
- We have NOT run an independent 71,794,750-row Coinexx source quote replay
  in this GitHub branch. Do not interpret CI fixtures as that verification.

## All 9 months: three substantial original historical cycle families

| Original *ex-post* family | complete cycles | original R9 net | first entry median second | first entries by 5s | second-entry median |
| --- | ---: | ---: | ---: | ---: | ---: |
| A: single-leg directional persistence | 112,622 | +$187,569.57 | 20 | 18.20% | n/a |
| B: favorable first leg, developed reversal, favorable second leg | 53,094 | +$138,198.20 | 2 | 85.93% | 27 |
| C: adverse first leg, rapid recovery, favorable second leg | 24,592 | +$35,460.16 | 5 | 51.75% | 23 |

Remaining two-leg sequences are the historical failing complement and are
retained for whole-population denominators and full accounting; no negative
family is promoted to a profitable trading mechanism.

R9 first-leg all-family cumulative early entry counts:
0s 5,557; <=3s 55,653 (28.9%); <=5s 80,680 (41.9%);
<=9s 107,986 (56.1%). Requiring 5-second/15-second current basket
maturity imposes artificial early-minute rejection.

For B and C the available mapped *post-second* quote marks show median
exit→opposite-entry intervals ~17.924s and ~4.926s, respectively, with
median toward-opposite midpoint/quote movement ~$0.24 and ~$0.07.
These differences are RETROSPECTIVE market characteristics, not evidence a
proposed realtime reentry classifier can predict future second-leg success.

Source-aligned features "source_s1", "source_eff", "source_atr" in the combined
CSV are attached to the subsequently mapped quote event. Do NOT assume they
were available at the synthetic entry time. V11 instead computes its own
S1/ATR and basket features strictly from previously received Coinexx quotes.

## Rebuild performed on isolated research branch

* Original V9/Micro180 four-lane 5s/15s basket x 15s/30s breakout architecture
  is retained as *bounded, live as-of* 180-second quote observations.
* V11 overrides both R9's entry controller and minute-start anchor routine.
  Its own dual-basket seed stage has a causal midpoint bracket at the first
  actual quote of the minute, immediately permits early evaluation, and
  calculates R9-equivalent displacement/efficiency/turning/range from already
  completed Bid seconds in the Micro180 rolling ring.
* The original source-shared M5 ATR, spread/session qualification and
  quote-based position order are preserved as common *causal plumbing*.
* Every entry includes 5s AND 15s current-basket displacement/observed span,
  four 5/15x15/30 historical breakout-lane evidence, quote ordinal, Bid/Ask
  execution side, S1 trend and regime/volatility qualification.
* A first-leg entry is tagged only by its AS-OF market phase: early probe,
  transition or mature directional. No future cycle result is known.
* When a first position closes, V11 can distinguish an ALREADY observed
  favorable or adverse first quote exit before the opposite-side entry and
  observe the flat interval. This is not the eventual "WIN_WIN"/"LOSS_WIN"
  teacher label and does not predict the second leg.
* Maximum two legs per original entry minute, matching the existing teacher's
  two-leg campaign structure. No open pyramiding or extra order lanes.
* Exit behavior is deliberately held fixed to the R9 common state machine
  in this **entry-identification** gate. Stop/target optimization cannot be
  mixed into entry recall certification.
* Only a separate research Python class is added. V9, native MQL5, risk
  governors and trading accounts are untouched.

## What 'same entry' must actually mean

The original R9 SYNTH event clock is whole seconds. The merged Coinexx mapped
price is observed from the first REAL quote strictly after the NEXT whole
second. Those are different times. Therefore four independent measurements
are mandatory:

1. **Opportunity identity:** source minute + leg + BUY/SELL; count all
   original reference rows and ALL additional V11-only entries.
2. **Original R9 entry second:** whether the independent V11 price-trigger
   occurred in the same original teacher second.
3. **Mapped quote time:** V11 millisecond time minus the post-second quote
   mapping time. Do NOT falsely require both this timestamp AND the earlier
   teacher second to be identical.
4. **Executable Coinexx price distance:** absolute V11 BUY Ask or SELL Bid
   cents from the stored mapped quote price. Report exact, <=1c, <=3c,
   <=5c and <=10c, with median and p95; no fabricated execution fills.

All are stratified by historical A/B/C family **after** the independent replay.
The first entry's eventual teacher net and future WIN_WIN/LOSS_WIN class are
NEVER used in the entry or reentry decision.

## Current verification

- Deterministic offline CI tests verify that the V11 entry method does not
  call the inherited R9 _process_entries method and that it matches the
  source-faithful R9 reference's first/two-leg source quote/time/side when the
  same R9 parameters and executable test quote stream are supplied.
- Early entry can occur within 44ms of an independently anchored source
  minute even without matured current 5s/15s baskets.
- Unit tests verify no future-relabeling, as-of first-leg recovery/favorable
  classification and two-leg cap.
- The merged entry comparator now reports full 9-month, per-family entry
  recall, same ORIGINAL teacher-second recall, post-second quote value
  difference and extra candidate counts, preserving original teacher net.
- Those are programming contracts, not full market results or native compiled
  MT5 parity.

## Full research replay, no data rebuild

Run ONLY with already existing original Coinexx REAL TickLogger file parts and
the existing original merged CSV, in exact chronological source order:

    cd research/coinexx_r9_chronological
    PYTHONPATH=src:variable_cash_horizon_20261114:dual_basket_20261114:micro180_20261114 \
      python micro180_20261114/run_v11_independent_merged_concordance.py \
        --ticks /existing/TickLogger_part01.csv.gz ... /existing/TickLogger_part10.csv.gz \
        --merged /existing/r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz \
        --clock-offset-minutes VERIFIED_SOURCE_OFFSET \
        --full-nine-months \
        --out-json v11_compact_entry_concordance.json

One streaming pass, compact summary only, no alternate fee or historical
trade revaluation, no duplicated tick libraries, no training on future labels.
All nine months must be covered. If the autonomous entry match is materially
below target, diagnose early/late basket state, R9/real source clock alignment
and incomplete quote windows, then change the **independent micro180 entry
engine** on this protected research fork only.

**Release gate:** an achieved same-second and executable-price concordance
across all original mapped entries, high independent entry precision, and
stable A/B/C recall must be measured before any independent exit/rearm policy
is enabled or a native MT5 research EA is changed. There is no claim that a
real-tick causal system can guarantee every original synthetic entry at the
future quote-mark value. Full-system profitability is a separate gate.
