#!/usr/bin/env python3
import argparse, datetime as dt, json, os, shutil, socket, subprocess, sys, threading, time
from pathlib import Path

def utcnow(): return dt.datetime.now(dt.timezone.utc).isoformat()
def run(cmd,cwd=None): return subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

def atomic_json(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True),encoding="utf-8")
    os.replace(tmp,path)

def sync_remote(repo,branch):
    run(["git","fetch","origin",branch],cwd=repo)
    ahead=run(["git","rev-list","--count",f"origin/{branch}..HEAD"],cwd=repo)
    if ahead.returncode==0 and ahead.stdout.strip().isdigit() and int(ahead.stdout.strip())>0:
        if run(["git","push","origin",branch],cwd=repo).returncode!=0: return False
    if run(["git","status","--porcelain"],cwd=repo).stdout.strip(): return True
    run(["git","checkout",branch],cwd=repo)
    return run(["git","pull","--ff-only","origin",branch],cwd=repo).returncode==0

def push_with_retry(repo,branch,tries=12):
    for _ in range(tries):
        if run(["git","push","origin",branch],cwd=repo).returncode==0: return True
        run(["git","pull","--rebase","origin",branch],cwd=repo); time.sleep(30)
    return False

def read_json(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception: return {}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root",required=True); ap.add_argument("--branch",default="carson/r9-durable-runner")
    ap.add_argument("--checkpoint-root",required=True); ap.add_argument("--poll-seconds",type=int,default=60); ap.add_argument("--once",action="store_true")
    ns=ap.parse_args()
    repo=Path(ns.repo_root).resolve(); cp=Path(ns.checkpoint_root).resolve(); cp.mkdir(parents=True,exist_ok=True)
    queue=repo/"research"/"R9_Rebuild"/"jobs"/"pending"; results=repo/"research"/"R9_Rebuild"/"jobs"/"results"; dead=repo/"research"/"R9_Rebuild"/"jobs"/"deadletter"; results.mkdir(parents=True,exist_ok=True); dead.mkdir(parents=True,exist_ok=True)
    runner=repo/"research"/"R9_Rebuild"/"r9_durable_job_runner.py"; health=cp/"daemon_health.json"
    current={"job_id":None,"phase":"IDLE"}; stop=threading.Event()

    def daemon_beat():
        while not stop.wait(20):
            atomic_json(health,{"status":"ALIVE","host":socket.gethostname(),"pid":os.getpid(),"heartbeat_utc":utcnow(),**current})
    th=threading.Thread(target=daemon_beat,daemon=True); th.start()

    try:
        while True:
            current.update(job_id=None,phase="REMOTE_SYNC"); sync_remote(repo,ns.branch)
            queue.mkdir(parents=True,exist_ok=True); did=False
            for spec in sorted(queue.glob("*.json")):
                job=read_json(spec); jid=job.get("job_id")
                if not jid: continue
                result_dir=results/jid; remote_manifest=result_dir/"manifest.json"; rm=read_json(remote_manifest)
                if rm.get("status") in ("COMPLETED_LOCAL","VERIFIED_DURABLE"): continue

                blocked=False
                for dep in job.get("depends_on",[]):
                    dm=read_json(results/str(dep)/"manifest.json")
                    if dm.get("status") not in ("COMPLETED_LOCAL","VERIFIED_DURABLE"):
                        blocked=True
                        break
                if blocked: continue

                local_manifest=cp/jid/"manifest.json"; lm=read_json(local_manifest)
                attempt=int(lm.get("attempt",rm.get("attempt",0)))
                max_attempts=int(job.get("max_attempts",3))
                if lm.get("status")=="FAILED_RECOVERABLE" and attempt>=max_attempts:
                    dl=dead/f"{jid}.json"
                    if not dl.exists():
                        atomic_json(dl,{"job_id":jid,"status":"DEADLETTER","attempt":attempt,"max_attempts":max_attempts,"last_manifest":lm,"job_spec":job,"utc":utcnow()})
                        run(["git","add",str(dl.relative_to(repo))],cwd=repo)
                        if run(["git","diff","--cached","--quiet"],cwd=repo).returncode!=0:
                            run(["git","commit","-m",f"research: deadletter {jid} after {attempt} attempts"],cwd=repo); push_with_retry(repo,ns.branch)
                    continue
                backoff=int(job.get("retry_backoff_seconds",120))
                if lm.get("status")=="FAILED_RECOVERABLE" and local_manifest.exists() and time.time()-local_manifest.stat().st_mtime<backoff: continue

                did=True; current.update(job_id=jid,phase="EXECUTE")
                run([sys.executable,str(runner),"--job-spec",str(spec),"--repo-root",str(repo),"--checkpoint-root",str(cp)],cwd=repo)
                lm=read_json(local_manifest); result_dir.mkdir(parents=True,exist_ok=True)
                att=int(lm.get("attempt",attempt or 1))
                if local_manifest.exists():
                    shutil.copy2(local_manifest,result_dir/"manifest.json")
                    shutil.copy2(local_manifest,result_dir/f"manifest_attempt_{att:03d}.json")
                log=cp/jid/"worker.log"
                if log.exists(): shutil.copy2(log,result_dir/f"worker_attempt_{att:03d}.log")

                max_mb=float(job.get("publish_max_mb",20))
                for rel in job.get("publish_files",[]):
                    src=(repo/rel).resolve()
                    if src.exists() and src.is_file() and src.stat().st_size<=max_mb*1024*1024:
                        shutil.copy2(src,result_dir/src.name)

                current.update(phase="REMOTE_COMMIT")
                run(["git","add",str(result_dir.relative_to(repo))],cwd=repo)
                if run(["git","diff","--cached","--quiet"],cwd=repo).returncode!=0:
                    run(["git","commit","-m",f"research: {jid} {lm.get('status','UNKNOWN')} attempt {att}"],cwd=repo)
                    push_with_retry(repo,ns.branch)
            current.update(job_id=None,phase="IDLE")
            if ns.once: return 0
            time.sleep(5 if did else ns.poll_seconds)
    finally:
        stop.set(); th.join(timeout=2)
        atomic_json(health,{"status":"STOPPED","host":socket.gethostname(),"pid":os.getpid(),"heartbeat_utc":utcnow(),**current})

if __name__=="__main__": raise SystemExit(main())
