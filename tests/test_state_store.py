from pathlib import Path
import json

from pm_decision.constants import STATE_FILE_NAME, STATE_KEY_LAST_REPO_PATH
from pm_decision.state_store import (
    load_last_repository_path,
    save_last_repository_path,
    state_file_path,
)


def test_load_returns_none_when_state_file_is_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert load_last_repository_path() is None


def test_save_and_load_roundtrip_when_path_still_exists(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    repo = tmp_path / "conecta-industria"
    repo.mkdir()
    save_last_repository_path(repo)
    loaded = load_last_repository_path()
    assert loaded == repo.resolve()
    payload = json.loads(state_file_path().read_text(encoding="utf-8"))
    assert payload[STATE_KEY_LAST_REPO_PATH] == str(repo.resolve())
    assert state_file_path() == tmp_path / "pm-decision" / STATE_FILE_NAME


def test_load_returns_none_when_saved_path_was_deleted(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    repo = tmp_path / "apagado"
    repo.mkdir()
    save_last_repository_path(repo)
    repo.rmdir()
    assert load_last_repository_path() is None


def test_empty_last_repo_path_is_treated_as_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    state_dir = tmp_path / "pm-decision"
    state_dir.mkdir()
    (state_dir / STATE_FILE_NAME).write_text("{}", encoding="utf-8")
    assert load_last_repository_path() is None
