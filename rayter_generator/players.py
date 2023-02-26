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


def get_players(games, env):
    players = {}
    players_metadata = {} # env.players_metadata

    for game in games:
        for player in game["ratings"]:
            name = player[0]
            players[name] = create_player_from_games(name, games)



    # if players_metadata != None:
    #     players = players_result["players"]

    #     # Overwrite generic player values with player metadata
    #     for player in players:
    #         players[player["playerName"]] = player

    #     # For every player, if they have no image add gravatar image or generated avatar
    #     for player in players:
    #         player = players[player]
    #         if not 'imageUrl' in player:
    #             player['imageUrl'] = make_image_url(player)


    return players
