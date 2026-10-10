"""DAA V1 L0-L7 endogenous *funded-state kernel* (033, incomplete parity).

This is a reusable deterministic execution subsystem, NOT a reproduction of all
original 049/051/075/084/119/131E/134K signal generators, nor a Coinexx fill model.
It accepts event-time source adapters and updates them only after a physical fill
or actually executed close. Original owner's V1 architecture is unchanged.

Units: Dukascopy ask_raw / bid_raw are 1/1000 USD; one 0.01-lot
100oz/lot XAUUSD contract yields 1 oz, so price move $1 = $1 profit.
"""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Callable, Iterable, Protocol


@dataclass(frozen=True)
class Quote:
    time_ms: int
    ask_raw: int
    bid_raw: int

    def __post_init__(self):
        if self.ask_raw < self.bid_raw or self.bid_raw <= 0:
            raise ValueError('Invalid executable Bid/Ask')


@dataclass(frozen=True)
class Structure:
    """Provided by ORIGINAL completed-HTF/geometry adapters, never calculated from future ticks."""
    session: str
    h4: int
    h1: int
    m15: int
    m5: int
    completed_until_ms: int
    grid_key: str
    phase: int = 0
    # Provenance for EACH completed H4, H1, M15 and M5 bar, respectively.
    completed_bar_end_ms: tuple[int, int, int, int] | None = None

    def valid_at(self, t: int) -> bool:
        return (self.completed_bar_end_ms is not None and len(self.completed_bar_end_ms) == 4
                and all(0 < end <= self.completed_until_ms < t for end in self.completed_bar_end_ms)
                and self.grid_key != '' and self.session != ''
                and all(x in (-1, 0, 1) for x in (self.h4, self.h1, self.m15, self.m5)))


@dataclass(frozen=True)
class Proposal:
    layer: str
    source: str
    cell: str
    side: int
    tp_usd: float
    sl_usd: float
    ttl_ms: int
    parent_id: int | None = None
    recovery_of: int | None = None
    first_scout: bool = False
    requires_earned_watchdog: bool = False
    # Original metadata and source IDs must be retained, no implicit source remapping.
    source_event_key: str = ''
    priority: int = 0  # Explicit as-of source priority; never fitted from future P/L here.

    def __post_init__(self):
        if self.layer not in ('L3', 'L4', 'L5', 'L6'):
            raise ValueError('Proposal has no owner source layer')
        if self.side not in (-1, 1) or self.tp_usd < 0 or self.sl_usd < 0 or self.ttl_ms <= 0:
            raise ValueError('Invalid finite, fixed-size opportunity')
        if self.layer == 'L6' and self.recovery_of is None:
            raise ValueError('Recovery must identify genuinely funded original')
        if self.layer == 'L4' and not (self.first_scout or self.requires_earned_watchdog):
            raise ValueError('Watchdog proposal must own scout or earned-child policy')


@dataclass
class Position:
    id: int
    layer: str
    source: str
    cell: str
    side: int
    entry_ms: int
    entry_raw: int
    tp_raw: int
    sl_raw: int
    expiry_ms: int
    parent_id: int | None
    recovery_of: int | None
    source_event_key: str
    best_favorable_usd: float = 0.0
    failure_seen: bool = False
    closed: bool = False


@dataclass(frozen=True)
class Close:
    position_id: int
    time_ms: int
    exit_raw: int
    net_usd: float
    held_ms: int
    reason: str
    source: str
    layer: str
    parent_id: int | None


@dataclass
class Campaign:
    streak: int = 0
    earned: bool = False
    relocks: int = 0
    last_realized_ms: int = -1
    last_good_parent_id: int | None = None
    depth: int = 0
    scout_consumed: bool = False
    scout_root_id: int | None = None
    scout_children_funded: int = 0


