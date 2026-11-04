"""Lossless eight-source R20 report, day/week/month accounting and archival ZIPs.
No upstream raw or original future-known arrays copied or modified.
"""
from __future__ import annotations
import json,csv,hashlib,zipfile,datetime as dt,collections,sys
from pathlib import Path
ROOT=Path('/mnt/data/h1v2_r20_last46');RESULT=ROOT/'results';ARCH=ROOT/'archives';ARCH.mkdir(exist_ok=True)
MONTHS=('01','02','06','07');SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
SCENARIOS=('C1_ASOF_EVERY_DISTINCT_MS_CAP4000_H60_100MS','C2_ASOF_EVERY_DISTINCT_MS_CAP8000_H60_100MS','C3_ASOF_EVERY_DISTINCT_MS_CAP8000_H30_100MS','C4_ASOF_EVERY_DISTINCT_MS_CAP8000_H15_100MS','C5_ASOF_EVERY_DISTINCT_MS_CAP8000_H60_500MS_SLIP20','C6_ASOF_FIRST25MS_CAP8000_H60_100MS')
STOPS=('S0_FIXED_ADVERSE100','S1_FIXED_ADVERSE200','S2_FIXED_ADVERSE500','S3_FIXED_ADVERSE1000','S4_SPREAD_RATIO_25PC_BOUNDED')

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def csvrows(path):
 with open(path,encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def writecsv(path,arr):
 if not arr:raise ValueError('EMPTY_OUTPUT')
 with open(path,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(arr[0]));w.writeheader();w.writerows(arr)

def keyed(rows,col):
 result=collections.defaultdict(list)
 for x in rows:result[x[col]].append(x)
 return result

def main():
 allcases=[];daily=[];weekly=[];months=[];witness=[];allsha=[];sourcepaths={};zip_recs=[]
 for src in SOURCES:
  for mon in MONTHS:
   base=f'R20_{src}_{mon}';stop=f'R20C8_{src}_{mon}';
   bp=RESULT/f'{base}_ALL_SOURCE_SCENARIOS.csv';sp=RESULT/f'{stop}_ALL_SCENARIOS.csv'
   bsc=csvrows(bp);ssc=csvrows(sp)
   assert len(bsc)==6 and len(ssc)==5
   qreg=keyed(csvrows(RESULT/f'{base}_ALL_UTC_15MIN_SCENARIOS.csv'),'scenario')
   qstop=keyed(csvrows(RESULT/f'{stop}_ALL_UTC_QUARTERS.csv'),'mechanism')
   hourreg=keyed(csvrows(RESULT/f'{base}_ALL_UTC_HOURS_SCENARIOS.csv'),'scenario')
   hourstop=keyed(csvrows(RESULT/f'{stop}_ALL_UTC_HOURS.csv'),'mechanism')
   originalrefs=None
   for state in bsc+ssc:
    key=state.get('scenario') or state.get('mechanism');mode='BASE_NOMINAL_ADMISSION' if 'scenario' in state else 'NEW_ADVERSE_INVENTORY_RISK_CONTRACT';rqs=qreg[key] if 'scenario' in state else qstop[key]
    rhs=hourreg[key] if 'scenario' in state else hourstop[key]
    qstarts=[];qref=[];good=[]
    for x in rqs:
     qstarts.append(x['UTC_quarter']);qref.append(int(x.get('R9_SYNTH_ref',x.get('R9_SYNTH_source_ref'))));good.append(int(x.get('R20_total_future_winners',x.get('R20_future_total'))))
    if originalrefs is None:originalrefs=list(qref)
    assert originalrefs==qref and len(rhs)==len(qstarts)//4
    hcounts=[sum(good[i:i+4]) for i in range(0,len(good),4)];hrefs=[sum(qref[i:i+4]) for i in range(0,len(qref),4)]
    assert hcounts==[int(x.get('R20_total_future_winners',x.get('future_total_hour'))) for x in rhs]
    cases={'feed':src,'month':'2026-'+mon,'mechanism':key,'mechanism_type':mode,
     'full_utc_quarters':len(rqs),'original_R9_reference_trade_count':sum(qref),
     'future_selected_hindsight_trades':sum(good),'active_quarters':sum(int(x>0) for x in qref),
     'active_quarters_with_original_quota':sum(int(r>0 and n>=r) for n,r in zip(good,qref)),
     'active_hours':sum(int(x>0) for x in hrefs),
     'active_hours_with_original_quota':sum(int(r>0 and n>=r) for n,r in zip(hcounts,hrefs)),
     'gross_future_oracle_volume_ratio_to_SYNTH_reference':(sum(good)/sum(qref)) if sum(qref) else None,
     'NEW_mechanism_not_asof_BUY_SELL_qualified':True,'no_broker_live_fill_cash_profit':True,
     'source_scenario_file':bp.name if mode.startswith('BASE') else sp.name}
    allcases.append(cases)
    # All original source calendar days in original source, including reference-zero.
    days=collections.OrderedDict()
    for tm,n,r in zip(qstarts,good,qref):
     dd=tm[:10]
     if dd not in days:days[dd]={'source':src,'month':mon,'mechanism':key,'UTC_date':dd,'R9_SYNTH_ref_trade_count':0,'R20_hindsight_future_winner_count':0,'source_active_15m_quarters':0,'15m_quotas_met':0}
     x=days[dd];x['R9_SYNTH_ref_trade_count']+=r;x['R20_hindsight_future_winner_count']+=n;x['source_active_15m_quarters']+=int(r>0);x['15m_quotas_met']+=int(r>0 and n>=r)
    for x in days.values():
     x['day_ref_met']=int(x['R20_hindsight_future_winner_count']>=x['R9_SYNTH_ref_trade_count']) if x['R9_SYNTH_ref_trade_count'] else ''
     x['unmet_15m_quotas']=x['source_active_15m_quarters']-x['15m_quotas_met']
     daily.append(x)
    byweek=collections.OrderedDict()
    for x in days.values():
     iso=dt.date.fromisoformat(x['UTC_date']).isocalendar();wkey=f'{iso.year}-W{iso.week:02d}'
     if wkey not in byweek:byweek[wkey]={'source':src,'month':mon,'mechanism':key,'ISO_week':wkey,'month_sample_days':0,'ref_trades_in_month_clip':0,'hindsight_trades_in_month_clip':0,'source_active_quarters_in_month_clip':0,'quarter_quotas_met_in_month_clip':0,'INCOMPLETE_ISO_WEEK_CALENDAR_POSSIBLE':True}
     p=byweek[wkey];p['month_sample_days']+=1;p['ref_trades_in_month_clip']+=x['R9_SYNTH_ref_trade_count'];p['hindsight_trades_in_month_clip']+=x['R20_hindsight_future_winner_count'];p['source_active_quarters_in_month_clip']+=x['source_active_15m_quarters'];p['quarter_quotas_met_in_month_clip']+=x['15m_quotas_met']
    weekly.extend(byweek.values())
    months.append({**cases,'source_active_days':sum(int(x['R9_SYNTH_ref_trade_count']>0) for x in days.values()),
     'active_days_meeting_reference':sum(int(x['R9_SYNTH_ref_trade_count']>0 and x['R20_hindsight_future_winner_count']>=x['R9_SYNTH_ref_trade_count']) for x in days.values())})
    if key=='S4_SPREAD_RATIO_25PC_BOUNDED':
     # Preserve all 43 remaining negative evidence records, no sampling.
     for q,x in enumerate(rqs):
      if qref[q] and good[q]<qref[q]:
       witness.append({'source':src,'month':mon,'UTC_quarter':qstarts[q],
         'R9_SYNTH_ref':qref[q],'future_winning_actions':good[q],'still_unmet':qref[q]-good[q],
         'original_R19_selected':int(x['base_R19_S3_future_winners']),
         'new_spread_stop_adaptive_added':int(x['new_counterfactual_future_winners']),
         'changed_stop_can_increase_loss_magnitude':True,'not_a_causal_action':True})
   # Files retained losslessly inside source archive, no raw original gzip copies.
   keep=sorted(set(list(RESULT.glob(f'{base}_*'))+list(RESULT.glob(f'{stop}_*'))))
   assert len(keep)>=11
   zp=ARCH/f'R20_{src}_{mon}_ALL_11_CONTRACTS_COMPLETE_UTC_QUARTER_HOUR_SOURCE_ORDINALS_20261103.zip'
   memberhash=[]
   with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for file in keep:
     z.write(file,arcname='results/'+file.name)
     memberhash.append({'path':'results/'+file.name,'bytes':file.stat().st_size,'sha256':sha(file)})
   with zipfile.ZipFile(zp,'r') as z:
    assert z.testzip() is None and len(z.namelist())==len(keep)
    for member in memberhash:
     with z.open(member['path']) as f:
      h=hashlib.sha256()
      for bb in iter(lambda:f.read(1<<20),b''):h.update(bb)
      assert h.hexdigest()==member['sha256']
   zip_recs.append({'source':src,'month':mon,'archive':zp.name,'bytes':zp.stat().st_size,'sha256':sha(zp),'members':memberhash,'crc_and_full_member_sha_verified':True,
    'original_raw_source_gzip_SHA256':json.loads((RESULT/f'{base}_EXACT_SOURCE_AND_OUTPUT_SHA_RECEIPT.json').read_text())['original_r18_sha']})
   print('ZIP',src,mon,zp.stat().st_size,len(keep),flush=True)
 writecsv(ROOT/'R20_ALL_88_EXACT_SOURCE_MONTH_CONTRACT_RESULTS.csv',allcases)
 writecsv(ROOT/'R20_ALL_UTC_DAYS_ALL_11_SCENARIOS_EIGHT_SOURCE_MONTHS.csv',daily)
 writecsv(ROOT/'R20_ALL_UTC_MONTHLY_REFERENCE_AND_DAY_QUARTER_HOUR_RESULTS.csv',months)
 writecsv(ROOT/'R20_ALL_MONTH_CLIPPED_ISO_WEEKS_ALL_11_SCENARIOS.csv',weekly)
 writecsv(ROOT/'R20_ALL_43_RESIDUAL_15MIN_FAILURE_WITNESSES_FULL.csv',witness)
 assert len(witness)==43,(len(witness),witness)
 receipt={'name':'R20_H1V2_8_SOURCE_11_REGIME_COMPLETE_SOURCE_EXACT_QUOTE_ORDINAL_AND_CALENDAR_BUNDLES',
   'source_receipts':zip_recs,'original_repaired_R9_sha':'ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0',
   'original_R19_git_sha':'0c8aaa8430bdd668ab6e8585cb75e702f21b1f9f',
   'eight_sources':len(zip_recs),'total_scenarios':len(allcases),'all_original_UTC_days_eight_source_x11_regimes':len(daily),
   'all_month_clipped_iso_weeks':len(weekly),'preserved_negative_residual_quarters':len(witness),
   'all_source_month_archive_crc_sha_verified':True,'actual_live_fill_and_causal_edge_not_established':True}
 p=ARCH/'R20_ALL_EIGHT_ARCHIVES_AND_EXACT_SOURCE_MEMBER_SHA_MANIFEST.json';p.write_text(json.dumps(receipt,indent=2)+'\n')
 # Source, testing and receipt kit.
 kit=ARCH/'R20_NEW_SOURCE_TESTS_FULL_VERIFIERS_AND_REPORT_GENERATOR_20261103.zip'
 kitfiles=(sorted((ROOT/'src').glob('*.py'))+sorted((ROOT/'tests').glob('test_*.py'))+
    [ROOT/'verify_r20_source_experiment.py',ROOT/'verify_r20_adaptive_stop.py',ROOT/'build_r20_archive_and_unabridged_report.py',ROOT/'R20_FULL_EIGHT_SOURCE_INDEPENDENT_REPLAY_RECEIPT.json'])
 with zipfile.ZipFile(kit,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for file in kitfiles:z.write(file,arcname=str(file.relative_to(ROOT)))
 with zipfile.ZipFile(kit) as z:assert z.testzip() is None
 print('COMPLETE',json.dumps({'days':len(daily),'weeks':len(weekly),'source_regimes':len(allcases),'remaining_witness':len(witness),'archives':len(zip_recs),'kit':kit.name}),flush=True)
 return receipt
if __name__=='__main__':main()
