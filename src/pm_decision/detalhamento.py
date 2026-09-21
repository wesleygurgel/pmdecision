from __future__ import annotations

from pathlib import Path
import logging
import re

from openai import OpenAI

from pm_decision.constants import (
    DETALHAMENTO_GIT_FALLBACK_PREFIX,
    DETALHAMENTO_MAX_CHARACTERS,
    DETALHAMENTO_TAG_TEMPLATE,
    GENERIC_DETALHAMENTO_WITHOUT_REPO,
    GENERIC_DETALHAMENTO_WITH_REPO,
    OPENAI_MAX_TOKENS,
    OPENAI_TEMPERATURE,
    OPENAI_TIMEOUT_SECONDS,
)
from pm_decision.git_source import GitCommitSummary, read_head_commit
from pm_decision.settings import Settings

logger = logging.getLogger(__name__)
LEADING_TAG_PATTERN = re.compile(r"^\[[^\]]+\]\s*")


def build_detalhamento(
    settings: Settings,
    selected_directory: Path | None,
) -> str:
    if selected_directory is None:
        return _clip(GENERIC_DETALHAMENTO_WITHOUT_REPO, DETALHAMENTO_MAX_CHARACTERS)
    tag = build_repository_tag(selected_directory, settings.repositories_root)
    commit = read_head_commit(selected_directory)
    if commit is None:
        return _compose(tag, GENERIC_DETALHAMENTO_WITH_REPO)
    generated = None
    if settings.has_openai_key:
        generated = _generate_with_openai(settings, commit, tag)
    if generated:
        return _compose(tag, generated)
    if commit.is_useful_subject:
        return _compose(tag, f"{DETALHAMENTO_GIT_FALLBACK_PREFIX}{commit.subject}")
    return _compose(tag, GENERIC_DETALHAMENTO_WITH_REPO)


def build_repository_tag(selected_directory: Path, repositories_root: Path) -> str:
    try:
        relative = selected_directory.resolve().relative_to(repositories_root.resolve())
        project_name = relative.parts[0]
    except ValueError:
        project_name = selected_directory.name
    return project_name.upper()


def _generate_with_openai(
    settings: Settings,
    commit: GitCommitSummary,
    tag: str,
) -> str | None:
    prefix_length = len(DETALHAMENTO_TAG_TEMPLATE.format(tag=tag))
    body_limit = DETALHAMENTO_MAX_CHARACTERS - prefix_length
    prompt = (
        "Escreva UMA frase em português na PRIMEIRA PESSOA DO SINGULAR "
        "(eu: Melhorei, Ajustei, Fiz, Implementei, Corrigi). "
        f"No máximo {body_limit} caracteres. "
        "Não coloque tag, aspas, SHA nem prefixo de commit. Não invente tickets.\n\n"
        f"Repositório: {commit.repository_name}\n"
        f"Subject: {commit.subject}\n"
        f"Body: {commit.body}\n"
        f"Stat:\n{commit.stat}\n"
    )
    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=OPENAI_TIMEOUT_SECONDS,
        )
        response = client.chat.completions.create(
            model=settings.openai_model,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você escreve detalhamento curto de timesheet em primeira pessoa."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        content = (response.choices[0].message.content or "").strip()
        return _strip_leading_tag(content) or None
    except Exception as error:
        logger.warning("Falha ao gerar detalhamento com OpenAI: %s", error)
        return None


def _compose(tag: str, body: str) -> str:
    prefix = DETALHAMENTO_TAG_TEMPLATE.format(tag=tag)
    body_limit = DETALHAMENTO_MAX_CHARACTERS - len(prefix)
    normalized_body = _strip_leading_tag(_clip(body, body_limit))
    if not normalized_body:
        normalized_body = _clip(GENERIC_DETALHAMENTO_WITH_REPO, body_limit)
    return prefix + normalized_body


def _strip_leading_tag(text: str) -> str:
    cleaned = " ".join(text.strip().strip("\"'").split())
    return LEADING_TAG_PATTERN.sub("", cleaned).strip()


def _clip(text: str, max_characters: int) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_characters:
        return cleaned
    truncated = cleaned[:max_characters].rsplit(" ", 1)[0]
    return truncated[:max_characters]
