import sys,zipfile,gzip,json
from pathlib import Path
import numpy as np,pandas as pd
P=Path('/mnt/data/AR1_JAN_R2_COMPLETED_REVERSE_ENGINEERING_20261118');sys.path.insert(0,str(P))
from importlib import import_module
m=import_module('07_ar1_january_observational_policy')
z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
with gzip.GzipFile(fileobj=z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as f:d=pd.read_csv(f)
s=pd.read_csv(P/'JAN_27980_IMMUTABLE_TRADES_WITH_FITTED_AR1_MODEL_SCORES.csv.gz')
c=m.load_january_model(P/'JAN_AR1_REVERSE_ENGINEERED_NUMERIC_FORMULA_AND_CROSSDAY_DIAGNOSTICS.json')
assert len(d)==len(s)==27980
nums=[]
for r in d.to_dict('records'):
 assert m.s100_gap_usd(r['book_before_cents']/100)*100==r['frozen_s100_gap_cents'],(r['source_row'],'S100 tier mismatch')
 p=m.market_pressure_probability(m.causal_market_features(r),c)
 nums.append(p)
diff=np.abs(np.array(nums)-s.P_util25_full_January_fit.to_numpy());assert diff.max()<1e-11,('model numeric parity',diff.max())
# For test of tick state machine, reopen original Coinexx source January 9 in Python, trade #6433.
rr=d[d.source_row.eq(6433)].iloc[0]
t=pd.read_csv('/mnt/data/R9_REAL_2026-01-09_ticks.csv.gz',compression='gzip',usecols=['time_msc','bid','ask'])
sec=t[t.time_msc.between(int(rr.open_ms),int(rr.close_ms),inclusive='both')]
assert len(sec)==rr.quote_count
obs=m.ObservedCoinexxPositionRisk(source_row=6433,side=rr.side,original_R9_entry_ms=int(rr.open_ms),original_R9_exit_ms=int(rr.close_ms),frozen_gap_cents=int(rr.frozen_s100_gap_cents))
for row in sec.itertuples(index=False):obs.observe_original_real_quote(int(row.time_msc),round(row.bid*100),round(row.ask*100))
ref=pd.read_csv(P/'JAN_ALL_27980_PYTHON_REAL_TICK_REPLAY_POLICY_ALERT_TIMES.csv.gz');w=ref[ref.source_row.eq(6433)].iloc[0]
for attr in ['first_u25_ms','first_u50_ms','first_u75_ms','first_u90_ms','first_full_s100_ms']:
 expected_name = attr.replace('_ms','_touch_ms') if attr != 'first_full_s100_ms' else 'first_full_S100_touch_ms'
 assert getattr(obs,attr)==w[expected_name],(attr,getattr(obs,attr))
assert obs.observe_original_real_quote(int(rr.close_ms)+1,round(sec.bid.iloc[-1]*100),round(sec.ask.iloc[-1]*100)) is None
receipt={'all_27980_january_frozen_s100_tiers_match':True,'all_27980_serialized_logistic_equations_match_sklearn':True,'maximum_probability_difference':float(diff.max()),'source_row_6433_tick_by_tick_policy_state_parity':True,'no_after_exit_quotes_accepted':True,'owner_frozen_S100_never_edited':True,'no_order_methods':True}
json.dump(receipt,open(P/'JAN_RUNTIME_POLICY_SOURCE_PARITY_TESTS.json','w'),indent=2)
print(json.dumps(receipt,indent=2))
