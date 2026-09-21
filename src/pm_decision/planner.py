from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from pm_decision.constants import EXPECTED_INTERVALS_PER_DAY
from pm_decision.detalhamento import build_detalhamento
from pm_decision.hours import (
    TimeInterval,
    WorkdaySchedule,
    afternoon_from_morning,
    generate_workday_schedule,
    is_morning_interval,
    morning_from_afternoon,
)
from pm_decision.settings import Settings
from pm_decision.timesheet_browser import OpenTimesheet, TimesheetBrowser
from pm_decision.work_calendar import workdays_until


@dataclass(frozen=True)
class PlannedEntry:
    day: date
    schedule: WorkdaySchedule
    intervals_to_save: tuple[TimeInterval, ...]


@dataclass(frozen=True)
class RunPlan:
    timesheet: OpenTimesheet
    repository_path: Path | None
    detalhamento: str
    entries: list[PlannedEntry]


def build_run_plan(
    settings: Settings,
    timesheet: OpenTimesheet,
    today: date,
    repository_path: Path | None,
    only_date: date | None,
) -> RunPlan:
    detalhamento = build_detalhamento(settings, repository_path)
    pending_days = workdays_until(timesheet.month, timesheet.year, today)
    if only_date is not None:
        pending_days = [day for day in pending_days if day == only_date]
        if not pending_days:
            raise ValueError(
                f"{only_date.isoformat()} não é dia útil lançável "
                "(fim de semana, feriado ou futuro)."
            )
    entries: list[PlannedEntry] = []
    for day in pending_days:
        planned = _plan_day(day, timesheet.intervals_for(day))
        if planned is not None:
            entries.append(planned)
    if only_date is not None and not entries:
        raise ValueError(
            f"{only_date.isoformat()} já está completo (manhã e tarde lançadas)."
        )
    return RunPlan(
        timesheet=timesheet,
        repository_path=repository_path,
        detalhamento=detalhamento,
        entries=entries,
    )


def apply_plan(browser: TimesheetBrowser, plan: RunPlan) -> None:
    saved_intervals = 0
    for entry in plan.entries:
        try:
            browser.save_intervals(entry.day, list(entry.intervals_to_save), plan.detalhamento)
            saved_intervals += len(entry.intervals_to_save)
        except Exception as error:
            raise RuntimeError(
                f"Falha ao salvar {entry.day.isoformat()}. "
                f"Intervalos gravados neste run antes da falha: {saved_intervals}. "
                "Confira no PM Decision antes de repetir o dia."
            ) from error


def _plan_day(day: date, existing: list[TimeInterval]) -> PlannedEntry | None:
    if len(existing) >= EXPECTED_INTERVALS_PER_DAY:
        return None
    if len(existing) == 1:
        recorded = existing[0]
        if is_morning_interval(recorded):
            afternoon = afternoon_from_morning(recorded)
            return PlannedEntry(
                day=day,
                schedule=WorkdaySchedule(morning=recorded, afternoon=afternoon),
                intervals_to_save=(afternoon,),
            )
        morning = morning_from_afternoon(recorded)
        return PlannedEntry(
            day=day,
            schedule=WorkdaySchedule(morning=morning, afternoon=recorded),
            intervals_to_save=(morning,),
        )
    schedule = generate_workday_schedule()
    return PlannedEntry(
        day=day,
        schedule=schedule,
        intervals_to_save=schedule.intervals,
    )
