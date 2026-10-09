"""DAA-033 Phase C2D2: bridge original 084 renewal geometry to actual L7 fills.

This is an isolated, broker-idealized *partial* funded adapter, NOT full V1,
original 084 event parity on funded market windows, or an MT5 EA. Original
unabridged owner L0-L7 whitepaper remains authoritative.

Unlike source-only 084, the renewal state moves on accepted L7 fill/close
callbacks. Rejected child proposals never consume a scout, set a rearm
reference, or earn campaign renewal. Existing C2C 119 paid multi-parent rules
remain responsible for actual realized-close credit and relock.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from v1_funded_core_033c import Quote, Structure, Proposal, Position, Close, FundedEngine
from original_119_multi_parent_033c2c import Original119MultiParentL4


class Funded084L7Bridge(Original119MultiParentL4):
    """Quote-causal renewal bound to physical (modeled) L7 positions.

    For the 119 source geometry, the first child may be proposed only from the
    *next observed quote* after L3 parent acceptance. At most one accepted
    child belongs to a window at once. Subsequent child proposals require an
    actually closed child, a later quote, and favorable executable quote
    movement against the last executed exit price (zero rearm is original
    084/119 default, not an averaging-down invitation).

    No source-only OPEN event advances a paid campaign. All genuine close
    attribution stays in the existing funded account kernel.
    """

    CHILD_SOURCE = 'ORIGINAL_119_C2C_CHILD'

    def __init__(self, parent_window_ms: int = 1800000,
                 *, rearm_raw: int = 0, initial_rearm_raw: int = 0):
        super().__init__(parent_window_ms=parent_window_ms)
        if rearm_raw < 0 or initial_rearm_raw < 0:
            raise ValueError('Invalid 084 rearm distances')
        self.rearm_raw = rearm_raw
        self.initial_rearm_raw = initial_rearm_raw
        self.quote_index = -1
        self.parent_tick: dict[int, int] = {}
        self.initial_favorable_raw: dict[int, int] = {}
        self.exit_favorable_raw: dict[int, int] = {}
        self.actual_live_child: dict[int, int] = {}
        self.child_last_close_tick: dict[int, int] = {}
        self.children_funded: dict[int, int] = defaultdict(int)
        self.funded_entry_events: list[tuple] = []
        self.funded_close_events: list[tuple] = []
        self.proposal_denials_do_not_mutate_state = True
        self.invalid_terminated_windows: set[int] = set()

    def on_market_quote(self, q: Quote, engine: FundedEngine) -> None:
        # Called by engine at the start of every quote, even on HTF outage.
        self.quote_index += 1

    def on_funded_entry(self, p: Position, q: Quote, s: Structure,
                        engine: FundedEngine) -> None:
        # Inherited gate registers actual funded L3 049 parents and child owners.
        super().on_funded_entry(p, q, s, engine)
        if p.layer == 'L3' and p.id in self.windows:
            self.parent_tick[p.id] = self.quote_index
            self.initial_favorable_raw[p.id] = (
                q.bid_raw if p.side == 1 else q.ask_raw)
        elif p.layer == 'L4' and p.source == self.CHILD_SOURCE:
            owner = self.accepted_children.get(p.id)
            if owner is None or owner not in self.windows:
                raise ValueError('Accepted 084 child lacks a funded parent')
            if owner in self.actual_live_child:
                raise AssertionError('Simultaneous 084 children in one window')
            self.actual_live_child[owner] = p.id
            self.children_funded[owner] += 1
            self.funded_entry_events.append(
                (self.quote_index, q.time_ms, owner, p.id, p.entry_raw))

    def on_funded_close(self, c: Close, engine: FundedEngine) -> None:
        # Capture genuine execution BEFORE superclass removes child ownership.
        owner = self.accepted_children.get(c.position_id)
        if owner is not None:
            if self.actual_live_child.get(owner) != c.position_id:
                raise AssertionError('084 closure has no matching live child')
            self.actual_live_child.pop(owner)
            self.child_last_close_tick[owner] = self.quote_index
            self.exit_favorable_raw[owner] = c.exit_raw
            self.funded_close_events.append(
                (self.quote_index, c.time_ms, owner, c.position_id,
                 c.exit_raw, c.net_usd, c.reason))
            # Original 084 has favorable first-touch renewals; forced/external
            # exit is terminal for this particular parent window. The inherited
            # earned/relock contract still records the real losing close.
            if c.reason != 'TP':
                self.invalid_terminated_windows.add(owner)
        if c.position_id in self.windows:
            self.invalid_terminated_windows.add(c.position_id)
        super().on_funded_close(c, engine)

    def propose(self, q: Quote, s: Structure,
                engine: FundedEngine) -> Iterable[Proposal]:
        # C2C owns exact paid-119 eligibility; C2D2 adds 084 event sequencing.
        for p in super().propose(q, s, engine):
            if p.source != self.CHILD_SOURCE:
                continue
            try:
                owner = int(p.source_event_key.split(':')[1])
            except (IndexError, ValueError) as exc:
                raise ValueError('Malformed funded 084 owner key') from exc
            w = self.windows.get(owner)
            if (w is None or not w.active or owner not in engine.positions
                    or owner in self.invalid_terminated_windows):
                continue
            if self.quote_index <= self.parent_tick.get(owner, self.quote_index):
                continue
            if owner in self.actual_live_child:
                continue
            if self.quote_index <= self.child_last_close_tick.get(owner, -1):
                continue
            first = self.children_funded[owner] == 0
            reference = (self.initial_favorable_raw.get(owner)
                         if first else self.exit_favorable_raw.get(owner))
            if reference is None:
                continue
            favorable = q.bid_raw if w.side == 1 else q.ask_raw
            needed = self.initial_rearm_raw if first else self.rearm_raw
            if (favorable - reference) * w.side < needed:
                continue
            # Explicit quote ordinal prevents two proposals at identical ms
            # sharing one event identity. State still advances only at FILL.
            yield Proposal(
                p.layer, p.source, p.cell, p.side, p.tp_usd, p.sl_usd,
                p.ttl_ms, parent_id=p.parent_id,
                recovery_of=p.recovery_of, first_scout=p.first_scout,
                requires_earned_watchdog=p.requires_earned_watchdog,
                source_event_key=(
                    f'C2CWINDOW:{owner}:{q.time_ms}:{self.quote_index}'),
                priority=p.priority)
