"""V16 causal harvest extension at original V9 harvest event; quote-side next-tick execution.
NOT fully rearmed: overlapping subsequent original entries must be removed if extended.
"""
import argparse,hashlib,json,time,os
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(os.environ.get('COINEXX_DATA_ROOT','/mnt/data'))
LEDGERS=Path(os.environ.get('V12_EVENT_LEDGER_ROOT',str(ROOT/'r9_micro180_v12_results')))
OUT=Path(os.environ.get('V16_RESEARCH_OUT',str(ROOT/'v16_profitfirst')))
EXTENSIONS=(
 ('C_CLEAN_1S', 1_000,0.60,0.02,'CLEAN'),
 ('C_CLEAN_3S', 3_000,1.00,0.05,'CLEAN'),
 ('R_RECOVERY_3S',3_000,1.00,0.05,'RECOVERY'),
 ('C_CLEAN_5S',5_000,1.50,0.10,'CLEAN'),
 ('C_FAST_PROTECTED_1500MS',1_500,0.60,0.12,'CLEAN'),
)

def first_extension_exit(ms,bid,ask,original_exit,entry_execution,
                         entry_liquidation,side,target,floor,hold_ms):
    """Earliest source-ordinal target, protective boundary, gap, or timeout.

    Called *only when* the original harvest became observable. Start at the
    next quote; preserve absolute initial liquidation-side risk. No future
    quote values are used to decide that the extension should start.
    """
    end=min(len(ms),int(np.searchsorted(ms,int(ms[original_exit])+hold_ms,side='right')))
    if end<=original_exit+1:return None
    mark=(bid[original_exit+1:end] if side>0 else ask[original_exit+1:end]).astype(np.int32)
    cash=side*(mark-entry_execution)/100.-.2
    drift=side*(mark-entry_liquidation)
    gap=np.diff(ms[original_exit:end])>2500
    hit=np.flatnonzero((cash>=target)|(cash<=floor)|(drift<=-30)|gap)
    index=original_exit+1+int(hit[0]) if len(hit) else end-1
    price=int(bid[index] if side>0 else ask[index])
    return index,round(side*(price-entry_execution)/100.-.2,4)

