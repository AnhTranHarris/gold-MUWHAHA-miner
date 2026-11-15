"""Limited source-exact V9-signal alternative entry/exit cohort confirmation."""
from research import run_month,CONFIGS
import json,time,sys
from pathlib import Path
import os
selected={'E_micro180_fib236','F_micro180_fib382','G_signal_fib236_step','H_equal_25c_step','P_fib382_structural_R10_T3_10m'}
configs=[x for x in CONFIGS if x.name in selected]
P=Path(os.environ.get('CFAEL_V13_OUTPUT','/mnt/data/cfael_v13'))
for a in sys.argv[1:] or [f'{i:02d}' for i in range(1,10)]:
 t=time.monotonic();r=run_month(int(a),configs)
 for x in r['models'].values():
  x.pop('trades',None)
 (P/f'{a}_small_confirm.json').write_text(json.dumps(r,indent=2))
 print('DONE',a,round(time.monotonic()-t,1),flush=True)
