"""Research R12: opt-in shared-account deferred-profit runner geometry.

Standalone R12 native-tick optimization found paired profit/DD improvement
against its matched fixed-exit control, across both independent broker tapes.
This module ports only *intended* order geometry to official Replay. It is NOT
tick-parity-certified to the standalone simulator. All user owner risk settings
must be explicitly supplied in the CLI; no live order is sent.
"""
from __future__ import annotations
from dataclasses import replace
from .economic_exit import ExitProfile
from .signal_bus import SignalIntent

STOP_DISTANCE_PRICE = 1.8
TARGET_DISTANCE_PRICE = 5.0

def deferred_runner_profile() -> ExitProfile:
    # Activation must be supported by a large favorable quote move.
    # The stop amendment itself remains latency-delayed in Replay.
    return ExitProfile(max_hold_ms=60000,
                       min_locked_net_usd=0.20,
                       activate_net_usd=2.10,
                       trail_floor_price=1.30,
                       atr_trail_fraction=0.0)

class R12RunnerGeometry:
    """Change initial execution geometry for an existing source, never history.

    This deliberately doesn't change trade direction, confidence, observation
    timestamp, specialist, priority or position size. The central arbiter still
    applies the one-position margin and research-only risk controls.
    """
    def __init__(self, source):
        self.source=source

    @staticmethod
    def _adapt(intents):
        out=[]
        for event in intents or ():
            if not isinstance(event,SignalIntent):
                raise TypeError("only SignalIntent may be adapted")
            if event.kind=="entry":
                event=replace(event,stop_distance=STOP_DISTANCE_PRICE,
                              target_distance=TARGET_DISTANCE_PRICE)
            out.append(event)
        return tuple(out)

    def on_bar(self,bar,quote,account):
        return self._adapt(self.source.on_bar(bar,quote,account))

    def on_tick(self,quote,account):
        return self._adapt(self.source.on_tick(quote,account))
