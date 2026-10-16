"""Exact SHA-256 allowlist for only the 16 user-supplied monthly XAUUSD sources.

Public repository deliberately excludes the private Google Drive per-file IDs.
The Drive-only research handoff maintains the original URLs and source manifest.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SourcePin:
    broker: str
    sha256: str

REGISTERED: dict[str,SourcePin] = {
    'XAUUSD_DUKAS_2026_01_ticks.csv.gz': SourcePin('dukascopy', 'd2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'),
    'XAUUSD_DUKAS_2026_02_ticks.csv.gz': SourcePin('dukascopy', 'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'),
    'XAUUSD_DUKAS_2026_03_ticks.csv.gz': SourcePin('dukascopy', '814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177'),
    'XAUUSD_DUKAS_2026_04_ticks.csv.gz': SourcePin('dukascopy', '30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f'),
    'XAUUSD_DUKAS_2026_05_ticks.csv.gz': SourcePin('dukascopy', '3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d'),
    'XAUUSD_DUKAS_2026_06_ticks.csv.gz': SourcePin('dukascopy', '34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2'),
    'XAUUSD_DUKAS_2026_07_ticks.csv.gz': SourcePin('dukascopy', 'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'),
    'XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz': SourcePin('coinexx', '1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8'),
    'XAUUSD_MT5_BROKER_2026_02_ticks_ALL.csv.gz': SourcePin('coinexx', '5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05'),
    'XAUUSD_MT5_BROKER_2026_03_ticks_ALL.csv.gz': SourcePin('coinexx', '3e9a03d97c6403036c4f5731e2e9eff43b8c4c9b25ac61adc6cc2147e3e79112'),
    'XAUUSD_MT5_BROKER_2026_04_ticks_ALL.csv.gz': SourcePin('coinexx', 'f04660a094aa2d9738300c409f7f1c85868d5415c3bb8be11f0026740e7dc3be'),
    'XAUUSD_MT5_BROKER_2026_05_ticks_ALL.csv.gz': SourcePin('coinexx', '3e39c2810a40858f17245f4e07b6e15a0b52bbb48320a94fbe123a77c6343e29'),
    'XAUUSD_MT5_BROKER_2026_06_ticks_ALL.csv.gz': SourcePin('coinexx', '3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4'),
    'XAUUSD_MT5_BROKER_2026_07_ticks_ALL.csv.gz': SourcePin('coinexx', 'd9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d'),
    'XAUUSD_MT5_BROKER_2026_08_ticks_ALL.csv.gz': SourcePin('coinexx', '8e337d18377c318de17ceb72d46bbfc976a29cef4571dfa3457d3ac7fc0e1c17'),
    'XAUUSD_MT5_BROKER_2026_09_ticks_ALL.csv.gz': SourcePin('coinexx', 'deaf191f65506178d501256f084a0ff4615fd21946f27ec1d9ee8f5e8c64b8ff'),
}

def verify(filename: str, broker: str, digest: str, allow_unregistered: bool=False) -> SourcePin | None:
    pin=REGISTERED.get(Path(filename).name)
    if pin is None:
        if allow_unregistered: return None
        raise ValueError('source absent from user-approved allowlist (testing: --allow-unregistered-input)')
    if broker!=pin.broker: raise ValueError('registered source belongs to a different broker')
    if digest!=pin.sha256: raise ValueError('SOURCE SHA-256 MISMATCH: abort rather than mix data')
    return pin
