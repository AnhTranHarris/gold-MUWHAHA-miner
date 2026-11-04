from __future__ import annotations
import json,sys,traceback
from pathlib import Path
from r24_restore_actual_event_clock import restore
from r24_firstpass_engine import R24,SOURCE_NAMES
for mon in ('01','02','06','07'):
 for src in SOURCE_NAMES:
  dest=R24/'results'/src/mon/f'R24_{src}_{mon}_ACTUAL_BROKER_QUOTE_CLOCK_RECEIPT.json'
  if dest.exists():
   print('SKIP_ALREADY_VERIFIED',src,mon,flush=True);continue
  print('CLOCK_START',src,mon,flush=True)
  try:restore(src,mon)
  except Exception:
   print('CLOCK_FAIL',src,mon,flush=True);traceback.print_exc();raise
  print('CLOCK_COMPLETE',src,mon,flush=True)
