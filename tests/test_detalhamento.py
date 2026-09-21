from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from pm_decision.constants import (
    DETALHAMENTO_MAX_CHARACTERS,
    GENERIC_DETALHAMENTO_WITHOUT_REPO,
    GENERIC_DETALHAMENTO_WITH_REPO,
)
from pm_decision.detalhamento import build_detalhamento, build_repository_tag
from pm_decision.git_source import GitCommitSummary

from tests.helpers import make_settings


def _commit(subject: str, repository: Path) -> GitCommitSummary:
    return GitCommitSummary(
        repository_path=repository,
        repository_name=repository.name,
        subject=subject,
        body="body",
        stat="1 file changed",
    )


def test_without_repository_uses_generic_text_without_tag() -> None:
    text = build_detalhamento(make_settings(), None)
    assert text == GENERIC_DETALHAMENTO_WITHOUT_REPO
    assert not text.startswith("[")


def test_repository_without_git_uses_tagged_generic_text(
    monkeypatch, repositories_root: Path
) -> None:
    selected = repositories_root / "conecta-industria" / "frontend"
    selected.mkdir(parents=True)
    monkeypatch.setattr("pm_decision.detalhamento.read_head_commit", lambda path: None)
    text = build_detalhamento(
        make_settings(repositories_root=repositories_root),
        selected,
    )
    assert text == f"[CONECTA-INDUSTRIA] {GENERIC_DETALHAMENTO_WITH_REPO}"


def test_tag_is_first_folder_under_repositories_root(repositories_root: Path) -> None:
    selected = repositories_root / "conecta-industria" / "conecta-industria-frontend"
    selected.mkdir(parents=True)
    assert (
        build_repository_tag(selected, repositories_root) == "CONECTA-INDUSTRIA"
    )


def test_tag_falls_back_to_folder_name_outside_root(tmp_path: Path) -> None:
    selected = tmp_path / "outro-projeto"
    selected.mkdir()
    assert build_repository_tag(selected, tmp_path / "first") == "OUTRO-PROJETO"


def test_useful_git_subject_is_used_when_openai_is_missing(
    monkeypatch, repositories_root: Path
) -> None:
    selected = repositories_root / "sdic_api"
    selected.mkdir()
    monkeypatch.setattr(
        "pm_decision.detalhamento.read_head_commit",
        lambda path: _commit("Corrige timeout no login", selected),
    )
    text = build_detalhamento(
        make_settings(repositories_root=repositories_root, openai_api_key=None),
        selected,
    )
    assert text == "[SDIC_API] Trabalhei nisto: Corrige timeout no login"


def test_useless_git_subject_falls_back_to_generic(
    monkeypatch, repositories_root: Path
) -> None:
    selected = repositories_root / "oid-backend"
    selected.mkdir()
    monkeypatch.setattr(
        "pm_decision.detalhamento.read_head_commit",
        lambda path: _commit("Merge branch 'main'", selected),
    )
    text = build_detalhamento(
        make_settings(repositories_root=repositories_root),
        selected,
    )
    assert text == f"[OID-BACKEND] {GENERIC_DETALHAMENTO_WITH_REPO}"


def test_openai_success_prefixes_tag_and_strips_duplicate_tag(
    monkeypatch, repositories_root: Path
) -> None:
    selected = repositories_root / "conecta-industria"
    selected.mkdir()
    monkeypatch.setattr(
        "pm_decision.detalhamento.read_head_commit",
        lambda path: _commit("Melhora gestão de demandas", selected),
    )
    fake_message = SimpleNamespace(
        content='"[CONECTA-INDUSTRIA] Melhorei a gestão de demandas."'
    )
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=fake_message)]
    )
    monkeypatch.setattr("pm_decision.detalhamento.OpenAI", lambda **kwargs: fake_client)

    text = build_detalhamento(
        make_settings(repositories_root=repositories_root, openai_api_key="sk-test"),
        selected,
    )
    assert text == "[CONECTA-INDUSTRIA] Melhorei a gestão de demandas."
    assert text.count("[CONECTA-INDUSTRIA]") == 1
    assert "eu:" not in text.lower()


def test_openai_failure_falls_back_to_git_subject(
    monkeypatch, repositories_root: Path
) -> None:
    selected = repositories_root / "conecta-industria"
    selected.mkdir()
    monkeypatch.setattr(
        "pm_decision.detalhamento.read_head_commit",
        lambda path: _commit("Ajusta Dockerfile", selected),
    )

    def explode(**kwargs):
        raise TimeoutError("openai timeout")

    monkeypatch.setattr("pm_decision.detalhamento.OpenAI", explode)
    text = build_detalhamento(
        make_settings(repositories_root=repositories_root, openai_api_key="sk-test"),
        selected,
    )
    assert text == "[CONECTA-INDUSTRIA] Trabalhei nisto: Ajusta Dockerfile"


def test_detalhamento_never_exceeds_character_cap(
    monkeypatch, repositories_root: Path
) -> None:
    selected = repositories_root / "conecta-industria"
    selected.mkdir()
    long_subject = "Implementei " + ("melhorias no fluxo de demandas " * 20)
    monkeypatch.setattr(
        "pm_decision.detalhamento.read_head_commit",
        lambda path: _commit(long_subject, selected),
    )
    text = build_detalhamento(
        make_settings(repositories_root=repositories_root),
        selected,
    )
    assert len(text) <= DETALHAMENTO_MAX_CHARACTERS
    assert text.startswith("[CONECTA-INDUSTRIA] ")
    assert not text.endswith(" ")
