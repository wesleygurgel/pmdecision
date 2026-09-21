from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pm_decision.cli import _parse_arguments, _print_plan, main
from pm_decision.hours import TimeInterval, WorkdaySchedule
from pm_decision.planner import PlannedEntry, RunPlan

from tests.helpers import make_settings, make_timesheet


class FakeBrowser:
    def __init__(self, *args, **kwargs) -> None:
        self.headed = kwargs.get("headed", False)
        self.login = MagicMock()
        self.open_create_form = MagicMock(return_value=make_timesheet())

    def __enter__(self) -> "FakeBrowser":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


def test_parse_arguments_defaults_to_dry_run() -> None:
    parsed = _parse_arguments([])
    assert parsed.apply is False
    assert parsed.repo is None
    assert parsed.only_date is None
    assert parsed.headed is False


def test_parse_arguments_accepts_apply_only_date_repo_and_headed(tmp_path: Path) -> None:
    parsed = _parse_arguments(
        [
            "--apply",
            "--only-date",
            "2026-09-16",
            "--repo",
            str(tmp_path),
            "--headed",
        ]
    )
    assert parsed.apply is True
    assert parsed.only_date == date(2026, 9, 16)
    assert parsed.repo == tmp_path
    assert parsed.headed is True


def test_invalid_only_date_is_rejected() -> None:
    with pytest.raises(SystemExit):
        _parse_arguments(["--only-date", "16/09/2026"])


def test_dry_run_never_calls_apply_plan(monkeypatch) -> None:
    apply_plan = MagicMock()
    monkeypatch.setattr("pm_decision.cli.load_settings", lambda: make_settings())
    monkeypatch.setattr(
        "pm_decision.cli.resolve_repository_directory",
        lambda settings, override: None,
    )
    monkeypatch.setattr("pm_decision.cli.TimesheetBrowser", FakeBrowser)
    monkeypatch.setattr(
        "pm_decision.cli.build_run_plan",
        lambda **kwargs: RunPlan(
            timesheet=make_timesheet(),
            repository_path=None,
            detalhamento="detalhe",
            entries=[
                PlannedEntry(
                    day=date(2026, 9, 16),
                    schedule=WorkdaySchedule(
                        morning=TimeInterval("08:53", "12:35"),
                        afternoon=TimeInterval("13:35", "17:53"),
                    ),
                    intervals_to_save=(
                        TimeInterval("08:53", "12:35"),
                        TimeInterval("13:35", "17:53"),
                    ),
                )
            ],
        ),
    )
    monkeypatch.setattr("pm_decision.cli.apply_plan", apply_plan)
    assert main([]) == 0
    apply_plan.assert_not_called()


def test_apply_with_no_pending_days_does_not_save(monkeypatch) -> None:
    apply_plan = MagicMock()
    monkeypatch.setattr("pm_decision.cli.load_settings", lambda: make_settings())
    monkeypatch.setattr(
        "pm_decision.cli.resolve_repository_directory",
        lambda settings, override: None,
    )
    monkeypatch.setattr("pm_decision.cli.TimesheetBrowser", FakeBrowser)
    monkeypatch.setattr(
        "pm_decision.cli.build_run_plan",
        lambda **kwargs: RunPlan(
            timesheet=make_timesheet(),
            repository_path=None,
            detalhamento="detalhe",
            entries=[],
        ),
    )
    monkeypatch.setattr("pm_decision.cli.apply_plan", apply_plan)
    assert main(["--apply"]) == 0
    apply_plan.assert_not_called()


def test_apply_with_pending_days_saves_plan(monkeypatch) -> None:
    apply_plan = MagicMock()
    plan = RunPlan(
        timesheet=make_timesheet(),
        repository_path=None,
        detalhamento="detalhe",
        entries=[
            PlannedEntry(
                day=date(2026, 9, 16),
                schedule=WorkdaySchedule(
                    morning=TimeInterval("08:53", "12:35"),
                    afternoon=TimeInterval("13:35", "17:53"),
                ),
                intervals_to_save=(TimeInterval("08:53", "12:35"),),
            )
        ],
    )
    monkeypatch.setattr("pm_decision.cli.load_settings", lambda: make_settings())
    monkeypatch.setattr(
        "pm_decision.cli.resolve_repository_directory",
        lambda settings, override: None,
    )
    monkeypatch.setattr("pm_decision.cli.TimesheetBrowser", FakeBrowser)
    monkeypatch.setattr("pm_decision.cli.build_run_plan", lambda **kwargs: plan)
    monkeypatch.setattr("pm_decision.cli.apply_plan", apply_plan)
    assert main(["--apply"]) == 0
    apply_plan.assert_called_once()
    assert apply_plan.call_args.args[1] is plan


def test_main_returns_error_code_when_settings_are_missing(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "pm_decision.cli.load_settings",
        lambda: (_ for _ in ()).throw(ValueError("Defina PM_DECISION_USER")),
    )
    assert main([]) == 1
    captured = capsys.readouterr()
    assert "Defina PM_DECISION_USER" in captured.err


def test_print_plan_lists_pending_intervals(capsys) -> None:
    plan = RunPlan(
        timesheet=make_timesheet(),
        repository_path=Path("C:/repo"),
        detalhamento="[REPO] Trabalhei no desenvolvimento do projeto.",
        entries=[
            PlannedEntry(
                day=date(2026, 9, 16),
                schedule=WorkdaySchedule(
                    morning=TimeInterval("08:53", "12:35"),
                    afternoon=TimeInterval("13:35", "17:53"),
                ),
                intervals_to_save=(
                    TimeInterval("08:53", "12:35"),
                    TimeInterval("13:35", "17:53"),
                ),
            )
        ],
    )
    _print_plan(plan, apply_changes=False)
    output = capsys.readouterr().out
    assert "[DRY-RUN]" in output
    assert "16/09/2026" in output
    assert "08:53-12:35" in output
    assert "13:35-17:53" in output
    assert "[APPLY]" not in output
