"""Pinned NYSE core-session daily/weekly gate. All runtime timestamps are UTC epoch ms."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import numpy as np
NY=ZoneInfo('America/New_York'); TOKYO=ZoneInfo('Asia/Tokyo'); UTC=timezone.utc
# Official NYSE calendar, retrieved 2026-11-24. Fail closed outside coverage.
HOLIDAYS={date.fromisoformat(s) for s in '''2026-01-01 2026-01-19 2026-02-16 2026-04-03 2026-05-25 2026-06-19 2026-07-03 2026-09-07 2026-11-26 2026-12-25 2027-01-01 2027-01-18 2027-02-15 2027-03-26 2027-05-31 2027-06-18 2027-07-05 2027-09-06 2027-11-25 2027-12-24 2028-01-17 2028-02-21 2028-04-14 2028-05-29 2028-06-19 2028-07-04 2028-09-04 2028-11-23 2028-12-25'''.split()}
EARLY={date.fromisoformat(s) for s in '2026-11-27 2026-12-24 2027-11-26 2028-07-03 2028-11-24'.split()}
def ms(t):return int(t.timestamp()*1000)
@dataclass(frozen=True)
class ClockConfig:
    enabled: bool=True
    mode: str="daily"
    entry_buffer_seconds: int=120
    flatten_buffer_seconds: int=60
    def __post_init__(self):
        if self.mode not in ('daily','weekly'):raise ValueError('mode must be daily or weekly')
        if type(self.enabled) is not bool:raise ValueError('enabled must be bool')
        if type(self.entry_buffer_seconds) is not int or type(self.flatten_buffer_seconds) is not int or not 0<self.flatten_buffer_seconds<self.entry_buffer_seconds<=3600:raise ValueError('require 0 < flatten buffer < entry buffer <=3600')
@dataclass(frozen=True)
class Week:
    monday: date
    open_ms: int
    block_ms: int
    flatten_ms: int
    close_ms: int
    close_date: date

def week(monday,cfg=ClockConfig()):
    if monday.weekday()!=0:raise ValueError('Monday required')
    friday=monday+timedelta(days=4)
    if monday<date(2026,1,1) or friday>date(2028,12,31):raise ValueError('NYSE calendar not covered')
    last=friday
    while last in HOLIDAYS and last>=monday:last-=timedelta(days=1)
    if last<monday:raise ValueError('No NYSE session in week')
    close=ms(datetime.combine(last,time(13 if last in EARLY else 16),NY))
    return Week(monday,ms(datetime.combine(monday,time(9),TOKYO)),close-cfg.entry_buffer_seconds*1000,close-cfg.flatten_buffer_seconds*1000,close,last)

def historical_weeks(cfg):
    # First historical week began in 2025; its final session is Jan 2, 2026.
    m=date(2025,12,29); close=ms(datetime(2026,1,2,16,tzinfo=NY)); out=[Week(m,ms(datetime.combine(m,time(9),TOKYO)),close-cfg.entry_buffer_seconds*1000,close-cfg.flatten_buffer_seconds*1000,close,date(2026,1,2))]
    m+=timedelta(days=7)
    while m+timedelta(days=4)<=date(2028,12,31):out.append(week(m,cfg));m+=timedelta(days=7)
    return out

def daily_windows(cfg=ClockConfig()):
    """One session per NYSE trading date, Tokyo 09:00 to NYSE core close.
    Full NYSE holidays are skipped. NYSE date is also Tokyo opening date.
    Calendar coverage is finite; no implicit trading on unknown dates.
    """
    d=date(2026,1,1);out=[]
    while d<=date(2028,12,31):
        if d.weekday()<5 and d not in HOLIDAYS:
            close=ms(datetime.combine(d,time(13 if d in EARLY else 16),NY))
            out.append(Week(d-timedelta(days=d.weekday()),ms(datetime.combine(d,time(9),TOKYO)),close-cfg.entry_buffer_seconds*1000,close-cfg.flatten_buffer_seconds*1000,close,d))
        d+=timedelta(days=1)
    return out

def calendar_windows(cfg):
    return daily_windows(cfg) if cfg.mode=='daily' else historical_weeks(cfg)

def action(now_ms,owned_position,owned_pending,broker_open,clock_valid,weeks,cfg,overdue_close=False):
    """Pure live adapter contract, called on tick AND timer. No order is sent here.
    Close/cancel requests must be retried until confirmed, including after reopen.
    Caller maintains overdue exposure flag and must not open while close is pending.
    """
    if overdue_close or not clock_valid:return 'FLATTEN' if owned_position or owned_pending else 'BLOCK'
    if not cfg.enabled:return 'TRADE' if broker_open else 'BLOCK'
    w=next((w for w in weeks if w.open_ms<=now_ms<w.close_ms),None)
    if w is None or now_ms>=w.flatten_ms:return 'FLATTEN' if owned_position or owned_pending else 'BLOCK'
    if now_ms>=w.block_ms:return 'DRAIN_CANCEL_PENDING' if owned_pending else 'DRAIN'
    return 'TRADE' if broker_open else 'BLOCK'

def gate_arrays(qms,proposal_ms,e,x,weeks):
    """Evaluate calendar membership at proposal AND fill; clip exits only when timer forces close.
    The first strictly later quote is the historical fill proxy. No retroactive last-quote fill.
    """
    starts=np.array([w.open_ms for w in weeks],np.int64);blocks=np.array([w.block_ms for w in weeks],np.int64);flats=np.array([w.flatten_ms for w in weeks],np.int64);closes=np.array([w.close_ms for w in weeks],np.int64)
    i=np.searchsorted(starts,proposal_ms,side='right')-1; idx=np.maximum(i,0); et=qms[e];allowed=(i>=0)&(proposal_ms<blocks[idx])&(et>=starts[idx])&(et<blocks[idx]);
    force_idx=np.searchsorted(qms,flats[idx],side='right'); forced=allowed&(force_idx<x); new_x=np.where(forced,force_idx,x).astype(np.int32); late=allowed&(qms[new_x]>=closes[idx]); return allowed,new_x,forced,late
