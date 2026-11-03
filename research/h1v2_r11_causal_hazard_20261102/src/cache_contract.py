"""R11 content-addressed research artifact guard; no stale model resurrection.

Use before reusing any R6/R9 or new R11 fitted weights or scored blocks. Caller
must pin ORIGINAL source/feature/label paths, fit code and model role. Immutable
receipts are additive; this utility never overwrites legacy model files.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

def sha256(path):
    with Path(path).open('rb') as fh:
        return hashlib.file_digest(fh,'sha256').hexdigest()

def freeze_dependency_contract(files,*,feature_version,role,hyperparameters,calendar_split):
    if not files or not feature_version or not role or not calendar_split:
        raise ValueError('empty dependency contract')
    names=sorted(str(k) for k in files)
    if len(names)!=len(files):raise ValueError('duplicate role labels')
    raw={name:{'path':str(Path(files[name]).resolve()),'sha256':sha256(files[name])} for name in names}
    h={'feature_version':feature_version,'model_role':role,'sources':raw,
       'hyperparameters':hyperparameters,'calendar_split':calendar_split}
    serial=json.dumps(h,sort_keys=True,separators=(',',':'))
    h['contract_sha256']=hashlib.sha256(serial.encode('utf-8')).hexdigest()
    return h

def require_frozen_model(model_path,fit_receipt,actual_contract):
    p=Path(model_path)
    rec=json.loads(Path(fit_receipt).read_text())
    for k in ('feature_version','model_role','contract_sha256'):
        if rec.get(k)!=actual_contract.get(k):raise ValueError(f'stale {k}; FAIL CLOSED')
    if rec.get('sources')!=actual_contract.get('sources') or rec.get('calendar_split')!=actual_contract.get('calendar_split') or rec.get('hyperparameters')!=actual_contract.get('hyperparameters'):
        raise ValueError('fit dependence drift; FAIL CLOSED')
    if rec.get('model_sha256')!=sha256(p):raise ValueError('weight SHA mismatch; FAIL CLOSED')
    return True
