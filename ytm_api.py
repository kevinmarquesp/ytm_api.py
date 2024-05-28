#!/usr/bin/env python3

from sys import argv, stdin, stderr
from argparse import Namespace, ArgumentParser
from json import dumps

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

        results += result

    if len(results) == 0:
        raise Exception("Could not find anything")
    elif len(results) == 1:
        return results[0]

    return results


@command_error_logger
def artist(ytm: YTMusic, ids: list[str]) -> dict | list[dict]:
    """Featch the artist information, the custom flags is suposed to be used
    as a filter mechanism. It will return a list of dicts or a simple dict if
    the list has only one dict element.
    """
    results = []

    for id in ids:
        result = ytm.get_artist(id)

        results.append(result)

    return results


def main(args: Namespace) -> None:
    """Giving the command line arguments, already parsed, this funcion will
    figure out which subcommand routine it should run and display the result on
    the standart output.
    """
    JSON_INDENT_SIZE = 2

    ytm = YTMusic()
    result = "null"

    match args.subcommand:
        case "search":
            result = search(ytm, args.terms, args.top_result_only)

        case "artist":
            result = artist(ytm, args.ids)

    result_json = dumps(result, indent=JSON_INDENT_SIZE)

    print(result_json)


def parse_app_args(args: list[str]) -> Namespace:
    """It does what you expect, it uses the argparse builtin Python library to
    parse the command line argumens AND subcommands. In the source code, try to
    keep each subcommand parser separated by a commentary to improve
    readability.
    """
    VERSION = "1.4.1"

    # Parser and subparser definition, global flags should be here.
    parser = ArgumentParser(prog="ytm-api", description="Python script created\
                            to easely fetch data from the Youtube Music API\
                            from command line, where I can use jq, yt-dlp and\
                            other tools to automate some downloaidng process.")
    subparser = parser.add_subparsers(title="subcommands", dest="subcommand")

    parser.add_argument("--version", "-v", action="version",
                        version=f"%(prog)s {VERSION}")
    parser.add_argument("--pipe", "-p", action="store_true", help="...TODO...")

    # Search subcommand parser.
    search = subparser.add_parser("search", help="Given a list of terms to\
                                  search, it will iterate over each one and\
                                  return the results in a JSON array string.")

    search.add_argument("terms", nargs="*", help="...TODO...")
    search.add_argument("--top-result-only", "-t", action="store_true",
                        help="Filter the search output to only return the top\
                        results JSON object.")

    # Artist subcommand parser.
    artist = subparser.add_parser("artist", help="Fetch information about all\
                                  data from a artist profile uising its ID.\
                                  This data will include metada data info like\
                                  description, name, etc. and songs info such\
                                  as albums, singles, urls, etc.")

    artist.add_argument("ids", nargs="*", help="...TODO...")

    # This will parse everything, including the subcommand parsers.
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_app_args(argv[1:])

    # Include the pipeline args and parse it again if the user used the --pipe.
    while args.pipe:
        line = stdin.readline().strip()

        if not line:
            args = parse_app_args(argv[1:])

            break

        argv.append(line)

    main(args)
