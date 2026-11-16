"""V19 shadow-only causal R9 minute-cycle policy for micro180 research.

The immutable R9 v1.90 source-faithful Python state machine drives entries,
stops, timeouts and opposite-side rearm. A completed-M5-ATR-based trailing
choice is frozen AT ENTRY. The source-order interface never sends orders.
"""
from __future__ import annotations
from dataclasses import dataclass,replace
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
SOURCE_DIR=HERE/'src' if (HERE/'src').is_dir() else HERE.parent/'src'
if str(SOURCE_DIR) not in sys.path:sys.path.insert(0,str(SOURCE_DIR))
from coinexx_r9.r9_baseline import R9HybridGateBaseline,R9Config


@dataclass(frozen=True,slots=True)
class CycleResearchSettings:
    high_volatility_m5_atr_cents:int=800
    high_volatility_trail_cents:int=25
    standard_trail_cents:int=3
    max_same_minute_rearms:int=1

    def validate(self):
        if self.high_volatility_m5_atr_cents<=0 or not 1<=self.standard_trail_cents<=self.high_volatility_trail_cents:
            raise ValueError("Invalid causal trailing settings")
        if self.max_same_minute_rearms!=1:
            raise ValueError("V19 requires one same-minute rearm, hence two legs maximum")


class R9V19TwoLegCausalTrail(R9HybridGateBaseline):
    """Python-only quote-ordinal policy candidate, not MT5 or broker-certified."""
    def __init__(self,settings:CycleResearchSettings|None=None):
        self.research=settings or CycleResearchSettings()
        self.research.validate()
        super().__init__(R9Config(max_same_minute_rearms=self.research.max_same_minute_rearms,
                                  trail_pips=self.research.standard_trail_cents))
        self._base_cfg=self.cfg
        self._hi_cfg=replace(self.cfg,trail_pips=self.research.high_volatility_trail_cents)
        self.active_trail=self.cfg.trail_pips
        self.entry_trail_receipts=[]

    def _open_trade(self,t,side):
        pre=len(self.entries)
        atr=self.atr.atr_u
        trail=(self.research.high_volatility_trail_cents if atr is not None and
               atr>=self.research.high_volatility_m5_atr_cents else
               self.research.standard_trail_cents)
        super()._open_trade(t,side)
        if len(self.entries)>pre:
            self.active_trail=trail
            self.entry_trail_receipts.append((t.ordinal,t.time_msc,side,self.rearms,
                None if atr is None else round(atr,4),trail))

    def _manage_position(self,t):
        fixed=self.cfg
        try:
            self.cfg=(self._hi_cfg if self.active_trail==self.research.high_volatility_trail_cents
                      else self._base_cfg)
            super()._manage_position(t)
        finally:
            self.cfg=fixed


class R9Micro180CycleShadow:
    """Observe original Coinexx quote order alongside V9; NEVER route trades.

    The caller supplies already-known micro180 state. Same-symbol inventory
    collisions are diagnosed, not traded or used to override the frozen EA.
    """
    def __init__(self,settings:CycleResearchSettings|None=None):
        self.policy=R9V19TwoLegCausalTrail(settings)
        self.previous_ordinal=None
        self.observations=0
        self.candidate_collision_quotes=0
        self.micro180_intents=0

    def observe(self,t,*,micro180_open=False,micro180_entry_side=0):
        if self.previous_ordinal is not None and t.ordinal<=self.previous_ordinal:
            raise ValueError("Tick source ordinals reordered or duplicated")
        self.previous_ordinal=t.ordinal
        self.policy.on_tick(t)
        self.observations+=1
        if micro180_entry_side not in (-1,0,1):
            raise ValueError("Invalid micro180 entry side")
        if micro180_entry_side:self.micro180_intents+=1
        collision=bool(self.policy.position is not None and (micro180_open or micro180_entry_side))
        self.candidate_collision_quotes+=int(collision)
        return {
            "research_only":True,"candidate_cycle_minute":self.policy.cycle_minute,
            "candidate_position_side":0 if self.policy.position is None else self.policy.position.side,
            "candidate_rearms":self.policy.rearms,
            "candidate_locked_trail_cents":self.policy.active_trail,
            "micro180_entry_side":micro180_entry_side,
            "same_symbol_inventory_collision":collision,
            "modify_live_orders":False,"override_micro180_orders":False
        }
