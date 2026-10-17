"""Source-isolated, as-of-time specialist evidence book for experimental HTF EA.

It cannot open, fill or close broker orders. Future realized outcomes cannot
change routing scores until their explicit chronological maturity timestamp.
Research-only; broker-specific calibration must not mix tapes/capital.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from heapq import heappop, heappush
from math import sqrt, isfinite


@dataclass(frozen=True, slots=True)
class ClosedOutcome:
    broker: str
    specialist: str
    observed_ms: int
    mature_ms: int
    aftercost_net_usd: float
    # if this is a counterfactual shadow result, it is not a filled live trade
    shadow: bool = False

    def __post_init__(self) -> None:
        if not self.broker or not self.specialist or not isfinite(self.aftercost_net_usd):
            raise ValueError("invalid outcome identity or P&L")
        if (not isinstance(self.observed_ms, int) or
                not isinstance(self.mature_ms, int) or
                self.observed_ms < 0 or self.mature_ms < self.observed_ms):
            raise ValueError("invalid outcome chronology")


@dataclass(frozen=True, slots=True)
class MatureScore:
    broker: str
    specialist: str
    observations: int
    mean_net_usd: float
    conservative_net_usd: float
    # Shadow evidence is separately counted to prevent it being called executed P&L.
    shadow_observations: int


class MaturedOpportunityBook:
    """Bounded trailing evidence for AFTER-COST outcomes, never future labels.

    Simulators can submit an outcome at observation-time but it becomes visible
    only once its actual first-hit/time-expiry has elapsed. Live deployments
    should instead submit real outcomes at close. Other broker's prices never
    enter this book, even as counterfactuals.
    """

    def __init__(self, broker: str, observations_per_specialist: int = 180):
        if not broker or observations_per_specialist < 2:
            raise ValueError("invalid broker or evidence horizon")
        self.broker = broker
        self.cap = observations_per_specialist
        self.last_ms: int | None = None
        self._counter = 0
        self._pending: list[tuple[int, int, ClosedOutcome]] = []
        self._outcomes: dict[str, deque[ClosedOutcome]] = defaultdict(
            lambda: deque(maxlen=self.cap))

    def enqueue(self, outcome: ClosedOutcome) -> None:
        if outcome.broker != self.broker:
            raise ValueError("cross-broker outcome contamination")
        # Also prevents history edits after the system's as-of-time watermark.
        if self.last_ms is not None and outcome.observed_ms < self.last_ms:
            raise ValueError("cannot backfill a past observation")
        heappush(self._pending, (outcome.mature_ms, self._counter, outcome))
        self._counter += 1

    def advance(self, now_ms: int) -> int:
        if now_ms < 0 or (self.last_ms is not None and now_ms < self.last_ms):
            raise ValueError("out-of-order evidence clock")
        self.last_ms = now_ms
        matured = 0
        while self._pending and self._pending[0][0] <= now_ms:
            _, _, x = heappop(self._pending)
            self._outcomes[x.specialist].append(x)
            matured += 1
        return matured

    def score(self, specialist: str, minimum: int = 30,
              uncertainty_z: float = 1.64) -> MatureScore | None:
        if minimum < 2 or uncertainty_z < 0:
            raise ValueError("invalid evidence bound")
        xs = list(self._outcomes.get(specialist, ()))
        if len(xs) < minimum:
            return None
        mean = sum(x.aftercost_net_usd for x in xs) / len(xs)
        var = sum((x.aftercost_net_usd-mean)**2 for x in xs)/len(xs)
        bound = mean - uncertainty_z * sqrt(var/len(xs))
        return MatureScore(self.broker, specialist, len(xs),
                           mean, bound, sum(x.shadow for x in xs))

    def ranked(self, minimum: int = 30, uncertainty_z: float = 1.64
               ) -> list[MatureScore]:
        scores = (self.score(name, minimum, uncertainty_z)
                  for name in self._outcomes)
        return sorted((x for x in scores if x is not None),
                      key=lambda x: (-x.conservative_net_usd,
                                     -x.observations, x.specialist))
