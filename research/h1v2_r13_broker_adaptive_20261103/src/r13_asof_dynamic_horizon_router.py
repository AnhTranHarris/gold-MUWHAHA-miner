"""R13 distinct broker-conditional AS-OBSERVED adaptive horizon teacher.

This is a RESEARCH oracle: the chosen 5/15/30s horizon is fixed using prefix
source-only spread/ordered Bid/Ask geometry BEFORE the outcome, BUT the BUY/SELL
side and entry are still selected using FUTURE outcomes. It is NOT a causal
trade policy and no 30s favorable case is relabeled ORIGINAL 15s strict GOOD.

Within the ~1-hour tri-feed source test, spread and microtrend vary by feed.
Rule pre-registered independent of future labels:
- 5s when past BOTH-side displacement over 3s >= 2*(entry spread+.12)
- 30s when current spread >= $1.50 and <= 90% its prior 300s EMA,
- otherwise 15s.

All cases retain complete observed coverage and $0.10 opening-liq adverse veto
THROUGH 30s; actual executable ASK/BID and nominal $.02 cost. Position
occupancy is first favorable quote EXIT, so future optimal selection distinct.
"""
from __future__ import annotations
import csv,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import r13_crossbroker_horizon_lanes as r


def dynamic_prefix_choice(spread,ema300,mb3,ma3):
 motion=np.minimum(np.abs(mb3.astype(np.int64)),np.abs(ma3.astype(np.int64)))
 fast=motion>=2*(spread.astype(np.int64)+120)
 recovering=(spread>=1500)&(spread<=.90*ema300)
 return np.where(fast,5000,np.where(recovering,30000,15000)).astype(np.int32)


