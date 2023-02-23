import os

from jinja2 import Environment, FileSystemLoader

from .settings import ROOT_DIR



def get_template(name):
    env = Environment(loader=FileSystemLoader(os.path.join(ROOT_DIR, "templates")))
    return env.get_template(name)


def render_game_page(game, base_path):
    filename = os.path.join(base_path, game['slug'], 'index.html')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    print('Writing', filename)
    with open(filename, 'w') as f:
        f.write(get_template("game.html").render(
            name=game["game_name"],
            players=game["ratings"],
            game_name=game["game_name"],
            users=[],
        ))


def render_index_page(games, base_path):
    games.sort(key=lambda g: g["count"], reverse=True)
    filename = os.path.join(base_path, 'index.html')
    print('Writing', filename)
    with open(filename, 'w') as f:
        f.write(get_template("index.html").render(
            games=games,
            users=[],
            global_chart=[],
            log=[],
        ))
