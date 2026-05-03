import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli import main as cli_main


def test_cli_integration_cli_runner(tmp_path):
    runner = CliRunner()
    db = tmp_path / "cli.db"

    # init-db
    r = runner.invoke(cli_main.app, ["init-db", "--db", str(db)])
    assert r.exit_code == 0, r.output
    assert "Initialized DB" in r.output

    # add
    r = runner.invoke(cli_main.app, ["add", "CLI item", "--db", str(db)])
    assert r.exit_code == 0, r.output
    m = re.search(r"Created ID (\d+)", r.output)
    assert m, r.output
    tid = int(m.group(1))

    # list contains item
    r = runner.invoke(cli_main.app, ["list", "--db", str(db)])
    assert r.exit_code == 0
    assert "CLI item" in r.output

    # mark done
    r = runner.invoke(cli_main.app, ["done", str(tid), "--db", str(db)])
    assert r.exit_code == 0
    assert f"Marked {tid}" in r.output

    r = runner.invoke(cli_main.app, ["list", "--db", str(db)])
    assert "[x]" in r.output

    # invalid id should fail
    r = runner.invoke(cli_main.app, ["done", "9999", "--db", str(db)])
    assert r.exit_code != 0
    assert "id not found" in r.output or "ValueError" in r.output

    # delete
    r = runner.invoke(cli_main.app, ["delete", str(tid), "--db", str(db)])
    assert r.exit_code == 0
    assert f"Deleted {tid}" in r.output

    r = runner.invoke(cli_main.app, ["list", "--db", str(db)])
    assert "CLI item" not in r.output

    # add with empty title should error (service raises ValueError)
    r = runner.invoke(cli_main.app, ["add", "", "--db", str(db)])
    assert r.exit_code != 0
    assert "title required" in r.output or "ValueError" in r.output
