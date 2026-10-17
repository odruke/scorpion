import sys

import pytest

from src.arguments_manager import argument_manager
from src.constants import DEBUG, EDIT, FILES, GUI, RUN_TESTS


def test_argument_manager_parses_files_and_flags(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scorpion.py",
            "one.jpg",
            "two.png",
            "--gui",
            "--debug",
        ],
    )

    options = argument_manager()

    assert options[FILES] == ["one.jpg", "two.png"]
    assert options[GUI] is True
    assert options[EDIT] is False
    assert options[DEBUG] is True
    assert options[RUN_TESTS] is False


def test_edit_flag_also_enables_gui(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["scorpion.py", "--edit", "image.jpg"])

    options = argument_manager()

    assert options[EDIT] is True
    assert options[GUI] is True


def test_test_mode_does_not_require_image(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["scorpion.py", "--run_tests"])

    options = argument_manager()

    assert options[FILES] == []
    assert options[RUN_TESTS] is True


def test_no_files_or_test_mode_is_rejected(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["scorpion.py"])

    with pytest.raises(SystemExit):
        argument_manager()
