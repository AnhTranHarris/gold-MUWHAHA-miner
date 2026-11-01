"""R150 stage2A strictly market-rooted 193D independent evidence schema."""
from __future__ import annotations
import numpy as np

BLOCKS={'r120':(0,128),'jlm':(128,137),'native':(137,169),'bayes':(169,193)}
SCHEMA_SIZE=193
DENY=('teacher','truth','correct_label','outcome','matured','r24','r148b','r150g','future')

def compose(*,r120:np.ndarray,jlm_market_scores:np.ndarray,
            native:np.ndarray,bayes:np.ndarray)->np.ndarray:
    """Four source-only blocks, frozen order, no arbitrary FIT-time target fields."""
    blocks=(np.asarray(r120,dtype=np.float32),np.asarray(jlm_market_scores,dtype=np.float32),
            np.asarray(native,dtype=np.float32),np.asarray(bayes,dtype=np.float32))
    if any(x.ndim!=1 or len(x)!=n for x,n in zip(blocks,(128,9,32,24))):
        raise ValueError('market feature provenance/width mismatch')
    x=np.concatenate(blocks)
    if not np.isfinite(x).all():raise ValueError('nonfinite market state')
    x.setflags(write=False)
    return x


def feature_groups():
    """Three DIFFERENT predeclared independent evidence views, not clones."""
    def b(name):
        s,e=BLOCKS[name];return np.arange(s,e,dtype=np.int64)
    cont=np.r_[b('r120'),b('jlm'),b('native')[:9],b('native')[23:30],b('bayes')[8:16]]
    reliability=np.r_[b('r120'),b('native')[8:26],b('bayes')]
    hard=np.arange(SCHEMA_SIZE,dtype=np.int64)
    assert len({tuple(v) for v in (cont,reliability,hard)})==3
    return {'continuation':cont,'reliability':reliability,'hard_negative':hard}
