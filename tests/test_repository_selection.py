from pathlib import Path
import subprocess
from unittest.mock import MagicMock

from pm_decision.repository_selection import resolve_repository_directory

from tests.helpers import make_settings


def test_absolute_repo_override_skips_explorer_and_saves_path(
    tmp_path, monkeypatch
) -> None:
    repo = tmp_path / "conecta-industria"
    repo.mkdir()
    saved: list[Path] = []
    monkeypatch.setattr(
        "pm_decision.repository_selection.save_last_repository_path",
        saved.append,
    )
    picker = MagicMock()
    monkeypatch.setattr(
        "pm_decision.repository_selection._pick_folder_with_timeout",
        picker,
    )
    resolved = resolve_repository_directory(make_settings(), repo)
    assert resolved == repo.resolve()
    assert saved == [repo.resolve()]
    picker.assert_not_called()


def test_relative_repo_name_resolves_under_repositories_root(
    repositories_root: Path, monkeypatch
) -> None:
    repo = repositories_root / "conecta-industria"
    repo.mkdir()
    monkeypatch.setattr(
        "pm_decision.repository_selection.save_last_repository_path",
        lambda path: None,
    )
    resolved = resolve_repository_directory(
        make_settings(repositories_root=repositories_root),
        Path("conecta-industria"),
    )
    assert resolved == repo.resolve()


def test_missing_repo_override_returns_none_and_does_not_save(monkeypatch, tmp_path) -> None:
    saved = MagicMock()
    monkeypatch.setattr(
        "pm_decision.repository_selection.save_last_repository_path",
        saved,
    )
    resolved = resolve_repository_directory(
        make_settings(repositories_root=tmp_path),
        Path("nao-existe"),
    )
    assert resolved is None
    saved.assert_not_called()


def test_explorer_selection_is_saved_and_returned(tmp_path, monkeypatch) -> None:
    selected = tmp_path / "escolhido"
    selected.mkdir()
    saved: list[Path] = []
    monkeypatch.setattr(
        "pm_decision.repository_selection.load_last_repository_path",
        lambda: None,
    )
    monkeypatch.setattr(
        "pm_decision.repository_selection.save_last_repository_path",
        saved.append,
    )
    monkeypatch.setattr(
        "pm_decision.repository_selection._pick_folder_with_timeout",
        lambda initial, timeout: selected,
    )
    resolved = resolve_repository_directory(make_settings(repositories_root=tmp_path), None)
    assert resolved == selected
    assert saved == [selected]


def test_timeout_or_cancel_uses_last_saved_folder_without_overwriting(
    tmp_path, monkeypatch
) -> None:
    last = tmp_path / "ultima"
    last.mkdir()
    saved = MagicMock()
    monkeypatch.setattr(
        "pm_decision.repository_selection.load_last_repository_path",
        lambda: last,
    )
    monkeypatch.setattr(
        "pm_decision.repository_selection.save_last_repository_path",
        saved,
    )
    monkeypatch.setattr(
        "pm_decision.repository_selection._pick_folder_with_timeout",
        lambda initial, timeout: None,
    )
    resolved = resolve_repository_directory(make_settings(repositories_root=tmp_path), None)
    assert resolved == last
    saved.assert_not_called()


def test_first_run_timeout_without_last_folder_continues_without_repo(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(
        "pm_decision.repository_selection.load_last_repository_path",
        lambda: None,
    )
    monkeypatch.setattr(
        "pm_decision.repository_selection._pick_folder_with_timeout",
        lambda initial, timeout: None,
    )
    resolved = resolve_repository_directory(make_settings(repositories_root=tmp_path), None)
    assert resolved is None


def test_picker_timeout_expired_without_stdout_returns_none(monkeypatch, tmp_path) -> None:
    def explode(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr("pm_decision.repository_selection.subprocess.run", explode)
    from pm_decision.repository_selection import _pick_folder_with_timeout

    assert _pick_folder_with_timeout(tmp_path, 1) is None
