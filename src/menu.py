import curses

from src.constants import DELETE_METADATA, EXIT, CONFIRM, YES, NO


def selector(stdscr, options: list, prompt: str) -> int:

    selected = 0

    while True:
        stdscr.clear()

        stdscr.addstr(prompt)

        for index, option in enumerate(options):
            if index == selected:
                stdscr.addstr(f"> {option}\n")
            else:
                stdscr.addstr(f"  {option}\n")

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected -= 1

        elif key == curses.KEY_DOWN:
            selected += 1

        elif key == curses.KEY_ENTER or key in [10, 13]:
            return selected

        if selected < 0:
            selected = len(options) - 1

        elif selected >= len(options):
            selected = 0


def menu(stdscr, options: str) -> str:
    menus = {
        DELETE_METADATA: [
           DELETE_METADATA,
           EXIT,
        ],
        CONFIRM: [
            YES,
            NO,
        ]
    }

    prompts = {
        DELETE_METADATA: "You are about to delete all metadata from the\
 selected files.\n------ THIS ACTION IS IRREVERSIBLE ------\nDo you want to\
 continue?\n\n",
        CONFIRM: "Are you sure?\n\n"
    }

    selection = selector(
        stdscr=stdscr,
        options=menus[options],
        prompt=prompts[options]
        )

    return menus[options][selection]
