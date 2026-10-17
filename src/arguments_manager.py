import argparse
from src.constants import DEBUG, EDIT, FILES, GUI, Options, RUN_TESTS, DELETE


def argument_manager() -> Options:
    options: Options = {
        FILES: [],
        EDIT: False,
        DELETE: False,
        GUI: False,
        DEBUG: False,
        RUN_TESTS: False
    }

    parser = argparse.ArgumentParser()

    parser.add_argument('FILES', type=str, nargs="*", help='Image files from \
where extract metadata')

    parser.add_argument('-g',
                        '--gui',
                        action='store_true',
                        help='Launch the graphical user interface')

    parser.add_argument('-e',
                        '--edit',
                        action='store_true',
                        help='Run the program in edition mode, GUI by default')

    parser.add_argument('--delete',
                        action='store_true',
                        help='Delete all metadata from a image or images.\
 Overrides --edit and --gui flags')

    parser.add_argument('-t',
                        '--run_tests',
                        action='store_true',
                        help='Run test for the program')

    parser.add_argument('--debug',
                        action='store_true',
                        help='Activates a more verbose debug log')

    args = parser.parse_args()

    if not args.FILES and not args.run_tests:
        parser.error(
            "You must either provide a valid FILE path \
or run tests with -t/--run_tests"
                     )

    options[FILES] = args.FILES
    options[EDIT] = args.edit
    options[DELETE] = args.delete
    options[GUI] = True if args.edit is True else args.gui
    options[RUN_TESTS] = args.run_tests
    options[DEBUG] = args.debug
    return options
