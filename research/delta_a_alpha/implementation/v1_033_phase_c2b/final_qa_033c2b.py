from pathlib import Path
import json,subprocess,sys,hashlib,zipfile
R=Path(__file__).parent
p=json.loads((R/'REAL_049_UNION_PARITY_033C2B.json').read_text())
a=json.loads((R/'REAL_INTEGRATED_033C2B_SMOKE.json').read_text())
b=json.loads((R/'REAL_CAPPED_049_033C2B_SMOKE.json').read_text())
assert p['status']=='PASS_EXACT' and p['source_indices_original']==p['source_indices_ported']==13063
assert not p['mismatch_first5']
assert a['february_dukascopy_contiguous_quotes']==b['february_dukascopy_contiguous_quotes']==1136212
assert a['source_049_total_entry_events']==b['source_049_total_entry_events']==13063
assert a['actually_funded_119_cell_windows']==5 and b['actually_funded_119_cell_windows']==2
assert a['actually_funded_119_children']==20 and b['actually_funded_119_children']==10
assert b['049_source_cap_denials']==13042
cmd=[sys.executable,'-m','unittest','-q',*(f.stem for f in sorted(R.glob('test_*.py')))]
r=subprocess.run(cmd,cwd=R,capture_output=True,text=True,check=True)
assert 'Ran 47 tests' in r.stderr,r.stderr
manifest={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in R.glob('*.py')}
result={'unit':'DAA_033_PHASE_C2B_ENTRY_SOURCE_UNION_PARITY_AND_FUNDED_PARENT_SENSITIVITY',
 'status':'PASS_SOURCE_EVENT_PARITY__FULL_119_EARNED_MULTIPARENT_AND_V1_PARITY_OPEN',
 'all_regression_tests':47,'original_049_entry_union_on_real_ticks':p,
 'default_funded_diagnostic':a,'source_cap2_funded_diagnostic':b,
 'original_source_sha256_C2A_reference':'PHASE_C2A_QA_033.json','entry_source_identity_sha256':manifest,
 'gates_unfinished':['ORIGINAL_119_MULTIPARENT_AFTER_EARNED','ORIGINAL_084_CHILD_RESIDUAL_AND_QUOTE_ADMISSIONS','L2_TRUE_HTF_ROLES','L5_NATIVE_SPECIALISTS','L6_NATIVE_FAILURE_ENGINE','COINEXX_L7_BROKER','FULL_JAN_FEB_FUNDED_ECONOMICS','MQL5_BROKER_REAL_TICKS'],
 'original_owner_V1':'UNCHANGED','jan039_feb045_feb047':'IMMUTABLE_RESEARCH_REFERENCES','march':'HELD','august':'SEALED','september':'RESERVED'}
(R/'PHASE_C2B_QA_033.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'qa':'PASS','contract_tests':47,'real_feb_entry_parity':13063,'funded_parent_default':5,'funded_parent_cap2':2,'full_V1':False}))