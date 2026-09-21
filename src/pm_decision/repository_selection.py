from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from pm_decision.settings import Settings
from pm_decision.state_store import load_last_repository_path, save_last_repository_path


def resolve_repository_directory(
    settings: Settings,
    override_path: Path | None,
) -> Path | None:
    if override_path is not None:
        resolved = _resolve_override(settings, override_path)
        if resolved is not None:
            save_last_repository_path(resolved)
        return resolved
    last_path = load_last_repository_path()
    initial_directory = last_path if last_path else settings.repositories_root
    selected = _pick_folder_with_timeout(
        initial_directory,
        settings.folder_picker_timeout_seconds,
    )
    if selected is not None:
        save_last_repository_path(selected)
        return selected
    return last_path


def _resolve_override(settings: Settings, override_path: Path) -> Path | None:
    if override_path.exists():
        return override_path.resolve()
    relative = settings.repositories_root / override_path
    if relative.exists():
        return relative.resolve()
    return None


def _pick_folder_with_timeout(initial_directory: Path, timeout_seconds: int) -> Path | None:
    command = [
        sys.executable,
        "-m",
        "pm_decision.folder_picker",
        str(initial_directory),
    ]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as expired:
        if expired.stdout:
            output = expired.stdout if isinstance(expired.stdout, str) else expired.stdout.decode(
                "utf-8", errors="ignore"
            )
            candidate = Path(output.strip())
            if candidate.is_dir():
                return candidate
        return None
    output = (completed.stdout or "").strip()
    if completed.returncode != 0 or not output:
        return None
    candidate = Path(output)
    if not candidate.is_dir():
        return None
    return candidate