@dataclass(frozen=True)
class Limits:
    balance_usd: float = 100000.0
    fixed_lot: float = 0.01
    contract_oz_per_lot: float = 100.0
    leverage: float = 500.0
    commission_roundtrip_usd: float = 0.02
    max_open: int = 512
    max_layer_open: int = 512
    max_per_source_open: int = 512
    max_same_direction: int = 512
    max_per_cell_side: int = 32
    max_orders_per_second: int = 3
    max_orders_per_tick: int = 1
    max_spread_usd: float = 3.0
    max_equity_drawdown_usd: float = 25000.0
    max_margin_fraction_of_equity: float = 0.3
    max_underwater_open_usd: float = 25000.0
    min_scout_funded_wins: int = 4
    good_hold_ms: int = 60000
    max_watchdog_depth: int = 30
    scout_family_budget: int = 4
    max_recoveries_per_predecessor: int = 1
    recovery_permission_window_ms: int = 120000
    reserve_stopout_fraction: float = 0.5
    fail_closed_broker: bool = True

    def __post_init__(self):
        if self.fixed_lot != 0.01 or min(self.contract_oz_per_lot, self.leverage) <= 0:
            raise ValueError('V1 fixed 0.01 lot and valid explicit contract/leverage required')
        if min(self.max_open, self.max_layer_open, self.max_per_source_open, self.max_same_direction, self.max_per_cell_side,
               self.max_orders_per_second, self.max_orders_per_tick) <= 0:
            raise ValueError('Bad exposure/order caps')
        if not 0 < self.max_margin_fraction_of_equity < 1 or not 0 < self.reserve_stopout_fraction < 1:
            raise ValueError('Bad risk constraints')


class SourceAdapter(Protocol):
    def propose(self, q: Quote, s: Structure, engine: 'FundedEngine') -> Iterable[Proposal]: ...
    def on_funded_close(self, close: Close, engine: 'FundedEngine') -> None: ...


