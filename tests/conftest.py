from pathlib import Path

import pytest

from tests.helpers import make_settings


@pytest.fixture
def repositories_root(tmp_path: Path) -> Path:
    root = tmp_path / "Repositorios" / "first"
    root.mkdir(parents=True)
    return root


@pytest.fixture
def settings(repositories_root: Path):
    return make_settings(repositories_root=repositories_root)
