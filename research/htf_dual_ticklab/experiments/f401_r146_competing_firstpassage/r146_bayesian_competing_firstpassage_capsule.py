"""F401-R146 standalone absorbing-barrier Bayesian VOI kernel.
Research-only GitHub capsule: full tested source, per-event original masks,
numerical lookup, and MQL5 research adapter remain in pinned portable ZIP.
Not an original R9 incorrect probability; no submitted orders.
"""
from dataclasses import dataclass
from math import exp, erf, sqrt
from typing import Sequence
FAST_CLOCKS=(250,500,1000,5000,15000,30000)
CORRECT_LOSS_CAP=.008278

def phi(z):
    return .5*(1.+erf(z/sqrt(2.)))

def competing_first_passage(drift:float, vol:float, good_barrier:float,
                            bad_barrier:float, seconds:float,
                            bins:int=17,steps:int=24)->tuple[float,float,float]:
    """Finite-volume absorbing diffusion with within-step bridge correction.
    Three EXCLUSIVE physical outcomes: favorable first, adverse first, survivor.
    Intended for independent calibration, not an original correctness classifier.
    """
    if min(vol,good_barrier,bad_barrier,seconds)<=0:raise ValueError("physical parameters")
    dx=(good_barrier+bad_barrier)/bins
    pos=[-bad_barrier+(i+.5)*dx for i in range(bins)]
    mass=[0.]*bins
    k=max(0,min(bins-1,int(bad_barrier/dx)))
    mass[k]=1.
    dt=seconds/steps
    sd=vol*sqrt(dt)
    favored=adverse=0.
    for _ in range(steps):
        new=[0.]*bins
        for i,p in enumerate(mass):
            if p<1.e-15:continue
            mean=pos[i]+drift*dt
            adverse+=p*phi((-bad_barrier-mean)/sd)
            favored+=p*(1.-phi((good_barrier-mean)/sd))
            for j in range(bins):
                lower=-bad_barrier+j*dx
                upper=lower+dx
                prob=phi((upper-mean)/sd)-phi((lower-mean)/sd)
                if prob<=0:continue
                gg=exp(max(-75.,-2*(good_barrier-pos[i])*(good_barrier-pos[j])/(vol*vol*dt)))
                bb=exp(max(-75.,-2*(bad_barrier+pos[i])*(bad_barrier+pos[j])/(vol*vol*dt)))
                absorbed=min(1.,gg+bb)
                favored+=p*prob*absorbed*gg/(gg+bb+1.e-30)
                adverse+=p*prob*absorbed*bb/(gg+bb+1.e-30)
                new[j]+=p*prob*(1.-absorbed)
        mass=new
    survivor=sum(mass)
    norm=favored+adverse+survivor
    return favored/norm,adverse/norm,survivor/norm

@dataclass(frozen=True)
class CorrectProtection:
    broker:str
    original_side:int
    cal_correct_sample:int
    upper_false_veto_rate:float
    frozen_model_sha:str
    frozen_calibration_sha:str
    def permits_veto(self)->bool:
        if self.broker not in ("coinexx","dukascopy") or self.original_side not in (-1,1):
            raise ValueError("broker/direction mismatch")
        if self.cal_correct_sample<100 or not self.frozen_model_sha or not self.frozen_calibration_sha:
            raise ValueError("uncalibrated correct protection")
        return 0<=self.upper_false_veto_rate<=CORRECT_LOSS_CAP

@dataclass(frozen=True)
class QuoteState:
    broker:str
    original_side:int
    original_t0_ms:int
    decision_ms:int
    latest_quote_ms:int
    clocks_ms:tuple[int,...]
    source_sha:str
    favorable_drift_per_second:float
    sigma_per_root_second:float
    price_to_favorable:float
    price_to_adverse:float
    current_spread:float
    change_probability:float
    original_truth_read:bool=False
    t0_order_submitted:bool=False
    def check(self):
        if self.clocks_ms!=FAST_CLOCKS:raise ValueError("NO minute/hour clocks")
        if self.original_side not in (-1,1):raise ValueError("direction")
        if not self.source_sha or self.broker not in ("coinexx","dukascopy"):raise ValueError("source")
        if self.latest_quote_ms>=self.decision_ms or not 0<=self.decision_ms-self.original_t0_ms<=15000:raise ValueError("future or invalid time")
        if self.original_truth_read or self.t0_order_submitted:raise ValueError("truth leakage / retroactive veto")
        if min(self.sigma_per_root_second,self.price_to_favorable,self.price_to_adverse)<=0:raise ValueError("barrier scale")
        if not 0<=self.change_probability<=1:raise ValueError("changepoint")

def protected_decision(s:QuoteState,g:CorrectProtection,fee_per_oz=.20):
    s.check()
    if (s.broker,s.original_side)!=(g.broker,g.original_side):raise ValueError("guard broker side")
    uncertainty=s.sigma_per_root_second*(.2+.65*s.change_probability)
    cases=[competing_first_passage(s.favorable_drift_per_second+d,s.sigma_per_root_second,
                                  s.price_to_favorable,s.price_to_adverse,15.)
           for d in (-uncertainty,0.,uncertainty)]
    good,bad,neutral=cases[1]
    bad_lower=min(r[1] for r in cases)
    good_upper=max(r[0] for r in cases)
    expected_quote_edge=good*s.price_to_favorable-bad*s.price_to_adverse-s.current_spread-fee_per_oz
    if g.permits_veto() and bad_lower>=.75 and good_upper<=.10:
        action="VETO_NEW_UNSUBMITTED_INTENT"
    elif s.decision_ms-s.original_t0_ms<15000:
        action="CONTINUE_OBSERVING"
    elif expected_quote_edge<=0 or not g.permits_veto():
        action="EXPIRE_UNSUBMITTED_INTENT"
    else:
        action="SHADOW_LIMIT_REPRICE_NOT_A_BROKER_FILL"
    return dict(action=action,physical_favorable=good,physical_adverse=bad,
                neutral_survivor=neutral,estimated_quote_edge=expected_quote_edge,
                original_truth_not_used=True,order_sent=False)

if __name__=="__main__":
    good,bad,neutral=competing_first_passage(0.,.5,1.,1.,15.)
    assert abs(good-bad)<.08 and abs(good+bad+neutral-1.)<1.e-9
    print(dict(favorable=good,adverse=bad,neutral=neutral))
