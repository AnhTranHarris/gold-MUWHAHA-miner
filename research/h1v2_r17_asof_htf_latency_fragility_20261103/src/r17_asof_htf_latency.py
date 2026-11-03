"""R17: add-only experimental cross-scale as-of geometry and latency fragility.

Strictly diagnostic. Its input signals are original R16 future-informed schedules,
so selecting/trading them is NOT a prospective model. Source raw quotes, side,
position occupancy, fee and original 15s favorable/30s no-adverse are unchanged.

R17 may *diagnose* prior state as an independent causal feature contract;
future R16 labels are never a feature. 100ms delayed replays are counterfactual
fragility measurements of an already future-informed signal universe.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data'); LAB=ROOT/'h1v2_r17_multiscale_latency'
R16_ROOT=ROOT/'h1v2_r16_broker_adaptive';sys.path.insert(0,str(R16_ROOT/'src'))
import r16_fullcalendar_broker_adaptive as r16
from r16_source_delayed_fills import freeze_delayed_oneposition
HORIZONS=(900_000,3_600_000,14_400_000)
LANES=('BASE_250_1500','DENSE_1500','WIDE_REQUOTE_4000','BUDGETED_MULTI_REGIME','FULL_WIDE_DENSE_DIAGNOSTIC')
GATES=('ALL_FUTURE_SELECTED_CONTROL','ORIGINAL_SPREAD_1500','CURRENT_SPREAD_LE_300S_EMA',
       'SPREAD_RELIEF_080_AND_3S_FLOW','HTF_15M_1H_SIDE_ALIGNED',
       'HTF_15M_1H_4H_SIDE_ALIGNED','BROKER_ADAPTIVE_HTF_COST_GATE',
       'HTF_ALIGNED_AND_ORIGINAL_SPREAD')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()

def htf_asof_features(t,b,a,ordinals,side):
 """All price anchors are at or BEFORE the decision-minus-horizon cutoff.

 Returns ordinal and age for each anchor; -1 means insufficient historical data.
 Nothing may inspect a quote ordinal > current ordinal, including same-ms.
 Bid/ask sum is used as 2x-midpoint, no invented mid-price execution.
 """
 assert np.all(np.diff(t)>=0) and len(ordinals)==len(side)
 if len(ordinals):assert int(ordinals.min())>=0 and int(ordinals.max())<len(t)
 now=t[ordinals];mid=b.astype(np.int64)+a.astype(np.int64)
 features={}
 for h,name in zip(HORIZONS,('15m','1h','4h')):
  cutoff=now-h
  anchor=np.searchsorted(t,cutoff,side='right').astype(np.int64)-1
  anchor=np.minimum(anchor,ordinals-1)
  valid=(anchor>=0)
  stored=np.maximum(anchor,0)
  age=np.where(valid,cutoff-t[stored],-1)
  signed=np.where(valid,side.astype(np.int64)*(mid[ordinals]-mid[stored]),-2**40)
  if np.any(valid & (t[stored]>cutoff)):raise AssertionError('FUTURE_ANCHOR_LEAK')
  features[f'anchor_{name}_ordinal']=anchor
  features[f'anchor_{name}_age_ms']=age
  features[f'side_signed_mid2_{name}_raw']=signed
  features[f'has_asof_{name}']=valid
  features[f'side_aligned_{name}']=valid&(signed>0)&(age<=h)
 return features

def asof_gate_masks(spread,ema15,ema300,mb3,ma3,side,htf):
 # Fails closed on NaN/invalid historical states; no outcome used here.
 valid=(spread>=0)&np.isfinite(ema15)&np.isfinite(ema300)&(ema300>0)
 relief=valid&(spread<=0.8*ema300)&(ema15<=ema300)
 three=(np.sign(mb3)==side)&(np.sign(ma3)==side)&(np.minimum(abs(mb3),abs(ma3))>=spread+120)
 h15=htf['side_aligned_15m']; h1=htf['side_aligned_1h'];h4=htf['side_aligned_4h']
 return dict(zip(GATES,(
  valid,valid&(spread<=1500),valid&(spread<=ema300),relief&three,
  valid&h15&h1,valid&h15&h1&h4,
  valid&((spread<=1500)|((spread<=4000)&relief&three&h15&h1)),
  valid&(spread<=1500)&h15&h1&h4
 )))

def run(mon):
 out=LAB/'results';out.mkdir(parents=True,exist_ok=True)
 raw=ROOT/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
 if sha(raw)!=r16.RAW_PINS[mon]:raise RuntimeError('RAW_SHA_DRIFT')
 t,b,a=r16.tp.read_raw(mon)
 qrows,hrows,qkeys,qref,href=r16.read_refs(mon)
 allgood=R16_ROOT/'results'/f'R16_{mon}_ALL_SOURCE_ORIGINAL_AND_EXPANDED_QUOTE_GOOD_FIRSTTP.npz'
 selected=R16_ROOT/'results'/f'R16_{mon}_ALL_LANE_SELECTED_ENTRY_EXIT_ORDINALS.npz'
 sourcepins={'raw':sha(raw),'r16_future_good':sha(allgood),'r16_original_selected':sha(selected)}
 with np.load(allgood,allow_pickle=False) as g:
  ix=g['source_ordinal'].copy();side=g['side_buy1_sellminus1'].copy()
  em15=g['past_spread_ema15'].copy();em300=g['past_spread_ema300'].copy()
  mb3=g['past_bid3s_move_raw'].copy();ma3=g['past_ask3s_move_raw'].copy()
 with np.load(selected,allow_pickle=False) as sel:
  sels={l:sel[l+'_good_ordinal_index'].copy() for l in LANES}
 quarter_rows=[]; group_rows=[];full={}
 for lane,ind in sels.items():
  si=ix[ind];ss=side[ind]
  if np.any(np.diff(t[si])<=0):raise AssertionError('NONCHRONOLOGICAL_HINDSIGHT_SIGNALS')
  st=r16.RAW_PINS[mon]
  sp=(a[si]-b[si]).astype(np.int32)
  htf=htf_asof_features(t,b,a,si,ss)
  gates=asof_gate_masks(sp,em15[ind],em300[ind],mb3[ind],ma3[ind],ss,htf)
  actual=R16_ROOT/'results'/f'R16_{mon}_{lane}_lag100_slip0_FULL_FROZEN_TICK_OUTCOME.npz'
  with np.load(actual,allow_pickle=False) as z:
   if not np.array_equal(z['source_signal_tick_ordinal'],si):raise RuntimeError('R16_FROZEN_SOURCE_MISMATCH')
   if not np.array_equal(z['source_signal_side'],ss):raise RuntimeError('R16_SIDE_PARITY')
   frozen=z['outcome_code_good1_bad0_rejectminus1_busym2_censm3'].copy()
  sourcepins[lane+'_100ms_frozen_input']=sha(actual)
  cap=1500 if lane in ('BASE_250_1500','DENSE_1500') else 4000
  for gate,mask in gates.items():
   # Mask is determined entirely by prefix and current quote. This is
   # a sensitivity intervention on a FUTURE-SELECTED source signal list.
   fi=si[mask];fs=ss[mask]
   res,fills,exits,net=freeze_delayed_oneposition(t,b,a,fi,fs,100,0,cap)
   cgood=int(np.count_nonzero(res==1));cbad=int(np.count_nonzero(res==0));
   crej=int(np.count_nonzero(res==-1));cbusy=int(np.count_nonzero(res==-2));ccens=int(np.count_nonzero(res==-3))
   if cgood+cbad+crej+cbusy+ccens!=len(fi):raise AssertionError('MISSING_OUTCOME')
   completed=cgood+cbad
   qcount=np.zeros(len(qkeys),np.int32);qgood=np.zeros(len(qkeys),np.int32)
   for code,target in ((1,qgood),(0,qcount)):
    hit=np.flatnonzero(res==code)
    if len(hit):
     bins=(t[fills[hit]]//900000-qkeys[0]).astype(np.int64)
     if np.any((bins<0)|(bins>=len(qkeys))):raise AssertionError('QUARTER_RANGE')
     target[:]=np.bincount(bins,minlength=len(qkeys))
   qcount+=qgood
   # Quarter success uses completed strict accuracy and actual filled count;
   # never count a rejected/censored/busy signal as a successful trade.
   cut=np.divide(qgood,qcount,out=np.zeros(len(qcount),np.float64),where=qcount>0)
   goodq=(qref>0)&(qcount>=qref)&(cut>=0.8)
   for q,row in enumerate(qrows):
    quarter_rows.append({'month':'2026-'+mon,'lane':lane,'asof_gate':gate,'utc_quarter':row['utc_quarter'],
      'original_R9_SYNTH_15min_quota':int(qref[q]),'actual_filled_in_quarter':int(qcount[q]),
      'actual_strict_good_in_quarter':int(qgood[q]),'completed_precision':None if qcount[q]==0 else float(cut[q]),
      'joint_quota_and_80pct':int(goodq[q]) if qref[q]>0 else '',
      'hindsight_signal_origin_not_predictive':True})
   hvol=qcount.reshape(-1,4).sum(axis=1);hgood=qgood.reshape(-1,4).sum(axis=1)
   hp=np.divide(hgood,hvol,out=np.zeros(len(hvol),np.float64),where=hvol>0)
   gh=(href>0)&(hvol>=href)&(hp>=.8)
   group_rows.append({'month':'2026-'+mon,'lane':lane,'asof_gate':gate,
     'original_future_selected_signals':len(si),'asof_gate_admitted':int(mask.sum()),
     'original_frozen_r16_100ms_good':int(np.count_nonzero(frozen==1)),
     'selected_filtered_100ms_good':cgood,'selected_filtered_100ms_bad':cbad,
     'selected_filtered_quote_reject':crej,'selected_filtered_busy_skip':cbusy,
     'selected_filtered_censored':ccens,
     'completed_precision':None if not completed else cgood/completed,
     'joint_quarters_with_80pct_and_reference':int(goodq.sum()),
     'source_active_quarters':int((qref>0).sum()),
     'joint_hours_with_80pct_and_reference':int(gh.sum()),
     'source_active_hours':int((href>0).sum()),
     'not_cross_broker_NOR_causal_student':True})
   full[lane+'__'+gate+'__original_source_quote_ordinal']=fi
   full[lane+'__'+gate+'__source_side_buy1_sellminus1']=fs
   full[lane+'__'+gate+'__replayed_100ms_status']=res
   full[lane+'__'+gate+'__filled_source_quote_ordinal']=fills
   full[lane+'__'+gate+'__exit_source_quote_ordinal']=exits
  # ALL source signals, as-of features and untouched 100ms R16 result.
  full[lane+'__ALL_source_quote_ordinal']=si
  full[lane+'__ALL_side']=ss
  full[lane+'__ALL_spread_raw']=sp
  full[lane+'__ALL_past_ema15_raw']=em15[ind]
  full[lane+'__ALL_past_ema300_raw']=em300[ind]
  full[lane+'__ALL_past_bid3s_move_raw']=mb3[ind]
  full[lane+'__ALL_past_ask3s_move_raw']=ma3[ind]
  full[lane+'__ALL_original_R16_100ms_frozen_status']=frozen
  for key,vals in htf.items():full[lane+'__ALL_'+key]=vals
 # Print/store complete no-omission rows, 4 months done in atomic stages.
 csvp=out/f'R17_{mon}_FULL_{len(group_rows)}_MECHANISM_FALSIFICATION.csv'
 with csvp.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(group_rows[0]));w.writeheader();w.writerows(group_rows)
 qcsv=out/f'R17_{mon}_ALL_{len(quarter_rows)}_ORIGINAL_QUARTER_OUTCOMES.csv'
 with qcsv.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(quarter_rows[0]));w.writeheader();w.writerows(quarter_rows)
 npzp=out/f'R17_{mon}_ALL_HINDSIGHT_ORIGINAL_QUOTE_ORDINAL_AND_ASOF_MTF_STRESS.npz'
 np.savez_compressed(npzp,**full)
 rec={'month':mon,'source_geometry':'original_DUKASCOPY_only','original_R9_SYNTH_quarters':len(qrows),
  'source_active_quarters':int((qref>0).sum()),'full_mechanism_records':len(group_rows),
  'full_quarter_records':len(quarter_rows),'source_pins':sourcepins,
  'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (csvp,qcsv,npzp)},
  'source_future_selected_signals':True,'new_asof_features_use_only_quote_ordinals_at_or_before_entry':True,
  'R16_EA_still_untouched':True,'no_coinexx_full_fourmonth_source':True,
  'status':'FROZEN_FUTURE_ORACLE_DIAGNOSTIC_ONLY_NOT_QUALIFIED_AS_CAUSAL_OR_PROFITABLE'}
 receipt=out/f'R17_{mon}_EXACT_SOURCE_AND_REPLAY_RECEIPT.json';receipt.write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'month':mon,'groups':len(group_rows),'quarters':len(quarter_rows),'receipt':str(receipt)}),flush=True)
 return rec
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--month',required=True,choices=['01','02','06','07']);run(ap.parse_args().month)
