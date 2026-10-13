"""Authoritative research roles and fail-closed UTC / MT5 candle alignment.

R9 SYNTH: aspirational day/week/month WHOLE-PORTFOLIO benchmark.
R9 OVERFIT: historical per-trade entry/hold/exit/profit/drawdown/gross-loss teacher;
             no post-entry teacher values are admissible runtime features.
Dukascopy original ticks: Python research/refinement executable chronology.
Coinexx R9 REAL/SYNTH: independent tester quote/time and historical comparator.
All raw timestamps remain UTC milliseconds. Broker H4/D1 candle phase is NOT
inferred from quote timestamps or from R9 SYNTH hindsight.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

DAY_MS=86_400_000
TIMEFRAMES_MS={
 'TICK': None,'MS250':250,'S1':1000,'S5':5000,'S15':15000,
 'S30':30000,'S45':45000,'M1':60000,'M5':300000,'M7':420000,
 'M15':900000,'M30':1800000,'M45':2700000,'H1':3600000,
 'H4':14400000,'H12':43200000,'D1':DAY_MS,
}
R9_SYNTH_IDEAL_PERIODS=('UTC_DAY','UTC_ISO_WEEK','UTC_MONTH')
R9_SYNTH_OBJECTIVES=('completed_trade_count','net_realized_cash','gross_loss',
                     'max_equity_drawdown','max_balance_drawdown')
R9_OVERFIT_PER_TRADE_TEACHER=('entry','hold','exit','profit','drawdown','gross_loss')
FORBIDDEN_RUNTIME_TEACHER_FIELDS=frozenset((
 'r9_overfit_optimal_entry','r9_overfit_optimal_hold','r9_overfit_optimal_exit',
 'r9_overfit_future_profit','r9_overfit_future_drawdown','r9_overfit_future_gross_loss',
 'future_mfe','future_mae','future_exit','hindsight_best_action'))


def require_runtime_feature_names(names):
    forbidden=set(names)&FORBIDDEN_RUNTIME_TEACHER_FIELDS
    if forbidden:
        raise ValueError('hindsight R9 OVERFIT fields prohibited in execution: '+str(sorted(forbidden)))
    return True


def verify_coinexx_utc_text(time_msc:int,second_text:str,minute_text:str,minute_second:str)->None:
    """Only authentic logged fields from the SAME row. No inferred offset."""
    if type(time_msc) is not int or time_msc<0:
        raise ValueError('Coinexx milliseconds must be UTC-epoch integer')
    d=datetime.fromtimestamp(time_msc/1000,timezone.utc)
    if second_text!=d.strftime('%Y.%m.%d %H:%M:%S'):
        raise ValueError('Coinexx logged time does not match UTC epoch')
    if minute_text!=d.strftime('%Y.%m.%d %H:%M'):
        raise ValueError('Coinexx logged minute does not match UTC epoch')
    if minute_second!=str(d.second):
        raise ValueError('Coinexx minute_second does not match UTC epoch')


@dataclass(frozen=True)
class CandleClock:
    """UTC research default; MT5 chart phase only with directly observed evidence.

    Time-of-day sessions ALWAYS consume actual UTC epoch and IANA local clocks;
    the chart candle phase affects only the start/end of derived bars.
    """
    mode:str='UTC_RESEARCH'
    offset_minutes:int|None=None  # chart/server civil minute versus UTC
    evidence_id:str|None=None  # concrete MT5 chart-bar timestamp verification
    valid_from_ms:int|None=None
    valid_until_ms:int|None=None

    def __post_init__(self):
        if self.mode=='UTC_RESEARCH':
            if any(x is not None for x in (self.offset_minutes,self.evidence_id,
                                             self.valid_from_ms,self.valid_until_ms)):
                raise ValueError('UTC research clock must not inject a broker shift')
        elif self.mode=='MT5_CHART_PARITY':
            if (type(self.offset_minutes) is not int or abs(self.offset_minutes)>14*60
                or not isinstance(self.evidence_id,str) or not self.evidence_id.strip()
                or type(self.valid_from_ms) is not int
                or type(self.valid_until_ms) is not int
                or self.valid_until_ms<=self.valid_from_ms):
                raise ValueError('MT5 chart phase needs independently observed bounded evidence')
        else:
            raise ValueError('unknown candle clock mode')

    def start_ms(self,utc_ms:int,timeframe:str)->int:
        if type(utc_ms) is not int or utc_ms<0:
            raise ValueError('UTC tick timestamp must be exact nonnegative integer')
        if timeframe not in TIMEFRAMES_MS or timeframe=='TICK':
            raise ValueError('unsupported candle timeframe')
        width=TIMEFRAMES_MS[timeframe]
        if self.mode=='MT5_CHART_PARITY' and not self.valid_from_ms<=utc_ms<self.valid_until_ms:
            raise ValueError('MT5 chart candle offset stale/out of evidence window')
        # Civil-day anchor makes unconventional M7/M45 explicit, not Unix-epoch
        # drift across a date boundary. For UTC_RESEARCH this phase is zero.
        shift=(self.offset_minutes or 0)*60_000
        shifted=utc_ms+shift
        start_day=(shifted//DAY_MS)*DAY_MS
        local_start=start_day+((shifted-start_day)//width)*width
        return local_start-shift

    def end_ms(self,utc_ms:int,timeframe:str)->int:
        start=self.start_ms(utc_ms,timeframe)
        width=TIMEFRAMES_MS[timeframe]
        # Even 7m / 45m labels never claim a candle spans beyond local midnight.
        shift=(self.offset_minutes or 0)*60_000
        next_day=((utc_ms+shift)//DAY_MS+1)*DAY_MS-shift
        return min(start+width,next_day)


def utc_partition_labels(utc_ms:int)->dict:
    if type(utc_ms) is not int or utc_ms<0:
        raise ValueError('UTC millisecond timestamp required for benchmarks')
    d=datetime.fromtimestamp(utc_ms/1000,timezone.utc)
    iso=d.isocalendar()
    return {'UTC_DAY':d.date().isoformat(),
            'UTC_ISO_WEEK':f'{iso.year}-W{iso.week:02d}',
            'UTC_MONTH':d.strftime('%Y-%m')}
