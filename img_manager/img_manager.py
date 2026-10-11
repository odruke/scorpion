
from PIL import Image
from PIL.Image import Exif
from PIL.ExifTags import TAGS, IFD, GPSTAGS
from PIL.TiffImagePlugin import IFDRational


class ImgManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        try:
            with Image.open(file_path) as image:
                self.preview = self.__get_preview(image)

                exif_data = image.getexif()
                if not exif_data:
                    pass  # TODO manage this

                self.primary_data: dict = self.__get_primary_data(image)
                self.exif_metadata: dict = self.__get_exif_metadata(exif_data)
                self.exif_subdirs: dict = self.__get_exif_subdirs(exif_data)
        except (OSError, ValueError) as error:
            raise error

    def __format_value(self, value: str):
        """
        Format and clean metadata values to make them readeable.
        Manages bytes, fractions (IDFRational) and tuples
        """
        if isinstance(value, bytes):
            try:
                # Tries to decode text in UTF-8 deleting null characters
                decoded = value.decode('utf-8', errors='ignore').strip('\x00')
                return decoded if decoded.isprintable() \
                    else f"<Binary block: {len(value)} bytes>"
            except Exception:
                return f"<Binary block: {len(value)} bytes>"
        elif isinstance(value, IFDRational):
            # converts native pillow fractions to legible floats
            return float(value)
        elif isinstance(value, tuple):
            return tuple(self.__format_value(v) for v in value)
        return value

    def __get_preview(self, image: Image) -> bytearray:
        pass

    def __get_primary_data(self, image: Image) -> dict:  # TODO check for excep
        return {
                    "Filename": image.filename,
                    "Image Size": image.size,
                    "Image Height": image.height,
                    "Image Width": image.width,
                    "Image Format": image.format,
                    "Image Mode": image.mode,
                    "Image is Animated": getattr(image, "is_animated", False),
                    "Frames in Image": getattr(image, "n_frames", 1)
                }

    def __get_exif_metadata(self, exif_data: Exif) -> dict:
        ifd_pointers = [ifd.value for ifd in IFD]

        main_metadata = {}
        for tag_id, value in exif_data.items():
            # Skip pointers to subdirectories
            if tag_id in ifd_pointers:
                continue
            main_metadata[tag_id] = value

        return main_metadata

    def __get_exif_subdirs(self, exif_data: Exif) -> dict:
        subdirectories = {}

        for ifd_enum in IFD:
            try:
                subdirectory = exif_data.get_ifd(ifd_enum)
            except Exception:
                continue

            if not subdirectory:
                continue

            subdir_dict = {}
            for tag_id, value in subdirectory.items():
                subdir_dict[tag_id] = value

            subdirectories[ifd_enum] = subdir_dict

        return subdirectories

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

    def edit_exif_field(self, new_data: str, pointer_id: int) -> None:
        with Image.open(self.file_path) as image:
            exif_data = image.getexif()

            exif_data[pointer_id] = new_data

            image.save(self.file_path, exif=exif_data)

    def delete_exif_field(self, pointer_id: int):
        with Image.open(self.file_path) as image:
            exif_data = image.getexif()

            exif_data[pointer_id] = ''

            image.save(self.file_path, exif=exif_data)
