"""DELTA R037 14B specialist-parent provenance / SORB readiness decision.

No tick replay and no threshold search. This bounded decision consumes only durable
provenance freezes plus Checkpoint 14A. It prevents endless same-sample historical
recuts while preserving the distinction between exact historical parity and a
non-promoting surrogate-parent research lane.
"""
from __future__ import annotations
import argparse, json, os, tempfile
from pathlib import Path

SCHEMA='delta-r037-r032-specialist-parent-residual-provenance-sorb-readiness-evidence-14b-v1'

def atomic_write_json(path:Path,obj:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=None
    try:
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',dir=path.parent,prefix='.'+path.name+'.',suffix='.tmp',delete=False) as f:
            tmp=f.name; json.dump(obj,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path); tmp=None
    finally:
        if tmp:
            try: os.unlink(tmp)
            except FileNotFoundError: pass

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--evidence',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    ev=json.loads(a.evidence.read_text())
    if ev.get('schema')!=SCHEMA: raise SystemExit('14B evidence schema mismatch')
    freezes=ev['specialist_provenance_freezes']
    if set(freezes)!={'DH05_S06','DH02_S11','DH02_S08','DH03_S06'}: raise SystemExit('14B specialist set mismatch')
    exhausted=all((not x['exact_historical_parity']) and (not x['further_same_sample_recuts']) for x in freezes.values())
    p=ev['parent_14a']
    if p['exact_historical_parent_parity'] is not False: raise SystemExit('14A unexpectedly exact; 14B decision no longer applicable')
    scheduler=p['leading_scheduler']
    if scheduler!='BACKBONE_FIRST_FLAT_ONLY_CONFIG_ORDER': raise SystemExit('14A leading scheduler fingerprint changed')
    residual={
      'c00_specialist_entry_gap':p['c00_specialist_entries_actual']-p['c00_specialist_entries_target'],
      's11_increment_gap':p['s11_increment_actual']-p['s11_increment_target'],
      's08_increment_gap':p['s08_increment_actual']-p['s08_increment_target'],
      'c03_increment_gap':p['c03_increment_actual']-p['c03_increment_target'],
      'c03_total_trade_gap':p['surrogate_c03_actual']['trades']-p['historical_c03_target']['trades'],
      'c03_official_win_gap':p['surrogate_c03_actual']['official_wins']-p['historical_c03_target']['official_wins'],
      'c03_net_gap':round(p['surrogate_c03_actual']['net_profit']-p['historical_c03_target']['net_profit'],2),
    }
    no_reconstructible_exact_path=bool(exhausted and residual['s11_increment_gap']>0 and residual['s08_increment_gap']>0)
    out={
      'schema':'delta-r037-r032-specialist-parent-provenance-sorb-readiness-decision-14b-v1',
      'status':'COMPLETE_PROVENANCE_LIMITED_PARENT_FREEZE_SURROGATE_SORB_LANE_AUTHORIZED' if no_reconstructible_exact_path else 'INCONCLUSIVE',
      'unit':ev['unit'],'parent_checkpoint':ev['parent_checkpoint'],'surface':ev['surface'],
      'numeric_retuning':False,'august_accessed':False,'all_four_specialist_recuts_exhausted':exhausted,
      'leading_scheduler':scheduler,'residual':residual,
      'decision':{
        'claim_exact_historical_parent_parity':False,
        'run_more_same_sample_historical_ownership_recuts':False if no_reconstructible_exact_path else True,
        'freeze_provenance_limited_parent':no_reconstructible_exact_path,
        'official_exact_parent_sorb_lane':'BLOCKED',
        'authorize_non_promoting_surrogate_parent_sorb_stage_a_screen':no_reconstructible_exact_path,
        'surrogate_parent':'14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS',
        'surrogate_lane_can_promote_final_delta_candidate':False,
        'reason':'All four specialist streams independently exhausted source-grounded reconstruction; 14A exact backbone plus scheduler localization isolates the remaining mismatch to unavailable historical specialist timing/ownership provenance. Continuing same-sample recuts would be retrospective fitting. Use the frozen 14A C03 surrogate only as a non-promoting research control so candidate families can be harvested without falsifying exact historical parity.',
        'next':'R037_SORB_SURROGATE_PARENT_STAGE_A_SCREEN' if no_reconstructible_exact_path else 'R037_R032_SPECIALIST_PARENT_PROVENANCE_REVIEW'
      },
      'sorb_integrated_replay_started':False,'mql5_authorized':False
    }
    atomic_write_json(a.output,out); print(json.dumps(out['decision'],separators=(',',':')))

if __name__=='__main__': main()
