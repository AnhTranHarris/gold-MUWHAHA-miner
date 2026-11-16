# V17 — Additional positive-trade forensics: new orthogonal specialists

**15 November 2026 · Coinexx XAUUSD · Jan–Sep 2026 original source SHA pins · Research only · no MT5 EA edits**

## Owner's positive-trade objective

The existing V16 checkpoint found **+$3,825.26** modeled *incremental* cash on its clean 5s extension (98.27% matched original opportunities retained); its complete system remained negative. This audit asks a different question: **where else did actual historical trades earn cash, or approach a cash-winning exit, and which causal microstructure events could let a fresh specialist reproduce them?** It does not repeat a parameter brute-force optimization.

We independently reopened the nine V12 exact-ms original trade ledgers (338,064 completed trades, 128,203 originally positive), and for two new exit hypotheses read the nine unchanged, independently SHA-pinned Coinexx original broker quote archives. All decisions occur using past source ordinals, actions at the next quote, and original BUY Bid / SELL Ask liquidation with an additional assumed $0.20 round-trip cash charge.

## New prospective profit opportunity families

### A. Stalled-recovery small-profit capture — a new post-entry mechanism

The original stopped trades include **9,696** that temporarily reached at least **+$0.02** modeled cash but eventually closed at a stop. We developed a rule that requires an actual **20-cent adverse quotation first**, waits for an observed **+$0.02** recoverable net price, then exits on the **next** source quote. Its fixed original-entry screen was **+$62.71** modeled cash in 6/9 months, converting 609 originally nonpositive outcomes into positive outcomes while sacrificing 1,237 historical winners. This is not enough to qualify as a win-rate improvement.

A *time-conditioned subtype* requiring at least **two seconds between the first deep adverse quote and the positive recovery** produced **+$68.54** across 4,326 affected lifecycles, in 6/9 months. The January/May/September development subset contributed **+54.39**; the other six contributed **+14.15** without further changes. It created **535** newly positive trade outcomes but sacrificed **957** previous winners, so **the full-system majority-win objective still fails**. The setup is causal and different from extending an already-clean V9 harvest, although altered exits can still affect later entries in a rearmed strategy.

### B. Near-harvest failure protection — second independent cash-capture mechanism

The candidate arms only after a current, executable quote is at least **+$0.02 modeled cash**, then watches for the quote to fall back to **zero or below** and sends a hypothetical exit at the **next original source quote**. It never knows a trade's eventual stop or winner when acting. Its fixed-entry screen improved modeled cash by **+$401.39** over nine months (7/9 positive months), acting on 36,021 trades and intercepting **9,234** original stop outcomes. But it also converted **19,006** originally winning exits into nonwinning exits while turning **1,265** previously nonwinning exits positive.

**This is NOT an acceptable majority-winning execution policy.** Its cash improvement is only about **$0.0111 per affected trade**; a modest unmodeled broker fill cost can erase it. We preserve it as a distinct mechanism for study, not a deployment candidate. Its eligible harvest trajectories can overlap with the V16 extension; gains are NOT additive.

### C. Early profitable impulse with unusually tight spread — third, orthogonal trade class

From the original entry ledger, **43,961** trades stayed alive at least 250ms and had a *past-only* +10c favorable quote displacement without a -10c adverse displacement at that landmark. **24,858 (56.55%)** later completed positively. When the *entry-time* spread was **≤18 cents/oz**, **3,590 of 6,011** in that group were profitable (**59.72%**). This is a time-t+250ms **conditional majority-winner subtype**, not a new entry-time oracle.

The subtype's positive completed trades provided **+$960.27**, while its 2,421 negative outcomes lost **$2,021.28**, leaving **−$1,061.01** on this particular cohort. To make this existing cohort net positive without sacrificing its current winners would require reducing average loss magnitude from ~$0.835 to below **$0.397**; no current tested risk mechanism proves that. It represents an actionable *scientific target* for a protected favorable-impulse specialist, not an approved trade rule.

### D. Fast same-side rearm after a stop — fourth, entry-time specialist class

