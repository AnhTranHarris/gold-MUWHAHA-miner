"""GRID0337: Independent source-exact R8 January MQL5 CurrentSession broker-clock stress.
Strict R8 is unmodified; recovered UTC+2 is inference from timestamp-price matching.
Source file below used only for a NEW causal alternative, not production edits.
"""
from pathlib import Path
import importlib.util,json,time,numpy as np
BASE=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH/r8_causal_tick_port.py')
source=BASE.read_text()
original='def execute(t,ask,bid,spread_max_price=.25,latency_ms=250,roundtrip_fee=.20,initial_cash=100.,leverage=500.,stopout_ratio=1.,atr_on=True):'
assert source.count(original)==1
source=source.replace(original,original.replace('atr_on=True):','atr_on=True,clock_shift_minutes=0):'))
rule='minuteutc=(s%86400)//60'
assert source.count(rule)==1
source=source.replace(rule,'minuteutc=((s+clock_shift_minutes*60)%86400)//60')
source=source.replace('@njit(cache=True)','@njit(cache=False)')
namespace={'__file__':str(BASE)}
exec(compile(source,'grid0337_original_r8_clock_derivative','exec'),namespace)
execute=namespace['execute']
def main():
 t=np.load('/mnt/data/R8_JAN_DUKAS_RESEARCH/ticks_t.npy',mmap_mode='r')
 b=np.load('/mnt/data/R8_JAN_DUKAS_RESEARCH/ticks_bid.npy',mmap_mode='r')
 a=np.load('/mnt/data/R8_JAN_DUKAS_RESEARCH/ticks_ask.npy',mmap_mode='r')
 start=time.time();out=[]
 for shift in [0,120]:
  for spread in [.25,.50,.75]:
   res,reasons=execute(t,a,b,spread,250,.20,100.,500.,1.,True,shift)
   keys='final_cash trades wins losses gross_profit gross_loss min_tick_equity max_tick_equity_drawdown max_closed_balance_drawdown max_simul forced stop timeout signal_requests denied_requests spreadgate_ticks atrgate_ticks candidate_evals first_nonpositive_tick durations_s max_margin_usd'.split()
   d={k:float(v) for k,v in zip(keys,res)}
   d.update(clock_shift_minutes=shift,spread_ceiling_usd=spread,r8_reason_signals=reasons.tolist())
   out.append(d)
   print('DONE',shift,spread,round(d['final_cash'],2),int(d['trades']),round(d['max_tick_equity_drawdown'],2),'time',round(time.time()-start,2),flush=True)
 path=Path('/mnt/data/r8_followup_20261014/grid0337_r8_source_session_clock_stress_results.json')
 path.write_text(json.dumps({'scope':'original January 9,135,062 raw Dukascopy Bid/Ask, source-generated R8 entries','status':'UNPROMOTED_RESEARCH_ONLY','reference':'MQL5 R8 immutable blob 6b246...','strict_zero_shift':'MQL5 default quote UTC offset=0, but quoteTime is broker server clock','research_shift_120':'MT5 R8 report probable UTC+2 vs raw market UTC, applied to session classifier only; not confirmed actual Coinexx UTC metadata','limitations':['.01 USD SYMBOL_POINT assumed for max spread conversion','250ms modeled entry, 100% margin stopout, 500x leverage, 1oz/0.01 lot, fee 0.20','R8 source spread+ATR effective R8 tester symbols unknown','No fresh signal support from original MT5 trade times','Per-period acceptance and repeated $100 starting days not satisfied'], 'variants':out,'seconds':time.time()-start},indent=2));print('FILE',path,flush=True)
if __name__=='__main__':main()
