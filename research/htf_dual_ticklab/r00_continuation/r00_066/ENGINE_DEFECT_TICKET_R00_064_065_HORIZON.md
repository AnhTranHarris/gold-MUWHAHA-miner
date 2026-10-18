# XAU-HTF-ENGINE-DEFECT-20261018-001: 10s lookup mislabeled as 30s

**Status:** Proven in original authenticated source and synthetic fixture. Corrected historical scores NOT MEASURED.

Exact source archival ZIP SHA-256:
- R00-063 c36bd88c018c8fa10f47b9f344a8e551abf7059961436b4b71051b61c436c880 — source selects first original quote at t+30000ms.
- R00-064 502a40ccee95aaa50d520f3c2c73a09f471c448f94ba4afebd515c5f58e57c29 — source selects t+10000ms, reports 30s.
- R00-065 5519db1486895fa16d4b148dadae596677c1376febfbc931efdc432d5ee8db66 — source selects t+10000ms, reports 30s.

The R00-064/065 timestamp freshness predicate only tests (future_ts - decision_ts - 30000)<2000; it omits >=0 and therefore treats a +10s quote as a valid +30s result. A deterministic fixture with UP at +10s and DOWN at +30s reproduced the inconsistent label.

Historical results 234944/563858 (R00-064) and 236026/567117 (R00-065) are retained exactly as recorded, NOT certified +30s results. January training labels, February frozen calibration and June/July transfer require a scoped correction of all three phases. Original episode decisions, source hashes, historic negative outcomes and full research archives must remain immutable.

Repair: use the first original tick at or later than t+30000ms, with 0<=freshness<2000ms; missing/neutral outcomes counted wrong. Revalidate on synthetic fixtures, then on only the eight SHA-pinned approved month files; rerun only affected 064/065 data derivation, Jan fit, Feb freeze and historically exposed Jun/Jul scoring. Report original and corrected per-broker/week/day/hour/month ledgers side by side. This does not authorize broker-reader rebuild, extra sources, or live-trading claims.

Source GitHub head before this isolated bootstrap: 07a93fb8d26b4386e332aeef625c7f1f27e96eb6. No original branches or source ZIPs changed.
