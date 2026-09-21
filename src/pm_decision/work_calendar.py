from __future__ import annotations

from datetime import date, datetime
from calendar import monthrange

import holidays

from pm_decision.constants import EXPECTED_INTERVALS_PER_DAY, HOLIDAY_COUNTRY_CODE


def brazilian_holidays(year: int) -> holidays.HolidayBase:
    return holidays.country_holidays(HOLIDAY_COUNTRY_CODE, years=year)


def is_workday(day: date, holiday_calendar: holidays.HolidayBase | None = None) -> bool:
    calendar = holiday_calendar or brazilian_holidays(day.year)
    if day.weekday() >= 5:
        return False
    return day not in calendar


def workdays_until(
    month: int,
    year: int,
    until: date,
    holiday_calendar: holidays.HolidayBase | None = None,
) -> list[date]:
    last_day_of_month = monthrange(year, month)[1]
    end = min(until, date(year, month, last_day_of_month))
    calendar = holiday_calendar or brazilian_holidays(year)
    days: list[date] = []
    current = date(year, month, 1)
    while current <= end:
        if is_workday(current, calendar):
            days.append(current)
        current = date.fromordinal(current.toordinal() + 1)
    return days


def missing_workdays(
    month: int,
    year: int,
    until: date,
    filled_dates: set[date],
    holiday_calendar: holidays.HolidayBase | None = None,
) -> list[date]:
    return [
        day
        for day in workdays_until(month, year, until, holiday_calendar)
        if day not in filled_dates
    ]


def dates_with_complete_entries(entries_by_date: dict[date, int]) -> set[date]:
    return {
        day
        for day, count in entries_by_date.items()
        if count >= EXPECTED_INTERVALS_PER_DAY
    }


def parse_brazilian_date(value: str) -> date:
    return datetime.strptime(value, "%d/%m/%Y").date()
