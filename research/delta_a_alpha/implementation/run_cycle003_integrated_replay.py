"""Causal whole-funnel test on untouched raw Dukascopy quote-side prices.
The hypothetical contract, leverage and margin are deliberately flagged as
uncertified; NO live market or completed monthly gate is implied.
"""
import argparse,json,time
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd
from v1_vertical_grid import Quote
from v1_four_session_architecture import FourSessionV1
P=Path('/mnt/data')
parser=argparse.ArgumentParser()
parser.add_argument('--month',choices=['01','02'],required=True)
parser.add_argument('--start',required=True)
parser.add_argument('--quotes',type=int,default=600000)
parser.add_argument('--latency',type=int,default=250)
parser.add_argument('--cash',type=float,default=300)
args=parser.parse_args()
t0=time.time();start_ms=int(datetime.fromisoformat(args.start+'T00:00:00+00:00').timestamp()*1000)
file=P/f'XAUUSD_DUKAS_2026_{args.month}_ticks.csv(3).gz'
# A hypothetical 100oz contract / 1:500 leverage. NOT sourced from Coinexx.
eng=FourSessionV1(starting_cash=args.cash,leverage=500,commission_per_roundtrip_usd=.20,
                  latency_ms=args.latency,broker_session_confirmed=True)
used=0
for df in pd.read_csv(file,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                      dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'},chunksize=250000):
 selection=df[df.timestamp_ms_utc>=start_ms]
 if len(selection)==0:continue
 for ts,ask,bid in selection.itertuples(index=False,name=None):
  eng.on_tick(Quote(int(ts),int(bid),int(ask)),simulate_broker=True,broker_tradable=True)
  used+=1
  if used>=args.quotes:break
 if used>=args.quotes:break
out=eng.result()
out.update({'schema':'CLEAN_V1_CYCLE003_RESEARCH_INTEGRATED_FOUR_SESSION_PARTIAL_HISTORY',
  'input_month':args.month,'after_utc':args.start,'last_tick_utc':datetime.fromtimestamp(int(eng.last_tick.time_ms_utc)/1000,tz=timezone.utc).isoformat() if eng.last_tick else None,'input_ticks':used,'lag_ms':args.latency,
  'hypothetical_margin':'100 oz/lot and 1:500 account leverage not confirmed Coinexx',
  'simulated_only':True,'source':'Original protected Dukascopy raw BidAsk','run_secs':time.time()-t0,
  'velocity_gate':'NOT_EVALUABLE_FROM_PARTIAL_DAY_SAMPLES',
  'performance_certification':'FAILED_OR_UNDETERMINED__NO_BROKER_PARITY'} )
outpath=Path(__file__).parent/f'INTEGRATED_{args.month}_{args.start}_{args.latency}ms_{used}.json'
outpath.write_text(json.dumps(out,indent=2)+'\n')
print('FINISHED',outpath,'ticks',used,'seconds',round(time.time()-t0,1),'closes',out['closed'],'net',round(out['net_realized'],2),'entry_requests',out['counters'].get('l7_risk_eligible_requests',0),flush=True)
