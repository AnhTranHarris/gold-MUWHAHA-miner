import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pytest
from cache_contract import freeze_dependency_contract,require_frozen_model,sha256

def test_cache_invalidates_changed_training_schema_source(tmp_path):
 raw=tmp_path/'X.bin';raw.write_bytes(b'old')
 model=tmp_path/'fit.txt';model.write_text('fitted code')
 c=freeze_dependency_contract({'features':raw},feature_version='v11',role='BUY',hyperparameters={'rounds':23},calendar_split={'fit':['01']})
 receipt=tmp_path/'fit.json';receipt.write_text(json.dumps({**c,'model_sha256':sha256(model)}))
 assert require_frozen_model(model,receipt,c)
 raw.write_bytes(b'mutated')
 c2=freeze_dependency_contract({'features':raw},feature_version='v11',role='BUY',hyperparameters={'rounds':23},calendar_split={'fit':['01']})
 with pytest.raises(ValueError):require_frozen_model(model,receipt,c2)
