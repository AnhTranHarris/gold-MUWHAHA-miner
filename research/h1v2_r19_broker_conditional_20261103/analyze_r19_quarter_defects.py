"""All source-quarter independent raw Bid/Ask / quote arrival / gap diagnostics.

Raw-source associations, not causal proof that spread/news caused a miss.
Source quote snapshots are original preexisting gzip, independently SHA-checked.
"""
from __future__ import annotations
import argparse,csv,sys,json
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/h1v2_r19_broker_union')
sys.path.insert(0,str(ROOT/'src'))
import r19_multi_clock_union as r19
import r18_broker_multihorizon as r18
from r18_frozen_latency_economic_stress import get_frozen
OUT=ROOT/'results_defect_diagnostics'
CASE='lag100_slip0_fillcap4000'

def run(source,mon):
 t,b,a,orig,side,origexit,prov=get_frozen(source,mon)
 refs=r18.refs_for_month(mon,Path('/mnt/data'));qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 src=ROOT/('results_v2' if (source=='DUKASCOPY_RAW' and mon=='02') or (source=='MT5_BROKER_EXPORT' and mon in ['06','07']) else 'results')
 with open(src/f'R19_{source}_{mon}_ALL_QUARTERS.csv',newline='') as f:
  qr=[r for r in csv.DictReader(f) if r['case']==CASE]
 assert len(qr)==len(qref)
 union,side,bits,mask,counts,pin=r19.read_unions(source,mon,t,b,a,orig,side)
 allquote_spread=(a.astype(np.int64)-b.astype(np.int64))
 epoch=np.r_[qkeys*900000, (qkeys[-1]+1)*900000]
 bnds=np.searchsorted(t,epoch,side='left')
 unionidx=np.searchsorted(t[union],epoch,side='left')
 rows=[]
 for k,r in enumerate(qr):
  assert int(r['R9_SYNTH_clock_UTC_ref'])==int(qref[k])
  rr=int(qref[k]);sel=int(r['future_selected_good']);i=int(bnds[k]);j=int(bnds[k+1]);num=j-i
  sq=allquote_spread[i:j]
  # These are RAW original source observations, not the execution ledger.
  median=float(np.median(sq))/1000 if num else None
  p90=float(np.percentile(sq,90))/1000 if num else None
  p99=float(np.percentile(sq,99))/1000 if num else None
  hi=float((max(np.max(b[i:j])-np.min(b[i:j]),np.max(a[i:j])-np.min(a[i:j]))))/1000 if num else None
  gaps=int(np.count_nonzero(np.diff(t[i:j])>15000)) if num>1 else 0
  max_gap=int(np.max(np.diff(t[i:j]))) if num>1 else None
  row={'source':source,'month':mon,'original_UTC_quarter':r['utc_quarter'],
   'original_R9_SYNTH_quarter_ref':rr,'R19_hindsight_selected_actual_100ms_quote_fill':sel,
   'source_ref_is_active':int(rr>0),'R19_quarter_deficit':max(0,rr-sel),
   'original_source_raw_quote_rows':num,'original_quote_median_spread_USD_per_oz':median,
   'original_quote_p90_spread_USD_per_oz':p90,'original_quote_p99_spread_USD_per_oz':p99,
   'original_quote_fraction_spread_gt1p50':(float((sq>1500).mean()) if num else None),
   'original_quote_fraction_spread_gt4p00':(float((sq>4000).mean()) if num else None),
   'original_quote_max_one_side_high_low_range_USD_per_oz':hi,
   'R18_original_10lane_frozen_unique_candidate_ordinals_in_quarter':int(unionidx[k+1]-unionidx[k]),
   'original_quote_gaps_gt15s_wholly_inside_quarter':gaps,'max_original_intraperiod_gap_ms':max_gap,
   'zero_raw_quote_quarter':int(num==0),
   'source_forensics_not_broker_dealer_fill':True,'negative_outcome_not_dropped':True}
  rows.append(row)
 OUT.mkdir(exist_ok=True)
 out=OUT/f'R19_{source}_{mon}_ALL_ORIGINAL_UTC_QUARTER_RAW_SPREAD_GAPS_AND_DEFICITS.csv'
 with open(out,'w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 misses=[x for x in rows if x['R19_quarter_deficit']>0 and x['source_ref_is_active']]
 return {'source':source,'mon':mon,'original_source_sha':r18.PINS[source][mon],
  'all_quarters':len(rows),'reference_active':int(np.count_nonzero(qref)),
  'missed_reference_quarters':len(misses),'missing_reference_trades':sum(x['R19_quarter_deficit'] for x in misses),
  'no_raw_quote_reference_active_quarters':sum(x['zero_raw_quote_quarter'] for x in rows if x['source_ref_is_active']),
  'missed_quarters_with_spread_gt4_fraction_gt50pct':sum((x['original_quote_fraction_spread_gt4p00'] or 0)>.5 for x in misses),
  'missed_quarters_at_UTC_23':sum(x['original_UTC_quarter'][11:13]=='23' for x in misses),
  'result_path':str(out)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=r19.SOURCES,required=True);p.add_argument('--month',choices=r19.MONTHS,required=True)
 a=p.parse_args();print(json.dumps(run(a.source,a.month),indent=2))
