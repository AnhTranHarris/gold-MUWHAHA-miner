"""Freeze classwise February risk controls (offline only; truth never shipped)."""
import json,hashlib,shutil
from pathlib import Path
import numpy as np
from r150_stage1_regime_probe import cuts
from r150_stage1_runtime import PINS,HEADS
ROOT=Path('/mnt/data/r150_repair_advanced');out=ROOT/'stage1_candidate';out.mkdir(parents=True,exist_ok=True)
model_root=ROOT/'models';cell=np.load('/mnt/data/r150_lean_candidate/staged/dukascopy_02.npz')
a={k:cell[k] for k in cell.files};cell.close()
scores={'guardian':np.load(model_root/'scores_control_02_SCORES.npz')['guardian']}
for h in ('opposite','neutral'):
    scores[h]=np.load(model_root/f'r120_conditional_02_{h}.npy')
c=cuts(a,scores);frozen={f'{side}|{"13_15" if session else "other"}':{'opposite':z[0],'neutral':z[1],'guardian_floor':.80} for (side,session),z in c.items()}
sources={'guardian':model_root/'scores_control_guardian.joblib',
         'opposite':model_root/'r120_conditional_opposite.joblib',
         'neutral':model_root/'r120_conditional_neutral.joblib'}
files={};hashes={}
for h,p in sources.items():
    dest=out/f'{h}.joblib';shutil.copy2(p,dest);files[h]=dest.name;hashes[h]=hashlib.sha256(dest.read_bytes()).hexdigest()
cfg={'status':'RESEARCH_ONLY_UNAPPROVED','broker':'dukascopy','clock':'T1','orders_authorized':False,
     'candidate':'R150_STAGE1_R120_PHASE_CONDITIONAL_JLM','parents':PINS,'model_files':files,'model_sha256':hashes,
     'cuts':frozen,'training':'DK Jan last40% after unsupervised R120 Jan first60%; CAL DK Feb',
     'limitations':'JLM parent trained historical four months; T1 pending proof missing in original classification score tapes; no MT5 approval'}
(out/'stage1_frozen.json').write_text(json.dumps(cfg,indent=2))
print(json.dumps({'frozen_groups':len(frozen),'model_hashes':hashes},indent=2))
