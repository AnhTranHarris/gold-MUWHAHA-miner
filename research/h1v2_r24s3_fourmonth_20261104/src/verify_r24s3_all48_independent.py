"""Independent full 48-case R24S3 source ordinal and UTC calendar validator.

Reads atomic evidence files. Recomputes each selected outcome, source-original
quote ordinal identity, one-position chronology, exact UTC 15m/hour/day bucketing,
all 48 calendar counts and every SHA guard. Does NOT claim independent rebuild of
raw tick first barrier labels; upstream raw SHA + label generation are distinct.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r24_asof/source')
import r24_firstpass_engine as r
LAB=Path('/mnt/data/h1v2_r24_s3')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as fh:
  for b in iter(lambda:fh.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def check(cond,message):
 if not cond:raise AssertionError(message)

def verify(src,mon):
 out=LAB/'lossless_all48'/src/mon; root=r.R24/'results'/src/mon
 p=out/f'R24S3_{src}_{mon}_ALL_48_INDEPENDENT_SOURCE_CALENDAR_SHA_RECEIPT.json'
 a=json.loads(p.read_text());counter=0;ops=[]
 exact_r9={'01':27980,'02':33523,'06':31758,'07':24324}[mon]
 qtimes,qref=r.calendar_reference(mon);nq=len(qref);qfirst=int(qtimes[0]//900000)
 check(int(qref.sum())==exact_r9,'R9_REF_MONTH_SUM');counter+=1
 check(len(a['variants'])==48 and a['rows_full_calendar']==48*(nq+nq//4+nq//96),'ALL_48_SHAPES');counter+=1
 z=out/f'R24S3_{src}_{mon}_ALL_48_FULL_QUARTER_HOUR_DAY_CALENDARS.csv.gz';f=out/f'R24S3_{src}_{mon}_ALL_48_TRIALS_FULL_MONTH.csv.gz'
 check(sha(z)==a['calendar_sha256'] and sha(f)==a['monthcases_sha256'],'REQUIRED_CSV_SHA');counter+=2
 raworig=np.load(root/f'R24_{src}_{mon}_1000MS_source_quote_ordinal.npy',mmap_mode='r');
 sig=np.load(root/f'R24_{src}_{mon}_1000MS_signal_utc_ms.npy',mmap_mode='r')
 fillidx=np.load(root/f'R24_{src}_{mon}_1000MS_fill_source_quote_ordinal.npy',mmap_mode='r')
 fillt=np.load(root/f'R24_{src}_{mon}_1000MS_actual_fill_utc_ms.npy',mmap_mode='r')
 labels=np.load(root/f'R24_{src}_{mon}_1000MS_labels_2SIDE_3HORIZON.npy',mmap_mode='r')
 check(a['source_pins']['raw']==sha(r.source_file(src,mon)),'RAW_SOURCE_CHANGED');counter+=1
 rows=defaultdict(dict)
 with gzip.open(z,'rt',encoding='utf-8',newline='') as fh:
  for row in csv.DictReader(fh):
   key=(row['variant'],row['resolution'],row['utc_start'])
   check(key not in rows[row['variant']],'DUPLICATE_CALENDAR_KEY')
   rows[row['variant']][key]=row;counter+=1
 nblocks=(nq+nq//4+nq//96)
 check(len(rows)==48,'TOTAL_VARIANTS');counter+=1
 for record in a['variants']:
  code=record['variant'];file=out/f'R24S3_{src}_{mon}_{code}_ALL_SELECTED_CORRECT_WRONG_ORIGINAL_ORDINALS.npz'
  receipt=out/f'R24S3_{src}_{mon}_{code}_ATOMIC_SHA_RECEIPT.json'
  saved=json.loads(receipt.read_text())
  check(saved['selected_member_sha256']==sha(file)==record['selected_member_sha256'],'ORDINAL_ZIP_SHA_MISMATCH');counter+=1
  check(len(rows[code])==nblocks,'INCOMPLETE_MONTH_HOUR_QUARTER_CSV');counter+=1
  with np.load(file,allow_pickle=False) as x:
   ind=x['source_signal_candidate_index'];rawidx=x['source_original_quote_ordinal'];ss=x['source_signal_utc_ms'];
   fillidx_src=x['source_fill_quote_ordinal'];filled=x['actual_observed_fill_utc_ms'];
   side=x['side_buy1_sellminus1'];h=x['selected_horizon_0_15_1_30_2_60'];state=x['correct_target1_stop0_timeout2_censor3'];occupy=x['one_position_occupied_until_utc_ms'];prob=x['asof_model_target_p_at_decision']
   n=len(ind)
   check(all(len(xxx)==n for xxx in (rawidx,ss,fillidx_src,filled,side,h,state,occupy,prob)),'SELECTED_ORDINAL_LENGTH_MISMATCH');counter+=1
   check(np.array_equal(rawidx,raworig[ind]) and np.array_equal(ss,sig[ind]),'SELECTED_ORIGINAL_SIGNAL_ORDINAL_MISMATCH');counter+=2
   check(np.array_equal(filled,fillt[ind]) and np.array_equal(fillidx_src,fillidx[ind]),'SELECTED_FILL_QUOTE_ORDINAL_MISMATCH');counter+=2
   check(np.array_equal(state,labels[ind,np.where(side==1,0,1),h]),'SOURCE_FUTURE_FIRST_PASS_LABEL_MISMATCH');counter+=1
   check(np.isin(side,[-1,1]).all() and np.isin(h,[0,1,2]).all() and np.isin(state,[0,1,2,3]).all(),'ILLEGAL_SIDE_HORIZON_CAUSE');counter+=3
   check((filled>=ss+100).all() and (occupy>=filled).all(),'FILLED_BEFORE_100MS_OR_EXIT_BEFORE_FILL');counter+=2
   check(n<=1 or np.all(filled[1:]>occupy[:-1]),'ONE_POSITION_TIME_VIOLATION');counter+=1
   check(np.isfinite(prob).all(),'NONFINITE_ASOF_MODEL_PROBABILITY');counter+=1
   bins=(filled//900000-qfirst).astype(np.int64)
   check(np.all((bins>=0)&(bins<nq)),'FILLED_BUCKET_OUT_OF_MONTH');counter+=1
   for state_code,field in ((1,'target_first'),(0,'stop_first'),(2,'timeout'),(3,'right_censored')):
    counts=np.bincount(bins[state==state_code],minlength=nq)
    for scale,width in (('QUARTER',1),('HOUR',4),('DAY',96)):
     totals=counts.reshape(-1,width).sum(axis=1)
     for i,xnum in enumerate(totals):
      tick=qtimes[width*i];d=datetime.fromtimestamp(int(tick)/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
      key=(code,scale,d)
      check(int(rows[code][key][field])==int(xnum),'CALENDAR_CAUSE_COUNT_DRIFT '+str(key));counter+=1
   for scale,width in (('QUARTER',1),('HOUR',4),('DAY',96)):
    allcount=np.bincount(bins,minlength=nq).reshape(-1,width).sum(axis=1)
    goal=qref.reshape(-1,width).sum(axis=1)
    for i in range(len(allcount)):
     d=datetime.fromtimestamp(int(qtimes[width*i])/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
     row=rows[code][(code,scale,d)]
     check(int(row['filled'])==int(allcount[i]) and int(row['R9_SYNTH_UTC_REFERENCE'])==int(goal[i]),'QUOTA_PARITY_DRIFT');counter+=2
   check(record['n_selected']==n and record['target_first']==int((state==1).sum()) and record['stop_first']==int((state==0).sum()),'ORIGINAL_RECEIPT_COUNTS');counter+=3
  ops.append({'variant':code,'source_ordinals_n':int(n),'sha256':record['selected_member_sha256']})
 proof={'status':'PASS_SOURCE_HASH_AND_FULL_CALENDAR_AND_ACTION_ORDINALS','source':src,'month':mon,'validation_checks':counter,'failures':0,
        'source_original_quarters':nq,'original_reference_month_count':exact_r9,'selected_variants':ops,
        'verified_all_period_rows':len(rows)*nblocks,'source_archive_sha256':a['source_pins']['raw'],
        'IMPORTANT_LIMIT':'Source original two-sided first passage labels are upstream R24; this verifier recomputes label joins and UTC accounting, NOT all raw quote barrier searches',
        'no_trading_or_out_of_sample_claim':True}
 target=LAB/f'R24S3_{src}_{mon}_INDEPENDENT_ALL_48_FULLCALENDAR_RECEIPT.json'
 target.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps({k:v for k,v in proof.items() if k!='selected_variants'},indent=2),flush=True)
 return proof

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',choices=r.SOURCE_NAMES,required=True);a.add_argument('--month',choices=['01','02','06','07'],required=True)
 x=a.parse_args();verify(x.source,x.month)
