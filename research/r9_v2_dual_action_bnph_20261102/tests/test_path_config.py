import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pytest
from path_config import paired_action_root,restore_root,artifact_stem
from source_exact import path_for

def test_missing_source_root_fails_closed(monkeypatch):
    monkeypatch.delenv('R9_V2_PAIRED_ACTION_ROOT',raising=False)
    with pytest.raises(FileNotFoundError,match='R9_V2_PAIRED_ACTION_ROOT'):paired_action_root()

def test_explicit_source_root_and_artifact_stem(tmp_path):
    p=tmp_path/'R9_V2_PAIRED_ACTION_COINEXX_2026_01_FULL_CHECKPOINT.zip';p.write_bytes(b'x')
    assert path_for('coinexx','01',tmp_path)==p
    assert artifact_stem('Dukascopy',1,'2026-01-06')=='dukascopy_01_2026-01-06'

def test_restore_root_uses_environment(monkeypatch,tmp_path):
    monkeypatch.setenv('R9_V2_RESTORE_ROOT',str(tmp_path))
    assert restore_root()==tmp_path.resolve()