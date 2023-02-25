from io import StringIO

from rayter.game_parser import GamesParser
from rayter.rater import Rater


def parse_game_file(path, slug):
    """
    Fetch game file and re-calculate ratings. If the game file does not exist, the data will be deleted.
    """
    with open(path, "r") as f:
        content = f.read()

    parser = GamesParser(StringIO(content), slug)
    matches = parser.parse_file()
    rater = Rater(matches)
    ratings = rater.rate_games(parser.score_type)

    if len(matches) > 0:
        game = {
            "slug": slug,
            "game_name": parser.game_name,
            "rating_history": {name:player.rating_history for name, player in rater.players.items()},
            "ratings": ratings,
            "count": len(matches),
            "score_type": parser.score_type
        }

        return game
    else:
        return None
