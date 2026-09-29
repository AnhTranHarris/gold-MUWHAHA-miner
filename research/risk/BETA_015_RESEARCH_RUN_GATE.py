"""Prevent ungoverned new BETA research results from being called policy-compliant.

Not a substitute for actual replay. Fails closed if a simulation does not attest to
using the versioned PropRiskGuard enforcement and an independent replay QA check.
"""
from __future__ import annotations
from pathlib import Path
from typing import Mapping
import hashlib
import json
from BETA_015_PROP_POLICY_V1 import Policy, PolicyViolation

HERE=Path(__file__).resolve().parent
CONFIG=HERE/'BETA_015_PROP_POLICY_V1.json'

def config_sha256()->str:
    Policy.from_json(CONFIG)
    return hashlib.sha256(CONFIG.read_bytes()).hexdigest()

def assert_new_funded_replay_manifest(manifest:Mapping):
    """Requires actual per-quote guard and funding-stop evidence for NEW runs.

    This check verifies metadata integrity / obvious invariants; it does not
    prove every order used the guard. For that run unit tests + ledger audit.
    """
    p=Policy.from_json(CONFIG)
    r=manifest.get('prop_policy')
    if not isinstance(r,dict):raise PolicyViolation('Missing BETA015 policy manifest')
    if r.get('policy_id') != p.policy_id:raise PolicyViolation('Wrong policy version')
    if r.get('config_sha256') != config_sha256():raise PolicyViolation('Policy hash mismatch')
    if r.get('tick_by_tick_guard') is not True:raise PolicyViolation('Marked-equity guard must execute on every quote')
    if r.get('single_account') is not True:raise PolicyViolation('One chronological account required')
    if r.get('fixed_lots') != p.fixed_lots:raise PolicyViolation('Fixed .01 lots required')
    if r.get('initial_cash_usd') != p.initial_balance:raise PolicyViolation('Wrong initial cash')
    if r.get('commission_per_roundtrip_usd') != 2*p.fee_side:raise PolicyViolation('Wrong commission')
    if r.get('news_gate_status') not in ('NOT_EVALUATED','POINT_IN_TIME_VERIFIED'):
        raise PolicyViolation('Do not claim unverifiable news-compliance')
    if r.get('owner_mql5_authorization') not in (None,False):
        raise PolicyViolation('MQL5 candidate authorization is an independent owner approval gate')
    if r.get('source_data_through_month') not in ('2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07'):
        raise PolicyViolation('August is SEALED')
    funded=manifest.get('funded_account')
    if not isinstance(funded,dict):raise PolicyViolation('No funded account results')
    if funded.get('terminal_breach') and (funded.get('post_terminal_new_trades') != 0 or funded.get('post_terminal_deposits') != 0):
        raise PolicyViolation('Funded portfolio cannot trade or receive deposits after terminal stop')
    if funded.get('max_open_lots',0)>p.fixed_lots:
        raise PolicyViolation('Open portfolio exposure exceeds fixed .01 lot')
    if not manifest.get('independent_accounting_qa_passed'):
        raise PolicyViolation('Missing independent accounting assertions')
    if not isinstance(manifest.get('shadow_counterfactual'),dict):
        raise PolicyViolation('Shadow must be separately labeled—even if disabled')
    if manifest['shadow_counterfactual'].get('mixed_into_funded_totals') is not False:
        raise PolicyViolation('Never mix unfunded shadow with funded profit')
    return True

if __name__=='__main__':
    print(json.dumps({'config_sha256':config_sha256(),'policy_id':Policy.from_json(CONFIG).policy_id},indent=2))