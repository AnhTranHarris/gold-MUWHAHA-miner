"""Explicit filesystem configuration for R9 v2 research/recovery sources.

No research source directory is silently bound to a machine-specific /mnt/data
layout. Callers may pass an explicit path or set the documented environment
variables. Missing configuration fails closed with a precise error.
"""
from __future__ import annotations
import os
from pathlib import Path

PAIRED_ENV='R9_V2_PAIRED_ACTION_ROOT'
RESTORE_ENV='R9_V2_RESTORE_ROOT'
RAW_ENV='R9_V2_RAW_ROOT'

def _resolve(explicit,env_name,label,must_exist=True):
    value=explicit if explicit is not None else os.environ.get(env_name)
    if value is None or not str(value).strip():
        raise FileNotFoundError(f'{label} is not configured; pass an explicit path or set {env_name}')
    p=Path(value).expanduser().resolve()
    if must_exist and not p.is_dir():raise FileNotFoundError(f'{label} directory not found: {p}')
    return p

def paired_action_root(explicit=None,must_exist=True):return _resolve(explicit,PAIRED_ENV,'paired-action source root',must_exist)
def restore_root(explicit=None,must_exist=True):return _resolve(explicit,RESTORE_ENV,'legacy restore root',must_exist)
def raw_root(explicit=None,must_exist=True):return _resolve(explicit,RAW_ENV,'raw tick root',must_exist)

def artifact_stem(source,month,day=None):
    source=str(source).lower();month=str(month).zfill(2)
    if source not in ('coinexx','dukascopy'):raise ValueError('source')
    if not month.isdigit() or len(month)!=2:raise ValueError('month')
    return f'{source}_{month}' + (f'_{day}' if day else '')