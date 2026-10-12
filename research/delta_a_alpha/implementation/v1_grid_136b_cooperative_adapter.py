"""Add ORIGINAL 136B session G0 to EXISTING MultiSpeedGridGenesis; no new EA.

Original 48-H1/M5/S1/M1 generator keeps first priority. The historical
hourly HIGHVOL and 23:00 Asia virtual campaigns fill ONLY otherwise-empty
source quotes. Shared L1-L7 quality and funding remain unchanged.
"""
from __future__ import annotations
from v1_grid_multiscale_stack import MultiSpeedGridGenesis
from v1_original_136b_hourly_grid import Original136BHourlyGrid
from v1_native_136a_minute_grid import Native136AMinuteGrid


class CooperativeGridGenesis:
    def __init__(self, *, original_stack=None, hourly=None, native=None):
        self.original_stack = original_stack or MultiSpeedGridGenesis()
        self.hourly = hourly or Original136BHourlyGrid()
        self.native = native or Native136AMinuteGrid()
        self.native_handoffs = 0
        self.native_priority_collisions = 0
        self.original_handoffs = 0
        self.hourly_handoffs = 0
        self.priority_collisions = 0

    @property
    def ready(self):
        return self.original_stack.ready

    def on_tick(self, tick, last_completed_h1, session_geometry: str,
                *, last_completed_m5=None, last_completed_h4=None, broker_tradable: bool = True):
        original = self.original_stack.on_tick(
            tick, last_completed_h1, session_geometry,
            last_completed_m5=last_completed_m5,
            broker_tradable=broker_tradable)
        parent = self.original_stack.parent.parent
        hourly = self.hourly.on_tick(
            tick, ready=self.ready, broker_tradable=broker_tradable,
            rolling_high=getattr(parent, 'cached_high', None),
            rolling_low=getattr(parent, 'cached_low', None),
            geometry=session_geometry)
        native = self.native.on_tick(
            tick,last_completed_h4,last_completed_h1,session_geometry,
            broker_tradable=broker_tradable)
        if original:
            self.original_handoffs += 1
            if hourly:self.priority_collisions += 1
            if native:self.native_priority_collisions += 1
            return original[:1]
        if hourly:
            self.hourly_handoffs += 1
            if native:self.native_priority_collisions += 1
            return hourly[:1]
        if native:self.native_handoffs += 1
        return native[:1]

    def stats(self):
        return {'cooperative_g0_original_handoffs': self.original_handoffs,
                'cooperative_g0_hourly_handoffs': self.hourly_handoffs,
                'cooperative_g0_priority_collisions': self.priority_collisions,
                'original_multispeed': self.original_stack.stats(),
                'hourly_136b': self.hourly.stats(),
                'native_136a_handoffs':self.native_handoffs,
                'native_136a_priority_collisions':self.native_priority_collisions,
                'native_136a':self.native.stats()}