class FundedEngine:
    """One account, all L3-L6 owners, all close and fill decisions ordered by quote.

    Broker-independent idealized instantaneous quote-side fills. A broker adapter
    must replace this idealization, and validate actual account hedging, order queue,
    permissions and margin before *any* economic promotion.
    """
    def __init__(self, limits: Limits, adapters: list[SourceAdapter] | None = None,
                 *, broker_contract_verified: bool = False):
        self.limits = limits
        self.adapters = adapters or []
        self.broker_contract_verified = broker_contract_verified
        self.balance = limits.balance_usd
        self.equity = limits.balance_usd
        self.peak_equity = self.equity
        self.dd_max = 0.0
        self.balance_peak = self.balance
        self.balance_dd = 0.0
        self.gross_profit = 0.0
        self.gross_loss = 0.0
        self.positions: dict[int, Position] = {}
        self.closed: list[Close] = []
        self.campaigns: dict[str, Campaign] = defaultdict(Campaign)
        self.events: list[dict] = []
        self._next_id = 1
        self._last_t = -1
        self._sec = -1
        self._sec_orders = 0
        self._tick_orders = 0
        self._seen_events: set[str] = set()
        self._funded_ids: set[int] = set()
        self._failures: dict[int, int] = {}
        self._recovery_counts: dict[int, int] = defaultdict(int)
        self._last_quote: Quote | None = None
        self._reduction_queue: deque[int] = deque()
        # Conditional FEB047 requests are re-priced at the *actual* close tick.
        # Existing unconditional L7 safety reductions retain their old semantics.
        self._profit_reduce_guards: dict[int, float] = {}
        self.max_open = 0
        self.reject_counts: dict[str, int] = defaultdict(int)
        self.invalid_recoveries = 0
        self._ready_since: int | None = None
        self.readiness_deadline_missed = False
        self.had_ready_context = False
        self.history_missing = 0
        self.combined_order_rate_max = 0

    @property
    def one_oz_size(self) -> float:
        return self.limits.fixed_lot * self.limits.contract_oz_per_lot

    def _assert_time(self, q: Quote) -> None:
        if q.time_ms < self._last_t:
            raise ValueError('Out-of-order quote')
        self._last_t = q.time_ms
        sec = q.time_ms // 1000
        if sec != self._sec:
            self._sec = sec
            self._sec_orders = 0
        self._tick_orders = 0
        self._last_quote = q

    def _mark(self, p: Position, q: Quote) -> float:
        raw = q.bid_raw if p.side == 1 else q.ask_raw
        return (raw - p.entry_raw) * p.side / 1000 * self.one_oz_size

    def _mark_account(self, q: Quote) -> None:
        floating = sum(self._mark(p, q) for p in self.positions.values())
        # Entry commissions have already been charged; reserve future exit fee at marks.
        self.equity = self.balance + floating - len(self.positions) * self.limits.commission_roundtrip_usd / 2
        self.peak_equity = max(self.peak_equity, self.equity)
        self.dd_max = max(self.dd_max, self.peak_equity - self.equity)
        self.balance_peak = max(self.balance_peak, self.balance)
        self.balance_dd = max(self.balance_dd, self.balance_peak - self.balance)

    def _margin(self, q: Quote) -> float:
        notional = (q.ask_raw / 1000) * self.one_oz_size
        return notional / self.limits.leverage

    def _order_room(self) -> bool:
        return (self._sec_orders < self.limits.max_orders_per_second and
                self._tick_orders < self.limits.max_orders_per_tick)

    def _use_order(self) -> None:
        self._sec_orders += 1
        self._tick_orders += 1
        self.combined_order_rate_max = max(self.combined_order_rate_max, self._sec_orders)

    def _reject(self, reason: str, q: Quote, p: Proposal | None = None) -> None:
        self.reject_counts[reason] += 1
        self.events.append(dict(t=q.time_ms, event='DENY', reason=reason, layer=p.layer if p else 'L7',
                                source=p.source if p else None, cell=p.cell if p else None))

    def _funded_child_gate(self, p: Proposal) -> bool:
        if p.recovery_of is not None:
            # No shadow predecessor, unobserved failure, or unbounded rescue additions.
            return (p.recovery_of in self._funded_ids and p.recovery_of in self._failures
                    and self._last_quote is not None and 0 <= self._last_quote.time_ms - self._failures[p.recovery_of] <= self.limits.recovery_permission_window_ms
                    and self._recovery_counts[p.recovery_of] < self.limits.max_recoveries_per_predecessor)
        if p.parent_id is not None and p.parent_id not in self._funded_ids:
            return False
        if p.layer == 'L4':
            if p.source.startswith('ORIGINAL_119') and p.parent_id is None:
                # Native Watchdog must never bootstrap from a shadow-only parent.
                return False
            c = self.campaigns[p.cell]
            if p.first_scout:
                if not c.scout_consumed:
                    # A scout can be anchored to an actual funded L3 parent.
                    # Never let a denied/shadow parent sponsor an L4 scout.
                    return p.parent_id is None or p.parent_id in self._funded_ids
                # One genuine funded scout-root family can have finitely many
                # separately accepted children before earned renewal.
                return (p.parent_id == c.scout_root_id and p.parent_id in self._funded_ids
                        and c.scout_children_funded < self.limits.scout_family_budget)
            return c.earned and c.depth < self.limits.max_watchdog_depth and c.last_good_parent_id is not None and p.parent_id == c.last_good_parent_id
        return True

    def _admission_reason(self, q: Quote, s: Structure, p: Proposal) -> str | None:
        if self._last_quote != q or self._sec != q.time_ms // 1000:
            return 'NOT_CURRENT_QUOTE'
        if not self.broker_contract_verified and self.limits.fail_closed_broker:
            return 'BROKER_CONTRACT_UNKNOWN'
        if not s.valid_at(q.time_ms) or not self.had_ready_context:
            return 'NO_COMPLETED_HTF'
        if not self._funded_child_gate(p):
            return 'UNFUNDED_OR_UNEARNED_GENEALOGY'
        if not self._order_room():
            return 'ORDER_RATE'
        if (q.ask_raw - q.bid_raw) / 1000 > self.limits.max_spread_usd:
            return 'SPREAD'
        if len(self.positions) >= self.limits.max_open:
            return 'GLOBAL_CAP'
        if sum(x.layer == p.layer for x in self.positions.values()) >= self.limits.max_layer_open:
            return 'LAYER_CAP'
        if sum(x.source == p.source for x in self.positions.values()) >= self.limits.max_per_source_open:
            return 'SOURCE_CAP'
        if sum(x.side == p.side for x in self.positions.values()) >= self.limits.max_same_direction:
            return 'SIDE_CAP'
        if sum(x.cell == p.cell and x.side == p.side for x in self.positions.values()) >= self.limits.max_per_cell_side:
            return 'CELL_CAP'
        if self.peak_equity - self.equity >= self.limits.max_equity_drawdown_usd:
            return 'EQUITY_REDUCE_ONLY'
        # Incremental adverse heat uses a finite, explicit per-ticket stress quantum.
        current_heat = sum(max(0.0, -self._mark(x, q)) for x in self.positions.values())
        if current_heat + p.sl_usd * self.one_oz_size > self.limits.max_underwater_open_usd:
            return 'PORTFOLIO_HEAT'
        requested_margin = self._margin(q)
        total_margin = requested_margin * (len(self.positions) + 1)
        if (self.equity <= 0 or total_margin >= self.equity * self.limits.max_margin_fraction_of_equity
                or self.equity - total_margin < self.limits.balance_usd * (1 - self.limits.reserve_stopout_fraction)):
            return 'INSUFFICIENT_MARGIN_OR_EQUITY'
        if p.source_event_key and p.source_event_key in self._seen_events:
            return 'DUPLICATE_SOURCE_EVENT'
        return None

    def enter(self, q: Quote, s: Structure, p: Proposal) -> int | None:
        reason = self._admission_reason(q, s, p)
        if reason:
            self._reject(reason, q, p)
            return None
        eid = self._next_id
        self._next_id += 1
        entry_raw = q.ask_raw if p.side == 1 else q.bid_raw
        self.positions[eid] = Position(eid, p.layer, p.source, p.cell, p.side, q.time_ms, entry_raw,
                                       int(round(p.tp_usd * 1000 / self.one_oz_size)),
                                       int(round(p.sl_usd * 1000 / self.one_oz_size)),
                                       q.time_ms + p.ttl_ms, p.parent_id, p.recovery_of, p.source_event_key)
        self.balance -= self.limits.commission_roundtrip_usd / 2
        self._funded_ids.add(eid)
        self._use_order()
        if p.source_event_key:
            self._seen_events.add(p.source_event_key)
        if p.layer == 'L4':
            c = self.campaigns[p.cell]
            if p.first_scout:
                if not c.scout_consumed:
                    c.scout_root_id = eid
                    c.scout_consumed = True
                else:
                    c.scout_children_funded += 1
            else:
                c.depth += 1
                # Original 119 parent-cell gate changes on realized child CLOSE,
                # not on entry. Keep earned credit until observed bad/slow close.
        if p.recovery_of is not None:
            self._recovery_counts[p.recovery_of] += 1
        self.max_open = max(self.max_open, len(self.positions))
        self.events.append(dict(t=q.time_ms, event='FILL', id=eid, source=p.source, layer=p.layer,
                                cell=p.cell, parent_id=p.parent_id, raw=entry_raw))
        # Only a physically accepted fill can create a live downstream parent.
        # Older source adapters without a funded-entry callback remain compatible.
        for adapter in self.adapters:
            callback = getattr(adapter, 'on_funded_entry', None)
            if callback is not None:
                callback(self.positions[eid], q, s, self)
        return eid

    def _finish(self, q: Quote, pid: int, reason: str) -> Close:
        p = self.positions.pop(pid)
        self._profit_reduce_guards.pop(pid, None)
        p.closed = True
        price = q.bid_raw if p.side == 1 else q.ask_raw
        gross = (price - p.entry_raw) * p.side / 1000 * self.one_oz_size
        self.balance += gross - self.limits.commission_roundtrip_usd / 2
        pnl = gross - self.limits.commission_roundtrip_usd
        if pnl > 0:
            self.gross_profit += pnl
        else:
            self.gross_loss += pnl
        c = Close(pid, q.time_ms, price, pnl, q.time_ms - p.entry_ms, reason, p.source, p.layer, p.parent_id)
        self.closed.append(c)
        self._use_order()
        self.events.append(dict(t=q.time_ms, event='CLOSE', id=pid, pnl=round(pnl, 8), reason=reason))
        if p.layer == 'L4':
            # Other L3/L5/L6 wins do not magically pay an L4 renewal child.
            campaign = self.campaigns[p.cell]
            good = pnl > 0 and c.held_ms <= self.limits.good_hold_ms
            campaign.streak = campaign.streak + 1 if good else 0
            campaign.earned = campaign.streak >= self.limits.min_scout_funded_wins
            if good:
                campaign.last_good_parent_id = pid
            else:
                campaign.relocks += 1
                campaign.last_good_parent_id = None
                campaign.depth = 0
            campaign.last_realized_ms = q.time_ms
        # Recovery permission cannot be created from an unfilled or merely shadowed signal.
        for adapter in self.adapters:
            adapter.on_funded_close(c, self)
        return c

    def mark_failure(self, p_id: int, q: Quote, s: Structure, *,
                     min_elapsed_ms: int = 1000, min_adverse_usd: float = 0.2) -> bool:
        """L6 failure evidence must be BOTH funded AND already observable.

        This generic invariant is not the final original recovery strategy:
        source-owned structural reclaim / native phase gates are also required
        inside the original L6 adapter before it may propose any recovery.
        """
        p = self.positions.get(p_id)
        if (p is None or self._last_quote != q or min_elapsed_ms <= 0 or min_adverse_usd <= 0
                or q.time_ms < p.entry_ms + min_elapsed_ms or not s.valid_at(q.time_ms)
                or s.m5 != -p.side or self._mark(p, q) > -min_adverse_usd):
            return False
        p.failure_seen = True
        self._failures[p_id] = q.time_ms
        self.events.append(dict(t=q.time_ms, event='OBSERVED_FUNDED_FAILURE', id=p_id,
                                observed_adverse_usd=round(self._mark(p, q), 6),
                                h1=s.h1, m15=s.m15, m5=s.m5))
        return True

    def request_reduce(self, pid: int) -> None:
        if pid in self.positions:
            # An unconditional safety/stop-out reduction takes precedence over
            # any optional FEB047 profit floor on this physical position.
            self._profit_reduce_guards.pop(pid, None)
            if pid not in self._reduction_queue:
                self._reduction_queue.append(pid)

    def request_profit_reduce(self, pid: int, *, minimum_net_usd: float) -> None:
        """FEB047 conditional physical order, never a shadow or guaranteed-profit close.

        The original FEB047 strict queue checks profit at each observed executable
        Bid/Ask quote.  Funding/order rate may delay an actual close; the original
        request must therefore RECHECK its floor immediately before settlement.
        Stale, no-longer-profitable queued reductions are cancelled, not filled.
        The pre-existing unconditional request_reduce remains a safety action.
        """
        if minimum_net_usd < 0 or not isfinite(minimum_net_usd):
            raise ValueError('FEB047 profit floor must be finite and nonnegative')
        if pid in self.positions:
            # An existing UNCONDITIONAL safety order owns this position.
            # Optional profit protection may never downgrade it to conditional.
            if (pid in self._reduction_queue and
                pid not in self._profit_reduce_guards):
                return
            if pid not in self._reduction_queue:
                self._reduction_queue.append(pid)
            self._profit_reduce_guards[pid] = float(minimum_net_usd)

    def process_quote(self, q: Quote, s: Structure | None, *, proposals: Iterable[Proposal] = (),
                      max_new_per_tick: int = 1) -> None:
        """Single funded quote loop: protective exits NEVER require new HTF readiness.

        Even if pre-start history becomes unavailable, an existing funded position
        remains exposed to every Bid/Ask quote and its TP/SL/timeout/reduce orders
        must be attempted.  Only *new* source proposals fail closed without a
        complete, as-of L2 structural state.  This separation is a V1 L0/L7
        safety invariant, not a new trading strategy.
        """
        self._assert_time(q)
        # Original L1 first-touch intelligence must see ALL real quote events,
        # including during missing higher-timeframe history. Trading eligibility
        # is checked separately after protective position management.
        for adapter in self.adapters:
            tick_callback = getattr(adapter, 'on_market_quote', None)
            if tick_callback is not None:
                tick_callback(q, self)
        if self._ready_since is None:
            self._ready_since = q.time_ms
        valid_context = s is not None and s.valid_at(q.time_ms)
        if valid_context:
            self.had_ready_context = True
        else:
            self.history_missing += 1
            if q.time_ms - self._ready_since > 300000 and not self.had_ready_context:
                self.readiness_deadline_missed = True

        # Record the executable price mark BEFORE taking protective exits.  This
        # captures transient underwater inventory even at an exit tick.
        self._mark_account(q)
        to_exit: list[tuple[int, str]] = []
        for pid, p in list(self.positions.items()):
            pnl = self._mark(p, q)
            p.best_favorable_usd = max(p.best_favorable_usd, pnl)
            if p.tp_raw > 0 and pnl >= p.tp_raw / 1000 * self.one_oz_size:
                to_exit.append((pid, 'TP'))
            elif p.sl_raw > 0 and pnl <= -p.sl_raw / 1000 * self.one_oz_size:
                to_exit.append((pid, 'SL'))
            elif q.time_ms >= p.expiry_ms:
                to_exit.append((pid, 'TIME'))
        reductions_at_quote = len(self._reduction_queue)
        to_exit_ids = {pid for pid, _ in to_exit}
        for _ in range(reductions_at_quote):
            pid = self._reduction_queue.popleft()
            if pid in self.positions and pid not in to_exit_ids:
                guarded = pid in self._profit_reduce_guards
                if guarded:
                    floor = self._profit_reduce_guards[pid]
                    executable_net = (self._mark(self.positions[pid], q)
                                      - self.limits.commission_roundtrip_usd)
                    if executable_net + 1e-9 < floor:
                        self._profit_reduce_guards.pop(pid, None)
                        self.events.append(dict(t=q.time_ms, event='CANCEL', id=pid,
                            reason='FEB047_PROFIT_FLOOR_NOT_EXECUTABLE'))
                        continue
                to_exit.append((pid, 'FEB047_PROFIT_REDUCE' if guarded else 'L7_REDUCE'))
                to_exit_ids.add(pid)
        for pid, reason in to_exit:
            if not self._order_room():
                if reason == 'FEB047_PROFIT_REDUCE':
                    self.request_profit_reduce(pid,
                        minimum_net_usd=self._profit_reduce_guards[pid])
                else:
                    self.request_reduce(pid)
                continue
            self._finish(q, pid, reason)
        self._mark_account(q)
        if self.peak_equity - self.equity >= self.limits.max_equity_drawdown_usd:
            for pid in list(self.positions):
                self.request_reduce(pid)

        if not valid_context:
            # No new L3/L4/L5/L6 activity; actual close feedback above remains
            # visible to the source adapters, but no speculative shadow credit.
            return
        queue = list(proposals)
        for adapter in self.adapters:
            queue.extend(adapter.propose(q, s, self))
        queue.sort(key=lambda candidate: -candidate.priority)
        new_count = 0
        for p in queue:
            if new_count >= max_new_per_tick:
                self._reject('SOURCE_PER_TICK_SINGLE_OWNER', q, p)
                continue
            if self.enter(q, s, p) is not None:
                new_count += 1
        self._mark_account(q)

    def score(self) -> dict:
        total = self.gross_profit + self.gross_loss
        return dict(net=round(total, 8), gross_profit=round(self.gross_profit, 8),
                    gross_loss=round(self.gross_loss, 8),
                    profit_factor=round(self.gross_profit / -self.gross_loss, 8) if self.gross_loss < 0 else None,
                    trades=len(self.closed), open_positions=len(self.positions), max_open=self.max_open,
                    max_equity_dd=round(self.dd_max, 8), max_balance_dd=round(self.balance_dd, 8),
                    combined_max_orders_sec=self.combined_order_rate_max,
                    rejected=dict(self.reject_counts), month_blind=True,
                    funded_recovery_count=sum(1 for x in self.closed if x.layer == 'L6'),
                    history_missing_quotes=self.history_missing,
                    idle_funding_source_returns_prevented=True,
                    model='DETERMINISTIC_BIDASK_IDEALIZED_RESEARCH_KERNEL_NOT_V1_SOURCE_PARITY')


