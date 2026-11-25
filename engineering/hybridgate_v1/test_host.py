"""Mechanical C++ compatibility harness. Does NOT compile MQL or test real terminal APIs."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,shutil,os
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--install',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--targets',nargs='+',choices=['core','ea','tester','journal','fault','dispatch','fill'],default=['core','ea','tester','journal','fault','dispatch','fill']);a=p.parse_args();here=Path(__file__).resolve().parent;out=a.build;out.mkdir(parents=True,exist_ok=False);inc=out/'include';inc.mkdir()
# Match prior Stage5 mechanical array transform, adding types used by the terminal adapter.
types=r'HG[56]\w+|MqlTick|uchar|int|long|double|float|uint|string'
def trans(s):
 s=re.sub(r'^#property.*$','',s,flags=re.M);s=re.sub(r'^input group.*$','',s,flags=re.M);s=re.sub(r'^input\s+','',s,flags=re.M);s=s.replace("D'2026.01.01 00:00'",'1767225600L')
 s=re.sub(r'#include <HybridGateV1/([^>]+)>',r'#include "\1"',s)
 s=re.sub(r'\b(const )?('+types+r') &(\w+)\[\]',lambda m:f'{m[1] or ""}std::vector<{m[2]}> &{m[3]}',s)
 s=re.sub(r'\b('+types+r') ((?:\w+\[\],)*\w+\[\]);',lambda m:';'.join('std::vector<'+m[1]+'> '+v[:-2] for v in m[2].split(','))+';',s)
 # Initialized global string arrays (manifest) are native C++ arrays; existing API overloads handle them.
 return s.replace('MqlTick g_raw[HG6_TICK_BATCH];','std::vector<MqlTick> g_raw(HG6_TICK_BATCH);').replace('float x[],f5[],p[8];','std::vector<float> x,f5;float p[8];').replace('const std::vector<int> &idx','const int *idx')
for src in (a.install/'MQL5/Include/HybridGateV1').glob('*.mqh'):(inc/src.name).write_text(trans(src.read_text()))
for src in (a.install/'MQL5/Scripts/HybridGateQC').glob('*.mqh'):
 if not (inc/src.name).exists():(inc/src.name).write_text(trans(src.read_text()))
shutil.copyfile(here/'host_compat.hpp',inc/'host_compat.hpp')
# Full original sealed 131072-quote fixture with the new live core, additionally exercise one actual fill path.
s=trans((a.install/'MQL5/Scripts/HybridGateQC/HG5CoreQC.mq5').read_text()).replace('"HG5Core.mqh"','"HG6Core.mqh"').replace('HG5Core core;','std::unique_ptr<HG6Core> core=std::make_unique<HG6Core>();').replace('core.','core->')
needle='if(!core->StepGroup(g,s,r,h,a))';assert needle in s
inject='''if(lo==10641){if(!core->BindActual(90001,HGQL(data,qp+16*10640),-1,(int)HGQI(data,qp+16*10640+8),1)||core->ActualState()!=2)return false;}
 if(lo==10641|| (lo>10640&&lo<10665&&core->ActualState()==2&&!did_restart)){
  if(!did_restart){std::vector<uchar> state,other;if(!core->ExportState(state))return false;auto restored=std::make_unique<HG6Core>();for(int k=0;k<88;k++){if(!HG5ReadVerified("HG5QC\\\\"+HG_ID[k]+".hg5p",HG_MODEL_SHA[k],67108864,bytes)||!restored->Load(k,bytes))return false;}
  if(!restored->Start(w,cap)||!restored->RestoreState(state)||!restored->ExportState(other)||state!=other||restored->ActualId()!=90001)return false;core=std::move(restored);did_restart=true;}}
 '''
s=s.replace('int si=0,pi=0,he=0,ae=0;','bool did_restart=false,actual_match=false,actual_closed=false;int si=0,pi=0,he=0,ae=0;').replace(needle,inject+needle)
s=s.replace('he++;}', '''if(h[i].id==1&&h[i].kind==1){if(core->ActualReason()!=h[i].why||core->ActualId()!=90001)return false;actual_match=true;}if(h[i].id==1&&h[i].kind==2){if(!core->ConfirmFlat(90001)||core->ActualState()!=0)return false;actual_closed=true;}he++;}''')
s=s.replace('if(si!=ns||pi!=np||he!=nh||ae!=na)return false;','if(si!=ns||pi!=np||he!=nh||ae!=na||!did_restart||!actual_match||!actual_closed)return false;')
(out/'core.cpp').write_text('#include "host_compat.hpp"\n'+s+'\nint main(){bool ok=HGQTest();Print(ok?"HG6 CORE: 131072 quotes, 4171 stages, 440 proposals, 1318 path events, 5220 account events, all arrays and actual path restart PASS":"HG6 CORE FAIL");return ok?0:1;}\n')
# Full EA event-pump shim: observation and explicit tester-only mock execution.
s=trans((a.install/'MQL5/Experts/HybridGateV1/GoldMuwahahaMiner_HybridGateV1.mq5').read_text())
(out/'ea.cpp').write_text('#include "host_compat.hpp"\n'+s+'\n'+(here/'host_ea_tests.cpp').read_text())
(out/'tester.cpp').write_text('#include "host_compat.hpp"\n'+s+'\n'+(here/'host_tester_tests.cpp').read_text())
(out/'fill.cpp').write_text((here/'host_actual_fill_tests.cpp').read_text())
(out/'dispatch.cpp').write_text('#include "host_compat.hpp"\n'+s+'\n'+(here/'host_dispatch_tests.cpp').read_text())
(out/'fault.cpp').write_text('#include "host_compat.hpp"\n'+s+'\n'+(here/'host_fault_tests.cpp').read_text())
(out/'journal.cpp').write_text((here/'host_journal_tests.cpp').read_text())
for target in a.targets:
 cmd=['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-parameter','-I'+str(inc),str(out/(target+'.cpp')),'-lcrypto','-o',str(out/target)]
 print('BUILD',target,flush=True);subprocess.run(cmd,check=True)
files=a.install/'MQL5/Files';work=out/'run';work.mkdir();(work/'HG5QC').symlink_to((files/'HG5QC').resolve(),target_is_directory=True)
for target in a.targets:
 print('RUN',target,flush=True)
 if target=='journal':subprocess.run([os.sys.executable,str(here/'test_journal_processes.py'),'--binary',str((out/target).resolve()),'--work',str((out/'journal_processes').resolve())],check=True)
 else:subprocess.run([str((out/target).resolve())],cwd=work,check=True)
 if target=='fault':
  partial=out/'partial_run';partial.mkdir();(partial/'HG5QC').symlink_to((files/'HG5QC').resolve(),target_is_directory=True);subprocess.run([str((out/target).resolve()),'partial'],cwd=partial,check=True)
print('PASS host compatibility compilation and fixture tests. Native MetaEditor/terminal not run.')
