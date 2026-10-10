"""DAA033 incremental cooperative Jan/Feb L3 integration, source-only research gate.

This composes existing original JAN037/JAN038/JAN039 and FEB042/FEB045/FEB047
operators inside ONE funded L7 account. It does not regenerate original
JAN039/FEB045 source-oracle exit tapes, nor claim full L1-L6 original parity.
Original V1 owner whitepaper remains authoritative. No month selector.
"""
from __future__ import annotations
from dataclasses import replace
from typing import Iterable

from v1_funded_core_033c import Quote, Structure, Proposal, Position, Close, FundedEngine
from original_50ms_funded_bridge_033 import OriginalJAN037L3QuoteBridge, OriginalSourceFeed033
from source_stmr_completed_ema_033 import SourceSTMRCompletedStack
from original_jan039_source_owner_adapter_033 import exact_jan039_l3_chain
from feb045_source_native_context_033 import FEB045NativeQualityL3
from source_native_s26_s27_033 import S26, S27
from feb045_physical_heat_feb047_queue_033 import (
    FEB045PhysicalHeatL3, PhysicalHeatConfig045, FEB047QueuedProfitReduceL7,
)


class _PerQuoteRelay:
    """One observed source event, offered independently to original policy chains.

    No endogenous event, funded close, profit or loss is manufactured here.
    Relays do not forward physical callbacks, preventing double-counted funding.
    """
    def __init__(self):
        self._offer = ()

    def set_offer(self, offer: Proposal) -> None:
        self._offer = (offer,)

    def propose(self, q: Quote, s: Structure, engine: FundedEngine) -> Iterable[Proposal]:
        value = self._offer
        self._offer = ()
        return value

    def on_funded_close(self, close: Close, engine: FundedEngine) -> None:
        pass


