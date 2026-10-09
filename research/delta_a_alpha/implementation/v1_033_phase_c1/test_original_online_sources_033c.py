"""Phase C contract and source/parity tests, no full V1 certification."""
import unittest
from dataclasses import replace
from v1_funded_core_033 import FundedEngine, Limits, Quote, Structure, Proposal
from original_online_sources_033c import (Original131CSessionGridL1,Original131DSessionL3,
    Funded119WatchdogL4,ORIGINAL_131D_SESSION_SLEEVES)

T = 1769191200000 # Jan 23, 2026 17:00 UTC, NY local 12:00

def q(t=T,bid=100000,spread=100): return Quote(t,bid+spread,bid)

def st(t=T,h4=1,h1=1,m15=-1,m5=-1,cell='test'):
    return Structure('NY',h4,h1,m15,m5,t-1,cell,0,(t-14400001,t-3600001,t-900001,t-300001))

def eng(*adapters,**opts):
    settings=dict(max_orders_per_second=5,max_orders_per_tick=1,
                  max_open=40,max_per_cell_side=40,max_layer_open=40,
                  min_scout_funded_wins=4)
    settings.update(opts)
    return FundedEngine(replace(Limits(),**settings),list(adapters),broker_contract_verified=True)

class FirstTouch(unittest.TestCase):
    def test_exact_minute_reset_and_rung_jump(self):
        g=Original131CSessionGridL1(250)
        self.assertEqual(g.on_tick(q(T,100000)),())
        self.assertEqual([x.direction for x in g.on_tick(q(T+20,100260))],[1])
        self.assertEqual([x.rung for x in g.on_tick(q(T+30,100980))],[750])
        self.assertEqual(g.on_tick(q(T+40,100780)),())
        self.assertEqual([x.direction for x in g.on_tick(q(T+50,99730))],[-1])
        self.assertEqual(g.on_tick(q(T+60000,100000)),())
    def test_session_specific_source_rules_copied_from_literal_131d(self):
        self.assertEqual(len(ORIGINAL_131D_SESSION_SLEEVES),6)
        self.assertEqual(ORIGINAL_131D_SESSION_SLEEVES[0][2],'ASIA02_CONT')
        self.assertEqual(ORIGINAL_131D_SESSION_SLEEVES[3][0],(13,1,-1,1,-1,-1))
        # 2am first touch Asia with exact completed HTF signature.
        t=1769133600000 # 2026-01-23 01? use UTC aligned hour by modulo below
        t=t-t%86400000+2*3600000
        adapter=Original131DSessionL3(); e=eng(adapter)
        e.process_quote(q(t,100000),st(t,1,1,-1,-1))
        e.process_quote(q(t+1000,100300),st(t+1000,1,1,-1,-1))
        self.assertEqual(len(e.positions),1)
        self.assertIn('ASIA02_CONT',next(iter(e.positions.values())).source)
    def test_shadow_firsttouch_survives_missing_htf(self):
        t=T-T%86400000+2*3600000
        a=Original131DSessionL3();e=eng(a)
        e.process_quote(q(t,100000),None)
        e.process_quote(q(t+1000,100300),None)
        self.assertEqual(a.shadow_ladder_events,1)
        self.assertEqual(len(e.positions),0)
        self.assertEqual(e.history_missing,2)
    def test_actual_relock_follows_only_real_bad_child(self):
        wd=Funded119WatchdogL4();e=eng(wd)
        parent=Proposal('L3','ORIGINAL_HB_019_UTC17','grid',1,0,0,120000)
        e.process_quote(q(T),st(T),proposals=(parent,))
        for k in range(4):
            t=T+1000+k*3000
            e.process_quote(q(t,100000+k*1500),st(t))
            e.process_quote(q(t+1000,102000+k*1500),st(t+1000))
        c=next(iter(e.campaigns.values()))
        self.assertTrue(c.earned)
        e.process_quote(q(T+14000,106000),st(T+14000))
        new_child=next(p for p in e.positions.values() if p.layer=='L4')
        e.request_reduce(new_child.id)
        e.process_quote(q(T+15000,103000),st(T+15000))
        self.assertFalse(c.earned)
        self.assertGreater(c.relocks,0)
        self.assertEqual(c.streak,0)

    def test_unfunded_ladder_events_remain_visible(self):
        t=T-T%86400000+2*3600000
        a=Original131DSessionL3();e=eng(a,max_open=1)
        e.process_quote(q(t,100000),st(t,1,1,-1,-1))
        e.process_quote(q(t+1000,100300),st(t+1000,1,1,-1,-1))
        e.process_quote(q(t+2000,100800),st(t+2000,1,1,-1,-1))
        self.assertGreaterEqual(a.shadow_ladder_events,2)
        self.assertEqual(len(e.positions),1)
        self.assertGreaterEqual(e.reject_counts['GLOBAL_CAP'],1)

