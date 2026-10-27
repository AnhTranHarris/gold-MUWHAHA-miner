import pytest
from r34_mt5_demo_tick_observer import OrderedTickCollector,DemoFeedError

def mk(msc,bid=4500,ask=4501,flags=6):return {'time_msc':msc,'bid':bid,'ask':ask,'flags':flags}

def test_same_millisecond_stable_ordinal_without_dropping_duplicate():
 a=OrderedTickCollector();x=mk(1000);q=[x,x,mk(1001)]
 assert len(a.new_ticks(q))==3
 assert a.new_ticks(q)==[]
 assert len(a.new_ticks([mk(1001),mk(1001),mk(1002)]))==2
 assert a.ordinal==4

def test_same_millisecond_history_reorder_fails():
 a=OrderedTickCollector();a.new_ticks([mk(1000,4500),mk(1000,4501,4502)])
 with pytest.raises(DemoFeedError):a.new_ticks([mk(1000,4501,4502),mk(1000,4500)])

def test_broker_quote_spread_invalid():
 a=OrderedTickCollector()
 with pytest.raises(DemoFeedError):a.new_ticks([mk(1000,4502,4501)])

def test_input_not_sorted_rejected():
 a=OrderedTickCollector()
 with pytest.raises(DemoFeedError):a.new_ticks([mk(1002),mk(1001)])
