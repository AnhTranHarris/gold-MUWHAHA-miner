# Delta-A-alpha — April Cross-Month Portability Study 136W3

**Status:** COMPLETE / TIMEOUT RECOVERED / ATOMIC

## Why this exists

The April transition upper bound (136T2) proved that the vertical-grid spine can support **+$67,531.19 / 31,974 trades** at cap512 while beating April R9 SYNTH net, gross loss, PF, win rate, expectancy and trade count. The unresolved problem is learning that opportunity causally from prior months rather than selecting April transition cells with April outcomes.

## Recovered tests

- **W0 — frozen Jan-Mar n=4/60 campaign governor:** best about +$45,691 / 14,364 trades. Portable but too slow.
- **W1 — credit router:** best about +$53,970 / 28,860 trades. Velocity improved sharply, but gross loss -$9,751 and PF ~6.53 fail the quality contract.
- **W2 — parent-credit router:** +$40,761.83 / 6,937 trades / gross loss -$1,923.33 / PF 22.19. All quality gates pass, but velocity collapses.
- **W3 — adaptive credit/scout expansion:** 486 atomic portfolio variants. 144 pass all non-velocity R9 gates; none reaches R9 SYNTH trade count. Best all-metric velocity is **7,650 trades**.

## Scientific conclusion

The missing April mechanic is **not more credit** and not a larger scout quota. The system needs a richer causal state discriminator between the sparse exact transition-cell learner (too cold-start) and the coarse rule-family campaign learner (too permissive or too restrictive).

The next hypothesis is a **hierarchical contextual transition governor**: seed with Jan-Mar prior evidence and back off from specific rule/depth/previous-outcome context toward broader rule/session/hour/subphase context until enough prior-closed evidence exists. Every admission decision must use only information known before the child entry.

## Recovery rule

Do not rerun W0-W3. Use the exact JSON/helpers in the April interim Library bundle. T2 is the research opportunity upper bound; V2 is the April parametric quality frontier; W0-W3 are the portability-boundary evidence.