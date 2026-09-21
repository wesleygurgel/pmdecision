from datetime import date
from pathlib import Path

import pytest

from pm_decision.timesheet_browser import (
    TimesheetBrowser,
    _normalize_clock,
    _parse_entry_date,
    _parse_month_year,
)

from tests.helpers import make_settings, make_timesheet, recorded


def test_parse_month_year_from_open_timesheet_label() -> None:
    assert _parse_month_year("09/2026") == (9, 2026)
    assert _parse_month_year(" 09/2026 ") == (9, 2026)


def test_parse_entry_date_accepts_brazilian_and_iso() -> None:
    assert _parse_entry_date("16/09/2026") == date(2026, 9, 16)
    assert _parse_entry_date("2026-09-16T08:53:00") == date(2026, 9, 16)
    assert _parse_entry_date("") is None
    assert _parse_entry_date("invalid") is None


def test_normalize_clock_keeps_hh_mm_and_rejects_invalid() -> None:
    assert _normalize_clock("08:53") == "08:53"
    assert _normalize_clock("08:53:00") == "08:53"
    assert _normalize_clock("8:53") == "08:53"
    assert _normalize_clock("") is None
    assert _normalize_clock("hora") is None


def test_complete_dates_need_morning_and_afternoon() -> None:
    day = date(2026, 9, 16)
    timesheet = make_timesheet(recorded_intervals=[recorded(day, "08:53", "12:35")])
    assert timesheet.complete_dates == set()
    complete = make_timesheet(
        recorded_intervals=[
            recorded(day, "08:53", "12:35"),
            recorded(day, "13:35", "17:53"),
        ]
    )
    assert complete.complete_dates == {day}


def test_browser_url_joins_base_without_double_slash() -> None:
    browser = TimesheetBrowser(make_settings(base_url="https://app.firstdecision.com.br/pmdecision/"))
    assert browser._url("/Login") == "https://app.firstdecision.com.br/pmdecision/Login"
    assert browser._url("Lancamento/Create") == (
        "https://app.firstdecision.com.br/pmdecision/Lancamento/Create"
    )


def test_page_access_before_start_raises() -> None:
    browser = TimesheetBrowser(make_settings())
    with pytest.raises(RuntimeError, match="Browser not started"):
        _ = browser.page


def test_approval_screen_is_not_referenced_by_the_automation() -> None:
    root = Path(__file__).resolve().parents[1] / "src" / "pm_decision"
    sources = (root / "timesheet_browser.py").read_text(encoding="utf-8")
    sources += (root / "cli.py").read_text(encoding="utf-8")
    sources += (root / "planner.py").read_text(encoding="utf-8")
    assert "EnvioAprovacao" not in sources
    assert "EnvioAprovacaoTimesheet" not in sources
