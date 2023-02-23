import argparse
import os
import pathlib
import shutil

from .games import refresh_from_game_file
from .render import render_game_page, render_index_page
from .settings import ROOT_DIR


def main():
    arg_parser = argparse.ArgumentParser(
        description="Generate Rayter website from game files",
    )
    arg_parser.add_argument(
        "--games-path",
        type=pathlib.Path,
        help="Path to directory containing game files",
        required=True,
    )
    arg_parser.add_argument(
        "--output",
        type=pathlib.Path,
        help="Path to directory to output rendered files",
        required=True,
    )
    args = arg_parser.parse_args()
    #print(args)

    games_path = args.games_path
    output_path = args.output

    games = []
    for filename in os.listdir(games_path):
        if not filename.endswith(".txt"):
            continue
        # remove .txt from filename
        name = filename[:-4]
        games.append(refresh_from_game_file(os.path.join(games_path, filename), name))

    # render game pages
    for game in games:
        render_game_page(game, output_path)

    # render index page
    render_index_page(games, output_path)

    # recursively copy static files to output directory
    print("Copying static files")
    shutil.copytree(
        os.path.join(ROOT_DIR, "static"), 
        os.path.join(output_path, "static"), 
        dirs_exist_ok=True,
    )


if __name__ == '__main__':
    main()
