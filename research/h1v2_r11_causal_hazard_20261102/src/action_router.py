"""R11 independent BUY/SELL/WAIT economic admissibility controller.

This is a research interface, NOT a fitted prediction model or live EA.
Inputs MUST be causally trained/frozen and independently calibrated. A finite
policy score never substitutes for out-of-sample evidence or trade-volume tests.
"""
from __future__ import annotations
import numpy as np

WAIT=0; BUY=1; SELL=-1

def decide_actions(probs,calibration_lower,conditional_win_net,
                   conditional_loss_magnitude,neutral_loss_magnitude,
                   additional_cost,cvar_penalty,
                   spread,*, max_spread=1.50,min_good_lower=.80,
                   max_bad=.20,min_expected_net=0.0,
                   min_directional_margin=.08):
    """Every side is checked independently before comparing score.

    probs[n,2,3] in [BAD,NEUTRAL,GOOD] order; conditional win/loss already
    contain *base* spread and historic research fee. additional_cost is only
    incremental broker/slippage cost: no fee double count. Returns WAIT if no
    independently eligible side. No quota-fill, no hindsight label access.
    """
    p=np.asarray(probs,np.float64)
    if p.ndim!=3 or p.shape[1:]!=(2,3):raise ValueError('probabilities need (n,2,3)')
    n=len(p)
    def shape(x,expect):
        z=np.asarray(x,np.float64)
        if z.shape!=expect:raise ValueError('shape or role mismatch')
        if not np.isfinite(z).all():raise ValueError('nonfinite policy inputs')
        return z
    lb=shape(calibration_lower,(n,2))
    gain=shape(conditional_win_net,(n,2));loss=shape(conditional_loss_magnitude,(n,2))
    neut=shape(neutral_loss_magnitude,(n,2));cost=shape(additional_cost,(n,2))
    cvar=shape(cvar_penalty,(n,2));spr=shape(spread,(n,))
    if not np.isfinite(p).all() or np.any(p<0) or np.any(p>1) or np.any(np.abs(p.sum(axis=2)-1)>1e-5):
        raise ValueError('invalid posteriors')
    if np.any(lb<0) or np.any(lb>1) or np.any(gain<0) or np.any(loss<0) or np.any(neut<0) or np.any(cost<0) or np.any(cvar<0) or np.any(spr<0):
        raise ValueError('invalid economic inputs')
    good=p[:,:,2];bad=p[:,:,0];neutral=p[:,:,1]
    net=good*gain-bad*loss-neutral*neut-cost-cvar
    eligible=(lb>=min_good_lower)&(bad<=max_bad)&(net>min_expected_net)&(spr[:,None]<=max_spread)
    independent=eligible.copy()
    # Real directional uniqueness: an otherwise eligible action requires
    # separation from its rival's strict-good posterior; even if rival has
    # failed independent qualification, ambiguity can still be penalized.
    separation=good[:,0]-good[:,1]
    # A rival that already failed its independent economic gate must NOT veto
    # the sole eligible side by having a misleadingly larger p(GOOD).
    eligible[:,0]&=(~independent[:,1]) | (separation>=min_directional_margin)
    eligible[:,1]&=(~independent[:,0]) | (-separation>=min_directional_margin)
    safe=np.where(eligible,net,-np.inf)
    selected=np.argmax(safe,axis=1)
    selected_any=eligible.any(axis=1)
    action=np.where(selected_any,np.where(selected==0,BUY,SELL),WAIT).astype(np.int8)
    return {'action':action,'eligible':eligible,'expected_incremental_net':net,
            'selected_expected_net':np.where(selected_any,safe[np.arange(n),selected],0.),
            'status':'CAUSAL_INPUT_CONTRACT_ONLY_NO_APPROVED_FITTED_POLICY'}
