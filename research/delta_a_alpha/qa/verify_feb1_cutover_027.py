#!/usr/bin/env python3
import hashlib, json, datetime as dt
from pathlib import Path
import pandas as pd, numpy as np
R=Path('/mnt/data/daa_feb1_whitepaper_integrity_027');S=Path('/mnt/data')
cutoff=int(pd.Timestamp('2026-02-01T00:00:00Z').timestamp()*1000)
sources=[('january',S/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'),('february',S/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d')]
out={}
for name,path,exp in sources:
  h=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
  f=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
  t=f.timestamp_ms_utc.to_numpy();a=f.ask_raw.to_numpy();b=f.bid_raw.to_numpy()
  record={'sha256':h,'sha_verified':h==exp,'ticks':len(f),'first_ts':int(t[0]),'last_ts':int(t[-1]),'time_disorder':int(np.sum(np.diff(t)<0)),'crossed_quotes':int(np.sum(a<b)),'outside_calendar_window':int(np.sum(t>=cutoff if name=='january' else t<cutoff)),'first_spread_usd':float((int(a[0])-int(b[0]))/1000.)}
  out[name]=record;print(name,json.dumps(record),flush=True)
out['first_feb_quote_utc']=pd.Timestamp(out['february']['first_ts'],unit='ms',tz='UTC').isoformat();out['start_utc']='2026-02-01T00:00:00+00:00';out['first_quote_is_after_start']=out['february']['first_ts']>=cutoff;out['february_1_is_sunday']=dt.date(2026,2,1).weekday()==6
out['pass']=all(out[m]['sha_verified'] and out[m]['time_disorder']==0 and out[m]['crossed_quotes']==0 and out[m]['outside_calendar_window']==0 for m in ('january','february'))
(R/'feb1_cutover_tick_integrity.json').write_text(json.dumps(out,indent=2));print('first_feb_quote_utc',out['first_feb_quote_utc']);print('SOURCE_INTEGRITY',out['pass']);