def run_one(name):
 p=r.OUT/f'R13_{name}_ALL_ASOF_CANDIDATES_AND_SEPARATE_HORIZON_LABELS.npz'
 with np.load(p,allow_pickle=False) as v:data={k:v[k].copy() for k in v.files}
 t,b,a,pin=r.load_source(name)
 ix=data['source_quote_ordinal'];bit=data['asof_clock_bits']
 assert np.array_equal(t[ix],data['entry_utc_ms'])
 assert np.array_equal(b[ix],data['entry_bid_raw'])
 assert np.array_equal(a[ix],data['entry_ask_raw'])
 spread=(a[ix]-b[ix]);ema=data['past_300s_spread_ema_raw']
 h=dynamic_prefix_choice(spread,ema,data['past_bid_move_3s_raw'],data['past_ask_move_3s_raw'])
 # No hidden future in h: separate arrays contain only current spread and past
 # fully observed quote revisions. Side, goodness and scheduling use future!
 eligible=(bit&3)!=0
 selectedmask=np.zeros(len(ix),bool);selected_side=np.zeros(len(ix),np.int8)
 for horizon in r.HORIZONS:
  mask=(h==horizon)&eligible
  buy=data[f'h{horizon}_future_good_BUY'];sell=data[f'h{horizon}_future_good_SELL']
  assert not np.any(buy&sell)
  selectedmask|=mask&(buy|sell)
  selected_side[mask&(buy|sell)]=np.where(buy[mask&(buy|sell)],1,-1)
 good=np.flatnonzero(selectedmask);side=selected_side[good]
 # Offline first observed liquidation exit, one position. Each individual
 # effective h locked earlier from past, BEFORE future labels are inspected.
 exit_ix=np.full(len(good),-1,np.int64);exit_ms=np.full(len(good),-1,np.int64)
 for horizon in r.HORIZONS:
  take=np.flatnonzero(h[good]==horizon)
  if not len(take):continue
  jj,tt=r.first_tp(t,b,a,ix[good[take]],side[take],horizon)
  exit_ix[take]=jj;exit_ms[take]=tt
 assert np.all(exit_ix>=0) and np.all(exit_ms>t[ix[good]])
 sel=r.exact_interval_schedule(t[ix[good]],exit_ms)
 candidates=good[sel];source_ix=ix[candidates];exits=exit_ix[sel];ts=t[source_ix]
 orig_strict=np.where(side[sel]>0,data['h15000_future_good_BUY'][candidates],data['h15000_future_good_SELL'][candidates])
 net=(np.where(side[sel]>0,b[exits]-a[source_ix],b[source_ix]-a[exits])-r.FEE)
 assert np.all(net>=100)
 if len(ts)>1: assert np.all(ts[1:]>t[exits[:-1]])
 rows=[];qrows=[];qref=(28,27,25,24)
 for k,i in enumerate(source_ix):
  rows.append({'source':name,'entry_source_quote_ordinal':int(i),'exit_source_quote_ordinal':int(exits[k]),
   'entry_UTC_ms':int(t[i]),'exit_UTC_ms':int(t[exits[k]]),
   'horizon_source_only_asof_ms':int(h[candidates[k]]),
   'side_future_selected':int(side[sel[k]]),'entry_bid_raw':int(b[i]),'entry_ask_raw':int(a[i]),
   'exit_bid_raw':int(b[exits[k]]),'exit_ask_raw':int(a[exits[k]]),
   'entry_spread_raw':int(a[i]-b[i]),'source_price_path_net_after_0p02_fee_raw':int(net[k]),
   'satisfies_original_first15_safe_full30':bool(orig_strict[k]),
   'entry_asof_horizon_but_side_and_time_future_omniscient':True})
 for q in range(4):
  start=r.T0+q*900000
  qsel=(ts>=start)&(ts<start+900000)
  qn=int(qsel.sum());qs=int(orig_strict[qsel].sum())
  qrows.append({'source':name,'quarter_UTC':__import__('datetime').datetime.fromtimestamp(start/1000,__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
   'r9_SYNTH_exact_source_quarter_ref':qref[q],
   'oracle_firstTP_multi_horizon_selected':qn,'of_those_original_strict_15s':qs,
   'original_strict_15s_fraction_of_selected':(qs/qn if qn else None),
   'multi_horizon_quarter_count_met':bool(qn>=qref[q]),
   'original_strict_count_meets_quarter_ref':bool(qs>=qref[q]),
   'H5_count':int(np.count_nonzero(qsel&(h[candidates]==5000))),
   'H15_count':int(np.count_nonzero(qsel&(h[candidates]==15000))),
   'H30_count':int(np.count_nonzero(qsel&(h[candidates]==30000))),
   'selection_future_omniscient_not_PNL_or_realtime':True})
 stem=f'R13_{name}_ADAPTIVE_ASOF_HORIZON_V1'
 r.write_csv(r.OUT/(stem+'_ALL_TRADE_ORDINALS.csv'),rows)
 r.write_csv(r.OUT/(stem+'_ALL_FOUR_QUARTERS.csv'),qrows)
 np.savez_compressed(r.OUT/(stem+'_ALL_PAST_DECISION_HORIZONS_AND_FUTURE_LABELS.npz'),
  candidate_source_ordinal=ix,candidate_source_ms=t[ix],asof_chosen_horizon_ms=h,
  source_eligible=eligible,source_future_strict_candidate=selectedmask,
  accepted_future_selected_candidate_row=candidates,source_future_selected_side=side[sel],
  source_future_selected_exit_quote_ordinal=exits,original_strict15_at_selected=orig_strict)
 receipt={'source':name,'source_sha256':pin,'full_candidate_past_horizon_count':len(ix),
  'asof_horizon_5_count':int((h==5000).sum()),'asof_horizon_15_count':int((h==15000).sum()),
  'asof_horizon_30_count':int((h==30000).sum()),'future_good_h_selected_candidates':len(good),
  'future_omniscient_nonoverlap_count':len(sel),'strict_original_first15_selected':int(orig_strict.sum()),
  'original_first15_rate_under_adaptive_horizon_teacher':float(orig_strict.mean()),
  'four_quarters':qrows,'not_causal_or_live':True}
 (r.OUT/(stem+'_COMPLETE_RECEIPT.json')).write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 return receipt

if __name__=='__main__':
 for source in r.EXPECTED:
  rec=run_one(source)
  print(json.dumps({k:v for k,v in rec.items() if k!='four_quarters'},indent=2),flush=True)
