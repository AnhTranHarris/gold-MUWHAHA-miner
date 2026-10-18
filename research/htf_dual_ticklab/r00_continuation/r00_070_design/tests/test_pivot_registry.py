from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from causal_pivot_registry import CompleteBar, confirm_pivots, available_pivots

def test_no_right_bar_future_leak_and_publication_timestamp():
    b=[CompleteBar(i*900000,(i+1)*900000,h,l,(h+l)*.5) for i,(h,l) in enumerate([(3,1),(4,2),(8,0),(5,2),(4,1)])]
    p=confirm_pivots(b,2,2)
    assert len([x for x in p if x.kind=='HIGH'])==1
    assert p[0].pivot_bar_start_utc_ms==2*900000
    assert p[0].publicly_known_utc_ms==5*900000
    assert not available_pivots(p,5*900000-1)
    assert available_pivots(p,5*900000)

def test_gap_prevents_pivot_construction():
    b=[CompleteBar(i*900000+(900000 if i>=3 else 0),(i+1)*900000+(900000 if i>=3 else 0),3+i,0,1) for i in range(5)]
    assert confirm_pivots(b,2,2)==[]
