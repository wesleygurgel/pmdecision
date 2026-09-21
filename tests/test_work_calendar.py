from datetime import date

from pm_decision.work_calendar import (
    dates_with_complete_entries,
    is_workday,
    missing_workdays,
    parse_brazilian_date,
    workdays_until,
)


def test_weekends_are_not_workdays() -> None:
    assert not is_workday(date(2026, 9, 5))
    assert not is_workday(date(2026, 9, 6))
    assert is_workday(date(2026, 9, 21))


def test_brazilian_independence_day_is_not_a_workday() -> None:
    independence_day = date(2026, 9, 7)
    assert not is_workday(independence_day)
    days = workdays_until(9, 2026, date(2026, 9, 21))
    assert independence_day not in days


def test_workdays_until_today_excludes_future_weekend_and_holiday() -> None:
    days = workdays_until(9, 2026, date(2026, 9, 21))
    assert date(2026, 9, 22) not in days
    assert date(2026, 9, 5) not in days
    assert date(2026, 9, 7) not in days
    assert days[0] == date(2026, 9, 1)
    assert days[-1] == date(2026, 9, 21)
    assert date(2026, 9, 16) in days
    assert date(2026, 9, 18) in days


def test_missing_workdays_skips_already_filled_complete_days() -> None:
    filled = {date(2026, 9, 1), date(2026, 9, 2)}
    missing = missing_workdays(9, 2026, date(2026, 9, 4), filled)
    assert missing == [date(2026, 9, 3), date(2026, 9, 4)]


def test_dates_with_complete_entries_require_two_intervals() -> None:
    day = date(2026, 9, 16)
    assert dates_with_complete_entries({day: 1}) == set()
    assert dates_with_complete_entries({day: 2}) == {day}
    assert dates_with_complete_entries({day: 3}) == {day}


def test_parse_brazilian_date() -> None:
    assert parse_brazilian_date("16/09/2026") == date(2026, 9, 16)
