from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

from pm_decision.constants import (
    APPLICATION_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_REPOSITORIES_ROOT,
    FOLDER_PICKER_TIMEOUT_SECONDS,
)


@dataclass(frozen=True)
class Settings:
    username: str
    password: str
    base_url: str
    repositories_root: Path
    openai_api_key: str | None
    openai_model: str
    folder_picker_timeout_seconds: int

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)


def load_settings() -> Settings:
    load_dotenv()
    username = os.getenv("PM_DECISION_USER", "").strip()
    password = os.getenv("PM_DECISION_PASSWORD", "")
    if not username or not password:
        raise ValueError(
            "Defina PM_DECISION_USER e PM_DECISION_PASSWORD no arquivo .env"
        )
    repositories_root_value = os.getenv("REPOSITORIES_ROOT", "").strip()
    repositories_root = (
        Path(repositories_root_value)
        if repositories_root_value
        else DEFAULT_REPOSITORIES_ROOT
    )
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
    return Settings(
        username=username,
        password=password,
        base_url=os.getenv("PM_DECISION_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        repositories_root=repositories_root,
        openai_api_key=openai_api_key,
        openai_model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip()
        or DEFAULT_OPENAI_MODEL,
        folder_picker_timeout_seconds=FOLDER_PICKER_TIMEOUT_SECONDS,
    )


def local_app_data_directory() -> Path:
    appdata = os.getenv("LOCALAPPDATA")
    if appdata:
        return Path(appdata) / APPLICATION_NAME
    return Path.home() / ".local" / "share" / APPLICATION_NAME
