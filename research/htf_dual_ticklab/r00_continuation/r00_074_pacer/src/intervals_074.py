"""Exact historical R9 SYNTH reference intervals for full R00-074 control / frozen rule.
Original R9 trades stay a separate benchmark metric, not relabeled as EA fills.
"""
from pathlib import Path
import numpy as np,pandas as pd,json
from importlib.machinery import SourceFileLoader
ROOT=Path(__file__).resolve().parents[2];HERE=ROOT/'r00_074_pacer';O=HERE/'results'
mod=SourceFileLoader('r00_074_pacer',str(HERE/'src/selective_074.py')).load_module()
bench=pd.read_csv(ROOT/'r00_070_experiment/results/R00_070_071_R9_WEEK_MONTH.csv')
bench=bench[(bench.policy=='R00_068_PROTECTED')&(bench.interval.isin(['ISO_week','UTC_month']))]
frozen=json.loads((O/'FROZEN_FEB_POLICY.json').read_text())['policy'];rows=[]
for broker in ('coinexx','dukascopy'):
 for m in ('06','07'):
  d=mod.get(broker,m);t=d['ts_ms'];y=d['y'];base=d['reference_side'];prio,ps=mod.policies(d)
  for strategy in ('U_all_events',frozen):
   q,th,kind=ps[strategy];use=np.ones(len(t),bool) if q==0 else mod.emit_mask(t,prio[kind],q,th)
   clock=pd.to_datetime(t[use],unit='ms',utc=True)
   weekly=clock.strftime('%G-W%V');monthly=clock.strftime('%Y-%m')
   good=((base==y)&(y!=0))[use]
   for unit,key in (('ISO_week',weekly),('UTC_month',monthly)):
    z=pd.DataFrame({'key':key,'correct':good}).groupby('key').agg(emitted=('correct','size'),correct=('correct','sum'))
    for row in bench[(bench.broker==broker)&(bench.interval==unit)].itertuples():
     v=z.loc[row.key] if row.key in z.index else None
     emitted=int(v.emitted) if v is not None else 0;correct=int(v.correct) if v is not None else 0
     rows.append({'broker':broker,'source_month':m,'interval':unit,'UTC_key':row.key,'policy':strategy,
      'R9_SYNTH_trades':int(row.R9_SYNTH_trades),'floor90':int(row.floor90),
      'emitted':emitted,'correct':correct,'emitted_pass':emitted>=int(row.floor90),'correct_pass':correct>=int(row.floor90)})
table=pd.DataFrame(rows)
# Rows for R9 month/week appearing in a source month OTHER than current source month
# are zero; combine per UTC interval across all underlying data months first, then
# make a SINGLE comparison against each R9 reference row rather than double count.
g=table.groupby(['broker','interval','UTC_key','policy'],as_index=False).agg(R9_SYNTH_trades=('R9_SYNTH_trades','max'),floor90=('floor90','max'),emitted=('emitted','sum'),correct=('correct','sum'))
g['emitted_pass']=g.emitted>=g.floor90;g['correct_pass']=g.correct>=g.floor90
g.to_csv(O/'TRANSFER_074_R9_WEEK_MONTH_EXACT_ALL_ROWS.csv',index=False)
s=g.groupby(['policy','interval']).agg(rows=('UTC_key','count'),emitted_pass=('emitted_pass','sum'),correct_pass=('correct_pass','sum'),emitted=('emitted','sum'),correct=('correct','sum'),R9_SYNTH_trades=('R9_SYNTH_trades','sum'));s.to_csv(O/'TRANSFER_074_R9_WEEK_MONTH_SUMMARY.csv')
print(s.to_string())
