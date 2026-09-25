#!/usr/bin/env python3
import argparse, datetime as dt, hashlib, importlib.util, json, os, platform, shlex, shutil, socket, subprocess, sys, threading, time
from pathlib import Path

def utcnow(): return dt.datetime.now(dt.timezone.utc).isoformat()

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+f".tmp.{os.getpid()}")
    with tmp.open("w",encoding="utf-8") as w:
        json.dump(obj,w,indent=2,sort_keys=True); w.flush(); os.fsync(w.fileno())
    os.replace(tmp,path)

def git(repo,*args):
    try: return subprocess.check_output(["git","-C",str(repo),*args],text=True,stderr=subprocess.STDOUT).strip()
    except Exception: return None

def pid_alive(pid):
    if not pid: return False
    try:
        if os.name=="nt":
            q=subprocess.run(["tasklist","/FI",f"PID eq {int(pid)}","/NH"],text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
            return str(pid) in q.stdout and "No tasks" not in q.stdout
        os.kill(int(pid),0); return True
    except Exception: return False

def resolve_path(raw,repo,env):
    s=os.path.expandvars(str(raw))
    for k,v in env.items(): s=s.replace("${"+k+"}",str(v))
    p=Path(s).expanduser()
    return p.resolve() if p.is_absolute() else (repo/p).resolve()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--job-spec",required=True); ap.add_argument("--repo-root",required=True); ap.add_argument("--checkpoint-root",required=True)
    ns=ap.parse_args()
    repo=Path(ns.repo_root).resolve(); cp=Path(ns.checkpoint_root).resolve(); cp.mkdir(parents=True,exist_ok=True)
    spec_path=Path(ns.job_spec).resolve(); spec=json.loads(spec_path.read_text(encoding="utf-8"))
    job_id=spec["job_id"]; safe="".join(c for c in job_id if c.isalnum() or c in "-_.")
    if safe!=job_id or not job_id: raise SystemExit("invalid job_id")
    job_dir=cp/job_id; job_dir.mkdir(parents=True,exist_ok=True)
    manifest=job_dir/"manifest.json"; heartbeat=job_dir/"heartbeat.json"; stage=job_dir/"stage_state.json"; log_path=job_dir/"worker.log"; lock_path=job_dir/"RUNNING.lock.json"
    old={}
    if manifest.exists():
        try: old=json.loads(manifest.read_text(encoding="utf-8"))
        except Exception: old={}
        if old.get("status")=="COMPLETED_LOCAL":
            print(json.dumps({"job_id":job_id,"status":"ALREADY_COMPLETED_LOCAL"})); return 0
    attempt=int(old.get("attempt",0))+1

    if lock_path.exists():
        try: lk=json.loads(lock_path.read_text(encoding="utf-8"))
        except Exception: lk={}
        live=(lk.get("host")==socket.gethostname() and pid_alive(lk.get("pid")))
        age=time.time()-lock_path.stat().st_mtime
        stale_after=int(spec.get("stale_lock_seconds",300))
        if live or age<stale_after: raise SystemExit(f"active/nonstale lock exists: {lock_path}")
        os.replace(lock_path,job_dir/f"STALE_LOCK_{int(time.time())}.json")
    atomic_json(lock_path,{"job_id":job_id,"pid":os.getpid(),"host":socket.gethostname(),"attempt":attempt,"created_utc":utcnow()})

    env=os.environ.copy()
    for k,v in spec.get("env",{}).items():
        if not str(k).startswith("R9_"): raise SystemExit(f"env key not allowed: {k}")
        env[str(k)]=str(v)
    script_rel=Path(spec["script"]); allowed=(repo/"research"/"R9_Rebuild").resolve(); script=(repo/script_rel).resolve()
    if script_rel.is_absolute() or ".." in script_rel.parts or script_rel.suffix.lower()!=".py" or not str(script).startswith(str(allowed)) or not script.exists():
        raise SystemExit("script outside allowlist or missing")

    failures=[]; checked_inputs=[]
    free_gb=shutil.disk_usage(cp).free/(1024**3)
    if free_gb<float(spec.get("min_free_gb",1.0)): failures.append(f"free_disk_gb={free_gb:.2f}")
    for mod in spec.get("required_modules",[]):
        if importlib.util.find_spec(str(mod)) is None: failures.append(f"missing_module:{mod}")
    for item in spec.get("required_inputs",[]):
        ent={"path":item} if isinstance(item,str) else dict(item)
        p=resolve_path(ent["path"],repo,env); rec={"path":str(p),"exists":p.exists()}
        if p.exists() and p.is_file():
            rec["bytes"]=p.stat().st_size
            if ent.get("sha256"): rec["sha256"]=sha256(p); rec["sha_match"]=(rec["sha256"].lower()==str(ent["sha256"]).lower())
        checked_inputs.append(rec)
        if not p.exists(): failures.append(f"missing_input:{p}")
        elif ent.get("min_bytes") and p.stat().st_size<int(ent["min_bytes"]): failures.append(f"short_input:{p}")
        elif ent.get("sha256") and not rec.get("sha_match",False): failures.append(f"sha_mismatch:{p}")

    base={"job_id":job_id,"attempt":attempt,"host":socket.gethostname(),"platform":platform.platform(),"python":sys.version,
          "repo_root":str(repo),"git_branch":git(repo,"branch","--show-current"),"git_sha":git(repo,"rev-parse","HEAD"),
          "script":str(script_rel),"args":[str(x) for x in spec.get("args",[])],"source_spec":str(spec_path),"inputs":checked_inputs}
    atomic_json(stage,{**base,"phase":"PREFLIGHT","status":"PASS" if not failures else "FAIL","utc":utcnow(),"failures":failures})
    if failures:
        final={**base,"status":"FAILED_RECOVERABLE","failure_reason":"PREFLIGHT","failures":failures,"completed_utc":utcnow()}
        atomic_json(manifest,final); atomic_json(heartbeat,{"job_id":job_id,"status":"FAILED_RECOVERABLE","phase":"PREFLIGHT","heartbeat_utc":utcnow()})
        try: lock_path.unlink()
        except FileNotFoundError: pass
        print(json.dumps(final,indent=2)); return 2

    cmd=[sys.executable,str(script),*[str(x) for x in spec.get("args",[])]]
    state={**base,"status":"STARTED","phase":"COMPUTE","started_utc":utcnow(),"pid":os.getpid(),"child_pid":None,"command":cmd}
    atomic_json(manifest,state)
    stop=threading.Event()
    def beat():
        while not stop.wait(int(spec.get("heartbeat_seconds",20))):
            atomic_json(heartbeat,{"job_id":job_id,"attempt":attempt,"status":"RUNNING_VERIFIED","phase":state.get("phase"),"heartbeat_utc":utcnow(),
                                   "supervisor_pid":os.getpid(),"child_pid":state.get("child_pid"),"log_bytes":log_path.stat().st_size if log_path.exists() else 0})
    th=threading.Thread(target=beat,daemon=True); th.start()
    rc=999; reason=None
    try:
        with log_path.open("a",encoding="utf-8",buffering=1) as log:
            log.write(f"[{utcnow()}] ATTEMPT {attempt} START {shlex.join(cmd)}\n")
            proc=subprocess.Popen(cmd,cwd=str(repo),stdout=log,stderr=subprocess.STDOUT,env=env)
            state["child_pid"]=proc.pid; state["status"]="RUNNING_VERIFIED"; atomic_json(manifest,state)
            try: rc=proc.wait(timeout=int(spec.get("timeout_seconds",21600)))
            except subprocess.TimeoutExpired:
                reason="TIMEOUT"; proc.terminate()
                try: rc=proc.wait(timeout=30)
                except subprocess.TimeoutExpired: proc.kill(); rc=proc.wait()
            log.write(f"[{utcnow()}] EXIT {rc} reason={reason}\n")
    finally:
        stop.set(); th.join(timeout=2)

    state["phase"]="VALIDATE"; artifacts=[]; validation=[]
    for pattern in spec.get("artifact_globs",[]):
        for p in sorted(repo.glob(pattern)):
            if p.is_file(): artifacts.append({"path":str(p.relative_to(repo)),"bytes":p.stat().st_size,"sha256":sha256(p)})
    for item in spec.get("required_outputs",[]):
        ent={"path":item} if isinstance(item,str) else dict(item)
        p=resolve_path(ent["path"],repo,env); rec={"path":str(p),"exists":p.exists()}
        if p.exists() and p.is_file(): rec.update(bytes=p.stat().st_size,sha256=sha256(p))
        validation.append(rec)
        if not p.exists(): reason=reason or f"MISSING_OUTPUT:{p}"
        elif ent.get("min_bytes") and p.stat().st_size<int(ent["min_bytes"]): reason=reason or f"SHORT_OUTPUT:{p}"
    status="COMPLETED_LOCAL" if rc==0 and reason is None else "FAILED_RECOVERABLE"
    atomic_json(stage,{**base,"phase":"VALIDATE","status":"PASS" if status=="COMPLETED_LOCAL" else "FAIL","utc":utcnow(),
                       "returncode":rc,"failure_reason":reason,"required_outputs":validation})
    final={**state,"status":status,"phase":"LOCAL_COMMIT","returncode":rc,"failure_reason":reason,"completed_utc":utcnow(),
           "artifacts":artifacts,"required_outputs":validation,"log_path":str(log_path),"log_sha256":sha256(log_path) if log_path.exists() else None}
    atomic_json(manifest,final)
    atomic_json(heartbeat,{"job_id":job_id,"attempt":attempt,"status":status,"phase":"LOCAL_COMMIT","heartbeat_utc":utcnow(),"child_pid":None})
    try: lock_path.unlink()
    except FileNotFoundError: pass
    print(json.dumps(final,indent=2)); return 0 if status=="COMPLETED_LOCAL" else (rc if rc else 3)

if __name__=="__main__": raise SystemExit(main())
