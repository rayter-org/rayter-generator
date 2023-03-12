import hashlib
import urllib

def create_player_from_games(name, games):
    ratings = []

    for game in games:
        players = game["ratings"]
        placement = 0
        for player_name, _0, rating, _1 in players:
            if player_name == name:
                ratings.append(
                    (game["slug"], game["game_name"], rating, placement))
            placement += 1

    # Sort ratings by rating, best first. The actual rating is the third element in the tuple.
    ratings.sort(key=lambda rating: int(rating[2]), reverse=True)

    player = {
        "name": name,
        "slug": name,
        "ratings": ratings,
    }

    return player

# Creates an image url for a player. If the player has an email, use gravatar. Otherwise use a generated avatar.
def make_image_url(player):
    # Don't override explicit imageUrl
    if 'imageUrl' in player:
        return player['imageUrl']

    gravatar_size = 300

    if 'email' in player:
        email = player['email']
        hash = hashlib.md5(email.lower().encode("utf-8")).hexdigest()
        gravatar_url = "https://www.gravatar.com/avatar/" + hash + "?"
        gravatar_url += urllib.parse.urlencode({
            's': str(gravatar_size)
        })
        return gravatar_url
    else:
        return None


def get_all_players(games, env):
    players = {}
    players_metadata = env.players_metadata

    # Collect all players from all games
    for game in games:
        for player in game["ratings"]:
            name = player[0]
            if not name in players:
                players[name] = create_player_from_games(name, games)

    # Overwrite generic player values with player metadata from file
    if players_metadata != None:
        for player_name in players_metadata.keys():
            # If player exists in players, update it with all values in the player's metadata
            if player_name in players:
                player_metadata = players_metadata[player_name]
                players[player_name].update(player_metadata)

        # For every player, if they have no image url, try to create one from their metadata
        # FIXME: Should this be moved into create_player_from_games()?
        for player_name in players.keys():
            player = players[player_name]
            if not 'imageUrl' in player:
                player['imageUrl'] = make_image_url(player)

    return players
