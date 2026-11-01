Yes. Based on the audit, I would keep the **Bayesian + Neyman–Pearson + Hawkes core**, but I would change what it is trying to predict and how the clocks feed it.

The current architecture is still too close to:

**“Is this a strong directional impulse?” → BUY/SELL**

I would replace that with:

**“Given the current market state, which action—BUY, SELL, or WAIT—has the highest probability of reaching a profitable executable exit before reaching an adverse barrier?”**

That is a fundamentally better target for R9.

## Would a rolling 5-minute internal clock be enough?

**Yes for the immediate predictive memory; no as the sole market context.**

I would make **5 minutes the EA's high-resolution working-memory horizon**. Inside those five minutes we maintain the complete causal subminute state:

**ticks → 250 ms → 500 ms → 1 s → 5 s → 15 s → 30 s → 45 s → 1 m → rolling 5 m**

That is enough history to characterize the short-lived impulse R9 actually trades.

But I would then feed that five-minute engine slow-changing **context priors** from:

**15 m → 1 h → 4 h**

Those larger horizons should **not trigger the trade**. They answer things such as:

- Is the 5-minute impulse aligned with or fighting the larger directional state?
- Is price locally extended or discounted?
- Is volatility expanding or compressing?
- Is the current impulse continuation, breakout, exhaustion or mean reversion?
- Is this normal London liquidity, overlap acceleration, New York continuation, rollover, or dead/off-session behavior?

So we get the larger geometry you want **without returning to the old mistake of waiting for H1/H4 geometry before executing a high-volume scalp**.

The architecture becomes:

**HTF geometry determines context.  
Five-minute state determines opportunity.  
Subsecond state determines exact execution.**

That distinction is crucial.

---

# The R9 Entry Engine I would build now

I would call the research architecture something like **R9 Probabilistic Entry Router v2**.

### Layer 1 — Event clock, not candle clock

The base clock should be `time_msc`.

Every quote gets classified into event types:

- Bid up
- Bid down
- Ask up
- Ask down
- Bid+Ask move together
- Spread widens
- Spread narrows
- Midpoint up/down
- No-price quote update
- Large jump
- Rapid reversal
- Quote drought / gap

