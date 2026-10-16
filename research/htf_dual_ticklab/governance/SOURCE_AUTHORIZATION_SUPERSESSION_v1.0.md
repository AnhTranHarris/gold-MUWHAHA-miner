# Authorized Sources — Explicit Supersession Record

**Record:** `XAU-HTF-SRC-002` · 2026-10-16 · supplements older `SOURCE_LOCK_AND_DECISION_LEDGER.md`; does not delete it.

## Why this exists

The older freeze document states "Dukascopy excluded" because Dukascopy files had not yet been explicitly authorized when that version was written. The user subsequently supplied the **specific Dukascopy Jan–Jul 2026 Google Drive folder** as the second broker feed and instructed us to build and use a separate Dukascopy Python backtester. The exclusion in the earlier handoff is therefore **superseded exclusively for those seven supplied files**. The anti-contamination rule itself stays in force for all other unapproved sources.

## Currently permitted, subject to exact file and hash checks

- Coinexx MT5 broker-export XAUUSD tick CSV.GZ Jan–Sep 2026, Drive folder `(exact ID in restricted Drive-only handoff)` (nine exact `REGISTERED` hashes).
- Dukascopy XAUUSD tick CSV.GZ Jan–Jul 2026, Drive folder `(exact ID in restricted Drive-only handoff)` (seven exact `REGISTERED` hashes).
- R9 tester logs in exactly `(exact ID in restricted Drive-only handoff)` (REAL) and `(exact ID in restricted Drive-only handoff)` (SYNTH), plus reports in `(exact ID in restricted Drive-only handoff)`, only for targeted reference research.
- Only approved R9 source branch commit `8729a6345655a7b4ea31facc81982004ee2b8921` and the independently developed backtest baseline descendant of GitHub commit `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`.
- Official MetaQuotes for platform mechanics; no outside trading-data sourcing or community strategy imports.

## Explicitly still forbidden

Any other GitHub research branch (even in the same repository); prior ChatGPT project sources; neighboring Google Drive files; assumed missing reports; third-party price feeds not named here; new Dukascopy months or Coinexx months not on `REGISTERED`; use of source material in GitHub as trusted historical test data; synthetic profits as real executable expectations.

## Required clock handling

Jan–Feb Coinexx corrected UTC minus 120 minutes; Mar 2026 DST transition and Apr–Jul minus 180 minutes. Aug–Sep Coinexx profile is extrapolated and lacks independent Dukascopy verification. Preserve source time and corrected time; compare only normalized matching UTC coverage.

**Change protocol:** A new source needs explicit user approval, exact URL/Drive file ID, SHA-256, date range, broker/unit/timestamp audit, new policy version and matching GitHub+Drive receipts. No "temporary" exception in scored research.
