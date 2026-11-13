# Gold MUWHAHAHA Miner R9 v1.94 — Coinexx Model155 MT5 EA checkpoint

**Checkpoint date:** 2026-11-13
**Type:** SOURCE-CHECKPOINT, NOT A COMPILED/PROFIT-CERTIFIED LIVE SYSTEM.
**Branch:** carson/r9-v194-mt5-ea-checkpoint-20261113
**Parent:** carson/r9-v194-m60-155-model-integration-20261113, frozen commit 689cb572c7ca36c78aaea204715fc230b8efe65f
**Critical v1.90 rollback:** 8729a6345655a7b4ea31facc81982004ee2b8921 (not modified).
**v1.93:** also preserved, not overwritten.

## Exact EA source and what works
- Experts/GoldMuwahahaMiner_R9_HybridGate.mq5, #property version 1.94, pinned Git blob 07222b1a3800c9cc826abe10a4ce6afbd97b0af5.
- Experts/GoldMuwahahaR9M60ModelBridge.mqh, pinned Git blob 585d97a63f6ff89f94ae296b6b4ea0013742f517.
- Experts/GoldMuwahahaR9PortfolioGovernor.mqh, pinned Git blob 7e457e1ad5b3a39038a3556857307e193f6248ef.
- Experts/GoldMuwahahaR9M1IndicatorContext.mqh, pinned Git blob cedba0205d198e8f9fb63b67137fd09b111a4be2.
- Experts/GoldMuwahahaR9CashGeometry.mqh, pinned Git blob e4474b60a2febc1c30dfa365454462cde4585bf6.

Baseline bracket, ATR, S1 gate, trailing/timeout, account gross-loss governor, and M1 shadow features are retained. Exact model probability packet lookup occurs *after an original R9 S1-qualified candidate* and *before OpenTrade*. A score never bypasses portfolio risk controls. v1.94 defaults to InpR9M60Mode=1 (SHADOW): entry decisions are unchanged regardless of missing/successful score. Experimental FILTER mode 2 additionally requires the owner to turn on InpR9M60ExperimentalFilterUnlock, supply nonzero prevalidated threshold, disable rescued S1 entries, and use XAUUSD 0.01 quote scaling. These prerequisites do not in themselves certify any filter.

The account-based risk governor was inherited unchanged from 1.93; in small accounts it can independently halt trading and reduce original high volume. Do not bypass it solely to increase classifier-driven fills.

## Full archived approved high-AUC lineage — VERIFY BEFORE PROMOTION

Original archived input: R9_M60_JanSep_FullTraining_155Features_20261113.zip (existing Drive asset, ~1.7MB, no retraining).
- Original approved 155-feature *direct 5-second LightGBM* contains **14** frozen R9 context, **25** selected HFT path summaries, **77** exact event-time trend/quote-derived flow, **23** CUSUM/quote-arrival intensity proxies, **11** Brownian first-passage geometry features, and **5** side/stop/target/spread/action-match features. Exactly 155, in the original run_train.read_month ordering.
- The 77 include 46 event-time trend features and 31 quote-event derived flow/quote-position/QAF features; these are NOT executed volume or market depth.
- Lineage sources copied byte-exact from historic original GitHub research branch into the small checkpoint's lineage folder (17KB total): hft.py, event_engine.py, signal_features.py. SHA-1 original Git blobs: dd475c621a47c7d6eecbcb0454976110cb141f20 / f151abed6abb5f68328f5b451fd5c772abdb5de6 / 5c6710e6b8b1a1c60486e4413de20c82a3c8dfc5.
- Existing archived six direct model artifacts SHA-256 pinned in lineage_audit.py. All are 95-tree binary LightGBM with 155 inputs. Final all-month January–September direct model SHA-256 09e1f1b9514dd18bbf6966055e2c277da3695d43cd4c861f997f5ad2c5d75b2f, **IN-SAMPLE** research only.
- Historic pooled May–Sep retrospective 5s AUC 0.738513, original R9 direction 0.723175; no prospective OOS acceptance and no actual after-cost USD profit conclusion. Later 182 and 237 feature research is NOT part of the approved model and cannot be silently stacked into the 155 inputs.
- Old approved feature families and model snapshots are compared against original archive CRC, archive SHA256 receipts, exact Git blobs, all six model SHA256s, class order, 95 estimators and 155 input dimensions with the checkpoint's lineage audit script.

