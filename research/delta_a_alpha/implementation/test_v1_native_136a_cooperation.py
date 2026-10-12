"""One global quote G0 arbitration across original 136B and native 136A."""
import unittest
from types import SimpleNamespace
from v1_vertical_grid import Quote,ClosedBar
from v1_creator_grid_genesis import GridOpportunity
from v1_grid_136b_cooperative_adapter import CooperativeGridGenesis
from v1_native_136a_minute_grid import Native136AMinuteGrid
T=1775055600000

def b(tf):return ClosedBar(tf,T-3600000,T,4400000,4403000,4397000,4401000,100)
def q(dt,mid):return Quote(T+dt,mid-100,mid+100)
class OriginalEmpty:
    ready=True
    parent=SimpleNamespace(parent=SimpleNamespace(cached_high=4403,cached_low=4397))
    def on_tick(self,*args,**kw):return ()
    def stats(self):return {}
class HourlyEmpty:
    def on_tick(self,*args,**kw):return ()
    def stats(self):return {}
class OriginalHit(OriginalEmpty):
    def on_tick(self,tick,*args,**kw):
        return (GridOpportunity(tick.time_ms_utc,1,1,4400.,4400.,4399.8,4403.,4397.,.5,'LONDON',0,'ORIGINAL_PARENT'),)
class CooperationTests(unittest.TestCase):
    def test_native_adds_only_otherwise_empty_quote(self):
        g=CooperativeGridGenesis(original_stack=OriginalEmpty(),hourly=HourlyEmpty())
        self.assertFalse(g.on_tick(q(0,4400000),b('H1'),'LONDON',last_completed_h4=b('H4')))
        e=g.on_tick(q(100,4400060),b('H1'),'LONDON',last_completed_h4=b('H4'))
        self.assertEqual(len(e),1)
        self.assertEqual(e[0].source,'APR136A_NATIVE_CAUSAL_MINUTE_EXTENSION_V1')
        self.assertEqual(g.native_handoffs,1)
    def test_original_priority_never_replaced(self):
        g=CooperativeGridGenesis(original_stack=OriginalHit(),hourly=HourlyEmpty())
        g.on_tick(q(0,4400000),b('H1'),'LONDON',last_completed_h4=b('H4'))
        e=g.on_tick(q(100,4400060),b('H1'),'LONDON',last_completed_h4=b('H4'))
        self.assertEqual(e[0].source,'ORIGINAL_PARENT')
        self.assertEqual(g.native_handoffs,0)
        self.assertEqual(g.native_priority_collisions,1)
    def test_no_native_when_h4_unknown(self):
        g=CooperativeGridGenesis(original_stack=OriginalEmpty(),hourly=HourlyEmpty())
        self.assertFalse(g.on_tick(q(0,4400000),b('H1'),'LONDON'))
        self.assertFalse(g.on_tick(q(100,4400060),b('H1'),'LONDON'))

if __name__=='__main__':unittest.main()
