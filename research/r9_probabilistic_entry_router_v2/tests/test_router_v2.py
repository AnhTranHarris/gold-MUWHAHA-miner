import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from router_v2_features import Quote,MarkedHawkesBank,CausalImpulseTracker,RouterV2FeatureEngine
from router_v2_labels import ActivePath,outcome_class
from router_v2_model import BayesianCompetingRiskModel,np_order_threshold

class RouterV2Tests(unittest.TestCase):
    def q(self,ms,bid,ask):return Quote(ms,bid,ask,ms)

    def test_marked_events_distinguish_ask_only_from_joint_move(self):
        h=MarkedHawkesBank();h.add(self.q(0,100,100.20))
        e=h.add(self.q(100,100,100.21));self.assertIn('AU',e);self.assertIn('SW',e);self.assertNotIn('BU',e)
        e=h.add(self.q(200,100.01,100.22));self.assertIn('BU',e);self.assertIn('AU',e)


    def test_cross_excitation_feature_records_follow_event(self):
        h=MarkedHawkesBank();h.add(self.q(0,100,100.20));h.add(self.q(100,100.01,100.21));h.add(self.q(200,100.01,100.22))
        f=h.features();self.assertTrue(any(k.startswith('hawk_cross_dir_') for k in f))

    def test_impulse_anchor_uses_observed_path_only(self):
        x=CausalImpulseTracker();x.update(1000,100.50,.50,.9,.20)
        self.assertEqual(x.side,1);start=x.start;ext=x.extreme
        x.update(1100,100.60,.10,.8,.20)
        self.assertEqual(x.start,start);self.assertGreaterEqual(x.extreme,ext)
        f=x.features(100.55,1200);self.assertGreaterEqual(f['fib_retracement'],0)

    def test_first_passage_label_does_not_exit_on_entry_tick(self):
        p=ActivePath(self.q(1000,100,100.20),1)
        self.assertIsNone(p.update(self.q(1000,99.0,99.2)))
        o=p.update(self.q(1100,99.69,99.89));self.assertIsNotNone(o);self.assertEqual(o.exit_type,'SL')
        self.assertEqual(outcome_class(o),'ADVERSE')

    def test_trailing_target_is_recorded_before_later_stop(self):
        p=ActivePath(self.q(1000,100,100.20),1)
        self.assertIsNone(p.update(self.q(1100,100.35,100.55)))
        self.assertIsNotNone(p.targets['0.10'])
        o=p.update(self.q(1200,p.stop-.01,p.stop+.19));self.assertEqual(o.exit_type,'SL')

    def test_feature_snapshot_cannot_change_when_only_future_ticks_change(self):
        def build(future):
            e=RouterV2FeatureEngine();ms=0;bid=100.;ask=100.2
            # >15 minutes gives 15m context and >2m local ready
            for i in range(16*60*4):
                ms+=250;bid+=.001 if i%7<4 else -.0008;ask=bid+.2
                e.add(self.q(ms,bid,ask))
            q=self.q(ms,bid,ask);snap=e.snapshot(q)
            for dx in future:
                ms+=250;bid+=dx;ask=bid+.2;e.add(self.q(ms,bid,ask))
            return snap
        a=build([1,1,-2]);b=build([-5,3,2]);self.assertEqual(a,b)

    def test_teacher_is_not_runtime_feature(self):
        e=RouterV2FeatureEngine();ms=0;bid=100.
        for i in range(16*60*4):
            ms+=250;bid+=.001; e.add(self.q(ms,bid,bid+.2))
        f=e.snapshot(self.q(ms,bid,bid+.2));self.assertIsNotNone(f);self.assertNotIn('teacher',f)


    def test_250ms_feature_exists_after_warmup(self):
        e=RouterV2FeatureEngine();ms=0;bid=100.
        for i in range(16*60*4):
            ms+=250;bid+=.0005 if i%3 else -.0002;e.add(self.q(ms,bid,bid+.2))
        f=e.snapshot(self.q(ms,bid,bid+.2));self.assertIn('disp_250ms',f)

    def test_htf_geometry_not_faked_before_full_horizon(self):
        e=RouterV2FeatureEngine();ms=0;bid=100.
        for i in range(20*60*4):
            ms+=250;bid+=.0005;e.add(self.q(ms,bid,bid+.2))
        f=e.snapshot(self.q(ms,bid,bid+.2));self.assertEqual(f['geo_15m_ready'],1.0)
        self.assertEqual(f['geo_1h_ready'],0.0);self.assertEqual(f['geo_4h_ready'],0.0)

    def test_np_fails_closed_when_insufficient_bad_calibration(self):
        self.assertIsNone(np_order_threshold([0.1]*20,.1))


    def test_model_preserves_sparse_subsecond_feature_union(self):
        ex=[]
        for c,net in [('FAVORABLE',.2),('ADVERSE',-.4),('TIMEOUT',-.01)]:
            for j in range(20):
                f={'side':1.0,'session_london':1.0,'state_continuation':1.0,'disp_250ms':0.5} if j%2==0 else {'side':1.0,'session_london':1.0,'state_continuation':1.0}
                ex.append({'features':f,'class':c,'net':net,'teacher':0})
        m=BayesianCompetingRiskModel(min_context=10).fit(ex)
        self.assertIn('disp_250ms',m.feature_names)

    def test_router_can_wait(self):
        # synthetic transparent dataset with both good/bad/timeout classes.
        ex=[]
        for i,c in enumerate(('FAVORABLE','ADVERSE','TIMEOUT')):
            for j in range(120):
                side=1 if j%2==0 else -1
                f={'x':(-1 if c=='ADVERSE' else 1 if c=='FAVORABLE' else 0)+j*1e-4,
                   'side':float(side),'session_london':1.,'state_continuation':1.}
                ex.append({'features':f,'class':c,'net':.2 if c=='FAVORABLE' else -.4 if c=='ADVERSE' else -.01,'teacher':0})
        m=BayesianCompetingRiskModel(min_context=20).fit(ex)
        cal=[x for x in ex if x['class']=='ADVERSE']*2
        self.assertTrue(m.calibrate_np(cal))
        bad={'x':-1.,'side':1.,'session_london':1.,'state_continuation':1.}
        good={'x':1.,'side':-1.,'session_london':1.,'state_continuation':1.}
        action,_=m.route(bad,good,min_utility=10.0);self.assertEqual(action,'WAIT')

if __name__=='__main__':unittest.main()
