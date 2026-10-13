"""GRID0259: R9-synth-target / R9-overfit-TEACHER daily/hourly grid scorekeeper.

Source entry/exit ledgers are after-friction one-ounce USD/oz *quote model*
NOT equivalent to MT5 broker cash. Never convert to broker USD without
explicit account contract, fees, exchange and audited execution fills.

Time-domain anti-leakage: R9 tester trade-close DAY is MT5 SERVER local;
Dukascopy source is UTC. Cross-feed same-day comparisons REQUIRE confirmed
fixed server UTC offset (and tested DST validity); otherwise report only
separate clock-native series; MONTH/WEEK are likewise not automatically matched.

Outputs time-bucket diagnostics, R9 target ledger and an unpromoted audit.
No orders, balance mutations, month-aware trade routing, or August access.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import pandas as pd
import numpy as np

SOURCE_COLUMNS=('entry','exit','direction','net','cohort')
@dataclass(frozen=True)
class ClockCertification:
    server_utc_offset_minutes: int
    mt5_server_clock_tested: bool
    coverage_jan_jul_confirmed: bool

    def approved(self)->bool:
        return self.mt5_server_clock_tested and self.coverage_jan_jul_confirmed


def check_source_ledger(source:pd.DataFrame)->pd.DataFrame:
    missing=set(SOURCE_COLUMNS)-set(source.columns)
    if missing:raise ValueError(f'missing required original source columns {sorted(missing)}')
    d=source.copy()
    if d.empty:raise ValueError('no completed source trades')
    for x in ('entry','exit','direction','net'):
        if pd.to_numeric(d[x],errors='coerce').isna().any():raise ValueError(f'non-numeric {x}')
    if (d['exit']<d['entry']).any():raise ValueError('exit timestamp precedes entry')
    if (~d.direction.isin([-1,1])).any():raise ValueError('unsupported grid trade side')
    if d[['entry','exit','direction','net','cohort']].isna().any().any():raise ValueError('missing trade facts')
    return d


def summarize_source(source:pd.DataFrame,*,level:str,clock:Optional[ClockCertification]=None)->pd.DataFrame:
    d=check_source_ledger(source)
    time=pd.to_datetime(d['exit'],unit='ms',utc=True)
    if clock is not None:
        if not clock.approved():raise ValueError('uncertified MT5 server clock mapping')
        time=time+pd.to_timedelta(clock.server_utc_offset_minutes,unit='m')
    fmt={'hour':'%Y-%m-%dT%H','day':'%Y-%m-%d','week':'%G-W%V','month':'%Y-%m'}
    if level not in fmt:raise ValueError(f'bad period {level}')
    d['period']=time.dt.strftime(fmt[level])
    d['plus']=np.where(d.net>0,d.net,0.)
    d['minus']=np.where(d.net<0,d.net,0.)
    d['hold_ms']=d.exit-d.entry
    out=d.groupby('period',sort=True).agg(
        completed=('net','size'),net_quote_usd_oz=('net','sum'),
        gross_profit_quote_usd_oz=('plus','sum'),gross_loss_quote_usd_oz=('minus','sum'),
        winning_trades=('plus',lambda x:(x>0).sum()),
        median_hold_ms=('hold_ms','median'),
        mean_hold_ms=('hold_ms','mean'),
        p90_hold_ms=('hold_ms',lambda x:float(np.percentile(x,90))),
        distinct_source_families=('cohort','nunique')
    ).reset_index()
    out['net_positive']=out.net_quote_usd_oz>0
    out['time_domain']='MT5_SERVER_FIXED_OFFSET_VERIFIED' if clock is not None else 'ORIGINAL_UTC_SOURCE'
    out['is_broker_cash']=False
    return out


def benchmark_r9_daily(r9:pd.DataFrame)->pd.DataFrame:
    must={'mt5_server_day','closed_positions','net_usd','gross_profit_usd','gross_loss_usd'}
    if not must.issubset(r9):raise ValueError(f'R9 daily ledger missing {sorted(must-set(r9.columns))}')
    if r9.mt5_server_day.duplicated().any():raise ValueError('duplicate R9 MT5 server day')
    out=r9.copy()
    out['target_net_r9_100pct_usd']=out['net_usd']
    out['target_trades_r9_100pct']=out['closed_positions']
    out['target_net_r9_50pct_usd']=out['net_usd']*.5
    out['target_trades_r9_50pct']=np.ceil(out.closed_positions*.5).astype(int)
    out['clock_domain']='MT5_SERVER_UNCALIBRATED'
    return out


def daily_r9_comparison(source:pd.DataFrame,r9:pd.DataFrame,*,clock:ClockCertification)->pd.DataFrame:
    if not clock.approved():raise ValueError('explicit owner-verified MT5/Duka clock required')
    s=summarize_source(source,level='day',clock=clock)
    ref=benchmark_r9_daily(r9)
    out=ref.merge(s,left_on='mt5_server_day',right_on='period',how='left',validate='one_to_one')
    out['completed']=out.completed.fillna(0).astype(int)
    out['net_quote_usd_oz']=out.net_quote_usd_oz.fillna(0.)
    out['quote_net_positive']=out.net_quote_usd_oz>0
    # No invented conversion of quote PnL into MT5 account cash.
    out['broker_net_parity_certified']=False
    out['trade_volume_fraction_vs_r9']=out.completed/out.closed_positions
    return out


def audit_report(source:pd.DataFrame,r9:pd.DataFrame)->dict:
    s=check_source_ledger(source)
    measures={x:summarize_source(s,level=x) for x in ['hour','day','week','month']}
    a={}
    for kind,df in measures.items():
        a[kind]={'represented_periods':int(len(df)),
                 'profitable_periods':int(df.net_positive.sum()),
                 'total_completed_source_closes':int(df.completed.sum()),
                 'max_completed_per_period':int(df.completed.max()),
                 'median_completed_per_period':float(df.completed.median()),
                 'source_quote_net_usd_oz':float(df.net_quote_usd_oz.sum())}
    ref=benchmark_r9_daily(r9)
    return {'source':'GRID0258 ORIGINAL QUOTE CLOSED SIMULATIONS',
            'r9_source':'R9_SYNTH MT5 SERVER closed positions',
            'objective':'R9_SYNTH 100pct daily net and trading volume; R9_OVERFIT is offline optimal cycle teacher',
            'clock_comparison_status':'UNMAPPED: MT5 server-day timezone offset has not been confirmed',
            'cross_feed_net_cash_comparable':False,
            'source_quote_usd_per_oz_not_broker_cash':True,
            'source_trade_count':int(len(s)),
            'source_gross_profit_usd_per_oz':round(float(s.loc[s.net>0,'net'].sum()),3),
            'source_gross_loss_usd_per_oz':round(float(s.loc[s.net<0,'net'].sum()),3),
            'r9_complete_positions':int(ref.closed_positions.sum()),
            'r9_net_broker_tester_usd':round(float(ref.net_usd.sum()),2),
            'r9_server_trading_days':int(len(ref)),
            'source_trade_volume_fraction_vs_r9':float(len(s)/ref.closed_positions.sum()),
            'source_utc_time_buckets':a,
            'not_promoted':True}