MQL5 provides millisecond timestamps and tick flags specifically allowing us to determine which parts of a quote changed. `CopyTicks`/`CopyTicksRange` can also reconstruct millisecond-ordered tick history rather than assuming every `OnTick` callback represents an isolated market event. [MQL5](https://www.mql5.com/en/docs/series/copyticksrange?utm_source=chatgpt.com)

That lets us finally exploit what the SYNTH model destroyed: **the actual ordering of bid/ask events**.

---

# Layer 2 — Multiscale Hawkes becomes much more important

I would replace the current simple Hawkes intensity with a **marked, multivariate, cross-exciting quote process**.

Instead of one general intensity:

\[
\lambda(t)
\]

we maintain something closer to:

\[
\lambda_{BU},\lambda_{BD},
\lambda_{AU},\lambda_{AD},
\lambda_{SW},\lambda_{SN}
\]

where:

- BU = bid up
- BD = bid down
- AU = ask up
- AD = ask down
- SW = spread widening
- SN = spread narrowing

Then explicitly model cross-excitation.

Example:

**Bid increases → does Ask follow?**

That is different from:

**Ask increases → Bid stays behind → spread widens.**

Both might look like an upward midpoint move, but the second may be a much worse BUY environment.

That directly attacks the audit finding that our present midpoint/momentum information is insufficient.

Recent Hawkes research specifically models spread-dependent interactions between best Bid and Ask and finds useful cross-side excitation terms. [arXiv](https://arxiv.org/abs/2609.36631?utm_source=chatgpt.com)

### Hawkes decay should be multi-speed

I would run several exponentially decaying intensity memories simultaneously:

- 250 ms
- 500 ms
- 1 sec
- 5 sec
- 15 sec
- 45 sec
- ~180–300 sec slow activity state

Then the important information becomes **relative intensity**.

For example:

\[
H_{\text{BUY}}
=
\frac{
\lambda_{BU}+\lambda_{AU}
}{
\lambda_{BD}+\lambda_{AD}+\epsilon
}
\]

but also:

\[
H_{\text{spread}}
=
\frac{\lambda_{SN}}
{\lambda_{SW}+\epsilon}
\]

A BUY with strong upside intensity **and narrowing/controlled spread** is different from upside intensity occurring while spread explodes.

---

# Layer 3 — Convert the indicators into state variables, not triggers

I would retain ATR, RSI, BB, Fibonacci and the price-anchor idea, but substantially modify them.

### ATR becomes a volatility surface

Not one ATR.

Calculate causal realized movement/range over:

**1s, 5s, 15s, 45s, 1m, 5m, 15m, 1h**

Then derive ratios:

\[
V_{5s/5m}
=
\frac{\sigma_{5s}}{\sigma_{5m}}
\]

\[
V_{45s/15m}
=
\frac{\sigma_{45s}}{\sigma_{15m}}
\]

That tells us whether current movement is:

- normal noise,
- local ignition,
- abnormal acceleration,
- volatility shock,
- exhausted expansion.

This is far more useful than asking whether ATR is merely above some fixed number.

---

### RSI becomes event-time pressure

Classical RSI is too coarse for this job.

I would calculate separate RSI-like pressure states on:

- bid revisions,
- ask revisions,
- midpoint revisions,
- 1-second close changes,
- 5-second changes,
- 45-second changes,
- 5-minute context.

We want divergence such as:

**price ↑ but bid-pressure RSI ↓**

That may signal exhaustion.

Or:

**price ↑ + bid pressure ↑ + ask follows + spread stable**

which is much stronger continuation evidence.

---

### Bollinger Bands become a volatility-state geometry

Instead of:

> crossed upper band → BUY

we use:

- normalized band width,
- rate of width expansion,
- position within band,
- band velocity,
- band asymmetry,
- repeated band rejection,
- time outside envelope.

An important state could be:

**compression → first expansion → continuation**

versus:

**late expansion → extreme extension → quote reversal**

Both are "above upper Bollinger," but should have very different probabilities.

---

### Fibonacci becomes causal impulse geometry

This is where we must be extremely strict about hindsight.

We do **not** find the ultimate swing high and later draw Fibonacci levels backward.

Instead, establish an impulse anchor only from information already confirmed at time \(t\).

For example:

1. causal local impulse is detected;
2. anchor is frozen;
3. current retracement measured against that frozen impulse;
4. levels are updated only when another causal structural event confirms a new anchor.

Then we can obtain states such as:

- shallow pullback 0–23.6%
- normal pullback 23.6–38.2%
- deeper pullback 38.2–61.8%
- failed impulse >61.8%

This could be especially useful given the earlier structural-pullback behavior we discovered.

---

# Layer 4 — replace “VWAP” with something honest for spot gold

This is important.

Coinexx XAUUSD is OTC spot/CFD-like pricing. We do **not** possess a consolidated exchange volume tape.

Therefore I would not tell the EA it has a true market VWAP.

Instead use three anchors:

### Quote-Time Weighted Price

\[
QTWP =
\frac{\sum p_i\Delta t_i}
{\sum\Delta t_i}
\]

### Tick-activity weighted price

More weight during dense quote arrival.

### True volume-weighted calculation only when `Last/volume_real` is demonstrably valid

MQL5 ticks can contain Last and volume fields and flags that specify whether a trade/volume actually changed, but those fields should not be treated as valid centralized XAUUSD volume simply because they exist. [MQL5](https://www.mql5.com/en/docs/series/copyticks?utm_source=chatgpt.com)

I would therefore call the feature:

**Liquidity-Weighted Price Anchor**

rather than VWAP unless the feed actually supports true volume.

---

# Layer 5 — 5-minute rolling geometry

This is where your proposed five-minute internal clock becomes valuable.

Within the continuously rolling 300 seconds, maintain:

- high / low / midpoint
- causal pivots
- directional displacement
- realized variance
- spread distribution
- quote-event count
- Hawkes intensity
- impulse count
- pullback count
- rejection count
- failed breakout count
- acceleration/deceleration
- path efficiency
- entropy/choppiness
- distance from rolling liquidity-weighted anchor

Do **not** rebuild this every five minutes.

It should be a rolling window:

**12:00:00–12:05:00  
12:00:00.250–12:05:00.250  
12:00:00.500–12:05:00.500  
...**

Always moving.

That means the EA continuously understands approximately the previous five minutes of market behavior rather than waiting for an arbitrary M5 candle boundary.

---

# Layer 6 — larger geometry becomes Bayesian priors

This is how I would bring back the 15m / 1h / 4h structures without letting them slow down execution.

Suppose our fast model produces:

\[
P(BUY|X_{\text{fast}})=0.76
\]

Instead of simply requiring H1 bullish, the larger horizons alter the prior.

For instance:

\[
P(BUY|R,S,G,X)
\]

where:

- \(R\) = volatility/regime
- \(S\) = session
- \(G\) = larger geometry
- \(X\) = fast features

So perhaps:

**Fast BUY = 0.76  
15m continuation supports = +evidence  
1h overextended = −evidence  
4h strong trend = +weak evidence**

Final posterior might become:

\[
P(BUY)=0.81
\]

Alternatively:

**Fast BUY = 0.76  
15m exhaustion  
1h resistance geometry  
4h neutral**

could fall to:

\[
P(BUY)=0.58
\]

Then we WAIT.

No hard veto required.

This is much more appropriate for a Bayesian system.

---

# Layer 7 — explicit market-state model

This is another thing I would add.

The EA should estimate a current latent state such as:

1. **Compression**
2. **Ignition**
3. **Trend continuation**
4. **Orderly pullback**
5. **Exhaustion**
6. **Reversal**
7. **Volatility shock**
8. **Chop**
9. **Spread toxicity**
10. **Quote drought / maintenance**

These states can have probabilities rather than hard classifications.

Example:

\[
P(\text{continuation})=.64
\]

\[
P(\text{exhaustion})=.22
\]

\[
P(\text{chop})=.14
\]

Then different entry specialists operate differently.

A BUY during **ignition** should not use the same evidence requirements as a BUY during **pullback continuation**.

That gives us the multi-state architecture you are asking for.

---

# Layer 8 — session becomes a model parameter

Not simply London = allowed / Asia = disabled.

Build separate priors for:

- Australia/Sydney
- Tokyo/Asia
- London
- London–NY overlap
- New York
- rollover
- weekend transition

For example, a 5-second impulse magnitude of $0.30 may mean very different things in:

**Asian liquidity**

versus:

**London–NY overlap**.

So the Bayesian model becomes:

\[
P(Y|X,\text{session},\text{regime})
\]

rather than one universal model.

---

# Layer 9 — Neyman–Pearson must control bad entries, not generic classification error

This is one of the most important changes I would make.

Current thinking:

> Choose a probability cutoff.

New approach:

We define a **false entry** as an entry whose realized executable outcome is unacceptable.

Then choose the NP threshold so that:

\[
P(\text{ENTER}|\text{bad outcome})
\leq \alpha
\]

for each important regime.

But \(\alpha\) can differ.

Example:

| State | permitted false-entry rate |
|---|---:|
| London trend ignition | 10% |
| NY continuation | 8% |
| pullback continuation | 7% |
| chop | 2% |
| spread toxicity | 0% |
| rollover | 0% |

Neyman–Pearson becomes our **safety governor**.

Bayesian inference chooses what looks attractive.

NP controls how much bad evidence we permit.

---

# Layer 10 — most important change: competing first-passage probabilities

This should become the actual target.

For BUY, estimate:

\[
P(T_{+0.10}<T_{SL})
\]

then:

\[
P(T_{+0.30}<T_{SL})
\]

and:

\[
P(T_{+0.50}<T_{SL})
\]

plus:

\[
P(T_{SL}<T_{+0.10})
\]

and timeout.

Across different horizons:

- 1 sec
- 3 sec
- 5 sec
- 10 sec
- 15 sec
- 30 sec

That gives us a **future path distribution** without needing future information at runtime.

Offline, future ticks generate the training labels.

Online, only historical ticks generate the features.

That is normal causal supervised prediction.

Research shows high-frequency returns and event durations can contain materially more short-horizon predictability than longer-horizon returns, and that timeliness down to milliseconds can matter. [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4095405\&utm_source=chatgpt.com)

---

# Layer 11 — BUY / SELL / WAIT should be expected-value decisions

This becomes the final router.

For each tick/evaluation point calculate:

\[
EU_{BUY}
\]

\[
EU_{SELL}
\]

\[
EU_{WAIT}=0
\]

For example:

\[
EU_{BUY}
=
P_F E[G]
-
P_A E[L]
-
C
-
\lambda CVaR
\]

where:

- \(P_F\) = favorable first-passage probability
- \(E[G]\) = expected gain
- \(P_A\) = adverse first-passage probability
- \(E[L]\) = expected loss
- \(C\) = spread/slippage/commission
- \(CVaR\) = tail-risk penalty

Then:

**BUY only if**

\[
EU_{BUY}>EU_{SELL}
\]

and

\[
EU_{BUY}>0
\]

and NP gate passes.

Likewise for SELL.

Otherwise:

# WAIT

The WAIT action is essential.

Our audit demonstrated why.

On Dukascopy, even a hindsight oracle choosing BUY versus SELL was still negative if forced to participate broadly.

So the most valuable decision may often be:

**“There is movement, but this movement cannot currently be monetized under our execution geometry.”**

---

# Layer 12 — use SYNTH R9 differently

I would keep the SYNTH teacher, but demote it further.

Instead of:

**teacher says BUY → student learns BUY**

use:

**teacher says this historical region contains exploitable geometry**

Then ask the real-tick model:

> What causal information existed immediately before these synthetic opportunities?

We use teacher membership as an auxiliary target.

Something like:

\[
Loss =
Loss_{real-profit}
+
0.10\,Loss_{teacher}
\]

not:

\[
Loss=Loss_{teacher}
\]

Real-tick outcome always dominates.

Teacher becomes a **treasure map**, not truth.

---

# Proposed complete hierarchy

I would structure the new entry mechanism like this:

**Macro Context**

4h geometry/regime

↓

1h structure / volatility state

↓

15m directional geometry / extension

↓

**Rolling 5-minute Market Brain**

regime · causal pivots · volatility · liquidity · impulse state · session

↓

45s / 30s / 15s

state evolution

↓

5s / 1s

impulse confirmation

↓

500ms / 250ms / ticks

bid/ask response · Hawkes excitation · spread behavior

↓

**Competing-risk prediction**

favorable barrier vs adverse barrier vs timeout

↓

**Bayesian posterior**

BUY vs SELL vs WAIT

↓

**Neyman–Pearson governor**

reject unacceptable false-entry risk

↓

**Expected net value**

spread + slippage + commission + tail risk

↓

# BUY / SELL / WAIT

That is the architecture I would pursue.

## And one key change from our earlier research

I would **not** optimize for “accuracy” alone.

If we achieve 85% accurate calls whose average winner is $0.05 while the 15% losers average −$0.50, it is useless.

The objective should be something closer to:

\[
\max E[P\&L]
\]

subject to:

\[
P(\text{catastrophic adverse path})<\alpha
\]

and:

\[
Trades/day \geq T_{minimum}
\]

That gives us all three things you actually want:

**accuracy + survivability + high-volume profitability.**

And this is where the five-minute rolling clock is exactly useful: **five minutes supplies enough high-resolution local history for the execution prediction, while 15m/1h/4h supply context rather than slowing the decision.**

I would make this the next architecture rather than spending more cycles tuning the present classifier.