"""Single-pass R9 Micro180 v3 quote-asymmetric research runner.

Reads existing Coinexx gzip bytes in source order. Writes only compact JSON;
never generates or uploads replacement raw market data.
"""
import argparse,json,sys,time,hashlib
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for s in ('src','variable_cash_horizon_20261114','micro180_20261114'):
    sys.path.insert(0,str(ROOT/s))
from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import Micro180Spec
from asymmetric_v3 import AsymSpec,AsymmetricMicroR9


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ticks',type=Path,required=True)
    p.add_argument('--limit',type=int,default=150000,help='0 explicitly means ALL source quotes')
    p.add_argument('--initial-equity',type=float,default=1000.0)
    p.add_argument('--roundtrip-extra-cost',type=float,default=.20)
    p.add_argument('--cash-per-xau-price-dollar',type=float,default=1.0)
    p.add_argument('--profile',choices=('strict','balanced','active'),default='active')
    p.add_argument('--buy-floor',type=float,default=.15)
    p.add_argument('--sell-floor',type=float,default=.15)
    p.add_argument('--coincidence-floor',type=float,default=.30)
    p.add_argument('--disable-account-governor-research-only',action='store_true')
    p.add_argument('--experimental-protected-runner',action='store_true')
    p.add_argument('--expected-source-sha256',default=None)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.limit<0 or not a.ticks.is_file():p.error('Provide existing file and nonnegative limit')
    if a.expected_source_sha256:
        with a.ticks.open('rb') as fh:
            actual=hashlib.file_digest(fh,'sha256').hexdigest()
        if actual.lower()!=a.expected_source_sha256.lower():p.error('SOURCE SHA-256 MISMATCH')
    profiles={
        'strict':{},
        'balanced':dict(breakout_router='balanced_30s_veto'),
        'active':dict(breakout_router='balanced_30s_veto',
                      s1_mode='micro_only',
                      structural_confirmation='causal_active_or_completed')
    }
    spec=Micro180Spec(**profiles[a.profile],experimental_runner=a.experimental_protected_runner)
    quant=AsymSpec(min_buy_score=a.buy_floor,min_sell_score=a.sell_floor,
                   min_coincident_quote_fraction=a.coincidence_floor)
    cash=ResearchCash(k=a.cash_per_xau_price_dollar,cost=a.roundtrip_extra_cost,
                      initial_capital=a.initial_equity,
                      governor=not a.disable_account_governor_research_only)
    engine=AsymmetricMicroR9(R9Config(),cash,spec,quant)
    started=time.perf_counter();count=0;last=None
    for count,t in enumerate(iter_coinexx_ticks(a.ticks,strict=True),1):
        engine.on_tick(t);last=t
        if a.limit and count>=a.limit:break
    out=engine.report()
    out.update({
        'research_only':True,'out_of_sample':False,
        'uses_old_high_auc':False,'volume_claim':'QUOTE UPDATES ONLY',
        'source':a.ticks.name,'quotes_seen':count,'last_time_msc':last.time_msc if last else None,
        'source_hash_verified':bool(a.expected_source_sha256),
        'initial_account_equity':a.initial_equity,
        'cash_k':a.cash_per_xau_price_dollar,
        'incremental_cash_cost':a.roundtrip_extra_cost,
        'research_governor_disabled':not cash.governor,
        'experimental_runner_enabled':a.experimental_protected_runner,
        'micro_spec':asdict(spec),'quant_spec':asdict(quant),
        'seconds':round(time.perf_counter()-started,2),
        'not_certified':True,
        'unsettled_position_at_end':engine.position is not None,
    })
    payload=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output:
        a.output.write_text(payload,encoding='utf-8')
        print('Saved compact result',a.output,'quotes',count)
    else:print(payload)


if __name__=='__main__':main()
