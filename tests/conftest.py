from pathlib import Path

import pytest
from PIL import Image
from PIL.ExifTags import IFD


@pytest.fixture
def image_path(tmp_path: Path) -> Path:
    path = tmp_path / "sample.jpg"
    image = Image.new("RGB", (16, 12), "white")
    exif = image.getexif()
    exif[270] = "initial description"
    gps = exif.get_ifd(IFD.GPSInfo)
    gps[1] = "N"
    image.save(path, exif=exif)
    return path
