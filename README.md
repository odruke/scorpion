*This project has been created as part of the 42 curriculum by odruke-s.*

# Scorpion

Scorpion is a Python image metadata inspector and editor created as part of
the 42 curriculum.

The program opens one or more local image files with
[Pillow](https://python-pillow.org/), extracts their basic image information
and EXIF metadata, and presents the result either in the terminal or in a
Tkinter graphical interface. The GUI also provides actions for editing and
deleting individual EXIF fields.

## Features

- Read one or more local image files.
- Display basic image information:
  - filename;
  - dimensions and total size;
  - format and mode;
  - animation status and frame count.
- Read main EXIF tags.
- Read EXIF image file directories, including GPS information when available.
- Format byte values, rational values, and tuples for terminal output.
- Correct image orientation for GUI previews using EXIF transpose data.
- Create thumbnails for GUI previews.
- Edit individual EXIF fields through the GUI.
- Delete individual EXIF fields through the GUI.
- Delete all metadata through the `ImgManager` API.
- Enable more detailed logging with `--debug`.
- Run the configured pytest command with `-t` or `--run_tests`.

Scorpion works with the image formats supported by the installed Pillow
version. The repository does not currently contain automated test files, so
test mode currently completes with no collected tests.

## Requirements

- Python 3.12 or a compatible Python 3 release.
- Pillow, as listed in [`requirements.txt`](requirements.txt).
- Tkinter for GUI mode. On some Linux distributions, Tkinter must be
  installed separately through the system package manager.
- pytest if the `-t` or `--run_tests` option is used.

## Installation

From the project directory, create a virtual environment and install the
dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The repository may contain a local `.venv` directory, but virtual
environments should be created locally rather than copied between machines.

## Usage

Run Scorpion from the project root:

```bash
python scorpion.py IMAGE [IMAGE ...]
```

For example, inspect one image in the terminal:

```bash
python scorpion.py img_examples/pic.jpg
```

Inspect several images:

```bash
python scorpion.py img_examples/pic.jpg img_examples/rana.jpg
```

When no GUI option is selected, Scorpion prints the basic image information,
main EXIF metadata, and EXIF subdirectories for each image that could be
opened.

### Command-line options

| Option | Description |
| --- | --- |
| `IMAGE [IMAGE ...]` | One or more local image paths. Required unless test mode is selected. |
| `-g`, `--gui` | Open the graphical interface. |
| `-e`, `--edit` | Open the graphical interface in edit mode. |
| `--debug` | Enable debug-level logging. |
| `-t`, `--run_tests` | Run `pytest` using the current Python interpreter instead of processing images. |
| `-h`, `--help` | Display the command-line help. |

Examples:

```bash
# Open the metadata viewer
python scorpion.py --gui img_examples/pic.jpg

# Open the metadata editor
python scorpion.py --edit img_examples/pic.jpg

# Enable debug logging while inspecting an image
python scorpion.py --debug img_examples/pic.jpg

# Run the configured test command
python scorpion.py --run_tests
```

`--gui` and `--edit` require a graphical desktop session. If an image cannot
be opened, Scorpion logs the error and continues with the remaining image
paths.

## Terminal output

Terminal mode displays three sections for each successfully opened image:

1. **Main image metadata** — filename, dimensions, format, mode, animation
   status, and frame count.
2. **Main EXIF metadata** — EXIF tags that are not pointers to a subdirectory.
3. **Image file directory subdirectories** — metadata found in EXIF,
   GPS, interoperability, or other available IFDs.

Binary metadata values are decoded as UTF-8 when possible. Values that are not
printable are represented as a binary-block description. Pillow rational
values are displayed as floats, and nested tuples are formatted recursively.

## Graphical interface

The GUI displays each loaded image with a thumbnail and its basic image
information. EXIF data is exposed through menus:

- the **Main Exif data** menu contains main EXIF fields;
- additional menus contain available EXIF subdirectories;
- selecting a field opens an edit/delete confirmation flow;
- editing converts the entered text to the existing field's value type before
  saving;
- deleting removes the selected field from the image.

Changes are written back to the original image file. Metadata editing can
damage or remove information, so use copies of important images.

## Project structure

```text
scorpion/
├── scorpion.py
├── img_manager/
│   ├── __init__.py
│   └── img_manager.py
├── src/
│   ├── arguments_manager.py
│   ├── constants.py
│   ├── gui.py
│   └── tools.py
├── requirements.txt
└── README.md
```

- [`scorpion.py`](scorpion.py): application entry point, image loading,
  logging setup, CLI/test dispatch, and terminal output dispatch.
- [`img_manager/img_manager.py`](img_manager/img_manager.py): Pillow image
  loading, metadata extraction, formatting, preview creation, and EXIF
  mutation.
- [`src/arguments_manager.py`](src/arguments_manager.py): command-line
  parsing and option validation.
- [`src/constants.py`](src/constants.py): option keys, GUI dimensions,
  metadata labels, and other shared constants.
- [`src/gui.py`](src/gui.py): Tkinter image list, previews, metadata menus,
  and edit/delete dialogs.
- [`src/tools.py`](src/tools.py): logging configuration.

## Testing

Run the test command directly:

```bash
python -m pytest
```

Or use the application option:

```bash
python scorpion.py --run_tests
```

At the time of writing, no test files are included in the repository, so
pytest reports that no tests were collected.

## Limitations and responsible use

- Scorpion processes local files; it does not download images or crawl
  websites.
- EXIF support and writable field types depend on Pillow and the image format.
- Some metadata may be binary, malformed, unsupported, or unavailable.
- GUI mode requires Tkinter and a display server.
- Metadata writes modify the original file path.
- Always keep a backup before editing or deleting metadata.
- A failed image is logged and skipped; successfully opened images continue to
  be processed.

## References

- [Pillow documentation](https://pillow.readthedocs.io/en/stable/)
- [Pillow: extracting image metadata](https://thepythoncode.com/article/extracting-image-metadata-in-python)
- [EXIF](https://en.wikipedia.org/wiki/Exif)
- [CIPA Exif standards](https://www.cipa.jp/e/std/std-sec.html)
- [Tkinter introduction](https://www.youtube.com/watch?v=ibf5cx221hk&t=1s)
- [Tkinter `grid` geometry manager](https://www.pythontutorial.net/tkinter/tkinter-grid/)
