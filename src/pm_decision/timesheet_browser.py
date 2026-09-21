from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import urljoin

from playwright.sync_api import Browser, Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from pm_decision.constants import (
    CREATE_PATH,
    DATE_FORMAT_BR,
    EXPECTED_INTERVALS_PER_DAY,
    LOGIN_PATH,
    LOGOUT_PATH,
    SAVE_NAVIGATION_TIMEOUT_MS,
    SELECTOR_ACTIVITY_TYPE,
    SELECTOR_CLIENT,
    SELECTOR_DAY,
    SELECTOR_DETAILS,
    SELECTOR_END_TIME,
    SELECTOR_LOGIN,
    SELECTOR_MONTH_YEAR,
    SELECTOR_PASSWORD,
    SELECTOR_PROJECT,
    SELECTOR_PROJECT_ROLE,
    SELECTOR_SAVE,
    SELECTOR_START_TIME,
    SELECTOR_SUBMIT_LOGIN,
    TIME_FORMAT,
)
from pm_decision.hours import TimeInterval, WorkdaySchedule
from pm_decision.settings import Settings


@dataclass(frozen=True)
class RecordedInterval:
    day: date
    interval: TimeInterval


@dataclass(frozen=True)
class OpenTimesheet:
    month: int
    year: int
    client_label: str
    project_label: str
    role_label: str
    activity_label: str
    recorded_intervals: list[RecordedInterval]

    @property
    def complete_dates(self) -> set[date]:
        counts: dict[date, int] = {}
        for item in self.recorded_intervals:
            counts[item.day] = counts.get(item.day, 0) + 1
        return {
            day
            for day, count in counts.items()
            if count >= EXPECTED_INTERVALS_PER_DAY
        }

    def intervals_for(self, day: date) -> list[TimeInterval]:
        return [item.interval for item in self.recorded_intervals if item.day == day]


