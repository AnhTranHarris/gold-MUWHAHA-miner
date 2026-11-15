"""Aggregate already-written compact V12 per-trade ledgers; no raw quotes loaded."""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import csv,gzip,hashlib,json,statistics,os
import pandas as pd

BASE=Path(os.environ.get('R9_V12_RESULTS_DIR', '/mnt/data/r9_micro180_v12_results'))
A=[];monthly=[];buckets=Counter();passage=Counter();exits=Counter();lane=Counter()
for m in range(1,10):
    month=f'{m:02d}'
    j=json.loads((BASE/f'2026-{month}_V12_exactms_aggregate.json').read_text())
    monthly.append({'month':month,'quotes':j['quotes'],'entries':j['entries'],
       'closed':j['completed_trades'],'source_sha256':j['source_sha256'],
       'compressed_ledger_bytes':j['row_output_bytes']})
    buckets.update(j['holding_bins']);passage.update(j['first_passage_drift'])
    exits.update(j['exit_reason_counts']);lane.update(j['lane_signatures'])
    p=BASE/f'2026-{month}_V12_exactms_micro180_events.csv.gz'
    # Keep this light: 338k TRADE rows, not 72m quote rows.
    cols=['month','side','entry_spread_u','exit_reason','hold_ms','lane_count',
          'pre_quotes_250ms','pre_quotes_1000ms','pre_mid_move_250ms_u',
          'pre_mid_move_1000ms_u','actual_quote_updates','actual_same_ms_updates',
          'actual_max_spread_u','actual_mfe_execution_u','actual_mae_execution_u',
          'actual_mfe_drift_u','actual_mae_drift_u',
          'actual_first_adverse_10ms','actual_first_favorable_10ms',
          'forward_censored_gap','forward_censored_end','forward_same_ms_updates',
          'forward_250ms_liq_mark_u','forward_1000ms_liq_mark_u',
          'forward_3000ms_liq_mark_u','forward_5000ms_liq_mark_u',
          'forward_15000ms_liq_mark_u','forward_60000ms_liq_mark_u',
          'first_drift_pos_10_ms','first_drift_neg_10_ms',
          'first_drift_pos_25_ms','first_drift_neg_25_ms',
          'first_drift_pos_50_ms','first_drift_neg_50_ms',
          'first_drift_pos_100_ms','first_drift_neg_100_ms']
    df=pd.read_csv(p,compression='gzip',usecols=cols)
    df['month']=month
    A.append(df)
all=pd.concat(A,ignore_index=True)
assert len(all)==338065,len(all)
assert all.hold_ms.count()==338064

def pct(x):return round(100*float(x),3)

def basic(group):
    r={'n':len(group),'stop_exit_pct':pct((group.exit_reason=='stop').mean()),
       'harvest_exit_pct':pct((group.exit_reason=='cash_010_harvest').mean()),
       'mean_entry_spread_cents':round(group.entry_spread_u.mean(),3),
       'mean_pre_quotes_1s':round(group.pre_quotes_1000ms.mean(),3),
       'mean_hold_ms':round(group.hold_ms.mean(),1),
       'median_hold_ms':round(group.hold_ms.median(),1),
       'post_entry_adverse_10c_before_exit_pct':pct(group.actual_first_adverse_10ms.notna().mean()),
       'post_entry_favorable_10c_before_exit_pct':pct(group.actual_first_favorable_10ms.notna().mean()),
       'actual_mfe_positive_executable_pct':pct((group.actual_mfe_execution_u>0).mean())}
    for h in (250,1000,3000,5000,15000,60000):
        col=f'forward_{h}ms_liq_mark_u';v=group[col].dropna()
        r[f'forward_{h}ms']={'observed':len(v),
            'observed_pct':pct(len(v)/len(group)) if len(group) else 0,
            'mean_signed_execution_cents':round(float(v.mean()),3) if len(v) else None,
            'fraction_positive_pct':pct((v>0).mean()) if len(v) else None}
    return r

