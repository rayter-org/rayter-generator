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

    # FIXME: (?)
    # All games are traversed twice, first in the loop above and then inside
    # get_games_and_toplist(), maybe they can be combined?
# (games, global_chart) = get_games_and_toplist()

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

    size = 300
    # fallbackImageUrl = 'https://ui-avatars.com/api/?background=random&name=' + player['name'] + '&size=' + str(size)
    fallbackImageUrl = 'https://api.multiavatar.com/' + player['name'] + '.svg'

    if 'email' in player:
        email = player['email']
        hash = hashlib.md5(email.lower().encode("utf-8")).hexdigest()
        gravatar_url = "https://www.gravatar.com/avatar/" + hash + "?"
        gravatar_url += urllib.parse.urlencode({
            's': str(size),
            'd': fallbackImageUrl
        })
        return gravatar_url
    else:
        return fallbackImageUrl


def get_players(games, env):
    players = {}
    players_metadata = env.players_metadata

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

        # For every player, if they have no image add gravatar image or generated avatar
        for player_name in players.keys():
            player = players[player_name]
            if not 'imageUrl' in player:
                player['imageUrl'] = make_image_url(player)

    return players
