# V2 F1 / High-Throughput Multi-Session Grid — January Research Chassis

**2026-10-15 | Owner project: Gold MUWHAHA Miner | Branch `v2-f1-january-research` | EXPERIMENTAL ONLY — NO TRADING DEPLOYMENT**

## Mission / improved research specification

Design a structurally new F1-class **tick-first execution chassis** for XAUUSD instead of repeatedly retuning an underperforming V1 source signal. The system must deterministically read the ordered original January Dukascopy Bid/Ask quote stream, synchronize its M1/M5/M15/H1/H4 (and S1/S5/S15/S30) completed-state hierarchy without hindsight, and arbitrate competing *virtual* grids across Sydney, Tokyo, London, and New York under **one real-funded-account position governor**. It must support R9's high-frequency minute-bracket/rapid-rearm behavior as an observed research hypothesis, but never assume MT5 synthetic `Every tick` prices, fixed broker spread, or R9 future results are executable Dukascopy signals. Evaluate *realized daily and hourly cash, gross loss, marked-equity drawdown, risk halt, fills, and turnover* against the actual $100 starting R9 SYNTH historical reference. Repeat structurally different integrated experiments, retain failures and complete hashes, and never promote a configuration below the owner's absolute joint acceptance standard.

## F1 architecture (research implementation)

| F1 metaphor | Trading infrastructure | Code |
|---|---|---|
| **Track telemetry** | L0 ordered UTC original Bid/Ask and first observed executable quote, timestamp precision | `load_source`, `StreamingF1.on_quote` |
| **Telemetry acquisition / RPM** | Completed S1 movement, price-path efficiency, acceleration, turns, quote updates, no invented empty ticks | `micro_features`, `StreamingF1._micro_quality` |
| **Track map / GPS** | Current observed minute origin, last **completed** M1/M5/M15/H1/H4 and ATR(14) | `prev_frames`, `Candle`, `Snapshot` |
| **Pit crew / race strategy** | Four simultaneous DST-aware sessions; multi-regime admission and risk ownership | `_session_policy`, `_permit` |
| **Gearbox** | Eight independently defined virtual grid idea families; one genuine funded trade at a time | `generate_sources`, `execute` |
| **Launch control** | Exact R9-inspired minute-frozen mid-brackets, completed S1 entry quality, opposite-direction intraminute rearm after actual funded close | `execute`, `candidate_bracket` |
| **Brake/traction controller** | Spread/latency/drift, stop-target-trail, bounded hold, no martingale, 60%-equity halt | `execute` L6/L7 |
| **Lap telemetry** | Every completed physical deal, every 744 UTC clock-hour/31 date including zeros; separate R9 tester-clock comparison | `v2_source_and_r9_audit.py` |

The V2 module is a **new, internally integrated research chassis**, not a claim of full audited drop-in compatibility with `FourSessionV1`. Exact V1 source files and hash manifest are included in the evidence archive; V1 remains unmodified. Migrating each accepted older native subgrid and broker transaction genealogy into V2 will require subsequent source-by-source parity testing. Its virtual research entries are **not** independent funded or hedged positions.

## Original evidence hierarchy

- Governing owner January QC law: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit
- Source pin Git original V1 parent implementation tree SHA `c22f955314206ec457856e633b349549d9386a69`, current scientific `J0183`, trading OFF.
- Institutional ten-page January R9 quantitative report: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/R9_JAN2026_INSTITUTIONAL_QUANT_REVERSE_ENGINEERING_SOURCE_OF_TRUTH_10P.md
- Exact original Coinexx generated `Every tick` M1/M5/H1 and M1 logger: https://drive.google.com/drive/folders/1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF
- Original January Dukascopy Bid/Ask source sha256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, 9,135,062 ticks. Pinned original source already in owner's Google Drive.

MetaQuotes documentation of **generated versus actual ticks**: https://www.metatrader5.com/en/terminal/help/algotrading/tick_generation . MT5 `OnTick` may coalesce incoming NewTick events while an event is already in flight: https://www.mql5.com/en/docs/event_handlers/ontick . Any eventual MQL5 implementation needs timestamped `CopyTicks` replay/catch-up, tick-loss audit and broker verified fill/stop evidence, not blind assumption that every observed live tick will be delivered to `OnTick`: https://www.mql5.com/en/docs/series/copyticks .

## Reproducibility

From repository source (not suitable for deployment), with January original data at exact source path `/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`:

```bash
python v2_f1_integrated.py                  # 1 R9-inspired control + 1920 structurally different whole-funded-book replays
python -m unittest discover -p 'test*.py' -v
python v2_original_feed_stream_parity_qa.py # 180k original quote independent streaming/batch parity
python v2_source_and_r9_audit.py            # original Bid/Ask 1:1 tick/price/deal audit & 744h/31d reference
python v2_research_capacity_diag.py         # separate $1M UNFUNDED DIAGNOSTIC throughput only
```

- No future/current unfinished OHLC injected as signal features.
- Funding research assumptions: `$100` initial account, fixed `0.01` lot assumed `1 oz`, leverage `1:500` assumed, `$0.20` round-trip fee assumed, 250ms minimum observed quote admission, one physical position maximum, stop adding new risk below 60% initial equity. These are **not confirmed Coinexx contract semantics**.
- The engine stops a historical funded run when its account has no position and irreversible entry halt is reached; all subsequent zero hours are recorded in the 744-hour and 31-day investor comparison.
- Exactly **1,921** initial structural `$100` experiments; none meets **60% of R9's contemporaneous hourly or daily net goal**. These are ***internal negative research***. No relative percentage to weaker previous Python baselines can be called a success.
- The **separate** high-capital 12-run diagnostic only tests throughput/software scheduling. Its profits/losses have NO direct $100 investor interpretation, and none of its outputs can qualify as a successful investor backtest.
- Stream-vs-batch parity verified on 180k original quotes, 206495 M1/M5/M15/H1/H4 state checks and 41275 completed S1 microstate comparisons, zero mismatches. Independently all 27 native control closes found exact raw original entry and exit quotes (27/27), zero chronology/cash errors.
- No certified broker UTC offset; `+2h` is an explicitly unverified offset used only for the *report-clock comparison* (raw quote UTC remains immutable).

## Scientific disposition / next engineering gate

**Infrastructure candidate, not profit candidate.** V2 can ingest a high-volume quote tape and derive the cross-timeframe decision clock. It does **not** yet have a profitable full-account microstructure source at the investor's $100 costs. It has not been exported to MQL5, undergone broker real-tick validation, passed original full V1 genealogy/MT5 stop/freeze/contract audits, or received owner deployment approval. Do not automatically promote or trade it. V1 J0183 stays unchanged; August remains SEALED.

## Preservation contract

The companion full ZIP includes every local V2 helper, research source, SHA manifest, original-trade ledger, 1,921-case structural sweep, 12 extra software-throughput diagnostic records, all original-source QA, 744-hour and 31-day scorecards, stdout/error logs, Python caches, and selected original V1 bridge inputs. Never delete or overwrite negative configurations to make acceptance look better. The source repo branch is **additive and segregated**, with an explicit SHA to the V1 parent tree.
