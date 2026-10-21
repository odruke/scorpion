# binary constants
from fractions import Fraction
from PIL.ExifTags import TAGS
from typing import Any

MARKER_PREFIX = 0xFF
BIG_ENDIAN = b"MM"
LITTLE_ENDIAN = b"II"

# markers
APP1_MARKER = 0xE1
EXIF_MARKER = b"Exif\x00\x00"
SOI = 0xD8
EOI = 0xD9
SOS = 0xDA

RST0 = 0xD0
RST7 = 0xD7

# type formats
BYTE = 1  # 1 byte
ASCII = 2  # 1 byte
SHORT = 3  # 2 bytes
LONG = 4  # 4 bytes
RATIONAL = 5  # 8 bytes
UNDEFINED = 7  # 1 byte
SLONG = 9  # 4 bytes
SRATIONAL = 10  # 8 bytes

TYPE_INFO: dict[int, tuple[type, int]] = {
    BYTE: (int, 1),
    ASCII: (str, 1),
    SHORT: (int, 2),
    LONG: (int, 4),
    RATIONAL: (Fraction, 8),
    UNDEFINED: (bytes, 1),
    SLONG: (int, 4),
    SRATIONAL: (Fraction, 8),
}


# ========= format identifiers (magic number) =========
# JPEG
JPEG_IDENTIFIER = b"\xFF\xD8\xFF"
JPEG_SOI = b"\xFF\xD8"

# PNG
PNG_IDENTIFIER = b"\x89PNG\r\n\x1A\n"

# GIF
GIF87_IDENTIFIER = b"GIF87a"
GIF89_IDENTIFIER = b"GIF89a"

# BMP
BMP_IDENTIFIER = b"BM"


def get_type(field_type: int) -> tuple[type, int]:
    try:
        return TYPE_INFO[field_type]
    except KeyError as error:
        raise ValueError(
            f"Unsupported EXIF field type: {field_type}"
        ) from error

def get_value(
    count: int,
    byte_size: int,
    value_or_offset: bytes,
    payload: bytes,
    tiff_offset: int,
    endian: str,
) -> bytes:
    total_size = count * byte_size

    if total_size <= 4:
        return value_or_offset[:total_size]

    value_offset = int.from_bytes(value_or_offset, endian)

    start = tiff_offset + value_offset
    end = start + total_size

    return payload[start:end]


def cast_value(
    raw_value: bytes,
    field_type: int,
    count: int,
    endian: str,
) -> Any:
    if field_type == ASCII:
        return raw_value.rstrip(b"\x00").decode(
            "ascii",
            errors="replace",
        )

    if field_type == UNDEFINED:
        return raw_value

    _, byte_size = get_type(field_type)

    if field_type in {RATIONAL, SRATIONAL}:
        signed = field_type == SRATIONAL
        values = []

        for start in range(0, len(raw_value), byte_size):
            numerator = int.from_bytes(
                raw_value[start:start + 4],
                endian,
                signed=signed,
            )
            denominator = int.from_bytes(
                raw_value[start + 4:start + 8],
                endian,
                signed=signed,
            )

            if denominator == 0:
                raise ValueError("EXIF rational denominator cannot be zero")

            values.append(Fraction(numerator, denominator))

        return values[0] if count == 1 else values

    signed = field_type == SLONG
    values = []

    for start in range(0, len(raw_value), byte_size):
        values.append(
            int.from_bytes(
                raw_value[start:start + byte_size],
                endian,
                signed=signed,
            )
        )

    return values[0] if count == 1 else values



