"""Owner clean V1 L0/L1: UTC-authoritative tick source and broker server offset.
The market-desk clocks never use the broker clock as their calendar source.
No historical broker offset inference from MT5 tester TimeGMT/TimeTradeServer.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import median
from zoneinfo import ZoneInfo

UTC=timezone.utc
ZONES={"SYDNEY":"Australia/Sydney","TOKYO":"Asia/Tokyo",
       "LONDON":"Europe/London","NEW_YORK":"America/New_York"}

@dataclass(frozen=True)
class BrokerSync:
    offset_seconds: int
    sample_utc_ms: int
    samples: int
    confidence: str

class ClockNotCalibrated(RuntimeError): pass

class BrokerClock:
    """Conservative server-time converter (date+time), not a trading signal.

    Only accepts paired *simultaneous* server wall datetime (naive in the
    broker's stated clock) with an independently trustworthy UTC capture.
    Samples require a declared <=250ms uncertainty; rounded to one minute,
    and must have corroborating observations within 30 seconds of one another.
    A DST offset jump never carries forward without fresh stable samples.
    """
    def __init__(self, *, require_samples=3, max_age_ms=300_000):
        self.require_samples=require_samples
        self.max_age_ms=max_age_ms
        self.samples=[]
        self.state=None
    def observe(self,server_wall:datetime, trusted_utc:datetime,uncertainty_ms=250):
        if server_wall.tzinfo is not None or trusted_utc.tzinfo is None:
            raise ValueError("paired naive broker wall and aware UTC required")
        if uncertainty_ms>250 or uncertainty_ms<0:raise ClockNotCalibrated("untrusted observation")
        utc=trusted_utc.astimezone(UTC)
        # The datetime deltas are between UTC civil face values, not epoch
        delta=(server_wall-utc.replace(tzinfo=None)).total_seconds()
        candidate=int(round(delta/60)*60)
        if abs(delta-candidate)>1.0:raise ClockNotCalibrated("ambiguous server offset")
        stamp=int(utc.timestamp()*1000)
        if self.samples and stamp<self.samples[-1][0]:raise ClockNotCalibrated("unsequenced clock probe")
        if self.state and candidate!=self.state.offset_seconds:
            # Never silently re-use stale mapping across a DST/server shift.
            self.state=None
            self.samples=[]
        self.samples.append((stamp,candidate))
        self.samples=self.samples[-self.require_samples:]
        if len(self.samples)>=self.require_samples and len(set(c for _,c in self.samples))==1 and (self.samples[-1][0]-self.samples[0][0])<=60_000:
            self.state=BrokerSync(candidate,stamp,len(self.samples),"PAIRED_LIVE_UTC")
        return self.state
    def as_utc(self,server_wall:datetime, observed_at_utc:datetime)->datetime:
        if not self.state:raise ClockNotCalibrated("not enough aligned broker observations")
        if server_wall.tzinfo is not None or observed_at_utc.tzinfo is None:raise ValueError("clock inputs")
        stamp=int(observed_at_utc.astimezone(UTC).timestamp()*1000)
        if not 0<=stamp-self.state.sample_utc_ms<=self.max_age_ms:
            raise ClockNotCalibrated("stale broker calibration")
        converted=(server_wall-timedelta(seconds=self.state.offset_seconds)).replace(tzinfo=UTC)
        if abs((converted-observed_at_utc.astimezone(UTC)).total_seconds())>2:
            raise ClockNotCalibrated("broker quote/UTC divergence")
        return converted


def local_clocks(timestamp_ms_utc:int)->dict:
    utc=datetime.fromtimestamp(timestamp_ms_utc/1000,tz=UTC)
    return {name:utc.astimezone(ZoneInfo(zone)) for name,zone in ZONES.items()}


def server_wall_quote_to_utc_ms(calibrator:BrokerClock,server_wall:datetime,
                                trusted_utc_capture:datetime)->int:
    """Only for sources delivering broker-local wall dates, not MT5 time_msc.

    On no calibration or a 1h DST/offset error this raises, never falling back
    to the machine PC clock or guessing broker timezone from XAUUSD source.
    """
    dt=calibrator.as_utc(server_wall,trusted_utc_capture)
    return int(dt.timestamp()*1000)

def mt5_tick_utc_ms(time_msc:int)->int:
    """MetaTrader5 Python tick time_msc is UTC epoch ms: no double shift."""
    if not isinstance(time_msc,int) or time_msc<0:
        raise ValueError("invalid MT5 tick timestamp")
    return time_msc
