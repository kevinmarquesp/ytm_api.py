#!/usr/bin/env python3

from sys import argv
from argparse import Namespace, ArgumentParser

try:
    from ytmusicapi import YTMusic

except ModuleNotFoundError as err:
    print(f"\033[31m{err}\033[m")

    exit(1)

VERSION = "0.1.0"


# The CLI related functions will be below.

def main(args: Namespace) -> None:
    """Giving the command line arguments, already parsed, this funcion will
    figure out which subcommand routine it should run and display the result on
    the standart output. It will be respeonsible to handle the errors if
    needed.
    """
    print(args)


def parse_app_args(args: list[str]) -> Namespace:
    """It does what you expect, it uses the argparse builtin Python library to
    parse the command line argumens AND subcommands. In the source code, try to
    keep each subcommand parser separated by a commentary to improve
    readability.
    """
    # Parser and subparser definition, global flags should be here.
    parser = ArgumentParser(prog="ytm-api", description="Python script created\
                            to easely fetch data from the Youtube Music API\
                            from command line, where I can use jq, yt-dlp and\
                            other tools to automate some downloaidng process.")
    subparser = parser.add_subparsers(title="subcommands", dest="subcommand")

    parser.add_argument("--version", "-v", action="version",
                        version=f"%(prog)s {VERSION}")

    # Search subcommand parser.
    search = subparser.add_parser("search", help="Given a list of terms to\
                                  search, it will iterate over each one and\
                                  return the results in a JSON array string.")

    search.add_argument("terms", type=str, nargs="*", help="...TODO...")
    search.add_argument("--top-result-only", "-t", action="store_true",
                        help="Filter the search output to only return the top\
                        results JSON object.")

    # This will parse everything, including the subcommand parsers.
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_app_args(argv[1:])

    main(args)
