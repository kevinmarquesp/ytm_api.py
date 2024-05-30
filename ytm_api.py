#!/usr/bin/env python3

from sys import argv, stdin, stderr
from argparse import Namespace, ArgumentParser
from json import dumps
from concurrent.futures import ThreadPoolExecutor

try:
    from ytmusicapi import YTMusic

except ModuleNotFoundError as err:
    stderr.write(f"[ERRO] {err}.\n")

    exit(1)


# The CLI related functions will be below.

def search(ytm: YTMusic, terms: list[str], is_top: bool) -> list[dict]:
    if len(terms) == 0:
        raise Exception("No search therms specified")

    def search_term(term):
        result = ytm.search(term)

        if is_top:
            result = filter(lambda e: e["category"] == "Top result", result)
            result = list(result)

        return result

    results = []

    with ThreadPoolExecutor(max_workers=12) as executor:
        for result in list(executor.map(search_term, terms)):
            results.extend(result)

    return results


def artist(ytm: YTMusic, ids: list[str]) -> list[dict]:
    """Featch the artist information, the custom flags is suposed to be used
    as a filter mechanism. It will return a list of dicts or a simple dict if
    the list has only one dict element.
    """
    results = []

    for id in ids:
        result = ytm.get_artist(id)

        results.append(result)

    return results


def albums(ytm: YTMusic, ids: list[str]) -> list[dict]:
    """...TODO...
    """
    results = []

    for id in ids:
        artist = ytm.get_artist(id)

        # Some artists may have any albums.
        try:
            browse_id = artist["albums"]["browseId"]
        except KeyError as _:
            continue

        # Some artists have just a few albums that doesn't need a browse page.
        if browse_id:
            params = artist["albums"]["params"]
            results += ytm.get_artist_albums(browse_id, params, limit=None)

            continue

        results += artist["albums"]["results"]

    return results


def songs(ytm: YTMusic, ids: list[str]) -> list[dict]:
    results = []

    for id in ids:
        artist = ytm.get_artist(id)

        # Some artists may have any albums.
        try:
            browse_id = artist["songs"]["browseId"]
        except KeyError as _:
            continue

        # Some artists have just a few albums that doesn't need a browse page.
        if browse_id:
            params = artist["songs"]["params"]
            results += ytm.get_artist_albums(browse_id, params, limit=None)

            continue

        results += artist["songs"]["results"]

    return results


def singles(ytm: YTMusic, ids: list[str]) -> list[dict]:
    results = []

    for id in ids:
        artist = ytm.get_artist(id)

        # Some artists may have any albums.
        try:
            browse_id = artist["singles"]["browseId"]
        except KeyError as _:
            continue

        # Some artists have just a few albums that doesn't need a browse page.
        if browse_id:
            params = artist["singles"]["params"]
            results += ytm.get_artist_albums(browse_id, params, limit=None)

            continue

        results += artist["singles"]["results"]

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
        case "albums":
            result = albums(ytm, args.ids)
        case "songs":
            result = songs(ytm, args.ids)
        case "singles":
            result = singles(ytm, args.ids)

    result_json = dumps(result, indent=JSON_INDENT_SIZE)

    print(result_json)


def parse_app_args(args: list[str]) -> Namespace:
    """It does what you expect, it uses the argparse builtin Python library to
    parse the command line argumens AND subcommands. In the source code, try to
    keep each subcommand parser separated by a commentary to improve
    readability.
    """
    VERSION = "2.7.1"

    # Parser and subparser definition, global flags should be here.
    parser = ArgumentParser(prog="ytm-api", description="Python script created\
                            to easely fetch data from the Youtube Music API\
                            from command line, where I can use jq, yt-dlp and\
                            other tools to automate some downloaidng process.")
    subparser = parser.add_subparsers(title="subcommands", dest="subcommand")

    parser.add_argument("--version", "-v", action="version",
                        version=f"%(prog)s {VERSION}")
    parser.add_argument("--pipe", "-p", action="store_true", help="Will read\
                        each line from the pipeline and include in the list\
                        of arguments. If it's empty, it will freeze the\
                        execution of this script, be aware.")

    # Search subcommand parser.
    search = subparser.add_parser("search", help="Given a list of terms to\
                                  search, it will iterate over each one and\
                                  return the results in a JSON array string.")

    search.add_argument("terms", nargs="*", help="List for terms to search,\
                        use quotes to specify more than one search query.")
    search.add_argument("--top-result-only", "-t", action="store_true",
                        help="Filter the search output to only return the top\
                        results JSON object.")

    # Artist subcommand parser.
    artist = subparser.add_parser("artist", help="Fetch information about all\
                                  data from a artist profile uising its ID.\
                                  This data will include metada data info like\
                                  description, name, etc. and songs info such\
                                  as albums, singles, urls, etc.")

    artist.add_argument("ids", nargs="*", help="List of artist IDs to fetch,\
                        use quotes to specify more than one artist ID.")

    # Albums subcommand parser
    albums = subparser.add_parser("albums", help="Fetch the album data from an\
                                  artist given its ID.")

    albums.add_argument("ids", nargs="*", help="List of artist IDs to fetch,\
                        use quotes to specify more than one artist ID.")

    # Songs subcommand parser
    songs = subparser.add_parser("songs", help="...TODO...")

    songs.add_argument("ids", nargs="*", help="List of artist IDs to fetch,\
                       use quotes to specify more than one artist ID.")

    # Singles subcommand parser
    singles = subparser.add_parser("singles", help="...TODO...")

    singles.add_argument("ids", nargs="*", help="List of artist IDs to fetch,\
                         use quotes to specify more than one artist ID.")

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

    try:
        main(args)

    except Exception as err:
        stderr.write(f"\033[31m{type(err)} :: {err}\033[m\n")
        exit(1)
