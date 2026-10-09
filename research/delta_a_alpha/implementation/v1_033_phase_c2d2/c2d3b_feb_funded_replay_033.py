"""C2D3-B continuous ORIGINAL 049->paid119->funded084 February L7 research replay.

Source-only NY 049 candidate parity is distinct from broker-idealized funding.
No claim of full original owner V1 native L1-L6 or Coinexx execution parity.
No frozen strategy/model mutation. All replay order decisions depend on past quote.
"""
from __future__ import annotations
import argparse, hashlib, json, time, sys
from collections import Counter
from pathlib import Path
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from real_dukas_event_smoke_033 import orig_completed_state_fn, load_window, EXPECTED
from v1_funded_core_033c import Quote, Structure, Limits, FundedEngine
from original_funded_lineage_033c2 import Original049FundedCapacity, Original049Settings
from original_ny049_union_033c2b import Original049NYSourceL3
from original_online_sources_033c import Original131DSessionL3
from funded_084_l7_bridge_033c2d2 import Funded084L7Bridge

SOURCE_GITHUB_HEAD='delta-A-alpha as of journal 0075; exact 12 source blobs verified in bootstrap'
SOURCE_MODEL='ORIGINAL_COMPLETED_EMA_SIGN_PROXY_NOT_OWNER_ROLE_SEPARATED_L2'


def sha256(file:Path):
 h=hashlib.sha256()
 with file.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()


