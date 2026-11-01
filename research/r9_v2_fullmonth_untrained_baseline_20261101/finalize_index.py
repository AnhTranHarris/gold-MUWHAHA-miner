import json,hashlib
from pathlib import Path
base=Path('/mnt/data/r9_v2_fullmonth_baseline_verified_20261101')
index=json.loads((base/'checkpoints/CHECKPOINT_INDEX.json').read_text())
ids={('coinexx','2026-01'):'1H-gXk65lGq1vYYZZ0syPTD9gUEfuLCOM',('coinexx','2026-02'):'1nCf6uL6flSDtAzW6viyAaMYacxGnLnMF',('coinexx','2026-06'):'1eHonseZjVg-S5otCW8lDpv-8zgypxUI4',('coinexx','2026-07'):'1I5UZdpVOD06-IdY36Mnl3EWXQ1L-EhH0',('dukascopy','2026-01'):'17fQThQQtguqX15HNv3OGCt49saI3VTs7',('dukascopy','2026-02'):'1HVahgCQmbOWsIy5tLRFvqXExAaWWePuL',('dukascopy','2026-06'):'1LRc8H7VGShSecdnFuFgKb6uvIxX2XC-A',('dukascopy','2026-07'):'1gHxihyyi5E2HzOrO0lo5CuqcVXRqXxG0'}
for x in index:
 x['drive_id']=ids[(x['source'],x['month'])]
 x['drive_url']='https://drive.google.com/file/d/'+x['drive_id']+'/view'
manifest={
 'checkpoint_status':'COMPLETE_EIGHT_NATIVE_MONTH_SOURCE_BACKUPS',
 'source_branch':'carson/r9-v2-high-volume-event-stream-repair-20261101',
 'entry_policy':'UNTRAINED streaming continuation/reversal specialists; not fitted Bayes/NP',
 'original_source_unchanged':True,
 'full_source_with_every_checkpoint':True,
 'teacher_runtime_uses':False,
 'threshold':'v2 85pct of R9 synthetic trades per month each broker',
 'observed_volume_pass':'8/8','observed_economic_pass':'0/8',
 'large_original_recovery_url':'https://drive.google.com/file/d/1A7F-l0NhdgtYYlmhLABGP1zt-0pyf-_4/view',
 'checkpoint_archives':index}
(base/'BASELINE_DRIVE_ARCHIVE_INDEX.json').write_text(json.dumps(manifest,indent=2))
readme=(base/'SOURCE_EXACT_BASELINE_README.md').read_text()
readme+='\n## Durable Google Drive exact-binary checkpoints\n\n'
for s in ('coinexx','dukascopy'):
 readme+=f'### {s.upper()}\n\n'
 for x in index:
  if x['source']==s:
   readme+=f"- {x['month']}: [{x['name']}]({x['drive_url']}) · {x['sha256']} · {x['trades']:,} trades · ${x['net']:,.2f} modeled net.\n"
readme+='\nThe eight checkpoint ZIPs contain the actual complete compressed ledgers and full v2/repair source; the Google Doc/README is a navigation aid, not a substitute for those files.\n'
(base/'BASELINE_README_WITH_DRIVE_LINKS.md').write_text(readme)
(base/'BASELINE_README_WITH_DRIVE_LINKS.txt').write_text(readme)
print('Saved index and complete README',len(readme), 'bytes')
