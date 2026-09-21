from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
import random

from pm_decision.constants import (
    ENTRY_TIME_END,
    ENTRY_TIME_START,
    LUNCH_DURATION,
    LUNCH_START_RANGE_BEGIN,
    LUNCH_START_RANGE_END,
    MORNING_INTERVAL_START_LIMIT,
    TIME_FORMAT,
    WORK_DURATION,
)


@dataclass(frozen=True)
class TimeInterval:
    start: str
    end: str


@dataclass(frozen=True)
class WorkdaySchedule:
    morning: TimeInterval
    afternoon: TimeInterval

    @property
    def intervals(self) -> tuple[TimeInterval, TimeInterval]:
        return (self.morning, self.afternoon)


def is_morning_interval(interval: TimeInterval) -> bool:
    start = datetime.strptime(interval.start, TIME_FORMAT).time()
    return start < MORNING_INTERVAL_START_LIMIT


def afternoon_from_morning(morning: TimeInterval) -> TimeInterval:
    entry = datetime.strptime(morning.start, TIME_FORMAT)
    lunch_end = datetime.strptime(morning.end, TIME_FORMAT) + LUNCH_DURATION
    exit_time = entry + WORK_DURATION + LUNCH_DURATION
    return TimeInterval(start=_format_clock(lunch_end), end=_format_clock(exit_time))


def morning_from_afternoon(afternoon: TimeInterval) -> TimeInterval:
    lunch_end = datetime.strptime(afternoon.start, TIME_FORMAT)
    lunch_start = lunch_end - LUNCH_DURATION
    exit_time = datetime.strptime(afternoon.end, TIME_FORMAT)
    entry = exit_time - WORK_DURATION - LUNCH_DURATION
    return TimeInterval(start=_format_clock(entry), end=_format_clock(lunch_start))


def generate_workday_schedule(randomizer: random.Random | None = None) -> WorkdaySchedule:
    rng = randomizer or random.Random()
    entry = _random_time_between(ENTRY_TIME_START, ENTRY_TIME_END, rng)
    lunch_start = _random_time_between(
        LUNCH_START_RANGE_BEGIN, LUNCH_START_RANGE_END, rng
    )
    lunch_end = lunch_start + LUNCH_DURATION
    exit_time = entry + WORK_DURATION + LUNCH_DURATION
    return WorkdaySchedule(
        morning=TimeInterval(
            start=_format_clock(entry),
            end=_format_clock(lunch_start),
        ),
        afternoon=TimeInterval(
            start=_format_clock(lunch_end),
            end=_format_clock(exit_time),
        ),
    )


def _random_time_between(start: time, end: time, rng: random.Random) -> datetime:
    start_at = datetime.combine(datetime.today().date(), start)
    end_at = datetime.combine(datetime.today().date(), end)
    total_minutes = int((end_at - start_at).total_seconds() // 60)
    offset = rng.randint(0, total_minutes)
    return start_at + timedelta(minutes=offset)


def _format_clock(value: datetime) -> str:
    return value.strftime(TIME_FORMAT)
