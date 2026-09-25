#!/usr/bin/env python3
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

def run(cmd,cwd=None):
    return subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

def main():
    ap=argparse.ArgumentParser(description="R9 durable daemon. Polls dedicated GitHub branch for allowlisted job specs.")
    ap.add_argument("--repo-root",required=True); ap.add_argument("--branch",default="carson/r9-durable-runner")
    ap.add_argument("--checkpoint-root",required=True); ap.add_argument("--poll-seconds",type=int,default=60); ap.add_argument("--once",action="store_true")
    ns=ap.parse_args()
    repo=Path(ns.repo_root).resolve(); cp=Path(ns.checkpoint_root).resolve(); cp.mkdir(parents=True,exist_ok=True)
    queue=repo/"research"/"R9_Rebuild"/"jobs"/"pending"; results=repo/"research"/"R9_Rebuild"/"jobs"/"results"; results.mkdir(parents=True,exist_ok=True)
    runner=repo/"research"/"R9_Rebuild"/"r9_durable_job_runner.py"
    while True:
        if not run(["git","status","--porcelain"],cwd=repo).stdout.strip():
            run(["git","fetch","origin",ns.branch],cwd=repo); run(["git","checkout",ns.branch],cwd=repo); run(["git","pull","--ff-only","origin",ns.branch],cwd=repo)
        queue.mkdir(parents=True,exist_ok=True); did=False
        for spec in sorted(queue.glob("*.json")):
            job=json.loads(spec.read_text(encoding="utf-8")); jid=job["job_id"]; result_dir=results/jid
            if (result_dir/"manifest.json").exists(): continue
            did=True
            run([sys.executable,str(runner),"--job-spec",str(spec),"--repo-root",str(repo),"--checkpoint-root",str(cp)],cwd=repo)
            local_manifest=cp/jid/"manifest.json"; result_dir.mkdir(parents=True,exist_ok=True)
            if local_manifest.exists(): shutil.copy2(local_manifest,result_dir/"manifest.json")
            log=cp/jid/"worker.log"
            if log.exists(): shutil.copy2(log,result_dir/"worker.log")
            max_mb=float(job.get("publish_max_mb",20))
            for rel in job.get("publish_files",[]):
                src=(repo/rel).resolve()
                if src.exists() and src.is_file() and src.stat().st_size<=max_mb*1024*1024: shutil.copy2(src,result_dir/src.name)
            run(["git","add",str(result_dir.relative_to(repo))],cwd=repo)
            if run(["git","diff","--cached","--quiet"],cwd=repo).returncode!=0:
                run(["git","commit","-m",f"research: persist durable job {jid}"],cwd=repo)
                for _ in range(5):
                    q=run(["git","push","origin",ns.branch],cwd=repo)
                    if q.returncode==0: break
                    run(["git","pull","--rebase","origin",ns.branch],cwd=repo); time.sleep(10)
        if ns.once: return 0
        time.sleep(5 if did else ns.poll_seconds)

if __name__=="__main__": raise SystemExit(main())
