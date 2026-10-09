"""C2D3E original 131D quote identity — independent minimal GitHub CI gate."""
from __future__ import annotations
import hashlib
import unittest
from pathlib import Path
from v1_funded_core_033c import Quote, Structure, Limits, FundedEngine
from original_online_sources_033c import ORIGINAL_131D_SESSION_SLEEVES
from original_131d_quote_ordinal_033 import Original131DOrdinalL3

SOURCE = Path(__file__).parent / "verified_original_sources" / "jan_session_portfolio_131d.py"
EXPECTED = "c612e0b71b777206b93447af17a4bdc3863a28a69334d416dc108bb1dd2e966f"

class SourceIdentityCI(unittest.TestCase):
    def test_frozen_jan032_131d_source_integrity(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), EXPECTED)
        self.assertEqual(len(ORIGINAL_131D_SESSION_SLEEVES), 6)

    def test_actual_l7_two_distinct_quotes_same_millisecond(self):
        t = 2 * 3600000
        s = Structure("ASIA", 1, 1, -1, -1, t - 1, "131C",
                      completed_bar_end_ms=(t-1,)*4)
        adapter = Original131DOrdinalL3()
        engine = FundedEngine(Limits(max_orders_per_second=2, max_orders_per_tick=1,
                max_spread_usd=1.0), [adapter], broker_contract_verified=True)
        for q in (Quote(t,100050,100000),Quote(t+10,100250,100200),
                  Quote(t+10,100400,100350)):
            engine.process_quote(q, s)
        self.assertEqual(adapter.source_candidates, 2)
        self.assertEqual(len(engine.positions), 2)
        self.assertEqual(engine.combined_order_rate_max, 2)
        self.assertEqual(len(set(p.source_event_key for p in engine.positions.values())), 2)
        self.assertEqual(engine.reject_counts.get("DUPLICATE_SOURCE_EVENT",0), 0)

if __name__ == "__main__":
    unittest.main()
