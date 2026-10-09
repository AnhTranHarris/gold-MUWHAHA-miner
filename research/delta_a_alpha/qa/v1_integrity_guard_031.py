"""CI hard stop on editing the owner's V1 source or changing its eight layer names.

The parent repo's exact original Drive transcript is frozen and intentionally not
replaced with the derivative shorter whitepaper. No trade/PnL certification implied.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'research'/'delta_a_alpha'
LOCK=BASE/'governance'/'DAA_V1_HARDLOCK_031.json'
WHITEPAPER=BASE/'whitepapers'/'DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt'
MANIFEST=BASE/'artifacts'/'DAA_VERTICAL_GRID_SYSTEM_V1_MANIFEST.json'
RESTORE=BASE/'architecture'/'DAA_V1_EXACT_SOURCE_RESTORATION_030.json'
SRC=BASE/'runtime'/'v1_startup_contract_031.py'
EXPECTED=[
    'ORDERED TICK EXECUTION ROOT','SESSION-SPECIFIC GRID GEOMETRY',
    'COMPLETED MULTI-TIMEFRAME STRUCTURE','HOURLY HIGH-VOLUME HARVESTING',
    'WATCHDOG / REGIME RENEWAL','TREND-WITHIN-TREND NATIVE ROUTING',
    'WRONG-DIRECTION RECOVERY','PORTFOLIO HEAT / CAPITAL GOVERNOR',
]

def git_sha(blob:bytes):
    return hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()

def checks():
    lock=json.loads(LOCK.read_text())
    restore=json.loads(RESTORE.read_text())
    white=WHITEPAPER.read_bytes()
    old=json.loads(MANIFEST.read_text())
    text=white.decode('utf-8-sig')
    positions=[text.find('LAYER '+str(i)+' — '+name) for i,name in enumerate(EXPECTED)]
    source=SRC.read_text()
    return {
        'whole_exact_owner_whitepaper_git_blob':git_sha(white)==lock['canonical_git_blob_sha1'],
        'unaltered_original_manifest_git_blob':git_sha(MANIFEST.read_bytes())==lock['canonical_manifest_git_blob_sha1'],
        'original_L0_to_L7_read_in_order':min(positions)>=0 and positions==sorted(positions),
        'manifest_eight_original_stages':len(old['permanent_spine'])==8,
        'restored_source_map_eight_layers':len(restore['original_layer_order'])==8,
        'jan1_asof_owner_override':lock['owner_date_override']=='2026-01-01T00:00:00Z',
        'fivemin_not_forced_profit':lock['software_readiness_seconds']==300 and lock['profit_within_five_minutes_guaranteed'] is False,
        'no_loss_dependent_sizing':lock['martingale'] is False and lock['loss_dependent_lot_sizing'] is False,
        'offline_learner_not_gate':lock['online_learning_does_not_gate_first_scout'] is True,
        'source_adapter_only_no_orders':all(s not in source for s in ('OrderSend(', 'trade.Buy(', 'trade.Sell(')),
        'missing_real_history_must_fail':lock['missing_broker_history']=='FAIL_READINESS_NOT_FAKE_WARMUP_OR_AUTO_ADMIT',
        'sealed_august':lock['august_2026']=='SEALED',
        'baseline_not_certified':lock['full_integrated_economic_parity']=='NOT_CERTIFIED',
    }

if __name__=='__main__':
    state=checks()
    print(json.dumps({'passed':sum(state.values()),'total':len(state),'checks':state,'economic_certified':False},indent=2))
    raise SystemExit(0 if all(state.values()) else 2)