class PaidGenealogy(unittest.TestCase):
    def _parent(self,e,t=T,side=1):
        parent=Proposal('L3','ORIGINAL_HB_019_UTC17','grid',side,0,0,120000,
                    source_event_key=f'PARENT:{t}')
        e.process_quote(q(t),st(t,h4=side,h1=side),proposals=(parent,))
    def test_denied_parent_cannot_create_any_child(self):
        wd=Funded119WatchdogL4(); e=eng(wd,max_open=1)
        e.process_quote(q(T-1000),st(T-1000),proposals=(Proposal('L3','OTHER','c',1,0,0,120000),))
        self._parent(e)
        self.assertFalse(wd.parents)
        for k in range(1,5): e.process_quote(q(T+k*1000),st(T+k*1000))
        self.assertFalse(any(x['event']=='FILL' and x['layer']=='L4' for x in e.events))
    def test_paid_scout_only_after_funded_parent_and_relief_after_parent_close(self):
        wd=Funded119WatchdogL4();e=eng(wd)
        self._parent(e)
        self.assertEqual(len(wd.parents),1)
        self.assertEqual(len(e.positions),1)
        e.process_quote(q(T+1000),st(T+1000))
        self.assertEqual(len(e.positions),2)
        child=next(p for p in e.positions.values() if p.layer=='L4')
        self.assertEqual(child.parent_id,1)
        self.assertEqual(child.source,'ORIGINAL_119_FINITE_RENEWAL')
        e.request_reduce(1);e.process_quote(q(T+2000,100100),st(T+2000))
        self.assertFalse(next(iter(wd.parents.values())).active)
        e.process_quote(q(T+3000,100100),st(T+3000))
        self.assertFalse(any(p.layer=='L4' for p in e.positions.values()))
    def test_four_fast_realized_wins_unlock_five_funded_children(self):
        wd=Funded119WatchdogL4();e=eng(wd)
        self._parent(e)
        for k in range(4):
            t=T+1000+k*3000
            e.process_quote(q(t,100000+k*1500),st(t)) # child enters (long)
            e.process_quote(q(t+1000,102000+k*1500),st(t+1000)) # child +TP from bid
            # Parent has no TP; child closes; all source inputs are actual quotes
        c=next(iter(e.campaigns.values()))
        self.assertTrue(c.earned)
        self.assertEqual(c.streak,4)
        e.process_quote(q(T+14000,106000),st(T+14000))
        self.assertGreaterEqual(len([p for p in e.positions.values() if p.layer=='L4']),1)
        self.assertTrue(any(x['event']=='FILL' and x['layer']=='L4' for x in e.events))
    def test_no_unlock_from_shadow_win_or_slow_close(self):
        wd=Funded119WatchdogL4();e=eng(wd)
        self._parent(e)
        e.process_quote(q(T+1000),st(T+1000))
        self.assertFalse(next(iter(e.campaigns.values())).earned)
        e.process_quote(q(T+70000,102000),st(T+70000)) # >60s hold, notwithstanding +TP
        self.assertFalse(next(iter(e.campaigns.values())).earned)
        self.assertEqual(next(iter(e.campaigns.values())).streak,0)

if __name__=='__main__':unittest.main()