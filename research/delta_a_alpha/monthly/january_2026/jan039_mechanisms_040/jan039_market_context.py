"""Causal-candidate feature extraction from ordered Dukascopy Bid/Ask.

Export end-of-bucket descriptors for later month-blind correlation. The completed
10-minute bucket is not available for decisions inside that same 10-minute bucket.
No label-derived threshold or January-specific decision is selected here.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd


def fingerprint(ticks_csv_gz: Path, output_json: Path):
    parts = []
    columns = {'timestamp_ms_utc': 'int64', 'ask_raw': 'int64', 'bid_raw': 'int64'}
    for df in pd.read_csv(ticks_csv_gz, compression='gzip', usecols=list(columns),
                          dtype=columns, chunksize=500_000):
        mid = (df['ask_raw'].to_numpy() + df['bid_raw'].to_numpy()) / 2000.0
        spread = (df['ask_raw'].to_numpy() - df['bid_raw'].to_numpy()) / 1000.0
        bucket = df['timestamp_ms_utc'].to_numpy() // 600_000
        temp = pd.DataFrame({'bucket': bucket, 'mid': mid, 'spread': spread})
        p = temp.groupby('bucket', sort=True).agg(
            n=('mid','size'), first=('mid','first'), last=('mid','last'),
            high=('mid','max'), low=('mid','min'), spread_sum=('spread','sum'),
            spread_high=('spread','max'))
        parts.append(p.reset_index())
    grouped = pd.concat(parts, ignore_index=True).groupby('bucket',sort=True).agg(
        n=('n','sum'), first=('first','first'), last=('last','last'),
        high=('high','max'), low=('low','min'), spread_sum=('spread_sum','sum'),
        spread_high=('spread_high','max'))
    grouped['range_usd'] = grouped.high - grouped.low
    grouped['directional_change_usd'] = grouped['last'] - grouped['first']
    grouped['mean_spread_usd'] = grouped.spread_sum / grouped.n
    grouped['tick_rate_per_second'] = grouped.n / 600.0
    t_end_ms = (grouped.index.to_numpy() + 1) * 600_000
    # Timestamp = right edge of FULLY CLOSED bucket. Startup pre-T0 still needed.
    dates = pd.to_datetime(t_end_ms-1,unit='ms',utc=True).strftime('%Y-%m-%d')
    grouped['end_ms'] = t_end_ms
    grouped['date_utc_EVALUATION_ONLY'] = dates
    jan30 = grouped[grouped.date_utc_EVALUATION_ONLY == '2026-01-30']
    other = grouped[grouped.date_utc_EVALUATION_ONLY != '2026-01-30']
    fields = ['n','range_usd','mean_spread_usd','spread_high','tick_rate_per_second']
    def desc(subset):
        return {key:{'median':round(float(subset[key].median()),6),
                     'p90':round(float(subset[key].quantile(.90)),6),
                     'max':round(float(subset[key].max()),6)} for key in fields}
    out={'source':'January raw Dukascopy XAUUSD ordered Bid/Ask',
         'classification':'RETROSPECTIVE_DESCRIPTIVE_ONLY_NO_JAN_MONTH_SIGNAL',
         'complete_10m_buckets':len(grouped),
         'raw_ticks':int(grouped.n.sum()),
         'january_30_descriptive_only':desc(jan30),
         'other_january_dates_descriptive_only':desc(other),
         'feature_contract':{
              'usable_at_ms':'bucket_end_ms, never before',
              'cross_month_adaptation':'requires independently validated mapping from completed HTF/session/quote and funded state',
              'H4_H1_M15_M5':'must be independently completed pre-decision',
              'date':'never a live feature',
         }}
    output_json.write_text(json.dumps(out,indent=2,sort_keys=True))
    grouped[['end_ms','n','range_usd','directional_change_usd',
             'mean_spread_usd','spread_high','tick_rate_per_second']].to_csv(
             output_json.with_suffix('.csv'), index=False)
    print(json.dumps({'raw_ticks':out['raw_ticks'], 'complete_10m_buckets':out['complete_10m_buckets'],
                      'jan30_median_range':out['january_30_descriptive_only']['range_usd']['median'],
                      'other_median_range':out['other_january_dates_descriptive_only']['range_usd']['median']}))
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('ticks_csv_gz',type=Path)
    ap.add_argument('output_json',type=Path)
    a=ap.parse_args()
    fingerprint(a.ticks_csv_gz,a.output_json)