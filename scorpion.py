#!/usr/bin/env python3

import logging
import subprocess
import sys

from src.arguments_manager import argument_manager
from src.constants import RUN_TESTS, FILES, GUI, EDIT, DEBUG
from src.tools import setup_logger
from img_manager.img_manager import ImgManager
from src.gui import gui

logger = logging.getLogger(__name__)


def main():
    options = argument_manager()

    if options[RUN_TESTS]:
        return subprocess.run([sys.executable, "-m", "pytest"])

    setup_logger(options[DEBUG])
    images = []
    for image_path in options[FILES]:
        try:
            images.append(ImgManager(image_path))
        except (OSError, ValueError) as error:
            logger.error(
                f"Couldn't manage file {image_path}. Reason: {error}"
                )

    if options[GUI] or options[EDIT]:
        gui(images)
    else:
        for image in images:
            image.print_all_data()


if __name__ == "__main__":
    main()
