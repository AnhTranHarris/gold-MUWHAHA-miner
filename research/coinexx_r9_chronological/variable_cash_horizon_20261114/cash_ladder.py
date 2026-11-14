"""R9 v1.94 research-only variable-horizon cash-exit controller.

Pure causal per-quote logic; does NOT modify the MT5 EA or generate market
quotes. All inputs are externally observed/fold-calibrated as-of values.
Stop/close outcomes remain subject to slippage, quote gaps and broker rules.
The controller must be embedded in the ORIGINAL chronological simulator before
any actual policy-profit or trade-frequency claims can be made.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

Action = Literal["HOLD", "CLOSE_NOW", "TIGHTEN_STOP", "BLOCK_ENTRY"]


@dataclass(frozen=True)
class CashLadderSpec:
    min_net_profit: float = 0.50
    stretch_net_profit: float = 1.75
    intended_max_loss_per_position: float = 2.00
    emergency_max_hold_s: float = 120.0  # failsafe, NOT a profit timer
    exit_advantage_lower_bound_min: float = 0.05
    first_cause_probability_margin: float = 0.10
    original_p5_valid_for_s: float = 5.0
    max_quote_age_ms: int = 2500
    incremental_trailing_gap_cash: float = 0.35
    account_capital_loss_ceiling_fraction: float = 0.25
    retain_original_peak_dd_fraction: float = 0.10

    def __post_init__(self) -> None:
        nums = (self.min_net_profit,self.stretch_net_profit,
                self.intended_max_loss_per_position,self.emergency_max_hold_s,
                self.exit_advantage_lower_bound_min,
                self.first_cause_probability_margin,
                self.original_p5_valid_for_s,self.incremental_trailing_gap_cash,
                self.account_capital_loss_ceiling_fraction,
                self.retain_original_peak_dd_fraction)
        if not all(isfinite(v) for v in nums):
            raise ValueError("Nonfinite policy input")
        if not (0 < self.min_net_profit < self.stretch_net_profit and
                self.intended_max_loss_per_position>0 and
                self.emergency_max_hold_s>0 and
                self.original_p5_valid_for_s>0 and
                0<=self.first_cause_probability_margin<=1 and
                0<=self.exit_advantage_lower_bound_min and
                0<self.incremental_trailing_gap_cash and
                0<self.account_capital_loss_ceiling_fraction<1 and
                0<self.retain_original_peak_dd_fraction<1 and
                self.max_quote_age_ms>0):
            raise ValueError("Invalid policy range")


@dataclass(frozen=True)
class AccountSnapshot:
    opening_reference_capital: float
    observed_peak_equity: float
    equity_now: float
    gross_loss_used_today: float
    allowed_daily_gross_loss_budget: float
    account_currency: str = "USD"

    def __post_init__(self) -> None:
        values = (self.opening_reference_capital, self.observed_peak_equity,
                  self.equity_now, self.gross_loss_used_today,
                  self.allowed_daily_gross_loss_budget)
        if not all(isfinite(z) for z in values) or not all(z>=0 for z in values):
            raise ValueError("Invalid account observation")
        if not self.account_currency:
            raise ValueError("Missing account currency")
        if self.opening_reference_capital<=0 or self.observed_peak_equity<=0:
            raise ValueError("Capital and peak must be positive")
        if self.observed_peak_equity < self.opening_reference_capital:
            raise ValueError("Peak must include opening reference capital")

    def lock_reason(self, spec: CashLadderSpec) -> str | None:
        if self.equity_now <= self.opening_reference_capital * (
                1.0-spec.account_capital_loss_ceiling_fraction):
            return "25% capital-loss emergency ceiling reached"
        if self.equity_now <= self.observed_peak_equity * (
                1.0-spec.retain_original_peak_dd_fraction):
            return "Existing 10% account peak-equity drawdown halt reached"
        if self.gross_loss_used_today >= self.allowed_daily_gross_loss_budget:
            return "Existing daily account gross-loss budget consumed"
        return None


@dataclass(frozen=True)
class CurrentPosition:
    side: int                           # 1 BUY, -1 SELL
    entry_executed_price: float         # BUY Ask / SELL Bid
    liquidation_bid: float
    liquidation_ask: float
    original_or_current_stop_price: float | None
    cash_per_xau_price_dollar: float    # K: broker calibrated for THIS lot/account
    additional_roundtrip_cost_cash: float  # C beyond Bid/Ask spread
    age_seconds: float
    since_last_quote_ms: int
    min_legal_stop_distance_xau: float  # broker stop+freeze+tick price distances

    def __post_init__(self) -> None:
        nums = (self.entry_executed_price,self.liquidation_bid,
                self.liquidation_ask,self.cash_per_xau_price_dollar,
                self.additional_roundtrip_cost_cash,self.age_seconds,
                self.min_legal_stop_distance_xau)
        if not all(isfinite(x) for x in nums):
            raise ValueError("Nonfinite quote or cash parameter")
        if (self.side not in (-1,1) or self.entry_executed_price<=0 or
                self.liquidation_bid<=0 or self.liquidation_ask<self.liquidation_bid or
                self.cash_per_xau_price_dollar<=0 or
                self.additional_roundtrip_cost_cash<0 or self.age_seconds<0 or
                self.since_last_quote_ms<0 or self.min_legal_stop_distance_xau<0):
            raise ValueError("Invalid executable quote/state")
        if self.original_or_current_stop_price is not None and (
                not isfinite(self.original_or_current_stop_price) or
                self.original_or_current_stop_price<=0):
            raise ValueError("Invalid existing stop")

    def liquidation_price(self) -> float:
        return self.liquidation_bid if self.side==1 else self.liquidation_ask

    def net_cash(self, exit_price: float | None = None) -> float:
        price = self.liquidation_price() if exit_price is None else exit_price
        return (self.side*(price-self.entry_executed_price)*
                self.cash_per_xau_price_dollar-
                self.additional_roundtrip_cost_cash)

    def stop_price_at_min_net_cash(self, cash_lock: float) -> float:
        """Stop quote price whose idealized fill earns >= cash_lock after costs."""
        shift = (cash_lock+self.additional_roundtrip_cost_cash)/self.cash_per_xau_price_dollar
        return self.entry_executed_price+self.side*shift

    def stop_is_legal_and_tighter(self, proposed: float) -> bool:
        # Trade server may reject freeze/stop modifications; tests check only
        # necessary quoted-side geometrical conditions, NOT acceptance.
        actual_liq = self.liquidation_price()
        if self.side == 1:
            legal=actual_liq-proposed >= self.min_legal_stop_distance_xau-1e-9
            improves=(self.original_or_current_stop_price is None or
                      proposed > self.original_or_current_stop_price+1e-9)
        else:
            legal=proposed-actual_liq >= self.min_legal_stop_distance_xau-1e-9
            improves=(self.original_or_current_stop_price is None or
                      proposed < self.original_or_current_stop_price-1e-9)
        return legal and improves


@dataclass(frozen=True)
class ConditionalEvidence:
    """Missing evidence never authorizes a speculative runner.

    P5/p_cash are entry-time five-second FIRST-CAUSE probabilities, not a
    probability of +$1.75 or a perpetual holding advantage. The lower bound
    of incremental hold cash utility requires a SEPARATE policy-specific
    chronological test; previous landmark research did not validate one.
    """
    favorable_first_5s: float | None = None
    adverse_first_5s: float | None = None
    lower_bound_hold_minus_exit_cash: float | None = None
    policy_specific_out_of_fold_validated: bool = False

    def __post_init__(self) -> None:
        for n in (self.favorable_first_5s,self.adverse_first_5s):
            if n is not None and (not isfinite(n) or n<0 or n>1):
                raise ValueError("Invalid first-cause probability")
        if (self.favorable_first_5s is not None and
                self.adverse_first_5s is not None and
                self.favorable_first_5s+self.adverse_first_5s>1+1e-9):
            raise ValueError("Invalid combined first-cause incidence")
        if (self.lower_bound_hold_minus_exit_cash is not None and
                not isfinite(self.lower_bound_hold_minus_exit_cash)):
            raise ValueError("Invalid incremental cash advantage")


@dataclass(frozen=True)
class ExitDecision:
    action: Action
    reason: str
    observed_liquidation_net_cash: float
    hypothetical_stop_price: float | None = None
    min_net_cash_lock: float | None = None
    baseline_fallback: bool = False


class VariableCashHorizonPolicy:
    """Does not create/close positions; recommends ONLY a causal action.

    Evaluate on EACH quote of an EXISTING R9 position, before trade execution;
    MT5 implementation would require confirmed server fills, proper rounding,
    OrderCalcProfit, Symbol stops/freeze and OnTradeTransaction reconciliation.
    """
    def __init__(self,spec:CashLadderSpec=CashLadderSpec()) -> None:
        self.spec=spec
        self.peak_observed_cash=float("-inf")
        self.profit_zone_visited=False

    def decide(self,position:CurrentPosition,account:AccountSnapshot,
               evidence:ConditionalEvidence | None=None) -> ExitDecision:
        s=self.spec
        observed=position.net_cash()
        self.peak_observed_cash=max(self.peak_observed_cash,observed)
        self.profit_zone_visited |= observed>=s.min_net_profit
        locked=account.lock_reason(s)
        if locked:
            return ExitDecision("CLOSE_NOW",locked,observed)
        if observed<=-s.intended_max_loss_per_position:
            return ExitDecision("CLOSE_NOW","Per-position $2 intended loss ceiling",observed)
        if (self.peak_observed_cash-observed >=
                s.intended_max_loss_per_position):
            return ExitDecision("CLOSE_NOW",
                "Per-position $2 peak-to-current cash drawdown ceiling",observed)
        if position.since_last_quote_ms>s.max_quote_age_ms:
            return ExitDecision("CLOSE_NOW","Stale quote: request close, do not trust price guarantee",observed)
        if observed>=s.stretch_net_profit:
            return ExitDecision("CLOSE_NOW","Stretch $1.75 realized cash goal reached",observed)
        if position.age_seconds>=s.emergency_max_hold_s:
            return ExitDecision("CLOSE_NOW","120s stranded-position failsafe (not profit clock)",observed)
        if observed>=s.min_net_profit:
            # The original five-second model is NOT sufficient to justify
            # holding; require a distinct, chronologically validated positive
            # lower bound for continuation value versus taking cash now.
            eligible = (evidence is not None and
                evidence.policy_specific_out_of_fold_validated and
                evidence.favorable_first_5s is not None and
                evidence.adverse_first_5s is not None and
                evidence.lower_bound_hold_minus_exit_cash is not None and
                position.age_seconds<=s.original_p5_valid_for_s and
                evidence.favorable_first_5s-evidence.adverse_first_5s >
                    s.first_cause_probability_margin and
                evidence.lower_bound_hold_minus_exit_cash >
                    s.exit_advantage_lower_bound_min)
            if eligible:
                # Lock >=$0.50 net if the broker allows a protective stop now.
                # Do not claim a cash floor is guaranteed under real slippage.
                desired=max(s.min_net_profit,
                            self.peak_observed_cash-s.incremental_trailing_gap_cash)
                proposed=position.stop_price_at_min_net_cash(desired)
                if position.stop_is_legal_and_tighter(proposed):
                    return ExitDecision("TIGHTEN_STOP",
                        "Validated runner: tighten to account-cash profit floor",
                        observed,proposed,desired)
                # If CURRENT stop already locks at least the desired minimum,
                # we can hold without loosening or sending an illegal change.
                old=position.original_or_current_stop_price
                if old is not None and position.net_cash(old)>=desired-1e-9:
                    return ExitDecision("HOLD",
                        "Existing stop already locks eligible runner net cash",
                        observed,old,desired)
                return ExitDecision("CLOSE_NOW",
                    "Cannot legally lock $0.50 net; harvest available cash",observed)
            return ExitDecision("CLOSE_NOW",
                "Take $0.50–$1.75 net; no validated positive continuation value",observed)
        # Preserve original R9 protective stop, including when its threshold
        # is much tighter than -$2. Do not widen simply because budget exists.
        if self.profit_zone_visited:
            return ExitDecision("CLOSE_NOW","Profit-zone quote reversed before protected exit",observed)
        return ExitDecision("HOLD","Below profit zone: original protective stop remains",observed,
                            baseline_fallback=True)

    def entry_permitted(self,position:CurrentPosition,account:AccountSnapshot) -> ExitDecision:
        """Risk gate only; NOT a high-AUC entry veto. Caller handles original S1."""
        if account.lock_reason(self.spec):
            return ExitDecision("BLOCK_ENTRY","Account safety lock",position.net_cash())
        stop=position.original_or_current_stop_price
        if stop is None:
            return ExitDecision("BLOCK_ENTRY","Missing protective stop",position.net_cash())
        if position.net_cash(stop)<-self.spec.intended_max_loss_per_position:
            return ExitDecision("BLOCK_ENTRY","Broker stop exceeds $2 intended cash risk",position.net_cash())
        potential_cash_loss=max(0.0,-position.net_cash(stop))
        if (account.gross_loss_used_today+potential_cash_loss
            >= account.allowed_daily_gross_loss_budget):
            return ExitDecision("BLOCK_ENTRY","Insufficient remaining daily gross-loss budget",position.net_cash())
        return ExitDecision("HOLD","Original R9 entry allowed by this overlay only",position.net_cash())