def inspect_jpeg(path) -> None:
    with open(path, "rb") as file:
        data = file.read()
        header = data[:8]

    print(f"Size: {len(data)} bytes")

    if header.startswith(JPEG_IDENTIFIER):
        print("JPEG")
    elif header == PNG_IDENTIFIER:
        print("PNG")
    elif header.startswith((GIF87_IDENTIFIER, GIF89_IDENTIFIER)):
        print("GIF")
    elif header.startswith(BMP_IDENTIFIER):
        print("BMP")
    else:
        print("Unkown format")

    # this is also the SOI (Start Of Image). with EOI enclouses all the data for the image
    # we will only cover jpeg in this example
    if data[:2] != JPEG_SOI:
        print("The file does not start with the jpeg SOI identifier")
        return

    # Buscar todos los marcadores APP1
    offset = 2

    while offset < len(data) - 1:
        # Look for the FF marker prefix
        if data[offset] != MARKER_PREFIX:
            print(f"Unexpected byte: {data[offset]} in offset: {offset}")
            break

        # Skip possible filling extra FF bytes
        while offset < len(data) and data[offset] == MARKER_PREFIX:
            offset += 1

        if offset >= len(data):
            break

        marker = data[offset]
        offset += 1

        # Markers with no length field
        if marker in (EOI, SOI) or RST0 <= marker <= RST7:
            if marker == EOI:
                print("End of JPEG (EOI)")
                break
            continue

        # Read segment length (big-endian)
        if offset + 2 > len(data):
            break

        length = int.from_bytes(data[offset:offset + 2], "big")

        if length < 2 or offset + length > len(data):
            print("Invalid segment length")
            break

        if marker == APP1_MARKER:
            print(f"APP1 found in offset {offset - 2}")
            print(f"Segment lenght: {length}")

            payload_start = offset + 2  # we start after the marker
            payload_end = offset + length
            payload = data[payload_start:payload_end]

            if payload.startswith(EXIF_MARKER):
                print("EXIF found")
                ifd_offset = len(EXIF_MARKER)

                # reading TIFF header
                print("\n----- Reading TIFF header")
                """
                TIFF header structure
                endian: 2 bytes
                magic number: 2 bytes
                offset: 4 bytes
                """
                byte_order = payload[ifd_offset:ifd_offset + 2]
                print(f"endian: {byte_order}")
                if byte_order == LITTLE_ENDIAN:
                    endian = "little"
                    print("little endian")
                elif byte_order == BIG_ENDIAN:
                    endian = "big"
                    print("big endian")
                else:
                    print("Could not recognize endian")
                    break

                tiff_magic_nb_bytes = payload[ifd_offset + 2:ifd_offset + 2 + 2]
                tiff_magic_nb = int.from_bytes(tiff_magic_nb_bytes, endian)
                print(f"TIFF magic number: {tiff_magic_nb}")
                if tiff_magic_nb != 42:
                    print("Wrong TIFF magic number")
                    break

                first_content_offset_bytes = payload[ifd_offset + 4:ifd_offset + 4 + 4]
                first_content_offset = int.from_bytes(first_content_offset_bytes, endian) + ifd_offset
                print(f"IFD offset + exif marker (8 + 6): {first_content_offset}")
                print("End of TIFF header -----\n")
                # end of TIFF header

                # Reading IFD directory
                print("\n----- Reading directory")
                """
                Directory structure:
                tag: 2 bytes
                field type: 2 bytes
                count: 4 bytes
                value: 4 bytes
                """

                ifd_entries = int.from_bytes(payload[first_content_offset:first_content_offset + 2], endian)
                print(f"Number of entries inside IFD: {ifd_entries}")

                entries_raw = []
                i = 0
                entry_offset = first_content_offset + 2
                while i < ifd_entries:
                    entries_raw.append(payload[entry_offset:entry_offset + 12])
                    count = f"{i}:"
                    print(f"Raw entry {count:3} {payload[entry_offset:entry_offset + 12].hex(" ")}")
                    entry_offset += 12
                    i += 1

                entries = []
                for entry in entries_raw:

                    tag = int.from_bytes(entry[0:2], endian)
                    field_type_id = int.from_bytes(entry[2:4], endian)
                    python_type, byte_size = get_type(field_type_id)
                    count = int.from_bytes(entry[4:8], endian)
                    raw_value = get_value(
                        count=count,
                        byte_size=byte_size,
                        value_or_offset=entry[8:12],
                        payload=payload,
                        tiff_offset=ifd_offset,
                        endian=endian,
                    )

                    value = cast_value(
                        raw_value=raw_value,
                        field_type=field_type_id,
                        count=count,
                        endian=endian,
                    )

                    entry_dic = {
                        "tag": tag,
                        "field_type": field_type_id,
                        "python_type": python_type,
                        "count": count,
                        "value": value,
                    }
                    entries.append(entry_dic)

                # print directory
                print()
                for entry in entries:
                    label = TAGS.get(entry['tag'], f"unknown_tag_{entry['tag']}")
                    print(f"{label}: {entry['value']}")
                print("End of directory -----\n")
            else:
                print("APP1 found, but does not contain EXIF")

        # fordward the offset with the length of the segment
        offset += length

        # SOS marker indicates the begining of the compresed content.
        # we should not interpret these bytes as regular segments.
        if marker == SOS:
            print("Beggining of compressed data (SOS)")
            break


if __name__ == "__main__":
    inspect_jpeg("img_examples_edit/rana_full.jpg")
