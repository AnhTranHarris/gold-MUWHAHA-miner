#!/usr/bin/env python3
"""R12C-Q V2: all three independent feeds x 54 stress scenarios x 4 exact
source-R9-SYNTH UTC 15-minute quota buckets. Full frozen source-ordinal traces.

Additive research after frozen R12C V1 archive; never edit original 54-scenario
results, original R12/R11 sources, or synthetic R9 reference. V2 recomputes
all scenarios exactly, checks V1 totals, derives ALL quarters from ORIGINAL
source trade-entry timestamps (not hourly count/4). No causal prediction.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,sys
from pathlib import Path
import numpy as np
from r12c_latency_and_execution_stress import (load_source,sha256,freeze_delayed_signal_replay,
          TARGET_START,TARGET_END,EXPECTED_SOURCE_SHA,H15,H30)


def run(sources,refpath,engine_dir,priorcsv,outdir):
 sys.path.insert(0,str(engine_dir))
 from r12_dense_requote import asof_quote_clocks,_rolling_extrema
 from r12_tp_oracle import quote_tp_first,earliest_finish_schedule
 outdir.mkdir(parents=True,exist_ok=True)
 allref=list(csv.DictReader(refpath.open(newline='')))
 qrefs=[r for r in allref if r['utc_hour']=='2026-02-02T06:00:00Z']
 assert len(qrefs)==4,(len(qrefs),refpath)
 keys=[r['utc_quarter'] for r in qrefs]
 assert keys==['2026-02-02T06:00:00Z','2026-02-02T06:15:00Z','2026-02-02T06:30:00Z','2026-02-02T06:45:00Z']
 quotas=[int(r['R9_SYNTH_exact_15min_reference']) for r in qrefs]
 assert quotas==[28,27,25,24] and sum(quotas)==104
 prior=list(csv.DictReader(priorcsv.open(newline='')))
 assert len(prior)==54
 ledger={(r['source'],int(r['latency_nominal_ms']),int(r['entry_and_exit_each_slip_raw_usd_0p001'])):r for r in prior}
 rows=[];hour_records=[];allsource=[]
 for source,path in sources.items():
  t,b,a,pin=load_source(path,source)
  ix,flags=asof_quote_clocks(t,b,a)
  ix=ix[(t[ix]>=TARGET_START)&(t[ix]<TARGET_END)&((flags&1)!=0)]
  mn15,mx15,ma15,xa15,_,_,cover15=_rolling_extrema(t,b,a,ix,15000)
  mn30,mx30,ma30,xa30,_,_,cover30=_rolling_extrema(t,b,a,ix,30000)
  buy=(mx15.astype(np.int64)>=a[ix].astype(np.int64)+120)&(mn30.astype(np.int64)>b[ix].astype(np.int64)-100)&cover15&cover30
  sell=(ma15.astype(np.int64)<=b[ix].astype(np.int64)-120)&(xa30.astype(np.int64)<a[ix].astype(np.int64)+100)&cover15&cover30
  assert not np.any(buy&sell)
  ixgood=ix[buy|sell];side=np.where(buy[buy|sell],1,-1).astype(np.int8)
  tp,exitt=quote_tp_first(t,b,a,ixgood,a[ixgood],b[ixgood],side)
  selection=earliest_finish_schedule(t[ixgood],exitt)
  sig=ixgood[selection];sides=side[selection]
  assert len(sig)=={'R9_REAL_MT5_TESTER':705,'R9_SYNTH_MT5_TESTER':1853,'DUKASCOPY_RAW':6}[source]
  allsource.append({'source':source,'sha256':pin,'frozen_source_good_signal_count':len(sig),'original_reference':104})
  for lag in (0,50,100,250,500,1000):
   for slip in (0,20,50):
    out,fill,ex,nets=freeze_delayed_signal_replay(t,b,a,sig,sides,lag,slip)
    rec=ledger[(source,lag,slip)]
    assert int((out==1).sum())==int(rec['good_first15_and_safe_full30_at_delayed_quote'])
    assert int((out==0).sum())==int(rec['failed_after_fill'])
    assert int((out==-1).sum())==int(rec['quote_reject'])
    assert int((out==-2).sum())==int(rec['busy_after_other_stressed_fill'])
    assert int((out==-3).sum())==int(rec['source_censored_after_fill'])
    npz=outdir/f'R12C_Q_FULL_SOURCE_{source}_lag{lag}_slip{slip}_ALL_SIGNAL_OUTCOMES.npz'
    np.savez_compressed(npz,signal_utc_ms=t[sig],signal_quote_ordinals=sig,signal_side=sides,
        delayed_fill_quote_ordinals=fill,delayed_exit_quote_ordinals=ex,
        outcome_code=out,modeled_net_raw_ONLY_WHEN_STRICT_GOOD=nets)
    source_signal_bucket=(t[sig]-TARGET_START)//900000
    source_fill_bucket=np.full(len(fill),-1,np.int64)
    valid=fill>=0;source_fill_bucket[valid]=(t[fill[valid]]-TARGET_START)//900000
    for k,key in enumerate(keys):
     signal_sel=(source_signal_bucket==k)
     fill_sel=(source_fill_bucket==k)
     g=int(np.sum(fill_sel & (out==1)))
     bad=int(np.sum(fill_sel & (out==0)))
     cens=int(np.sum(fill_sel & (out==-3)))
     req=int(quotas[k]);den=g+bad
     rows.append({'source':source,'utc_quarter':key,'original_R9_SYNTH_source_15m_reference':req,
      'quarter_index':k,'latency_ms':lag,'entry_exit_extra_slippage_each_raw_0p001':slip,
      'roundtrip_extra_slippage_usd':2*slip/1000,
      'frozen_hindsight_source_signals_in_quarter':int(signal_sel.sum()),
      'good_delayed_execution_fills_in_quarter':g,
      'completed_bad_delayed_execution_fills_in_quarter':bad,
      'source_censored_fills_in_quarter':cens,
      'source_no_quote_reject_at_signal_in_quarter':int(np.sum(signal_sel&(out==-1))),
      'one_position_busy_dropped_signal_in_quarter':int(np.sum(signal_sel&(out==-2))),
      'strict_precision_completed_fills_in_quarter':g/den if den else '',
      'strict_80pct_precision_completed_fills_in_quarter':int(g/den>=.8) if den else '',
      'exact_R9_quarter_volume_parity_correct_delayed_fills':int(g>=req),
      'joint_15min_80precision_and_100pct_count':int(g>=req and den>0 and g/den>=.8),
      'nondeployable_future_selected_signal':1,'fee_usd':0.02,
      'true_live_broker_order_fill_proven':0})
    hour_records.append({'source':source,'lag':lag,'slip_each_0p001':slip,
      'exact_original_104_R9_hour_reference':104,
      'good_delayed_fill_total':int((out==1).sum()),
      'quarter_good_sum':sum(r['good_delayed_execution_fills_in_quarter'] for r in rows[-4:]),
      'hour_volume_correct':int((out==1).sum()>=104),
      'quarters_meet_exact_source_target':sum(int(r['exact_R9_quarter_volume_parity_correct_delayed_fills']) for r in rows[-4:]),
      'quarters_joint_volume_and_80pct_precision':sum(int(r['joint_15min_80precision_and_100pct_count']) for r in rows[-4:])})
    assert int((out==1).sum())==sum(r['good_delayed_execution_fills_in_quarter'] for r in rows[-4:]),('fill outside quarter',source,lag,slip)
 def writecsv(p,rr):
  with p.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 writecsv(outdir/'R12C_Q_ALL_216_QUARTER_SOURCE_EXACT_LATENCY_AND_PRECISION.csv',rows)
 writecsv(outdir/'R12C_Q_ALL_54_HOURLY_FULL_STRESS_RECONCILED.csv',hour_records)
 receipt={'source_R9_SYNTH_exact_quarter_reference':dict(zip(keys,quotas)),'calendar_source_15min_rows':len(rows),
   'hours_source_rows':len(hour_records),'source_verification':allsource,
   'source_R9_quarter_ledger_full_original':str(refpath),'original_v1_54_receipt_sha256':sha256(priorcsv),
   'scientific_status':'FROZEN_HINDSIGHT_SIGNAL_STRESS_NOT_CAUSAL_OR_REAL_FILL',
   'no_source_substitution':True,'no_overlapping_reexecuted_entries':True,
   'complete_signal_quote_trace_count':len(list(outdir.glob('R12C_Q_FULL_SOURCE*.npz'))),
   'no_runtime_model_qualified':True}
 (outdir/'R12C_Q_ATOMIC_SOURCE_15MIN_RECONCILIATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 manifest={p.name:{'bytes':p.stat().st_size,'sha256':sha256(p)} for p in sorted(outdir.iterdir()) if p.is_file() and p.name!='R12C_Q_ALL_OUTPUT_MANIFEST.json'}
 (outdir/'R12C_Q_ALL_OUTPUT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return receipt

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['real','synth','dukas','quarter-reference','engine-dir','prior-scenarios','out']:p.add_argument('--'+n,required=True)
 x=p.parse_args();rec=run({'R9_REAL_MT5_TESTER':Path(x.real),'R9_SYNTH_MT5_TESTER':Path(x.synth),'DUKASCOPY_RAW':Path(x.dukas)},Path(x.quarter_reference),Path(x.engine_dir),Path(x.prior_scenarios),Path(x.out));print(json.dumps(rec,indent=2))
