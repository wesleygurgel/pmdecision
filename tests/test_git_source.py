from pathlib import Path

from pm_decision.git_source import GitCommitSummary, read_head_commit, resolve_git_root

from tests.helpers import init_git_repository


def test_useful_commit_subjects() -> None:
    useful = GitCommitSummary(
        repository_path=Path("."),
        repository_name="repo",
        subject="Corrige máscara de hora no lançamento",
        body="",
        stat="",
    )
    assert useful.is_useful_subject


def test_merge_wip_and_copilot_subjects_are_useless() -> None:
    def summary(subject: str) -> GitCommitSummary:
        return GitCommitSummary(
            repository_path=Path("."),
            repository_name="repo",
            subject=subject,
            body="",
            stat="",
        )

    assert not summary("Merge branch 'main' into feature").is_useful_subject
    assert not summary("WIP ajuste local").is_useful_subject
    assert not summary("Atualização: commit via Copilot").is_useful_subject
    assert not summary("").is_useful_subject


def test_resolve_git_root_prefers_direct_repository(tmp_path: Path) -> None:
    init_git_repository(tmp_path, "Commit raiz")
    nested = tmp_path / "frontend"
    init_git_repository(nested, "Commit nested")
    assert resolve_git_root(tmp_path) == tmp_path


def test_nested_git_skips_node_modules_and_picks_newest_head(tmp_path: Path) -> None:
    selected = tmp_path / "conecta-industria"
    skipped = selected / "node_modules" / "lib"
    older = selected / "backend"
    newer = selected / "frontend"
    init_git_repository(skipped, "dependência")
    init_git_repository(older, "backend antigo")
    init_git_repository(newer, "frontend novo")
    (older / ".git" / "HEAD").touch()
    (newer / ".git" / "HEAD").touch()
    import os
    import time

    now = time.time()
    os.utime(older / ".git" / "HEAD", (now - 120, now - 120))
    os.utime(newer / ".git" / "HEAD", (now, now))
    assert resolve_git_root(selected) == newer


def test_read_head_commit_returns_subject_from_head(tmp_path: Path) -> None:
    init_git_repository(tmp_path, "Implementa suíte de testes", "Detalhe do commit")
    commit = read_head_commit(tmp_path)
    assert commit is not None
    assert commit.subject == "Implementa suíte de testes"
    assert "Detalhe do commit" in commit.body
    assert commit.repository_name == tmp_path.name


def test_read_head_commit_returns_none_without_git(tmp_path: Path) -> None:
    empty = tmp_path / "sem-git"
    empty.mkdir()
    assert read_head_commit(empty) is None
    assert resolve_git_root(empty) is None
