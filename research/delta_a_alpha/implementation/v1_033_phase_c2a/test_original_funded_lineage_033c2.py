"""Parity/causality tests for legacy 049→051→075→119→131A C2 partial port."""
import unittest,heapq,sys
from pathlib import Path
from dataclasses import replace
import numpy as np
sys.path.insert(0,str(Path(__file__).parent/'source'))
from gamma02_profit_funded_surge_equity_051 import select_idx
from original_funded_lineage_033c2 import (Original049FundedCapacity,Original049Settings,
    Original049OnlineSource,Original119FundedParentSource)
from v1_funded_core_033 import (Quote,Structure,Proposal,Position,Close,
    Limits,FundedEngine,OriginalHourlyHeartbeatL3)

T=1769191200000 # 2026 Jan 23 UTC 17:00 = NY local 12:00

def quote(tm,bid=100000):return Quote(tm,bid+100,bid)
def struct(tm,h4=1,h1=1,m15=-1,m5=-1):
    return Structure('NY',h4,h1,m15,m5,tm-1,'ORIGINAL_GRID',0,
                    (tm-14400001,tm-3600001,tm-900001,tm-300001))
def engine(*sources,max_open=30):
    return FundedEngine(replace(Limits(),max_open=max_open,max_layer_open=max_open,
                    max_per_source_open=max_open,max_same_direction=max_open,
                    max_per_cell_side=max_open,max_orders_per_second=5),list(sources),
                    broker_contract_verified=True)

class Historical049Parity(unittest.TestCase):
    def test_exact_original_051_selector_on_realized_outcomes_fixture(self):
        # Original source's `select_idx` precomputes future pnl, but its capacity
        # decisions only advance when PREVIOUS selected exits have realized.
        rng=np.random.default_rng(23009)
        for seed in range(4):
            et=np.cumsum(rng.integers(1,230,size=500,dtype=np.int64)).astype(np.int64)
            xt=et+rng.integers(0,2100,size=500,dtype=np.int64)
            pn=rng.choice(np.array([-3.0,-.2,0.,2.0,11.,50.,350.,-230.]),size=500).astype(float)
            src=rng.choice(np.array([16,17],dtype=np.int16),size=500)
            c=Original049Settings(base_cap=2,base_step=2,base_unit=40.,base_max=12,
                  initial_surge=1,surge_step=2,surge_unit=25.,max_surge=15,hard_max=25)
            ref,_,_=select_idx(et,xt,pn,src,c.base_cap,c.base_step,c.base_unit,c.base_max,
                   c.initial_surge,c.surge_step,c.surge_unit,c.max_surge,c.hard_max)
            online=Original049FundedCapacity(c)
            active=[];chosen=[]
            for i,now in enumerate(et):
                # exact original kernel uses active slot order; integer threshold
                # here avoids floating roundoff influencing eligibility.
                remaining=[]
                for k in active:
                    if xt[k]<=now:
                        close=Close(k+1,int(xt[k]),0,float(pn[k]),int(xt[k]-et[k]),'TIME',
                                    f'ORIGINAL_049_UNION_UTC{src[k]}','L3',None)
                        online.on_funded_close(close,None)
                    else:remaining.append(k)
                active=remaining
                p=Proposal('L3',f'ORIGINAL_049_UNION_UTC{src[i]}','a',1,0,0,1000)
                if online.permit(p,int(now)):
                    online.on_funded_entry(Position(i+1,'L3',p.source,'a',1,int(now),100,0,0,
                                   int(xt[i]),None,None,str(i)),quote(int(now)),struct(int(now)),None)
                    active.append(i);chosen.append(i)
            self.assertEqual(chosen,list(ref),f'seed={seed}')
    def test_denied_parent_never_enters_realized_bank(self):
        quota=Original049FundedCapacity(Original049Settings(base_cap=1,base_step=1,base_unit=2.,base_max=1,
             initial_surge=0,surge_step=0,surge_unit=2.,max_surge=0,hard_max=1))
        p=Proposal('L3','ORIGINAL_HB_019_UTC17','x',1,0,0,60000)
        self.assertTrue(quota.permit(p,T))
        quota.on_funded_entry(Position(5,'L3',p.source,'x',1,T,100,0,0,T+60000,None,None,'x'),quote(T),struct(T),None)
        self.assertFalse(quota.permit(p,T+1))
        quota.on_funded_close(Close(15,T+2,0,500.,2,'TP',p.source,'L3',None),None)
        self.assertEqual(quota.realized,0.0)
        self.assertFalse(quota.permit(p,T+3))
        quota.on_funded_close(Close(5,T+4,0,20.,4,'TP',p.source,'L3',None),None)
        self.assertEqual(quota.realized,20.)
        self.assertTrue(quota.permit(p,T+5))

