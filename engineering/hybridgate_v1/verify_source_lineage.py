"""Read only: validate registered original archives, source/model members and Stage5 pins."""
from pathlib import Path
import argparse,csv,hashlib,json,zipfile
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assets',type=Path,required=True);a=p.parse_args();here=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest();report={};err=[]
for name in ('RECOVERY_DEPENDENCIES.csv','SOURCE_ANCHORS.csv','MODEL_DEPENDENCIES.csv','SUPPORT_INVENTORY.csv'):
 rows=list(csv.DictReader((here/name).open()));ok=0
 for row in rows:
  try:
   if 'member' in row:
    with zipfile.ZipFile(a.assets/row['archive']) as z:b=z.read(row['member'])
    valid=len(b)==int(row['bytes']) and sha(b)==row['sha256']
   else:
    f=a.assets/row['local_name'];valid=f.stat().st_size==int(row['bytes']) and hashlib.file_digest(f.open('rb'),'sha256').hexdigest()==row['sha256']
   if not valid:raise ValueError('hash/length mismatch')
   ok+=1
  except Exception as e:err.append({'inventory':name,'record':row.get('member',row.get('local_name')),'error':str(e)})
 report[name]={'passed':ok,'total':len(rows)}
for key,v in json.loads((here/'DEPENDENCY_PINS.json').read_text()).items():
 try:
  f=a.assets/v['filename'];assert hashlib.file_digest(f.open('rb'),'sha256').hexdigest()==v['sha256'];
  with zipfile.ZipFile(f) as z:
   assert z.testzip() is None;m=json.loads(z.read('SHA256_MANIFEST.json'));assert len(m)==v['manifest_members_verified'];assert all(sha(z.read(n))==h for n,h in m.items());report[key]={'passed':len(m),'total':len(m)}
 except Exception as e:err.append({'archive':key,'error':str(e)})
f=a.assets/'R9_HYBRIDGATE_V1_STAGE5_RELEASE_GATES_QC_20261125.zip'
try:
 assert hashlib.file_digest(f.open('rb'),'sha256').hexdigest()=='7a6f0f752d26827694ad978f2c93db77f661ca67132d3df3f133dc0b386c18d3'
 with zipfile.ZipFile(f) as z:
  assert z.testzip() is None;m=json.loads(z.read('SHA256_MANIFEST.json'));assert len(m)==89;assert all(sha(z.read(n))==h for n,h in m.items());report['Stage5_release']={'passed':len(m),'total':len(m)}
except Exception as e:err.append({'archive':'Stage5_release','error':str(e)})
print(json.dumps({'verified':report,'failures':err},indent=2));raise SystemExit(bool(err))
