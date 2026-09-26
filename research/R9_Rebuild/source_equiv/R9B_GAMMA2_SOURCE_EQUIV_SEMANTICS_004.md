# R9B_GAMMA2_SOURCE_EQUIV_SEMANTICS_004

January-only exact source-equivalence diagnostic.

Authoritative modeled-bid completed-second basis. Two previously untested CONT side-effect combinations:
- quota_only: CONT resets active sweep setup and consumes the per-minute quota, but sets no cooldown.
- cooldown_only: CONT resets active sweep setup and sets one-second cooldown, but does not consume sweep quota.

Executable runtime source SHA-256: `0d50a48034eef062fb898730b011115ebea5990517d14e1ff513f6d456c2b941`.
Result SHA-256: `cc842110512edbff5eaab5e1673936168cc19bfb07aae192607b623c0dd5e74b`.

Conclusion: count shifts bracket the certified 30,943 population, but winner conversion remains about 68%, so CONT side-effect semantics are not the missing Gamma_2 edge. Recover exact multiscale alignment-cache/lifecycle semantics next. August remains sealed.
