"""Package verified, additive R12D-Q source and UNABRIDGED replay receipts.

Never archives original massive raw feeds by inference or deletes any source;
archive references external original immutable raw source and full NPZ, by SHA.
"""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
HERE=Path('/mnt/data');R=HERE/'h1v2_r12';DEST=R/'archive';DEST.mkdir(exist_ok=True)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

assets=[];traces=[]
def add(src,inside,role,trace=False):
 p=Path(src);assert p.is_file(),p
 to=traces if trace else assets
 if any(x[1]==inside for x in to):raise ValueError(('COLLIDING_ARCHIVE_PATH',inside))
 to.append((p,inside,role))
for fn in ('r12_dense_requote.py','r12d_quota_priority.py','assemble_r12dq_full_fourmonths.py','r12d_crossfeed_acute_spread_audit.py',
           'r12b_broker_native_hour_probe.py','build_r12dq_recovery_archive.py','README_R12D_Q_SOURCE_EXACT.md'):
 add(R/'source'/fn,'NEW_ADD_ONLY_SOURCE/'+fn,'new tested source')
for fn in ('r12_tp_oracle.py','r12_quarter_priority_swap.py','r12_synth_quarter_fast.py','assemble_r12_all_quarter_forensic.py'):
 add(R/'source'/fn,'PARENT_FROZEN_R12_CONTROL/'+fn,'original R12 source copy, unchanged')
for fn in ('entry_contract.py','entry_survivability.py'):
 add(R/'upstream'/fn,'PINNED_R11_UPSTREAM/'+fn,'original exact dependencies; unmodified')
for fn in ('test_r12_tp_oracle.py','test_r12d_asof_and_priority.py'):
 add(R/'tests'/fn,'TESTS/'+fn,'executed mechanical regression')
for fn in ('H1V2_COMPLETE_DEEP_HOURLY_AUDIT_20261103.md',
            'H1V2 R11 APPEND-ONLY R&D EXECUTION AND RECOVERY LEDGER — 20261102.txt',
            'H1V2_R12_UNABRIDGED_APPEND_ONLY_PROGRESS_LEDGER_20261103.txt'):
 add(HERE/fn,'PRESERVED_FULL_ORIGINAL_RESEARCH/'+fn,'unabridged original audit or full ledger')
for fn in ('R12_COMPLETE_FOUR_MONTH_11520_QUARTER_EXECUTION_RECEIPT.json',
           'R12_ALL_11520_EXACT_UTC_QUARTERS_R9_S4_TP_FULL_MATRIX.csv',
           'R12DQ_ALL_FOUR_MONTH_COMPLETE_EVIDENCE_AND_EXECUTION_RECEIPT.json',
           'R12DQ_COMPLETE_ALL_11520_SOURCE_QUARTERS_S4_R12_R12DQ.csv',
           'R12DQ_COMPLETE_ALL_2880_SOURCE_HOURS_S4_R12_R12DQ.csv',
           'R12DQ_COMPLETE_ALL_208_PROVEN_INFEASIBLE_SOURCE_QUARTERS.csv',
           'R12D_XF_ALL_TEN_SOURCE_COUNT_STARVED_HOURS_R9_SYNTH_VS_DUKAS_SPREAD.csv',
           'R12D_XF_TEN_HOUR_CROSSFEED_SOURCE_AUDIT_RECEIPT.json',
           'R12B_NATIVE_R9_SYNTH_2026-02-02_06UTC_HINDSIGHT_PROBE.json'):
 add(R/'results'/fn,'ALL_FOUR_MONTH_EXACT_OUTPUTS/'+fn,'complete source raw joined evidence')
