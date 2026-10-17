from typing import TypedDict

# launch options
FILES = "files"
EDIT = "edit"
DELETE = "delete"
GUI = "GUI"
DEBUG = "debug"
RUN_TESTS = "Run tests"

# menu options
DELETE_METADATA = "Delete metadata"
EXIT = "Exit"
CONFIRM = "Confirm"
YES = "yes"
NO = "no"

# constants values
PREVIEW_SIZE = 250
LIST_ITEM_EXTRA_HEIGHT = 52
CANVAS_WIDTH = 500
MOUSE_WHEEL_DELTA = 120
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

#
FILENAME_LABEL = "Filename"
NO_EXIF_METADATA = "No EXIF metadata found"
EDIT_ACTION = "edit"
DELETE_ACTION = "delete"


class Options(TypedDict):
    files: list[str]
    edit: bool
    delete: bool
    gui: bool
    debug: bool
    Run_tests: bool
