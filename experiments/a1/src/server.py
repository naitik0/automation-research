"""Start/stop the local llama-server for one model (protocol §3).

  python -m src.server start qwen3-4b      # detached; logs to runs/server_<model>.log
  python -m src.server stop
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

import requests

from .common import RUNS
from .models import LOCAL_URL, MODELS, server_command, wait_for_local

PIDFILE = RUNS / "server.pid.json"


def start(model_key: str) -> None:
    if MODELS[model_key]["kind"] != "local":
        raise SystemExit(f"{model_key} is not a local model")
    stop(quiet=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    log = open(RUNS / f"server_{model_key}.log", "a", encoding="utf-8")   # append: earlier sessions' logs are kept
    log.write(f"\n===== server start {datetime.now(timezone.utc).isoformat(timespec='seconds')} {model_key} =====\n")
    log.flush()
    flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
    p = subprocess.Popen(server_command(model_key), stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
    PIDFILE.write_text(json.dumps({"pid": p.pid, "model": model_key}))
    wait_for_local()
    props = requests.get(LOCAL_URL + "/props", timeout=30).json()
    print(json.dumps({"pid": p.pid, "model": model_key, "build": props.get("build_info"),
                      "model_path": props.get("model_path")}))


def stop(quiet: bool = False) -> None:
    if not PIDFILE.exists():
        if not quiet:
            print("no server pid file")
        return
    pid = json.loads(PIDFILE.read_text())["pid"]
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
    else:
        subprocess.run(["kill", str(pid)], capture_output=True)
    PIDFILE.unlink()
    if not quiet:
        print(f"stopped {pid}")


if __name__ == "__main__":
    {"start": lambda: start(sys.argv[2]), "stop": stop}[sys.argv[1]]()
