# R9 Priority 1 — Source-exact Coinexx quote path signatures: five-pass receipt

**Research completed 2026-11-13 UTC. STATUS: ALL FIVE ECONOMIC CHECKS FAILED.**

## Immutable source and reproduction

- Python engine parent: `de3e61702759af67f93eb12cff01084789357645`.
- Original R9 HybridGate MQL5 v1.90 blob: `7eecb5f1947017a01ce85b2520725de54749e523`.
- Nine complete original Coinexx XAUUSD raw tick gzip files, January–September 2026: **72,129,347** raw rows in monthly source order, including **49,069** equal-adjacent-millisecond events. All nine source hashes in `results/source_receipt.json`.
- Frozen original R9 quote execution replay: **303,934 completed trades** (297,763 stop, 6,171 timeout), 0 open at the end. This is not certified trade-server fill parity.
- One-pass as-of quote-signature feature extraction (500ms, 2s, 10s, depth 2); original source not sorted, deduped, sampled or overwritten.
- All training labels use the unchanged R9 side's eventual executable-quote liquidation movement. Training label: price move exceeding a modeled 20 one-cent-price-unit per-trade buffer. **Do not treat modeled quote-price proxy as broker-account USD after realized commissions.**

## Chronological passes

| Pass | Train months | Later evaluation | Evaluated R9 paths | ROC-AUC | Selected / all | All mean after modeled cost ($ gold-price) | Selected mean after modeled cost |
|---|---|---|---:|---:|---:|---:|---:|
| P1 | Jan–Apr | May | 31,615 | 0.52665 | 5,293 / 31,615 | −0.42943 | −0.42425 |
| P2 | Jan–May | June | 33,946 | 0.53858 | 8,937 / 33,946 | −0.40757 | −0.40153 |
| P3 | Jan–June | July | 32,536 | 0.53634 | 3,998 / 32,536 | −0.39520 | −0.38976 |
| P4 | Jan–July | August | 31,214 | 0.53786 | 7,126 / 31,214 | −0.40747 | −0.40679 |
| P5 | Jan–August | September once | 33,001 | 0.52983 | 6,815 / 33,001 | −0.40580 | −0.40307 |

- Selected subset thresholds were fixed from the median of training scores, never fitted against the later evaluation month. More stringent training-score quantiles and all daily denominators are preserved in the original full receipts inside the `MT5_EXPAND` result package.
- P1 linear solver hit maximum iterations, retained as failure; P2/P3 use training-only quantile normalization. No identical earlier rejected R9 v2 model was retrained here.
- August outcome-level diagnostic, not a strategy guarantee: observed winning R9 quote paths averaged about +0.219 gold-price after modeled cost; losses about −0.531. Their conditional mean magnitudes imply a break-even win rate around 70.8%, while only 15.9% of frozen R9 entries cleared modeled cost.
- P1–P5 each evaluate a DIFFERENT month; AUC figures are not paired estimates of incremental improvement. Even the most favorable selected subset remains negative.

## Frozen nine-month refit

After P5 had been evaluated on untouched September, the full nine-month dataset was used for a separate **SHADOW-ONLY UNAPPROVED** model refit (`full_fit.py`). This model contains all nine training months and has no unseen post-September validation. It is not a usable profitability-certified trading policy.

## Durable artifacts

- Complete five-pass source, models, daily check receipts, hashes and full nine-month refit: https://drive.google.com/file/d/1KfDhOvrX0_R8a8fCYhxTQZU5NBnHJY-8/view
- Reusable source-ordinal, as-of candidate feature cache (NOT the raw ticks): https://drive.google.com/file/d/1Kkdrh-IYrTmjNS2tpBgJDq9SKrfeFewa/view
- Original nine complete raw source files stay at `Micro_account/gold_mt5_tick_all`, not replaced by derived cache. Source-internal quote units are price cents; original data remain authoritative.

## Decision

No Priority-1 path-signature model passes the positive real-quote expectancy requirement, let alone the high-frequency, drawdown and broker-fill prerequisites. **Do not merge into R9's EA, demo, or live execution.** A substantively new experiment should investigate subsecond first-passage adverse selection and the spread/stop geometry before considering a model of order-event intensity. Preserve these negative results and avoid re-running identical experiments.
