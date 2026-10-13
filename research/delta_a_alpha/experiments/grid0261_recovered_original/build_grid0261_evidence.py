import pandas as pd,json,hashlib,zipfile,datetime,math,os
from pathlib import Path
root=Path('/mnt/data')
out=root/'grid0261_intrinsic';out.mkdir(exist_ok=True)
base=pd.read_csv(root/'GRID0244_R9_SYNTH_MONTHLY_MT5_SERVER_CLOSED.csv')
orc=json.loads((out/'GRID0261_R9_60PCT_RETROSPECTIVE_5SEC_QUOTE_EVENT_UPPER_BOUND.json').read_text())
cap=json.loads((out/'GRID0261_ORACLE_OVERLAP_AND_60PCT_SLOT_FEASIBILITY.json').read_text())
raw=[]
for i,r in base.iterrows():
 m=i+1;c=cap[str(m)]['fixed_exit_60sec_slot_density_upper_by_slot']
 raw.append({'month':r.mt5_server_month,'R9_SYNTH_original_completed':int(r.closed_positions),
    'R9_SYNTH_60pct_completed_goal':math.ceil(.6*int(r.closed_positions)),
    'R9_SYNTH_60pct_net_broker_usd_goal':round(float(r.net_usd)*.6,2),
    'retrospective_5s_oracle_best_net_2p1_after_spread_fee_event_count':orc[str(m)]['oracle_2p1_count'],
    'hindsight_60sec_full_occupancy_slots4':c['4']['admissible_hindsight_candidates_60s_occupancy'],
    'hindsight_60sec_full_occupancy_slots7':c['7']['admissible_hindsight_candidates_60s_occupancy'],
    'hindsight_60sec_full_occupancy_slots8':c['8']['admissible_hindsight_candidates_60s_occupancy'],
    'oracle_profitable_fraction':orc[str(m)]['oracle_profitable_fraction'],
    'oracle_best_2p1_fraction':orc[str(m)]['oracle_over_2p1_fraction']})
pd.DataFrame(raw).to_csv(out/'GRID0261_SIXTY_PERCENT_R9_MONTHLY_AND_HINDSIGHT_SOURCE_FEASIBILITY.csv',index=False)
count=sum(orc[str(m)]['oracle_2p1_count'] for m in range(1,8))
assert count==260462
assert cap['total_hindsight_60s_occupancy_8_slot']==216802
assert sum(x['hindsight_60sec_full_occupancy_slots8']>=x['R9_SYNTH_60pct_completed_goal'] for x in raw)==7
assert sum(x['hindsight_60sec_full_occupancy_slots7']>=x['R9_SYNTH_60pct_completed_goal'] for x in raw)==6
positive_ratio=orc['3']['oracle_over_2p1_fraction']/orc['7']['oracle_over_2p1_fraction']
report=f'''# GRID0261 — R9 SYNTH 60% objective and intrinsic-time grid source reachability

**RESEARCH ONLY; NO SCIENTIFIC PROMOTION OR BROKER PERFORMANCE CLAIM.** Exact scope: active `AnhTranHarris/gold-MUWHAHA-miner` branch `delta-A-alpha`, journal J0183 and trading OFF. August SEALED. R9 SYNTH is the performance target; R9 OVERFIT shows hindsight-optimal entry/side/speed/exit and is NEVER an online trading feature. Each month has its own observed market conditions. The owner calls for daily high-volume, hourly high-accuracy, multiday multigeometry, multiple HTF, multi-scalping, and sniper sleeves. The 60% minimum is a **conservative performance acceptance objective, not an attained figure**.

## Audit inherited actual GRID0258–0260 code BEFORE experiment

- The actual `FourSessionV1`0 executable root (`v1_four_session_architecture.py`) still uses `CooperativeGridGenesis`, not the GRID0246–0258 cumulative `GridStrategySourceRouter` with HTF sniper, paid-close and J179F permission. GRID0259's separate `ResearchFundingEngine`0 exists only in local verified portable source and cannot certify Coinexx symbol contract, leverage, margin, stop/freeze or server clock. Its GitHub commit had been blocked after the daily scoreboard files.
- Existing GRID0258 preserved **1,228** quote-research closed positions **+$6,838.528 quote USD per 1oz**, positive 7 of 7 historical months, positive only 23 of 31 represented weeks; this is not MT5 account cash and cannot be summed blindly with isolated extra specialists. GRID0260 generated **2,864** separate H4/H1 causal entries over Jan–Jul, so an HTF-only source cannot supply 60% R9 trade turnover even with a very good exit. Preserve original profitable J179F, H4 retest, H4 second-acceptance, earned fixed-size positions and original S1/M1/M5; no production changes.

## Frozen 60% R9 SYNTH performance objective

R9 original Jan–Jul tester: **219,342 closed deals; +$309,122.85 tester-account USD; 149 server-date trading days**. This research gate uses an upward-rounded **131,606 completed deals** and **+$185,473.71 original tester-dollar cash**, simultaneously. Require each month (and its corresponding verified server-calendar weeks) positive, with per-period 60%-of-own-benchmark targets when broker-clock mapping is verified. A constant 60% of each trading day is not the same as a UTC quote-source tally. The implied benchmark mean net cash per completed deal is **$1.4093**, but fees, lot oz, original Coinexx trading costs, spreads and margin must be separately honored. Do not convert historical quote PnL/oz into broker PnL without actual Coinexx contract and fee data.

Per-month 60% target and *offline future-knowledge* event-density test:

| Month | R9 60% closes | R9 60% tester net USD | Retrospective five-second quote events with future-optimal net >=$2.10/oz | Eight-position 60-second occupancy subset |
|---|---:|---:|---:|---:|
'''
for x in raw:
 report+=f"| {x['month']} | {x['R9_SYNTH_60pct_completed_goal']:,} | ${x['R9_SYNTH_60pct_net_broker_usd_goal']:,.2f} | {x['retrospective_5s_oracle_best_net_2p1_after_spread_fee_event_count']:,} | {x['hindsight_60sec_full_occupancy_slots8']:,} |\n"
