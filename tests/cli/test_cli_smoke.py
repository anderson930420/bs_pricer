from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_price_no_persist(tmp_path: Path) -> None:
    # run inside project root; adjust if needed
    proj = Path(__file__).resolve().parents[2]

    p = _run([sys.executable, "-m", "bs_pricer", "price", "--no-persist"], cwd=proj)
    assert p.returncode == 0
    assert "Call Price:" in p.stdout
    assert "Put Price:" in p.stdout


def test_cli_price_persist_and_show(tmp_path: Path) -> None:
    proj = Path(__file__).resolve().parents[2]
    db = tmp_path / "tmp.db"

    p1 = _run([sys.executable, "-m", "bs_pricer", "price", "--persist", "--db", str(db)], cwd=proj)
    assert p1.returncode == 0
    assert "run_id=" in p1.stdout

    # extract run_id
    run_id_line = next(line for line in p1.stdout.splitlines() if line.startswith("run_id="))
    run_id = run_id_line.split("=", 1)[1].strip()

    p2 = _run([sys.executable, "-m", "bs_pricer", "show", "--db", str(db), "--run-id", run_id], cwd=proj)
    assert p2.returncode == 0
    assert "Outputs:" in p2.stdout
    assert run_id in p2.stdout


def test_cli_history(tmp_path: Path) -> None:
    proj = Path(__file__).resolve().parents[2]
    db = tmp_path / "tmp.db"

    # create one persisted run
    _run([sys.executable, "-m", "bs_pricer", "price", "--persist", "--db", str(db)], cwd=proj)

    p = _run([sys.executable, "-m", "bs_pricer", "history", "--db", str(db), "--limit", "5"], cwd=proj)
    assert p.returncode == 0
    assert "run_id" in p.stdout

def test_cli_show_not_found_exits_1(tmp_path: Path) -> None:
    proj = Path(__file__).resolve().parents[2]
    db = tmp_path / "tmp.db"

    p = _run([sys.executable, "-m", "bs_pricer", "show", "--db", str(db), "--run-id", "nope"], cwd=proj)
    assert p.returncode == 1


def test_cli_price_validation_error_exits_2(tmp_path: Path) -> None:
    proj = Path(__file__).resolve().parents[2]
    # invalid S (domain policy: S>0)
    p = _run([sys.executable, "-m", "bs_pricer", "price", "--no-persist", "--S", "-1"], cwd=proj)
    assert p.returncode == 2
