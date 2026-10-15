"""Original January quote-level integration smoke, not a performance acceptance backtest.
Scope is deliberately limited; it makes no hourly/daily success claim.
Use --limit 100000 to test real original source import+native G0+funded lifecycle.
"""
import sys,argparse,json,hashlib,time
from pathlib import Path
import pandas as pd
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),'/mnt/data/jan_current_integrated_engine_20261015']
from v1_vertical_grid import Quote
from v2_performance_chassis import V2PerformanceChassis
RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--limit',type=int,default=80000);a.add_argument('--no-native',action='store_true');z=a.parse_args()
 t=time.perf_counter();assert hashlib.sha256(RAW.read_bytes()).hexdigest()==SHA
 c=V2PerformanceChassis(enable_native=not z.no_native)
 stream=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'},chunksize=40_000)
 k=0
 for chunk in stream:
  chunk=chunk[['timestamp_ms_utc','bid_raw','ask_raw']]  # CRITICAL: usecols does not reorder CSV fields
  for row in chunk.itertuples(index=False,name=None):
   c.on_tick(Quote(int(row[0]),int(row[1]),int(row[2])))
   k+=1
   if k>=z.limit:break
  if k>=z.limit:break
 p=c.result()
 p['source_original_sha256']=SHA;p['original_ticks_replayed']=k;p['fraction_of_month']=k/9135062.;p['seconds_elapsed']=time.perf_counter()-t
 p['disposition']='SMOKE_ONLY_NOT_JAN_FULL_BROKER_FUNDING_OR_OWNER_60PCT_SUCCESS';p['research_law']='V1_WHITEPAPER_SUBORDINATE_EXPERIMENT_NO_ENGINE_REPLACEMENT'
 (HERE/'ORIGINAL_TICK_INTEGRATION_SMOKE.json').write_text(json.dumps(p,indent=2,default=str)+'\n')
 pd.DataFrame(c.account.settlements).to_csv(HERE/'ORIGINAL_TICK_SMOKE_SETTLEMENTS.csv',index=False)
 print('SMOKE',json.dumps({q:p[q] for q in ('original_ticks_replayed','fraction_of_month','trades','net','capital_halt','max_tick_equity_dd','seconds_elapsed')}))
