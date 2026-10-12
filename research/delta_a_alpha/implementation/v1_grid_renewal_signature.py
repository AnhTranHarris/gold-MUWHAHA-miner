"""Restored exact April136T0/T2 CAUSAL renewal state buckets; research only.

Original April 136 archive defines previous child source-normalized P and
hold-time H buckets. Original P is NOT independently validated Coinexx
account USD. Never silently bucket broker cash as April-normalized P or port
April outcome-selected profitable whitelist/rule-depth settings into V1.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Optional

ORIGINAL_SOURCE_UNIT='APRIL_136_RESEARCH_NORMALIZED_P'

@dataclass(frozen=True)
class RenewalSignature:
    rule_index:int
    depth:int
    prior_profit_bucket:int
    prior_hold_bucket:int
    parent_ticket_id:Optional[int]
    evidence_unit:str
    # Signature is a causal FEATURE, not a profitable renewal authorization.

def source_profit_bucket(value:Optional[float],*,unit:str)->int:
    if unit!=ORIGINAL_SOURCE_UNIT:
        raise ValueError('original 136 source-P bucketing requires explicit normalized unit')
    if value is None:return -1
    p=float(value)
    if not isfinite(p):raise ValueError('invalid/non-finite archived P')
    return 0 if p<=0 else 1 if p<.5 else 2 if p<1 else 3 if p<2 else 4

def hold_bucket(seconds:Optional[float])->int:
    if seconds is None:return -1
    h=float(seconds)
    if not isfinite(h) or h<0:raise ValueError('invalid hold seconds')
    return 0 if h<=30 else 1 if h<=60 else 2 if h<=120 else 3 if h<=180 else 4 if h<=300 else 5

def signature_from_original(*,rule_index:int,depth:int,
                            previous_source_p:Optional[float],
                            previous_h_seconds:Optional[float],
                            parent_ticket_id:Optional[int],
                            evidence_unit:str=ORIGINAL_SOURCE_UNIT)->RenewalSignature:
    if rule_index<0 or depth<1:raise ValueError('invalid rule/depth')
    if parent_ticket_id is None and (previous_source_p is not None or previous_h_seconds is not None):
        raise ValueError('cannot attribute prior child outcomes without closed parent')
    if parent_ticket_id is not None and (previous_source_p is None or previous_h_seconds is None):
        raise ValueError('incomplete prior closed child record')
    return RenewalSignature(rule_index,depth,
        source_profit_bucket(previous_source_p,unit=evidence_unit),
        hold_bucket(previous_h_seconds),parent_ticket_id,evidence_unit)

def broker_cash_context(proposal, funded_campaign)->dict:
    """Entry-known paid-closed CASH + holding time, no fake April cash/P conversion."""
    parent_id=proposal.prior_paid_close_id
    if parent_id is None:
        return {'parent_ticket_id':None,'verified_parent_available':False,
                'prior_profit_sign':None,'prior_hold_bucket':-1,
                'april_136_source_profit_bucket':None}
    close=funded_campaign.last_paid_close[proposal.side]
    if (close is None or close.ticket_id!=parent_id or close.close_ms>=proposal.quote_ms
            or close.realized_net_cash<=0 or close.duration_ms<0
            or not isfinite(close.realized_net_cash)):
        raise ValueError('paid-parent credit is not causally documented')
    return {'parent_ticket_id':parent_id,'verified_parent_available':True,
            'prior_profit_sign':1,
            'prior_hold_bucket':hold_bucket(close.duration_ms/1000),
            'april_136_source_profit_bucket':None,
            'broker_cash_recorded_usd':close.realized_net_cash}
