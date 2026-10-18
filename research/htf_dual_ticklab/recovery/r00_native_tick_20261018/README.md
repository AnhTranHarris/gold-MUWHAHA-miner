# R00 native-tick forecasting — original-source recovery and continuation

**Preservation date:** 2026-10-18. **Research only; entry signals, not execution, profitability or a qualified EA.**
**Source class:** original research artifacts with hashes and cloud byte provenance. **Do not replace original research reports or governance laws with this README.**

## Canonical complete original evidence

1. **R00-001 2026-10-17 native real-tick initial forecast research (ORIGINAL):**
   - GitHub: `research/htf_dual_ticklab/recovery/r00_native_tick_20261018/R00_XAUUSD_TICK_ENTRY_RESEARCH_2026-10-17.zip` (binary original, not a reconstructed model).
   - ZIP SHA-256 `c8c6fa3131c2393b09f5f488d4c59a6a8c69a3a7fd2e73821f5937cdd5ce8819`; 226,652 bytes; 24 ZIP members; CRC passed; 23/23 member SHA-256 and byte-length checks passed against bundled `R00_RESEARCH_ARTIFACT_SHA256_MANIFEST.json`.
   - MT5_EXPAND byte-identical cloud source: https://drive.google.com/file/d/1aXYWRRVb8xK3d-JUwuQKzu-r8cU9Ytvb/view
   - MT5_EXPAND dedicated copy: https://drive.google.com/file/d/1ThT6jZ4SmzHdqhWsZP0VZS4p8rli3OLQ/view
   - Unpack to recover **original Python scripts**, January-trained `r00_data/R00_HGB_signal_model.joblib`, original training/model metadata, eight per-broker-month source receipts, 128-rule-family audit, 280-sweep quality/density frontier, intervals CSV.GZ, and planned entry-002 JSON. All scripts and raw results reside in the ZIP, not in this README.
   - The eight large `R00_{broker}_2026_{month}_5s_events.pkl` caches **were not included** in this original ZIP. The `r00_signal_research.py` feature generator produces them from registered Jan/Feb/Jun/Jul raw real-tick files; a regeneration is a new run, and byte-for-byte cache identity is not asserted without a verified hash match.
2. **Later R00-053A/B/C forecasting source/models/result-ledger original ZIP:**
   - MT5_EXPAND cloud source: https://drive.google.com/file/d/1vKpwUIEhPW_j3uSMzXsTCIZqEuz_SH8v/view
   - Dedicated duplicate: https://drive.google.com/file/d/1DVwXGADDHIIm8HxUY2FZ9RhYWlZV7Syg/view
   - SHA-256 `4a116604acb684b395a9ae0dac100d58949455848e88254eb1ff96b0a41d6577`; 82,961,206 bytes; 51 entries; CRC passed on recovered source. Includes `r00_053a_extract.py`, `r00_053a_forecast*.py`, `r00_053b_router.py`, `r00_053c_native_passage.py`, `r00_053d_interval_audit.py`, original trained per-broker models/parameters, result transfer grids, exact R9 interval scorecards and nested original 001/023-026/050-052 archives. Original raw sources remain in PRIMARY Drive.
3. **Complete 053 recovery features/arrays (large archive, not in GitHub):**
   - ZIP SHA-256 `283909651335eeebeeb04aa2e56957d6c780690f93582ea88d1bf47947ecc012`; 572,358,288 bytes, 95 members, 9 cloud chunk files and original reassembly script. Full-original manifest: https://drive.google.com/file/d/1F9IYoq1MgwN0IqxW8c3Eq3mqNYkcpjQ1/view . Dedicated copied manifest: https://drive.google.com/file/d/1dOoFhH1WgKFKSv3P6iHqWoKo1vj3imGX/view . 9 parts reside in MT5_EXPAND/05_CHECKPOINTS_AND_RECOVERY at https://drive.google.com/drive/folders/1duJq0j5P5y9EtUyC0LvIaAubFJ9Gt3AY .
   - Original verified preservation receipt: https://drive.google.com/file/d/1vSRbECQfHTvB0F50YetELXO8McVx2zlM/view .
