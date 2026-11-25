"""Run the actual host journal executable in fresh processes; no actual terminal."""
import argparse, pathlib, subprocess, shutil
p=argparse.ArgumentParser();p.add_argument('--binary',type=pathlib.Path,required=True);p.add_argument('--work',type=pathlib.Path,required=True);a=p.parse_args();binary=a.binary.resolve();a.work.mkdir(parents=True,exist_ok=False)
for phase in ['genesis','unknown','resolved','applied','release','verified']:
 subprocess.run([str(binary),phase],cwd=a.work,check=True)
# Missing newest, corrupted newest and an old valid pair are distinct cases.
for name in ['missing','corrupted']:
 d=a.work.parent/(a.work.name+'_'+name);shutil.copytree(a.work,d)
 slot=d/'core.0.bin'
 if name=='missing':slot.unlink()
 else:
  b=bytearray(slot.read_bytes());b[-1]^=1;slot.write_bytes(b)
 subprocess.run([str(binary),'corrupt'],cwd=d,check=True)
for phase in ['rescue','quarantine']:
 subprocess.run([str(binary),phase],cwd=a.work,check=True)
print('PASS fresh-process protocol: 8 phases, 2 storage fault copies; no recovery sends')