def prepare(root:Path,count:int,cache:Path):
 jan=root/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz';feb=root/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
 assert sha256(jan)==EXPECTED['jan'] and sha256(feb)==EXPECTED['feb'], 'Source hash mismatch'
 def ms(s):return int(pd.Timestamp(s,tz='UTC').value//1000000)
 t0=time.monotonic()
 j=load_window(jan,ms('2026-01-22'),ms('2026-02-01'))
 f=load_window(feb,ms('2026-02-02 06:30:00'),ms('2026-02-03 19:00:00')).iloc[:count]
 z=pd.concat((j,f),ignore_index=True)
 t=z.timestamp_ms_utc.to_numpy(np.int64);a=z.ask_raw.to_numpy(np.int32);b=z.bid_raw.to_numpy(np.int32)
 assert np.all(t[1:]>=t[:-1]) and np.all(a>=b)
 assert len(f)==count,(len(f),count)
 print('DATA_READY',len(j),len(f),'seconds',round(time.monotonic()-t0,1),flush=True)
 states={};ends={};fn=orig_completed_state_fn(root/'JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip')
 for name,tf in [('h4',14400000),('h1',3600000),('m15',900000),('m5',300000)]:
  states[name]=fn(t,b,tf,8,21).astype(np.int8)
  bucket=t//tf;starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1];last=np.r_[starts[1:]-1,len(t)-1]
  prev=np.searchsorted(bucket[starts],bucket,side='left')-1
  en=np.full(len(t),-1,np.int64);ok=prev>=0;en[ok]=t[last[prev[ok]]]
  ends[name]=en
  print('COMPLETED_HISTORY_READY',name,flush=True)
 # Only immutable arrays needed for identical chronological replay.
 cache.parent.mkdir(parents=True,exist_ok=True)
 np.savez(cache, t=t[len(j):],a=a[len(j):],b=b[len(j):],
   **{name:states[name][len(j):] for name in states},
   **{name+'_end':ends[name][len(j):] for name in ends},
   january_context_ticks=np.array(len(j),dtype=np.int64))
 print('CACHE_READY',str(cache),'seconds',round(time.monotonic()-t0,1),flush=True)


class ExitAblation049(Original049NYSourceL3):
 """As-of proposal-only counterfactual; frozen 049 signal event generator is unchanged."""
 def __init__(self,quota,ttl_scale=1.,tp_scale=1.):
  super().__init__(quota); self.ttl_scale=ttl_scale;self.tp_scale=tp_scale
 def propose(self,q,s,engine):
  for p in super().propose(q,s,engine):
   yield replace(p,ttl_ms=max(1,int(round(p.ttl_ms*self.ttl_scale))),
     tp_usd=p.tp_usd*self.tp_scale)


class C2D3BL7FundingAblation(FundedEngine):
 """Controlled real L7 denials; never alters original 049 entry manufacture.

 Experiments only. An original 049 proposal is still made and considered by
 L7, but an explicitly banned funded parent receives an actual recorded L7
 denial. A delayed 084 child must resubmit and fill at a later observed quote.
 Never synthesize a past fill or treat a rejected parent as a paid sponsor.
 """
 def __init__(self, limits, adapters, *, deny_049_parents=False,
              child_after_parent_ms=0, **kwargs):
  super().__init__(limits, adapters, **kwargs)
  assert child_after_parent_ms>=0
  self.deny_049_parents=deny_049_parents
  self.child_after_parent_ms=child_after_parent_ms

 def _admission_reason(self,q,s,p):
  if (self.deny_049_parents and p.layer=='L3'
      and p.source.startswith('ORIGINAL_049_UNION_')):
   return 'AB_DENY_FUNDED_049_PARENT'
  if (self.child_after_parent_ms and p.layer=='L4'
      and p.source=='ORIGINAL_119_C2C_CHILD'):
   # child proposal owner is the 049 parent whose actually-funded window
   # generated it (the parent_id sponsor may instead be a paid prior child).
   parts=(p.source_event_key or '').split(':')
   if len(parts)<2 or parts[0]!='C2CWINDOW':
    raise AssertionError('C2D3-B child lost original paid-window identity')
   parent=int(parts[1])
   owner=self.positions.get(parent)
   if owner is None:
    return 'AB_PARENT_NOT_PHYSICALLY_OPEN'
   if q.time_ms-owner.entry_ms < self.child_after_parent_ms:
    return 'AB_DELAY_FUNDED_084_CHILD'
  return super()._admission_reason(q,s,p)


class IndependentPhysicalOracle:
 """Second account book: derives FILL/CLOSE cash and mark independently of engine.positions."""
 def __init__(self,limits:Limits):
  self.balance=limits.balance_usd;self.open={};self.peak=limits.balance_usd
  self.max_dd=0.;self.pre_max_dd=0.;self.max_orders_sec=0;self.last_second=-1;self.this_second=0
  self.close_count=0;self.mismatch_count=0;self.first_mismatches=[];self.max_positions=0
  self.fee=limits.commission_roundtrip_usd;self.size=limits.fixed_lot*limits.contract_oz_per_lot
  self.total_net=0.;self.by_layer=Counter();self.max_equity_delta=0.;self.last_post=limits.balance_usd;self.exec_trace=[]
  self.daily=Counter();self.weekly=Counter();self.daily_trades=Counter();self.weekly_trades=Counter()
 def mark(self,q):
  return self.balance + sum(( (q.bid_raw if p[1]>0 else q.ask_raw)-p[0])*p[1]*self.size/1000 for p in self.open.values())-len(self.open)*self.fee/2
 def ingest(self,q,events,engine):
  # Mirror quote mark before executable close, including delayed reduce-only queue.
  pre=self.mark(q);self.peak=max(self.peak,pre);self.max_dd=max(self.max_dd,self.peak-pre)
  sec=q.time_ms//1000
  if sec!=self.last_second:self.last_second=sec;self.this_second=0
  for e in events:
   if e['event']=='FILL':
    assert e['id'] not in self.open and e['id'] in engine._funded_ids
    self.open[e['id']]=(e['raw'],1 if e['raw']==q.ask_raw else -1,e['layer'],e.get('parent_id'))
    # A zero-spread tick could make quote-side ambiguous. The source-funded side
    # will be checked on exact engine position before marking if still live.
    if q.ask_raw==q.bid_raw and e['id'] in engine.positions:
     p=engine.positions[e['id']]; self.open[e['id']]=(e['raw'],p.side,e['layer'],e.get('parent_id'))
    self.balance-=self.fee/2;self.this_second+=1
    self.exec_trace.append({'t':q.time_ms,'event':'FILL','id':e['id'],'layer':e['layer'],
      'source':e['source'],'cell':e.get('cell'),'sponsor_id':e.get('parent_id'),
      'side':self.open[e['id']][1],'entry_raw':e['raw'],'ask_raw':q.ask_raw,'bid_raw':q.bid_raw,
      'balance_after':round(self.balance,8)})
   elif e['event']=='CLOSE':
    assert e['id'] in self.open,('unmatched_close',e)
    raw,side,layer,parent=self.open.pop(e['id']);price=q.bid_raw if side>0 else q.ask_raw
    gross=(price-raw)*side/1000*self.size
    pnl=gross-self.fee
    if abs(pnl-e['pnl'])>1e-7:self.mismatch_count+=1;self.first_mismatches.append({'id':e['id'],'reported':e['pnl'],'oracle':pnl}) if len(self.first_mismatches)<5 else None
    self.balance+=gross-self.fee/2;self.total_net+=pnl;self.by_layer[layer]+=1;self.close_count+=1;self.this_second+=1
    now=datetime.fromtimestamp(q.time_ms/1000,timezone.utc)
    day=now.strftime('%Y-%m-%d'); iso=now.isocalendar();week=f'{iso.year}-W{iso.week:02d}'
    self.daily[day]+=pnl;self.weekly[week]+=pnl;self.daily_trades[day]+=1;self.weekly_trades[week]+=1
    self.exec_trace.append({'t':q.time_ms,'event':'CLOSE','id':e['id'],'layer':layer,'sponsor_id':parent,
      'side':side,'entry_raw':raw,'exit_raw':price,'reason':e.get('reason'),'net_usd':round(pnl,8),
      'ask_raw':q.ask_raw,'bid_raw':q.bid_raw,'balance_after':round(self.balance,8)})
  assert self.this_second<=engine.limits.max_orders_per_second,('order budget',q.time_ms,self.this_second)
  self.max_orders_sec=max(self.max_orders_sec,self.this_second)
  assert len(self.open)==len(engine.positions),('book positions diverge',q.time_ms,len(self.open),len(engine.positions))
  self.max_positions=max(self.max_positions,len(self.open))
  post=self.mark(q);self.peak=max(self.peak,post);self.max_dd=max(self.max_dd,self.peak-post)
  self.max_equity_delta=max(self.max_equity_delta,abs(post-engine.equity),abs(self.balance-engine.balance))
  if abs(post-engine.equity)>1e-6 or abs(self.balance-engine.balance)>1e-6:
   self.mismatch_count+=1
   if len(self.first_mismatches)<5:self.first_mismatches.append({'t':q.time_ms,'book_equity':post,'engine_equity':engine.equity,'book_balance':self.balance,'engine_balance':engine.balance})
  self.last_post=post


def replay(cache:Path, out:Path, *, source_root:Path=Path('/mnt/data'), cap=32, spread=3., orders=4, low_surge=False, limit=None,parent_ttl_scale=1.,parent_tp_scale=1., deny_049_parents=False, child_after_parent_ms=0):
 # Original handoff: source SHA is rechecked BEFORE every simulation, not
 # merely when the ephemeral derived-state cache is initially generated.
 # A cache is an acceleration layer, never a replacement for source authority.
 jan=source_root/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
 feb=source_root/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
 actual_inputs={'jan':sha256(jan),'feb':sha256(feb)}
 assert actual_inputs==EXPECTED,('C2D3-B original raw input bytes changed',actual_inputs)
 derived_cache_sha256=sha256(cache)
 with np.load(cache,allow_pickle=False) as data:
  j=int(data['january_context_ticks']);t=data['t'];a=data['a'];b=data['b'];
  if limit is not None:t=t[:limit];a=a[:limit];b=b[:limit]
  states={n:data[n] for n in ('h4','h1','m15','m5')}
  ends={n:data[n+'_end'] for n in ('h4','h1','m15','m5')}
 assert len(t)>0 and np.all(t[1:]>=t[:-1]) and np.all(a>=b), 'derived quote cache chronology corrupted'
 assert j==3900880, ('Unexpected Jan warmup context',j)
 quota=Original049FundedCapacity(Original049Settings(base_cap=2,base_step=1,base_unit=2500.,base_max=2,initial_surge=0,surge_step=0,surge_unit=2500.,max_surge=0,hard_max=2)) if low_surge else Original049FundedCapacity()
 wd=Funded084L7Bridge();hb=ExitAblation049(quota,parent_ttl_scale,parent_tp_scale);grid=Original131DSessionL3()
 limits=Limits(max_open=cap,max_layer_open=cap,max_same_direction=cap,max_per_source_open=cap,
    max_per_cell_side=min(cap,16),max_orders_per_second=orders,max_orders_per_tick=1,
    max_underwater_open_usd=8000,max_spread_usd=spread)
 eng=C2D3BL7FundingAblation(limits,[hb,grid,wd],broker_contract_verified=True,
    deny_049_parents=deny_049_parents,child_after_parent_ms=child_after_parent_ms)
 oracle=IndependentPhysicalOracle(limits)
 t0=time.monotonic();ev_cursor=0;N=len(t)
 for i in range(N):
  tm=int(t[i]);q=Quote(tm,int(a[i]),int(b[i]));be=tuple(int(ends[k][i]) for k in ('h4','h1','m15','m5'))
  s=Structure('DIAGNOSTIC',*(int(states[k][i]) for k in ('h4','h1','m15','m5')),
     max(be),f'GRID:{tm//600000}',(tm//600000)%6,be) if all(x>0 for x in be) else None
  # Equity oracle reconstructs marks strictly from independently accounted actual fills.
  eng.process_quote(q,s)
  oracle.ingest(q,eng.events[ev_cursor:],eng);ev_cursor=len(eng.events)
  if (i+1)%200000==0:print('REPLAY_PROGRESS',i+1,'/',N,'fills',eng._next_id-1,'closes',len(eng.closed),'source049',hb.total_source_events,'secs',round(time.monotonic()-t0,1),flush=True)
 report={
   'unit':'DAA_033_PHASE_C2D3B_REAL_FEB_FUNDED_PARENT_CHILD_QUEUE_AND_EQUITY_REPLAY',
   'scope':'BROKER_IDEALIZED_PARTIAL_V1_049_119_084_CHAIN_NOT_COMPLETE_OWNER_V1',
   'verified_input_sha256':actual_inputs,'derived_cached_source_array_sha256':derived_cache_sha256,
   'per_simulation_fresh_raw_sha256_validation':True,
   'february_contiguous_quotes':N,'genuine_january_context_quotes':j,
   'feb_first_ms':int(t[0]),'feb_last_ms':int(t[-1]),'utc_window':'Feb 02 06:30 to Feb 03 19:00 UTC (first specified 1,136,212 quotes)',
   'source_049_candidates_before_l7_denial':hb.total_source_events,'source_049_families':hb.by_family,
   'source_049_expectation_13063':13063 if N==1136212 else None,
   'source_049_candidate_count_parity':('PASS_COUNT' if hb.total_source_events==13063 else 'FAIL_COUNT') if N==1136212 else 'PARTIAL_WINDOW_NOT_TESTED',
   'source_049_capacity_eligible':hb.eligible_source_events,'source_049_capacity_denials':quota.denied,
   'funded_119_parent_windows':wd.admitted_parent_windows,'funded_119_new_parent_earned_admissions':wd.earned_parent_admissions,
   'funded_084_actual_child_fills':sum(wd.children_funded.values()),'funded_084_actual_child_exits':len(wd.funded_close_events),
   'funded_084_parent_windows_with_children':len(wd.children_funded),
   'funded_084_realized_good_child_closes':sum(c.layer=='L4' and c.net_usd>0 and c.held_ms<=limits.good_hold_ms for c in eng.closed),
   'funded_084_bad_or_slow_child_closes':sum(c.layer=='L4' and not(c.net_usd>0 and c.held_ms<=limits.good_hold_ms) for c in eng.closed),
   'relocks':sum(c.relocks for c in eng.campaigns.values()),
   'combined_sec_max_engine':eng.combined_order_rate_max,'combined_sec_max_independent':oracle.max_orders_sec,
   'independent_equity_max_abs_difference':oracle.max_equity_delta,'independent_account_mismatches':oracle.mismatch_count,
   'independent_account_first_mismatches':oracle.first_mismatches,
   'independent_all_quote_max_dd_pre_and_post':round(oracle.max_dd,6),
   'engine_max_dd_pre_and_post':eng.dd_max,
   'independent_net_closed':round(oracle.total_net,6),'engine_net_closed':round(eng.gross_profit+eng.gross_loss,6),
   'independent_closed_count':oracle.close_count,'oracle_closes_by_layer':dict(oracle.by_layer),
   'independent_daily_net_usd':{k:round(v,6) for k,v in sorted(oracle.daily.items())},
   'independent_weekly_net_usd':{k:round(v,6) for k,v in sorted(oracle.weekly.items())},
   'independent_daily_trades':dict(sorted(oracle.daily_trades.items())),
   'independent_weekly_trades':dict(sorted(oracle.weekly_trades.items())),
   'final_open_positions':len(eng.positions),'final_marked_equity':round(oracle.last_post,6),
   'funded_score':eng.score(),'ledger_execution_event_count':len(oracle.exec_trace),
   'model_limits':limits.__dict__,'low_source_surge_ablation':low_surge,'counterfactual_parent_ttl_scale':parent_ttl_scale,'counterfactual_parent_tp_scale':parent_tp_scale,
   'ab_forced_physical_049_parent_denial':deny_049_parents,
   'ab_minimum_084_funded_child_delay_from_paid_parent_ms':child_after_parent_ms,
   'completed_HTF_model':SOURCE_MODEL,
   'source_049_entry_index_parity':'COUNTS_ONLY_NEED_INDEPENDENT_001_017_019_INDEX_COMPARISON',
   'remaining':['TRUE_COMPLETED_H4_H1_M15_M5_ROLE_SEMANTICS','FULL_L1_L3_L5_L6_SOURCE_STACK','075_PARENT_SELECTION_PARITY','COINEXX_MARGIN_HEDGING_SLIPPAGE','ENTIRE_FEB_MONTH_AND_JAN_V1_PARITY','METAEDITOR_MT5'],
   'governance':{'original_whitepaper':'UNMODIFIED','JAN039':'FROZEN','FEB045_047':'FROZEN','production_delta':'READ_ONLY','march':'HELD','august':'SEALED','september':'RESERVED'},
   'elapsed_seconds':round(time.monotonic()-t0,3)}
 assert oracle.mismatch_count==0 and oracle.max_equity_delta<1e-6,('independent equity mismatch',oracle.first_mismatches)
 assert sum(oracle.daily_trades.values())==oracle.close_count
 assert sum(oracle.weekly_trades.values())==oracle.close_count
 assert abs(sum(oracle.daily.values())-oracle.total_net)<1e-5
 assert abs(sum(oracle.weekly.values())-oracle.total_net)<1e-5
 if deny_049_parents:
  assert wd.admitted_parent_windows==0 and not wd.funded_entry_events and not wd.funded_close_events
  assert eng.reject_counts['AB_DENY_FUNDED_049_PARENT']>0, 'AB test failed to actually deny candidate parents'
 assert abs(oracle.total_net-(eng.gross_profit+eng.gross_loss))<1e-6
 assert oracle.max_orders_sec<=orders
 out.parent.mkdir(parents=True,exist_ok=True)
 trace_path=out.with_name(out.stem+'_PHYSICAL_LEDGER.jsonl')
 with trace_path.open('w') as f:
  for event in oracle.exec_trace:f.write(json.dumps(event,separators=(',',':'))+'\n')
 report['physical_execution_ledger_filename']=trace_path.name
 report['physical_execution_ledger_sha256']=sha256(trace_path)
 out.write_text(json.dumps(report,indent=2)+'\n')
 print('C2D3B_SUMMARY',json.dumps({k:report[k] for k in ('source_049_candidates_before_l7_denial','source_049_candidate_count_parity','funded_119_parent_windows','funded_084_actual_child_fills','funded_084_actual_child_exits','independent_account_mismatches','engine_max_dd_pre_and_post','independent_all_quote_max_dd_pre_and_post','elapsed_seconds')}),flush=True)
 return report

if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('--root',type=Path,default=Path('/mnt/data'));pa.add_argument('--cache',type=Path,default=Path('/mnt/data/c2d3b_work/feb_source_arrays.npz'));pa.add_argument('--out',type=Path,default=Path('/mnt/data/c2d3b_work/C2D3B_FEB_REPLAY_RESULT.json'));pa.add_argument('--count',type=int,default=1136212);pa.add_argument('--prepare',action='store_true');pa.add_argument('--low-surge',action='store_true');pa.add_argument('--cap',type=int,default=32);pa.add_argument('--orders',type=int,default=4);pa.add_argument('--spread',type=float,default=3.0);pa.add_argument('--limit',type=int,default=None);pa.add_argument('--parent-ttl-scale',type=float,default=1.);pa.add_argument('--parent-tp-scale',type=float,default=1.);pa.add_argument('--deny-049-parents',action='store_true');pa.add_argument('--child-after-parent-ms',type=int,default=0)
 args=pa.parse_args()
 if args.prepare or not args.cache.exists():prepare(args.root,args.count,args.cache)
 replay(args.cache,args.out,source_root=args.root,cap=args.cap,spread=args.spread,orders=args.orders,low_surge=args.low_surge,limit=args.limit,parent_ttl_scale=args.parent_ttl_scale,parent_tp_scale=args.parent_tp_scale,
  deny_049_parents=args.deny_049_parents,child_after_parent_ms=args.child_after_parent_ms)
