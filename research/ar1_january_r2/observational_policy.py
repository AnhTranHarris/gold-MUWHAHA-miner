"""AR1 January R2 - observational account-risk state engine (NOT an order governor).

Original R9: exact fixed trade schedule, fee-inclusive net results and BOOKED balance only.
Original Coinexx REAL TickLogger: timestamped bid/ask path and causal completed-bar feature context.
This module NEVER creates, edits, suppresses, closes, replaces or books a trading order.
S100 frozen gap schedule is read-only and must be computed from the original R9 entry book.

MARKET-FIT NOTE: coefficients are a January 2026 historical in-sample fit. Numeric online
features are causal but coefficients learned from January are not prospective validation.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
import math
from pathlib import Path

FROZEN_S100_TIERS_USD = ((100,4),(700,5),(1100,9),(16200,11),(19900,14),
                         (27500,15),(29300,23),(33200,24),(33300,30),(340100,74))

def s100_gap_usd(original_r9_booked_balance_usd: float)->int:
    """Owner-frozen single-trade S100 gap, no refitting or inference from Coinexx P&L."""
    tier=max(100,int(original_r9_booked_balance_usd//100)*100)
    out=4
    for threshold,gap in FROZEN_S100_TIERS_USD:
        if tier>=threshold:out=gap
    return out

def _logp(v:float)->float:
    x=float(v)
    return math.log1p(max(0,x)) if math.isfinite(x) else float('nan')

def causal_market_features(s:dict)->dict[str,float]:
    """No observed future DD, outcome, retrospective 27-family label or future bar."""
    gap=float(s['frozen_s100_gap_cents'])/100
    ln10=_logp(s['quotes_10s']);lns=_logp(s['spread_mean_60s_USD'])
    return {
      'ln_10s_quote_updates':ln10,
      'ln_60s_spread':lns,
      'ln_10s_travel':_logp(s['mid_abs_travel_10s_USD']),
      'ln_60s_travel':_logp(s['mid_abs_travel_60s_USD']),
      'ln_M1_ATR14':_logp(s['M1_ATR14_USD']),
      'ln_M5_ATR14':_logp(s['M5_ATR14_USD']),
      'ln_S100_gap':_logp(gap),
      'spread_times_quote_intensity':lns*ln10,
      'ln_quote_staleness':_logp(s['quote_age_sec']),
      'ln_asof_60m_gross_losses':_logp(float(s['gross_loss_rolling_60m_cents'])/100),
      'R9_preentry_hwm_drawdown_pct':float(s['R9_book_HWM_drawdown_pct']),
      'ln_M5_ATR_per_gap':_logp(float(s['M5_ATR14_USD'])/gap),
    }

def load_january_model(path:str|Path)->dict:
    d=json.loads(Path(path).read_text())
    return d['util25']['selected_model_parameters']

def market_pressure_probability(causal:dict[str,float],frozen_january_fit:dict)->float:
    """Exact serialized 12-variable regularized logistic equation, no sklearn runtime."""
    z=float(frozen_january_fit['intercept_on_scaled_features'])
    for name in frozen_january_fit['features']:
        val=float(causal[name]);stats=frozen_january_fit
        if not math.isfinite(val):val=stats['training_imputation_medians'][name]
        center=stats['training_standardization_means'][name]
        scale=stats['training_standardization_stds'][name]
        z+=stats['standardized_coefficients'][name]*(val-center)/(scale if scale>0 else 1.)
    return 1/(1+math.exp(-max(-700,min(700,z))))

@dataclass
class ObservedCoinexxPositionRisk:
    """Read-only tick risk. buy=Bid liquidation, sell=Ask liquidation, all integer cents."""
    source_row: int
    side: str
    original_R9_entry_ms: int
    original_R9_exit_ms: int
    frozen_gap_cents: int
    peak_liquidation_cents: int | None = None
    latest_u: float | None = None
    number_of_ticks: int = 0
    first_u25_ms: int = -1
    first_u50_ms: int = -1
    first_u75_ms: int = -1
    first_u90_ms: int = -1
    first_full_s100_ms: int = -1

    def observe_original_real_quote(self,t_ms:int,bid_cents:int,ask_cents:int)->dict|None:
        if not (self.original_R9_entry_ms<=t_ms<=self.original_R9_exit_ms):return None
        if bid_cents<=0 or ask_cents<bid_cents:raise ValueError('invalid original real quote')
        if self.frozen_gap_cents<=0:raise ValueError('invalid S100 gap')
        q=bid_cents if self.side.lower()=='buy' else -ask_cents
        self.peak_liquidation_cents=q if self.peak_liquidation_cents is None else max(self.peak_liquidation_cents,q)
        dd=int(self.peak_liquidation_cents-q)
        self.number_of_ticks+=1
        self.latest_u=dd/self.frozen_gap_cents
        for level,field in [(0.25,'first_u25_ms'),(0.50,'first_u50_ms'),(0.75,'first_u75_ms'),(0.90,'first_u90_ms'),(1.,'first_full_s100_ms')]:
            if self.latest_u>=level and getattr(self,field)<0:setattr(self,field,t_ms)
        return {'source_row':self.source_row,'tick_time_ms':t_ms,'observed_quote_giveback_cents':dd,'S100_utilization':self.latest_u,'market_observation_state':('OBSERVED_FULL_S100_TOUCH' if self.latest_u>=1 else 'OBSERVED_HIGH_INTRAHOLD_PRESSURE' if self.latest_u>=.5 else 'OBSERVED_ELEVATED_INTRAHOLD_PRESSURE' if self.latest_u>=.25 else 'OBSERVED_BELOW_QUARTER_S100_ALLOWANCE'),'trade_action':None}

def asof_booked_risk(original_R9_book_cents:int,previous_book_HWM_cents:int,earlier_realized_negative_60m_cents:int,earlier_consecutive_losses:int)->dict:
    """All values are from already-realized prior R9 exits; nothing from future trade outcome."""
    if original_R9_book_cents<=0:return {'booked_capital_state':'NONPOSITIVE_BOOK_UNSUPPORTED'}
    return {'R9_book_drawdown_pct':100*max(0,previous_book_HWM_cents-original_R9_book_cents)/max(1,previous_book_HWM_cents),
      'gross_loss_60m_USD':earlier_realized_negative_60m_cents/100,
      'prior_consecutive_negative_R9_exits':earlier_consecutive_losses,
      'booked_capital_state':('UNDER_PREVIOUS_BOOK_HIGH' if original_R9_book_cents<previous_book_HWM_cents else 'AT_BOOK_HIGH'),
      'trade_action':None}
