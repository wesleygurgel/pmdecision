from pathlib import Path

import pytest

from pm_decision.constants import DEFAULT_BASE_URL, DEFAULT_OPENAI_MODEL
from pm_decision.settings import load_settings, local_app_data_directory


def _clear_settings_env(monkeypatch) -> None:
    monkeypatch.setattr("pm_decision.settings.load_dotenv", lambda: None)
    for name in (
        "PM_DECISION_USER",
        "PM_DECISION_PASSWORD",
        "PM_DECISION_BASE_URL",
        "REPOSITORIES_ROOT",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
    ):
        monkeypatch.delenv(name, raising=False)


def test_load_settings_requires_credentials(monkeypatch) -> None:
    _clear_settings_env(monkeypatch)
    with pytest.raises(ValueError, match="PM_DECISION_USER"):
        load_settings()


def test_load_settings_uses_defaults_and_optional_openai(monkeypatch) -> None:
    _clear_settings_env(monkeypatch)
    monkeypatch.setenv("PM_DECISION_USER", " wesley.oliveira ")
    monkeypatch.setenv("PM_DECISION_PASSWORD", "secret")
    settings = load_settings()
    assert settings.username == "wesley.oliveira"
    assert settings.password == "secret"
    assert settings.base_url == DEFAULT_BASE_URL
    assert settings.openai_api_key is None
    assert settings.has_openai_key is False
    assert settings.openai_model == DEFAULT_OPENAI_MODEL


def test_load_settings_strips_trailing_slash_and_reads_openai(monkeypatch, tmp_path) -> None:
    _clear_settings_env(monkeypatch)
    monkeypatch.setenv("PM_DECISION_USER", "user")
    monkeypatch.setenv("PM_DECISION_PASSWORD", "pass")
    monkeypatch.setenv("PM_DECISION_BASE_URL", "https://app.firstdecision.com.br/pmdecision/")
    monkeypatch.setenv("REPOSITORIES_ROOT", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", " sk-test ")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    settings = load_settings()
    assert settings.base_url == "https://app.firstdecision.com.br/pmdecision"
    assert settings.repositories_root == tmp_path
    assert settings.openai_api_key == "sk-test"
    assert settings.has_openai_key is True


def test_local_app_data_uses_localappdata_when_set(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert local_app_data_directory() == tmp_path / "pm-decision"
