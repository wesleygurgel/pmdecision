from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
import logging
import sys

from pm_decision.constants import DATE_FORMAT_BR
from pm_decision.planner import RunPlan, apply_plan, build_run_plan
from pm_decision.repository_selection import resolve_repository_directory
from pm_decision.settings import load_settings
from pm_decision.timesheet_browser import TimesheetBrowser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    arguments = _parse_arguments(argv)
    try:
        settings = load_settings()
        repository_path = resolve_repository_directory(settings, arguments.repo)
        with TimesheetBrowser(settings, headed=arguments.headed) as browser:
            browser.login()
            timesheet = browser.open_create_form()
            plan = build_run_plan(
                settings=settings,
                timesheet=timesheet,
                today=date.today(),
                repository_path=repository_path,
                only_date=arguments.only_date,
            )
            _print_plan(plan, apply_changes=arguments.apply)
            if arguments.apply:
                if not plan.entries:
                    return 0
                apply_plan(browser, plan)
                print("Lançamentos gravados.")
        return 0
    except Exception as error:
        cause = error.__cause__ or error.__context__
        details = f"{error}"
        if cause:
            details = f"{error} ({cause})"
        print(f"Erro: {details}", file=sys.stderr)
        return 1


def _parse_arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automação de timesheet do PM Decision (dry-run por padrão)."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Grava os lançamentos. Sem esta flag, apenas mostra o plano.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Pasta do repositório (pula o File Explorer). Uso de teste.",
    )
    parser.add_argument(
        "--only-date",
        type=_parse_iso_date,
        default=None,
        help="Restringe a um dia (YYYY-MM-DD). Útil no primeiro apply.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Abre o Chromium visível.",
    )
    return parser.parse_args(argv)


def _parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _print_plan(plan: RunPlan, apply_changes: bool) -> None:
    mode = "APPLY" if apply_changes else "DRY-RUN"
    print(f"[{mode}]")
    print(f"Timesheet: {plan.timesheet.month:02d}/{plan.timesheet.year}")
    print(f"Cliente: {plan.timesheet.client_label}")
    print(f"Projeto: {plan.timesheet.project_label}")
    print(f"Função: {plan.timesheet.role_label}")
    print(f"Atividade: {plan.timesheet.activity_label}")
    print(
        "Repositório: "
        + (str(plan.repository_path) if plan.repository_path else "(não selecionado)")
    )
    print(f"Detalhamento ({len(plan.detalhamento)} chars): {plan.detalhamento}")
    already = ", ".join(
        day.strftime(DATE_FORMAT_BR) for day in sorted(plan.timesheet.complete_dates)
    )
    print(f"Já lançados (manhã+tarde): {already or '(nenhum)'}")
    if not plan.entries:
        print("Nenhum dia pendente.")
        return
    print("Pendentes:")
    for entry in plan.entries:
        parts = [f"{interval.start}-{interval.end}" for interval in entry.intervals_to_save]
        print(f"  {entry.day.strftime(DATE_FORMAT_BR)}  " + " / ".join(parts))


if __name__ == "__main__":
    raise SystemExit(main())
