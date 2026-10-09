"""Partial V1 Phase C source ports, exact original 131C geometry + paid 119 family.

Authorities (immutable, in JAN037 binary source archive):
  general_session_state_discovery_131c.py::build_events (exact mid ladder)
  jan_session_portfolio_131d.py::RESCUE_RULES (six source-specific grid sleeves)
  gamma02_dynamic_watchdog_router_119.py (first-scout/4 good child relock)
  gamma02_083_heat_parent_ownership_084.py::renewal_owned (successive q child)
  gamma02_jan_watchdog119_grid_layer_refinement_131a.py (q=1190, final=1100)

Source parity is CLAIMED only for 131C first-touch geometry. 119 routing below
is an ONLINE-FUNDED CONTRACT TEST ADAPTER, NOT ORIGINAL 075 PARENT GENERATOR
PARITY, broker-parity, or a completed original V1 L4 strategy reproduction.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from v1_funded_core_033 import Quote, Structure, Proposal, Position, Close, FundedEngine

US_DST_START_2026_MS = 1772953200000  # literal stmr_base.py original (2026 spring only)


@dataclass(frozen=True)
class LadderEvent:
    time_ms: int
    direction: int
    rung: int
    minute_ms: int


class Original131CSessionGridL1:
    """Exact online form of build_events(t, midpoint_raw, step_raw=250).

    Independent pure event manufacturer; L7 may reject financing but never
    erase shadow/first-touch intelligence. Session-dependent rules downstream.
    """
    def __init__(self, step_raw: int = 250):
        if step_raw <= 0: raise ValueError('Step must be positive')
        self.step_raw = step_raw
        self.minute = -1
        self.anchor = 0
        self.up = 0
        self.down = 0
        self.events = 0
        self._last_time = -1

    def on_tick(self, q: Quote) -> tuple[LadderEvent, ...]:
        if q.time_ms < self._last_time: raise ValueError('Non-monotone tick')
        self._last_time = q.time_ms
        minute = q.time_ms // 60000 * 60000
        mid = (q.ask_raw + q.bid_raw) // 2
        if minute != self.minute:
            self.minute = minute; self.anchor = mid; self.up = self.down = 0
            return ()
        du = mid - self.anchor
        dd = self.anchor - mid
        out = []
        # Two conditions can be evaluated separately (original build_events).
        if du >= self.up + self.step_raw:
            self.up = du // self.step_raw * self.step_raw
            out.append(LadderEvent(q.time_ms, 1, self.up, minute))
        if dd >= self.down + self.step_raw:
            self.down = dd // self.step_raw * self.step_raw
            out.append(LadderEvent(q.time_ms, -1, self.down, minute))
        self.events += len(out)
        return tuple(out)


# Original jan_session_portfolio_131d.RESCUE_RULES, no revised hindsight cells.
# These historically researched session sleeves belong to L1/L3, not native
# L6 recovery despite the historical variable name RESCUE_RULES.
ORIGINAL_131D_SESSION_SLEEVES = (
    ((2, 1, 1, -1, -1, 1), (12., 4., 300000), 'ASIA02_CONT'),
    ((7, 1, -1, -1, -1, 1), (0., 0., 120000), 'LONDON07_ROTATE_LONG'),
    ((10, 1, -1, -1, -1, 1), (0., 0., 120000), 'LONDON10_ROTATE_LONG'),
    ((13, 1, -1, 1, -1, -1), (12., 4., 300000), 'OVERLAP13_SHORT'),
    ((16, 1, -1, -1, -1, 1), (0., 0., 120000), 'OVERLAP16_LONG'),
    ((21, 1, -1, -1, -1, 1), (12., 4., 300000), 'LATE21_LONG'),
)


class Original131DSessionL3:
    """Physical admission adapter for original six 131D research rules.

    Uses the original 131C first-touch stream; 131D historical selection is
    an EXPOSED JANUARY fitted rule table, not a universal V1 default policy.
    Even declined physical entries do not erase ladder events.
    """
    def __init__(self, grid: Original131CSessionGridL1 | None = None):
        # Literal jan_session_portfolio_131d.build_rescue(step=75), not
        # the standalone 131C discovery default step=250.
        self.grid = grid or Original131CSessionGridL1(step_raw=75)
        self.source_candidates = 0
        self.shadow_ladder_events = 0
        self._pending_t = -1
        self._pending_events: tuple[LadderEvent, ...] = ()

    def on_market_quote(self, q: Quote, engine: FundedEngine) -> None:
        # Shadow L1 source event sequence persists through HTF outages.
        self._pending_events = self.grid.on_tick(q)
        self._pending_t = q.time_ms
        self.shadow_ladder_events += len(self._pending_events)

    def propose(self, q: Quote, s: Structure, engine: FundedEngine) -> Iterable[Proposal]:
        if self._pending_t != q.time_ms:
            # Standalone source entry-parity caller, not the event engine.
            self.on_market_quote(q, engine)
        events = self._pending_events
        utc_hour = q.time_ms // 3600000 % 24
        out = []
        for event in events:
            signature = (utc_hour, s.h4, s.h1, s.m15, s.m5, event.direction)
            for key, (tp, sl, ttl), name in ORIGINAL_131D_SESSION_SLEEVES:
                if signature == key:
                    self.source_candidates += 1
                    out.append(Proposal('L3', 'ORIG_131D_' + name,
                        s.grid_key, event.direction, tp, sl, ttl,
                        source_event_key=f'131C:{event.time_ms}:{event.direction}:{name}',priority=0))
        return out

    def on_funded_close(self, close: Close, engine: FundedEngine) -> None: pass


@dataclass
class FundedParentWindow:
    parent_id: int
    cell: str
    source: str
    direction: int
    admitted_at_ms: int
    deadline_ms: int
    active: bool = True


class Funded119WatchdogL4:
    """Original 119/131A earned-renewal gate coupled to actual L3 funded entry.

    Source-local gate is *not* the whole original 075/119 parent proposal logic.
    First real L3 parent -> one scout; successive physically funded 1190/1100
    child first-touches -> four fast profitable closes -> earned renewal;
    any slow/losing actual L4 child relocks. The actual L3 window must still
    be active. No frozen child outcome can manufacture successor events.
    """
    def __init__(self, *, parent_sources: tuple[str,...] = ('ORIGINAL_HB_019_UTC17',),
                 parent_quote_window_ms: int = 1800000):
        self.parent_sources = parent_sources
        self.parent_quote_window_ms = parent_quote_window_ms
        self.parents: dict[str, FundedParentWindow] = {}
        self.parent_by_id: dict[int, str] = {}
        self.funded_wd_by_id: dict[int,str] = {}
        self.history: list[tuple[int,str,str]] = []
        self.active_cells: set[str] = set()

    @staticmethod
    def original_119_key(q: Quote, s: Structure, side: int) -> str | None:
        # Original 119 January/February exact one-way spring offset, NOT an
        # assertion of robust all-year DST or Coinexx server clock parity.
        offset = -300 if q.time_ms < US_DST_START_2026_MS else -240
        local_minutes = (q.time_ms // 60000 + offset) % 1440
        local_hour = local_minutes // 60
        if not 12 <= local_hour <= 13:
            return None
        if s.h4 == 0 or s.h4 != s.h1 or side != s.h4:
            return None
        subphase = local_minutes % 60 // 10
        signature = ((s.h4+1)*81+(s.h1+1)*27+(s.m15+1)*9+
                     (s.m5+1)*3+(side+1))
        return f'119:{q.time_ms//86400000}:{local_hour}:{subphase}:{signature}'

    def on_funded_entry(self, pos: Position, q: Quote, s: Structure, engine: FundedEngine) -> None:
        if pos.layer == 'L4' and pos.source.startswith('ORIGINAL_119'):
            self.funded_wd_by_id[pos.id] = pos.cell
            self.history.append((q.time_ms, 'FUNDED_L4', pos.cell))
            return
        if pos.layer != 'L3' or pos.source not in self.parent_sources:
            return
        cell = self.original_119_key(q,s,pos.side)
        if cell is None: return
        # Original 119 first chronological parent per cell may scout; on a
        # rejected parent no on_funded_entry callback occurs at all.
        if cell not in self.parents:
            deadline = min(pos.expiry_ms, q.time_ms + self.parent_quote_window_ms)
            self.parents[cell] = FundedParentWindow(pos.id,cell,pos.source,pos.side,q.time_ms,deadline)
            self.active_cells.add(cell)
            self.parent_by_id[pos.id] = cell
            self.history.append((q.time_ms,'FUNDED_ORIGINAL_119_PARENT',cell))

    def propose(self, q: Quote, s: Structure, engine: FundedEngine) -> Iterable[Proposal]:
        props = []
        # Deterministic campaign order: set hash randomization must not affect
        # capital allocation when multiple funded parents are simultaneously eligible.
        for cell in sorted(self.active_cells):
            parent = self.parents[cell]
            if not parent.active or q.time_ms >= parent.deadline_ms:
                self.active_cells.discard(cell)
                continue
            if q.time_ms <= parent.admitted_at_ms:
                continue
            # Genuine parent still funded: no later phantom parent continuation.
            if parent.parent_id not in engine.positions:
                continue
            if any(p.layer=='L4' and p.cell==cell for p in engine.positions.values()):
                continue
            c = engine.campaigns[cell]
            if c.scout_consumed and not c.earned and c.scout_children_funded >= engine.limits.scout_family_budget:
                continue
            first = not c.earned
            if first:
                sponsor = parent.parent_id if not c.scout_consumed else c.scout_root_id
            else:
                sponsor = c.last_good_parent_id
            if sponsor is None or sponsor not in engine._funded_ids:
                continue
            local_minutes = (q.time_ms // 60000 + (-300 if q.time_ms < US_DST_START_2026_MS else -240)) % 1440
            b10 = local_minutes % 60 // 10
            quantum = 1.10 if b10 == 5 else 1.19  # original 131A q-map
            ttl = parent.deadline_ms - q.time_ms
            if ttl <= 0: continue
            props.append(Proposal('L4','ORIGINAL_119_FINITE_RENEWAL',cell,
                     parent.direction,quantum,0.0,ttl,parent_id=sponsor,
                     first_scout=first,requires_earned_watchdog=not first,
                     source_event_key=f'119_PHYSICAL:{cell}:{q.time_ms}',priority=1))
        return props

    def on_funded_close(self, close: Close, engine: FundedEngine) -> None:
        if close.position_id in self.parent_by_id:
            cell = self.parent_by_id[close.position_id]
            parent=self.parents[cell]
            parent.active=False
            self.active_cells.discard(cell)
            for pid,p in list(engine.positions.items()):
                if p.layer=='L4' and p.cell==cell:
                    engine.request_reduce(pid)
            self.history.append((close.time_ms,'FUNDED_PARENT_EXIT',cell))
        if close.position_id in self.funded_wd_by_id:
            cell=self.funded_wd_by_id.pop(close.position_id)
            earned=engine.campaigns[cell].earned
            self.history.append((close.time_ms,'FUNDED_CHILD_CLOSE_EARNED' if earned else 'FUNDED_CHILD_CLOSE_LOCKED',cell))