"""Multi-pass behavior and monotonicity checks, no performance claims."""
import unittest,random
from v1_grid_funded_quote_gate_0259 import BrokerPhysics,ResearchIntent
from v1_grid_funded_quote_gate_0262_hardened import StrictExecutionQuote as Q,HardenedQuoteFundingEngine as E,HardenedBrokerPhysics
from v1_grid_observed_lifecycle_0262_hardened import HardenedExitPolicy as P,HardenedObservedLifecycleFundingEngine as L

PHY=BrokerPhysics(100.,500.,.01,.01,300,52.) # ASSUMED only

def makeengine(life=False):
    args=dict(starting_cash_usd=1000,physics=PHY,max_shared_positions=3)
    return L(exit_policies=(P('grid',200,100,500),),**args) if life else E(**args)

def open_one(e,side=1):
    e.on_observed_quote(Q(1000,4000000,4000200,True))
    e.offer(ResearchIntent('p','grid',1000,side,1500,10_000))
    e.on_observed_quote(Q(1250,4000000,4000200,True))
    assert len(e.open)==1

class TestHardenedEngine(unittest.TestCase):
    def test_zero_stop_level_and_max_lot_are_supported_without_invention(self):
        spec=HardenedBrokerPhysics(100,500,.01,.01,0,52,max_lot=.02,tick_size_raw=10)
        e=E(starting_cash_usd=1000,physics=spec)
        e.on_observed_quote(Q(1000,4000000,4000200,True))
        with self.assertRaises(ValueError):
            e.offer(ResearchIntent('over','grid',1000,1,1000,60000,research_lot=.03))
        e.offer(ResearchIntent('legal','grid',1000,1,200,60000))
        e.on_observed_quote(Q(1250,4000000,4000200,True))
        self.assertEqual(len(e.open),1)

    def test_broker_tick_size_alignment_cannot_be_assumed(self):
        spec=HardenedBrokerPhysics(100,500,.01,.01,0,52,tick_size_raw=10)
        e=E(starting_cash_usd=1000,physics=spec)
        with self.assertRaises(ValueError):
            e.on_observed_quote(Q(1000,4323698,4327902,True))
        self.assertIsNone(e.last_quote)
        e.on_observed_quote(Q(1000,4323700,4327900,True))
        self.assertIsNotNone(e.last_quote)

    def test_nan_contract_and_invalid_prices_cannot_be_accepted(self):
        with self.assertRaises(ValueError):HardenedBrokerPhysics(100,float('nan'),.01,.01,0,52)
        with self.assertRaises(ValueError):HardenedBrokerPhysics(100,500,.01,.01,0,float('inf'))
        e=makeengine()
        with self.assertRaises(ValueError):e.offer(ResearchIntent('nan','grid',1000,1,1000,60000,research_lot=float('nan')))

    def test_explicit_permission_required(self):
        with self.assertRaises(TypeError):Q(1000,4000000,4000200,'True')
        with self.assertRaises(TypeError):Q(1000,4000000,4000200,None)
        with self.assertRaises(TypeError):Q(1.5,4000000,4000200,True)
    def test_market_closed_never_executes_stop(self):
        e=makeengine();open_one(e)
        self.assertEqual(e.on_observed_quote(Q(1500,3990000,3990200,False)),())
        self.assertEqual(len(e.open),1)
        r=e.on_observed_quote(Q(1750,3989000,3989200,True))
        self.assertEqual(len(r),1)
        self.assertEqual(r[0].observed_exit_raw,3989000)
        self.assertEqual(r[0].reason,'OBSERVED_GAP_SLIPPED_STOP')
    def test_market_closed_never_executes_target(self):
        e=makeengine(True);open_one(e)
        self.assertEqual(e.on_observed_quote(Q(1500,4002000,4002200,False)),())
        self.assertEqual(e.target_closes,0)
        self.assertEqual(len(e.open),1)
        self.assertEqual(e.on_observed_quote(Q(1700,4000150,4000350,True)),())
        self.assertEqual(len(e.open),1)
    def test_market_closed_never_updates_stop(self):
        e=makeengine(True);open_one(e)
        stop=e.open[0].stop_raw
        e.on_observed_quote(Q(1500,4002000,4002200,False))
        self.assertEqual(e.open[0].stop_raw,stop)
    def test_pending_expires_without_tradeable_quote(self):
        e=makeengine()
        e.on_observed_quote(Q(1000,4000000,4000200,False))
        e.offer(ResearchIntent('p','grid',1000,1,1000,60000))
        e.on_observed_quote(Q(5000,4000000,4000200,False))
        self.assertEqual(len(e.waiting),0)
        self.assertEqual(e.rejections['stale'],1)
        self.assertEqual(len(e.open),0)
    def test_pending_does_not_fill_same_quote_as_stop(self):
        e=makeengine();open_one(e)
        e.offer(ResearchIntent('next','grid',1250,-1,1000,60000))
        r=e.on_observed_quote(Q(1500,3990000,3990200,True))
        self.assertEqual(len(r),1)
        self.assertEqual(len(e.open),0)
        self.assertEqual(len(e.waiting),0) # conservative reject, no future fill silently
    def test_target_is_first_observed_executable(self):
        e=makeengine(True);open_one(e)
        r=e.on_observed_quote(Q(1500,4001200,4001400,True))
        self.assertEqual(len(r),1)
        self.assertEqual(r[0].reason,'OBSERVED_TARGET_EXIT')
        self.assertEqual(r[0].observed_exit_raw,4001200)
    def test_stop_priority_over_target_or_trailing(self):
        e=makeengine(True);open_one(e)
        r=e.on_observed_quote(Q(1500,3998000,3998200,True))
        self.assertEqual(len(r),1)
        self.assertEqual(r[0].reason,'OBSERVED_GAP_SLIPPED_STOP')
    def test_stop_distance_is_measured_from_executable_opposing_side(self):
        e=makeengine()
        e.on_observed_quote(Q(1000,4000000,4000200,True))
        # Entry ASK 4000.200, BUY SL at 3999.950 => only 0.050 below BID.
        # Broker demands 0.300 from BID, so must refuse placement.
        e.offer(ResearchIntent('tiny','grid',1000,1,250,60000))
        e.on_observed_quote(Q(1250,4000000,4000200,True))
        self.assertEqual(len(e.open),0)
        self.assertEqual(e.rejections['broker_min_stop_after_spread'],1)
        # Clear at least current spread + broker minimum => accepted.
        e.offer(ResearchIntent('okay','grid',1250,1,500,60000))
        e.on_observed_quote(Q(1500,4000000,4000200,True))
        self.assertEqual(len(e.open),1)

    def test_deadline_priority_before_target(self):
        e=makeengine(True);open_one(e)
        r=e.on_observed_quote(Q(12_000,4001200,4001400,True))
        self.assertEqual(len(r),1)
        self.assertEqual(r[0].reason,'OBSERVED_TIME_EXPIRY')
    def test_short_opposing_ask(self):
        e=makeengine(True);open_one(e,-1)
        r=e.on_observed_quote(Q(1500,3998000,3998200,True))
        self.assertEqual(r[0].observed_exit_raw,3998200)
    def test_no_fills_when_permission_always_false(self):
        e=makeengine(True)
        for i in range(100):
            ms=1000+i*25
            e.on_observed_quote(Q(ms,4000000+i*10,4000200+i*10,False))
            if i%11==0:e.offer(ResearchIntent(f'e{i}','grid',ms,1,1000,10000))
        self.assertEqual(e.summary()['closed_count'],0)
        self.assertEqual(len(e.open),0)
    def test_bad_ba_and_nonmonotonic_are_atomic(self):
        e=makeengine();open_one(e)
        before=(e.cash,len(e.open),len(e.settlements),e.last_quote.utc_ms)
        for q in [Q(1200,4000000,4000200,True),Q(1500,4000500,4000000,True),Q(1500,-1,10,True)]:
            with self.assertRaises(ValueError):e.on_observed_quote(q)
        self.assertEqual((e.cash,len(e.open),len(e.settlements),e.last_quote.utc_ms),before)
    def test_duplicate_same_ms_price_tick_cannot_exit_same_ms_entry(self):
        e=makeengine(True);open_one(e)
        # Genuine CSV can contain several ordered changes within same ms.
        # A strict budget may not execute both entry and exit there.
        r=e.on_observed_quote(Q(1250,3994000,3994200,True))
        self.assertEqual(r,())
        self.assertEqual(len(e.open),1)
        r=e.on_observed_quote(Q(1251,3993500,3993700,True))
        self.assertEqual(len(r),1)
        self.assertEqual(r[0].exit_ms,1251)

    def test_untradable_does_not_override_realized_cash(self):
        e=makeengine();open_one(e)
        original=e.cash
        for j in range(10):e.on_observed_quote(Q(1300+j*100,3999900-j*200,4000100-j*200,False))
        self.assertEqual(e.cash,original)
    def test_ema_fuzz_replay_conservation(self):
        rng=random.Random(20261013)
        e=makeengine(True)
        ms=1000;price=4000000
        e.on_observed_quote(Q(ms,price,price+250,True))
        for j in range(750):
            if j%45==0:
                e.offer(ResearchIntent('id%d'%j,'grid',ms,1 if j%2==0 else -1,1000,3000))
            ms+=100
            price+=rng.randint(-170,170)
            can_trade=j%19!=0
            e.on_observed_quote(Q(ms,price,price+250,can_trade))
            self.assertAlmostEqual(e.cash-e.initial_cash,sum(x.net_usd for x in e.settlements),places=8)
            self.assertLessEqual(len(e.open),e.cap)
            self.assertTrue(all(x.exit_ms>=x.entry_ms for x in e.settlements))
            self.assertTrue(all(x.hypothetical for x in e.settlements))
        self.assertFalse(e.summary()['mt5_ea_conversion_certified'])
    def test_snapshot_never_certifies_real_broker(self):
        self.assertFalse(makeengine().summary()['broker_contract_verified'])
        self.assertEqual(makeengine().summary()['funded_broker_orders_placed'],0)

if __name__=='__main__': unittest.main()
