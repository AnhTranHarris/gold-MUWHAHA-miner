"""R19 two-source multi-clock hindsight-schedule UNION delayed-fill capacity lab.

SCIENTIFIC LIMIT: the R18 lanes and their sides were selected using FUTURE
quotes. Re-combining historically selected schedules, scoring delayed executable
first passage, and packing only hindsight GOOD intervals is NOT a runtime
BUY/SELL prediction. Never publish this as an 80%-accuracy causal strategy.

Distinct from R18-S2: tests 10 independent archived R18 60s source lane
schedules' UNION vs the original single R18 adaptive-union preselection.
Retains NEW_FIRST_TOUCH_60_BEFORE_ADVERSE, not original S1 15F/SAFE30.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,datetime as dt
from pathlib import Path
import numpy as np

LAB=Path('/mnt/data/h1v2_r18_dualbroker')
ROOT=Path('/mnt/data')
OUT=Path('/mnt/data/h1v2_r19_broker_union/results_v2')
sys.path.insert(0,str(LAB/'src'))
import r18_broker_multihorizon as r18
from r18_frozen_latency_economic_stress import get_frozen,GOOD,STOP,TIMEOUT,CENSOR,REJECT
from r18_s2_latency_frontier import independent_delayed_firsttouch,pack_future_good

CONTRACT='NEW_FIRST_TOUCH_60_BEFORE_ADVERSE'
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
MONTHS=('01','02','06','07')
LAGS=(100,500)
SLIPS=(0,20)
CAPS=(1500,2500,4000)


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()


def verify_unique_union(ordinals,sides,lanebits,source_quote_count):
 """Collapse duplicate time-ordinal entries; never let duplicate lanes inflate count."""
 if not len(ordinals):raise ValueError('NO_SOURCE_PRESELECTIONS')
 order=np.argsort(ordinals,kind='stable')
 x=ordinals[order].astype(np.int32);side=sides[order].astype(np.int8);bits=lanebits[order].astype(np.uint16)
 u,starts=np.unique(x,return_index=True)
 if np.any(u<0) or np.any(u>=source_quote_count):raise ValueError('SOURCE_QUOTE_ORD_OUTSIDE_ORIGINAL')
 lows=np.minimum.reduceat(side,starts);highs=np.maximum.reduceat(side,starts)
 if np.any(lows!=highs) or np.any((lows!=1)&(lows!=-1)):raise ValueError('FUTURE_SELECTED_SIDE_COLLISION')
 masks=np.bitwise_or.reduceat(bits,starts)
 return u,lows,masks


def read_unions(src,mon,t,b,a,original_signal,original_side):
 """R18 immutable lane selected ordinals are prechosen under *same* 60s contract."""
 tag=f'R18_{src}_{mon}'
 p=LAB/'results'/f'{tag}_LOSSLESS_SELECTED_ORIGINAL_QUOTE_ORDINALS.npz'
 if not p.exists():raise FileNotFoundError(p)
 arr=[];sides=[];bit=[];counts={}
 with np.load(p,allow_pickle=False) as z:
  for k,lane in enumerate(r18.LANES):
   head=lane+'__'+CONTRACT
   ix=z[head+'_entry_ord'].astype(np.int32)
   side=z[head+'_side_FUTURE_SELECTED'].astype(np.int8)
   exit_idx=z[head+'_firstTP_exit_ord'].astype(np.int32)
   assert len(ix)==len(side)==len(exit_idx)
   assert np.all(exit_idx>ix)
   counts[lane]=int(len(ix))
   if src=='MT5_BROKER_EXPORT' and mon=='06':
    pt=LAB/'results_r18_JUNE_TAIL_PATCH'/'R18_JUNE_MT5_HALO_FULL_50_SOURCE_QUOTE_ORDINAL_TAIL_SETS.npz'
    with np.load(pt,allow_pickle=False) as zz:
     extra_ix=zz[head+'_stitched_entry_ord'].astype(np.int32)
     extra_side=zz[head+'_future_selected_side'].astype(np.int8)
     extra_exit=zz[head+'_stitched_exit_ord'].astype(np.int32)
    if len(extra_ix):
     if np.any(extra_exit<=extra_ix):raise ValueError('TAIL_EXIT_INVALID')
     ix=np.r_[ix,extra_ix];side=np.r_[side,extra_side]
    counts[lane]=int(len(ix))
   arr.append(ix);sides.append(side);bit.append(np.full(len(ix),1<<k,np.uint16))
 u,s,masks=verify_unique_union(np.concatenate(arr),np.concatenate(sides),np.concatenate(bit),len(t))
 # All baseline source signal indices must exist in union with exact same side.
 off=np.searchsorted(u,original_signal)
 if np.any(off>=len(u)) or not np.array_equal(u[off],original_signal) or not np.array_equal(s[off],original_side):
  raise ValueError('ORIGINAL_R18_SINGLE_ROUTER_NOT_SUBSET_OF_UNION')
 original_spread=a[u].astype(np.int64)-b[u].astype(np.int64)
 mask4000=original_spread<=4000
 return u,s,masks,mask4000,counts,sha(p)


def prepare_delayed(t,b,a,qkeys,signals,sides,lag,slip):
 """Run expensive source-exact delayed first passage only once per lag and slip."""
 expected=t[signals]+lag
 allfill=np.searchsorted(t,expected,side='left').astype(np.int32)
 fi=np.clip(allfill,0,len(t)-1)
 start=int(qkeys[0]*900000);end=int((qkeys[-1]+1)*900000)
 valid=(allfill<len(t))&(fi>signals)&(t[fi]>t[signals])&((t[fi]-expected)<=1000)
 valid&=(t[fi]>=start)&(t[fi]<end)
 sp=(a[fi].astype(np.int64)-b[fi].astype(np.int64))
 valid&=(sp>=0)&(sp<=4000)
 fill=np.where(valid,fi,-1).astype(np.int32)
 state,exit_idx,net=independent_delayed_firsttouch(t,b,a,signals,sides,fill,slip)
 return fill,sp,state,exit_idx,net


def report_one(src,mon,lag,slip,cap,t,b,a,qkeys,qref,href,signals,sides,mask4000,unionbits,cached=None):
 fill,sp,state,exit_idx,net=prepare_delayed(t,b,a,qkeys,signals,sides,lag,slip) if cached is None else cached
 choose=(state==GOOD)&(sp<=cap)&mask4000
 idx=pack_future_good(t,fill,exit_idx,choose)
 chosen_fill=fill[idx]
 vals=net[idx]
 if not np.all(vals>=100):raise RuntimeError('FALSE_POSITIVE_SOURCE_EXECUTABLE_NET')
 if len(idx)>1 and np.any(t[chosen_fill[1:]]<=t[exit_idx[idx[:-1]]]):raise RuntimeError('ONE_POSITION_CONFLICT')
 qcounts=np.bincount(t[chosen_fill]//900000-qkeys[0],minlength=len(qref)).astype(np.int32)
 hcounts=qcounts.reshape(-1,4).sum(axis=1)
 qmeet=(qref>0)&(qcounts>=qref);hmeet=(href>0)&(hcounts>=href)
 name=f'lag{lag}_slip{slip}_fillcap{cap}'
 row={'source':src,'month':mon,'case':name,'latency_ms':lag,'per_leg_extra_slip_raw_0p001':slip,
  'actual_fill_spread_cap_raw_0p001':cap,'original_source_spread_gate_4000':True,
  'entire_r18_lane_union_source_count':len(signals),'first_quote_delayed_good_trails_repacked':len(idx),
  'eligible_frozen_delayed_good_independent':int(choose.sum()),
  'source_original_ref_trades':int(qref.sum()),'source_ref_active_quarters':int((qref>0).sum()),
  'source_ref_active_hours':int((href>0).sum()),'15m_quota_met':int(qmeet.sum()),
  'hourly_quota_met':int(hmeet.sum()),'shortfall_15m_quarters':int((qref>0).sum()-qmeet.sum()),
  'shortfall_hourly':int((href>0).sum()-hmeet.sum()),
  'quoted_price_favorable_net_raw_sum':int(vals.astype(np.int64).sum()),
  'future_selected_success_tautological':True,'not_an_asof_predictor':True,'not_broker_cash_pnl':True,
  'NOT_ORIGINAL_15F30S':True,'NO_RAW_SOURCE_PATCHES':True}
 tqs=[dt.datetime.fromtimestamp(int(q*900000)/1000,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') for q in qkeys]
 qrows=[{'source':src,'month':mon,'case':name,'utc_quarter':label,'R9_SYNTH_clock_UTC_ref':int(qref[k]),
  'future_selected_good':int(qcounts[k]),'counterfactual_source_quota_met':int(qmeet[k]) if qref[k]>0 else '',
  'missing_source_15min_slots':max(0,int(qref[k]-qcounts[k]))} for k,label in enumerate(tqs)]
 hrs=[{'source':src,'month':mon,'case':name,'utc_hour':tqs[h*4],
  'R9_SYNTH_clock_UTC_ref':int(href[h]),'future_selected_good':int(hcounts[h]),
  'counterfactual_source_quota_met':int(hmeet[h]) if href[h]>0 else '',
  'missing_source_hour_slots':max(0,int(href[h]-hcounts[h]))} for h in range(len(href))]
 trace={'source_signal_quote_ordinal':signals[idx],'original_future_selected_side':sides[idx],
  'source_lane_provenance_bitmask':unionbits[idx],
  'actual_observed_fill_quote_ordinal':chosen_fill,'first_target_exit_quote_ordinal':exit_idx[idx],
  'future_selected_nominal_bidask_net_raw':vals}
 return row,qrows,hrs,trace


def run_one(src,mon,fast=True):
 OUT.mkdir(parents=True,exist_ok=True)
 t,b,a,orig,origside,origex,prov=get_frozen(src,mon)
 r18.verify_upstreams()
 refs=r18.refs_for_month(mon,ROOT)
 u,s,bits,mask4,counts,pin=read_unions(src,mon,t,b,a,orig,origside)
 qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 if not np.array_equal(qref.reshape(-1,4).sum(axis=1),href):raise ValueError('ORIGINAL_REFERENCE_QUARTER_HOUR_MISMATCH')
 rows=[];qrows=[];hrows=[];outputs={}
 scenarios=[(100,0,4000),(100,20,4000),(500,20,4000),(100,0,2500),(100,0,1500)] if fast else [(l,s,c) for l in LAGS for s in SLIPS for c in CAPS]
 prepared={}
 for lag,slip,cap in scenarios:
  if (lag,slip) not in prepared:
   prepared[(lag,slip)]=prepare_delayed(t,b,a,qkeys,u,s,lag,slip)
  record,q,h,trace=report_one(src,mon,lag,slip,cap,t,b,a,qkeys,qref,href,u,s,mask4,bits,cached=prepared[(lag,slip)])
  rows.append(record);qrows+=q;hrows+=h
  outputs[record['case']]=trace
  print(src,mon,record['case'],'select',record['first_quote_delayed_good_trails_repacked'],'Q',record['15m_quota_met'],'/',record['source_ref_active_quarters'],'H',record['hourly_quota_met'],'/',record['source_ref_active_hours'],flush=True)
 tag=f'R19_{src}_{mon}'
 def write(path,data):
  with open(path,'w',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 result=OUT/f'{tag}_SCENARIOS.csv';quart=OUT/f'{tag}_ALL_QUARTERS.csv';hour=OUT/f'{tag}_ALL_HOURS.csv';traces=OUT/f'{tag}_EXACT_SELECTED_ORDINAL_TRACES.npz';receipt=OUT/f'{tag}_SOURCE_SHA_AND_EVIDENCE.json'
 write(result,rows);write(quart,qrows);write(hour,hrows)
 flat={f'{name}__{key}':val for name,cols in outputs.items() for key,val in cols.items()}
 np.savez_compressed(traces,**flat)
 record={'scientific_class':'FUTURE_ORACLE_UNION_BROKER_SPECIFIC_MULTICLOCK_HINDSIGHT_ONLY',
   'source':src,'month':mon,'original_source_SHA':r18.PINS[src][mon],
   'july_halo_mt5_june':prov.get('next_broker_month_sha'),
   'original_R18_source_sha':pin,'quote_count':len(t),'source_single_R18_signals':len(orig),
   'union_unique_source_frozen_signals':len(u),'unique_under_original_spread_cap4':int(mask4.sum()),
   'all_ten_source_lanes_selected_counts':counts,'ref_sha256':refs['sha256'],
   'scenarios':rows,'files':{x.name:{'size':x.stat().st_size,'sha256':sha(x)} for x in (result,quart,hour,traces)},
   'owner_accuracy_no_claim':True,'no_independent_oos_or_actual_broker_fill':True,
   'eligibility_spread_lte4_at_original_signal':True,'original_R11S1_15F30S_unmodified':True}
 receipt.write_text(json.dumps(record,indent=2)+'\n');return record

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=SOURCES,required=True)
 p.add_argument('--month',choices=MONTHS,required=True);p.add_argument('--all-scenarios',action='store_true')
 args=p.parse_args();run_one(args.source,args.month,fast=not args.all_scenarios)
