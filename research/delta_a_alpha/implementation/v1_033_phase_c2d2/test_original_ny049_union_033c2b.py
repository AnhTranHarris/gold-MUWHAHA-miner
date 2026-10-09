"""Exact entry EVENT indices for original 049 union; no future outcome arrays."""
from __future__ import annotations
import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent/'source'))
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_ny16_17_18_subphase_lifecycle_001 as cur
import gamma02_campaign_heartbeat_019 as hb
import gamma02_rebreak_latency_017 as lat
import gamma02_time_decay_conviction_001 as td
from v1_funded_core_033 import Quote,Structure
from original_ny049_union_033c2b import Original049NYSourceL3


def original_events(t,mid,h4,h1,m15,m5):
    """Reference only original NUMBA ENTRY manufacturers; no precomputed exits."""
    ev=[]
    ei,ed,eh,es,disp=g.build_perm_extension_events(t,mid,h4,h1,m15,m5,2,50,200)
    # Original 014.build_ny: filter as-of structural signature, source-level
    # band and last of multiple newly crossed rungs per same tick.
    for hour in (16,17):
        mask=(eh==hour)&(es==4)
        ix=ei[mask];di=ed[mask];dep=disp[mask]
        # Original 014.dedup_last keeps highest crossed rung per tick.
        keep=np.r_[ix[1:]!=ix[:-1],True] if len(ix) else np.empty(0,dtype=bool)
        for j,d,z in zip(ix[keep],di[keep],dep[keep]):
            ss=(int(h4[j]),int(h1[j]),int(m15[j]),int(m5[j]),int(d))
            if ss not in cur.SIGS[hour]:continue
            b10=int(t[j]//600000%6)
            if z<(500 if hour==16 else td.MAP17['lateBias'][b10*10]):continue
            ev.append((int(j),int(d),hour,0))
    ri,rd,rdep,_=lat.generic_rebreaks_latency(t,mid,h4,h1,500,1000,16,18,50)
    for j,d,dep in zip(ri,rd,rdep):
        if t[j]//3600000%24!=17:continue
        if (int(h4[j]),int(h1[j]),int(m15[j]),int(m5[j]),int(d)) not in cur.SIGS[17]:continue
        if int(dep)<td.MAP17['lateBias'][int(t[j]//600000%6)*10]:continue
        ev.append((int(j),int(d),17,1))
    for group,hour in [(2,16),(1,17)]:
        ix,di,src,_,_,_=hb.heartbeat_candidates(t,mid,h4,h1,m15,m5,120,group)
        for j,d,h in zip(ix,di,src):
            if h==hour:ev.append((int(j),int(d),hour,2))
    ev.sort(key=lambda x:(x[0],x[2],x[3]))
    unique=[];prev=None
    for j,d,h,pri in ev:
        k=(j,h)
        if k!=prev:unique.append((j,d,h));prev=k
    return unique


def port_events(t,ask,bid,h4,h1,m15,m5):
    gen=Original049NYSourceL3();out=[]
    for i,tm in enumerate(t):
        q=Quote(int(tm),int(ask[i]),int(bid[i]))
        s=Structure('DIAGNOSTIC',int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]),int(tm)-1,'G',0,
          (int(tm)-14400001,int(tm)-3600001,int(tm)-900001,int(tm)-300001))
        gen.on_market_quote(q,None)
        for z in gen.source_events(q,s):out.append((i,z.side,z.hour))
    return out

class SourceParity(unittest.TestCase):
    def test_original_union_entry_indices_on_state_changes(self):
        rng=np.random.default_rng(8441)
        for run in range(3):
            N=40000
            t=1769190000000+np.cumsum(rng.integers(1,150,size=N,dtype=np.int64))
            # start at UTC16:40; crosses multiple minutes and UTC17.
            t=t+(17*3600000-t[0]%86400000)-350000
            inc=rng.choice(np.array([-1200,-700,-300,-80,60,350,900,1200],dtype=np.int64),N)
            mid=(200000+np.cumsum(inc)).astype(np.int64)
            bid=(mid-60).astype(np.int64);ask=(mid+60).astype(np.int64)
            sgn=np.where((np.arange(N)//(1000+run*200))%3==0,-1,1).astype(np.int8)
            h4=sgn.copy();h1=sgn.copy();m15=np.where((np.arange(N)//800)%2==0,-1,1).astype(np.int8)
            m5=np.where((np.arange(N)//400)%2==0,-1,1).astype(np.int8)
            reference=original_events(t,mid,h4,h1,m15,m5)
            actual=port_events(t,ask,bid,h4,h1,m15,m5)
            self.assertEqual(actual,reference,f'run={run}: original={len(reference)} port={len(actual)}; prefix={list(zip(reference[:5],actual[:5]))}')

if __name__=='__main__':unittest.main()