class NullAdapter:
    def propose(self, q: Quote, s: Structure, engine: FundedEngine) -> Iterable[Proposal]:
        return ()
    def on_funded_close(self, close: Close, engine: FundedEngine) -> None:
        return None


class OriginalHourlyHeartbeatL3:
    """Online entry-only adapter reconstructed from ORIGINAL 019 heartbeat candidates.

    Provenance: `research/R9_GAMMA/helpers/gamma02_campaign_heartbeat_019.py`
    ORIGINAL UTC-hour semantics (do not silently replace by locale clock).
    Its L3 candidate manufacture is causal; selection/campaign economics are NOT
    parity-certified with the entire original Jan 131E/Feb 134K hierarchy.
    """
    THR = (0, 0, 0, 0, 0, 0, 0, 1000, 3000, 0, 0, 2000, 0, 4000, 4000, 3000, 0, 0, 0, 0, 0, 0, 0, 0)
    NY17_MIN = (8000, 8000, 6000, 3000, 1000, 0)
    NY18_MIN = (0, 0, 500, 500, 2000, 1000)
    NY18_MAX = (10**9, 10**9, 10**9, 10**9, 10**9, 6000)
    TP16 = (40000, 0, 40000, 40000, 40000, 0)
    SL16 = (20000, 40000, 40000, 60000, 60000, 40000)
    H16 = (1200000, 1200000, 900000, 1200000, 1200000, 1200000)
    TP17 = (80000, 80000, 120000, 80000, 0, 120000)
    SL17 = (40000, 40000, 60000, 40000, 60000, 120000)
    H17 = (1800000,) * 6
    TP18 = (12000, 12000, 12000, 8000, 4000, 4000)
    SL18 = (8000, 8000, 6000, 8000, 1000, 2000)
    H18 = (60000, 60000, 20000, 30000, 5000, 10000)

    def __init__(self, interval_ms: int = 50):
        self.interval_ms = interval_ms
        self.minute = -1
        self.anchor = 0
        self.last_fire = [-10**18] * 24
        self.was_eligible = [False] * 24

    @staticmethod
    def london_rule(hour: int, h4: int, h1: int, m15: int, m5: int) -> int:
        if h4 != 1 or h1 != 1:
            return 0
        if hour == 7 and m15 == -1 and m5 == -1: return 1800000
        if hour == 8:
            if m15 == -1 and m5 == -1: return 300000
            if m15 == -1 and m5 == 1: return 900000
        if hour == 9 and ((m15 == -1 and m5 == -1) or (m15 == 1 and m5 == -1)): return 1800000
        if hour == 11:
            if m15 == -1 and m5 == -1: return 1800000
            if m15 == -1 and m5 == 1: return 1800000
            if m15 == 1 and m5 == -1: return 900000
        if hour == 12:
            if m15 == -1 and m5 == -1: return 1800000
            if m15 == -1 and m5 == 1: return 900000
            if m15 == 1 and m5 == -1: return 1800000
        if hour == 13 and ((m15 == -1 and m5 == -1) or (m15 == -1 and m5 == 1) or (m15 == 1 and m5 == -1)): return 1800000
        if hour == 14:
            if m15 == -1 and m5 == -1: return 1800000
            if m15 == -1 and m5 == 1: return 900000
        if hour == 15 and ((m15 == -1 and m5 == 1) or (m15 == 1 and m5 == -1) or (m15 == 1 and m5 == 1)): return 1800000
        return 0

    @staticmethod
    def ny_dir(hour: int, h4: int, h1: int, m15: int, m5: int) -> int:
        if hour == 16:
            if h4 == -1 and h1 == -1 and m15 == -1 and m5 == -1: return -1
            if h4 == 1 and h1 == 1 and m15 == 1 and m5 == -1: return 1
            if h4 == 1 and h1 == 1 and m15 == -1 and m5 == 1: return 1
        elif hour == 17:
            if h4 == -1 and h1 == -1 and m15 == -1 and m5 == -1: return -1
            if h4 == 1 and h1 == 1 and m15 == -1 and m5 == -1: return 1
        elif hour == 18:
            if h4 == -1 and h1 == -1 and m15 == -1 and m5 == -1: return -1
        return 0

    def propose(self, q: Quote, s: Structure, engine: FundedEngine) -> Iterable[Proposal]:
        minute = (q.time_ms // 60000) * 60000
        hour = (q.time_ms // 3600000) % 24
        b10 = (q.time_ms // 600000) % 6
        mid = (q.ask_raw + q.bid_raw) // 2
        if minute != self.minute:
            self.minute = minute
            self.anchor = mid
        eligible = False
        side = 0
        ttl = 0
        tp = 0
        sl = 0
        if hour <= 15:
            ttl = self.london_rule(hour, s.h4, s.h1, s.m15, s.m5)
            if ttl > 0 and mid - self.anchor >= self.THR[hour]:
                eligible = True
                side = 1
        elif hour in (16, 17, 18):
            side = self.ny_dir(hour, s.h4, s.h1, s.m15, s.m5)
            if side:
                disp = (mid - self.anchor) * side
                if hour == 16 and disp >= 500:
                    eligible = True; ttl = self.H16[b10]; tp = self.TP16[b10]; sl = self.SL16[b10]
                elif hour == 17 and disp >= self.NY17_MIN[b10]:
                    eligible = True; ttl = self.H17[b10]; tp = self.TP17[b10]; sl = self.SL17[b10]
                elif hour == 18 and self.NY18_MIN[b10] <= disp < self.NY18_MAX[b10]:
                    eligible = True; ttl = self.H18[b10]; tp = self.TP18[b10]; sl = self.SL18[b10]
        if not eligible:
            self.was_eligible[hour] = False
            return ()
        if not self.was_eligible[hour] or q.time_ms - self.last_fire[hour] >= self.interval_ms:
            self.last_fire[hour] = q.time_ms
            self.was_eligible[hour] = True
            # Raw 019 prices are thousandths USD; proposal TP/SL in USD per 0.01 lot.
            p = Proposal('L3', f'ORIGINAL_HB_019_UTC{hour:02d}', s.grid_key, side,
                         tp/1000, sl/1000, ttl, source_event_key=f'HB019:{q.time_ms}:{hour}')
            return (p,)
        self.was_eligible[hour] = True
        return ()

    def on_funded_close(self, close: Close, engine: FundedEngine) -> None:
        pass
