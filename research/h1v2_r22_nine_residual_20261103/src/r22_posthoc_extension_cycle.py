"""R22 CYCLE-2: exploratory/hypothesis-generating only, not pre-registered OOS.
A broader 120/180/240s first-target horizon MAY improve retrospective capacity but
is NOT original R9/S1/R21 and must not be described as a trained as-of model.
Original source-verified eight data feeds and R21 R9 quotas remain unchanged.
"""
import argparse,sys
from pathlib import Path
sys.path.insert(0,'/mnt/data/h1v2_r22_nine_residual')
import r22_source_exact_rescue_v2 as v2
v2.LAB=Path('/mnt/data/h1v2_r22_nine_residual/cycle2')
v2.CASES=(
 ('F12_AFTERGAP0_Q8_CAP8000_H120_LAG100',0,8,120000,8000,100,0),
 ('F13_AFTERGAP0_Q8_CAP8000_H180_LAG100',0,8,180000,8000,100,0),
 ('F14_AFTERGAP0_Q8_CAP4000_H180_LAG100',0,8,180000,4000,100,0),
 ('F15_AFTERGAP0_Q8_CAP8000_H240_LAG100',0,8,240000,8000,100,0),
 ('F16_AFTERGAP0_Q8_CAP4000_H240_LAG100',0,8,240000,4000,100,0),
 ('F17_AFTERGAP0_Q1_CAP8000_H120_LAG100_DIAGNOSTIC',0,1,120000,8000,100,0),
 ('F18_AFTERGAP0_Q8_CAP4000_H180_LAG500_SLIP20',0,8,180000,4000,500,20),
 ('F19_AFTERGAP0_Q8_CAP8000_H120_LAG500_SLIP20',0,8,120000,8000,500,20),
)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',choices=v2.SOURCES,required=True);a.add_argument('--month',choices=v2.MONTHS,required=True)
 c=a.parse_args();v2.run_month(c.source,c.month)
