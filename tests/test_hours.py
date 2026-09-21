from datetime import datetime
import random

from pm_decision.constants import (
    ENTRY_TIME_END,
    ENTRY_TIME_START,
    LUNCH_DURATION,
    LUNCH_START_RANGE_BEGIN,
    LUNCH_START_RANGE_END,
    TIME_FORMAT,
    WORK_DURATION,
)
from pm_decision.hours import (
    TimeInterval,
    afternoon_from_morning,
    generate_workday_schedule,
    is_morning_interval,
    morning_from_afternoon,
)

from tests.helpers import minutes_between


def test_generated_schedule_always_totals_eight_work_hours_and_one_lunch() -> None:
    for seed in range(50):
        schedule = generate_workday_schedule(random.Random(seed))
        morning_minutes = minutes_between(schedule.morning.start, schedule.morning.end)
        afternoon_minutes = minutes_between(schedule.afternoon.start, schedule.afternoon.end)
        lunch_minutes = minutes_between(schedule.morning.end, schedule.afternoon.start)
        entry = datetime.strptime(schedule.morning.start, TIME_FORMAT)
        exit_time = datetime.strptime(schedule.afternoon.end, TIME_FORMAT)

        assert morning_minutes + afternoon_minutes == int(WORK_DURATION.total_seconds() // 60)
        assert lunch_minutes == int(LUNCH_DURATION.total_seconds() // 60)
        assert exit_time - entry == WORK_DURATION + LUNCH_DURATION
        assert schedule.morning.end < schedule.afternoon.start
        assert schedule.morning.start < schedule.morning.end
        assert schedule.afternoon.start < schedule.afternoon.end


def test_entry_and_lunch_stay_inside_configured_ranges() -> None:
    for seed in range(50):
        schedule = generate_workday_schedule(random.Random(seed))
        entry = datetime.strptime(schedule.morning.start, TIME_FORMAT).time()
        lunch_start = datetime.strptime(schedule.morning.end, TIME_FORMAT).time()
        assert ENTRY_TIME_START <= entry <= ENTRY_TIME_END
        assert LUNCH_START_RANGE_BEGIN <= lunch_start <= LUNCH_START_RANGE_END
        assert lunch_start > entry


def test_clock_values_are_zero_padded_hh_mm() -> None:
    schedule = generate_workday_schedule(random.Random(1))
    for interval in schedule.intervals:
        for value in (interval.start, interval.end):
            assert value == datetime.strptime(value, TIME_FORMAT).strftime(TIME_FORMAT)
            assert len(value) == 5
            assert value[2] == ":"


def test_same_seed_produces_the_same_schedule() -> None:
    first = generate_workday_schedule(random.Random(42))
    second = generate_workday_schedule(random.Random(42))
    assert first == second


def test_interval_starting_before_noon_is_morning() -> None:
    assert is_morning_interval(TimeInterval(start="08:53", end="12:35"))
    assert is_morning_interval(TimeInterval(start="11:59", end="12:00"))
    assert not is_morning_interval(TimeInterval(start="12:00", end="13:00"))
    assert not is_morning_interval(TimeInterval(start="13:35", end="17:53"))


def test_afternoon_complements_existing_morning_without_new_random_day() -> None:
    morning = TimeInterval(start="08:53", end="12:35")
    afternoon = afternoon_from_morning(morning)
    assert afternoon == TimeInterval(start="13:35", end="17:53")
    assert minutes_between(morning.start, morning.end) + minutes_between(
        afternoon.start, afternoon.end
    ) == 8 * 60
    assert minutes_between(morning.end, afternoon.start) == 60


def test_morning_complements_existing_afternoon() -> None:
    afternoon = TimeInterval(start="13:38", end="17:54")
    morning = morning_from_afternoon(afternoon)
    assert morning == TimeInterval(start="08:54", end="12:38")
    reconstructed = afternoon_from_morning(morning)
    assert reconstructed == afternoon
