# GAMMA-02 — January Watchdog Profit-per-Heat Breakthrough 131E

**Status:** COMPLETE / DURABLE PYTHON RESEARCH CHECKPOINT  
**Parent:** `GAMMA_02_JAN_SESSION_FIRM_DAILY_WEEKLY_131D`  
**Session portfolio:** frozen `LEAN4 + COLD64`  
**Watchdog:** refined q=$1.19/$1.10 family  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Objective

131D solved January's first deployment-quality problem: it produced positive net on all 21 R9-SYNTH trading days and beat R9 SYNTH on all five ISO weeks. The remaining major weakness was Watchdog's synchronized W05 floating heat.

This unit therefore does not add another broad entry sleeve. It asks whether the existing January architecture can retain its daily/weekly coverage while reducing Watchdog physical inventory.

Only two causal Watchdog controls are changed:

1. maximum favorable renewal layer = 35;
2. Watchdog physical concurrency cap.

No calendar date, week, or month enters the execution rule.

## Baseline entering 131E

131D `WD119_COVERAGE_LEAN4_COLD64`:

- net **+$207,653.32**
- trades **88,958**
- gross loss **-$5,075.10**
- PF **41.9161**
- win **97.96%**
- balance DD **~$818.71**
- full-tick equity DD **~$62,763.84**
- max open **703**
- positive days **21/21**
- same-date R9-SYNTH beats **13/21**
- weeks beating same-week R9 SYNTH **5/5**

## Profit-per-heat frontier

| Frontier | Net | Gross loss | PF | Win | Balance DD | Full-tick equity DD | Max open | 131D net retained |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Aggressive >$200K `L35_C703` | $203,532.62 | $-4,293.48 | 48.41 | 98.08% | $650.62 | $62,763.84 | 703 | 98.0% |
| Near-$200K `L35_C672` | $199,151.24 | $-3,926.38 | 51.72 | 98.06% | $451.92 | $59,996.16 | 672 | 95.9% |
| Balanced `L35_C640` | $194,425.92 | $-3,642.86 | 54.37 | 98.03% | $451.92 | $57,139.20 | 640 | 93.6% |
| Fundability `L35_C512` | $173,965.80 | $-3,642.86 | 48.76 | 97.72% | $451.92 | $45,711.36 | 512 | 83.8% |
| Defensive `L35_C240` | $121,582.26 | $-3,641.54 | 34.39 | 96.14% | $451.92 | $21,427.20 | 512 | 58.6% |

All five frontiers remain:

- **21/21 positive R9-SYNTH trading days**
- **13/21 days beating the same-date R9 SYNTH net**
- **5/5 positive ISO weeks**
- **5/5 weeks beating same-week R9 SYNTH**

Therefore the daily/weekly coverage breakthrough is not dependent on Watchdog running at full 703-position capacity.

## Preferred balanced frontier

### `L35_C640`

- net: **+$194,425.92**
- trades: **80,929**
- gross loss: **-$3,642.86**
- PF: **54.3718**
- win: **98.03%**
- expectancy: **+$2.4024/trade**
- balance DD: **~$451.92**
- full-tick equity DD: **~$57,139.20**
- max open: **640**

Versus 131D it retains **93.6%** of net while:

- cutting gross loss by **28.2%**
- improving PF by **29.7%**
- cutting closed-trade balance DD by **44.8%**
- cutting full-tick equity DD by **9.0%**
- cutting max simultaneous inventory by **9.0%**

This is the current preferred **balanced near-$200K** January frontier.

## Aggressive >$200K preservation frontier

### `L35_C703`

- net: **+$203,532.62**
- gross loss: **-$4,293.48**
- PF: **48.4050**
- win: **98.08%**
- balance DD: **~$650.62**
- full-tick equity DD: **~$62,763.84**
- max open: **703**

It retains **98.0%** of 131D net while reducing gross loss by **15.4%**, raising PF by **15.5%**, and reducing balance DD by **20.5%**. It does not reduce the full-tick floating-DD ceiling, so it is the aggressive economic frontier, not the preferred risk frontier.

## Near-$200K capacity frontier

### `L35_C672`

- net: **+$199,151.24**
- gross loss: **-$3,926.38**
- PF: **51.7213**
- balance DD: **~$451.92**
- equity DD: **~$59,996.16**
- max open: **672**

This is useful because it demonstrates a smooth tradeoff rather than one magical cap: Watchdog profit falls gradually as physical heat is removed.

## Stronger fundability frontier

### `L35_C512`

- net: **+$173,965.80**
- gross loss: **-$3,642.86**
- PF: **48.7553**
- win: **97.72%**
- balance DD: **~$451.92**
- equity DD: **~$45,711.36**
- max open: **512**

This retains **83.8%** of 131D net while reducing both max inventory and full-tick equity DD by **27.2%** and gross loss by **28.2%**.

## Defensive frontier

### `L35_C240`

- net: **+$121,582.26**
- gross loss: **-$3,641.54**
- full-tick equity DD: **~$21,427.20**
- all 21 days positive
- all five weeks beat R9 SYNTH

This sacrifices too much headline net to be the primary January system, but it proves that the session architecture can preserve firm-style daily/weekly reliability even after Watchdog equity DD is cut by approximately **65.9%**.

## Scientific interpretation

The January architecture now has two separate levers:

1. **session/state coverage** determines whether the system participates across ordinary days and weeks;
2. **Watchdog physical heat** determines how aggressively the rare high-renewal state is monetized.

That is a healthier architecture than asking one giant grid to do everything.

Layer depth 35 is a useful loss-quality boundary. Beyond it, extra physical renewal layers add enough realized loss that their marginal quality deteriorates. Capacity then gives a smooth economic frontier from defensive to aggressive operation.

## What did not solve the problem

Prior tests already rejected:

- naive hard stops;
- forced child timeouts;
- broad floating-loss gates;
- same-tick multiplicity caps that simply delete opportunity;
- brute session inventory;
- broad Asia continuation grids.

131E confirms that **plain capacity reduction works, but cannot fully solve profit-per-heat**. To get back above $200K with materially lower floating DD, the next mechanism has to extract more money per physical position.

## Next atomic unit

`GAMMA_02_JAN_WD119_VIRTUAL_RENEWAL_RUNNER_131F`

The next hypothesis family is deliberately different:

- keep the Watchdog virtual renewal ladder as causal evidence;
- do not require every virtual renewal to become another physical ticket;
- promote proven persistent paths into a physical runner/ratchet;
- compare dollars harvested per physical slot against the 131E frontier;
- preserve 131D's **21/21 positive-day** and **5/5 R9-SYNTH-beating-week** regression gates.

This is the most direct route toward the owner's desired combination:

**>$200K economics + substantially lower synchronized heat.**

## Reproducibility

Atomic helper SHA-256: `8c90db97910ee8fc9df193060b56507ac2cb55a91a766a856c395774f7cf7595`  
Atomic result SHA-256: `00ea46d09edae27200cc758ffc1438db4e195d9c197b9bad0ea7dde9a771c7b7`  
High-range helper SHA-256: `a633c9332de0bcc8186e2c59751f400d440c5e623125d1a117551d773195ba2c`  
High-range result SHA-256: `435f50189f7f13fdc8f9edff580194d64bea498503ff8e10d36d831e2fa9cbb6`

Compact 131E artifact SHA-256 is stored in the cursor after promotion.

Execution remains the GAMMA-02 normalized-spread Dukascopy research surface. It is not Coinexx MT5 certification.