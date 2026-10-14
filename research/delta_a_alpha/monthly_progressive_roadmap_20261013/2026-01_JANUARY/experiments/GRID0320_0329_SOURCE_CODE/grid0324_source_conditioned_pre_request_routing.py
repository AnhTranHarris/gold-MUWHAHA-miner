"""GRID0324 test reconstructible source-conditional pre-request microstructure routing.
No future outcomes/month or R9 targets influence conditional screen; source names
from previously frozen source code, not tuned on day identity. All replay research.
"""
from __future__ import annotations
import grid0320_causal_pre_request_microstructure_admission as prior
from pathlib import Path
S=prior.SOURCE
old='screen_quote_idx=None,pre_request_shock_5s=None,\n        max_observed_spread=0.,max_observed_5s_shock=0.,min_observed_5s_shock=0.):'
new='screen_quote_idx=None,pre_request_shock_5s=None,\n        max_observed_spread=0.,max_observed_5s_shock=0.,min_observed_5s_shock=0.,screen_sources=()):'
assert S.count(old)==1
S=S.replace(old,new)
old='if screen_quote_idx is not None and (max_observed_spread or max_observed_5s_shock or min_observed_5s_shock):'
new='if screen_quote_idx is not None and (max_observed_spread or max_observed_5s_shock or min_observed_5s_shock) and (not screen_sources or src in screen_sources):'
assert S.count(old)==1
S=S.replace(old,new)
# Numba compiled research function from generated source needs no caching.
ns={'__file__':str(Path(__file__).resolve().parent/'grid0312_tick_stopout_executable.py')}
exec(compile(S,str(Path(__file__).resolve()),'exec'),ns)
run=ns['run']
features=prior.features
