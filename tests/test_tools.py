import logging

from src import tools


def test_setup_logger_uses_debug_configuration(monkeypatch):
    calls = []
    monkeypatch.setattr(
        logging,
        "basicConfig",
        lambda **kwargs: calls.append(kwargs),
    )

    tools.setup_logger(debug=True)

    assert calls == [
        {
            "level": logging.DEBUG,
            "format": "%(levelname)s: %(message)s [%(filename)s:%(lineno)d]",
        }
    ]


def test_setup_logger_uses_info_configuration(monkeypatch):
    calls = []
    monkeypatch.setattr(
        logging,
        "basicConfig",
        lambda **kwargs: calls.append(kwargs),
    )

    tools.setup_logger(debug=False)

    assert calls == [{"level": logging.INFO}]
