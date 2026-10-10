"""Executable source tape gate tests; offline oracle is not a live EA."""
import unittest
import numpy as np
from original_jan037_feb041_entry_tape_oracle_033 import OriginalSourceEntryTapeOracle

class EntryTapeIntegrity(unittest.TestCase):
    def test_two_same_quote_source_offers_keep_distinct_quote_ordinal(self):
        o=OriginalSourceEntryTapeOracle([5,5,5,6],[22,26,0,27],[1,-1,1,-1])
        self.assertEqual(o.on_observed_quote(4,4000,100000,100100),())
        first=o.on_observed_quote(5,5000,100100,100200)
        self.assertEqual([(x.quote_ordinal,x.offer_ordinal,x.source,x.side) for x in first],[(5,0,22,1),(5,1,26,-1),(5,2,0,1)])
        self.assertEqual(len(set(x.source_event_key for x in first)),3)
        self.assertEqual(len(o.on_observed_quote(6,6000,100100,100200)),1)
        o.assert_exhausted()
        self.assertEqual((o.source_offer_count,o.same_tick_extra_count,o.max_offers_in_quote),(4,2,3))

    def test_can_skip_empty_quotes_but_not_source_events(self):
        o=OriginalSourceEntryTapeOracle([5,7],[22,27],[1,-1])
        with self.assertRaisesRegex(ValueError,'Unconsumed'): o.on_observed_quote(6,6000,100000,100010)
        self.assertEqual(len(o.on_observed_quote(5,5000,100000,100010)),1)
        self.assertEqual(o.on_observed_quote(6,6000,100000,100010),())
        self.assertEqual(len(o.on_observed_quote(7,7000,100000,100010)),1)

    def test_no_future_source_exit_or_pnl_access_and_no_live_trades(self):
        e=[5,6]; s=[22,0]; d=[1,-1]
        o=OriginalSourceEntryTapeOracle(e,s,d)
        with self.assertRaises(NotImplementedError):o.emit_live_trade()
        self.assertFalse(hasattr(o,'X'));self.assertFalse(hasattr(o,'P'))
        self.assertFalse(hasattr(o,'future_return'))

    def test_invalid_chronology_types_and_side_fail_closed(self):
        for e,s,d in (([2,1],[22,22],[1,1]),([1,2],[22,22],[1,0]),([-1,3],[22,22],[1,1])):
            with self.assertRaises(ValueError):OriginalSourceEntryTapeOracle(e,s,d)
        with self.assertRaises(TypeError):OriginalSourceEntryTapeOracle([1.2],[22],[1])
        o=OriginalSourceEntryTapeOracle([5],[22],[1])
        with self.assertRaises(ValueError):o.on_observed_quote(4,4000,1000,999)
        o.on_observed_quote(5,5000,1000,1001)
        with self.assertRaises(ValueError):o.on_observed_quote(5,5000,1000,1001)
        with self.assertRaises(ValueError):o.on_observed_quote(6,4900,1000,1001)

    def test_unvisited_event_is_not_accidentally_certified(self):
        o=OriginalSourceEntryTapeOracle([3],[22],[1])
        with self.assertRaises(AssertionError):o.assert_exhausted()
        o.on_observed_quote(3,3000,1000,1002)
        o.assert_exhausted()

    def test_original_source_metadata_independent_of_month(self):
        def replay(ts):
            o=OriginalSourceEntryTapeOracle([2,2],[26,27],[1,-1])
            return [(x.offer_ordinal,x.quote_ordinal,x.source,x.side) for x in o.on_observed_quote(2,ts,1000,1001)]
        self.assertEqual(replay(1768000000000),replay(1770600000000))
        self.assertEqual(replay(1768000000000),replay(1775700000000))

if __name__=='__main__':unittest.main()
