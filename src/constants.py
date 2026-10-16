from typing import Final, TypedDict


FILES: Final = "files"
EDIT: Final = "edit"
GUI: Final = "GUI"
DEBUG: Final = "debug"
RUN_TESTS: Final = "Run tests"
PREVIEW_SIZE: Final = 250
LIST_ITEM_EXTRA_HEIGHT: Final = 52
CANVAS_WIDTH: Final = 500
MOUSE_WHEEL_DELTA: Final = 120
WINDOW_WIDTH: Final = 700
WINDOW_HEIGHT: Final = 500
FILENAME_LABEL: Final = "Filename"
NO_EXIF_METADATA: Final = "No EXIF metadata found"
EDIT_ACTION: Final = "edit"
DELETE_ACTION: Final = "delete"


class Options(TypedDict):
    files: list[str]
    edit: bool
    GUI: bool
    debug: bool
    Run_tests: bool
