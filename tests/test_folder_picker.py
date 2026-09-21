from pathlib import Path

import pytest

from pm_decision.folder_picker import pick_folder


def test_native_folder_picker_is_windows_only(monkeypatch) -> None:
    monkeypatch.setattr("pm_decision.folder_picker.sys.platform", "linux")
    with pytest.raises(RuntimeError, match="apenas no Windows"):
        pick_folder(Path("."))
