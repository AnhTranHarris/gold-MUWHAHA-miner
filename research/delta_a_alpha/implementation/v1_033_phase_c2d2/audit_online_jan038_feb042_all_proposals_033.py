"""Cross-check online original JAN038+FEB042 module with exact original 234,698 offers.

This is a standalone event-input SOURCE parity oracle. It does not grant L7
admission, import frozen hypothetical exits, or use any calendar-month switch.
"""
import hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_jan038_feb042_online_033 import OriginalJAN038FEB042Online
ROOT=Path(os.environ.get('DAA_RAW_SOURCE_ROOT','/mnt/data')); HOME=Path(__file__).resolve().parent
RAW=[ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',ROOT/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz']
SHAS=['d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d']
PREPARED=Path(os.environ.get('DAA_FEB042_PREPARED_NPZ',str(ROOT/'c2d3i_native_src/feb042/FEB042/FEB042_JAN039_PREPARED_PROPOSALS.npz')))
PREP_SHA='64339d0e70dfdb9e85fbb90fb446f96ac1190da681b5e9520a442e3958daa29e'
WARM=3900880  # exact original FEB041 tape index offset: JAN full tail + FEB full

def read(path,sha):
 with path.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
 assert actual==sha,(path.name,actual)
 d=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
 return d.timestamp_ms_utc.to_numpy(),d.ask_raw.to_numpy(),d.bid_raw.to_numpy()

def main():
 st=time.time()
 with PREPARED.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==PREP_SHA
 jt,ja,jb=read(RAW[0],SHAS[0]);ft,fa,fb=read(RAW[1],SHAS[1]);
 t=np.r_[jt[-WARM:],ft];a=np.r_[ja[-WARM:],fa];b=np.r_[jb[-WARM:],fb]
 with np.load(PREPARED) as z: E=z['E'];S=z['S'];PH=z['phase'];SP=z['spread'];IM=z['imp20'];EX=z['excluded']
 assert len(t)==11439219 and len(E)==234698
 assert np.all(E[:-1]<=E[1:])
 run=OriginalJAN038FEB042Online(HOME/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json')
 left=0
 errors=dict(phase=0,spread=0,imp20=0,excluded=0)
 peak_per_tick=0;duplicate_ticks=0;first_error=[]
 for i in range(len(t)):
  run.on_quote(int(t[i]),int(a[i]),int(b[i]))
  first=left
  while left<len(E) and E[left]==i:
   v=run.context_for(int(S[left]));peak_per_tick=max(peak_per_tick,left-first+1)
   if left>first:duplicate_ticks+=1
   bad={
    'phase':v.phase10!=PH[left],
    'spread':v.spread_usd!=SP[left],
    'imp20':v.raw_impulse20_usd!=IM[left],
    'excluded':v.excluded_by_jan038!=EX[left]}
   for key,wrong in bad.items():errors[key]+=int(wrong)
   if any(bad.values()) and len(first_error)<3: first_error.append({'i':int(left),'tick':i,'bad':bad,'observed':str(v)})
   left+=1
  # no theoretical future proposal events processed; all exactly chronological
 assert left==len(E)
 report={"authority":"JAN038_SELECTED_EXACT.json + FEB042/prepare.py full original files",
   "event_authority":"FEB042_JAN039_PREPARED_PROPOSALS.npz exact frozen source offer tape",
   "tape_quotes":len(t),"jan_warmup_quotes":WARM,"feb_quotes":len(ft),"original_offers":len(E),
   "online_history_quotes":run.observed_quotes,"max_source_offers_per_real_tick":peak_per_tick,
   "duplicate_source_offers_after_first_on_tick":duplicate_ticks,
   "original_source_exclusions":int(EX.sum()),"mismatch":errors,"first_errors":first_error,
   "input_sha256":dict(zip([p.name for p in RAW],SHAS)),
   "prepared_npz_sha256":PREP_SHA,"no_calendar_month_execution_feature":True,
   "does_not_certify_upstream_source_generator_or_funded_pnl":True,
   "elapsed_seconds":round(time.time()-st,2)}
 path=HOME/'JAN038_FEB042_ONLINE_FULL_EVENT_PARITY.json';path.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
 if any(errors.values()):raise AssertionError('Unmatched source feats')

if __name__=='__main__':main()
