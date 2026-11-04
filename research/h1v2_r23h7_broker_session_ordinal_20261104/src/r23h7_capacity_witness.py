"""R23H-0007 independent R23H24 future-privileged bucket capacity witness register.

Reads original 32 source/month/contract × 3 exact month/day/hour/quarter files,
never reruns or changes future-labeled quote traversal. Full derived tables
preserve original row identities plus falsifiable capacity subtype. The independent
bucket capacity is an upper bound ONLY for frozen candidate/adverse hold contract;
it cannot prove cross-bucket feasibility or a causal prediction.
"""
from __future__ import annotations
import csv,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from r23h7_clock_news import clock_features
BASE=Path(os.environ.get('R23H24_WORKSPACE','/mnt/data/r23h24_workspace')).resolve()
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
MONTHS=('01','02','06','07')
CONTRACTS=('H15_ONLY','H30_ONLY','H60_ONLY','EARLIEST_QUALIFYING_H15_H30_H60')
KINDS=('QUARTER','HOUR','DAY')
def sha(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def month(source,mon,contract,kind,outroot):
 original=BASE/'oracle_held'/source/mon/f'{contract}_{kind}_COMPLETE.csv'
 with original.open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
 target_count={'01':(2976,744,31),'02':(2688,672,28),'06':(2880,720,30),'07':(2976,744,31)}[mon][KINDS.index(kind)]
 assert len(rows)==target_count
 ts=[]
 for row in rows:
  d=datetime.fromisoformat(row['utc_'+kind.lower()]);assert d.utcoffset().total_seconds()==0
  ts.append(int(d.timestamp()*1000))
 assert not np.any(np.diff(ts)<=0)
 if kind!='DAY':sess=clock_features(np.asarray(ts,np.int64))
 for j,r in enumerate(rows):
  ref=int(r['original_R9_SYNTH_exact_reference'])
  independent=int(r['FUTURE_KNOWN_independent_bucket_capacity_upper'])
  global_count=int(r['FUTURE_KNOWN_global_nonoverlap_selected_count'])
  if ref==0:classification='R9_REFERENCE_ZERO'
  elif independent<ref:classification='INDEPENDENT_BUCKET_PHYSICS_INSUFFICIENT'
  elif global_count<ref:classification='GLOBAL_EARLIEST_FINISH_SHORTFALL_CAPACITY_NOT_PROOF'
  else:classification='FUTURE_KNOWN_GLOBAL_MEETS_OR_EXCEEDS_REFERENCE'
  r.update({'R23H7_source_exact_case_classification':classification,
     'source_independent_R9_shortfall':max(ref-independent,0),
     'global_selected_R9_shortfall':max(ref-global_count,0),
     'clock_data_is_nominal_session_proxy_only':True,
     'historical_broker_trade_permission':'UNKNOWN',
     'historical_prop_firm_trade_permission':'UNKNOWN',
     'economic_news_asof_vintage':'UNKNOWN',
     'future_knowledge_not_causal':True})
  if kind!='DAY':
   for col,idx in (('nominal_sydney',4),('nominal_tokyo',5),('nominal_london',6),('nominal_newyork',7),('london_newyork_overlap',11)):
    r[col]=int(sess[j,idx])
 p=outroot/source/mon/f'R23H7_{source}_{mon}_{contract}_{kind}_ALL_WITNESSES.csv'
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 cats={key:sum(r['R23H7_source_exact_case_classification']==key for r in rows) for key in (
   'R9_REFERENCE_ZERO','INDEPENDENT_BUCKET_PHYSICS_INSUFFICIENT',
   'GLOBAL_EARLIEST_FINISH_SHORTFALL_CAPACITY_NOT_PROOF','FUTURE_KNOWN_GLOBAL_MEETS_OR_EXCEEDS_REFERENCE')}
 assert sum(cats.values())==len(rows)
 return {'source':source,'month':mon,'contract':contract,'kind':kind,'rows':len(rows),
   'original_sha256':sha(original),'derived_sha256':sha(p),'derived_path':str(p),
   'reference_sum':sum(int(r['original_R9_SYNTH_exact_reference']) for r in rows),
   'independent_shortfall_sum':sum(int(r['source_independent_R9_shortfall']) for r in rows),
   'global_shortfall_sum':sum(int(r['global_selected_R9_shortfall']) for r in rows),
   'classification_counts':cats}

def run(outroot):
 receipts=[month(s,m,c,k,Path(outroot)) for s in SOURCES for m in MONTHS for c in CONTRACTS for k in KINDS]
 assert len(receipts)==96
 groups={}
 for r in receipts:
  key=(r['source'],r['month'],r['contract'])
  groups.setdefault(key,[]).append(r)
 for key,rs in groups.items():
  assert len(rs)==3 and len({r['reference_sum'] for r in rs})==1,key
  assert rs[0]['reference_sum']=={'01':27980,'02':33523,'06':31758,'07':24324}[key[1]]
 meta={'contract':'IMMUTABLE_R23H24_HOLD15_30_60_FUTURE_PRIVILEGED_COMPLETE_BUCKET_WITNESSES',
       'records':len(receipts),'year':2026,
       'total_derived_rows_by_kind':{kind:sum(r['rows'] for r in receipts if r['kind']==kind) for kind in KINDS},
       'all_source_months_8':True,'full_complete_UTC_clock':True,'all_parent_hashes_recorded':True,
       'not_causal_or_cash_profit':True,'receipts':receipts}
 path=Path(outroot)/'R23H7_ALL_96_FUTURE_CAPACITY_WITNESS_HASHES.json'
 path.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8')
 return meta
if __name__=='__main__':
 root=Path(__file__).resolve().parents[1]/'results'/'capacity_witness'
 meta=run(root)
 print(json.dumps({'source_case_sets':meta['records'],'all_rows':meta['total_derived_rows_by_kind'],
                   'sha_manifest':str(root/'R23H7_ALL_96_FUTURE_CAPACITY_WITNESS_HASHES.json')},indent=2))
