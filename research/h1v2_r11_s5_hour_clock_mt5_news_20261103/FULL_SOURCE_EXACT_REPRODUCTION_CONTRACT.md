# H1V2 R11S5: exact month / UTC-day / UTC-hour market clock and historical MT5 calendar contract

## Non-optional original science and preserved source

This document is NOT a replacement for the original complete 233k+-character R11 append-only ledger, original complete H1V2 R11 full forensic audit, original R11S1 15s/30s source labels, R11S2 36 fitted failed student policies, R11S3 UTC clock-corrected all-hours policies, or original R11S4 145,401 selected quote-ordinal traces and full 2,880 hour records. The original 15-second favorable threshold, 30-second no-adverse threshold, 30-second position occupation, source-quote time chronology, original teacher fee and original v5 15-second drought/300-second warmup eligibility are completely unchanged. No MT5 EA entry/exit/stop logic was modified. No model was trained or refitted from unseen source data in this stage.

Original standalone R11S4 branch: `carson/h1v2-r11-s4-exact-optimal-hour-day-month-20261103` @ `897ae6217874296fbc065089e5e138a0ec0bb43b`.

Exact original 4-month combined ZIP: `https://drive.google.com/file/d/1C7b-T4hb5eaPY_IUQrCO2M8-fHPfXgpy/view` SHA-256 `fba5a62a4d77d09450a9ac00522cff2532664a5e4d466573cb2a5694bec711fc` (7,190,462 bytes, 33 members, CRC pass).

Original 2,880 UTC hourly input `R11S4_ALL_2880_COMPLETE_UTC_HOURLY_SOURCE_QUOTA_RESULTS.csv` SHA-256 `cfabfecd9ea57d05d806eb16922f20789e0ea75a77111785d0de565fc6c64542`, length 397,902 bytes, source link `https://drive.google.com/file/d/1fPzBjBCoUlA46eDyf_HIjy72sPBmCZ-K/view`.

Original 120 UTC day source `R11S4_ALL_120_COMPLETE_UTC_DAILY_SOURCE_QUOTA_RESULTS.csv` SHA-256 `300fddb83b563e439b2006957513242c3b732ba60495d176222b001475e6557a`, 6,464 bytes, link `https://drive.google.com/file/d/1C8wndnbgmxvscYpeN8wrSTtQuUpjf6q3/view`.

Full original preserved entry trace, 145,401 source exact rows: `https://drive.google.com/file/d/1ymwmsL3fnk5FnBpEeZCdYcHf1gQZj7Cd/view`.

Mathematically impossible fixed-contract hour source witnesses, 246 exact rows: `https://drive.google.com/file/d/1Oaf7l-8XDNpoY2vESVlFb2QEqcdS0Rzx/view`; impossible date records, 14 exact rows: `https://drive.google.com/file/d/1Htxda7N880VvvVbl-NnuvBJiQKr_v30P/view`.

R11 source audit (full): `https://docs.google.com/document/d/1KhPl9eZqUJZM8vh7W8n93tUQWwbLXhMhcPZDXEN909E/edit`.

Complete R11 append-only ledger: `https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit`.

## Actual new stage and reason it does not repeat prior S4

The new R11S5 stage attaches exact historical IANA timezone session states and a separate, independently verifiable broker/MT5 news-data interface to **each** of the original 2,880 UTC hours. The original 16 source hourly columns remain in the output unmodified. Output includes per-hour Australia/Sydney 08:00-17:00, Tokyo 09:00-18:00, London 08:00-17:00, and New York 08:00-17:00 nominal business-session minute counts. These are conventional **research windows**, not claimed exchange regulatory opens, actual Coinexx/XAUUSD order authorization or user-prop-firm policies. Session start/stop calculations use `zoneinfo` for local IANA DST on the actual source timestamp, not fixed UTC summer/winter hours. Multiple sessions may overlap; do NOT classify them as mutually exclusive.

For each source hour also record `next_open_min`, `next_close_min` for each named nominal session, overlap >=2 and >=3 sessions in the 60-minute block, source Chicago wall clock with both fall DST folds distinguished by UTC, and original R9 SYNTH exact hourly reference, original selected strict-future-privileged R11S4 entry count and original upper bound (all unchanged).

Broker trade permission is always `UNKNOWN_NEEDS_HISTORICAL_MT5_SESSION_SOURCE` unless a genuinely historically valid broker-specific rule is ingested. `SymbolInfoSessionTrade` and `SymbolInfoSessionQuote` export current terminal weekly sessions; these alone do NOT reconstruct holiday closures or past XAUUSD-specific sessions. Prop-firm or user-defined operating hours remain `UNCONFIGURED_NEEDS_OWNER_RULES` until explicitly established. Research session names NEVER override these states or become a hard live entry gate by themselves.

