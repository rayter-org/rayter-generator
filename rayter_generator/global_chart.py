import numpy

def get_global_chart(games):
    global_placements = get_global_placements(games)
    return global_chart_placements(global_placements)

# Returns a dictionary of players and their placements in all games.
# Only games with at least 3 players are included.
# Only players with at least 3 matches in each of those games are included.
# The dictionary has the following structure:
# {
#   "player_name": [
#     {
#       "game_name": "A game name",
#       "normalized_placement": 0.5,
#       "game_count": 5
#     },
#     {
#       "game_name": "Another game name",
#       "normalized_placement": 0.25,
#       "game_count": 3
#     }
#   ]
# }
# The "game_count" value is the number of matches the player has played in the game.
# This is used to weight the placement in the average placement calculation.
# The "normalized_placement" value is the placement of the player in the game,
# normalized to a number between 0 and 1, inclusive.
# The lowest placement is 0, the highest is 1.
# The game name is included for debugging purposes and is currently not used.
def get_global_placements(games):
    global_placements = {}
    for game in games:
      players = game["ratings"]
      placement = 0
      # Only include games with at least 3 players
      if len(players) >= 3:
        for player_name, game_count, rating, delta in players:
            if player_name not in global_placements:
                global_placements[player_name] = []

            # Only include placements in games where the player has played at least 3 matches
            if (game_count >= 3):
                # normalize placement to a number between 0 and 1, inclusive
                # To make it inclusive, subtract 1 from the length of the players list.
                # If the players list contains only one player, this would lead to
                # division by zero. But that shouldn't happen, right...?
                normalized_placement = placement / float(len(players) - 1)
                global_placements[player_name].append({
                    "game_name": game["game_name"],
                    "normalized_placement": normalized_placement,
                    "game_count": game_count
                })
            placement = placement + 1

    return global_placements


# Returns an ordered list of players and their average placement in all games.
# Only players with at least 3 matches in each of their games are included.
# The list is ordered by the average placement, with the lowest average placement first.
# The list has the following structure:
# [
#   {
#     "player_name": "A player name",
#     "average": 0.5
#   },
#   {
#     "player_name": "Another player name",
#     "average": 0.25
#   }
# ]
# The "average" value is the average placement of the player in all games.
# This is calculated by taking the weighted average of the normalized placements
# in all games. The weight is the number of matches the player has played in the game.
# Weighted averages are used to give more weight to games where the player has played
# more matches.
def global_chart_placements(placements):
    average_placements = []
    for player_name, player_data in placements.items():
        # If player has played at least 3 games
        if len(player_data) >= 3:
            # Create a list of placements for all games
            player_placements = list(map(lambda placement: placement["normalized_placement"], player_data))
            # Create a matching list of the number of played matches for each game
            player_counts = list(map(lambda placement: placement["game_count"], player_data))

            average = numpy.average(player_placements, weights=player_counts)
            average_placements.append({
                "player_name": player_name,
                "average": average
              })

    average_placements.sort(key=lambda average_placement: average_placement["average"])

    return average_placements
