"""Independent raw-gzip Python review of original entry second, no lookahead."""
from pathlib import Path
import pandas as pd,numpy as np,gzip,json
O=Path('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118')
d=pd.read_csv(O/'JAN_27980_STRICT_ENTRY_CAUSAL_MICRO_HA_FIB.csv').set_index('source_row')
refs={1:'2026-01-02',2:'2026-01-02',6433:'2026-01-09',26488:'2026-01-29',27060:'2026-01-30'}
w=[]
for day in sorted(set(refs.values())):
 p=Path('/mnt/data')/f'R9_REAL_{day}_ticks.csv.gz'
 raw=pd.read_csv(p,compression='gzip',usecols=['run_label','time_msc','bid','ask'],low_memory=False)
 raw=raw.loc[raw.run_label.eq('REAL')].sort_values('time_msc')
 for row,dtext in refs.items():
  if dtext!=day:continue
  u=d.loc[row];start=int(u.entry_ms);win=raw[(raw.time_msc>=start-60000)&(raw.time_msc<start)]
  last=win.tail(1).time_msc.iloc[0];s10=win[win.time_msc>=start-10000]
  v={'row':row,'r9_entry_ms_strict':start,'latest_quote_before_entry':int(last),'n10':len(s10),'n60':len(win),'mean_spread60':float((win.ask-win.bid).mean()),'python_last_quote_msc_strictly_before':bool(last<start)}
  assert v['n10']==int(u.quotes10) and v['n60']==int(u.quotes60)
  assert abs(v['mean_spread60']-u.mean_spread60_USD)<1e-6
  assert v['python_last_quote_msc_strictly_before']
  w.append(v)
(O/'JAN_PYTHON_STRICT_ENTRY_RAW_TICK_PARITY.json').write_text(json.dumps(w,indent=2));print('PARITY OK',len(w),'direct original gzip witnesses')
