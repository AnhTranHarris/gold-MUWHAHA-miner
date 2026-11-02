"""State-dependent multivariate bid/ask quote-event Hawkes research component.

SIX observable events: bid-up/down, ask-up/down, spread-widen/narrow.
Quote events are not genuine order-flow imbalance or trade-volume data.
The 6x6 excitation matrix is STABLE by construction but not fitted yet;
therefore its outputs are causal candidate features only, NEVER probabilities
of profitable trades until calibrated from strictly past time periods.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
import numpy as np

MARKS=('BID_UP','BID_DOWN','ASK_UP','ASK_DOWN','SPREAD_WIDEN','SPREAD_NARROW')

@dataclass(frozen=True)
class HawkesConfig:
    taus_ms:tuple=(250.,1000.,5000.,15000.,45000.)
    baseline:float=.02
    cross_excitation:float=.025
    self_excitation:float=.035
    spread_switch:float=.01

class CompetingQuoteHawkes:
    def __init__(self,config=HawkesConfig()):
        self.config=config;self.t=None;self.last_bid=None;self.last_ask=None
        self.state=np.zeros((len(config.taus_ms),6),dtype=np.float64)
        self.A=np.zeros((6,6),dtype=np.float64)
        for i in range(6):self.A[i,i]=config.self_excitation
        # Cross-side following/reversal from same direction (bid then ask / ask then bid).
        for a,b in ((0,2),(2,0),(1,3),(3,1)):
            self.A[a,b]=config.cross_excitation
        # Spread-widen events can excite narrowing, and vice-versa.
        self.A[4,5]=config.cross_excitation;self.A[5,4]=config.cross_excitation
        assert max(abs(np.linalg.eigvals(self.A)))<1.,'unstable excitation'
    def observe(self,t_ms,bid,ask):
        if ask<bid:raise ValueError('crossed quotes')
        if self.t is not None and t_ms<self.t:raise ValueError('future ordering violation')
        if self.t is not None:
            delta=t_ms-self.t
            decay=np.exp(-delta/np.asarray(self.config.taus_ms,dtype=np.float64))
            self.state*=decay[:,None]
        marks=np.zeros(6)
        if self.last_bid is not None:
            db=bid-self.last_bid;da=ask-self.last_ask
            ds=(ask-bid)-(self.last_ask-self.last_bid)
            for i,v in enumerate((db,-db,da,-da,ds,-ds)):
                marks[i]=float(v>1.e-10)
            # new quote mark *observable now* may cause future intensity, not
            # retroactively predict the mark which just occurred.
            self.state+=marks[None,:]
        self.t=int(t_ms);self.last_bid=float(bid);self.last_ask=float(ask)
        return tuple(marks)
    def intensities(self):
        # weighted combination of scales. Cross effect from positive marks.
        weighted=np.mean(self.state,axis=0)
        lam=self.config.baseline + self.A@weighted
        spread=self.last_ask-self.last_bid if self.last_bid is not None else 0.
        # At minimum spread, price/spread narrowing intensity is inhibited.
        if spread<=self.config.spread_switch:
            lam[5]=0.
        return lam
    def features(self):
        lam=self.intensities()
        up=lam[0]+lam[2];down=lam[1]+lam[3]
        direction=(up-down)/(up+down+1.e-12)
        sp=(lam[5]-lam[4])/(lam[5]+lam[4]+1.e-12)
        entropy=-float(np.sum((lam/(lam.sum()+1.e-12))*np.log(lam/(lam.sum()+1.e-12)+1.e-12)))
        return dict(lambda_channels=lam.copy(),direction=float(direction),
                    spread_pressure=float(sp),entropy=entropy,
                    raw_multi_tau=self.state.copy(),fitted=False)
