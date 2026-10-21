
import ast
import os
import tempfile
from fractions import Fraction
from typing import Any

from PIL import Image, ImageOps
from PIL.Image import Exif
from PIL.ExifTags import TAGS, IFD, GPSTAGS
from PIL.TiffImagePlugin import IFDRational
from src.constants import FILENAME_LABEL, PREVIEW_SIZE


class ImgManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        with Image.open(file_path) as image:
            exif_data = image.getexif()

            self.primary_data: dict = self.__extract_primary_data(image)
            self.exif_metadata: dict = self.__extract_exif_metadata(exif_data)
            self.exif_subdirs: dict = self.__extract_exif_subdirs(exif_data)

            image = ImageOps.exif_transpose(image)
            image.thumbnail((PREVIEW_SIZE, PREVIEW_SIZE))
            self.preview = image.copy()

    def __format_value(self, value: Any) -> Any:
        """
        Format and clean metadata values to make them readeable.
        Manages bytes, fractions (IDFRational) and tuples
        """
        if isinstance(value, bytes):
            decoded = value.decode('utf-8', errors='ignore').strip('\x00')
            return decoded if decoded.isprintable() \
                else f"<Binary block: {len(value)} bytes>"
        elif isinstance(value, IFDRational):
            # converts native pillow fractions to legible floats
            return float(value)
        elif isinstance(value, tuple):
            return tuple(self.__format_value(v) for v in value)
        return value

    def __extract_primary_data(self, image: Image.Image) -> dict[str, Any]:
        return {
                    FILENAME_LABEL: image.filename,
                    "Size": image.size,
                    "Height": image.height,
                    "Width": image.width,
                    "Format": image.format,
                    "Mode": image.mode,
                    "Is Animated": getattr(image, "is_animated", False),
                    "Frames": getattr(image, "n_frames", 1)
                }

    def __extract_exif_metadata(self, exif_data: Exif) -> dict[int, Any]:
        ifd_pointers = [ifd.value for ifd in IFD]

        main_metadata = {}
        for tag_id, value in exif_data.items():
            # Skip pointers to subdirectories
            if tag_id in ifd_pointers:
                continue
            main_metadata[tag_id] = value

        return main_metadata

    def __extract_exif_subdirs(
        self,
        exif_data: Exif,
    ) -> dict[IFD, dict[int, Any]]:
        subdirectories: dict[IFD, dict[int, Any]] = {}

        for ifd_enum in IFD:
            try:
                subdirectory = exif_data.get_ifd(ifd_enum)
            except (KeyError, TypeError, ValueError):
                continue

            if not subdirectory:
                continue

            subdir_dict: dict[int, Any] = {}
            for tag_id, value in subdirectory.items():
                subdir_dict[tag_id] = value

            subdirectories[ifd_enum] = subdir_dict

        return subdirectories

    def get_formatted_exif_data(self) -> dict[str, dict[str, Any]]:
        formatted_data: dict[str, dict[str, Any]] = {}

        for tag_id, value in self.exif_metadata.items():
            label = TAGS.get(tag_id, f"unknown_tag_{tag_id}")
            element: dict[str, Any] = {
                'id': tag_id,
                'value': value,
            }
            formatted_data[label] = element

        return formatted_data

    def get_formatted_exif_subdir(
        self,
    ) -> dict[IFD, dict[str, dict[str, Any]]]:
        dirs: dict[IFD, dict[str, dict[str, Any]]] = {}

        for ifd_enum, subdir in self.exif_subdirs.items():
            dirs[ifd_enum] = {}
            tag_mapping = GPSTAGS if ifd_enum == IFD.GPSInfo else TAGS
            for tag_id, value in subdir.items():
                label = tag_mapping.get(tag_id, f"unknown_tag_{tag_id}")
                element: dict[str, Any] = {
                    'id': tag_id,
                    'value': value,
                }
                dirs[ifd_enum][label] = element

        return dirs

    def print_all_data(self) -> None:
        print("======== Main image metadata =========")

        for label, value in self.primary_data.items():
            print(f"{label:20}: {value}")

        print("\n\n======== Main EXIF metadata =========")

        for tag_id, value in self.exif_metadata.items():
            tag_name = TAGS.get(tag_id, f"unknown_tag_{tag_id}")
            print(f"{tag_name:25}: {self.__format_value(value)}")

        print("\n\n======== Image File Directory subdirectories =========")

        for ifd_enum, subdir in self.exif_subdirs.items():
            print(f"\n------- {ifd_enum.name} subdirectory ---------")
            tag_mapping = GPSTAGS if ifd_enum == IFD.GPSInfo else TAGS
            for tag_id, value in subdir.items():
                tag_name = tag_mapping.get(tag_id, f"unknown_tag_{tag_id}")
                print(f"{tag_name:22}: {self.__format_value(value)}")

    def __convert_value(self, current_value: Any, new_value: str) -> Any:
        value = new_value.strip()

        if isinstance(current_value, bool):
            if value.lower() in {"true", "yes", "1"}:
                return True
            if value.lower() in {"false", "no", "0"}:
                return False
            raise ValueError(f"Invalid boolean value: {new_value}")

        if isinstance(current_value, IFDRational):
            try:
                fraction = Fraction(value)
                return IFDRational(
                    fraction.numerator,
                    fraction.denominator,
                )
            except (ValueError, ZeroDivisionError) as error:
                raise ValueError(
                    f"Invalid rational value: {new_value}"
                ) from error

        if isinstance(current_value, bytes):
            if value.lower().startswith("hex:"):
                try:
                    return bytes.fromhex(value[4:])
                except ValueError as error:
                    raise ValueError(
                        f"Invalid hexadecimal bytes: {new_value}"
                    ) from error
            return value.encode("utf-8")

        if isinstance(current_value, tuple):
            return self.__convert_sequence(
                current_value,
                value,
                tuple,
            )

        if isinstance(current_value, list):
            return self.__convert_sequence(
                current_value,
                value,
                list,
            )

        try:
            return type(current_value)(value)
        except (ValueError, TypeError) as error:
            raise ValueError(
                f"Invalid value: {new_value}\n{error}"
            ) from error

    def __convert_sequence(
        self,
        current_value: tuple[Any, ...] | list[Any],
        new_value: str,
        sequence_type: type[tuple[Any, ...]] | type[list[Any]],
    ) -> tuple[Any, ...] | list[Any]:
        try:
            parsed = ast.literal_eval(new_value)
        except (SyntaxError, ValueError) as error:
            raise ValueError(
                f"Invalid sequence value: {new_value}"
            ) from error

        if not isinstance(parsed, sequence_type):
            raise ValueError(
                f"Expected a {sequence_type.__name__} value"
            )

        if len(parsed) != len(current_value):
            raise ValueError(
                f"Expected {len(current_value)} values, got {len(parsed)}"
            )

        converted = [
            self.__convert_value(current, str(new))
            for current, new in zip(current_value, parsed)
        ]
        return sequence_type(converted)

    def __save_atomically(self, image: Image.Image, exif_data: Exif) -> None:
        source = os.path.abspath(self.file_path)
        directory = os.path.dirname(source)
        suffix = os.path.splitext(source)[1]
        temporary_path: str | None = None

        try:
            with tempfile.NamedTemporaryFile(
                dir=directory,
                prefix=".scorpion-",
                suffix=suffix,
                delete=False,
            ) as temporary:
                temporary_path = temporary.name

            image.save(temporary_path, exif=exif_data)
            os.replace(temporary_path, source)
            temporary_path = None
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass

    def edit_exif_field(
        self,
        new_data: str,
        pointer_id: int,
        ifd_enum: IFD | None = None,
    ) -> None:
        with Image.open(self.file_path) as image:
            exif_data = image.getexif()

            if ifd_enum is None:
                converted_new_data = self.__convert_value(
                    current_value=exif_data[pointer_id],
                    new_value=new_data
                )
                exif_data[pointer_id] = converted_new_data
            else:
                sub_ifd = exif_data.get_ifd(ifd_enum)
                converted_new_data = self.__convert_value(
                    current_value=sub_ifd[pointer_id],
                    new_value=new_data
                )
                sub_ifd[pointer_id] = converted_new_data

            self.__save_atomically(image, exif_data)
            if ifd_enum is None:
                self.exif_metadata[pointer_id] = converted_new_data
            else:
                self.exif_subdirs[ifd_enum][pointer_id] = converted_new_data

    def delete_exif_field(
        self,
        pointer_id: int,
        ifd_enum: IFD | None = None,
    ) -> None:
        with Image.open(self.file_path) as image:
            exif_data = image.getexif()

            if ifd_enum is None:
                del exif_data[pointer_id]
            else:
                sub_ifd = exif_data.get_ifd(ifd_enum)
                del sub_ifd[pointer_id]

            self.__save_atomically(image, exif_data)

            if ifd_enum is None:
                del self.exif_metadata[pointer_id]
            else:
                del self.exif_subdirs[ifd_enum][pointer_id]

    def delete_all_metadata(self) -> None:
        with Image.open(self.file_path) as image:
            self.__save_atomically(image, Image.Exif())

        self.exif_metadata.clear()
        self.exif_subdirs.clear()