class TimesheetBrowser:
    def __init__(self, settings: Settings, headed: bool = False) -> None:
        self._settings = settings
        self._headed = headed
        self._playwright = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    def __enter__(self) -> "TimesheetBrowser":
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=not self._headed)
        self._page = self._browser.new_page()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self._page is not None:
            try:
                self.logout()
            except Exception:
                pass
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser not started.")
        return self._page

    def login(self) -> None:
        self.page.goto(self._url(LOGIN_PATH), wait_until="domcontentloaded")
        self.page.locator(SELECTOR_LOGIN).fill(self._settings.username)
        self.page.locator(SELECTOR_PASSWORD).fill(self._settings.password)
        self.page.locator(SELECTOR_SUBMIT_LOGIN).click()
        self.page.get_by_role("button", name="Timesheet").wait_for(timeout=30_000)

    def logout(self) -> None:
        try:
            self.page.goto(self._url(LOGOUT_PATH), wait_until="domcontentloaded")
        except Exception:
            return

    def open_create_form(self) -> OpenTimesheet:
        self.page.goto(self._url(CREATE_PATH), wait_until="domcontentloaded")
        self._wait_for_loaded_form()
        self._assert_single_option(SELECTOR_MONTH_YEAR, "Timesheets Abertos")
        self._assert_single_option(SELECTOR_CLIENT, "Cliente")
        self._assert_single_option(SELECTOR_PROJECT, "Projeto")
        self._assert_single_option(SELECTOR_PROJECT_ROLE, "Função no Projeto")
        self._assert_single_option(SELECTOR_ACTIVITY_TYPE, "Tipo de Atividade")
        month_year_text = self._selected_option_text(SELECTOR_MONTH_YEAR)
        month, year = _parse_month_year(month_year_text)
        return OpenTimesheet(
            month=month,
            year=year,
            client_label=self._selected_option_text(SELECTOR_CLIENT),
            project_label=self._selected_option_text(SELECTOR_PROJECT),
            role_label=self._selected_option_text(SELECTOR_PROJECT_ROLE),
            activity_label=self._selected_option_text(SELECTOR_ACTIVITY_TYPE),
            recorded_intervals=self._read_recorded_intervals(),
        )

    def save_workday(
        self,
        day: date,
        schedule: WorkdaySchedule,
        detalhamento: str,
    ) -> None:
        self.save_intervals(day, list(schedule.intervals), detalhamento)

    def save_intervals(
        self,
        day: date,
        intervals: list[TimeInterval],
        detalhamento: str,
    ) -> None:
        for interval in intervals:
            self._save_interval(day, interval, detalhamento)

    def _save_interval(self, day: date, interval: TimeInterval, detalhamento: str) -> None:
        self._fill_day(day)
        self._fill_time(SELECTOR_START_TIME, interval.start)
        self._fill_time(SELECTOR_END_TIME, interval.end)
        self.page.locator(SELECTOR_DETAILS).fill(detalhamento)
        start_value = (self.page.locator(SELECTOR_START_TIME).input_value() or "").strip()
        end_value = (self.page.locator(SELECTOR_END_TIME).input_value() or "").strip()
        if start_value != interval.start or end_value != interval.end:
            raise RuntimeError(
                "Horários no formulário não conferem antes de salvar: "
                f"{start_value}-{end_value}, esperado {interval.start}-{interval.end}."
            )
        try:
            with self.page.expect_navigation(
                wait_until="domcontentloaded",
                timeout=SAVE_NAVIGATION_TIMEOUT_MS,
            ):
                self.page.locator(SELECTOR_SAVE).click()
        except PlaywrightTimeoutError as error:
            raise RuntimeError(
                "O formulário não recarregou após Salvar. "
                f"Validação: {self._visible_validation_errors() or '(vazia)'}"
            ) from error
        self._wait_for_loaded_form()
        self._wait_for_saved_interval(day, interval)

    def _fill_day(self, day: date) -> None:
        locator = self.page.locator(SELECTOR_DAY)
        locator.fill("")
        locator.fill(f"{day.day:02d}")
        locator.dispatch_event("change")
        locator.dispatch_event("blur")

    def _fill_time(self, selector: str, value: str) -> None:
        self.page.evaluate(
            """({ selector, value }) => {
                const element = document.querySelector(selector);
                if (!element) {
                    throw new Error('Campo de hora não encontrado: ' + selector);
                }
                if (window.jQuery) {
                    jQuery(element).val(value).trigger('input').trigger('change').valid();
                } else {
                    element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""",
            {"selector": selector, "value": value},
        )
        actual = (self.page.locator(selector).input_value() or "").strip()
        if actual != value:
            raise RuntimeError(
                f"Horário não aplicado em {selector}: ficou '{actual}', esperado '{value}'."
            )

    def _read_recorded_intervals(self) -> list[RecordedInterval]:
        payload = self.page.evaluate(
            """() => {
                if (window.lancamentosMes && Array.isArray(window.lancamentosMes.Lancamentos)) {
                    const pad = (value) => String(value).padStart(2, '0');
                    const formatDate = (value) => (
                        pad(value.getDate()) + '/' + pad(value.getMonth() + 1) + '/' + value.getFullYear()
                    );
                    const formatTime = (value) => pad(value.getHours()) + ':' + pad(value.getMinutes());
                    return window.lancamentosMes.Lancamentos
                        .filter(item => item.DataHoraEntrada instanceof Date && item.DataHoraSaida instanceof Date)
                        .map(item => ({
                            date: formatDate(item.DataHoraEntrada),
                            start: formatTime(item.DataHoraEntrada),
                            end: formatTime(item.DataHoraSaida),
                        }));
                }
                const rows = [];
                const cellsRows = document.querySelectorAll('#divLancamentoNoMes tbody tr');
                for (const row of cellsRows) {
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 3) continue;
                    rows.push({
                        date: (cells[0].innerText || '').trim(),
                        start: (cells[1].innerText || '').trim(),
                        end: (cells[2].innerText || '').trim(),
                    });
                }
                return rows;
            }"""
        )
        recorded: list[RecordedInterval] = []
        for raw in payload:
            day = _parse_entry_date(raw.get("date", ""))
            start = _normalize_clock(raw.get("start", ""))
            end = _normalize_clock(raw.get("end", ""))
            if day is None or start is None or end is None:
                continue
            recorded.append(RecordedInterval(day=day, interval=TimeInterval(start=start, end=end)))
        return recorded

    def _wait_for_saved_interval(self, day: date, interval: TimeInterval) -> None:
        date_text = day.strftime(DATE_FORMAT_BR)
        self.page.wait_for_function(
            """({ dateText, start, end }) => {
                const pad = (value) => String(value).padStart(2, '0');
                const formatDate = (value) => (
                    pad(value.getDate()) + '/' + pad(value.getMonth() + 1) + '/' + value.getFullYear()
                );
                const formatTime = (value) => pad(value.getHours()) + ':' + pad(value.getMinutes());
                if (window.lancamentosMes && Array.isArray(window.lancamentosMes.Lancamentos)) {
                    const found = window.lancamentosMes.Lancamentos.some((item) => {
                        if (!(item.DataHoraEntrada instanceof Date) || !(item.DataHoraSaida instanceof Date)) {
                            return false;
                        }
                        return formatDate(item.DataHoraEntrada) === dateText
                            && formatTime(item.DataHoraEntrada) === start
                            && formatTime(item.DataHoraSaida) === end;
                    });
                    if (found) return true;
                }
                const rows = document.querySelectorAll('#divLancamentoNoMes tbody tr');
                return Array.from(rows).some((row) => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 3) return false;
                    const rowDate = (cells[0].innerText || '').trim();
                    const rowStart = (cells[1].innerText || '').trim();
                    const rowEnd = (cells[2].innerText || '').trim();
                    return rowDate.includes(dateText)
                        && rowStart.startsWith(start)
                        && rowEnd.startsWith(end);
                });
            }""",
            arg={
                "dateText": date_text,
                "start": interval.start,
                "end": interval.end,
            },
            timeout=SAVE_NAVIGATION_TIMEOUT_MS,
        )

    def _visible_validation_errors(self) -> str:
        return self.page.evaluate(
            """() => {
                const summary = document.querySelector('#validationSummary');
                const summaryText = summary ? summary.innerText.trim() : '';
                const fields = Array.from(
                    document.querySelectorAll('.field-validation-error')
                ).map(node => node.innerText.trim()).filter(Boolean);
                return [summaryText, ...fields].filter(Boolean).join(' | ');
            }"""
        )

    def _wait_for_loaded_form(self) -> None:
        self.page.wait_for_function(
            """() => {
                const hasValue = (selector) => {
                    const element = document.querySelector(selector);
                    if (!element || element.disabled) return false;
                    return Array.from(element.options).some(
                        option => option.value && option.value !== '0'
                    );
                };
                return hasValue('#MesAnoId')
                    && hasValue('#ClienteId')
                    && hasValue('#ProjetoId')
                    && hasValue('#ProjetoFuncaoId')
                    && hasValue('#TipoAtividadeId')
                    && window.lancamentosMes !== null;
            }""",
            timeout=30_000,
        )

    def _assert_single_option(self, selector: str, field_name: str) -> None:
        values = self.page.eval_on_selector(
            selector,
            """element => Array.from(element.options)
                .map(option => option.value)
                .filter(value => value && value !== '0')""",
        )
        if len(values) != 1:
            raise RuntimeError(
                f"Campo '{field_name}' tem {len(values)} opções; "
                "a automação só segue quando há exatamente uma."
            )

    def _selected_option_text(self, selector: str) -> str:
        return self.page.eval_on_selector(
            selector,
            "element => element.options[element.selectedIndex]?.text || ''",
        ).strip()

    def _url(self, path: str) -> str:
        return urljoin(self._settings.base_url.rstrip("/") + "/", path.lstrip("/"))


def _parse_month_year(value: str) -> tuple[int, int]:
    parsed = datetime.strptime(value.strip(), "%m/%Y")
    return parsed.month, parsed.year


def _parse_entry_date(raw: str) -> date | None:
    text = (raw or "").strip()
    if not text:
        return None
    if "T" in text:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    try:
        return datetime.strptime(text, DATE_FORMAT_BR).date()
    except ValueError:
        return None


def _normalize_clock(raw: str) -> str | None:
    text = (raw or "").strip()
    if not text:
        return None
    for candidate in (text, text[:5]):
        try:
            return datetime.strptime(candidate, TIME_FORMAT).strftime(TIME_FORMAT)
        except ValueError:
            continue
    return None
