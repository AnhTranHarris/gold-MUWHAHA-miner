"""R139 finite-state Bayesian microgrid core — research only.
Full original-event alignment, training, masks and MQL5 kernel are in the
source-exact R139–R142 ZIP SHA256 7efe01e34fcbdf679c54d58e5f01cf5d28c6170b7b806fbbe07734e4759b5561.
Original classes: 0=CORRECT protected,1=OPPOSITE veto,2=NEUTRAL veto.
Use ONLY final t0+15s decision with this historical actiontime grid context.
Earlier prefix traces are NOT causally valid until an earlier-asof grid is supplied.
No orders. No trading authority.
"""
import numpy as np
from scipy.special import logsumexp
CLASSES,CONTEXTS,STATES,RUNS=3,6,5,4
HORIZONS_MS=(250,500,1000,2000,3000,5000,8000,10000,12000,15000)
def context_from_six_clock(x):
    """Source R120 six clock direction-signed slopes + native grid support."""
    s=x[:,[0,11,22,33,44,55]]
    u=x[:,[4,15,26]]
    trend=np.where((s>.045).sum(1)>=4,2,np.where((s>.045).sum(1)<=1,0,1))
    contact=(np.minimum(u,1-u).mean(1)<.19).astype('i1')
    return (2*trend+contact).astype('i1')
def quantize_signed_path(xpath,grid92):
    """Five-way weak/strong adverse vs weak/strong favorable, and neutral."""
    rng=np.expm1(np.clip(grid92[:,[6,17,28]],0,13))/1000.
    step=np.clip(.35*(.5*rng[:,0]+.3*rng[:,1]+.2*rng[:,2]),.04,1.50)
    mark=xpath[:,np.arange(0,30,3)]
    move=np.diff(np.column_stack([np.zeros(len(mark)),mark]),axis=1)/step[:,None]
    return np.where(move<=-1,0,np.where(move<-.18,1,np.where(move<=.18,2,np.where(move<1,3,4)))).astype('i1')
def posterior_on_complete_15s_path(model,state,context):
    """Bounded classwise forward log-evidence and renewal/run-length posterior.
    model keys prior(3,6),init(3,6,5),trans(3,6,5,4,5),renew(3,6,5).
    Caller must certify both native-grid snapshot and whole path are <=t0+15s.
    """
    n=len(state)
    q=np.zeros((3,n,4),dtype=np.float64)
    loge=np.zeros((3,n),dtype=np.float64)
    for cls in range(3):
        q[cls,:,0]=1.
        loge[cls]=np.log(np.maximum(model['class_prior'][cls,context],1e-300))
        loge[cls]+=np.log(np.maximum(model['init'][cls,context,state[:,0]],1e-300))
    for t in range(1,state.shape[1]):
        prev=state[:,t-1];now=state[:,t]
        for cls in range(3):
            h=np.clip(model['renew'][cls,context,prev],.02,.65)
            new=np.zeros((n,4),np.float64)
            new[:,0]=q[cls].sum(1)*h*model['init'][cls,context,now]
            for r in range(4):
                new[:,min(r+1,3)]+=q[cls,:,r]*(1-h)*model['trans'][cls,context,prev,r,now]
            evid=np.maximum(new.sum(1),1e-300)
            q[cls]=new/evid[:,None]
            loge[cls]+=np.log(evid)
    post=np.exp(loge-logsumexp(loge,axis=0,keepdims=True)).T
    assert np.all(np.isfinite(post)) and np.max(np.abs(post.sum(1)-1))<1e-8
    return post