report+=f'''
**Important scope limits:** the five-second source samples and their 60-second price windows **overlap**. Future direction AND best future exit are chosen after the fact. The $2.10/oz cutoff is a prespecified scenario (NOT the actual R9 cash/net target). The 60-second occupancy model conservatively reserves a slot the whole minute, then uses a greedy earliest-event ordering; it does NOT execute a stop/target, validate broker margin or price, or certify any funded profit. In this exact retrospective scenario, 4, 5, 6 and 7 slots do not meet the count benchmark in every month; **eight slots satisfy the 60% count-only gate**. This is not a universal lower bound: it depends on the $2.10 target, 5s grid sampling, cost scenario and 60s full occupancy. The quote sample contains {count:,} hindsight-optimal candidate windows across seven months, **216,802** of which fit that particular eight-slot reservation scheme. Neither are REAL executed or independent profitable deals.

## Actual repeated independent original-Dukascopy research cycles

1. **Eight prespecified causal intrinsic-time directional-change/reversal/overshoot policies** on 16.67m original Jan–Feb quotes, with true observed 250ms latency, side-correct Bid/Ask, bounded stops/targets/hold, $0.52/oz fee. No profitable January–February conditional population; DO NOT promote. `grid0261_intrinsic_time_research.py`, screen JSON.
2. **30 causal multi-geometry fixed-exit source screens** Jan–Jul: previous 5s/30s/60s/5m/15m price geometry, same/pullback/fade, 0.6/1.4/2.4 USD displacement, fixed 30/90s observed exit. On 57,527,562 real quotes no broker-certifiable strategy family. These **overlapping sample outcomes** are NOT summed as a funded account. Code and per-month score saved.
3. **36 independent spread-quality/relative-velocity source screens** Jan–Jul: ask-bid ceiling 0.30/0.45/0.60 USD, completed past movement 0.60/1.20 USD, three causal entry geometries, 30/90s first actual observed exits. As above, only unpromoted exploration; no cherry-picking a few positive single months. Code and score saved.
4. **One hindsight-oracle feasibility analysis** Jan–Jul: exactly 57,527,562 original quotes, five-second first observed quote, first actual quote >=250ms later to enter, first possible opposing exit quote >=another 250ms later, true observed bid/ask extrema over next 60s, $0.52/oz extra research fee; source spread ceiling <=$0.80/oz. This deliberately uses future extrema **OFFLINE ONLY** and has no trading call. July's fraction of samples with a hindsight best after-cost payout >=$2.10 is **7.06%**, versus **29.52%** in March—about **{positive_ratio:.2f}x** in availability. This supports OWNER'S different-month-conditions observation WITHOUT ever feeding month number or future outcomes to an entry decision.
5. **Retroactive source capacity accounting** reserves a full 60-second slot for each selected prior hindsight event and tests 1/2/4/5/6/7/8/16 slots. 8-slot count-only feasibility is thus a specific directional-knowledge **research upper reference**, not realized profit and not a certification that 8 real slots can survive $100 or meet Coinexx leverage/margin.

All tested rule and failure outputs are in this ZIP as **internal journal**. No negative result is falsely reported as profitable. Existing accepted HTF/sniper earnings remain intact.

## What is genuinely missing for a 60% outcome

A. A single high-frequency **source→latency→real funding→stop/target/trail→actually settled paid close→new causal source rearm** event loop; currently G0 router and funding/active FourSessionV1 still separated.\nB. Causal classifier of **R9 SYNTH-like path persistence** that can predict a profitable *direction and reachable exit price*, conditioned on past quote efficiency, spread, completed H1/H4/M15/M5 structure and market change; the oracle establishes potential, not predictability. Avoid monthly identifiers and hindsight score input.\nC. True time-and-capacity constrained throughput with original MT5 symbol margin and ability to survive losses, non-overlapping funded trade accountability, no multi-account fantasy.\nD. Accurate MT5 server-day conversion and shared-book daily/weekly/month cash and trade counts before declaring 60% benchmark achievement.\nE. Genuine holdout beyond already-inspected Jan–Jul before deployment; August SEALED without user authorization.

**Do not promote:** No hypothesis passed 60% net and trade counts, 7/7 and 31/31 verified funded profitability. No modifications to any active EA, Vertical L1–L7, owner whitepaper, sealed August or official J0183.

## Reconstructible independent conceptual research source

Petrov, Golub & Olsen, *Agent-based modelling in directional-change intrinsic time*, Quantitative Finance (2020): https://doi.org/10.1080/14697688.2019.1669809 . This source describes event-based directional changes and overshoot scaling, NOT any proven gold trading profit. Chinese empirical context: Ma et al., *Volatility measurement with directional change in Chinese stock market*, Physica A (2017), https://doi.org/10.1016/j.physa.2016.11.113. Both are inspiration for falsifiable algorithms, not external certification.
'''
(out/'GRID0261_R9_60PCT_AUDIT_AND_RESEARCH_RESULT.md').write_text(report)
files=[root/'GRID0244_R9_SYNTH_MONTHLY_MT5_SERVER_CLOSED.csv',
      root/'grid0260/v1_grid_r9_60pct_economic_gate_0261.py',
      root/'grid0260/test_v1_grid_r9_60pct_economic_gate_0261.py',
      root/'grid0260/test_grid0261_true_quote_hindsight_quarantine.py',
      root/'grid0260/grid0261_intrinsic_time_research.py',
      root/'grid0260/grid0261_60pct_r9_oracle_reachability.py',
      root/'grid0260/grid0261_oracle_capacity_feasibility.py',
      root/'grid0260/grid0261_causal_past_geometry_fixed_exit.py',
      root/'grid0260/grid0261_spread_regime_adaptive.py']+sorted(p for p in out.glob('*.json') if p.name!='GRID0261_SHA256_MANIFEST.json')+[out/'GRID0261_R9_60PCT_AUDIT_AND_RESEARCH_RESULT.md',out/'GRID0261_SIXTY_PERCENT_R9_MONTHLY_AND_HINDSIGHT_SOURCE_FEASIBILITY.csv']
files=[p for p in files if p.exists()]
manifest={'stage':'GRID0261','status':'NON_PROMOTED_RESEARCH_ONLY','source':'Original Dukascopy Jan-Jul BidAsk, 57,527,562 native quote ticks, R9 SYNTH MT5 benchmark','not_a_profit_breakthrough':True,'files':{str(p.relative_to(root)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size} for p in files},'August':'SEALED','active_branch':'delta-A-alpha'}
(out/'GRID0261_SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
archive=root/'GRID0261_R9_60PCT_ORIGINAL_DUKAS_74_CASE_CAUSAL_AND_ORACLE_20261012.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in files:z.write(p,p.relative_to(root))
 z.write(out/'GRID0261_SHA256_MANIFEST.json',(out/'GRID0261_SHA256_MANIFEST.json').relative_to(root))
with zipfile.ZipFile(archive)as z:
 assert z.testzip() is None
 for name,info in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==info['sha256']
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(files),'sufficient_slot_floor_this_oracle':8,'total_60pct_r9_closes':131606,'target_r9_account_net_usd':185473.71},indent=2))