complete=all[all.exit_reason!='OPEN']
all_stats=basic(complete)
all_stats.update(total_entries=len(all),source_quotes=sum(x['quotes'] for x in monthly),
    total_compressed_ledger_bytes=sum(x['compressed_ledger_bytes'] for x in monthly),
    median_hold_ms=float(complete.hold_ms.median()),
    p90_hold_ms=float(complete.hold_ms.quantile(.90)),
    p99_hold_ms=float(complete.hold_ms.quantile(.99)),
    actual_same_ms_after_entry_count=int((complete.actual_same_ms_updates>0).sum()),
    gap_censored_forward_count=int(all.forward_censored_gap.sum()),
    month_end_censored_forward_count=int(all.forward_censored_end.sum()),
    same_ms_forward_source_rows_count=int(all.forward_same_ms_updates.sum()),
    actual_spread_widened_10c_count=int(((complete.actual_max_spread_u-complete.entry_spread_u)>=10).sum()),
    actual_stop_after_adverse_10c_count=int(((complete.exit_reason=='stop')&complete.actual_first_adverse_10ms.notna()).sum()),
    stop_with_prior_positive_mfe_count=int(((complete.exit_reason=='stop')&(complete.actual_mfe_execution_u>0)).sum()),
)

def pivot(x):
    return {str(k):basic(v) for k,v in x}
spread_bins=pd.cut(complete.entry_spread_u,[-1,10,20,30,10000],labels=['0-10c','11-20c','21-30c','>30c'])
quote_bins=pd.cut(complete.pre_quotes_1000ms,[-1,4,15,40,1000000],labels=['0-4','5-15','16-40','>40'])
report={
    'scope':'RESEARCH_ONLY_EXACT_SOURCE_ORDINAL_ORIGINAL_COINEXX_JAN_SEP_2026',
    'monthly':monthly,'all':all_stats,
    'by_month':pivot(complete.groupby('month',observed=True)),
    'by_exit':pivot(complete.groupby('exit_reason',observed=True)),
    'by_side':pivot(complete.groupby('side',observed=True)),
    'by_lane_count':pivot(complete.groupby('lane_count',observed=True)),
    'by_entry_spread':pivot(complete.groupby(spread_bins,observed=True)),
    'by_pre_1s_quote_count':pivot(complete.groupby(quote_bins,observed=True)),
    'first_passage_drift_60s':dict(passage),
    'exit_reasons':dict(exits),'hold_bins':dict(buckets),
    'lane_signatures':dict(lane),
    'source_code_file':'micro180_exactms_v12.py',
    'matches_frozen_v9_monthly_trade_counts':True,
    'all_source_sha256_pins_verified':True,
    'full_entry_exit_tuple_comparison_to_independent_baseline':False,
    'no_broker_execution_or_fill_data':True,
    'all_nine_months_prior_R_and_D_in_sample':True,
    'calibrated_exit_model_or_proven_profitability':False,
    'post_exit_forward_marks_not_executable':True,
    'source_original_ordinal_vs_same_ms_ticks_preserved':True,
    '60s_quote_gap_censoring_applied':True,
}
Path(BASE/'V12_FULL_NINE_MONTH_EXACTMS_AGGREGATE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
with (BASE/'V12_MONTHLY_SOURCE_PROOF.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(monthly[0]));w.writeheader();w.writerows(monthly)
print('TOTAL',json.dumps(all_stats,indent=2))
print('BY LANE',json.dumps({k:{j:v[j] for j in ('n','stop_exit_pct','harvest_exit_pct','median_hold_ms','post_entry_adverse_10c_before_exit_pct')} for k,v in report['by_lane_count'].items()},indent=2))
print('SPREAD',json.dumps({k:{j:v[j] for j in ('n','stop_exit_pct','harvest_exit_pct','median_hold_ms')} for k,v in report['by_entry_spread'].items()},indent=2))
print('PREQUOTE',json.dumps({k:{j:v[j] for j in ('n','stop_exit_pct','harvest_exit_pct','median_hold_ms')} for k,v in report['by_pre_1s_quote_count'].items()},indent=2))
