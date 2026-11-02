from pathlib import Path
from zipfile import ZipFile
import gzip,pandas as pd,numpy as np,json,time,sys
root=Path('/mnt/data');dst=root/'v2_30s_teacher_training/results';dst.mkdir(exist_ok=True)
months=['01','02','06','07'];stats=[]
for broker in ['COINEXX','DUKASCOPY']:
 for m in months:
  t=time.monotonic(); path=root/f'R9_V2_FULLMONTH_{broker}_2026_{m}_EXACT.zip'
  with ZipFile(path) as z:
   with gzip.GzipFile(fileobj=z.open('full_run/trades.csv.gz')) as f:
    df=pd.read_csv(f,dtype={'entry_ms':'int64','exit_ms':'int64','side':'int8','entry_price':'float32','exit_price':'float32','net':'float32','spread':'float32','mfe':'float32','mae':'float32','evidence':'float32'})
  df['day_id']=(df.entry_ms//86400000).astype('int32')
  df['hour']=((df.entry_ms//3600000)%24).astype('int8')
  df['week_id']=(df.day_id//7).astype('int32') # group proper ISO during scoring
  df['win']=(df.net>0).astype('int8')
  df['target']=((df.net>0)&(df.mfe>=.12)).astype('int8')
  df['neutral']=((df.net>=-.1)&(df.net<=.1)).astype('int8')
  gr=df.groupby('day_id',observed=True).agg(trades=('win','size'),win_rate=('win','mean'),net=('net','sum'))
  gr.to_csv(dst/f'{broker.lower()}_{m}_daily_baseline.csv')
  df.to_pickle(dst/f'{broker.lower()}_{m}_raw.pkl')
  stats.append({'broker':broker,'month':m,'rows':int(len(df)),'win_rate':float(df.win.mean()),'target_rate':float(df.target.mean()),'neutral_rate':float(df.neutral.mean()),'win_available':int(df.win.sum()),'days':int(len(gr)),'days_gte80':int((gr.win_rate>=.8).sum()),'net':float(df.net.sum()),'seconds':round(time.monotonic()-t,3)})
  (dst/'full8_stats.json').write_text(json.dumps(stats,indent=2))
  print(stats[-1],flush=True)
