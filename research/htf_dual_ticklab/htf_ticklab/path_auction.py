"""Research-only causal multi-specialist auction, before funded order requests.

Models must estimate probabilities and MFE/MAE from historic PRIOR signals.
This never accesses future ticks, trains a model, places orders or claims fills.
No investor-approved risk cap is hardcoded here.
"""
from dataclasses import dataclass
from math import isfinite, sqrt

@dataclass(frozen=True,slots=True)
class PathProposal:
    specialist: str
    observed_ms: int
    broker: str
    side: int
    lots: float
    historical_samples: int
    probability_profit_first: float
    favorable_excursion_price: float
    adverse_excursion_price: float
    stop_distance_price: float
    target_distance_price: float

    def __post_init__(self):
        if not self.specialist or not self.broker or self.side not in (-1,1):
            raise ValueError("invalid proposal identity")
        if self.historical_samples<0 or not 0<=self.probability_profit_first<=1:
            raise ValueError("invalid evidence contract")
        if (not all(isfinite(x) for x in (
            self.lots,self.favorable_excursion_price,
            self.adverse_excursion_price,self.stop_distance_price,
            self.target_distance_price)) or
            min(self.lots,self.stop_distance_price,self.target_distance_price)<=0 or
            min(self.favorable_excursion_price,self.adverse_excursion_price)<0):
            raise ValueError("invalid path or order geometry")

@dataclass(frozen=True,slots=True)
class AuctionResult:
    selected: PathProposal | None
    expected_net_usd: float
    rejected: tuple[str,...]

def select_path(quote,proposals,broker_config, *,
                minimum_samples:int=100,maximum_signal_age_ms:int=2000,
                uncertainty_z:float=1.64)->AuctionResult:
    """Conservative expectancy-ranked alternative to global indicator AND gates.

    Probability is shrunk to a lower confidence bound, and all-in cost
    includes observable spread, round-trip slippage and commission.
    Only expected-net-positive, adequately sampled proposals may compete.
    A research-only separate account budget must approve the selected
    proposal before the existing shared-account engine queues any order.
    """
    if minimum_samples<2 or maximum_signal_age_ms<0 or uncertainty_z<0:
        raise ValueError("invalid calibration settings")
    if broker_config.name!=quote.broker:
        raise ValueError("broker account / quote mismatch")
    rejected=[];best=None;score=0.
    spread=quote.ask-quote.bid
    if not isfinite(spread) or spread<0:
        raise ValueError("invalid quote spread")
    for p in proposals:
        if p.broker!=quote.broker:
            rejected.append(p.specialist+":cross_broker");continue
        if p.observed_ms>quote.ms or quote.ms-p.observed_ms>maximum_signal_age_ms:
            rejected.append(p.specialist+":stale_or_future");continue
        if p.historical_samples<minimum_samples:
            rejected.append(p.specialist+":uncalibrated");continue
        if spread>broker_config.max_spread_price:
            rejected.append(p.specialist+":spread");continue
        # Minimum lot/step feasibility cannot be invented or silently resized.
        steps=round((p.lots-broker_config.min_lot)/broker_config.lot_step)
        if (p.lots<broker_config.min_lot or p.lots>broker_config.max_lot or
           abs(p.lots-(broker_config.min_lot+steps*broker_config.lot_step))>1e-8):
            rejected.append(p.specialist+":infeasible_lots");continue
        entry=quote.ask if p.side>0 else quote.bid
        margin=entry*p.lots*broker_config.contract_size/broker_config.leverage
        if margin>=broker_config.initial_balance:
            rejected.append(p.specialist+":minimum_margin");continue
        prob=p.probability_profit_first
        stderr=sqrt(prob*(1-prob)/p.historical_samples)
        conservative=max(0.,prob-uncertainty_z*stderr)
        units=p.lots*broker_config.contract_size
        gross=units*(conservative*min(p.favorable_excursion_price,p.target_distance_price)-
                     (1-conservative)*min(p.adverse_excursion_price,p.stop_distance_price))
        cost=units*(spread+2*broker_config.adverse_slippage_price)+(
                    2*broker_config.commission_per_lot_side*p.lots)
        expected=gross-cost
        if expected<=0:
            rejected.append(p.specialist+":negative_expected_net");continue
        if best is None or expected>score or (
           abs(expected-score)<1e-9 and p.specialist<best.specialist):
            best=p;score=expected
    return AuctionResult(best,round(score,9),tuple(rejected))
