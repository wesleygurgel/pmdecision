from datetime import time, timedelta

from pm_decision.constants import (
    DETALHAMENTO_MAX_CHARACTERS,
    ENTRY_TIME_END,
    ENTRY_TIME_START,
    EXPECTED_INTERVALS_PER_DAY,
    FOLDER_PICKER_TIMEOUT_SECONDS,
    HOLIDAY_COUNTRY_CODE,
    LUNCH_DURATION,
    LUNCH_START_RANGE_BEGIN,
    LUNCH_START_RANGE_END,
    MORNING_INTERVAL_START_LIMIT,
    SELECTOR_SAVE,
    WORK_DURATION,
)


def test_workday_invariants_match_business_rules() -> None:
    assert WORK_DURATION == timedelta(hours=8)
    assert LUNCH_DURATION == timedelta(hours=1)
    assert ENTRY_TIME_START == time(8, 45)
    assert ENTRY_TIME_END == time(9, 15)
    assert LUNCH_START_RANGE_BEGIN == time(11, 30)
    assert LUNCH_START_RANGE_END == time(14, 0)
    assert EXPECTED_INTERVALS_PER_DAY == 2
    assert HOLIDAY_COUNTRY_CODE == "BR"
    assert MORNING_INTERVAL_START_LIMIT == time(12, 0)


def test_detalhamento_and_picker_limits() -> None:
    assert DETALHAMENTO_MAX_CHARACTERS == 250
    assert FOLDER_PICKER_TIMEOUT_SECONDS == 60


def test_save_selector_targets_form_submit_not_accessibility_name() -> None:
    assert SELECTOR_SAVE == "#novolancamentoform button[type='submit']"
