from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from pm_decision.constants import (
    NESTED_GIT_MAX_DEPTH,
    NESTED_GIT_SKIP_DIRECTORY_NAMES,
    USELESS_COMMIT_PATTERNS,
)
import re


@dataclass(frozen=True)
class GitCommitSummary:
    repository_path: Path
    repository_name: str
    subject: str
    body: str
    stat: str

    @property
    def is_useful_subject(self) -> bool:
        normalized = self.subject.strip().lower()
        if not normalized:
            return False
        return not any(re.search(pattern, normalized) for pattern in USELESS_COMMIT_PATTERNS)


def resolve_git_root(selected_directory: Path) -> Path | None:
    direct = selected_directory / ".git"
    if direct.exists():
        return selected_directory
    candidates: list[tuple[float, Path]] = []
    _collect_git_roots(selected_directory, 0, candidates)
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def read_head_commit(selected_directory: Path) -> GitCommitSummary | None:
    git_root = resolve_git_root(selected_directory)
    if git_root is None:
        return None
    subject = _git_output(git_root, ["log", "-1", "--pretty=%s"])
    body = _git_output(git_root, ["log", "-1", "--pretty=%b"])
    stat = _git_output(git_root, ["log", "-1", "--stat"])
    return GitCommitSummary(
        repository_path=git_root,
        repository_name=selected_directory.name,
        subject=subject.strip(),
        body=body.strip(),
        stat=stat.strip(),
    )


def _collect_git_roots(
    directory: Path, depth: int, candidates: list[tuple[float, Path]]
) -> None:
    if depth > NESTED_GIT_MAX_DEPTH:
        return
    git_dir = directory / ".git"
    if git_dir.exists():
        head = git_dir / "HEAD" if git_dir.is_dir() else git_dir
        stamp = head.stat().st_mtime if head.exists() else 0.0
        candidates.append((stamp, directory))
        return
    try:
        children = list(directory.iterdir())
    except OSError:
        return
    for child in children:
        if not child.is_dir():
            continue
        if child.name in NESTED_GIT_SKIP_DIRECTORY_NAMES:
            continue
        _collect_git_roots(child, depth + 1, candidates)


def _git_output(repository: Path, arguments: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout
