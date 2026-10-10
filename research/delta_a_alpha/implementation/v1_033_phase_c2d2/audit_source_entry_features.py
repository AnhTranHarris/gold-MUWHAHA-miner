"""Full original JAN038=>FEB042 input feature parity from real JAN tail + FEB tape.

Original executable authorities:
  FEB042/prepare.py: qsp=(ask[E]-bid[E])/1000; searchsorted(t,t[E]-20000,'left')
  JAN038_SELECTED_EXACT.json: signal_gating_source_phase_pairs.
Original JAN039 source preprocessing defines X/exit outcomes, deliberately excluded.
This source audit uses only real ordered Bid/Ask quotes and entry-known timestamps.
"""
import hashlib, json, os, time
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(os.environ.get('DAA_RAW_SOURCE_ROOT','/mnt/data')); ORIG=Path(os.environ.get('DAA_FEB042_PREPARED_NPZ',str(ROOT/'c2d3i_native_src/feb042/FEB042/FEB042_JAN039_PREPARED_PROPOSALS.npz')))
JAN=ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'; FEB=ROOT/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
J38=Path(__file__).resolve().parent/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'
WARMUP=3900880
EXPECTED={JAN.name:'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',FEB.name:'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'}
def get_data(p):
 sha=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
 if sha!=EXPECTED[p.name]:raise ValueError(f'Bad compressed tick original {p.name}: {sha}')
 d=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
 return d.timestamp_ms_utc.to_numpy(),d.ask_raw.to_numpy(),d.bid_raw.to_numpy()
def main():
 tic=time.time(); jt,ja,jb=get_data(JAN); ft,fa,fb=get_data(FEB)
 t=np.r_[jt[-WARMUP:],ft];a=np.r_[ja[-WARMUP:],fa];b=np.r_[jb[-WARMUP:],fb]
 assert t.size == WARMUP+ft.size == 11439219
 assert bool(np.all(t[1:]>=t[:-1]))
 with np.load(ORIG) as z: rows={k:z[k] for k in ('E','S','phase','excluded','spread','imp20')}
 E=rows['E']; source=rows['S']; phase=(t[E]//600000)%6
 rules=json.loads(J38.read_text())['signal_gating_source_phase_pairs']
 excluded=np.zeros(len(E),dtype=bool)
 for src,bin10 in rules:excluded|=(source==src)&(phase==bin10)
 spread=(a[E].astype(np.int64)-b[E])/1000.
 prior=np.searchsorted(t,t[E]-20000,'left')
 imp20=(a[E].astype(np.int64)+b[E].astype(np.int64)-a[prior].astype(np.int64)-b[prior].astype(np.int64))/2000.
 compare={
 'phase':int(np.count_nonzero(phase!=rows['phase'])),
 'excluded':int(np.count_nonzero(excluded!=rows['excluded'])),
 'spread':int(np.count_nonzero(~np.isclose(spread,rows['spread'],rtol=0,atol=1e-10))),
 'imp20':int(np.count_nonzero(~np.isclose(imp20,rows['imp20'],rtol=0,atol=1e-10)))}
 gap={key:float(np.max(np.abs(x-rows[key]))) for key,x in [('spread',spread),('imp20',imp20)]}
 ans=dict(original='JAN038_SELECTED_EXACT.json+FEB042/prepare.py',raw_data_sha256=EXPECTED,
  warmup_quote_count=WARMUP,jan_quotes=len(jt),feb_quotes=len(ft),reconstructed_tape=len(t),
  source_events=len(E), first_event_index=int(E[0]),last_event_index=int(E[-1]),
  jan_warmup_end_ms=int(t[WARMUP-1]),feb_start_ms=int(t[WARMUP]),
  mismatches=compare,max_abs_diff=gap,exclusion_count=int(excluded.sum()),
  excluded_pairs=rules,elapsed_s=round(time.time()-tic,2),source_exclusion_is_monthblind=True,
  source_proposals_or_portfolio_PnL_certified=False)
 outfile=Path(__file__).resolve().parent/'JAN038_FEB042_REAL_11439219_QUOTE_ENTRY_PARITY.json'
 outfile.write_text(json.dumps(ans,indent=2)+'\n');print(json.dumps({k:v for k,v in ans.items() if k not in ('excluded_pairs',)},indent=2))
 if any(compare.values()): raise AssertionError('SOURCE ENTRY FEATURE MISMATCHES '+str(compare))
if __name__=='__main__':main()