All 120 UTC days are independent, atomic, readback-verified output chunks: `outputs/2026-MM/days/YYYY-MM-DD_ALL_24_HOURS.csv`. After daily writes complete, each of the four months has one full CSV with all original source fields + every new clock field, a machine JSON containing all 24 UTC hour group records and every date source hash, and completion manifest containing input SHA and output SHA. Any interruption after a day checkpoint can recover that day's full 24 hourly original and enriched entries instead of losing the month. The final four-month exact ZIP includes all 120 day CSVs and four monthly CSVs and reports; no monthly average substitutes for row detail.

## Original exact fixed-contract source results (unmodified)

| Source month | UTC calendar hours | UTC dates | Original R9 SYNTH UTC corrected reference | Original R11S4 future known strict 15s/30s entries | R9 SYNTH-active hours | All theoretically attainable hour quotas met | Mathematically impossible hour quotas |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jan 2026 | 744 | 31 | 27,980 | 35,652 | 480 | 430 | 50 |
| Feb 2026 | 672 | 28 | 33,523 | 33,640 | 458 | 307 | 151 |
| Jun 2026 | 720 | 30 | 31,758 | 40,296 | 497 | 470 | 27 |
| Jul 2026 | 744 | 31 | 24,324 | 35,813 | 482 | 464 | 18 |
| Total | 2,880 | 120 | 117,585 | 145,401 | 1,917 | 1,671 | 246 |

Do not replace corrected UTC June 31,758 or July 24,324 reference with the old server-month 31,801/24,382 without redoing historical source clock alignment. Neither a faster tree learner nor a future-privileged oracle can meet the 246 mathematically impossible R9 hourly quotas without changing the strict source definition, allowable temporal occupancy, or source opportunity population. The owner explicitly does NOT authorize changing the entry survival objective or R9 hold/exit conditions in this stage.

## Exact commands

Python 3.11+ dependencies `pytest`; standard-library production S5 modules (`zoneinfo` database must contain IANA history); MQL5 exporter executed only in separate Windows Coinexx/MetaTrader5 terminal:

```bash
PYTHONPATH=src python -m pytest -q tests
python -m compileall -q src tests
PYTHONPATH=src python -u src/run_hourly_clock.py \
  --source-hour /mnt/data/R11S4_ALL_2880_COMPLETE_UTC_HOURLY_SOURCE_QUOTA_RESULTS.csv \
  --source-day /mnt/data/R11S4_ALL_120_COMPLETE_UTC_DAILY_SOURCE_QUOTA_RESULTS.csv \
  --months 2026-01 2026-02 2026-06 2026-07 \
  --out outputs
```

Each source CSV must pass its original SHA256 before the script writes **anything**. It verifies 2,880 hourly and 120 daily records, exact UTC hour uniqueness, no missing hours, every day exactly 24 hours, each month independently 744/672/720/744 hours, original hourly and daily reference equality, source selection <= original independently optimistic hour upper, and exact feasible/impossible partition. It emits 120 original source-day chunks, four full-month CSVs, four month research JSONs and one overall completion JSON.

No live MT5 calendar access exists in the local Python environment of this run. Therefore the published complete clock results have exact explicit `UNKNOWN_NO_VERIFIED_COMPLETE_HISTORICAL_EXPORT` for **all 2,880** rows and never turn absent news into zero. Actual USD/non-USD medium/high influence has NOT been measured. No future macro release time, actual/forecast or revised value has been invented.

## MT5 calendar acquisition and historical UTC mapping

Official MetaQuotes Calendar API uses `TimeTradeServer` broker time rather than UTC, and `CalendarValueHistory` supports bounded server-time date windows. `CalendarEventById` yields importance, time_mode, country and event description. `SymbolInfoSessionTrade`/`SymbolInfoSessionQuote` give weekly session metadata from the currently connected broker. MetaQuotes explicitly documents the Calendar API is unavailable in the MT5 Strategy Tester (4014); export from an online chart and replay from files. References:

- https://www.mql5.com/en/docs/calendar/calendarvaluehistory
- https://www.mql5.com/en/docs/calendar/calendareventbyid
- https://www.mql5.com/en/docs/marketinformation/symbolinfosessiontrade
- https://www.mql5.com/en/book/advanced/calendar

