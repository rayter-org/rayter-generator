import os

from jinja2 import Environment, FileSystemLoader

from .settings import ROOT_DIR


def render_game_page(env, game):
    filename = os.path.join(env.output_path, game['slug'], 'index.html')
    env.render_template("game.html", {
        "name": game["game_name"],
        "ratings": game["ratings"],
        "game_name": game["game_name"],
        "slug": game["slug"],
        "players": [], # FIXME Fix players list
        "STATIC_URL": "../static/",
    }, output_path=filename)

def render_player_page(env, player):
    filename = os.path.join(env.output_path, 'player', player['slug'], 'index.html')
    env.render_template("player.html", {
        "player": player,
        "STATIC_URL": "../../static/",
    }, output_path=filename)

def render_index_page(env, games):
    games.sort(key=lambda g: g["count"], reverse=True)
    filename = os.path.join(env.output_path, 'index.html')
    env.render_template("index.html", {
        "games": games,
        "players": [],
        "global_chart": [],
        "log": [],
        "STATIC_URL": "static/",
    }, output_path=filename)