Run archive verification on a trusted Windows/Python computer (dependencies joblib, lightgbm, numpy, scipy, numba, pandas):

    python research/coinexx_r9_chronological/m60_155_integration/lineage_audit.py --archive "PATH_TO_EXISTING/R9_M60_JanSep_FullTraining_155Features_20261113.zip"

This audit operates on the existing 1.7MB ZIP and the committed small source pins only. It does not download, duplicate, resample or rebuild 72M Coinexx raw quotes or any Dukascopy archive.

## How to compile safely in the owner's Coinexx MetaEditor (NOT executed here)

On a Windows PC with the exact repository checkpoint checked out:

    powershell -ExecutionPolicy Bypass -File tools/Build-R9v194Checkpoint.ps1 -MetaEditorPath "C:\YOUR_COINEXX_MT5\metaeditor64.exe" -TerminalDataPath "C:\Users\YOU\AppData\Roaming\MetaQuotes\Terminal\YOUR_DATA_DIR"

The script uses an isolated R9_v194_Coinexx_Model155_Checkpoint subdirectory in that terminal's MQL5/Experts, stages MQ5 plus four matching MQH, invokes MetaEditor and requires a compiler log with zero errors and an EX5. It does not start or attach EA, use live execution, touch earlier R9 EX5, or download tick data. If stage already contains changed files, it refuses overwrite unless the operator deliberately passes -OverwriteOwnCheckpoint. Verify broker account currency USD if measuring net $1.75; an output EX5 is NOT a performance pass.

MetaEditor64 is NOT installed or accessible in this current environment. No honest claim of a compiled EX5 can be made until the user runs the provided script.

## Most important UNSOLVED dependency: true live source-exact 155-feature scoring
The historical frozen_snapshot.py supplies source-exact model inputs only for **existing previously frozen Coinexx candidate ordinals**; score_snapshot.py loads the real pinned LightGBM weights and writes one atomic score packet, not an ever-growing tick log. This historical single-decision path was tested.
The deployed MT5 engine currently consumes a score packet *if* the precomputed score for the exact incoming quote and original R9 side is already available. The checkpoint does **not** contain a verified streaming live 155-feature producer, a lossless event-ordinal synchronization protocol, or a full strategy tester score replay. Native ADX/EMA/ATR alone do not approximate the 155 input contract. If no matching score, SHADOW keeps baseline entry; FILTER fails closed. The default remains SHADOW, and filter unlock remains false.

A production implementation must obtain all exact raw-quote event features, 60s as-of 500ms path summaries and 14 original R9 context values without future data or quote loss. Source-ordinal mismatch, UTC/server offset and packet latency must be measured and fixed before score can control trade decisions. Do not pretend the high-AUC number has increased net USD/hour.

## Verification completed vs pending
Done:
- Original archived ZIP integrity CRC verified, all six direct model byte SHA256s checked, model dimensions and 95-tree count checked.
- Exact source pins checked against archive, 14+25+77+23+11+5 feature schema inspected.
- GitHub Python tests for protocol/frozen snapshot/static source contract pass in CI; no huge tick caches generated.
- Branch contains executable-source MQ5 + four MQH, a Windows build command, and source-locked provenance receipt.

Pending:
- Actual MetaEditor64 0-error compilation and terminal start, strict broker contract/quote-side stop checks, compile-time APIs verification.
- Full 155-feature historical value parity across frozen R9 ordinal selections and live source-ordinal stream; missing features/quote coalescence must NOT be imputed with guessed values.
- Genuine model original-side probabilities on time during live ticks; latency and missed-score rate; approved training-only threshold.
- Complete Coinexx-only source-ordered after-cost R9 actual-entry/hold/exit replay including gross loss governor, broker fills/fees, hourly net USD, original trade count retained, mean <=30s hold, tail risk, drawdown and chronological future-month certification.

## Policy
This checkpoint is for source preservation, MetaEditor compilation and SHADOW diagnostics. It is not approval to run on a live/funded account, nor a claim that AUC improved actual trades.
Official references:
https://www.mql5.com/en/docs/event_handlers/ontick
https://www.mql5.com/en/docs/files/fileopen
https://www.mql5.com/en/docs/trading/historyselect
