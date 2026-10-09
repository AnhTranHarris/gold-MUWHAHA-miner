"""036B checkpointed predefined 24-case quality/velocity frontier, fixed original candidate tape."""
from pathlib import Path
import sys,json,time, itertools
sys.path.insert(0,'/mnt/data/daa_jan_lattice_036')
from jan036_adaptive_cell_governor import engine,load,summarize
OUT=Path('/mnt/data/daa_jan_lattice_036')
def main():
 t,a,b,E,X,R,D,S=load()
 configs=list(itertools.product([384,512],[1000,2000,4000],[256,384],[1500,2500]))
 for perquote,width,cellcap,spread in configs:
  name=f'highvel_q{perquote}_w{width}_n{cellcap}_sp{spread}_lock12'
  path=OUT/(name+'.json')
  if path.exists():continue
  args=(perquote,12000,90000,128,1000,0,0,0,0,0,0,0,0,0,width,cellcap,spread,0)
  st=time.monotonic();rs=engine(t,a,b,E,X,R,D,S,*args);obj=summarize(name,args,t,rs)
  path.write_text(json.dumps(obj,indent=2)+'\n')
  print('CHECKPOINT',name,obj['net'],obj['trades'],obj['PF'],obj['gross_loss'],obj['equity_dd'],'s',round(time.monotonic()-st,2),flush=True)
if __name__=='__main__':main()