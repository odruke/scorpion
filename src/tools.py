import curses
import logging

from src.menu import menu

logger = logging.getLogger(__name__)


def setup_logger(debug: bool) -> None:
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s: %(message)s [%(filename)s:%(lineno)d]"
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
        )


def run_menu(options: str) -> str:
    return curses.wrapper(lambda stdscr: menu(stdscr, options))
