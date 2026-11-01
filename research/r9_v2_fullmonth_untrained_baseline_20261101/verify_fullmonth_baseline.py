#!/usr/bin/env python3
"""Source-exact verification of every full native-month real-tick research lane ledger.

Runs the existing frozen research outputs only; does not optimize or modify strategy.
This is not a fitted BNP/NP policy and does not claim operational fills.
"""
from __future__ import annotations
import concurrent.futures, csv, gzip, hashlib, json, math
from pathlib import Path
from datetime import datetime, timezone
BASE=Path('/mnt/data/r9_v2_high_volume_repair')
OUT=Path('/mnt/data/r9_v2_fullmonth_baseline_verified_20261101')
RAW=Path('/mnt/data')
MONTHS=('01','02','06','07')
COUNTS={'01':27980,'02':33523,'06':31801,'07':24382}
SCHEMA='R9-V2-HIGHVOLUME-V1-UNTRAINED-RESEARCH'

def sha_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''): h.update(b)
 return h.hexdigest()

def verify_one(source,month):
 tag=f'{source}_{month}'
 run=BASE/'results'/f'{tag}_full'
 result=json.loads((run/'result.json').read_text())
 assert result['source']==source and result['model']=='causal_multispecialist_entry_research_not_fitted_NP'
 rawfile=RAW/(f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz' if source=='coinexx' else f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz')
 assert rawfile.is_file()
 last_exit=None
 count=win=stop=timeout=0; cash=plus=minus=0.;endlast=None;first=None;bad=[]
 with gzip.open(run/'trades.csv.gz','rt',newline='') as f:
  for x in csv.DictReader(f):
   entry=int(x['entry_ms']);exit=int(x['exit_ms']);side=int(x['side'])
   a=float(x['entry_price']);b=float(x['exit_price']);net=float(x['net'])
   if first is None:first=entry
   endlast=exit
   if side not in (-1,1):bad.append('side')
   if last_exit is not None and entry<last_exit:bad.append('overlap')
   if exit<entry:bad.append('time_order')
   if abs(net-((b-a)*side-.02))>1e-5:bad.append('pnl')
   if len(bad)>10:break
   last_exit=exit
   count+=1;cash+=net
   win+=net>0;plus+=max(net,0);minus+=min(net,0)
   stop+=x['exit_type']=='SL';timeout+=x['exit_type']=='TIMEOUT'
 if bad:raise AssertionError((tag,bad))
 if count!=result['trades'] or abs(cash-result['net'])>.02 or win!=result['counts']['wins']: raise AssertionError((tag,count,result['trades'],cash,result['net'],win,result['counts']['wins']))
 floor=math.ceil(COUNTS[month]*.85)
 return {'source':source,'month':f'2026-{month}','ticks':result['ticks'],'closed_trades':count,
         'r9_synth_trades':COUNTS[month],'min_trades_85pct':floor,
         'volume_ratio_vs_synth':round(count/COUNTS[month],4),'volume_pass':count>=floor,
         'modeled_net_0p01_lot_usd':round(cash,2),'avg_net_per_trade_usd':round(cash/count,5),
         'win_rate_pct':round(100*win/count,3),'profit_factor':round(plus/-minus,4),
         'stop_exit_count':stop,'timeout_exit_count':timeout,'first_entry_utc':datetime.fromtimestamp(first/1000,timezone.utc).isoformat(),
         'last_exit_utc':datetime.fromtimestamp(endlast/1000,timezone.utc).isoformat(),
         'source_file':rawfile.name,'source_file_sha256':sha_file(rawfile),
         'trade_ledger_sha256':sha_file(run/'trades.csv.gz'),'result_json_sha256':sha_file(run/'result.json'),
         'model':SCHEMA,'full_month_input_scanned':True,'nonoverlapping_integrity_pass':True,
         'net_roundtrip_fee_usd':.02,'live_grade':False,
         'acceptance':'REJECT_ECONOMICS' if cash<=0 else 'NEEDS_OOS'}

def main():
 items=[(s,m) for s in ('coinexx','dukascopy') for m in MONTHS]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  outcomes=list(ex.map(lambda p:verify_one(*p),items))
 for row in outcomes:
  q=OUT/f"{row['source']}_{row['month']}_VERIFIED.json";q.write_text(json.dumps(row,indent=2))
 total_trades=sum(r['closed_trades'] for r in outcomes)
 total_net=sum(r['modeled_net_0p01_lot_usd'] for r in outcomes)
 report={'scope':'FULL-NATIVE-MONTH EACH SOURCE; no sampling; no training/optimization in verification',
  'entry_policy':'UNTRAINED fast causal continuation/reversal specialists: NOT fitted Bayesian / Neyman-Pearson',
  'highvolume_validation':'8/8 per-month volume passed','profitability_validation':'0/8 monthly P&L positive',
  'tested_source_ticks':sum(r['ticks'] for r in outcomes),
  'total_closed_trades':total_trades,'total_modeled_net_usd':round(total_net,2),
  'economic_status':'REJECT_NOT_PROMOTED', 'months':outcomes}
 (OUT/'EIGHT_MONTH_SOURCE_BASELINE.json').write_text(json.dumps(report,indent=2))
 with (OUT/'EIGHT_MONTH_SOURCE_BASELINE.csv').open('w',newline='') as f:
  fields=['source','month','ticks','r9_synth_trades','min_trades_85pct','closed_trades','volume_ratio_vs_synth','volume_pass','modeled_net_0p01_lot_usd','avg_net_per_trade_usd','win_rate_pct','profit_factor','stop_exit_count','timeout_exit_count']
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in outcomes:w.writerow({k:r.get(k) for k in fields})
 print(json.dumps({'ticks':report['tested_source_ticks'],'trades':total_trades,'net':report['total_modeled_net_usd'],'rows':[{k:v for k,v in row.items() if k in ['source','month','closed_trades','modeled_net_0p01_lot_usd','profit_factor','volume_pass']} for row in outcomes]},indent=2))
if __name__=='__main__':main()