Once a previous trade has actually stopped, the next V9 entry's prior exit reason, direction and gap are available at decision time. When the next entry reused the **same direction 1.5–6 seconds after a stop**, **1,997 of 4,913** trades finished positive (**40.65%**, versus 37.92% baseline). This is an *entry-context pattern* and does not overlap logically with after-entry clean/recovery path labels, but its existing average net remained about −$0.3845/trade. It needs a separate causal location and quote pressure confirmation before any extra positions are authorized; simply taking more of the same entries is not justified.

### E. Preferred-cap event transitions — fifth small contextual class

There were **313** existing V9 preferred-cap winners averaging about **+$2.62 net** each; **142/313 (45.37%)** *next* entries also completed positively. The small cohort is dominated by early-year activity and requires independent later validation. A speculative post-cap extension did not earn qualification, and none was promoted. This class may help detect exceptional impulse/volatility regimes but should not be used as a blanket rearm instruction.

## Trade volume and system economics

- All source-exact *fixed-entry comparisons* preserve the **338,064 original completed trade slots**. They do **not** certify ≥95% volume under a dynamic, fully rearmed EA where exits alter subsequent entries and cash/margin state.
- The V16 +$3,825.26 clean extension, V17 +$401.39 cash floor, and +$68.54 stalled recovery are **separate control comparisons**. Some trade histories overlap: **never add them** to claim combined system profits.
- Original frozen V9 simulated net remains **−$135,317.63** under the illustrative $1 cash per $1/oz and extra $0.20/trade model; profitable completed trade share **37.92%**. **No V17 candidate qualifies as a complete-system profitable or majority-winning strategy**, and none establishes that the older reported >$100K research ceiling is executable.
- Spread and costs matter: the +$401 cash-floor delta across 36,021 changed exits has only about **$0.0111** of additional cost headroom *per changed exit*; the stalled-recovery +$68.54 across 4,326 exits has ~$0.0158. Broker commission, rejection, stop fill and latency telemetry remain missing.
- All Jan–Sep 2026 observations have already been reused as development material. A six-month check is useful for noncontemporaneous robustness but is **not untouched OOS**. No institutional order book/real traded volume is inferred from Coinexx quote logs.

## Research priority, not a parameter grid search

Preserve the **five orthogonal classes** with evidence timestamps, then prioritize only **two** pending experiments: (1) a dynamically rearmed V9 + clean-extension baseline with *time-conditioned stall recovery* as a nonadditive, risk-neutral shadow; (2) a 250ms low-spread favorable-impulse specialist with conservative quote-side loss containment and the original stop as hard bound. For every candidate require **entire-system net after costs, >50% winners, ≥95% original monthly volume, no capital-floor violations, and later untouched chronology** before promoting to native MT5.

## Outside institutional context (supports hypotheses only)

- Carol Osler, Federal Reserve Bank of New York, *Currency Orders and Exchange-Rate Dynamics*: stop orders and take-profit orders cluster differently near levels, motivating separate continuation and failed-recovery states: https://www.newyorkfed.org/research/staff_reports/sr125.html
- Carol Osler, *Stop-Loss Orders and Price Cascades*: trends can intensify through stop clusters; it does **not** prove the V9 original broker stops reveal hidden orders: https://www.newyorkfed.org/research/staff_reports/sr150.html
- BIS 2025 Triennial Survey execution landscape: fragmented dealer/internalised FX activity means original Coinexx quote prints cannot establish actual order-book imbalance or filled institutional volume: https://www.bis.org/publications/qr-202512/fx-trade-execution-landscape-through-prism-2025-bis-triennial-survey

## Reproducibility and scope

The accompanying package contains six source helpers/test scripts, the nine original pinned monthly receipt IDs, three groups of **nine compact derived event JSON/CSV files**, a unified statistical JSON, and a monthly summary. **No raw tick archives**, no MT5 trading EA edits, no downloads into Google Drive. Synthetic source-order checks verify quote-side execution, same-millisecond ordinal order, deep-adverse-before-recovery, and quote-gap abstention. No MetaEditor compilation or broker-side parity certified.