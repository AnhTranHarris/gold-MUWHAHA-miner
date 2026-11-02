#!/usr/bin/env python3
"""Hard scientific acceptance gate for the entire high-volume entry system.

For each source-month requires: >=85% corresponding R9 SYNTH completed trades,
>=80% valid within-30s profitable survivor on EVERY day, EVERY ISO week, and
month; positive net after modeled costs. No zero-trade day/week passes.
Do not use label oracle to route actual orders. Do not relabel sampled checks
as complete-month performance.
"""
from __future__ import annotations
import math
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
def acceptance(source,month,score):
    expected=math.ceil(.85*SYNTH[month]);n=score['selected'];good=score['30s_win_count']
    d=score['daily_passes'];nd=score['daily_total'];w=score['weekly_passes'];nw=score['weekly_total']
    return {'source':source,'month':month,'required_trades':expected,'actual_trades':n,
      'volume_pass':n>=expected,'monthly_survival_pass':bool(n and good/n>=.8),
      'daily_survival_pass':bool(nd and d==nd),'weekly_survival_pass':bool(nw and w==nw),
      'positive_pnl_pass':score['profit_net']>0,
      'APPROVED':bool(n>=expected and n and good/n>=.8 and nd and d==nd and nw and w==nw and score['profit_net']>0)}
