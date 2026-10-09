"""Reproducible, offline C2A contract QA including source-archive integrity."""
import hashlib,json,zipfile,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).parent
PARENT=Path('/mnt/data/JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip')
assert PARENT.is_file()
SOURCE=['gamma02_profit_funded_surge_049.py','gamma02_profit_funded_surge_equity_051.py',
 'gamma02_ny17_quantum_minute_window_075.py','gamma02_083_heat_parent_ownership_084.py',
 'gamma02_dynamic_watchdog_router_119.py','gamma02_jan_watchdog119_grid_layer_refinement_131a.py',
 'gamma02_campaign_heartbeat_019.py','gamma02_intrinsic_cusum_pulse_024.py',
 'gamma02_rebreak_latency_017.py']
with zipfile.ZipFile(PARENT) as z:
 original={x:hashlib.sha256(z.read('032_source/'+x)).hexdigest() for x in SOURCE}
 local={x:hashlib.sha256((ROOT/'source'/x).read_bytes()).hexdigest() for x in SOURCE}
 assert original==local
flags=[]
for name in ('REAL_INTEGRATED_033C2_SMOKE.json','REAL_CAPPED_049_033C2_SMOKE.json'):
 r=json.loads((ROOT/name).read_text());flags.append(r)
assert all(r['february_dukascopy_contiguous_quotes']==1136212 for r in flags)
assert flags[0]['actually_funded_119_cell_windows']==4 and flags[1]['actually_funded_119_cell_windows']==2
assert flags[0]['actually_funded_119_children']==14 and flags[1]['actually_funded_119_children']==10
assert flags[1]['049_source_cap_denials']>0
cmd=[sys.executable,'-m','unittest','-q','test_v1_funded_core_033','test_original_heartbeat_parity_033','test_scorecard_033','test_broker_context_safety_033b','test_original_online_sources_033c','test_original_funded_lineage_033c2']
r=subprocess.run(cmd,cwd=str(ROOT),text=True,capture_output=True,check=True)
assert 'Ran 46 tests' in r.stderr
sha={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in ROOT.glob('*.py')}
result={'status':'PHASE_C2A_PARTIAL_ENGINEERING_TEST_PASS__FULL_049_UNION_119_PARENT_SOURCE_NOT_YET_PARITY',
 'source_sha256_exact_matching_JAN037_original':True,'original_sources_sha256':original,
 'unit_tests_ran':46,'unit_tests_passed':46,'original_049_051_capacity_selector_fixture_equivalence':True,
 'original_131c_real_feb_grid_parity_carried_from_C1':{'step250':40784,'step75':64896},
 'jan_warmup_quote_count':3900880,'feb_quote_count':1136212,
 'normal_surge':flags[0],'capped_source_stress':flags[1],
 'invariants':{'real_funded_parent_credit_only':'CONTRACT_PASS','original_049_union_candidate_manufacture':'NOT_YET_PORTED','original_119_multi_parent_admission':'NOT_YET_PORTED','native_L5_L6':'NOT_IMPLEMENTED','original_L2_roles':'NOT_CERTIFIED','Coinexx_broker_L7':'NOT_CERTIFIED','full_month_performance':'NOT_AVAILABLE','owner_V1_whitepaper':'UNCHANGED','JAN039_and_FEB045_FEB047':'UNCHANGED','march':'HOLD','august':'SEALED','september':'RESERVED'},
 'source_file_sha256':sha}
(ROOT/'PHASE_C2A_QA_033.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'tests':46,'original_source_sha256_count':len(original),'feb_ticks':1136212,'normal_parent_windows':4,'capped_parent_windows':2,'capped_source_denials':flags[1]['049_source_cap_denials']},indent=2))