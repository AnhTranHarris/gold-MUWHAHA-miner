"""H1V2 future-privileged teacher quality frontier, no predictor or deployable policy.

For each month start from already nonoverlapping H1V2 maximal-count selections.
Only remove (never add) selected trades so nonoverlap invariant holds, yielding
conservative retained-trade lower bound for stricter hindsight quality gates.
"""
import json, math
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/h1v2/results')
MONTHS=('01','02','06','07')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
MAX_MS=(1000,2000,3000,5000,10000,30000)
NET=(0.0,.10,.15,.20,.30,.50)
SPREAD=(.7,.8,1.0,1.5)

def run(root=ROOT):
    z={}
    for m in MONTHS:
        with np.load(root/f'h1v2_dukascopy_{m}_selected_exact_trace.npz') as d:
            z[m]={k:d[k].copy() for k in d.files}
        e=z[m]
        if len(e['entry_tick_ix'])>1:
            assert np.all(e['entry_tick_ix'][1:]>e['exit_tick_ix'][:-1]),'overlap'
        assert np.all(e['net']>0)
    rows=[]
    for ms in MAX_MS:
        for net in NET:
            for spr in SPREAD:
                by={};total=0;min_coverage=10.
                for m in MONTHS:
                    e=z[m];spread=e['entry_ask']-e['entry_bid'];n=int(((e['first_favorable_elapsed_ms']<=ms)&(e['net']>=net)&(spread<=spr+1e-5)).sum());floor=math.ceil(.8*SYNTH[m]);coverage=n/SYNTH[m]
                    by[m]={'selected':n,'floor':floor,'coverage':coverage,'floor_pass':n>=floor}
                    total+=n;min_coverage=min(min_coverage,coverage)
                rows.append({'first_hit_max_ms':ms,'net_min':net,'spread_max':spr,'by_month':by,'total_nonoverlap_retained':total,'every_month_floor_pass':all(y['floor_pass'] for y in by.values()),'minimum_vs_synth_coverage':min_coverage})
    passed=[r for r in rows if r['every_month_floor_pass']]
    pareto=sorted(passed,key=lambda r:(r['first_hit_max_ms'], -r['net_min'],r['spread_max']))
    out={'scope':'FUTURE_PRIVILEGED_ORACLE_GATE_ON_NONOVERLAPPING_ORIGINAL_WINNERS_NOT_A_POLICY','baseline_nonoverlapping':{m:len(z[m]['net']) for m in MONTHS},'tested_grid':len(rows), 'passing_grid':len(passed), 'best_fast':pareto[:15], 'all':rows, 'warning':'Retained entries satisfy historical label by original future selection. This is an in-sample quality frontier, not predictive precision.'}
    return out
if __name__=='__main__':
 o=run();p=Path('/mnt/data/h1v2_r2/results/H1V2_R2_ORACLE_QUALITY_FRONTIER.json');p.write_text(json.dumps(o,indent=2));print(json.dumps({k:o[k] for k in ['baseline_nonoverlapping','tested_grid','passing_grid','best_fast']},indent=2))
