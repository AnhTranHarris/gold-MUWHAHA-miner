#!/usr/bin/env python3
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

def run(cmd,cwd=None):
    return subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

def sync_remote(repo,branch):
    # First retry any previously completed local commits that were not pushed.
    run(["git","fetch","origin",branch],cwd=repo)
    ahead=run(["git","rev-list","--count",f"origin/{branch}..HEAD"],cwd=repo)
    if ahead.returncode==0 and ahead.stdout.strip().isdigit() and int(ahead.stdout.strip())>0:
        q=run(["git","push","origin",branch],cwd=repo)
        if q.returncode!=0: return False
    if run(["git","status","--porcelain"],cwd=repo).stdout.strip(): return True
    run(["git","checkout",branch],cwd=repo)
    q=run(["git","pull","--ff-only","origin",branch],cwd=repo)
    return q.returncode==0

def push_with_retry(repo,branch,tries=12):
    for _ in range(tries):
        q=run(["git","push","origin",branch],cwd=repo)
        if q.returncode==0: return True
        run(["git","pull","--rebase","origin",branch],cwd=repo)
        time.sleep(30)
    return False

def main():
    ap=argparse.ArgumentParser(description="R9 durable daemon. Polls dedicated GitHub branch for allowlisted job specs.")
    ap.add_argument("--repo-root",required=True); ap.add_argument("--branch",default="carson/r9-durable-runner")
    ap.add_argument("--checkpoint-root",required=True); ap.add_argument("--poll-seconds",type=int,default=60); ap.add_argument("--once",action="store_true")
    ns=ap.parse_args()
    repo=Path(ns.repo_root).resolve(); cp=Path(ns.checkpoint_root).resolve(); cp.mkdir(parents=True,exist_ok=True)
    queue=repo/"research"/"R9_Rebuild"/"jobs"/"pending"; results=repo/"research"/"R9_Rebuild"/"jobs"/"results"; results.mkdir(parents=True,exist_ok=True)
    runner=repo/"research"/"R9_Rebuild"/"r9_durable_job_runner.py"
    while True:
        sync_remote(repo,ns.branch)
        queue.mkdir(parents=True,exist_ok=True); did=False
        for spec in sorted(queue.glob("*.json")):
            job=json.loads(spec.read_text(encoding="utf-8")); jid=job["job_id"]; result_dir=results/jid
            # Remote result present => scientifically already persisted; local checkpoint may be discarded safely.
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
                push_with_retry(repo,ns.branch)
        if ns.once: return 0
        time.sleep(5 if did else ns.poll_seconds)

if __name__=="__main__": raise SystemExit(main())
