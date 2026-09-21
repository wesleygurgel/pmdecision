from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import subprocess

from pm_decision.constants import TIME_FORMAT
from pm_decision.hours import TimeInterval
from pm_decision.settings import Settings
from pm_decision.timesheet_browser import OpenTimesheet, RecordedInterval

SEPTEMBER_2026 = date(2026, 9, 21)


def make_settings(**overrides) -> Settings:
    values = {
        "username": "wesley.oliveira",
        "password": "secret",
        "base_url": "https://app.firstdecision.com.br/pmdecision",
        "repositories_root": Path(r"C:\Users\Wesley-\Documents\Repositorios\first"),
        "openai_api_key": None,
        "openai_model": "gpt-4o-mini",
        "folder_picker_timeout_seconds": 60,
    }
    values.update(overrides)
    return Settings(**values)


def make_timesheet(
    *,
    month: int = 9,
    year: int = 2026,
    recorded_intervals: list[RecordedInterval] | None = None,
    client_label: str = "MGI",
    project_label: str = "MDIC",
    role_label: str = "Desenvolvedor Sênior",
    activity_label: str = "Desenvolvimento",
) -> OpenTimesheet:
    return OpenTimesheet(
        month=month,
        year=year,
        client_label=client_label,
        project_label=project_label,
        role_label=role_label,
        activity_label=activity_label,
        recorded_intervals=recorded_intervals or [],
    )


def recorded(day: date, start: str, end: str) -> RecordedInterval:
    return RecordedInterval(day=day, interval=TimeInterval(start=start, end=end))


def minutes_between(start: str, end: str) -> int:
    start_at = datetime.strptime(start, TIME_FORMAT)
    end_at = datetime.strptime(end, TIME_FORMAT)
    return int((end_at - start_at).total_seconds() // 60)


def init_git_repository(path: Path, subject: str, body: str = "") -> None:
    path.mkdir(parents=True, exist_ok=True)
    _run_git(path, ["init"])
    _run_git(path, ["config", "user.email", "tests@pm-decision.local"])
    _run_git(path, ["config", "user.name", "pm-decision-tests"])
    _run_git(path, ["config", "commit.gpgsign", "false"])
    (path / "README.md").write_text("test repository\n", encoding="utf-8")
    _run_git(path, ["add", "README.md"])
    message = subject if not body else f"{subject}\n\n{body}"
    _run_git(path, ["commit", "-m", message])


def _run_git(path: Path, arguments: list[str]) -> None:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=path,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"git {' '.join(arguments)} failed in {path}: {completed.stderr}"
        )
