"""F401-R150 Bayesian quote-state bridge, market-only, still UNTRAINED as class head.

Reuses the verified R150T full-native-quote BOCPD/F3U source. One update per
native quote, one constant-time snapshot per eligible as-of decision. Does not
fit classifier, claim R150Q gain, or consume fitted FILTER08 class feedback.
"""
from dataclasses import dataclass
import numpy as np
from r150t_native_quote_bayes import NativeQuoteBayes,FEATURE_NAMES

@dataclass(frozen=True)
class SourceBayesState:
    last_native_ms:int
    decision_ms:int
    side:int
    features:np.ndarray

class NativeBayesPublisher:
    def __init__(self,hazard_seconds=180.,max_run=48):
        self._engine=NativeQuoteBayes(hazard_seconds,max_run)
    def update_native_quote(self,t_ms:int,bid_raw:int,ask_raw:int)->None:
        self._engine.observe(t_ms,bid_raw,ask_raw)
    def snapshot_prior_to(self,decision_ms:int,side:int)->SourceBayesState:
        o=self._engine.snapshot(decision_ms,side)
        return SourceBayesState(o.last_quote_ms,o.decision_ms,int(side),o.vector)

assert len(FEATURE_NAMES)==24
