"""V2 F1 deterministic internal engineering QA, NOT evidence of trading edge."""
import json,unittest
import numpy as np
from v2_f1_integrated import prev_frames,execute

class TestEngine(unittest.TestCase):
 def test_asof_completed_m1_m5_h1_h4(self):
  t=np.arange(15001,dtype=np.int64)
  p=np.linspace(100,200,len(t))
  for bar in [60,300,900,3600,14400]:
   oo,hh,ll,cc,atr=prev_frames(t,p,p,p,p,bar)
   self.assertTrue(np.isnan(cc[0]))
   self.assertTrue(np.isnan(cc[bar-1]))
   self.assertAlmostEqual(cc[bar],p[bar-1])
   self.assertTrue(np.isnan(atr[bar]))
 def test_no_same_quote_physical_overlap_and_fast_rearm(self):
  # Constructed engine-capacity test — fabricated quotes do not estimate profits.
  n=3600*4;ms=np.arange(n,dtype=np.int64)*250
  ts=np.arange(3600,dtype=np.int64)
  ix=np.arange(0,n,4,dtype=np.int64)
  bid=np.ones(n,np.int32)*4300000
  ask=bid+100
  sg=np.zeros((8,3600),np.int8);sg[1,:]=1
  q=np.ones(3600,np.int8);mid=np.ones(3600)*4300
  atr=np.ones(3600)*6;m5=np.ones(3600,np.int8);h1=m5.copy();h4=m5.copy();m15=m5.copy()
  ses=np.ones(3600,np.uint8)*15
  led,z=execute(ms,bid,ask,ix,ts,sg,q,mid,atr,m5,h1,h4,m15,ses,
     2,0,0,0,10_000.,.40,5.,100.,5.,2.,8,250,0,59,0)
  self.assertGreater(len(led),200) # technical order throughput, NOT $100 backtest P&L
  self.assertTrue(np.all(led[1:,0]>=led[:-1,1]))
  self.assertTrue(np.all(led[:,1]-led[:,0]>=8*1000))
  self.assertEqual(int(z[4]),len(led))
  self.assertEqual(int(z[2]),0)
 def test_original_quote_invariants(self):
  from pathlib import Path
  p=Path(__file__).parent/'V2_NATIVE_CONTROL_SMOKE_TRADES.csv'
  self.assertTrue(p.exists())
  import pandas as pd
  q=pd.read_csv(p)
  if len(q):
   self.assertTrue((q.exit_ms>=q.entry_ms).all())
   self.assertTrue((q.entry_ms.iloc[1:].to_numpy()>=q.exit_ms.iloc[:-1].to_numpy()).all())
   calc=(q.exit_price-q.entry_price)*q.side-.20
   self.assertTrue(np.allclose(calc,q.net_usd,atol=1e-6))

if __name__=='__main__':
 unittest.main(verbosity=2)

class TestIncremental(unittest.TestCase):
 def test_stream_completed_not_current_candle(self):
  from v2_streaming_chassis import StreamingF1
  s=StreamingF1()
  x=s.on_quote(0,4300000,4300100)
  self.assertIsNone(x.completed['M1'])
  x=s.on_quote(59000,4310000,4310100)
  self.assertIsNone(x.completed['M1'])
  x=s.on_quote(60000,4310000,4310100)
  self.assertEqual(x.completed['M1'].closing,4310.)
  x=s.on_quote(61000,4300000,4300100)
  self.assertEqual(x.completed['M1'].closing,4310.)
  self.assertEqual(x.minute_open_mid,4310.05)
  self.assertEqual(x.minute_buy_bracket,4310.2)
 def test_stream_rejects_bad_tick(self):
  from v2_streaming_chassis import StreamingF1
  s=StreamingF1();s.on_quote(1000,4300000,4300100)
  with self.assertRaises(ValueError):s.on_quote(999,4300000,4300100)
  with self.assertRaises(ValueError):s.on_quote(1002,4300100,4300000)