The research-only script `mql5/R11S5_ExportMT5Calendar.mq5` makes no trades. Put it in the connected MT5 terminal `MQL5/Scripts`, compile with MetaEditor and invoke as a SCRIPT on an online XAUUSD chart for each of the four original server-calendar months. Configure exact `InpStartServer` and `InpEndServer` separately, `InpCurrencies` and 24hr chunks; it writes original server-time medium/high releases (incl. value_id, event_id, country, currency, time mode, event name and raw MILLION-scaled actual/forecast values) and a separately named `*_STATUS.tsv` with each query return status and a final `COMPLETE` marker. It records current quote/trade session schedules as a separate `*_SESSIONS.tsv` current snapshot, NOT as a historical schedule. Any query error, metadata failure, invalid date, or tester invocation invalidates the export; never interpret a partial export as a news-free hour. **The script has not been compiled or run on MT5 in this research container.**

To convert a historical MT5 event server timestamp into an original source UTC instant, the Python adapter requires a separate `verified_server_offset_map.csv` with columns `from_utc,to_utc,server_utc_offset_min,broker,verified_evidence`. These must be historically verified for the **calendar provider's terminal**, not blindly copied from current `TimeTradeServer-TimeGMT` or R9 SYNTH tester timestamp assumptions. Missing, ambiguous, overlapping or unverified historical time ranges reject the news join. `CALENDAR_TIMEMODE_DATE` and `TENTATIVE` have no precise release instant and must not be assigned to an hourly bin as an exact published minute.

When a full verified historical export is eventually provided, `mt5_news.py` can join medium/high source timestamps with hourly windows and distinguish before/during/after. A retrospective backfill contains final actual/forecast/revision values that may not have been visible before the announcement; these must be EXCLUDED from causal pre-news model features until independent point-in-time snapshots exist. For that reason the output remains explicitly `RETROSPECTIVE_VERIFIED_OFFSET_NOT_POINT_IN_TIME` even after a complete historical export. The source script includes `mt5_pre_release_asof_actual_allowed=0` as a fixed no-leak condition.

## New hourly specialist mechanism hypotheses (never confuse with completed fits)

1. **Hour-boundary context router**: condition an *as-of* 250ms first-passage specialist on time-to-local-London/NY/Tokyo/Sydney open/close and actual broker session if historically proven; do not use future-known original R9 hourly counts or S4 strict entry labels as input. Compare pre-registered session transition model versus plain R11S2 controls with the source labels separated.
2. **Overlapping-session pressure decomposition**: independent time-to-session transition and overlap exposure for each hour. The one-hour overlap statistic is not a genuine order book or signed volume; any alpha claim requires raw source 15m/30s mark history and full first15+full30 label tests.
3. **News conditional competing risks**: after real exported MT5 schedule and verified historical broker clock, train a causal *preannouncement* hazard using only scheduled importance, currency, last known timing, minutes to event, as-of volatility/gap/spread; separate post-announcement actual-value news-surprise head only if point-in-time timestamp audit exists. Absent calendar -> UNKNOWN, prohibit hard veto and fabricated news-free label.
4. **Regime-specific expert training**: new specialists indexed by session/overlap, source quote event/rapid spread transition, and continuous time to major session open/close; calibrate BUY, SELL, WAIT and right-censored 15s favorable/30s adverse paths independently; no forced volume, no lying about the 246 impossible hours. Each specialist requires enough independent time blocks, frozen model weight/feature hashes, and unit/economic controls.
5. **Economic unknown-state uncertainty head**: a missing MT5 calendar is an explicit missing-feature domain, not zero news; any statistical learner that treats absent months as zero news is invalid. Compare exposure stratification only when news is documented. Current baseline is unknown for all 2880 hours.

These are scientifically new conditional hypotheses; NOT completed profitable/accurate fitted models. The original R11S4 hindsight upper bound is already optimal under the fixed first15 favorable / full30 no-adverse 30s occupancy constraint. New models must not be claimed to raise that mathematical bound; they can only attempt to infer it more reliably using as-of covariates, or document why an hours-of-operation veto is warranted when the human owner supplies restrictions.

## Original source invariance and anti-amnesia

Every created file in the R11S5 ZIP is hashed in the internal complete SHA256 manifest. The outer ZIP SHA and online Drive remote MIME/size/IDs are recorded in the original append-only Google Drive log. GitHub source changes must be on the isolated S5 child branch of original source-exact R11S4; commit only newly added S5 research paths; original historical science and MT5 EA unchanged. On a new chat, read original entire ledger, full original 15-finding audit, original R11S4 archive and negative S2 policies, then source-specific S5 ZIP and its manifest, before running an additional learner. Never replace original source arrays or skip failed experiments to present a more favorable result.
