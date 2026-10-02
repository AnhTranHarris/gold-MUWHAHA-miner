# DELTA GOV-011 — Prop-Style Maintenance, Capital Staging, and Small-Account Survivability Contract

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Evidence loading:** NOT AUTHORIZED  
**Layer:** MAINTENANCE / CAPITAL GOVERNANCE — NOT EDGE DISCOVERY

## 1. Purpose

DELTA separates trading-edge research from capital-maintenance behavior.

The maintenance layer behaves like a disciplined forex day-trading / prop-style risk controller across:
- individual trades;
- intraday equity;
- daily performance;
- weekly performance;
- staged starting capital;
- small-account survivability.

It may throttle, pause, or stop new risk when maintenance limits are reached, but it may not rewrite or hide the underlying candidate's raw edge metrics.

## 2. Owner-defined fixed-lot rule

All testing begins with a fixed lot size of:

`0.01 lots`

This remains fixed until:
1. all four primary DELTA categories are locked within the accepted range; and
2. the owner explicitly defines and authorizes a future lot-sizing ladder.

DELTA must not invent that future ladder.

## 3. Owner-defined staged starting capital

The starting capital for each test depends on the number of locked primary categories:

| Locked primary categories | Test starting capital | Maintenance stage |
|---:|---:|---|
| 0 | $100,000 | Research-safe / full prop-style maintenance |
| 1 | $1,000 | Standard maintenance boundary |
| 2 | $500 | Small-account transition |
| 3 | $500 | Hold last owner-defined stage; no invented intermediate capital |
| 4 / all primary categories | $100 | Small-account survivability focus |

The three-lock stage remains at $500 because the owner has not specified a different amount.

Once the four-lock $100 account grows to **$1,000 or more**, standard forex/prop-style maintenance rules reapply.

## 4. Primary-category locks

For this contract, a category is locked only under the active DELTA metric-lock governance.

Capital staging follows the durable lock count. A temporary or non-durable metric result does not lower the test starting capital.

If a composite loses an inherited lock, the next test must return to the appropriate higher-capital stage until the lock is restored.

## 5. Community-derived maintenance principles

The following principles are adopted from recurring community practice across Reddit, ForexFactory, Myfxbook, and TradingView discussions. They are research heuristics, not claims that all prop firms use identical rules.

### 5.1 Stop loss / bounded loss
Every active position must have a predefined maximum-loss mechanism.

### 5.2 Intraday equity matters
Daily-loss enforcement must monitor **equity including floating P/L**, not only closed balance.

### 5.3 No martingale/grid escalation
The maintenance layer may not recover losses by automatically multiplying size or adding increasingly larger losing positions.

### 5.4 Per-trade risk must fit inside the daily budget
The intended planned loss of one trade must be materially smaller than the daily loss allowance.

### 5.5 Daily stop means stop
If the hard daily maintenance threshold is reached, no new risk is opened until the next defined risk-day reset.

### 5.6 Weekly loss management
A separate weekly maintenance boundary prevents repeated losing days from consuming the entire account through daily-reset loopholes.

### 5.7 Machine enforcement
Maintenance limits must be enforced by deterministic code, not discretionary "we will be careful" language.

## 6. Community source registry

Community references used to establish the initial maintenance framework:

### Reddit
- r/Forex — "Prop firm accounts - how much do you risk per trade?"  
  https://www.reddit.com/r/Forex/comments/1mwicwj/prop_firm_accounts_how_much_do_you_risk_per_trade/
- r/Forex — "How much to risk"  
  https://www.reddit.com/r/Forex/comments/1e8naci/how_much_to_risk/
- r/Forex — prop risk / losing-streak discussion  
  https://www.reddit.com/r/Forex/comments/1jpmxj9/protecting_myself_with_5_risk_with_prop_firm_acc/

Recurring community practice includes reducing risk to roughly 0.25%–0.5% per trade under tight prop drawdown constraints and lowering risk further during drawdown.

### ForexFactory
- "Prop firms daily loss limit"  
  https://www.forexfactory.com/thread/1242978-prop-firms-daily-loss-limit
- "One System for All Pairs" prop-style example  
  https://www.forexfactory.com/thread/post/15866840
- Prop Firm Hub discussions  
  https://www.forexfactory.com/thread/1067970-prop-firm-hub

Recurring themes include intraday equity-based daily loss limits, common examples around 5% daily / 10% maximum account loss, fixed risk near 0.5% per trade in some systems, and traders voluntarily stopping before the formal maximum.

### Myfxbook
- Trend Flow community journal  
  https://www.myfxbook.com/community/trading-systems/trend-flow/3363395%2C1

The journal documents explicit per-trade risk, stop-loss use, daily-drawdown limits, trading suspension after the daily limit, and rejection of martingale/grid behavior. It also documents a real rule breach during large floating drawdown, reinforcing the need for automated enforcement.

### TradingView community
- XAUUSD risk-management education / community ideas  
  https://in.tradingview.com/ideas/xauusd%28w%29/page-2/?sort=recent&type=education
- XAUUSD ideas / risk-management community surface  
  https://www.tradingview.com/symbols/XAUUSD/ideas/

Recurring gold-specific community guidance includes percentage-based position risk, predefined daily loss limits, smaller exposure under exceptional volatility, hard stops, and explicit invalidation levels.

## 7. Provisional standard maintenance envelope — accounts at or above $1,000

Until changed by owner review, DELTA adopts a deliberately conservative internal envelope that sits inside commonly discussed prop-style limits.

### 7.1 Planned per-trade loss ceiling
Target maximum planned loss per position:

`0.50% of risk-day starting equity`

Because lot size is fixed at 0.01, the strategy may take less risk than this. It may not widen a stop merely to consume the full allowance.

