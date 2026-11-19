"""AR1 January R6 integrated historical *risk observation* state machine.

This is research telemetry only; no order methods, no risk veto, no modified exits.
Source contract: immutable R9 SYNTH entry/exit/book/fee net, original Coinexx REAL
millisecond bid/ask path, owner-frozen S100. All costs are original R9 recorded costs.

The primary six independent signals (no arbitrary weighted composite):
1 pre-entry prior-book realized HWM pressure
2 pre-entry loss-run and gross negative booked-PnL intensity (supplied causal inputs)
3 strict-preentry earlier-trained R5 loss probability or UNKNOWN if untrained
4 pre-entry Coinexx microstructure/HA/Fib contextual features
5 during-trade Coinexx quote-side S100 giveback and favorable/adverse excursions
6 data quality (no quote / delayed mapping / same-second exit/reentry ambiguity).
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
import numpy as np

S100_FROZEN=((100,4),(700,5),(1100,9),(16200,11),(19900,14),
             (27500,15),(29300,23),(33200,24),(33300,30),(340100,74))

def frozen_gap_cents(original_book_cents:int)->int:
    assert original_book_cents>0
    dollar_tier=max(100,(int(original_book_cents)//10000)*100)
    gap=4
    for minimum,g in S100_FROZEN:
        if dollar_tier>=minimum:gap=g
    return gap*100

@dataclass
class TradeRiskObservation:
    source_row:int
    side:str
    true_entry_second_ms:int
    observed_quote_window_entry_ms:int
    observed_quote_window_exit_ms:int
    gap_cents:int
    booked_hwm_drawdown_cents:int
    previous_closed_loss_run:int
    prior_60m_gross_loss_to_book:float
    strictly_prior_entry_loss_probability:float|None
    quote_count:int=0
    observed_mfe_cents:int|None=None
    observed_mae_cents:int|None=None
    observed_peak_dd_cents:int|None=None
    first_u25_ms:int=-1
    first_u50_ms:int=-1
    first_u75_ms:int=-1
    first_u90_ms:int=-1
    first_full_touch_ms:int=-1
    original_exit_processed:bool=False

    def observe_exact_window_quote_sequence(self,ms:np.ndarray,bids:np.ndarray,asks:np.ndarray):
        """Chronologically equivalent to per-tick high-water observer; records *first* crossings.

        All arrays must be original consecutive Coinexx quotes in source order, exclusively
        in the original fixed source window, and use integer-cent prices.
        """
        assert not self.original_exit_processed
        assert len(ms)==len(bids)==len(asks)
        assert (len(ms)==0 or (ms[0]>=self.observed_quote_window_entry_ms and ms[-1]<=self.observed_quote_window_exit_ms))
        assert (len(ms)<2 or bool(np.all(ms[1:]>=ms[:-1])))
        assert bool(np.all(bids>0)) and bool(np.all(asks>=bids))
        n=len(ms);self.quote_count=n
        if n==0:return
        marks=(bids-asks[0]) if self.side=='buy' else (bids[0]-asks)
        q=bids if self.side=='buy' else -asks
        dd=np.maximum.accumulate(q)-q
        self.observed_mfe_cents=int(max(0,marks.max()))
        self.observed_mae_cents=int(max(0,-marks.min()))
        self.observed_peak_dd_cents=int(dd.max())
        for f,field in ((.25,'first_u25_ms'),(.50,'first_u50_ms'),(.75,'first_u75_ms'),(.90,'first_u90_ms'),(1.,'first_full_touch_ms')):
            first=np.flatnonzero(dd>=self.gap_cents*f)
            setattr(self,field,int(ms[first[0]]) if first.size else -1)

    def state_at_end(self,strict_anchor:bool,ambiguous_prior_exit:bool)->dict:
        return {
            'source_row':self.source_row,
            'p_R9_loss_asof':self.strictly_prior_entry_loss_probability,
            'probability_is_held_day_trained':self.strictly_prior_entry_loss_probability is not None,
            'prior_R9_book_under_HWM':self.booked_hwm_drawdown_cents>0,
            'prior_R9_loss_cluster_ge2':self.previous_closed_loss_run>=2,
            'prior_R9_gross_loss_60m_fraction_of_book':self.prior_60m_gross_loss_to_book,
            'observed_S100_u25':self.first_u25_ms>=0,
            'observed_S100_u50':self.first_u50_ms>=0,
            'observed_S100_u75':self.first_u75_ms>=0,
            'observed_S100_u90':self.first_u90_ms>=0,
            'observed_full_S100':self.first_full_touch_ms>=0,
            'real_tick_quality':('NO_INSIDE_TICK' if not self.quote_count else ('STRICT' if strict_anchor else 'NONSTRICT_ANCHOR')),
            'same_second_prior_exit_ambiguity':bool(ambiguous_prior_exit),
            'trade_action':'NONE_OBSERVATIONAL_ONLY',
        }

class HistoricalR9BookObserver:
    def __init__(self,opening_book_cents=10000):
        self.book_cents=int(opening_book_cents)
        self.hwm_cents=self.book_cents
        self.completed=0
        self.sum_net_cents=0
    def start(self,expected_book_before_cents:int,expected_frozen_gap_cents:int):
        assert self.book_cents==int(expected_book_before_cents)
        assert frozen_gap_cents(self.book_cents)==int(expected_frozen_gap_cents)
        return max(0,self.hwm_cents-self.book_cents)
    def record_original_fixed_exit(self,original_r9_net_cents:int,expected_original_book_after_cents:int):
        self.book_cents+=int(original_r9_net_cents)
        self.sum_net_cents+=int(original_r9_net_cents)
        assert self.book_cents==int(expected_original_book_after_cents)
        self.hwm_cents=max(self.hwm_cents,self.book_cents)
        self.completed+=1
