"""Recover GRID0185 original as-of M5-energy conditional horizon, RESEARCH ONLY.

Read-only source: GRID0185/grid0185j_full_strict_49.py and GRID0185 report.
Input is completed M5 true range as of event, observed Bid/Ask current spread,
original extra per-oz cost. Returns a proposed research holding *horizon*,
NOT a funded trade, forecast, stop or authorization. 30/90 minute native
mechanism was historical Apr-Jul quote-positive with inadequate R9 volume.
"""
from dataclasses import dataclass
from typing import Optional
@dataclass(frozen=True)
class GridExitResearchHint:
    horizon_ms:int
    m5_energy:float
    rule:str='GRID0185_M5_ENERGY_FAST30_SLOW90'

class AsOfM5EnergyHarvestRunner:
    def __init__(self,*,cost_usd_per_oz=.52,fast_m=30,slow_m=90,energy_threshold=2.0):
        if cost_usd_per_oz<0 or fast_m<=0 or slow_m<fast_m or energy_threshold<=0:
            raise ValueError('bad original research horizon rule')
        self.cost=cost_usd_per_oz
        self.fast=fast_m*60000
        self.slow=slow_m*60000
        self.threshold=energy_threshold
    def select(self,*,quote_ms:int,bid_raw:int,ask_raw:int,
               completed_m5_tr_raw:Optional[int],asof_ms:Optional[int])->Optional[GridExitResearchHint]:
        if completed_m5_tr_raw is None:
            if asof_ms is not None:raise ValueError('orphan completed source timestamp')
            return None
        if asof_ms is None or asof_ms>=quote_ms:raise ValueError('future/current M5 source input')
        if completed_m5_tr_raw<0 or bid_raw<=0 or ask_raw<bid_raw:
            raise ValueError('invalid completed TR or executable quote')
        spread=(ask_raw-bid_raw)/1000
        tr=completed_m5_tr_raw/1000
        energy=tr/max(.1,spread+self.cost)
        return GridExitResearchHint(self.fast if energy<=self.threshold else self.slow,energy)
