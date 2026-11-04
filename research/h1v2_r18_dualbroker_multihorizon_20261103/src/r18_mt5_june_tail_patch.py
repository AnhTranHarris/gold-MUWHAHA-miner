"""Additive **two UTC-hour** frozen R18 experiment: repair June MT5 broker
historical source calendar using exact July monthly data, preserving the real
one-hour rollover quote drought and all ORIGINAL eight source R18 output files.

We recompute only missing 2026-06-30 22:00/23:00 UTC decisions from BOTH
SHA-pinned original June & July raw quote streams. No original GitHub files or
Drive research receipts changed. Hindsight first-passage only, not live fills.
"""
from __future__ import annotations
import sys,csv,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import r18_broker_multihorizon as r18
HERE=Path(__file__).resolve().parents[1];OUT=HERE/'results_r18_JUNE_TAIL_PATCH'
ORIG=HERE/'results';MONTH='06';SOURCE='MT5_BROKER_EXPORT'

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 root=Path('/mnt/data')
 # R18 original code verifies exact gzip SHA of each month before decoding.
 tj,bj,aj,jpath=r18.read_raw(SOURCE,MONTH,root)
 tx,bx,ax,xpath=r18.read_raw(SOURCE,'07',root)
 _,e=r18.month_range(MONTH)
 mark=(tx>tj[-1])&(tx<e+180000)
 assert np.any(mark) and tx[mark][0]>tj[-1]+15_000
 t=np.r_[tj,tx[mark]];b=np.r_[bj,bx[mark]];a=np.r_[aj,ax[mark]]
 assert np.all(np.diff(t)>=0)
 start=e-2*3600000
 # First 22:00 July source event becomes actual June source after -3h UTC.
 assert tj[-1]<start<=tx[mark][0]
 ix,lanes,admission=r18.candidate_lanes(t,b,a)
 in_tail=(t[ix]>=start)&(t[ix]<e)
 ix=ix[in_tail];lanes={k:v[in_tail] for k,v in lanes.items()}
 assert len(ix)>1
 b0,s0=r18.original_s1_labels(t,b,a,ix)
 risk=r18.first_pass_labels(t,b,a,ix)
 masks=[('ORIGINAL_S1_F15_SAFE30',b0,s0,15000)] + [
    (f'NEW_FIRST_TOUCH_{h//1000}_BEFORE_ADVERSE',
     risk['BUY_good']&(risk['BUY_tp']>=0)&(t[risk['BUY_tp'].clip(min=0)]<=t[ix]+h),
     risk['SELL_good']&(risk['SELL_tp']>=0)&(t[risk['SELL_tp'].clip(min=0)]<=t[ix]+h),h)
     for h in r18.HORIZONS]
 refs=r18.refs_for_month(MONTH,root);q0=refs['qkeys'][0]
 oldrows={(x['lane'],x['contract']):x for x in json.loads((ORIG/f'R18_{SOURCE}_06_SOURCE_VERIFIED_RECEIPT.json').read_text())['results']}
 all_q=[];all_h=[];result=[];traces={}
 for lane,accept in lanes.items():
  for contract,goodb,goods,h in masks:
   ids,side,ex,n=r18.selected_count(t,ix,accept,goodb,goods,risk['BUY_tp'],risk['SELL_tp'],h)
   assert len(ids)==0 or np.all(t[ix[ids[1:]]]>t[ex[:-1]])
   q=np.zeros(4,np.int32)
   for j in ids:
    qi=(t[ix[j]]-start)//900000
    assert 0<=qi<8
   last8=np.bincount(((t[ix[ids]]-start)//900000).astype('int64'),minlength=8)
   h2=last8.reshape(2,4).sum(axis=1)
   old=oldrows[(lane,contract)]
   tailq=0;tailh=0
   for z,count in enumerate(last8):
    y=start+z*900000;source_index=int(y//900000-q0)
    ref=int(refs['qref'][source_index])
    tailq+=int(ref>0 and count>=ref)
    all_q.append({'source':SOURCE,'month':'2026-06','lane':lane,'contract':contract,
      'utc_quarter':refs['rows'][source_index]['utc_quarter'],
      'original_R9_reference':ref,'source_exact_july_halo_selected':int(count),
      'meets_quarter':int(count>=ref) if ref else '',
      'historical_source_quote_ordinals_frozen':True})
   for z,count in enumerate(h2):
    hour=start+z*3600000;hindex=int((hour//900000-q0)//4)
    ref=int(refs['href'][hindex]);tailh+=int(ref>0 and count>=ref)
    all_h.append({'source':SOURCE,'month':'2026-06','lane':lane,'contract':contract,
      'utc_hour':refs['rows'][hindex*4]['utc_hour'],
      'original_R9_reference':ref,'source_exact_july_halo_selected':int(count),
      'meets_hour':int(count>=ref) if ref else '',
      'historical_source_quote_ordinals_frozen':True})
   rec={'source':SOURCE,'month':'06','lane':lane,'contract':contract,
     'original_JUNE_cutoff_selected':int(old['hindsight_firstTP_selected_onepos']),
     'NEW_JULY_RAW_UTC_HALO_tail_selected':int(len(ids)),
     'corrected_hindsight_selected':int(old['hindsight_firstTP_selected_onepos'])+len(ids),
     'original_quarter_quota_met':int(old['15m_quota_met']),
     'new_tail_quarters_meeting_quota':tailq,
     'corrected_quarters_met':int(old['15m_quota_met'])+tailq,
     'active_quarters':int(old['active_quarters']),
     'original_hourly_met':int(old['hourly_quota_met']),
     'new_tail_hours_meeting_quota':tailh,
     'corrected_hours_met':int(old['hourly_quota_met'])+tailh,
     'active_hours':int(old['active_hours']),
     'original_8_source_results_preserved':True,'future_selected_not_causal':True}
   assert rec['corrected_quarters_met']<=rec['active_quarters'] and rec['corrected_hours_met']<=rec['active_hours']
   result.append(rec)
   pfx=f'{lane}__{contract}'
   # Joined source ordinal at or after *new* July monthly quote path; full
   # ordinal mapping includes exact June file row count as offset.
   traces[pfx+'_stitched_entry_ord']=ix[ids]
   traces[pfx+'_future_selected_side']=side
   traces[pfx+'_stitched_exit_ord']=ex
   print(lane,contract,len(ids),rec['corrected_quarters_met'],'/',rec['active_quarters'],rec['corrected_hours_met'],'/',rec['active_hours'],flush=True)
 assert len(result)==50 and len(all_q)==400 and len(all_h)==100
 def save_csv(name,rows):
  p=OUT/name
  with p.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  return p
 q=save_csv('R18_JUNE_MT5_HALO_ALL_400_SOURCE_EXACT_QUARTER_RECORDS.csv',all_q)
 h=save_csv('R18_JUNE_MT5_HALO_ALL_100_SOURCE_EXACT_HOURLY_RECORDS.csv',all_h)
 r=save_csv('R18_JUNE_MT5_HALO_ALL_50_CASE_CORRECTED_SOURCE_COUNTS.csv',result)
 npz=OUT/'R18_JUNE_MT5_HALO_FULL_50_SOURCE_QUOTE_ORDINAL_TAIL_SETS.npz';np.savez_compressed(npz,**traces)
 rec={'status':'OFFLINE_FUTURE_SELECTED_HINDSIGHT_ONLY_DO_NOT_DEPLOY',
  'original_JUNE_file_sha256':r18.sha(jpath),'new_JULY_cross_month_file_sha256':r18.sha(xpath),
  'source_clock_shift_hours':-3,'source_JUNE_original_row_count':len(tj),
  'append_exact_JULY_raw_quote_rows':int(mark.sum()),
  'calendar_gap_ms_preserved':int(tx[mark][0]-tj[-1]),
  'utc_tail_start_ms':int(start),'utc_end_month_ms':int(e),
  'source_ordinal_mapping':'stitched row ordinals 0:(N_JUNE-1) are original June, N_JUNE.. are original first July quote rows',
  'source_calendar_50_scenarios':result,
  'input_source_sha_pinned':True,
  'outputs':{v.name:{'size':v.stat().st_size,'sha256':r18.sha(v)} for v in (q,h,r,npz)},
  'original_EIGHT_FULL_MONTH_R18_experiments_UNTOUCHED':True}
 (OUT/'R18_MT5_JUNE_UTC_HALO_FULL_50_CASE_SOURCE_RECOVERY_RECEIPT.json').write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
 print('PASS',len(result),'original June quote rows',len(tj),'July actual source quote tail',int(mark.sum()),flush=True)

if __name__=='__main__':main()
