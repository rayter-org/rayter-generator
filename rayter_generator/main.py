import argparse
import os
import pathlib
import shutil
import sys

from .env import GeneratorEnvironment
from .games import get_games
from .players import get_all_players
from .render import render_game_page, render_index_page, render_player_page, render_game_json, render_player_image
from .global_chart import get_global_chart

def _main(args):
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
    arg_parser.add_argument(
        "--config",
        type=pathlib.Path,
        help="Path to configuration file in TOML format. If not specified, will look for config file at: `./config/rayter.toml` and `./rayter.toml`",
        required=False,
    )
    arg_parser.add_argument(
        "--players",
        type=pathlib.Path,
        help="Path to player metadata file in JSON format. If not specified, will look for players file at: `./config/players.json` and `./players.json`",
        required=False,
    )
    args = arg_parser.parse_args(args)

    try:
        env = GeneratorEnvironment(
            games_path=args.games_path,
            output_path=args.output,
            config_path=args.config,
            players_path=args.players,
        )

        # get games
        games = get_games(env)

        # get players
        players = get_all_players(games, env)

        # get global chart
        global_chart = get_global_chart(games)

        # render player images, with the side effect of adding image filenames to players
        for player in players.values():
            render_player_image(env, player)

        # render player pages
        for player in players.values():
            render_player_page(env, player)

        # render game pages
        for game in games:
            render_game_page(env, game, players)

        # render game json
        for game in games:
            render_game_json(env, game)

        # render index page
        render_index_page(env, games, players, global_chart)

        # recursively copy static files to output directory
        print("Copying static files")
        shutil.copytree(
            os.path.join(env.root_path, "static"),
            os.path.join(env.output_path, "static"),
            dirs_exist_ok=True,
        )
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: {e.strerror} ({e.filename})\n")
        sys.exit(1)



def main():
    _main(sys.argv[1:])


if __name__ == '__main__':
    main()
