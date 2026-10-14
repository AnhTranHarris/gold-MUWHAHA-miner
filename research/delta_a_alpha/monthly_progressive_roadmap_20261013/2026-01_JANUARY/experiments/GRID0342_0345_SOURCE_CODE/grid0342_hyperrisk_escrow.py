"""Microcapital risk-envelope investigation, original Dukascopy ticks, RESEARCH ONLY.
Preserves original GRID0324 funded Watchdog+quote engine; injected L7 admission veto
uses ONLY paid cash, marked equity and known open positions on current entry quote.
No future exits or R9 labels in hyperrisk decisions. The upstream historically
selected candidate stream remains a material in-sample limitation.
"""
import sys
from pathlib import Path
SRCROOT=Path('/mnt/data/jan_work/engine')
sys.path.insert(0,str(SRCROOT))
import grid0324_source_conditioned_pre_request_routing as original
S=original.S
# Fail closed if a liquidation attempt fails to reduce current open position count.
anchor="            liquidation(hit,defensive_ratio>stopout_ratio)\n            if not live: x=hit+1;continue"
assert S.count(anchor)==1
S=S.replace(anchor,"            pre_close_count=len(live)\n"+anchor.replace('            if not live:',"            if len(live)>=pre_close_count:raise RuntimeError('STOP_OUT_NO_PROGRESS')\n            if not live:"))
# Exposure stress: per-physical-trade pre-agreed possible sudden adverse move
# in USD on 1 oz per 0.01 lot, no information from future quotes.
signature='        fees_per_roundtrip=.20, leverage=500., require_four=True,\n        screen_quote_idx=None,pre_request_shock_5s=None,\n        max_observed_spread=0.,max_observed_5s_shock=0.,min_observed_5s_shock=0.,screen_sources=()):'
replacement='        fees_per_roundtrip=.20, leverage=500., require_four=True,\n        screen_quote_idx=None,pre_request_shock_5s=None,\n        max_observed_spread=0.,max_observed_5s_shock=0.,min_observed_5s_shock=0.,screen_sources=(),\n        stress_move_per_lot=0.,stress_floor_cash_frac=0.):'
assert S.count(signature)==1
S=S.replace(signature,replacement)
needle="        need=px/leverage\n        if post<=0 or used_margin+need>post*admission_margin_fraction:denied['margin_admission']+=1;continue"
add="""        need=px/leverage
        if stress_move_per_lot and (post-(len(live)+1)*stress_move_per_lot)<stress_floor_cash_frac*max(100.,balance):
            denied['microcapital_cash_escrow_stress']+=1;continue
        if post<=0 or used_margin+need>post*admission_margin_fraction:denied['margin_admission']+=1;continue"""
assert S.count(needle)==1
S=S.replace(needle,add).replace('@njit(cache=True)','@njit(cache=False)')
ns={'__file__':str(SRCROOT/'grid0312_tick_stopout_executable.py')}
exec(compile(S,'grid0342_temporary_research_engine','exec'),ns)
run=ns['run'];features=original.features
