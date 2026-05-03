import re
import subprocess
import sys
from pathlib import Path


def test_cli_integration(tmp_path):
    root = Path(__file__).resolve().parents[1]
    python = sys.executable
    db = tmp_path / "cli.db"

    def run_cmd(args):
        proc = subprocess.run([python, "-m", "cli.main"] + args, cwd=root, capture_output=True, text=True)
        return proc

    # add
    r = run_cmd(["add", "CLI item", "--db", str(db)])
    assert r.returncode == 0, r.stderr
    m = re.search(r"Created ID (\d+)", r.stdout)
    assert m, r.stdout
    tid = int(m.group(1))

    # list contains item
    r = run_cmd(["list", "--db", str(db)])
    assert "CLI item" in r.stdout

    # mark done
    r = run_cmd(["done", str(tid), "--db", str(db)])
    assert r.returncode == 0

    r = run_cmd(["list", "--db", str(db)])
    assert "[x]" in r.stdout

    # delete
    r = run_cmd(["delete", str(tid), "--db", str(db)])
    assert r.returncode == 0

    r = run_cmd(["list", "--db", str(db)])
    assert "CLI item" not in r.stdout
