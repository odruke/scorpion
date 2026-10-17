#!/usr/bin/env python3

import logging
import subprocess
import sys

from src.arguments_manager import argument_manager
from src.constants import (
    RUN_TESTS,
    FILES,
    GUI,
    EDIT,
    DEBUG,
    DELETE_METADATA,
    CONFIRM,
    EXIT,
    YES,
    NO,
    FILENAME_LABEL)
from src.tools import setup_logger, run_menu
from img_manager.img_manager import ImgManager
from src.gui import gui

logger = logging.getLogger(__name__)


def main():
    options = argument_manager()

    if options[RUN_TESTS]:
        return subprocess.run([sys.executable, "-m", "pytest"])

    setup_logger(options[DEBUG])
    images: list[ImgManager] = []
    for image_path in options[FILES]:
        try:
            images.append(ImgManager(image_path))
        except (OSError, ValueError) as error:
            logger.error(
                f"Couldn't manage file {image_path}. Reason: {error}"
                )

    if not images:
        logger.info("No images were loaded, exiting program")
        return

    if options["delete"]:
        choice = run_menu(DELETE_METADATA)
        if choice == EXIT:
            logger.info("Deletion canceled, exiting program")
            return
        if choice == DELETE_METADATA:
            choice = run_menu(CONFIRM)
            if choice == NO:
                logger.info("Deletion canceled, exiting program")
                return
            if choice == YES:
                for image in images:
                    filename = image.primary_data[FILENAME_LABEL]
                    logger.info(f"deleting metadatadata from {filename}")
                    image.delete_all_metadata()
                logger.info(f"All metadata deleted from {len(images)} files")
                return

    if options[GUI] or options[EDIT]:
        gui(images)
    else:
        for image in images:
            image.print_all_data()


if __name__ == "__main__":
    main()