for month in ('01','02','06','07'):
 for prefix in (f'R12D_{month}_FULL_COMPLETE_DENSE_REQUOTE_ORACLE_RECEIPT.json',
                f'R12D_{month}_FULL_DENSE_THREE_ASOF_CLOCK_15MIN_MATRIX.csv',
                f'R12DQ_{month}_ALL_DISTINCT_MS_OBSERVED_COMPLETE_SCIENTIFIC_RECEIPT.json',
                f'R12DQ_{month}_ALL_DISTINCT_MS_OBSERVED_ALL_SOURCE_15MIN_QUOTAS.csv',
                f'R12DQ_{month}_ALL_DISTINCT_MS_OBSERVED_ALL_SOURCE_PROVEN_INFEASIBLE_15MIN.csv',
                f'R12_{month}_SYNTH_QUARTER_FULL_SOURCE_RECEIPT_FAST.json',
                f'R12_{month}_ORIGINAL_R9_SYNTH_ALL_ENTRY_EVENTS_CLOCKALIGNED_UTC.csv',
                f'R12_{month}_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv'):
  add(R/'results'/prefix,'MONTH_'+month+'/'+prefix,'all original month rows and individual original R9 source event times')
 for fn in (f'R12D_{month}_full_execution.log',f'R12DQ_{month}_execution.log',f'R12_{month}_synth_fast_execution.log'):
  if (R/'results'/fn).exists():add(R/'results'/fn,'EXECUTION_LOGS/'+fn,'unaltered stdout including original source checks')
 for v in ('FIRST50_OBSERVED','INTRABIN_SPREAD_NARROW','ALL_DISTINCT_MS_OBSERVED'):
  fn=f'R12D_{month}_{v}_FULL_SELECTED_QUOTE_TRACES.csv'
  add(R/'results'/fn,'FULL_ORIGINAL_DENSE_VARIANT_TRACES/'+fn,'full future-selected quote ordinals, no row loss',True)
 fn=f'R12DQ_{month}_ALL_DISTINCT_MS_OBSERVED_QUOTA_PRIORITY_FULL_SOURCE_TP_TRACE.csv'
 add(R/'results'/fn,'FULL_FINAL_QUOTA_PRIORITY_TRACES/'+fn,'final full source quote ordinal output, no row loss',True)
for fn in ('R12D_XF_execution.log','R12B_native_probe_execution.log','R12DQ_FULL_FOUR_MONTH_ASSEMBLY.log'):
 if (R/'results'/fn).exists():add(R/'results'/fn,'EXECUTION_LOGS/'+fn,'scientific record including failure repair')
for p in sorted((R/'atomic_r9_synth').glob('*.entry_receipt.json')):
 add(p,'EVERY_ORIGINAL_R9_SYNTH_DAILY_SOURCE_SHA_RECEIPT/'+p.name,'original exact daily SHA + every original R9 entry clock')
# Four large ORIGINAL full-observed labels are retained as separate original
# artifacts in MT5_EXPAND; they are NEVER silently omitted from recovery.
external={
 '01':{'id':'1YxNKD_mSJjXjvy8Yiit-jt_fkE-C76mj'},
 '02':{'id':'1vJuMiri5AGxfU7aTBLz10Jm1Iljp65bv'},
 '06':{'id':'1oFsfApt406ydtgAyJmqQta7nDNcy5xfH'},
 '07':{'id':'1KttWVH9X-PuRlzRaxSvGP3v4Y7sRzp_d'}}
for mon,r in external.items():
 p=R/'results'/f'R12D_{mon}_ALL_OBSERVED_INTRA250MS_EXACT_H15_H30_LABELS.npz'
 r.update({'title':p.name,'size_bytes':p.stat().st_size,'sha256':sha(p),
           'original_storage_url':f'https://drive.google.com/file/d/{r["id"]}/view',
           'external_by_design_due_to_large_binary_file':True})

def package(files,name):
 manifest={'classification':'SOURCE_EXACT_RECOVERY_READ_ONLY_HINDSIGHT_NOT_DEPLOYABLE',
           'original_R9_v2_runtime_sha':'ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0',
           'original_R12_branch_sha':'69215c4061a57fb4745404e2aeac0d0ff502eb03',
           'original_R11S5_parent_sha':'2bcd0372dfba415d7b28a84a3346011efbb32c2d',
           'external_unabridged_large_binary_labels':external,
           'members':{inside:{'sha256':sha(p),'size_bytes':p.stat().st_size,'role':role} for p,inside,role in files}}
 target=DEST/name
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for p,inside,role in files:z.write(p,inside)
  z.writestr('SOURCE_EXACT_RECOVERY_MEMBER_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(files)+1
  for k,v in manifest['members'].items():
   data=z.read(k);assert len(data)==v['size_bytes'] and hashlib.sha256(data).hexdigest()==v['sha256'],k
 return {'name':name,'absolute_path':str(target),'bytes':target.stat().st_size,
         'sha256':sha(target),'member_count':len(files)+1,'all_manifest_SHA_and_CRC_verified':True}

result={'source_and_fully_referenced_research':package(assets,'R12DQ_A_UNABRIDGED_SOURCE_ORIGINAL_AUDIT_11520_QUARTER_SCIENCE_20261103.zip'),
        'all_original_and_final_379291_full_quote_ordinal_traces':package(traces,'R12DQ_B_ALL_12_DENSE_VARIANT_TRACES_AND_FOUR_FINAL_SOURCE_ORDINAL_TRACES_20261103.zip'),
        'external_full_source_labels':external,'expected_original_R9_UTC_quarters':11520,'expected_R12DQ_final_trades':379291,
        'research_only_not_a_predictor':True}
rec=DEST/'R12DQ_SOURCE_EXACT_TWO_ARCHIVE_RECOVERY_MANIFEST.json';rec.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
