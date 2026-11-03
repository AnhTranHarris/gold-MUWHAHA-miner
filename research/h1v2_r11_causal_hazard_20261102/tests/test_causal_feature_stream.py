import numpy as np
from causal_feature_stream import USE_INDICES,FIELDS_USED,USE_NAMES
from event_graph import extract

def test_chunk_exact_prefix_with_equal_ms_and_mixed_quote_marks():
    rng=np.random.default_rng(10249)
    n=3200
    t=np.cumsum(rng.choice([0,0,1,4,17,100,1000],size=n)).astype(np.int64)
    b=100+np.cumsum(rng.choice([-.2,-.1,0,.1,.2],size=n)).astype(float)
    a=b+.8+np.cumsum(rng.choice([-.03,0,.03],size=n))*.01
    ix=np.arange(150,n,13,dtype=np.int64)
    direct=extract(t,b,a,ix)[:,USE_INDICES]
    parts=[]
    for start in range(0,n,420):
        end=min(n,start+420)
        lo=np.searchsorted(ix,start,side='left');hi=np.searchsorted(ix,end,side='left')
        if lo==hi:continue
        hist=max(0,np.searchsorted(t,t[start]-300000,side='left')-2)
        parts.append(extract(t[hist:end],b[hist:end],a[hist:end],ix[lo:hi]-hist)[:,USE_INDICES])
    got=np.vstack(parts)
    assert got.shape==direct.shape
    assert np.allclose(got,direct,atol=1e-4,rtol=1e-5)
    assert len(USE_NAMES)==len(FIELDS_USED)*7
