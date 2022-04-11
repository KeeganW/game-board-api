from django.db.models import Count

from gameboard.models import Game
from gameboard.queries.helpers import generate_dates
from gameboard.queries.search import search_games_by_player_in_time, search_wins_by_player_in_time


def generate_trophies(sorted_tuples):
    """
    A system for assigning trophies (gold, silver, bronze) to a sorted list of tuples, where the highest values come
    first in the array.

    :param sorted_tuples: A list of tuples, where the first item in the tuple is a name, and the second is a value
    :return: A dictionary, containing gold silver and bronze lists that may or may not be empty
    """
    trophies = {"gold": [], "silver": [], "bronze": []}
    total_trophies_given = 0
    for leader_id in range(len(sorted_tuples)):
        leader = sorted_tuples[leader_id]
        if total_trophies_given == 0:
            # This is the first trophy, it must be gold.
            trophies['gold'].append(leader)
        else:
            if trophies['gold'][0][1] == leader[1]:
                # This person is just as good as the gold player, so add them to gold.
                trophies['gold'].append(leader)
            elif len(trophies['silver']) == 0 or trophies['silver'][0][1] == leader[1]:
                # This person is the first silver trophy (but not gold), or is just as good as the current silver trophy
                trophies['silver'].append(leader)
            elif len(trophies['bronze']) == 0 or trophies['bronze'][0][1] == leader[1]:
                trophies['bronze'].append(leader)
        total_trophies_given += 1
        if total_trophies_given >= 3:
            # Check if it is safe to do a lookahead
            if leader_id + 1 >= len(sorted_tuples):
                break  # End of the list, so return
            else:
                # Check if the current value is equal to the next. If so, we want to add the next value too
                if sorted_tuples[leader_id + 1][1] != leader[1]:
                    break  # Next value is worse, so return

    return trophies


def favorite_games_wins(player):
    # Get the dates for this search
    date_start, date_end = generate_dates("all")

    # Get all the games
    all_games = search_games_by_player_in_time(player, date_start, date_end)
    all_wins = search_wins_by_player_in_time(player, date_start, date_end)

    # Group the games by their game_id, then count how many of each id there are
    sorted_most_played = all_games.values("game_id").annotate(total=Count('game_id')).order_by('-total')
    sorted_most_wins = all_wins.values("game_id").annotate(total=Count('game_id')).order_by('-total')

    total_games = {}
    for game_count in sorted_most_played:
        total_games[game_count['game_id']] = game_count['total']

    favorites = []
    game_log = []
    win_rate = ['Win Rate']
    loop_count = 0
    other_count = 0
    # Reformat wins into simple array
    for game_win in sorted_most_wins:
        game = Game.objects.filter(id=game_win["game_id"]).first()
        if loop_count < 5:
            favorites.append([game.name, game_win["total"]])
            game_log.append(game.name)
            win_rate.append(round(game_win["total"]/total_games[game.id]*100, 2))
        else:
            # Add to "other"
            other_count += game_win["total"]
        loop_count += 1
    favorites.append(['Other Games', other_count])

    return favorites, [game_log, win_rate]

def favorite_games(player):
    # Get the dates for this search
    date_start, date_end = generate_dates("all")

    # Get all the games
    all_games = search_games_by_player_in_time(player, date_start, date_end)
    all_wins = search_wins_by_player_in_time(player, date_start, date_end)

    # Group the games by their game_id, then count how many of each id there are
    sorted_most_played = all_games.values("game_id").annotate(total=Count('game_id')).order_by('-total')
    sorted_most_wins = all_wins.values("game_id").annotate(total=Count('game_id')).order_by('-total')

    total_games = {}
    for game_count in sorted_most_played:
        total_games[game_count['game_id']] = game_count['total']

    favorites = []
    game_log = []
    win_rate = ['Win Rate']
    loop_count = 0
    other_count = 0
    for game_play in sorted_most_played:
        game = Game.objects.filter(id=game_play["game_id"]).first()
        if loop_count < 5:
            favorites.append([game.name, game_play["total"]])
        else:
            # Add to "other"
            other_count += game_play["total"]
        loop_count += 1
    favorites.append(['Other Games', other_count])

    loop_count = 0
    # Reformat wins into simple array
    for game_win in sorted_most_wins:
        game = Game.objects.filter(id=game_win["game_id"]).first()
        if loop_count < 5:
            game_log.append(game.name)
            win_rate.append(round(game_win["total"]/total_games[game.id]*100, 2))
        loop_count += 1

    return favorites, [game_log, win_rate]
