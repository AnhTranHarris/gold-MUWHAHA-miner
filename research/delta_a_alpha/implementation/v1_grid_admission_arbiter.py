"""Quote-scoped G0→L7 request arbiter for the existing V1 vertical engine.

G0 and L2-L6 research qualifications do not consume a funded-request cooldown.
A quote becomes owned only after L7's *pre-queue* broker/risk gates pass;
subsequent latency, margin and actual fills remain the existing L7 governor's job.
One timestamp may contain multiple source quotes, so same-ms quotes conservatively
share one request slot. No orders, price prediction, or physical exposure here.
"""
from __future__ import annotations
from typing import Optional


class GridQuoteArbiter:
    def __init__(self, cooldown_ms: int = 6000):
        if not isinstance(cooldown_ms, int) or cooldown_ms < 0:
            raise ValueError('cooldown_ms must be a nonnegative integer')
        self.cooldown_ms = cooldown_ms
        self.last_request_ms: dict[str, int] = {}
        self.last_ms: Optional[int] = None
        self.claimed = False
        self.quote_collisions = 0
        self.desk_cooldowns = 0
        self.eligible_requests = 0

    def start_quote(self, ms: int) -> None:
        if not isinstance(ms, int) or ms < 0:
            raise ValueError('invalid UTC millisecond timestamp')
        if self.last_ms is not None and ms < self.last_ms:
            raise ValueError('out-of-order grid quote')
        if ms != self.last_ms:
            self.last_ms = ms
            self.claimed = False

    def can_request(self, desk: str, ms: int) -> bool:
        self.start_quote(ms)
        if self.claimed:
            self.quote_collisions += 1
            return False
        if ms - self.last_request_ms.get(desk, -10**15) < self.cooldown_ms:
            self.desk_cooldowns += 1
            return False
        return True

    def claim_eligible_request(self, desk: str, ms: int) -> bool:
        """Atomic in the engine's single-threaded, ordered on_tick loop."""
        if not self.can_request(desk, ms):
            return False
        self.claimed = True
        self.last_request_ms[desk] = ms
        self.eligible_requests += 1
        return True
