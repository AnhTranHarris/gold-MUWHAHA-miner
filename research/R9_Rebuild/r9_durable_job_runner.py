#!/usr/bin/env python3
import argparse, datetime as dt, hashlib, json, os, platform, shlex, socket, subprocess, sys, threading
from pathlib import Path

def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha256(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(path: Path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+f".tmp.{os.getpid()}")
    with tmp.open("w",encoding="utf-8") as f:
        json.dump(obj,f,indent=2,sort_keys=True); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def git(repo: Path,*args):
    try: return subprocess.check_output(["git","-C",str(repo),*args],text=True,stderr=subprocess.STDOUT).strip()
    except Exception: return None

def main():
    ap=argparse.ArgumentParser(description="Durable wrapper for one bounded R9 research job.")
    ap.add_argument("--job-spec",required=True)
    ap.add_argument("--repo-root",required=True)
    ap.add_argument("--checkpoint-root",required=True)
    ns=ap.parse_args()
    repo=Path(ns.repo_root).resolve(); checkpoint_root=Path(ns.checkpoint_root).resolve()
    spec_path=Path(ns.job_spec).resolve(); spec=json.loads(spec_path.read_text(encoding="utf-8"))
    job_id=spec["job_id"]; safe="".join(c for c in job_id if c.isalnum() or c in "-_.")
    if safe!=job_id or not job_id: raise SystemExit("invalid job_id")
    job_dir=checkpoint_root/job_id; job_dir.mkdir(parents=True,exist_ok=True)
    manifest=job_dir/"manifest.json"; heartbeat=job_dir/"heartbeat.json"; log_path=job_dir/"worker.log"; lock_path=job_dir/"RUNNING.lock"
    if manifest.exists():
        old=json.loads(manifest.read_text(encoding="utf-8"))
        if old.get("status")=="COMPLETED_LOCAL":
            print(json.dumps({"job_id":job_id,"status":"ALREADY_COMPLETED_LOCAL","manifest":str(manifest)})); return 0
    try:
        fd=os.open(lock_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.write(fd,str(os.getpid()).encode()); os.close(fd)
    except FileExistsError:
        raise SystemExit(f"lock exists: {lock_path}")
    script_rel=Path(spec["script"])
    if script_rel.is_absolute() or ".." in script_rel.parts or script_rel.suffix.lower()!=".py": raise SystemExit("script must be a relative .py path")
    allowed_root=(repo/"research"/"R9_Rebuild").resolve(); script=(repo/script_rel).resolve()
    if not str(script).startswith(str(allowed_root)) or not script.exists(): raise SystemExit(f"script outside allowlist or missing: {script}")
    args=[str(x) for x in spec.get("args",[])]; cmd=[sys.executable,str(script),*args]
    env=os.environ.copy()
    for k,v in spec.get("env",{}).items():
        k=str(k)
        if not k.startswith("R9_"): raise SystemExit(f"env key not allowed: {k}")
        env[k]=str(v)
    state={"job_id":job_id,"status":"STARTED","started_utc":utcnow(),"host":socket.gethostname(),"platform":platform.platform(),
           "python":sys.version,"pid":os.getpid(),"child_pid":None,"repo_root":str(repo),"git_branch":git(repo,"branch","--show-current"),
           "git_sha":git(repo,"rev-parse","HEAD"),"script":str(script_rel),"args":args,"command":cmd,"checkpoint_dir":str(job_dir),"source_spec":str(spec_path)}
    atomic_json(manifest,state)
    stop=threading.Event()
    def beat():
        while not stop.wait(20):
            atomic_json(heartbeat,{"job_id":job_id,"status":"RUNNING_VERIFIED","heartbeat_utc":utcnow(),"supervisor_pid":os.getpid(),"child_pid":state.get("child_pid")})
    th=threading.Thread(target=beat,daemon=True); th.start()
    rc=999
    try:
        with log_path.open("a",encoding="utf-8",buffering=1) as log:
            log.write(f"[{utcnow()}] START {shlex.join(cmd)}\n")
            proc=subprocess.Popen(cmd,cwd=str(repo),stdout=log,stderr=subprocess.STDOUT,env=env)
            state["child_pid"]=proc.pid; state["status"]="RUNNING_VERIFIED"; atomic_json(manifest,state)
            rc=proc.wait(); log.write(f"[{utcnow()}] EXIT {rc}\n")
    finally:
        stop.set(); th.join(timeout=2)
    artifacts=[]
    for pattern in spec.get("artifact_globs",[]):
        for p in sorted(repo.glob(pattern)):
            if p.is_file(): artifacts.append({"path":str(p.relative_to(repo)),"bytes":p.stat().st_size,"sha256":sha256(p)})
    final=dict(state); final.update({"status":"COMPLETED_LOCAL" if rc==0 else "FAILED_RECOVERABLE","returncode":rc,"completed_utc":utcnow(),
                                    "artifacts":artifacts,"log_path":str(log_path),"log_sha256":sha256(log_path) if log_path.exists() else None})
    atomic_json(manifest,final); atomic_json(heartbeat,{"job_id":job_id,"status":final["status"],"heartbeat_utc":utcnow(),"child_pid":None})
    try: lock_path.unlink()
    except FileNotFoundError: pass
    print(json.dumps(final,indent=2)); return rc

if __name__=="__main__": raise SystemExit(main())
