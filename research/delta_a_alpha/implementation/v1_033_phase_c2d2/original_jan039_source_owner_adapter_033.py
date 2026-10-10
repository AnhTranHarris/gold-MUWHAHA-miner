"""Exact-source ownership integration JAN037 L3 -> pre-existing JAN039 S26/S27.

Original research authorities:
  JAN037 original gamma02_campaign_heartbeat_019.py, S=hour+10 source rule;
  JAN039 frozen JAN039_SELECTED_VERIFIED.json (source ID 26/27 rules);
  previously accepted source_native_s26_s27_033.py pure source-specific target/caps.

Do NOT infer JAN039 entire engine equivalence. This is a source-naming bridge
for a particular pre-existing mechanism, not an invented trading condition.
It uses no calendar month switch and never changes event ordinal, direction,
original hold/stop values, or downstream actual L7 physical position ledger.
"""
from __future__ import annotations
from dataclasses import replace
from typing import Iterable
from v1_funded_core_033c import FundedEngine, Quote, Structure, Proposal, Position, Close
from source_native_s26_s27_033 import S26, S27, SourceNativeS26S27Policy

# Exact original JAN037 Sxx ids, and existing verified JAN039 policy ownership.
# Never remap F045 aliases, even when source IDs happen to be numerically equal.
JAN039_IDENTITIES={
    'ORIGINAL_J037_S26':S26,
    'ORIGINAL_J037_S27':S27,
}

class OriginalJAN039OwnerIdentity:
    """A pure source-ID relay; it never manufactures a trading proposal."""
    def __init__(self, upstream):
        self.upstream=upstream
        self.remapped=0
        self.entry_events=[]
        self.realized=[]

    def on_market_quote(self,q:Quote,engine:FundedEngine):
        fn=getattr(self.upstream,'on_market_quote',None)
        if fn is not None:fn(q,engine)

    def propose(self,q:Quote,s:Structure,engine:FundedEngine)->Iterable[Proposal]:
        output=[]
        for p in self.upstream.propose(q,s,engine):
            if p.layer!='L3':
                output.append(p);continue
            newname=JAN039_IDENTITIES.get(p.source)
            if newname is None:
                output.append(p);continue
            output.append(replace(p,source=newname))
            self.remapped+=1
        return tuple(output)

    def on_funded_entry(self,pos:Position,q:Quote,s:Structure,engine:FundedEngine):
        self.entry_events.append((pos.id,pos.source,pos.entry_ms))
        fn=getattr(self.upstream,'on_funded_entry',None)
        if fn is not None:fn(pos,q,s,engine)

    def on_funded_close(self,close:Close,engine:FundedEngine):
        self.realized.append((close.position_id,close.net_usd,close.reason))
        self.upstream.on_funded_close(close,engine)


def exact_jan039_l3_chain(source_upstream):
    """Pre-existing source-native JAN039 caps/TP in one shared physical L7."""
    return SourceNativeS26S27Policy(OriginalJAN039OwnerIdentity(source_upstream))
