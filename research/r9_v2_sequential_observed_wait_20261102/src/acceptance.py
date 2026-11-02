#!/usr/bin/env python3
"""R9 v2 source/day/week/month strict first-15s/30s + SYNTH volume gate.
Read ledger statistics from fully executed on-policy single-position streams.
No oracle action volumes, daily inactivity never a free passing day.
"""
import math
R9_SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}

def inspect(run,source,month):
    floor=math.ceil(.85*R9_SYNTH[month]);m=run['month']
    monthly={'trades':m.get('closed',0),'correct15':m.get('CORRECT15',0),'correct30':m.get('CORRECT30',0)}
    monthly['volume_floor']=floor;monthly['volume_pass']=monthly['trades']>=floor
    for h in (15,30):monthly[f'rate{h}']=monthly[f'correct{h}']/monthly['trades'] if monthly['trades'] else 0.
    def windows(v):
        out={}
        for name,b in v.items():
            n=b.get('closed',0);good=b.get('CORRECT30',0)
            out[name]={'trades':n,'correct30':good,'rate30':good/n if n else 0,
                       'correct15':b.get('CORRECT15',0),
                       'rate15':b.get('CORRECT15',0)/n if n else 0,
                       'pass30':n>0 and good/n>=.8,
                       'pass15':n>0 and b.get('CORRECT15',0)/n>=.8}
        return out
    days=windows(run['byday']);weeks=windows(run['byweek'])
    return {'source':source,'month':month,'monthly':monthly,
      'daily':days,'weekly':weeks,
      'passes':{'volume':monthly['volume_pass'],
        'daily30':len(days)>0 and all(d['pass30'] for d in days.values()),
        'weekly30':len(weeks)>0 and all(d['pass30'] for d in weeks.values()),
        'monthly30':monthly['rate30']>=.8,
        'daily15':len(days)>0 and all(d['pass15'] for d in days.values()),
        'weekly15':len(weeks)>0 and all(d['pass15'] for d in weeks.values()),
        'monthly15':monthly['rate15']>=.8,
        'positive_net':m.get('net_microdollar',0)>0},
      'accept':False if run.get('status')!='TRAINED_FROZEN_ON_POLICY' else None}
