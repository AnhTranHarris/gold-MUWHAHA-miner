"""January-1 source preflight ONLY; no order simulation or full-V1 claims."""
import csv, gzip, hashlib, json, statistics
from datetime import datetime, timezone
from pathlib import Path
SRC=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
EXPECTED_SHA256='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
sha=hashlib.sha256(SRC.read_bytes()).hexdigest()
if sha!=EXPECTED_SHA256: raise RuntimeError('January raw source hash mismatch')
T0=1767225600000 # Jan 1 2026 00:00 UTC
n=0;mn=10**18;mx=0;first=None;end=None;spreads=[]
with gzip.open(SRC,'rt',newline='') as f:
    r=csv.DictReader(f)
    for row in r:
        t=int(row['timestamp_ms_utc'])
        if first is None: first=t
        if t>first+300000:break
        a=int(row['ask_raw']);b=int(row['bid_raw']);s=(a-b)/1000
        n+=1;mn=min(mn,int(a-b));mx=max(mx,int(a-b));spreads.append(s);end=t
iso=lambda t:datetime.fromtimestamp(t/1000,tz=timezone.utc).isoformat()
res={
 'unit':'DAA_JAN1_ASOF_STARTUP_PREFLIGHT_031',
 'raw_source_sha256':sha,
 'claim':'EXACT_RAW_QUOTE_FIRST_FIVE_MINUTES_ONLY_NOT_V1_TRADING',
 'deployment_utc':iso(T0),
 'first_observed_quote_utc':iso(first),
 'quote_wait_from_midnight_seconds':(first-T0)/1000,
 'first_observed_300s_quote_count':n,
 'last_observed_quote_within_300s_utc':iso(end),
 'first_observed_spread_usd':spreads[0],
 'min_spread_usd':min(spreads),'max_spread_usd':max(spreads),
 'median_spread_usd':statistics.median(spreads),
 'january_gzip_contains_december_completed_HTF_bars':False,
 'actual_broker_margin_ready':'UNKNOWN_FROM_DUKAS_SOURCE',
 'actual_broker_tradable_status':'UNVERIFIED_FROM_QUOTES_ALONE',
 'january_source_only_five_minute_readiness':'NOT_CERTIFIABLE_WITHOUT_GENUINE_PRE_T0_HTF_BROKER_HISTORY',
 'asof_model_parameters':'MUST_BE_FROZEN_BEFORE_2026_01_01; JANUARY_RESULTS_CANNOT_SEED',
 'full_v1_economic_execution':'NOT_PERFORMED',
 'preserved_holdout_status':{'august':'SEALED','september':'RESERVED'},
}
out=Path('/mnt/data/daa_v1_hardlock_031/JAN1_ASOF_STARTUP_PREFLIGHT_031.json')
out.write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))