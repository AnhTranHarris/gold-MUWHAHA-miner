"""R162: research-only hypothetical action-time first-touch receipt.
Never changes an original R9 order; no broker fill is asserted.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Quote:
    ts_ms: int
    bid: float
    ask: float

def action_touch(intent_ts_ms, action_ts_ms, side, submitted, pre_action, post_action,
                 favorable_usd, adverse_usd, horizon_ms=30000):
    """Hypothetical market entry at action-time ask (BUY) or bid (SELL).
    Strictly prior quote for entry; post-action quotes label future only.
    No use of historical correct/incorrect labels. Unresolved is censored.
    """
    if submitted or side not in (-1, 1) or not (intent_ts_ms+15000 <= action_ts_ms < intent_ts_ms+16000):
        raise ValueError("No legal unsubmitted T1 action")
    if not isinstance(horizon_ms, int) or horizon_ms <= 0:
        raise ValueError("Bad horizon")
    if not all(isfinite(x) and x > 0 for x in (favorable_usd, adverse_usd)):
        raise ValueError("Bad thresholds")
    if not pre_action:
        raise ValueError("No prior executable quote")
    last = -1
    for q in pre_action:
        if not (last < q.ts_ms < action_ts_ms and isfinite(q.bid) and isfinite(q.ask) and 0 < q.bid <= q.ask):
            raise ValueError("Invalid prior quotes")
        last = q.ts_ms
    entry = pre_action[-1].ask if side == 1 else pre_action[-1].bid
    last = action_ts_ms - 1
    result = "unresolved"
    for q in post_action:
        if not (q.ts_ms > last and isfinite(q.bid) and isfinite(q.ask) and 0 < q.bid <= q.ask):
            raise ValueError("Invalid future quotes")
        last = q.ts_ms
        if q.ts_ms < action_ts_ms or q.ts_ms >= action_ts_ms + horizon_ms:
            continue
        pnl = side * ((q.bid if side == 1 else q.ask) - entry)
        if result == "unresolved" and pnl >= favorable_usd:
            result = "favorable"
        elif result == "unresolved" and pnl <= -adverse_usd:
            result = "adverse"
    return {"outcome":result,"entry_price":entry,"action_ts_ms":action_ts_ms,
            "horizon_exclusive_ms":action_ts_ms+horizon_ms}

if __name__ == "__main__":
    import unittest
    class Tests(unittest.TestCase):
        def run_case(self, side=1, submitted=False, pre=None, post=None):
            return action_touch(100000,115000,side,submitted,
                pre if pre is not None else [Quote(114999,2000,2000.2)],
                post if post is not None else [Quote(115001,2001.3,2001.5)],1,1)
        def test_buy_touch(self): self.assertEqual(self.run_case()["outcome"],"favorable")
        def test_sell_touch(self): self.assertEqual(self.run_case(-1,post=[Quote(115001,1998,1998.5)])["outcome"],"favorable")
        def test_entry_at_action_not_t0(self):
            x=self.run_case(pre=[Quote(99999,1000,1000.2),Quote(114999,2000,2000.2)])
            self.assertEqual(x["entry_price"],2000.2)
        def test_horizon(self):
            self.assertEqual(self.run_case(post=[Quote(145000,2005,2005.2)])["outcome"],"unresolved")
        def test_submitted(self):
            with self.assertRaises(ValueError): self.run_case(submitted=True)
        def test_future_quote_in_prefix(self):
            with self.assertRaises(ValueError): self.run_case(pre=[Quote(115000,2000,2000.2)])
        def test_nonfinite(self):
            with self.assertRaises(ValueError): self.run_case(post=[Quote(115001,float("nan"),2001)])
        def test_first_adverse(self):
            self.assertEqual(self.run_case(post=[Quote(115001,1998,1998.2),Quote(115002,2005,2005.2)])["outcome"],"adverse")
        def test_label_independence(self):
            self.assertEqual(self.run_case(),self.run_case())
        def test_invalid_spread(self):
            with self.assertRaises(ValueError): self.run_case(pre=[Quote(114999,2001,2000)])
    unittest.main()
