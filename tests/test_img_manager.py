from pathlib import Path

import pytest
from PIL.ExifTags import IFD, TAGS
from PIL.TiffImagePlugin import IFDRational
from PIL import Image

import img_manager.img_manager as img_manager_module
from img_manager.img_manager import ImgManager


def test_manager_extracts_primary_and_exif_data(image_path: Path):
    manager = ImgManager(str(image_path))

    assert manager.primary_data["Filename"] == str(image_path)
    assert manager.primary_data["Size"] == (16, 12)
    assert manager.primary_data["Width"] == 16
    assert manager.primary_data["Height"] == 12
    assert manager.primary_data["Format"] == "JPEG"
    assert manager.preview.size == (16, 12)
    assert manager.exif_metadata[270] == "initial description"
    assert IFD.GPSInfo in manager.exif_subdirs
    assert manager.exif_subdirs[IFD.GPSInfo][1] == "N"


def test_manager_rejects_invalid_image(tmp_path):
    invalid_path = tmp_path / "not-an-image.jpg"
    invalid_path.write_text("not an image")

    with pytest.raises((OSError, ValueError)):
        ImgManager(str(invalid_path))


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (b"hello\x00", "hello"),
        (b"\x00\xff", ""),
        (IFDRational(1, 2), 0.5),
        ((b"a\x00", IFDRational(2, 1)), ("a", 2.0)),
        ("unchanged", "unchanged"),
    ],
)
def test_format_value(value, expected):
    manager = object.__new__(ImgManager)

    assert manager._ImgManager__format_value(value) == expected


def test_formatted_metadata_uses_tag_names(image_path: Path):
    manager = ImgManager(str(image_path))

    formatted = manager.get_formatted_exif_data()

    assert formatted[TAGS[270]] == {
        "id": 270,
        "value": "initial description",
    }


def test_formatted_subdirectory_uses_gps_tag_names(image_path: Path):
    manager = ImgManager(str(image_path))

    formatted = manager.get_formatted_exif_subdir()

    assert formatted[IFD.GPSInfo]["GPSLatitudeRef"] == {
        "id": 1,
        "value": "N",
    }


def test_edit_main_exif_field_persists_and_updates_cache(image_path: Path):
    manager = ImgManager(str(image_path))

    manager.edit_exif_field("updated description", 270)

    assert manager.exif_metadata[270] == "updated description"
    reloaded = ImgManager(str(image_path))
    assert reloaded.exif_metadata[270] == "updated description"


def test_edit_subdirectory_field_uses_subdirectory_value_type(image_path: Path):
    manager = ImgManager(str(image_path))

    manager.edit_exif_field("S", 1, IFD.GPSInfo)

    assert manager.exif_subdirs[IFD.GPSInfo][1] == "S"
    reloaded = ImgManager(str(image_path))
    assert reloaded.exif_subdirs[IFD.GPSInfo][1] == "S"


@pytest.mark.parametrize(
    ("current_value", "new_value", "expected"),
    [
        (b"old", "new", b"new"),
        (b"old", "hex:01 ff", b"\x01\xff"),
        ((1, 2), "(3, 4)", (3, 4)),
        (IFDRational(1, 2), "3/4", IFDRational(3, 4)),
    ],
)
def test_convert_value_supports_common_metadata_types(
    current_value,
    new_value,
    expected,
):
    manager = object.__new__(ImgManager)

    assert manager._ImgManager__convert_value(
        current_value,
        new_value,
    ) == expected


def test_invalid_edit_does_not_modify_file_or_cache(image_path: Path):
    manager = ImgManager(str(image_path))

    with pytest.raises(ValueError):
        manager.edit_exif_field("not an integer", 274)

    assert manager.exif_metadata[274] == 1
    reloaded = ImgManager(str(image_path))
    assert reloaded.exif_metadata[274] == 1


def test_failed_atomic_replace_does_not_modify_file_or_cache(
    image_path: Path,
    monkeypatch,
):
    manager = ImgManager(str(image_path))

    def fail_replace(*args):
        assert len(args) == 2
        raise OSError("replacement failed")

    monkeypatch.setattr(img_manager_module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replacement failed"):
        manager.edit_exif_field("updated description", 270)

    assert manager.exif_metadata[270] == "initial description"
    with Image.open(image_path) as image:
        assert image.getexif()[270] == "initial description"


def test_delete_main_and_subdirectory_fields_updates_cache_and_file(
    image_path: Path,
):
    manager = ImgManager(str(image_path))

    manager.delete_exif_field(270)
    manager.delete_exif_field(1, IFD.GPSInfo)

    assert 270 not in manager.exif_metadata
    assert 1 not in manager.exif_subdirs[IFD.GPSInfo]
    reloaded = ImgManager(str(image_path))
    assert 270 not in reloaded.exif_metadata
    assert 1 not in reloaded.exif_subdirs.get(IFD.GPSInfo, {})


def test_delete_all_metadata_updates_cache_and_file(image_path: Path):
    manager = ImgManager(str(image_path))

    manager.delete_all_metadata()

    assert manager.exif_metadata == {}
    assert manager.exif_subdirs == {}
    reloaded = ImgManager(str(image_path))
    assert reloaded.exif_metadata == {}
    assert reloaded.exif_subdirs == {}
