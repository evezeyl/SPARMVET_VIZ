"""Run every `shiny run` launch command written in a document and report whether the app starts.

Why: launch commands in the test plan, the retest procedure and the guides are copied by
people. After a change of names or rules (ADR-091) a command can silently stop working.
This script finds the command lines, starts each one on a free port, waits for HTTP 200 (or
for the process to stop with a fatal message) and prints PASS or FAIL per command.

Only lines that start with one or more VAR=value settings (optionally after a leading "> " or
spaces) and contain `shiny run` are used. PYTHONPATH=. is added when missing. --reload is removed and the port is replaced.

Examples:
  .venv/bin/python assets/scripts/check_launch_commands.py .claude/tasks/test_plan_2026-06.md
  .venv/bin/python assets/scripts/check_launch_commands.py README.md DEPLOYMENT_CHECKLIST.md --timeout 40
"""
import argparse
import re
import shlex
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

LINE = re.compile(r"^[>\s`$]*((?:[A-Z_]+=\S*\s+)+.*shiny run .*)$")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def commands_in(path: Path):
    for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        m = LINE.match(line)
        if m:
            cmd = re.sub(r"\s+", " ", m.group(1).strip().rstrip("`"))
            yield n, cmd


def try_command(cmd: str, timeout: int) -> tuple[bool, str]:
    port = free_port()
    cmd = re.sub(r"--reload\s*", "", cmd)
    if "PYTHONPATH=" not in cmd:
        cmd = "PYTHONPATH=. " + cmd
    cmd = re.sub(r"--port\s+\d+", f"--port {port}", cmd)
    if "--port" not in cmd:
        cmd += f" --port {port}"
    proc = subprocess.Popen(["bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    start, status = time.time(), (False, "no answer before the timeout")
    try:
        while time.time() - start < timeout:
            if proc.poll() is not None:
                out = proc.stdout.read()
                fatal = [l for l in out.split("\n") if "[FATAL]" in l or "Error" in l]
                status = (False, (fatal[0] if fatal else out.strip().split("\n")[-1])[:160])
                break
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                    if r.status == 200:
                        status = (True, "HTTP 200")
                        break
            except Exception:
                time.sleep(1)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                proc.kill()
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path, help="documents that contain launch commands")
    ap.add_argument("--timeout", type=int, default=45, help="seconds to wait for each app (default 45)")
    ap.add_argument("--list", action="store_true", help="only list the commands found")
    args = ap.parse_args()
    failed = 0
    for f in args.files:
        for n, cmd in commands_in(f):
            if args.list:
                print(f"{f}:{n}: {cmd}")
                continue
            ok, msg = try_command(cmd, args.timeout)
            failed += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {f}:{n}  {msg}\n      {cmd[:150]}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
