import subprocess
import sys

import scorpion
from src.constants import DEBUG, EDIT, FILES, GUI, RUN_TESTS


def test_main_dispatches_test_mode(monkeypatch):
    monkeypatch.setattr(
        scorpion,
        "argument_manager",
        lambda: {RUN_TESTS: True},
    )
    completed = subprocess.CompletedProcess(args=["pytest"], returncode=0)
    calls = []
    monkeypatch.setattr(
        scorpion.subprocess,
        "run",
        lambda command: calls.append(command) or completed,
    )

    result = scorpion.main()

    assert result is completed
    assert calls == [[sys.executable, "-m", "pytest"]]


def test_main_logs_invalid_image_and_processes_valid_images(
    monkeypatch,
    caplog,
):
    class FakeImage:
        def print_all_data(self):
            pass

    options = {
        RUN_TESTS: False,
        FILES: ["bad.jpg", "good.jpg"],
        GUI: False,
        EDIT: False,
        DEBUG: False,
    }
    created = []

    def create_image(path):
        if path == "bad.jpg":
            raise OSError("cannot open")
        created.append(path)
        return FakeImage()

    def fake_setup_logger(debug):
        return debug

    monkeypatch.setattr(scorpion, "argument_manager", lambda: options)
    monkeypatch.setattr(scorpion, "setup_logger", fake_setup_logger)
    monkeypatch.setattr(scorpion, "ImgManager", create_image)

    with caplog.at_level("ERROR"):
        scorpion.main()

    assert created == ["good.jpg"]
    assert "Couldn't manage file bad.jpg" in caplog.text
