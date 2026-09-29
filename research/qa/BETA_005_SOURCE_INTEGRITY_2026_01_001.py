#!/usr/bin/env python3
"""Audit the bounded UTC 2026-01-02 original Dukascopy tick stream; scan the entire gzip bytes for source SHA.
This is NOT full-month CRC or causal-feature-cache certification. Read-only; August is sealed.
"""
from __future__ import annotations
import gzip, hashlib, json, math, os, time
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

SRC=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
OUT=Path('/mnt/data/BETA_005_2026_01_02_001_DAY_SOURCE_AUDIT.json')
DAY_START=1767312000000   # 2026-01-02 00:00 UTC
DAY_END=1767398400000     # 2026-01-03 00:00 UTC
EXPECTED_SIZE=68690420
EXPECTED_SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
LO_MS=1767225600000
HI_MS=1769904000000
FRAMES={'S250':250,'S1':1000,'S5':5000,'S15':15000,'S30':30000,'S45':45000,'M1':60000,
        'M5':300000,'M7':420000,'M15':900000,'M30':1800000,'M45':2700000,'H1':3600000,'H4':14400000,'H12':43200000,'D1':86400000}

def run():
 t0=time.perf_counter()
 sha=hashlib.sha256()
 with SRC.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):sha.update(block)
 digest=sha.hexdigest()
 counts={key:0 for key in FRAMES}
 last_bucket={key:None for key in FRAMES}
 problems=Counter();examples=[];rows=0;prev=None;first=None;last=None;equal_ts=0;gap_max=0;spread_min=None;spread_max=None;spread_sum=0;days=set();first_day=None
 with gzip.open(SRC,'rt',encoding='utf-8',newline='') as f:
  header=f.readline().rstrip('\r\n')
  expected_header='timestamp_ms_utc,ask_raw,bid_raw,ask_volume,bid_volume'
  if header!=expected_header:problems['header_mismatch']+=1
  for n,line in enumerate(f,start=2):
   cols=line.rstrip('\r\n').split(',')
   if len(cols)!=5:
    problems['wrong_column_count']+=1
    if len(examples)<8:examples.append({'line':n,'problem':'columns','text':line[:100]})
    continue
   try:
    t=int(cols[0]);ask=int(cols[1]);bid=int(cols[2]);av=float(cols[3]);bv=float(cols[4])
   except (ValueError,OverflowError):
    problems['parse_error']+=1
    if len(examples)<8:examples.append({'line':n,'problem':'parse','text':line[:100]})
    continue
   if t>=DAY_END:break
   if t<DAY_START:continue
   rows+=1
   if not (LO_MS<=t<HI_MS):problems['timestamp_outside_month']+=1
   if prev is not None:
    if t<prev:problems['timestamp_descended']+=1
    if t==prev:equal_ts+=1
    gap_max=max(gap_max,t-prev)
   if bid<=0 or ask<=0:problems['nonpositive_quote']+=1
   if ask<bid:problems['crossed_quote']+=1
   if not (math.isfinite(av) and math.isfinite(bv) and av>=0 and bv>=0):problems['invalid_volume']+=1
   spread=ask-bid
   spread_sum+=spread
   spread_min=spread if spread_min is None else min(spread,spread_min)
   spread_max=spread if spread_max is None else max(spread,spread_max)
   day=datetime.fromtimestamp(t/1000,tz=timezone.utc).strftime('%Y-%m-%d')
   days.add(day)
   if first is None:first=t
   last=t;prev=t
   # This counts tick-containing UTC-aligned bucket identities; it makes no OHLC/feature certification claim.
   for name,width in FRAMES.items():
    b=t//width
    if b!=last_bucket[name]:
     counts[name]+=1;last_bucket[name]=b
 report={'unit_id':'BETA_005_CACHE_INTEGRITY_CERTIFICATION__2026-01__001_DAY_2026-01-02',
         'type':'BOUNDED_DAY_SOURCE_SCAN_ONLY__NOT_FEATURE_CACHE_CERTIFIED',
         'file':SRC.name,'file_size_bytes':SRC.stat().st_size,'file_size_matches_manifest':SRC.stat().st_size==EXPECTED_SIZE,
         'sha256':digest,'sha256_matches_manifest':digest==EXPECTED_SHA,
         'gzip_full_read_crc_verified':False,'headers_match':header==expected_header,
         'month_utc':'2026-01','ticks_parsed':rows,'first_tick_ms':first,'last_tick_ms':last,
         'tick_days_utc':len(days),'first_day_utc':min(days),'last_day_utc':max(days),
         'timestamp_adjacent_equal_ms':equal_ts,'maximum_intertick_gap_ms':gap_max,
         'spread_raw_min':spread_min,'spread_raw_max':spread_max,'spread_raw_mean':spread_sum/rows if rows else None,
         'timestamp_and_quote_problems':dict(problems),'problem_examples':examples,
         'observed_bucket_counts_all_16':counts,
         'completed_month_source_scan':False,'completed_bounded_day_unit':True,'certified_causal_feature_cache':False,
         'strategy_trades':0,'profit_reported':False,'august_read':False,
         'cross_month_account_state':'NOT_APPLICABLE_SOURCE_ONLY',
         'science_gate':'BOUNDED_SOURCE_REVIEW_PASSED_NOT_FULL_MONTH' if digest==EXPECTED_SHA and not problems else 'BLOCKED_SOURCE_PROBLEMS',
         'seconds_runtime':round(time.perf_counter()-t0,3)}
 tmp=OUT.with_suffix(OUT.suffix+'.tmp')
 with tmp.open('w',encoding='utf-8') as f:
  json.dump(report,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,OUT)
 print(json.dumps({'unit_id':report['unit_id'],'row_count':rows,'crc_eof':report['gzip_full_read_crc_verified'],'hash_match':report['sha256_matches_manifest'],'problems':report['timestamp_and_quote_problems'],'bucket_M1':counts['M1'],'bucket_S250':counts['S250'],'seconds':report['seconds_runtime']},sort_keys=True))

if __name__=='__main__':run()
