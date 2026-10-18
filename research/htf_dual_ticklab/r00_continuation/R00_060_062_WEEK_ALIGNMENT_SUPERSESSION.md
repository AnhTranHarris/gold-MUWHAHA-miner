# Append-only correction: 2026-10-18 Monday/ISO week alignment

**Original experiment and model results are unchanged.** Previously shipped 060/061/062 weekly R9 comparison table used Unix epoch-seven-day buckets instead of the original R9 Monday-aligned key. Its reported week passes are superseded only for `interval=week`. Hour/day/month, emitted side, 30-second labels and model selection remain unchanged.

Exact corrected `key=(timestamp_ms_corrected_utc + 3*86400000)//604800000` based on original R9 weekly ledger. Recomputed against the preserved event-level BUY/SELL decisions, not guessed:
- R00-054 February-frozen control: **21/22** weeks pass 90%-R9 correct-direction floor.
- R00-060 February-frozen chosen: **21/22**.
- R00-061 February-frozen chosen: **1/22**.
- R00-062 February-frozen chosen: **21/22**.

All four original combined correct/emitted counts exactly reconcile to their prior receipts; no silent scoring changes.

**Patch exact ZIP**: 3,850 bytes, SHA-256 `db026a0202e8e4fd594e5cc4736d20ba75877e7c3445ec4de7cbc04e09d38b66`, CRC and member hashes PASS.
- PRIMARY verified: https://drive.google.com/file/d/1odG9n8xrgwEoxAkenx8hR4FTr8HUTN_z/view
- MT5_EXPAND verified: https://drive.google.com/file/d/1T6YAR_FzuJJOifspjL-oMF9qfHcC4ELW/view

The patch stores the exact independently executable Python reporting correction, corrected CSV and JSON supersession receipt. The prior original ZIPs remain immutable as historical evidence.