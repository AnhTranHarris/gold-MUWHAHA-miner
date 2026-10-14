"""GRID0320: unpromoted, causal quote-screen extension of GRID0312.

This is a research proposal only, NOT an endogenous signal creator or broker order
protocol. Entry quality features use the earliest observed quote at least 1 second
BEFORE the inherited quote-side entry, instead of leaking fill-time information
into a fictitious pre-entry decision. Caution: actual historical request times
are not present in the inherited source candidates; hence this is not physical
order-state certification and can only serve as a conservative hypothesis screen.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import grid0312_tick_stopout_executable as original
SOURCE=Path(original.__file__).read_text()
SRC_SHA='ad84a06bf1d2c3ad99c71d85f1e5bb16235be69c' # verified original git blob
old='max_tick_slippage_usd=0.,\n        fees_per_roundtrip=.20, leverage=500., require_four=True):'
new='max_tick_slippage_usd=0.,\n        fees_per_roundtrip=.20, leverage=500., require_four=True,\n        screen_quote_idx=None,pre_request_shock_5s=None,\n        max_observed_spread=0.,max_observed_5s_shock=0.,min_observed_5s_shock=0.):'
assert SOURCE.count(old)==1
SOURCE=SOURCE.replace(old,new)
anchor='        if typ==0:\n            if src_open[src]>='
assert SOURCE.count(anchor)==1
replace='''        # Causal pre-request microstructure veto: observe quote at least 1s
        # before modeled fill; no future quote or R9 outcome used here.
        if screen_quote_idx is not None and (max_observed_spread or max_observed_5s_shock or min_observed_5s_shock):
            qi=int(screen_quote_idx[ei]); observed_spread=(int(ask[qi])-int(bid[qi]))/1000.
            old_shock=float(pre_request_shock_5s[ei])
            if (max_observed_spread and observed_spread>max_observed_spread) or (max_observed_5s_shock and old_shock>max_observed_5s_shock) or (min_observed_5s_shock and old_shock<min_observed_5s_shock):
                denied['pre_request_microstructure']+=1;continue
''' + anchor
SOURCE=SOURCE.replace(anchor,replace)
# Generated research source has no on-disk Numba cache locator. Disable JIT disk caching only; computation unchanged.
SOURCE=SOURCE.replace('@njit(cache=True)', '@njit(cache=False)')
ns={'__file__':str(Path(__file__).resolve().parent/'grid0312_tick_stopout_executable.py')}
exec(compile(SOURCE,'grid0320_generated_ledger_engine','exec'),ns)
run=ns['run']

def features(t,bid,ask):
    assert len(t)>3
    # At least one full second before quote-side execution, causal conservative buffer.
    pre=np.maximum(0,np.searchsorted(t,t-1000,side='right')-1)
    older=np.maximum(0,np.searchsorted(t,t[pre]-5000,side='right')-1)
    # All source integer prices = USD*1000.
    shock=np.abs(((bid[pre].astype('float64')+ask[pre].astype('float64'))-
                  (bid[older].astype('float64')+ask[older].astype('float64')))*.0005)
    return pre,shock
