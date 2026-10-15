from pathlib import Path
import pandas as pd,numpy as np,hashlib,json
D=Path(__file__).parent
p=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz');s='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5';assert hashlib.sha256(p.read_bytes()).hexdigest()==s
raw=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
ms=raw.timestamp_ms_utc.to_numpy();b=raw.bid_raw.to_numpy();a=raw.ask_raw.to_numpy();ledger=pd.read_csv(D/'NATIVE_R9_DEFAULT_SPREAD_025_LATENCY250_LEDGER.csv');stat=pd.read_csv(D/'R9_MINUTE_BRACKET_SPREAD_ECONOMIC_RECONSTRUCTION.csv').query('spreadcap==0.25 and latency_ms==250').iloc[0];errors=[]
for j,row in ledger.iterrows():
 x=int(row.entry_ms);y=int(row.exit_ms);k=np.searchsorted(ms,x,'left');q=np.searchsorted(ms,y,'left');side=int(row.side)
 if k>=len(ms) or ms[k]!=x or q>=len(ms) or ms[q]!=y:errors.append((j,'timestamp_not_quote'));continue
 entry=(a[k] if side==1 else b[k])/1000;exit=(b[q] if side==1 else a[q])/1000
 if abs(entry-row.entry)>1e-8 or abs(exit-row.exit)>1e-8:errors.append((j,'entry_or_exit_nonquote'))
 if abs(side*(exit-entry)-.20-row.net)>1e-6:errors.append((j,'incorrect_pnl'))
 if x<int(row.signal_ms)+250:errors.append((j,'entry_lookahead'))
 if j and row.entry_ms<=ledger.iloc[j-1].exit_ms:errors.append((j,'concurrent_open'))
assert abs(ledger.net.sum()-stat.net_usd)<1e-6
assert not errors,errors[:10]
record={'source':'original Jan 9,135,062 Dukascopy Bid/Ask','mql5_reference_hybrid_git_blob':'7eecb5f1947017a01ce85b2520725de54749e523','mt5_native_parity_claim':False,'partial_source_derived_python_model_only':True,'quote_matched_closes':len(ledger),'timing_cash_occupancy_errors':errors,'sum_pnl':float(ledger.net.sum()),'max_hold_seconds':float(((ledger.exit_ms-ledger.entry_ms)/1000).max()),'owner_60pct_gate_result':'INTERNAL_ONLY_BELOW_THRESHOLD'}
(D/'INDEPENDENT_R9_SOURCE_PARITY_ORIGINAL_QUOTE_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n')
print(record)