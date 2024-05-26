#!/usr/bin/env python3

from sys import argv, stdin, stderr
from argparse import Namespace, ArgumentParser
from json import dumps
from select import select

try:
    from ytmusicapi import YTMusic

except ModuleNotFoundError as err:
    stderr.write(f"[ERRO] {err}.\n")

    exit(1)


# Helper functions and decorators.

def command_error_logger(command: callable) -> callable:
    """Just show the error message on the std error and then exit with status
    code 1 if the function command decorated doesn't raise some exception.
    """
    def wrapper(*args):
        try:
            return command(*args)

        except Exception as err:
            stderr.write(f"[ERRO] {err}.\n")
            exit(1)

    return wrapper


# The CLI related functions will be below.

@command_error_logger
def search(ytm: YTMusic, terms: list[str],
           is_top_result_only: bool) -> dict | list[dict]:
    """It will use the Youtube Music API to search for each term individually,
    the final result will be stored in a list of dicts with "searchTerm" and
    "searchResult" keys; Also, if the list has only one item (when the user
    just search for one term) it will return the only dict of that list.
    """
    if len(terms) == 0:
        raise Exception("No search therms specified")

    results = []

    for term in terms:
        result = ytm.search(term)

        if is_top_result_only:
            result = list(filter(lambda elm: elm["category"] == "Top result",
                                 result))

        results.append({
            "searchTerm": term,
            "searchResult": result
        })

    if len(results) == 0:
        raise Exception("Could not find anything")
    elif len(results) == 1:
        return results[0]

    return results


def main(args: Namespace) -> None:
    """Giving the command line arguments, already parsed, this funcion will
    figure out which subcommand routine it should run and display the result on
    the standart output.
    """
    JSON_INDENT_SIZE = 2

    ytm = YTMusic()

    match args.subcommand:
        case "search":
            result = search(ytm, args.terms, args.top_result_only)
            result_json = dumps(result, indent=JSON_INDENT_SIZE)

            print(result_json)


def parse_app_args(args: list[str]) -> Namespace:
    """It does what you expect, it uses the argparse builtin Python library to
    parse the command line argumens AND subcommands. In the source code, try to
    keep each subcommand parser separated by a commentary to improve
    readability.
    """
    VERSION = "0.2.0"

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
    if not select([stdin], [], [], 0) == ([], [], []):
        for pipe_line in stdin:
            pipe_line = pipe_line.replace("\n", "")

            argv.append(pipe_line)

    args = parse_app_args(argv[1:])

    main(args)
