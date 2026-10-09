"""Compare entry-known online L3 adapter with literally extracted original 019 code.
Requires JAN037 original-source archive (not used at live runtime).
"""
from pathlib import Path
import ast, zipfile, unittest
import numpy as np
from v1_funded_core_033 import Quote,Structure,OriginalHourlyHeartbeatL3

ORIGINAL_BUNDLE=Path('/mnt/data/JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip')

class Original019Test(unittest.TestCase):
    @unittest.skipUnless(ORIGINAL_BUNDLE.exists(), 'Original archived reference unavailable')
    def test_heartbeat_entry_identity_against_exact_original_019(self):
        z=zipfile.ZipFile(ORIGINAL_BUNDLE)
        doc=z.read('032_source/gamma02_campaign_heartbeat_019.py').decode()
        tree=ast.parse(doc)
        names={'THR','NY17_MIN','NY18_MIN','NY18_MAX','TP16','SL16','H16','TP17','SL17','H17','TP18','SL18','H18'}
        fun={'london_rule','ny_dir','heartbeat_candidates'}
        selected=[]
        for node in tree.body:
            if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id in names for x in node.targets):selected.append(node)
            if isinstance(node,ast.FunctionDef) and node.name in fun:
                node.decorator_list=[]
                selected.append(node)
        mod=ast.Module(body=selected,type_ignores=[])
        ast.fix_missing_locations(mod)
        ns={'np':np}
        exec(compile(mod,'original019:literally_extracted','exec'),ns)
        # Two real-style UTC hourly windows: includes minute resets, London and NY
        # sign/phase switching. All synthetic ticks are input fixtures ONLY.
        t=np.array([7*3600000+k*250 for k in range(1800)]+[17*3600000+k*250 for k in range(1800)],dtype=np.int64)
        # Signed displacement in milli-dollars, engineered to cross source boundaries.
        price=(4820000+(np.arange(len(t))%240)*220).astype(np.int32)
        ask=price+75;bid=price-75;mid=(ask.astype(np.int64)+bid.astype(np.int64))//2
        h4=np.where(np.arange(len(t))<1800,1,-1).astype(np.int8)
        h1=h4.copy();m15=np.full(len(t),-1,np.int8);m5=m15.copy()
        i,d,src,hold,tp,sl=ns['heartbeat_candidates'](t,mid,h4,h1,m15,m5,50,4)
        adapter=OriginalHourlyHeartbeatL3(50)
        got=[]
        for k,tm in enumerate(t):
            s=Structure('LONDON' if k<1800 else 'NY',int(h4[k]),int(h1[k]),-1,-1,int(tm-1),
                        'K',0,(int(tm-100000),int(tm-50000),int(tm-10000),int(tm-2000)))
            for proposal in adapter.propose(Quote(int(tm),int(ask[k]),int(bid[k])),s,None):
                got.append((k,proposal.side,int(proposal.source.rsplit('UTC',1)[1]),proposal.ttl_ms,
                            int(proposal.tp_usd*1000),int(proposal.sl_usd*1000)))
        exp=list(zip(i.tolist(),d.tolist(),src.tolist(),hold.tolist(),tp.tolist(),sl.tolist()))
        self.assertGreater(len(exp),0)
        self.assertEqual(got,exp)

if __name__=='__main__':unittest.main()