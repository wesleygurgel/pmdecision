from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from pm_decision.constants import (
    STATE_FILE_NAME,
    STATE_KEY_LAST_REPO_PATH,
    STATE_KEY_SELECTED_AT,
)
from pm_decision.settings import local_app_data_directory


def state_file_path() -> Path:
    return local_app_data_directory() / STATE_FILE_NAME


def load_last_repository_path() -> Path | None:
    path = state_file_path()
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_path = payload.get(STATE_KEY_LAST_REPO_PATH)
    if not raw_path:
        return None
    repository_path = Path(raw_path)
    if not repository_path.exists():
        return None
    return repository_path


def save_last_repository_path(repository_path: Path) -> None:
    directory = local_app_data_directory()
    directory.mkdir(parents=True, exist_ok=True)
    payload = {
        STATE_KEY_LAST_REPO_PATH: str(repository_path.resolve()),
        STATE_KEY_SELECTED_AT: datetime.now(timezone.utc).isoformat(),
    }
    state_file_path().write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
