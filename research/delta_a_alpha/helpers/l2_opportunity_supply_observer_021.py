#!/usr/bin/env python3
"""V1 L2 research-only opportunity supply observer; never transacts."""
from dataclasses import dataclass
from collections import deque
import json, math
from pathlib import Path
from typing import Optional

FEATURES = (
  "prior12_range10_rate", "prior48_range10_rate", "prior144_range10_rate",
  "prior48_range20_rate", "prior12_range_median", "prior48_range_p90",
  "prior144_mean_range", "prior12_mean_abs_change"
)

def _avg(seq):
    return sum(seq) / len(seq)

def _quantile(seq, p):
    data=sorted(seq); i=(len(data)-1)*p; j=int(i); frac=i-j
    return data[j]*(1-frac)+data[min(j+1,len(data)-1)]*frac

@dataclass(frozen=True)
class CompletedM5:
    close_usd: float
    high_usd: float
    low_usd: float

class L2OpportunitySupplyObserver:
    """Only call on fully completed M5 bars. Authorization for *frozen*
    JanFeb weights must not occur prior to 2026-03-01 UTC.
    This observer does NOT issue orders, renewals, or capital approvals.
    """
    def __init__(self, model):
        assert model["mode"] == "OBSERVE_ONLY_NO_ORDER_EFFECT"
        assert tuple(model["feature_names"]) == FEATURES
        self.model=model
        self.ranges=deque(maxlen=144)
        self.changes=deque(maxlen=12)
        self.prev_close=None

    def on_completed_m5(self, bar:CompletedM5, model_available:bool) -> Optional[float]:
        assert bar.high_usd >= bar.low_usd
        self.ranges.append(bar.high_usd-bar.low_usd)
        self.changes.append(0. if self.prev_close is None else abs(bar.close_usd-self.prev_close))
        self.prev_close=bar.close_usd
        if not model_available or len(self.ranges)<144:
            return None
        r=list(self.ranges)
        x=[
            _avg([v>=10. for v in r[-12:]]),
            _avg([v>=10. for v in r[-48:]]),
            _avg([v>=10. for v in r]),
            _avg([v>=20. for v in r[-48:]]),
            _quantile(r[-12:],.5),
            _quantile(r[-48:],.9),
            _avg(r),_avg(list(self.changes))
        ]
        z=float(self.model["logistic_intercept"])
        for val,mean,scale,coef in zip(x,self.model["scaler_mean"],self.model["scaler_scale"],self.model["logistic_coef"]):
            z+=coef*(val-mean)/scale
        z=max(-35.,min(35.,z))
        return 1./(1.+math.exp(-z))

    @staticmethod
    def can_send_orders():
        return False

def load_frozen_model(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
