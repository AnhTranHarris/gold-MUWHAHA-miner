#!/usr/bin/env python3
"""Prove all V1 historical structural bar sources exist before first Feb 2026 live quote.
Do not claim trading policy qualification or live startup 300s.
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np
ROOT=Path('/mnt/data/daa_feb1_whitepaper_integrity_027')
meta=json.loads((ROOT/'feb1_cutover_tick_integrity.json').read_text())
first=int(meta['february']['first_ts'])
src=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
df=pd.read_csv(src,compression='gzip',usecols=['timestamp_ms_utc','bid_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32'})
t=df.timestamp_ms_utc.to_numpy();b=df.bid_raw.to_numpy().astype(np.float64)
assert t[-1]<first
TFS={'M5':300000,'M15':900000,'H1':3600000,'H4':14400000};out={}
for name,tf in TFS.items():
  k=t//tf
  starts=np.r_[0,np.flatnonzero(np.diff(k)!=0)+1]
  ends=np.r_[starts[1:]-1,len(t)-1]
  complete=(k[starts]+1)*tf<=first
  j=ends[complete]
  closes=b[j]
  e8=e21=closes[0]
  for close in closes[1:]:
      e8 += (2/9)*(close-e8)
      e21 += (2/22)*(close-e21)
  lastend=int((k[starts][complete][-1]+1)*tf)
  out[name]={'historical_completed_bars':int(len(j)),'latest_completed_bar_end_ms':lastend,'history_age_at_first_quote_minutes':round((first-lastend)/60000,2),'EMA8_raw':float(e8),'EMA21_raw':float(e21),'state':int(np.sign(e8-e21)),'initialized':bool(len(j)>=21)}
# Need properly observe not force stale Friday completed M5 supply signal at Sunday reopen.
out['all_tf_initializable_on_first_feb_quote']=all(x['initialized'] for x in out.values());out['first_live_quote_spread_usd']=meta['february']['first_spread_usd'];out['real_market_entry_tested']=False;out['production_five_minute_eligibility_certified']=False;out['latest_january_tick_utc']=pd.Timestamp(int(t[-1]),unit='ms',tz='UTC').isoformat();out['first_february_tick_utc']=pd.Timestamp(first,unit='ms',tz='UTC').isoformat()
(ROOT/'feb1_predeployment_htf_bootstrap.json').write_text(json.dumps(out,indent=2))
for name in TFS:print(f'{name}: n_closed={out[name]["historical_completed_bars"]} initialized={out[name]["initialized"]} state={out[name]["state"]} age_min={out[name]["history_age_at_first_quote_minutes"]}')
print('HTF_BOOTSTRAP_ALL_READY',out['all_tf_initializable_on_first_feb_quote']);print('FIVE_MINUTE_TRADE_ELIGIBILITY_CERTIFIED',out['production_five_minute_eligibility_certified'])