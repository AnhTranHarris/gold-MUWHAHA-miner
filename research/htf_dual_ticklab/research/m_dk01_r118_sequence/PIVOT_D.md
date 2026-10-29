# F401-R118-D — matured online hierarchical error-state router — PREDECLARED SUCCESSOR

R118 A/B/C static sequence-liquidity/geometry portfolio completed its frozen Jan-CAL selection and did not approach high-capacity transfer. This successor changes the decision mechanism rather than retuning its trees.

At each original signal, use the frozen R118 direct/teacher/guardian scores plus source-causal context, then update several hierarchical empirical-Bayes wrong-rate experts only when a previous event's original 30s label is fully mature (`t_previous + 33.001s <= t_current`). No current/future label enters a decision.

Fixed expert views: (1) frozen direct-risk percentile bin (20 bins from Jan CAL reference mapping), (2) side × six-hour UTC session, (3) Jan-CAL-frozen quartiles of causal 120s realized volatility × 60s quote rate, (4) M1 completed close-location decile × 10-dollar grid-distance sign/near-far bucket, and (5) matured same-side 10-minute wrong-rate quartile. Maintain decayed Beta wrong/correct evidence at 10m, 30m and 120m half-lives. Each view shrinks to the contemporaneous all-event posterior when effective evidence is small.

Predeclared router scores combine the frozen direct-risk or teacher-distillation rank with the support-weighted log wrong-odds ratios from the views. The only model-family selection allowed is among these three fixed decay scales and direct-vs-distill base score on Jan CAL. Correct-loss reporting budgets remain 0.10%, 0.25%, 0.50%, 1%, 2%, 5%; freeze router/scale/cut once on Jan CAL, then replay Feb/Jun/Jul unchanged, resetting only local posterior state at month boundary and learning from that month's matured outcomes online.

This is an original-signal veto mechanism, not delayed order cancellation. It is distinct from R116's action-response correction and from R117's static lifecycle classifier. Failure of this configuration will trigger the already-declared multi-horizon future-path regression/distillation successor, not another posterior threshold sweep.
