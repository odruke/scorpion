import scorpion
from src import menu as menu_module
from src.constants import (
    CONFIRM,
    DEBUG,
    DELETE,
    DELETE_METADATA,
    EDIT,
    EXIT,
    FILES,
    GUI,
    NO,
    RUN_TESTS,
    YES,
)


class FakeImage:
    def __init__(self, filename):
        self.primary_data = {"Filename": filename}
        self.delete_calls = 0

    def delete_all_metadata(self):
        self.delete_calls += 1


def make_delete_options(*, gui=False, edit=False):
    return {
        RUN_TESTS: False,
        FILES: ["first.jpg", "second.jpg"],
        GUI: gui,
        EDIT: edit,
        DEBUG: False,
        DELETE: True,
    }


def install_fake_images(monkeypatch, options):
    images = []

    def create_image(path):
        image = FakeImage(path)
        images.append(image)
        return image

    monkeypatch.setattr(scorpion, "argument_manager", lambda: options)
    monkeypatch.setattr(scorpion, "setup_logger", lambda debug: None)
    monkeypatch.setattr(scorpion, "ImgManager", create_image)
    return images


def test_delete_flag_requires_confirmation_and_uses_warning_text(monkeypatch):
    displayed = {}

    def fake_selector(stdscr, options, prompt):
        displayed["options"] = options
        displayed["prompt"] = prompt
        return 0

    monkeypatch.setattr(menu_module, "selector", fake_selector)
    assert menu_module.menu(None, DELETE_METADATA) == DELETE_METADATA
    assert displayed["options"] == [DELETE_METADATA, EXIT]
    assert "IRREVERSIBLE" in displayed["prompt"]

    options = make_delete_options()
    images = install_fake_images(monkeypatch, options)
    menu_requests = []
    menu_choices = iter([DELETE_METADATA, YES])

    def fake_run_menu(menu_name):
        menu_requests.append(menu_name)
        return next(menu_choices)

    monkeypatch.setattr(scorpion, "run_menu", fake_run_menu)

    scorpion.main()

    assert menu_requests == [DELETE_METADATA, CONFIRM]
    assert [image.delete_calls for image in images] == [1, 1]


def test_delete_flag_cancellation_preserves_all_files(monkeypatch):
    options = make_delete_options()
    images = install_fake_images(monkeypatch, options)
    menu_requests = []
    menu_choices = iter([DELETE_METADATA, NO])

    def fake_run_menu(menu_name):
        menu_requests.append(menu_name)
        return next(menu_choices)

    monkeypatch.setattr(scorpion, "run_menu", fake_run_menu)

    scorpion.main()

    assert menu_requests == [DELETE_METADATA, CONFIRM]
    assert [image.delete_calls for image in images] == [0, 0]


def test_delete_flag_deletes_every_selected_file_but_not_gui_mode(monkeypatch):
    options = make_delete_options(gui=True, edit=True)
    images = install_fake_images(monkeypatch, options)
    gui_calls = []
    monkeypatch.setattr(
        scorpion,
        "run_menu",
        lambda menu_name: (
            DELETE_METADATA if menu_name == DELETE_METADATA else YES
        ),
    )
    monkeypatch.setattr(
        scorpion,
        "gui",
        lambda loaded_images, edit_mode: gui_calls.append(
            (loaded_images, edit_mode)
        ),
    )

    scorpion.main()

    assert [image.delete_calls for image in images] == [1, 1]
    assert gui_calls == []
