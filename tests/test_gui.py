from types import SimpleNamespace

from PIL.ExifTags import IFD

from src.gui import ListFrame


class FakeMenu:
    def __init__(self):
        self.commands = []
        self.delete_args = None

    def delete(self, *args):
        self.delete_args = args
        self.commands.clear()

    def add_command(self, **kwargs):
        self.commands.append(kwargs)


def test_subdirectory_menu_uses_current_model_data():
    menu = FakeMenu()
    values = {"GPSLatitudeRef": {"id": 1, "value": "N"}}
    image = SimpleNamespace(
        get_formatted_exif_subdir=lambda: {IFD.GPSInfo: values},
    )
    frame = object.__new__(ListFrame)

    frame.populate_exif_subdir(image, menu, IFD.GPSInfo)

    assert [command["label"] for command in menu.commands] == [
        "GPSLatitudeRef: N"
    ]


def test_subdirectory_menu_refresh_reads_new_values():
    menu = FakeMenu()
    current = {"value": "N"}

    def formatted_subdirs():
        return {
            IFD.GPSInfo: {
                "GPSLatitudeRef": {"id": 1, "value": current["value"]}
            }
        }

    image = SimpleNamespace(get_formatted_exif_subdir=formatted_subdirs)
    frame = object.__new__(ListFrame)

    frame.populate_exif_subdir(image, menu, IFD.GPSInfo)
    current["value"] = "S"
    frame.populate_exif_subdir(image, menu, IFD.GPSInfo)

    assert [command["label"] for command in menu.commands] == [
        "GPSLatitudeRef: S"
    ]