class Original119Funding(unittest.TestCase):
    def test_first_parent_requires_source_049_and_macro_and_actual_fill(self):
        wd=Original119FundedParentSource();q=quote(T)
        e=engine(wd,max_open=1)
        blocker=Proposal('L3','OTHER','x',1,0,0,60000)
        parent=Proposal('L3','ORIGINAL_HB_019_UTC17','x',1,0,0,60000)
        e.process_quote(q,struct(T),proposals=(blocker,parent))
        self.assertFalse(wd.parents)
        e2=engine(Original119FundedParentSource())
        e2.process_quote(q,struct(T,h4=-1,h1=-1),proposals=(parent,))
        self.assertFalse(next(a for a in e2.adapters if isinstance(a,Original119FundedParentSource)).parents)
        e3=engine(Original119FundedParentSource())
        e3.process_quote(q,struct(T),proposals=(parent,))
        self.assertEqual(len(e3.adapters[0].parents),1)
    def test_049_wrapper_funds_actual_l3_first_and_l4_in_next_quote(self):
        quota=Original049FundedCapacity()
        wd=Original119FundedParentSource()
        class Proposer:
            def __init__(self):self.n=0
            def propose(self,q,s,e):
                self.n+=1
                if self.n==1:return (Proposal('L3','ORIGINAL_HB_019_UTC17','c',1,0,0,80000),)
                return ()
            def on_funded_close(self,c,e):pass
        source=Original049OnlineSource(Proposer(),quota)
        e=engine(source,wd)
        e.process_quote(quote(T),struct(T))
        self.assertEqual(len(wd.parents),1)
        self.assertEqual(len(quota.funded_active),1)
        e.process_quote(quote(T+1000),struct(T+1000))
        self.assertTrue(any(p.layer=='L4' for p in e.positions.values()))
        e.process_quote(quote(T+3000,102000),struct(T+3000))
        self.assertGreaterEqual(len(e.closed),1)
        self.assertTrue(any(c.layer=='L4' for c in e.closed))
        self.assertTrue(quota.realized==0.) # only L3 closes count
        parent=next(p for p in e.positions.values() if p.layer=='L3')
        e.request_reduce(parent.id)
        e.process_quote(quote(T+4000,102000),struct(T+4000))
        self.assertEqual(len(quota.funded_active),0)
        self.assertGreater(quota.realized,0.)
    def test_qmap_bin5_is_1100_other_1190(self):
        wd=Original119FundedParentSource()
        e=engine(wd)
        e.process_quote(quote(T),struct(T),proposals=(Proposal('L3','ORIGINAL_HB_019_UTC17','x',1,0,0,80000),))
        pr=list(wd.propose(quote(T+1000),struct(T+1000),e))
        self.assertEqual(pr[0].tp_usd,1.19)
        # second case NY local minute :50
        time50=T+50*60000
        e2=engine(Original119FundedParentSource())
        e2.process_quote(quote(time50),struct(time50),proposals=(Proposal('L3','ORIGINAL_HB_019_UTC17','x',1,0,0,80000),))
        wd2=e2.adapters[0]
        self.assertAlmostEqual(tuple(wd2.propose(quote(time50+1000),struct(time50+1000),e2))[0].tp_usd,1.10)
    def test_119_first_touched_rearm_uses_observed_last_favorable_quote(self):
        wd=Original119FundedParentSource();e=engine(wd)
        e.process_quote(quote(T),struct(T),proposals=(Proposal('L3','ORIGINAL_HB_019_UTC17','x',1,0,0,80000),))
        e.process_quote(quote(T+1000,100000),struct(T+1000))
        self.assertEqual(len([p for p in e.positions.values() if p.layer=='L4']),1)
        e.process_quote(quote(T+2000,101400),struct(T+2000)) # TP @ >=1.19
        self.assertEqual(len([c for c in e.closed if c.layer=='L4']),1)
        e.process_quote(quote(T+3000,100000),struct(T+3000)) # below last favorable BID
        self.assertEqual(len([p for p in e.positions.values() if p.layer=='L4']),0)
        self.assertGreater(wd.renewal_rearm_rejects,0)
        e.process_quote(quote(T+4000,101500),struct(T+4000))
        self.assertEqual(len([p for p in e.positions.values() if p.layer=='L4']),1)

if __name__=='__main__':unittest.main()