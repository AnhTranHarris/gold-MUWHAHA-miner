import unittest,sys,random
from pathlib import Path
import numpy as np
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here/'source'))
from gamma02_083_heat_parent_ownership_084 import renewal_owned
from original_084_funded_event_replay_033c2d1 import Owned084Online

class ExactOriginal084(unittest.TestCase):
    def compare(self,t,ask,bid,starts,ends,sides,quantum,rearm,initial):
        E,X,R,D,P,H,O,S,W,Z=renewal_owned(t,ask,bid,np.array(starts,np.int64),np.array(ends,np.int64),np.array(sides,np.int8),quantum,rearm,initial,1)
        model=Owned084Online()
        begin={};end={}
        for k,j in enumerate(starts):begin.setdefault(j,[]).append(k)
        for k,j in enumerate(ends):end.setdefault(j,[]).append(k)
        for j in range(len(t)):
            # No parent is allowed to make an intra-window TP on its close tick
            for k in end.get(j,[]):model.funded_parent_close(k,j,int(t[j]),int(ask[j]),int(bid[j]))
            for k in begin.get(j,[]):model.funded_parent_open(k,int(sides[k]),j,int(t[j]),int(ask[j]),int(bid[j]),quantum,rearm,initial)
            model.on_tick(j,int(t[j]),int(ask[j]),int(bid[j]))
        actual=[]
        for k in range(len(starts)):
            w=model.windows[k]
            opens=[e for e in w.events if e.action=='OPEN']
            closes=[e for e in w.events if e.action=='CLOSE']
            self.assertEqual(len(opens),len(closes),'Owner has unmatched local geometry event')
            for a,c in zip(opens,closes):actual.append((a.tick,c.tick,a.raw,int(sides[k]),c.exit_pnl,c.hold_s,k))
        self.assertEqual(len(E),len(actual))
        for k,(e,x,r,d,p,h,o) in enumerate(actual):
            self.assertEqual((int(E[k]),int(X[k]),int(R[k]),int(D[k]),int(O[k])),(e,x,r,d,o))
            self.assertAlmostEqual(float(P[k]),p,places=8)
            self.assertAlmostEqual(float(H[k]),h,places=8)
        self.assertEqual((int(W),int(Z)),(sum(w.wins for w in model.windows.values()),sum(w.residuals for w in model.windows.values())))
        return model,len(E),W,Z

    def test_directional_first_touch_long(self):
        t=np.arange(60,dtype=np.int64)*1000+1769987186655
        bid=np.array([100000+200*((i//6)%6) + (i%6)*20 for i in range(60)],np.int64)
        ask=bid+50
        self.compare(t,ask,bid,[0,13],[38,54],[1,1],500,250,0)

    def test_directional_first_touch_short(self):
        t=np.arange(70,dtype=np.int64)*1000+1769987186655
        bid=np.array([100000-300*((i//7)%7)-(i%7)*50 for i in range(70)],np.int64)
        ask=bid+70
        self.compare(t,ask,bid,[1,16],[48,69],[-1,-1],1250,0,0)

    def test_initial_rearm_and_parent_residuals(self):
        t=np.arange(120,dtype=np.int64)*1000+1769987186655
        bid=np.array([100000+(i*177 if i<70 else 12000-(i-70)*205) for i in range(120)],np.int64)
        ask=bid+100
        self.compare(t,ask,bid,[0,5,10],[51,85,110],[1,1,-1],500,250,350)

    def test_real_feb_quotes_multiple_owned_parent_windows(self):
        import gzip,glob
        p=glob.glob('/mnt/data/XAUUSD_DUKAS_2026_02_ticks.csv*.gz')
        if not p:self.skipTest('Original February tick archive missing')
        import csv
        ts=[];ask=[];bid=[]
        with gzip.open(p[0],'rt') as fh:
            rows=csv.DictReader(fh)
            for i,r in enumerate(rows):
                if i>=20000:break
                ts.append(int(r['timestamp_ms_utc']));ask.append(int(r['ask_raw']));bid.append(int(r['bid_raw']))
        t=np.array(ts,np.int64);a=np.array(ask,np.int64);b=np.array(bid,np.int64)
        # Diagnostic source-contract parents: their exits are *simulated funded
        # closes at the event tick*, not computed future exits inside the model.
        m,c,w,z=self.compare(t,a,b,[120,1300,2800,5000,8500,13000],[1800,6500,7900,11000,16600,19750],[1,-1,1,-1,1,-1],1250,0,0)
        self.assertGreater(c,0)
        self.assertGreaterEqual(w,0)

    def test_denied_parent_has_no_owned_child_and_no_future_peek(self):
        model=Owned084Online()
        for j in range(20):model.on_tick(j,1000*j,100200+j*100,100000+j*100)
        self.assertEqual(len(model.events),0)
        self.assertEqual(model.windows,{})
        def run(suffix):
            m=Owned084Online();m.funded_parent_open(0,1,0,0,100200,100000,500,250)
            for j,b in enumerate([100150,100400,100800]+suffix,start=1):
                m.on_tick(j,1000*j,b+200,b)
            return m.events
        x=run([101000,101200]);y=run([99900,99700]);
        self.assertEqual([z for z in x if z.tick<=3],[z for z in y if z.tick<=3])

if __name__=='__main__':unittest.main()