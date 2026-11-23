# R9 HybridGate V7 — Event-Family Research (2026-11-23)

**Status: heavy nine-month in-sample research ONLY; acceptance FAIL. No approved or native-MT5-compiled EA.**

## Immutable source and recoverable implementation

- **Upstream R9 v1.90 source:** `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`, immutable blob SHA `7eecb5f1947017a01ce85b2520725de54749e523` on branch `carson/mt5-r9-hybrid-gate-certification`.
- **V6 research-only MQL5 files remain unmodified in this branch**: `Experts/GoldMuwahahaMiner_R9_TickBridgeV6_Research.mq5`, `Include/R9HybridGate_TickCandlesV6.mqh` and `Scripts/R9HybridGate_CoinexxTickCandleAuditV6.mq5`. Default experimental trade actions are disabled.
- **Complete V7 research executable source, 120-tree model, training/export scripts, full nine-month receipts, checksum manifest and continuation document:** [MT5_EXPAND source-only archive](https://drive.google.com/file/d/15sr5-gvdGnNqhXxr7vInLDGOJrFZVsgq/view). ZIP SHA-256: `97173873e40306167595cae0fe03de6f1180bf91dc88a990c86d4f2eba8ba228`. ~128 KB, 41 payload files; no duplicated raw ticks.
- C++ source files in that archive: `r9_hybridgate_v7.cpp`, `r9_hybridgate_v7b.cpp`, `r9_hybridgate_v7c.cpp`, `r9_hybridgate_v7d.cpp`, `r9_hybridgate_v7e.cpp`, and `r9_v7_value_model.hpp`. **These C++ V7 files are in the preserved archive, not yet checked into this GitHub branch.** Do not claim a native MQL5 V7 port.
- Nine months of original Coinexx TickLogger data must be fetched from PRIMARY Drive, files `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz` for MM 01–09. Frozen merge is a supervised historical research reference, not a causal trade clock.

## Actual R9-derived on-policy results

| Mode | Jan–Sep actual Coinexx trades | Fee-inclusive modeled net | Months meeting >=90% frozen R9 net |
|---|---:|---:|---:|
| Original R9 causal source replay | 303,298 | -$65,367.16 | 0/9 |
| V7B two-phase early/late minute R9 | 180,684 | -$41,035.98 | 0/9 |
| V7C strict nine-month **in-sample-fitted** R9 entry router | 2,697 | +$819.36 | 0/9 |

The positive fitted result is NOT deployable profitability: it is sparse, in-sample, broker execution and floating margin risk are unmodeled. The R9 cycle, completed source tick candles, as-of entry qualification, 1s/5s/15s state and same-minute rearm were retained in replay.

V7D intrinsic-time directional-change and V7E conditional same-side rearm were additional targeted mechanisms, not promotions. Tested subsets were economically inconsistent.

## Quality assurance and next mechanism

- Original R9 Jan ledger disabled-mode SHA256: `348aad4437afcd19b7bee248640a8e265ce954aae413b8fc4f86cd2287eb4fed`; V7 engines reproduce source baseline with research switches disabled.
- All **72,129,347** underlying raw Coinexx quotes covered by nine-month replay, 9/9 raw gzip source SHA256 matches in source receipts.
- C++ frozen model vs Python predictions: 24/24 parity samples.
- Conditional source-prefix non-anticipation: first 2,970 January closed trades identical between truncated future suffix and full source under fixed trained model.

**Next implementation, not completed:** Expand R9 within the original minute-cycle bracket/rearm state machine to create distinct initial break, overshoot, sweep/reclaim, late continuation, losing opposite rearm and profitable persistence *candidate states*. Apply source-clock forward first-passage and action-value modeling across 8/18/30s lifecycles, then full nine-month on-policy replay. Refine unsuccessful mechanisms by quote-path diagnosis; no trade-ID matching or bulk source regeneration.

**No branch merge and no production order switch.** Native MT5 compilation and independent Strategy Tester real-tick validation remain undone.
