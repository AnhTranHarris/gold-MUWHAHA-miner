"""Prospective recovery-branch cash target after source-exact 250ms adverse-FIRST landmark.
Original V9 stop/harvest remains authoritative until the change is executable.
No fabricated passive fills, same original entry count, no quote-rebuild.
"""
import hashlib,sys,time,json, argparse,os
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(os.environ.get('COINEXX_DATA_ROOT','/mnt/data'))
LEDGERS=Path(os.environ.get('V12_EVENT_LEDGER_ROOT',str(ROOT/'r9_micro180_v12_results')))
OUT=Path(os.environ.get('V16_RESEARCH_OUT',str(ROOT/'v16_profitfirst')))
POLICIES={
 'RECOVERY_CASH_002_AT_250MS':(.02,250),
 'RECOVERY_CASH_005_AT_250MS':(.05,250),
 'RECOVERY_CASH_002_AT_1000MS':(.02,1000)
}

def month_run(m):
 p=ROOT/f'XAUUSD_MT5_BROKER_2026_{m}_ticks_ALL.csv.gz'
 receipts=pd.read_csv(LEDGERS/'V12_MONTHLY_SOURCE_PROOF.csv',dtype={'month':str}).set_index('month')
 with p.open('rb') as f:sh=hashlib.file_digest(f,'sha256').hexdigest()
 assert sh==receipts.loc[m,'source_sha256']
 t0=time.monotonic();df=pd.read_csv(p,compression='gzip',usecols=['time_msc','bid','ask'])
 ts=df.time_msc.to_numpy(dtype='int64');bid=np.rint(df.bid.to_numpy()*100).astype('int32');ask=np.rint(df.ask.to_numpy()*100).astype('int32');del df
 path=LEDGERS/f'2026-{m}_V12_exactms_micro180_events.csv.gz'
 x=pd.read_csv(path,compression='gzip',usecols=['entry_ordinal','exit_ordinal','entry_time_msc','exit_time_msc','side','entry_execution_u','entry_liquidation_u','exit_price_u','exit_reason'])
 x=x[x.exit_ordinal.notna()];agg={k:dict(count=0,saved=0.,converted_losers=0,winners_lost=0,changed=0) for k in POLICIES}
 base=0.;nets={k:0. for k in POLICIES};win={k:0 for k in POLICIES};baseline_wins=0
 for trade in x.itertuples(index=False):
  i=int(trade.entry_ordinal)-1;end=int(trade.exit_ordinal)-1;side=int(trade.side)
  if end<=i:raise AssertionError('inverted source ordinal')
  assert ts[i]==trade.entry_time_msc and ts[end]==trade.exit_time_msc
  ex=int(trade.entry_execution_u);q=bid if side>0 else ask
  original=round(side*(int(trade.exit_price_u)-ex)/100-.2,4)
  base+=original;baseline_wins+=int(original>0)
  for k,(target,landmark) in POLICIES.items():
   new=original
   n=int(np.searchsorted(ts,int(ts[i])+landmark,side='left'))
   if n<end-1 and n>i and int(ts[n]-ts[i])-landmark<=250 and not np.any(np.diff(ts[i:n+1])>2500):
    deltas=side*(q[i+1:n+1].astype('int32')-int(trade.entry_liquidation_u))
    pos=np.flatnonzero(deltas>=10);neg=np.flatnonzero(deltas<=-10)
    adverse_first=len(neg)>0 and (not len(pos) or neg[0]<pos[0])
    if adverse_first:
     # The lower target is only in force from *now*, not before decision.
     quote_liq=q[n:end].astype('int32');cash=side*(quote_liq-ex)/100-.2
     crossing=np.flatnonzero(cash>=target)
     if len(crossing):
      observed_idx=n+int(crossing[0]);act=observed_idx+1
      if act<end and ts[act]-ts[observed_idx]<=600 and not np.any(np.diff(ts[n:act+1])>2500):
       new=round(side*(int(q[act])-ex)/100-.2,4)
       agg[k]['changed']+=1
       agg[k]['converted_losers']+=int(original<=0 and new>0)
       agg[k]['winners_lost']+=int(original>0 and new<=0)
   agg[k]['count']+=1;agg[k]['saved']+=new-original
   nets[k]+=new;win[k]+=int(new>0)
 result={'month':m,'source_sha256':sh,'closed_trades':len(x),'baseline':{'net':round(base,2),'wins':baseline_wins},
 'policies':{k:{'net':round(nets[k],2),'wins':win[k],
                 'win_rate':round(win[k]/len(x),6),'uplift':round(nets[k]-base,2),**{kk:(round(vv,3) if isinstance(vv,float) else vv) for kk,vv in z.items()}}
             for k,z in agg.items()},'research_only':True,'original_entry_opportunities_retained':len(x)}
 OUT.mkdir(parents=True,exist_ok=True);(OUT/f'V16_SALVAGE_{m}.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({'month':m,'runtime':round(time.monotonic()-t0,2),'baseline':round(base,2),
   'policies':{k:{'uplift':q['uplift'],'changes':q['changed'],'more_winners':q['wins']-baseline_wins} for k,q in result['policies'].items()}}),flush=True)
 return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('months',nargs='*');v=ap.parse_args()
 for mon in v.months or ['01','05','09']:month_run(mon)