class JanFebCausalPortfolioL3:
    """Single-account source-policy router; original predicates remain separate.

    The overlap arbitration is an explicitly *experimental*, entry-known
    selection rule, NOT a validated January/February excellence setting:
    when original FEB045 quality/heat admits source 17-25, its policy owns
    the opportunity; otherwise retain original JAN039 eligibility. Original
    JAN039 S26/S27 TP and physical caps always keep source ownership. An
    opportunity can enter only once on an observed quote. No calendar branch.
    """
    FEB_QUALITY_SOURCE_IDS = frozenset((17, 19, 21, 22, 23, 24, 25))
    # Frozen JAN039_SELECTED_VERIFIED.json physical source-research limits.
    JAN_MAX_FUNDED_SOURCE_POSITIONS = 512
    JAN_MAX_FILLED_ENTRIES_PER_UTC_SECOND = 3

    def __init__(self, source: OriginalJAN037L3QuoteBridge,
                 *, heat: PhysicalHeatConfig045 | None = None,
                 queue: FEB047QueuedProfitReduceL7 | None = None):
        self.source = source
        self.jan_relay = _PerQuoteRelay()
        self.feb_relay = _PerQuoteRelay()
        self.jan = exact_jan039_l3_chain(self.jan_relay)
        self.feb = FEB045PhysicalHeatL3(FEB045NativeQualityL3(self.feb_relay),
                                        heat or PhysicalHeatConfig045())
        self.queue = queue or FEB047QueuedProfitReduceL7()
        self.routed_jan = 0
        self.routed_feb = 0
        self.both_source_policies_eligible = 0
        self.unfunded_offers = 0
        self.funded_entries = 0
        self.funded_closes = 0
        self.jan_source_cap_denials = 0
        self.jan_source_rate_denials = 0
        self._jan_filled_second = -1
        self._jan_fills_this_second = 0
        self._seen_source_keys: set[str] = set()

    def on_market_quote(self, q: Quote, engine: FundedEngine) -> None:
        self.feb.on_market_quote(q, engine)
        self.queue.on_market_quote(q, engine)

    def propose(self, q: Quote, s: Structure,
                engine: FundedEngine) -> Iterable[Proposal]:
        # Original source bridge consumes at most once, on this exact quote.
        raw = tuple(self.source.propose(q, s, engine))
        if not raw:
            return ()
        if len(raw) != 1:
            raise ValueError("JAN037 bridge unexpectedly emitted multiple source events")
        original = raw[0]
        if not original.source.startswith("ORIGINAL_J037_S"):
            raise ValueError("Source must be original JAN037, never a generated oracle")
        tail = original.source.split("_S")[-1]
        if not tail.isdecimal() or not original.source_event_key:
            raise ValueError("Missing original numeric source ID/event identity")
        source_id = int(tail)
        if original.source_event_key in self._seen_source_keys:
            raise ValueError("Original source event repeated")
        self._seen_source_keys.add(original.source_event_key)
        self.unfunded_offers += 1

        self.jan_relay.set_offer(original)
        j = tuple(self.jan.propose(q, s, engine))
        # FEB entry/heat rules receive the identical source event, with
        # provenance-specific naming; they may veto it using as-of features.
        self.feb_relay.set_offer(
            replace(original, source=f"ORIGINAL_F045_S{source_id}"))
        f = tuple(self.feb.propose(q, s, engine))
        if len(j) > 1 or len(f) > 1:
            raise ValueError("One raw event must not multiply funded offers")
        if j and f:
            self.both_source_policies_eligible += 1
        # Use observed FEB quality permission, NOT month labels or future P/L.
        # Keep JAN source26/27 native exit/cap ownership intact.
        if f and source_id in self.FEB_QUALITY_SOURCE_IDS:
            self.routed_feb += 1
            return f
        if j:
            jan_live = sum(p.source in (S26,S27) or
                           p.source.startswith("ORIGINAL_J037_S")
                           for p in engine.positions.values())
            if jan_live >= self.JAN_MAX_FUNDED_SOURCE_POSITIONS:
                self.jan_source_cap_denials += 1
                return ()
            sec = q.time_ms // 1000
            if sec == self._jan_filled_second and (self._jan_fills_this_second >=
                    self.JAN_MAX_FILLED_ENTRIES_PER_UTC_SECOND):
                self.jan_source_rate_denials += 1
                return ()
            self.routed_jan += 1
            return j
        return ()

    def on_funded_entry(self, p: Position, q: Quote, s: Structure,
                        engine: FundedEngine) -> None:
        self.funded_entries += 1
        if p.source in (S26,S27) or p.source.startswith("ORIGINAL_J037_S"):
            sec = q.time_ms // 1000
            if sec != self._jan_filled_second:
                self._jan_filled_second = sec
                self._jan_fills_this_second = 0
            self._jan_fills_this_second += 1
        self.source.on_funded_entry(p, q, s, engine)
        # Both original policies observe physical positions in a single
        # engine; no source-generator callback is repeated.
        self.jan.on_funded_entry(p, q, s, engine)
        self.feb.on_funded_entry(p, q, s, engine)

    def on_funded_close(self, c: Close, engine: FundedEngine) -> None:
        self.funded_closes += 1
        self.jan.on_funded_close(c, engine)
        self.feb.on_funded_close(c, engine)
        self.queue.on_funded_close(c, engine)
        self.source.on_funded_close(c, engine)


def create_jan_feb_combined_engine(jan038_rules_path, *,
                                   limits=None, simulated_broker=False):
    """Use the already-tested original bridge/contexts with ONE account.

    simulated_broker=True means idealized model ONLY, not actual Coinexx
    contract/margin verification. Default fail-closed unless explicitly set.
    """
    from v1_funded_core_033c import Limits
    source = OriginalJAN037L3QuoteBridge(jan038_rules_path, apply_jan038=True,
                                         label_family="JAN037")
    owner = JanFebCausalPortfolioL3(source)
    # Preserve FEB045's physical 1536-slot research ceiling separately from
    # JAN039's source-owned 512/3s settings; shared L7 retains margin/heat.
    restrictions = limits or Limits(balance_usd=100000.,max_open=1536,
                                    max_layer_open=1536,max_per_source_open=1536,
                                    max_same_direction=1536,max_per_cell_side=1536,
                                    max_orders_per_second=10,max_orders_per_tick=1)
    engine = FundedEngine(restrictions, [owner],
                          broker_contract_verified=simulated_broker)
    feed = OriginalSourceFeed033(source, SourceSTMRCompletedStack())
    return feed, engine, owner


def on_real_quote(feed, engine, time_ms: int, ask_raw: int, bid_raw: int):
    """Consume each original quote, not source exit tape or post-hoc month P/L."""
    quote = Quote(int(time_ms), int(ask_raw), int(bid_raw))
    structure = feed.on_quote(quote)
    engine.process_quote(quote, structure)
    return engine.score()
