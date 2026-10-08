# GAMMA-02 — Cross-Month Risk Frontier 133C6

**Status:** COMPLETE MAJOR RISK-ADJUSTED CROSS-MONTH FRONTIER  
**Parent:** `GAMMA_02_CROSSMONTH_EXPERT_ENSEMBLE_BREAKTHROUGH_133C_G1`  
**January fallback:** untouched  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Take the SYNTH-beating G1 expert ensemble and determine the lowest tested global physical inventory cap that preserves time-matched R9 SYNTH monthly net in both February and March while reducing floating heat.

## Exact full-tick G1 risk before final cap

### February G1
- net: **+$71,884.88**
- balance DD: **~$2,633.73**
- full-tick equity DD: **~$19,449.55**
- max open: **957**

### March G1
- net: **+$86,864.48**
- balance DD: **~$7,855.20**
- full-tick equity DD: **~$11,647.55**
- max open: **667**

## Global-cap frontier

February narrow sweep:

| Cap | Net | PF | Equity DD | Max open | Beats Feb SYNTH? |
|---:|---:|---:|---:|---:|---|
| 584 | $65,776.40 | 4.254 | $16,169.92 | 584 | No |
| 592 | $66,113.87 | 4.268 | $16,390.32 | 592 | No |
| **600** | **$66,521.06** | **4.288** | **$16,611.84** | **600** | **YES** |
| 608 | $66,957.05 | 4.309 | $16,834.48 | 608 | Yes |
| 616 | $67,326.61 | 4.327 | $17,057.12 | 616 | Yes |
| 624 | $67,639.84 | 4.343 | $17,279.76 | 624 | Yes |
| 632 | $67,950.54 | 4.358 | $17,502.40 | 632 | Yes |
| 640 | $68,262.66 | 4.374 | $17,725.04 | 640 | Yes |

The tested crossover occurs between cap 592 and cap 600. **Cap 600 is therefore the minimum tested physical inventory ceiling that still exceeds February R9 SYNTH monthly net.**

## Selected risk-adjusted frontier — G1 / global cap 600

### February
R9 SYNTH: **+$66,213.65 / 33,523 trades**.

G1 cap600:
- net: **+$66,521.06** (**100.46% of SYNTH net**)
- trades: **26,816**
- gross loss: **-$20,234.19**
- PF: **4.2876**
- win: **87.86%**
- expectancy: **+$2.4806/trade**
- balance DD: **~$2,633.73**
- full-tick equity DD: **~$16,611.84**
- max open: **600**
- positive days: **14**
- same-date SYNTH-beating days: **7**
- positive weeks: **4/4**
- SYNTH-beating weeks: **2/4**

Relative to uncapped G1, February cap600 reduces max-open by **37.3%** (957 -> 600) and full-tick equity DD by **14.6%** (~$19,449.55 -> ~$16,611.84), while retaining enough net to remain above the monthly SYNTH benchmark.

### March
R9 SYNTH: **+$75,698.63 / 40,985 trades**.

G1 cap600:
- net: **+$86,318.27** (**114.03% of SYNTH net**)
- trades: **25,358**
- gross loss: **-$32,993.27**
- PF: **3.6162**
- win: **84.32%**
- expectancy: **+$3.4040/trade**
- balance DD: **~$7,855.20**
- full-tick equity DD: **~$11,647.55**
- max open: **600**
- positive days: **14**
- same-date SYNTH-beating days: **8**
- positive weeks: **5/5**
- SYNTH-beating weeks: **3/5**

## Scientific meaning

This is the first risk-adjusted frontier in the current owner-rebased research sequence that:

1. remains calendar-blind at execution time;
2. exceeds the exact time-matched R9 SYNTH monthly net in **both February and March**;
3. uses a bounded non-AI expert ensemble with shadow learning and causal promotion/demotion;
4. enforces a single tested global physical inventory ceiling of **600**;
5. materially reduces February floating heat versus the uncapped G1 breakthrough.

It does **not** beat R9 SYNTH on gross loss, PF, balance DD, or every daily/weekly metric. Those remain the next refinement targets. Do not discard this frontier while chasing those dimensions.

## Rejected refinements in this cycle

- blunt Watchdog/native mutual suppression: cut too much economic capture;
- source-only certification: stale source confidence transferred poorly into March;
- macro/HTF-key learner gating: improved February learner quality but suppressed March too aggressively;
- parallel ensemble Python processes: exceeded available memory and were killed; use single atomic blocks.

## Recovery rule

Use the durable 133C G1 helper/result and this 133C6 cap frontier. Do not rerun completed February/March discovery unless hashes fail. Continue only with bounded risk/Pareto refinements or January regression certification.