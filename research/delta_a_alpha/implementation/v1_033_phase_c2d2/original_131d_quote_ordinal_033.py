"""Source-faithful 131D L1->L3 adapter with original 131C quote ordinal identity.

Preserves the existing 131C event and 131D six-cell rules, changing only
source key collision semantics when two distinct quotes share one millisecond.
The original JAN032 build_events() identifies each candidate by tick *index*.
This is a bounded 033 implementation repair, not a new market strategy.
"""
from __future__ import annotations
from dataclasses import replace
from original_online_sources_033c import Original131DSessionL3, Original131CSessionGridL1
from v1_funded_core_033c import Quote, Structure, FundedEngine, Proposal


class Original131DOrdinalL3(Original131DSessionL3):
    """Causal ordinal key; no reclassification, reparameterization, or new offers."""

    def __init__(self, grid: Original131CSessionGridL1 | None = None):
        super().__init__(grid)
        self.quote_ordinal = -1

    def on_market_quote(self, q: Quote, engine: FundedEngine) -> None:
        super().on_market_quote(q, engine)
        self.quote_ordinal += 1

    def propose(self, q: Quote, s: Structure, engine: FundedEngine):
        original = tuple(super().propose(q, s, engine))
        # super().propose() generates pending L1 events before this identity key,
        # including its standalone on_market_quote() compatibility path.
        return tuple(replace(p, source_event_key=f'{p.source_event_key}:TICK{self.quote_ordinal}')
                     for p in original)