4. **This recovery folder:** https://drive.google.com/drive/folders/18fZPRE0ahzsYdE9ziurc4HNfUT2s9XN4 on the MT5_EXPAND connection, not the PRIMARY Drive account.

## R00-001 native-tick source contract — verified in ORIGINAL Python source

- Python stack: NumPy, pandas, scikit-learn, joblib; months 2026-01/02/06/07 separately for Coinexx and Dukascopy; 64,515,445 observed original tick records in prior experiment.
- Input files must match exact filename and SHA-256 allowlist in `research/htf_dual_ticklab/htf_ticklab/source_registry.py`. Dukascopy timestamp already UTC, Coinexx 2026 Jan/Feb subtract 120 min, Jun/Jul subtract 180 min, preserving originals. **Never merge separate broker quote tapes.**
- `r00_signal_research.py` derives first actual tick in populated 5s buckets, causal prior price movements, efficiency, spread, completed-bar RSI/ATR, quote-event *proxy* VWAP, Fibonacci state and scheduled 10s/30s future directional labels used **only for training/scoring**. No future label may become an input. No true executed volume/order book is supplied.
- `r00_directional_model.py` fits a historical HistGradientBoostingClassifier; training is January, February screening, June/July historical transfers; R00-001 model `.joblib` preserved. Thirty-second target is direction of future observed MID move exceeding USD 0.10, NOT ask-to-bid attainable P&L or executable order accuracy.
- Results include sufficient permissive event capacity but materially sub-90% directional accuracy and weak independence among raw successive triggers. Results are exploratory, not live-trading proof.
- Exact original R9 SYNTH comparative benchmark reports and governing policies are in PRIMARY Drive/approved GitHub; use originals. `R00_ENTRY_002_PREDECLARED_RESEARCH_PLAN.json` inside ZIP says PLANNED/NOT_EXECUTED in this original package; do not treat its instructions as already scored.

## Critical provenance gap — DO NOT FALSELY CLAIM RECOVERY

**R00-040 and R00-046 executable predecessor dependencies are NOT PRESENT in the verified R00-001 ZIP or later R00-053 light source archive.** Later cloud research receipts independently report original R00-040 and R00-046–050 model/code history still requires recovery. The original 053 source/models allow resuming 053-supported analyses, **not proving a byte-identical reproduction of R00-040 or R00-046**.

To cure this exact blocker, obtain the original `R00-040` and `R00-046` Python sources, frozen experiment plan, trained model-state files, transformation code, original event/label matrices and matching source-manifest SHA-256. Compare provenance and re-run only what is scientifically necessary. If original unavailable, label that chain `BLOCKED_PENDING_RECOVERY` and create an explicitly new experimental branch from approved source, not a counterfeit historic restore.

## Rules for next assistant/chat

1. Read original **four reports** and **governor/investor policy source documents** intact; source links are in canonical handoff and https://drive.google.com/file/d/1vSRbECQfHTvB0F50YetELXO8McVx2zlM/view . No self-summary authority.
2. Download and cryptographically verify both ZIPs above and inspect actual original methods. Restore larger 053 archive only if native per-event/cache arrays needed; verify all ordered chunk digests and whole ZIP checksum, not merely their names.
3. Read this branch head and confirm it descends from `1d1114fdbf0b3e0bf11ee734eefa425676fdd009` (which itself descends from `f9ca199d5c7627678b725c915e4c6eab279029da`).
4. Keep separate statuses: `R00-001 ORIGINAL RECOVERED`, `R00-053 ORIGINALS RECOVERED`, `R00-040/046 ORIGINAL PREDECESSOR SOURCE BLOCKED_PENDING_RECOVERY`. Do **not** restart or declare source dependencies recovered from this README. No prospectively untouched 2026 sample and no 90% accuracy achieved.
5. Continue constructive *entry-only* causal real-tick discovery only under explicit user instruction; no synthetic profitability promotion, no account-collapsing P&L addition, no unrelated GitHub projects.

**This is an additive recovery publication.** It does not change original tests, original model bytes, source data, approved broker clock or EA execution.
