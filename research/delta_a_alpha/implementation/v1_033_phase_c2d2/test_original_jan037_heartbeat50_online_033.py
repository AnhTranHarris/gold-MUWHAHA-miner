"""Compare literal original source functions and causal online heartbeat semantics."""
import ast,hashlib,itertools,unittest
from pathlib import Path
import numpy as np
import original_jan037_heartbeat50_online_033 as current
from original_jan037_heartbeat50_online_033 import OriginalJAN037Heartbeat50ms,london_rule,ny_dir,THR,NY17_MIN,NY18_MAX

SOURCE=Path(__file__).parent/'verified_original_sources'/'JAN037'/'gamma02_campaign_heartbeat_019.py'
SHA='3ddb58c2096cf33ffc092335cfae8bc3ee78d828901423f1466f3024593016d4'

def original_functions():
    src=SOURCE.read_bytes()
    assert hashlib.sha256(src).hexdigest()==SHA
    tree=ast.parse(src.decode('utf8'))
    fun=[]
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name in ('london_rule','ny_dir'):
            node.decorator_list=[];fun.append(node)
    ns={};exec(compile(ast.Module(body=fun,type_ignores=[]),str(SOURCE),'exec'),ns)
    return ns

class Jan037OriginalTests(unittest.TestCase):
    def test_source_sha_exact(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),SHA)

    def test_all_structural_states_london_ny_original_exact(self):
        funcs=original_functions()
        for hour in range(24):
            for h4,h1,m15,m5 in itertools.product((-1,0,1),repeat=4):
                args=hour,h4,h1,m15,m5
                self.assertEqual(london_rule(*args),funcs['london_rule'](*args))
                self.assertEqual(ny_dir(*args),funcs['ny_dir'](*args))

    def test_all_source_literals_match_frozen_original(self):
        keys=('THR','NY17_MIN','NY18_MIN','NY18_MAX','TP16','SL16','H16','TP17','SL17','H17','TP18','SL18','H18')
        tree=ast.parse(SOURCE.read_text())
        ns={'np':np}
        nodes=[n for n in tree.body if isinstance(n,ast.Assign) and
               len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and
               n.targets[0].id in keys]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),ns)
        self.assertEqual({k:tuple(ns[k]) for k in keys},
                         {k:getattr(current,k) for k in keys})

    def test_source_first_eligible_and_finite_50ms_cadence(self):
        o=OriginalJAN037Heartbeat50ms()
        # hour7 London threshold1000; eligible state H4/H1 positive M15/M5 negative
        h=7*3600000
        seq=[(0,100000),(1,101000),(2,101500),(3,101500),(4,101500)]
        out=[]
        for idx,mid in seq:
            t=h+[0,1,2,40,53][idx]
            v=o.on_observed_quote(idx,t,mid,1,1,-1,-1)
            if v:out.append((idx,v.source_id,v.side,v.hold_ms))
        self.assertEqual(out,[(1,17,1,1800000),(4,17,1,1800000)])

    def test_no_trade_without_original_structural_states(self):
        o=OriginalJAN037Heartbeat50ms()
        e=o.on_observed_quote(0,7*3600000,100000,-1,1,1,1)
        self.assertIsNone(e)
        with self.assertRaises(NotImplementedError):o.to_live_trade()

    def test_missing_bars_and_out_of_order_quotes_fail_closed(self):
        o=OriginalJAN037Heartbeat50ms()
        with self.assertRaises(ValueError):o.on_observed_quote(0,7*3600000,100000,2,1,1,1)
        o.on_observed_quote(0,7*3600000,100000,1,1,-1,-1)
        with self.assertRaises(ValueError):o.on_observed_quote(0,7*3600000,100000,1,1,-1,-1)

if __name__=='__main__':unittest.main()
