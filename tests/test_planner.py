from datetime import date
from unittest.mock import MagicMock

import pytest

from pm_decision.hours import TimeInterval, WorkdaySchedule
from pm_decision.planner import PlannedEntry, RunPlan, apply_plan, build_run_plan, _plan_day
from tests.helpers import SEPTEMBER_2026, make_settings, make_timesheet, recorded


def test_empty_month_plans_all_workdays_until_today_with_two_intervals() -> None:
    plan = build_run_plan(
        settings=make_settings(),
        timesheet=make_timesheet(),
        today=SEPTEMBER_2026,
        repository_path=None,
        only_date=None,
    )
    planned_days = [entry.day for entry in plan.entries]
    assert date(2026, 9, 7) not in planned_days
    assert date(2026, 9, 5) not in planned_days
    assert date(2026, 9, 22) not in planned_days
    assert planned_days[0] == date(2026, 9, 1)
    assert planned_days[-1] == date(2026, 9, 21)
    assert all(len(entry.intervals_to_save) == 2 for entry in plan.entries)


def test_complete_days_are_not_planned_again() -> None:
    complete = date(2026, 9, 16)
    timesheet = make_timesheet(
        recorded_intervals=[
            recorded(complete, "08:48", "12:00"),
            recorded(complete, "13:00", "17:48"),
        ]
    )
    plan = build_run_plan(
        settings=make_settings(),
        timesheet=timesheet,
        today=SEPTEMBER_2026,
        repository_path=None,
        only_date=None,
    )
    assert complete not in [entry.day for entry in plan.entries]


def test_day_with_only_morning_gets_complementary_afternoon() -> None:
    day = date(2026, 9, 16)
    planned = _plan_day(day, [TimeInterval(start="08:53", end="12:35")])
    assert planned is not None
    assert planned.intervals_to_save == (TimeInterval(start="13:35", end="17:53"),)
    assert planned.schedule.morning == TimeInterval(start="08:53", end="12:35")
    assert planned.schedule.afternoon == TimeInterval(start="13:35", end="17:53")


def test_day_with_only_afternoon_gets_complementary_morning() -> None:
    day = date(2026, 9, 17)
    planned = _plan_day(day, [TimeInterval(start="13:38", end="17:54")])
    assert planned is not None
    assert planned.intervals_to_save == (TimeInterval(start="08:54", end="12:38"),)


def test_day_with_two_intervals_is_skipped() -> None:
    planned = _plan_day(
        date(2026, 9, 18),
        [
            TimeInterval(start="09:05", end="13:44"),
            TimeInterval(start="14:44", end="18:05"),
        ],
    )
    assert planned is None


def test_only_date_restricts_plan_to_that_workday() -> None:
    plan = build_run_plan(
        settings=make_settings(),
        timesheet=make_timesheet(),
        today=SEPTEMBER_2026,
        repository_path=None,
        only_date=date(2026, 9, 16),
    )
    assert [entry.day for entry in plan.entries] == [date(2026, 9, 16)]
    assert len(plan.entries[0].intervals_to_save) == 2


def test_only_date_on_weekend_or_holiday_raises() -> None:
    settings = make_settings()
    timesheet = make_timesheet()
    with pytest.raises(ValueError, match="não é dia útil lançável"):
        build_run_plan(settings, timesheet, SEPTEMBER_2026, None, date(2026, 9, 19))
    with pytest.raises(ValueError, match="não é dia útil lançável"):
        build_run_plan(settings, timesheet, SEPTEMBER_2026, None, date(2026, 9, 7))
    with pytest.raises(ValueError, match="não é dia útil lançável"):
        build_run_plan(settings, timesheet, SEPTEMBER_2026, None, date(2026, 9, 22))


def test_only_date_already_complete_raises() -> None:
    day = date(2026, 9, 16)
    timesheet = make_timesheet(
        recorded_intervals=[
            recorded(day, "08:48", "12:00"),
            recorded(day, "13:00", "17:48"),
        ]
    )
    with pytest.raises(ValueError, match="já está completo"):
        build_run_plan(make_settings(), timesheet, SEPTEMBER_2026, None, day)


def test_apply_plan_saves_only_pending_intervals_in_order() -> None:
    browser = MagicMock()
    day = date(2026, 9, 16)
    morning = TimeInterval(start="08:53", end="12:35")
    afternoon = TimeInterval(start="13:35", end="17:53")
    plan = RunPlan(
        timesheet=make_timesheet(),
        repository_path=None,
        detalhamento="[REPO] Trabalhei no desenvolvimento do projeto.",
        entries=[
            PlannedEntry(
                day=day,
                schedule=WorkdaySchedule(morning=morning, afternoon=afternoon),
                intervals_to_save=(afternoon,),
            )
        ],
    )
    apply_plan(browser, plan)
    browser.save_intervals.assert_called_once_with(day, [afternoon], plan.detalhamento)


def test_apply_plan_reports_how_many_intervals_were_saved_before_failure() -> None:
    browser = MagicMock()
    first_day = date(2026, 9, 16)
    second_day = date(2026, 9, 17)
    morning = TimeInterval(start="08:53", end="12:35")
    afternoon = TimeInterval(start="13:35", end="17:53")
    schedule = WorkdaySchedule(morning=morning, afternoon=afternoon)
    browser.save_intervals.side_effect = [None, RuntimeError("Hora inválida")]
    plan = RunPlan(
        timesheet=make_timesheet(),
        repository_path=None,
        detalhamento="detalhe",
        entries=[
            PlannedEntry(day=first_day, schedule=schedule, intervals_to_save=schedule.intervals),
            PlannedEntry(day=second_day, schedule=schedule, intervals_to_save=schedule.intervals),
        ],
    )
    with pytest.raises(RuntimeError, match="Intervalos gravados neste run antes da falha: 2"):
        apply_plan(browser, plan)


def test_open_timesheet_is_not_complete_with_a_single_interval() -> None:
    day = date(2026, 9, 16)
    timesheet = make_timesheet(recorded_intervals=[recorded(day, "08:53", "12:35")])
    assert day not in timesheet.complete_dates
    assert timesheet.intervals_for(day) == [TimeInterval(start="08:53", end="12:35")]
