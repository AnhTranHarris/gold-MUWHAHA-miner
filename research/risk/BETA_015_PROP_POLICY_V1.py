"""Owner-fixed BETA research-account prop-style risk policy, independent of strategy.

Use this guard in NEW research simulators; it DOES NOT modify/claim historical BETA014.
No real orders, no MetaTrader calls, no automatic strategy authorisation.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, time, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import math
from typing import Literal


class PolicyViolation(ValueError):
    pass


@dataclass(frozen=True)
class Policy:
    policy_id: str
    initial_balance: float
    fixed_lots: float
    contract_oz: float
    fee_side: float
    soft_usd: float
    hard_usd: float
    overall_floor_usd: float
    risk_fraction: float
    margin_leverage: float
    timezone: str
    news_status: str
    slippage_per_oz: float

    @staticmethod
    def from_json(path: str | Path) -> "Policy":
        raw = json.loads(Path(path).read_text(encoding="utf8"))
        expected = {
            "policy_id": "BETA_015_PROP_V1", "symbol": "XAUUSD",
            "initial_balance_usd": 100000.0,
            "fixed_lots": 0.01,
            "contract_oz_per_standard_lot": 100.0,
            "max_concurrent_positions": 1, "max_total_open_lots": 0.01,
            "commission_per_side_usd": 0.01,
            "daily_soft_loss_usd": 4000.0,
            "daily_hard_loss_usd": 5000.0,
            "overall_static_equity_floor_usd": 90000.0,
            "max_planned_risk_fraction_of_current_equity": 0.0025,
            "risk_day_reset_timezone": "America/New_York",
            "risk_day_reset_hour_local": 17,
            "risk_checks_include_floating_pnl": True,
            "terminal_overall_stop_persists_forever": True,
            "owner_approval_change_required": True,
            "illustrative_margin_leverage": 100.0,
            "news_filter_status": "NOT_EVALUATED_UNTIL_VERIFIED_EVENT_CALENDAR",
        }
        for k, v in expected.items():
            if raw.get(k) != v:
                raise PolicyViolation(f"Owner-controlled research profile drift: {k}")
        if raw.get("higher_risk_profile_maturity_change") != "EXPLICIT_OWNER_REQUEST_NEW_VERSION_AND_FULL_REPLAY_REQUIRED":
            raise PolicyViolation("Profile revision must be owner-approved and versioned")
        return Policy(
            policy_id=raw["policy_id"], initial_balance=raw["initial_balance_usd"],
            fixed_lots=raw["fixed_lots"], contract_oz=raw["contract_oz_per_standard_lot"],
            fee_side=raw["commission_per_side_usd"], soft_usd=raw["daily_soft_loss_usd"],
            hard_usd=raw["daily_hard_loss_usd"], overall_floor_usd=raw["overall_static_equity_floor_usd"],
            risk_fraction=raw["max_planned_risk_fraction_of_current_equity"],
            margin_leverage=raw["illustrative_margin_leverage"],
            timezone=raw["risk_day_reset_timezone"],news_status=raw["news_filter_status"],
            slippage_per_oz=raw["slippage_usd_per_oz_assumed"]
        )


@dataclass
class Position:
    side: Literal[-1, 1]
    entry: float
    stop: float
    lots: float
    opened_utc: datetime


@dataclass(frozen=True)
class TickResult:
    equity: float
    balance: float
    daily_reference: float
    soft_locked: bool
    hard_locked: bool
    terminated: bool
    closed_by_risk: bool
    block_reason: str | None


class PropRiskGuard:
    """Stateful, persistent funded-account governor for ONE aggregate position.

    Inputs must be actual observed UTC times and executable bid/ask; no future data.
    on_tick() enforces marked-equity risk stops; strategy exits call close_position().
    Funding stops never restart. Does not synthesize weekend/holiday quotes.
    """
    def __init__(self, policy: Policy):
        self.policy = policy
        self.balance = float(policy.initial_balance)
        self.equity = self.balance
        self.peak_equity = self.balance
        self.max_equity_drawdown = 0.0
        self.position: Position | None = None
        self.current_day = None
        self.daily_reference = self.balance
        self.soft_locked = False
        self.hard_locked = False
        self.terminated = False
        self.terminal_at = None
        self.first_daily_soft = None
        self.first_daily_hard = None
        self.trades = 0
        self.wins = 0
        self.gross_profit = 0.0
        self.gross_loss = 0.0
        self.closed_for_risk = 0
        self.last_quote: tuple[datetime,float,float] | None = None
        self.last_block_reason = None

    def _risk_day(self, timestamp: datetime):
        z=timestamp.astimezone(ZoneInfo(self.policy.timezone))
        return (z-timedelta(hours=17)).date()

    @staticmethod
    def _check_timestamp(timestamp: datetime):
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise PolicyViolation("Ticks must have timezone-aware timestamps")

    def _validate_quote(self, timestamp: datetime, bid: float, ask: float):
        self._check_timestamp(timestamp)
        if not(math.isfinite(bid) and math.isfinite(ask) and bid>0 and ask>=bid):
            raise PolicyViolation("Invalid Bid/Ask quote")
        if self.last_quote and timestamp < self.last_quote[0]:
            raise PolicyViolation("Non-monotonic tick timestamp")
        self.last_quote=(timestamp,bid,ask)

    def _mark_equity(self, bid: float, ask: float):
        if self.position is None:
            self.equity=self.balance
        else:
            oz=self.position.lots*self.policy.contract_oz
            change=((bid-self.position.entry) if self.position.side==1 else (self.position.entry-ask))*oz
            self.equity=self.balance+change
        self.peak_equity=max(self.peak_equity,self.equity)
        self.max_equity_drawdown=max(self.max_equity_drawdown,self.peak_equity-self.equity)

    def _daily_reset(self, timestamp: datetime):
        d=self._risk_day(timestamp)
        if d != self.current_day:
            self.current_day=d
            self.daily_reference=max(self.balance, self.equity)
            self.soft_locked=False
            self.hard_locked=False

    def close_position(self, timestamp: datetime, bid: float, ask: float, risk_close=False):
        self._validate_quote(timestamp,bid,ask)
        if self.position is None:
            raise PolicyViolation("No position to close")
        pos=self.position
        oz=pos.lots*self.policy.contract_oz
        exit_price=bid if pos.side==1 else ask
        gross_move=(exit_price-pos.entry)*oz*pos.side
        realized=gross_move-2*self.policy.fee_side
        # Opening-side commission already debited on entry; debit exit-side only.
        self.balance+=gross_move-self.policy.fee_side
        self.position=None
        self.trades+=1
        if realized>0:
            self.wins+=1
            self.gross_profit+=realized
        else:
            self.gross_loss+=realized
        if risk_close:self.closed_for_risk+=1
        self._mark_equity(bid,ask)
        return realized

    def on_tick(self, timestamp: datetime, bid: float, ask: float) -> TickResult:
        self._validate_quote(timestamp,bid,ask)
        self._mark_equity(bid,ask)
        self._daily_reset(timestamp)
        if self.terminated:
            return self._result(False,"OVERALL_TERMINATED")
        if self.equity <= self.daily_reference-self.policy.soft_usd and not self.soft_locked:
            self.soft_locked=True
            self.first_daily_soft=self.first_daily_soft or timestamp
        if self.equity <= self.daily_reference-self.policy.hard_usd and not self.hard_locked:
            self.hard_locked=True
            self.first_daily_hard=self.first_daily_hard or timestamp
        overall=self.equity<=self.policy.overall_floor_usd
        hard=self.hard_locked
        close=False
        if overall or hard:
            if self.position is not None:
                self.close_position(timestamp,bid,ask,risk_close=True)
                close=True
            if overall or self.equity<=self.policy.overall_floor_usd:
                self.terminated=True
                self.terminal_at=timestamp
        return self._result(close, "OVERALL_TERMINATED" if self.terminated else "DAILY_HARD" if hard else "DAILY_SOFT" if self.soft_locked else None)

    def _result(self,closed: bool,reason: str|None) -> TickResult:
        self.last_block_reason=reason
        return TickResult(self.equity,self.balance,self.daily_reference,self.soft_locked,self.hard_locked,self.terminated,closed,reason)

    def can_enter(self, timestamp: datetime, bid: float, ask: float, side: int, stop: float, lots: float=0.01,
                  additional_adverse_slippage_per_oz: float=0.0, broker_trading_enabled=False,
                  economic_calendar_certified=False, is_high_impact_window=False):
        """Return (allowed,reason). News and real symbol sessions require live provider inputs.

        Absent a point-in-time economic calendar is RESEARCH_NOT_EVALUATED, not a
        declaration that a prop firm news rule is compliant.
        """
        self.on_tick(timestamp,bid,ask)
        if self.terminated:return False,"OVERALL_TERMINATED"
        if self.hard_locked:return False,"DAILY_HARD"
        if self.soft_locked:return False,"DAILY_SOFT"
        if self.position is not None:return False,"ONE_POSITION_MAX"
        if side not in (-1,1):return False,"INVALID_SIDE"
        if lots!=self.policy.fixed_lots:return False,"FIXED_LOT_ONLY"
        if broker_trading_enabled is not True:return False,"BROKER_SESSION_UNAVAILABLE"
        ny=timestamp.astimezone(ZoneInfo(self.policy.timezone))
        minute=ny.hour*60+ny.minute
        # FX week normally resumes on Sunday evening; the broker session flag
        # is still authoritative for specific Coinexx/XAUUSD hours and holidays.
        if ny.weekday()==5 or (ny.weekday()==6 and minute<17*60+5):
            return False,"WEEKEND_OR_SUNDAY_PREOPEN"
        if (16*60+55<=minute<17*60+5) or (ny.weekday()==4 and minute>=16*60+55):
            return False,"ROLLOVER_OR_FRIDAY_CLOSE"
        if economic_calendar_certified and is_high_impact_window:return False,"VERIFIED_HIGH_IMPACT_NEWS_WINDOW"
        # Symbol-stop validity is broker-side separate; enforce source-side expected-risk veto.
        if (side==1 and stop>=bid) or (side==-1 and stop<=ask):return False,"INVALID_PROTECTIVE_STOP"
        spread=ask-bid
        planned= (ask-stop if side==1 else stop-bid)*lots*self.policy.contract_oz
        planned+=2*self.policy.fee_side+additional_adverse_slippage_per_oz*lots*self.policy.contract_oz
        if planned>self.policy.risk_fraction*self.equity:return False,"PLANNED_RISK_LIMIT"
        margin=ask*lots*self.policy.contract_oz/self.policy.margin_leverage
        if self.equity<margin:return False,"INSUFFICIENT_MARGIN_ASSUMPTION"
        return True,"OK_NEWS_NOT_EVALUATED" if not economic_calendar_certified else "OK"

    def enter(self, timestamp: datetime, bid: float, ask: float, side: int, stop: float, lots: float=0.01,
              **kwargs):
        allowed,why=self.can_enter(timestamp,bid,ask,side,stop,lots,**kwargs)
        if not allowed:raise PolicyViolation(why)
        price=ask if side==1 else bid
        self.position=Position(side,price,stop,lots,timestamp)
        self.balance-=self.policy.fee_side
        self._mark_equity(bid,ask)
        # Some extremely wide spread edge cases could immediately breach a limit.
        self.on_tick(timestamp,bid,ask)
        return why

    def audit(self):
        return {
            "policy_id":self.policy.policy_id,"balance_usd":round(self.balance,4),
            "equity_usd":round(self.equity,4),"peak_equity_usd":round(self.peak_equity,4),
            "max_equity_drawdown_usd":round(self.max_equity_drawdown,4),
            "trades":self.trades,"wins":self.wins,"gross_profit_usd":round(self.gross_profit,4),
            "gross_loss_usd":round(self.gross_loss,4),
            "net_pnl_usd":round(self.gross_profit+self.gross_loss,4),
            "soft_locked":self.soft_locked,"hard_locked":self.hard_locked,
            "terminated":self.terminated,"terminal_at_utc":self.terminal_at.isoformat() if self.terminal_at else None,
            "news_filter_evidence":"NOT_EVALUATED_WITHOUT_VERIFIED_CALENDAR"
        }


if __name__=="__main__":
    p=Policy.from_json(Path(__file__).with_suffix(".json"))
    print(json.dumps({"verified_policy_id":p.policy_id,"initial":p.initial_balance,
                      "fixed_lots":p.fixed_lots,"soft":p.soft_usd,"hard":p.hard_usd,
                      "overall_floor":p.overall_floor_usd,"news":p.news_status},indent=2))