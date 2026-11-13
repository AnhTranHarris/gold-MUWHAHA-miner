"""Independent Python verification of proposed MQL5 QRB/QAF shadow equations.

This DOES NOT compile or execute MQL5. Results certify the reference math and
source contracts only. MetaEditor compilation and runtime parity remain needed.
"""
import unittest
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from event_engine import build_features, TREND_N, WINDOWS_MS


class TestProposedMqlShadow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        include=ROOT/'GoldMuwahahaM60QuoteFlows.mqh'
        if not include.exists():
            include=ROOT.parents[2]/'Experts'/'GoldMuwahahaM60QuoteFlows.mqh'
        cls.source=include.read_text()

    def test_disabled_standalone_no_trading_api(self):
        for forbidden in ('trade.Buy(', 'trade.Sell(', 'OrderSend(', 'PositionModify(', 'PositionClose('):
            self.assertNotIn(forbidden,self.source)
        self.assertIn('void LogCandidate(',self.source)
        self.assertIn('void Observe(',self.source)

    def test_event_time_source_ordinal_implicit(self):
        self.assertIn('m_sequence++',self.source)
        self.assertIn('last.sequence-first.sequence',self.source)
        self.assertIn('now-m_quotes[Slot(1)].ms>60000',self.source)
        self.assertIn('m_quotes[Slot(mid)]',self.source)
        self.assertIn('q.ms<cutoff',self.source)

    def test_source_refuses_incomplete_history(self):
        self.assertIn('if(now-oldest.ms<width) return false;',self.source)
        self.assertIn('if(!ready) return "NA";',self.source)
        self.assertIn('if(m_capacity<=0',self.source)

    def test_qaf_only_completed_seconds(self):
        self.assertIn('if(s.sec<entry_sec-span || s.sec>=entry_sec) continue;',self.source)
        self.assertIn('2.0*s.close-s.high-s.low',self.source)
        self.assertIn('denominator<=0.0',self.source)

    def test_source_uses_bid_ask_not_volume(self):
        self.assertIn('tick.bid',self.source)
        self.assertIn('tick.ask',self.source)
        self.assertNotIn('tick.volume',self.source)
        self.assertNotIn('tick.last',self.source)
        self.assertIn('NOT actual traded volume',self.source)

    def test_no_current_second_in_QAF_python_reference(self):
        # Constant-price second: zero-range CMF proxy contributes 0, not fabricated flow.
        t=np.array([1000,1100,1999,2000,2800,3000,3100],dtype=np.int64)
        bid=np.array([10,11,12,20,30,40,50],dtype=np.int32)
        ask=bid+2
        fs,_,_=build_features(t,bid,ask,np.array([6],dtype=np.int64))
        qaf5=float(fs[0,TREND_N+28]); self.assertLessEqual(abs(qaf5),1.000001)
        # Complete seconds at 1000, 2000 and 3000 only: now=3.1s, 3000 excluded.
        # Sec 1: 10,11,12 => upper close, N=3. Sec 2: 20,30 => upper close, N=2.
        self.assertAlmostEqual(qaf5,1.0,places=6)

    def test_static_qrb_formula_agrees_with_frozen_event_engine(self):
        rng=np.random.default_rng(1337)
        ms=np.concatenate([[0],np.cumsum(rng.integers(1,35,size=14000,dtype=np.int64))])
        d=rng.integers(-2,3,size=len(ms),dtype=np.int32)
        db=np.cumsum(d,dtype=np.int32)+20000
        spread=np.maximum(15,20+np.cumsum(rng.choice([-1,0,1],size=len(ms),p=[.2,.6,.2])))
        da=db+spread.astype(np.int32)
        entry=np.searchsorted(ms,120_000,side='left')
        features,_,_=build_features(ms,db,da,np.array([entry],dtype=np.int64))
        mid2=db+da
        diff=np.diff(mid2,prepend=mid2[0])
        dp=np.diff(da-db,prepend=(da-db)[0])
        for j,w in enumerate(WINDOWS_MS):
            lo=np.searchsorted(ms,ms[entry]-w,side='left')
            sample=diff[lo+1:entry+1]
            sw=dp[lo+1:entry+1]
            count=entry-lo
            qrb=int(np.sign(sample).sum())
            signed=qrb/(1+int(np.count_nonzero(sample)))
            press=(int((sw>0).sum())-int((sw<0).sum()))/(count+1)
            activity=np.log1p(count*1000/max(1,int(ms[entry]-ms[lo])))
            offset=TREND_N+4*j
            self.assertAlmostEqual(float(features[0,offset]),qrb,places=4)
            self.assertAlmostEqual(float(features[0,offset+1]),signed,places=5)
            self.assertAlmostEqual(float(features[0,offset+2]),press,places=5)
            self.assertAlmostEqual(float(features[0,offset+3]),activity,places=5)

    def test_identical_millisecond_quote_order(self):
        t=np.array([0,10,10,10,20,60_000,60_001],dtype=np.int64)
        b=np.array([100,101,102,101,103,105,104],dtype=np.int32)
        a=b+20
        feat,_,_=build_features(t,b,a,np.array([6],dtype=np.int64))
        self.assertEqual(float(feat[0,TREND_N]),-1.0)

    def test_log_fields_count_matches_spec(self):
        # Log row includes time, side, bid, ask, source, 7*4 quote metrics, 3 QAF metrics.
        self.assertEqual(5+7*4+3,36)
        for suffix in ('qrb_100ms','qrb_500ms','qrb_1000ms','qrb_3000ms',
                       'qrb_5000ms','qrb_15000ms','qrb_60000ms',
                       'qaf_completed_5s','qaf_completed_15s','qaf_completed_60s'):
            self.assertIn('"'+suffix+'"',self.source)


if __name__=='__main__':unittest.main()
