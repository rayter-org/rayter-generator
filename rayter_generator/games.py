from io import StringIO

from rayter.game_parser import GamesParser
from rayter.rater import Rater


def refresh_from_game_file(path, name):
    """
    Fetch game file and re-calculate ratings. If the game file does not exist, the data will be deleted.
    """
    with open(path, "r") as f:
        content = f.read()

    parser = GamesParser(StringIO(content), name)
    games = parser.parse_file()
    rater = Rater(games)
    ratings = rater.rate_games(parser.score_type)

    game = {
        "slug": name,
        "game_name": parser.game_name,
        "players": {
            name: player.rating_history
            for (name, player) in list(rater.players.items())
        },
        "ratings": ratings,
        "count": len(games),
        "score_type": parser.score_type
    }

    return game

