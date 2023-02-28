import json
import os

# try to import tomlib, if it fails, use tomli
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from jinja2 import Environment, FileSystemLoader


def get_toml(path):
    with open(path, "rb") as f:
        return tomllib.load(f)

def get_json(path):
    with open(path, "rb") as f:
        return json.load(f)


class GeneratorEnvironment:
    def __init__(self, games_path, output_path, config_path=None, players_path=None):
        self.games_path = games_path
        self.output_path = output_path
        self.config_path = config_path
        self.players_path = players_path
        self.root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))

        if self.config_path:
            self.config = get_toml(self.config_path)
        elif os.path.exists("./config/rayter.toml"):
            self.config = get_toml("./config/rayter.toml")
        elif os.path.exists("./rayter.toml"):
            self.config = get_toml("./rayter.toml")
        else:
            self.config = {
                "site_name": "Rayter",
            }

        if self.players_path:
            self.players_metadata = get_json(self.players_path)
        elif os.path.exists("./config/players.json"):
            self.players_metadata = get_json("./config/players.json")
        elif os.path.exists("./players.json"):
            self.players_metadata = get_json("./players.json")
        else:
            self.players_metadata = {}

        self.jinja_env = Environment(loader=FileSystemLoader(os.path.join(self.root_path, "templates")))
        self.jinja_env.globals.update({
            "CONFIG": self.config,
        })

    def render_template(self, template_path, context, output_path=None):
        contents = self.jinja_env.get_template(template_path).render(context)
        if output_path:
            print('Writing', output_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(contents)
        return contents
