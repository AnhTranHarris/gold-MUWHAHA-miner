# GRID-0108 — June untouched lockbox / pre-session hourly-and-daily progress check
**Frozen before reading June 2026 original raw quotes, 2026-10-10.**
Purpose: preserve GRID0107 105/105 weekday DAILY movement-capacity improvement, and find whether comparable improvement holds HOURLY, without claiming hourly trading profits, activating sessions/HTF, or introducing physical positions.

## Frozen source genesis (read-only)
- Original Dukascopy source native ms UTC ordered Bid/Ask integer prices /1000. User's original R9 SYNTH remains performance-count comparator, never sign ground truth. Future June R9 SYNTH original 31,801 entries (monthly only).
- Event source unchanged GRID0104: on first tick anchor at midquote, current unique observed quote update spread EWMA alpha=.001; virtual crossing when price shifts >= max(0.75 USD, 1.5×source spread EWMA) from last virtual anchor, one event per tick, anchor updates on crossing even if 7sec output cooldown blocks it.
- K5(t)=abs(mid(t)-latest actual source midquote at or before t-300s)/max(ask-bid at t,$0.10).
- Candidate tiers: broad K5>=2 and high-motion K5>=4.
- Offline-only outcome from first historical quote within 10 seconds after event+120 seconds: whether |future mid-mid at candidate| > 2×observed entry-time spread. The outcome is **not direction/predicted PnL**.

## Hourly audit — no trading-hour routing
- Grid does not use time-of-day; group diagnostic results by **UTC calendar hour containing the event**, never broker/server local hour or selected sessions. Explicitly report all hours, not only business-hour cohorts.
- An hourly paired comparison is eligible if it has >=20 future-valid BASELINE events and >=5 K5>=4 future-valid events. Report exact eligibility fraction against all source-quote-active UTC hours and against all baseline event hours. Do not silently discard weak/quiet hours.
- Count positive, zero, negative paired hour lift and average hour lift. Also report daily paired results using previously frozen GRID0107 date metric (>=100 future-valid baseline events, at least 1 strict event) and all regular weekdays plus Sunday partials. Do not conflate 105/105 weekdays daily magnitude lift with 105/105 positive PnL days.
- Hourly coverage not equivalent to >=75% R9 daily *qualified executable opportunities*; raw counts do not meet acceptance criterion.

## Frozen one new developmental challenge to static K4 (from Jan-May, tested after pre-registration)
- Dynamic prior-feedback grid-only high-tier threshold: observed quote-event K5>=4 **if** causal prior 60-minute event K4-tier Beta-smoothed success rate exceeds prior all-event smoothed success rate by 0.02; otherwise require K5>=5. Prior outcomes count only if event+120s+10s has elapsed before decision tick (i.e. prior event timestamp <= current event time minus 130s); source-invalid 120s horizons excluded. Prior rate smoothing (wins+12)/(eligible+20) = Beta prior 60%, 20 observations. This is not time-of-day routing and uses no future candidate outcomes.
- Frozen choice was examined in original January–May *development* only; June is first untouched out-of-sample test. Do not retune June based on results. Full comparisons must state if dynamic policy failed hourly rate, cost and opportunity count.
- Ignore any apparent positive signed direction from retrospective maximum Buy/Sell oracle; no directional rule has been certified. Do NOT infer future profitable trades or stage-0 full-V1 order readiness.
- Quote-side BUY/SELL at t and t+120s /600s are research controls only; include simple always-reversion, always-continuation averages if scripts permit, with $0.02 fee sensitivity. Those are no positions and no actual fills.

## Lossless scientific restrictions
- June input is reserved independent validation until this prereg document is committed to GitHub on `delta-A-alpha`.
- No lookahead by using 120s outcomes of events younger than 130s; no future 120s outcomes for current decision. At month start prior-feedback policy has no past model state (warmup disclosed; avoid inventing a prior month warmup).
- No traditional Martingale, no fixed hourly time-window routing, no session L1 or HTF L2 onward, no budget $100k account simulation, no MT5 trades, no lookahead in event creation. Original R9/Dukascopy, April research and GRID0107 immutable.
- File hashes for *prior* tested code at lock: `hourly_discovery.py` SHA256 `5dc149194bfe5e00125390d6d44098ae25b1c36a7913de152ec495452aa4e9f7`, `feedback_study.py` SHA256 `11617bca6662a4644c897b8b122cf57b083ca822ef4509c537da60ed31fe8769`; source original event prepare `prepare_events.py` SHA256 `92093f6499f9db808722c098edfd838e637a754f68e49ee34775baefbf866892`. Parameter decisions above fixed BEFORE June original source first opened.
- Independent June pass must report original compressed raw sha256, row count, hourly baseline and dynamic, day distributions, fail hours, labeled event counts, and quote-side directional negative evidence. No silent omission for poor month/hour.
- June will be inspected for validation and cannot be reused as untouched future holdout afterward; July still reserved.

Public reproducible research inspirations (NOT proven performance): https://www.mql5.com/en/articles/21833 and https://www.mql5.com/en/articles/22940 and https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/