If a structurally valid 0.01-lot trade cannot fit within the planned-loss ceiling, the trade is maintenance-ineligible under standard mode.

### 7.2 Daily warning
At:

`-2.5% of risk-day starting equity`

mark:

`DAILY_RISK_WARNING`

New opportunities may continue only if the active maintenance policy explicitly allows them; the controller must record the warning state.

### 7.3 Daily hard stop
At:

`-4.0% of risk-day starting equity/equity floor`

mark:

`DAILY_HARD_STOP`

No new positions may be opened until the next risk-day reset.

The 4% internal stop intentionally leaves buffer beneath the frequently discussed 5% prop-style daily limit.

### 7.4 Weekly warning
At:

`-5.0% of risk-week starting equity`

mark:

`WEEKLY_RISK_WARNING`.

### 7.5 Weekly hard stop
At:

`-8.0% of risk-week starting equity/equity floor`

mark:

`WEEKLY_HARD_STOP`.

No new positions may be opened until the next risk-week reset unless the owner explicitly authorizes a research override.

The 8% internal stop intentionally leaves buffer beneath the commonly discussed 10% total-loss style constraint.

## 8. Equity-based breach accounting

Daily and weekly maintenance must use the worst observed equity state, including:
- closed P/L;
- floating P/L;
- commissions;
- swaps when applicable;
- modeled execution costs.

A position that breaches a hard maintenance limit and later recovers remains a maintenance breach for that test.

## 9. Risk-day and risk-week reset definitions

Exact reset timestamps are not frozen by this contract because DELTA already has pending session/DST governance.

Before promotion-grade use, a dedicated timing rule must freeze:
- risk-day timezone;
- daily reset timestamp;
- risk-week start/end;
- DST behavior;
- weekend handling.

A backtest may not switch reset conventions after observing results.

## 10. Small-account transition — below $1,000

Below $1,000, fixed 0.01-lot sizing can make standard percentage-risk rules mechanically too restrictive or impossible for some structurally valid XAUUSD stops.

Therefore the maintenance controller enters:

`SMALL_ACCOUNT_SURVIVAL_MODE`

The objective changes to:

**grow rapidly enough to reach $1,000 while avoiding account destruction.**

This mode may relax or modify the standard daily/weekly percentage envelopes, but it may not remove:
- hard stop-loss logic;
- fixed 0.01 lot size;
- anti-martingale / anti-grid rules;
- equity monitoring;
- deterministic daily/weekly accounting;
- explicit account-survival constraints.

## 11. Small-account risk must be symbol-value based

Small-account mode must compute actual planned dollar loss from the broker/simulator symbol specification:

`planned_loss = stop_distance × value_per_price_unit_at_0.01_lot + modeled_costs`

DELTA must not assume a hard-coded XAUUSD dollar-per-point value without verifying the active symbol contract.

This is required because the minimum executable lot size can dominate percentage-risk mathematics on a $100–$500 account.

## 12. Small-account survival envelope is empirical, not invented

This contract does not yet freeze the exact:
- per-position percentage ceiling below $1,000;
- daily small-account stop;
- weekly small-account stop;
- minimum equity survival floor;
- consecutive-loss throttle;
- growth throttle.

Those parameters must be calibrated only after:
1. all primary categories are locked;
2. the $100/$500 stages are actually being tested;
3. the 0.01-lot symbol-value economics are verified;
4. the owner reviews survivability/growth evidence.

The goal is explicitly **not** to apply a rigid large-account prop rule that makes a $100 account incapable of taking valid trades.

## 13. Return to standard mode at $1,000

When an all-lock small-account test grows to equity of at least:

`$1,000`

the controller returns to the standard maintenance envelope unless the owner has approved a replacement policy.

This creates:

`$100 survival/growth -> $1,000 threshold -> standard maintenance`

## 14. Maintenance must not masquerade as edge

Every research report must preserve both:

### Raw candidate/composite performance
What the trading logic would have produced under its declared execution model without maintenance throttles.

### Maintenance-governed performance
What survives after daily/weekly risk rules, capital stage, pauses, and survival controls are applied.

A maintenance controller that improves drawdown by simply suppressing large amounts of opportunity must not be credited as a trading-edge breakthrough.

Its value is maintenance/risk control and must be labeled accordingly.

## 15. Interaction with high-opportunity-density governance

GOV-010 remains active.

The maintenance layer must report:
- opportunities blocked by daily/weekly limits;
- trades blocked by maintenance;
- activity lost to risk throttles;
- daily/weekly opportunity capture before and after maintenance.

This prevents prop-style safety rules from silently starving the high-frequency architecture.

## 16. Interaction with news/event specialists

Medium/high-impact event specialists remain permitted under GOV-009.

Maintenance may reduce or stop event exposure only through predetermined causal rules.

No news event receives unlimited risk merely because it is considered an opportunity regime.

## 17. Future lot-sizing ladder

The future post-maturity lot-sizing ladder is:

`OWNER_PENDING`

DELTA may model candidate ladders for analysis only if the owner asks, but no ladder becomes governing policy until the owner explicitly defines or approves it.

## 18. Human-review authority

The owner may revise:
- staged starting capital;
- fixed-lot policy;
- standard per-trade risk ceiling;
- daily/weekly warning and hard-stop levels;
- small-account survival rules;
- $1,000 transition threshold;
- reset timestamps;
- eventual lot-sizing ladder.

## 19. No evidence-load authorization

This contract defines maintenance policy only.

It does **not** authorize loading R9 REAL, R9 SYNTH, R9 OVERFIT, Coinexx reports, R9 ticklogs, Dukascopy tick files, or external news datasets. Existing owner evidence-loading restrictions remain active.