def simulate(month):
 p=ROOT/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
 receipt=pd.read_csv(LEDGERS/'V12_MONTHLY_SOURCE_PROOF.csv',dtype={'month':str}).set_index('month')
 with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==receipt.loc[month,'source_sha256']
 t=time.monotonic()
 df=pd.read_csv(p,compression='gzip',usecols=['time_msc','bid','ask'])
 ms=df.time_msc.to_numpy(dtype=np.int64);bid=np.rint(df.bid.to_numpy()*100).astype(np.int32);ask=np.rint(df.ask.to_numpy()*100).astype(np.int32);del df
 columns=['entry_ordinal','entry_time_msc','exit_ordinal','exit_time_msc','side','entry_execution_u','entry_liquidation_u','exit_price_u','exit_reason','hold_ms','actual_first_adverse_10ms']
 trades=pd.read_csv(LEDGERS/f'2026-{month}_V12_exactms_micro180_events.csv.gz',usecols=columns)
 closed=trades[trades.exit_ordinal.notna()].copy()
 base_cash=[];exts={name:[] for name,*_ in EXTENSIONS};exits={name:[] for name,*_ in EXTENSIONS};eligible={name:0 for name,*_ in EXTENSIONS};changed={name:0 for name,*_ in EXTENSIONS}
 for z in closed.itertuples(index=False):
  start=int(z.entry_ordinal)-1;original_exit=int(z.exit_ordinal)-1;side=int(z.side)
  assert ms[start]==z.entry_time_msc and ms[original_exit]==z.exit_time_msc
  entryprice=int(z.entry_execution_u)
  baseline=round(side*(int(z.exit_price_u)-entryprice)/100-.2,4)
  base_cash.append(baseline)
  for name,hold_ms,target,floor,family in EXTENSIONS:
   # The original decision to close on cash harvest is known at this event.
   # Clean/recovery split at that moment uses only the quote-path already seen.
   isclean=pd.isna(z.actual_first_adverse_10ms)
   eligible_event=(z.exit_reason=='cash_010_harvest' and z.hold_ms<=15000
                   and (isclean if family=='CLEAN' else not isclean)
                   and baseline<target)
   if name=='C_FAST_PROTECTED_1500MS':
    eligible_event=eligible_event and baseline>=0.20 and z.hold_ms<=3000
   new_idx=original_exit;net=baseline
   if eligible_event:
    eligible[name]+=1
    ext=first_extension_exit(ms,bid,ask,original_exit,entryprice,
                         int(z.entry_liquidation_u),side,target,floor,hold_ms)
    if ext is not None:new_idx,net=ext
   if new_idx!=original_exit:changed[name]+=1
   exts[name].append(net)
   exits[name].append(new_idx)
 base=np.array(base_cash)
 base_eq=np.r_[0,np.cumsum(base)]
 base_dd=float(np.max(np.maximum.accumulate(base_eq)-base_eq))
 result=dict(month=month,source_sha256=sha,closed_trades=len(closed),
             baseline_net=round(float(base.sum()),2),baseline_wins=int((base>0).sum()),
             baseline_max_closed_trade_dd=round(base_dd,2),
             policy={},research_only=True,source_order_preserved=True)
 old_entries=trades.entry_ordinal.to_numpy(dtype=float)-1
 for name,_,_,_,_ in EXTENSIONS:
  nets=np.array(exts[name],dtype=float);newexits=np.array(exits[name],dtype=np.int64)
  # Fixed-entry diagnostic: retains all original entries even if the extended
  # position overlaps a later entry. Prohibited from deployment/claiming volume.
  fixed_eq=np.r_[0,np.cumsum(nets)]
  fixed_dd=float(np.max(np.maximum.accumulate(fixed_eq)-fixed_eq))
  fixed_all=dict(net=round(float(nets.sum()),2),delta=round(float(nets.sum()-base.sum()),2),
                 win_rate=float((nets>0).mean()),winners=int((nets>0).sum()),
                 max_closed_trade_dd=round(fixed_dd,2),changed=changed[name],eligible=eligible[name])
  # Conservative one-active-position rearm: drop conflicting original entries.
  keep=np.ones(len(closed),dtype=bool);last=-1
  entries=closed.entry_ordinal.to_numpy(dtype=np.int64)-1
  for i,en in enumerate(entries):
   if en<=last:keep[i]=False;continue
   last=int(newexits[i])
  eff=nets[keep];frozen=base[keep]
  eq=np.r_[0,np.cumsum(eff)]
  max_dd=float(np.max(np.maximum.accumulate(eq)-eq))
  policy_res=dict(fixed_all=fixed_all,
    rearmed_existing_signals=dict(trades=int(len(eff)),trade_retention=float(len(eff)/len(base)),
      net=round(float(eff.sum()),2),win_rate=float((eff>0).mean()),
      winners=int((eff>0).sum()),max_closed_trade_dd=round(max_dd,2),
      delta_vs_same_retained_baseline=round(float((eff-frozen).sum()),2),
      # Baseline original existing trades that were blocked by extra hold are
      # included in relative total, not silently discarded from denominator.
      delta_vs_all_original=round(float(eff.sum()-base.sum()),2)))
  result['policy'][name]=policy_res
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/f'V16_HARVEST_{month}.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'month':month,'s':round(time.monotonic()-t,2),'baseline':result['baseline_net'],
                   'policy':{k:{'fixed':v['fixed_all']['delta'],'real_delta':v['rearmed_existing_signals']['delta_vs_all_original'],
                                'retention':round(v['rearmed_existing_signals']['trade_retention'],3)} for k,v in result['policy'].items()}}),flush=True)
 return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('months',nargs='*');x=ap.parse_args()
 for mon in x.months or ('01','05','09'):simulate(mon)
