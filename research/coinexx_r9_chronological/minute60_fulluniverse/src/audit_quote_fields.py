"""Read-only full nine-month audit of whether Coinexx Last/Volume fields contain trade prints."""
import collections,json
from pathlib import Path
import pandas as pd
base=Path('/mnt/data'); out=Path('/mnt/data/r9_m60_expanded/full_results');results={}
for m in range(1,10):
 month=f'{m:02}'; filename=base/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
 row=0; nlast=nvol=nvolr=0; flags=collections.Counter()
 for c in pd.read_csv(filename,usecols=['last','volume','volume_real','flags'],chunksize=1000000):
  row+=len(c);nlast+=int((c['last']!=0).sum());nvol+=int((c['volume']!=0).sum());nvolr+=int((c['volume_real']!=0).sum())
  flags.update({str(int(k)):int(v) for k,v in c['flags'].value_counts().items()})
 results[month]={'rows':row,'nonzero_last':nlast,'nonzero_volume':nvol,'nonzero_volume_real':nvolr,'flags':dict(flags)}
 (out/'quote_field_completeness.json').write_text(json.dumps(results,indent=2)+'\n')
 print('FIELDS',month,results[month],flush=True)
print('ALL_FIELDS_AUDITED',flush=True)
