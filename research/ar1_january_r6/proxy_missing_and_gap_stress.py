#!/usr/bin/env python3
"""JAN AR1-R6 proxy fallback research, strictly earlier observed Coinexx windows only.

Missing quotes remain unknown; this creates a *distributional* historical proxy, never
fictitious ticks, MFE, MAE, trade exits or account profit. A deterministic 1-in-41
masked-known-trade validation view tests quantitative reliability of the proxy.
"""
from pathlib import Path
import json,zipfile,gzip,math
import numpy as np,pandas as pd
O=Path('/mnt/data/AR1_JAN_R6_ACCOUNT_RISK_INTEGRATED_20261118')
R5=Path('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118')
R1=Path('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
D=pd.read_csv(O/'JAN_R6_ALL_27980_INTEGRATED_ACCOUNT_RISK_OBSERVER.csv.gz')
assert len(D)==27980
n=len(D)
start_ms=D.original_R9_immutable_entry_ms.to_numpy(np.int64)
exit_ms=(pd.to_datetime(D.original_R9_exit_time,utc=True).astype('int64')//1000000).to_numpy(np.int64)
quo=D.AR1_Coinexx_inside_window_quotes.to_numpy(int)
strict=D.AR1_Coinexx_anchor_both_strict.to_numpy(bool)
gap=D.S100_gap_cents_FROZEN.to_numpy(int)
ratio=D.AR1_Coinexx_observed_S100_utilization.to_numpy(float)
leg=D.R9_leg_known_at_entry.to_numpy(int)
# Intentional masked evidence flag: preserve underlying source and outcomes, remove
# selected strictly qualified known paths ONLY from the proxy's prior calibration pool.
masked=np.asarray([(i%41==0 and quo[i]>0 and strict[i]) for i in range(n)],bool)
requests=np.where((quo==0)|((quo>0)&~strict)|masked)[0]
allowed=(quo>0)&strict&~masked
out=[]
for i in requests:
    # All previous R9 exits must be strictly earlier than current entry second.
    earlier=allowed & (exit_ms < start_ms[i])
    earlier[i:]=False
    cand=earlier&(leg==leg[i])&(gap==gap[i]);scope='SAME_LEG_AND_S100_TIER'
    if cand.sum()<40:
        cand=earlier&(leg==leg[i]);scope='SAME_LEG_NORMALIZED_TO_S100'
    if cand.sum()<100:
        cand=earlier;scope='ALL_PRIOR_NORMALIZED_TO_S100'
    m=int(cand.sum())
    if m<100:
        out.append({'source_row':int(D.source_row.iloc[i]),'proxy_reason':'KNOWN_QUOTE_MASKED_VALIDATION' if masked[i] else ('NO_QUOTES' if quo[i]==0 else 'NONSTRICT_ANCHOR'),'time':str(D.original_R9_entry_time.iloc[i]),'leg':int(leg[i]),'frozen_S100_gap_usd':int(gap[i])/100,'scope':'NO_PRIOR_CALIBRATION','prior_examples':m,'pred_P95_observed_DD_over_S100':np.nan,'pred_P975_observed_DD_over_S100':np.nan,'pred_P99_observed_DD_over_S100':np.nan,'pred_P95_DD_usd':np.nan,'pred_P975_DD_usd':np.nan,'prior_empirical_P25_S100':np.nan,'actual_known_DD_over_S100_IF_MASKED':ratio[i] if masked[i] else np.nan})
        continue
    arr=ratio[cand];arr=arr[np.isfinite(arr)]
    p95=float(np.quantile(arr,.95));p975=float(np.quantile(arr,.975));p99=float(np.quantile(arr,.99));rate=float((arr>=.25).mean())
    out.append({'source_row':int(D.source_row.iloc[i]),'proxy_reason':'KNOWN_QUOTE_MASKED_VALIDATION' if masked[i] else ('NO_QUOTES' if quo[i]==0 else 'NONSTRICT_ANCHOR'),'time':str(D.original_R9_entry_time.iloc[i]),'leg':int(leg[i]),'frozen_S100_gap_usd':int(gap[i])/100,'scope':scope,'prior_examples':m,'pred_P95_observed_DD_over_S100':p95,'pred_P975_observed_DD_over_S100':p975,'pred_P99_observed_DD_over_S100':p99,'pred_P95_DD_usd':p95*gap[i]/100,'pred_P975_DD_usd':p975*gap[i]/100,'prior_empirical_P25_S100':rate,'actual_known_DD_over_S100_IF_MASKED':ratio[i] if masked[i] else np.nan})
result=pd.DataFrame(out)
assert result.proxy_reason.eq('NO_QUOTES').sum()==33
assert result.proxy_reason.eq('NONSTRICT_ANCHOR').sum()==195
assert result.proxy_reason.eq('KNOWN_QUOTE_MASKED_VALIDATION').sum()==masked.sum()
result.to_csv(O/'JAN_R6_MISSING_TICK_PROXY_AND_MASKED_KNOWN_STRESS.csv',index=False)
cal=result[result.proxy_reason=='KNOWN_QUOTE_MASKED_VALIDATION'].copy()
valid=cal.pred_P95_observed_DD_over_S100.notna()
V=cal.loc[valid]
observed=V.actual_known_DD_over_S100_IF_MASKED.to_numpy(float)
pred=V.pred_P95_observed_DD_over_S100.to_numpy(float)
coverage=float((observed<=pred).mean()) if len(V) else None
coverage975=float((observed<=V.pred_P975_observed_DD_over_S100.to_numpy(float)).mean()) if len(V) else None
coverage99=float((observed<=V.pred_P99_observed_DD_over_S100.to_numpy(float)).mean()) if len(V) else None
last2=V.time.str[:10].isin(['2026-01-29','2026-01-30'])
coverage975_last2=float((observed[last2]<=V.pred_P975_observed_DD_over_S100.to_numpy(float)[last2]).mean()) if last2.any() else None
# Historical tail-quantile coverage cannot by itself guarantee missing-window coverage.
stats={'all_original_R9_trades_retained':n,'original_missing_quote_windows':33,'original_nonstrict_quote_windows':195,'masked_known_quote_windows_for_proxy_validation':int(masked.sum()),'mask_is_research_view_not_source_edit':True,'masked_with_prior_sample_size_ge100':len(V),'masked_without_prior_sample':int(len(cal)-len(V)),'masked_P95_quantile_empirical_coverage':coverage,'target_nominal_coverage':.95,'conservative_P975_proxy_empirical_coverage':coverage975,'conservative_P99_proxy_empirical_coverage':coverage99,'P975_proxy_last2_shock_days_empirical_coverage':coverage975_last2,'last2_shock_day_validation_cases':int(last2.sum()),'masked_ratio_mean':float(observed.mean()) if len(V) else None,'masked_ratio_P95':float(np.quantile(observed,.95)) if len(V) else None,'missed_extreme_ratio_over_predicted_P95_count':int((observed>pred).sum()) if len(V) else None,'observed_noquote_with_proxy_n':int(result.loc[result.proxy_reason=='NO_QUOTES','pred_P95_DD_usd'].notna().sum()),'observed_nonstrict_with_proxy_n':int(result.loc[result.proxy_reason=='NONSTRICT_ANCHOR','pred_P95_DD_usd'].notna().sum()),'no_fabricated_tick_paths':True,'no_original_account_or_trade_replacement':True}
(O/'JAN_R6_PROXY_GAP_STRESS_RECEIPT.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
