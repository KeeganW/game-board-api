"""
Find

Finders are functions which gather a collection of searches to then create a more complicated "search"
"""
from datetime import datetime, timedelta
from operator import itemgetter

from gameboard.models import Group, Game, Player, Tournament
from gameboard.queries.generate import generate_trophies
from gameboard.queries.helpers import average_ranks, generate_dates
from gameboard.queries.search import search_games_by_player, search_ranks_by_player, search_wins_by_player, \
    search_games_by_player_in_time, search_wins_by_player_in_time, search_ranks_by_player_in_time, \
    search_wins_by_player_in_time_for_heavy, search_wins_by_player_in_time_that_are_unique, \
    search_wins_by_player_in_time_for_game


def find_win_percentage(player):
    """
    Calculate the win percentage for a player.

    :param player: A Player object, which contains the user info
    :return: The player's win percentage across all games played (and all groups)
    """
    percentage = 0
    if player:
        games_played = search_games_by_player(player)
        wins = search_wins_by_player(player)
        if len(games_played) > 0:
            percentage = (len(wins)/len(games_played)) * 100
    return percentage


def find_average_placement(player):
    """
    Calculate the average placement for a player.

    :param player: A Player object, which contains the user info
    :return: The player's win percentage across all games played (and all groups)
    """
    average = 0
    if player:
        ranks = list(search_ranks_by_player(player).values_list("rank", flat=True))
        average = average_ranks(ranks)
    return average


def find_favorite_game(player):
    """
    Find the favorite game for a given player. Uses all game data to find what game they play the most.

    :param player: A Player object, which contains the user info
    :return: The player's favorite game (as an object).
    """
    fav_game = ''
    if player.favorite_game:
        return player.favorite_game
    if player:
        games_played = search_games_by_player(player)
        game_dict = dict()
        for g in games_played:
            if g.game.name not in game_dict:
                game_dict[g.game.name] = 0
            game_dict[g.game.name] += 1

        max_count = 0
        for name in game_dict:
            if game_dict[name] > max_count:
                max_count = game_dict[name]
                fav_game = name
    return fav_game


def find_players_in_group(group):
    """
    Find the players who have played a game.

    :param group: A Group object, which contains the group info
    :return: All players who have played a game in a group
    """
    group_id = group.id
    players_ids = Group.objects.filter(id=group_id).values('players')
    players = []
    for item in players_ids:
        players.append(Player.objects.filter(id=item["players"]).first())
    return players


def find_games():
    """
    Get all games
    TODO is this necessary?

    :return: All games as an queryset of objects
    """
    games = Game.objects.all()
    return games


def find_groups(player):
    """
    Finds all groups that a player is a part of

    :param player: A Player object, which contains the user info
    :return: A queryset of group objects the player belongs to
    """
    group = Group.objects.filter(player__user=player.user)

    return group


def find_num_player_in_group(group):
    """
    find the number of players in a group

    :param group: A Group object
    :return: number of players in the group
    """
    players = group.players.all()

    return (len(players))


def find_is_player_admin(group, player):
    """
    Determines if a player is an admin in a group or not.

    :param group: Thr group object to check
    :param player: The player object to check against
    :return: A boolean value
    """
    admins = group.admins.all()
    for admin in admins:
        if player.user.username == admin.user.username:
            return True
    return False

def find_player_status(player):
    """
    Gets a string representing how active a player is across all groups.

    :param player: The player to check if they are active
    :return: A string(number of games needed), green(5), yellow(1-4), red (0)
    """
    # Get the dates for this search
    date_start, date_end = generate_dates("recent")

    # Search for recent games and count them
    recent_games = search_games_by_player_in_time(player, date_start, date_end).count()

    if recent_games > 2:
        return "green"
    elif recent_games > 0:
        return "yellow"
    else:
        return "red"


def find_player_monthly_log(player):
    # Get the dates for this search
    date_start, date_end = generate_dates("recent_year")

    date_log = ['Month']
    wins_log = ['Win Count']
    rate_log = ['Win Rate']
    ranks_log = ['Avg Rank']

    total_months = lambda dt: dt.month + 12 * dt.year
    day = int(date_start.strftime("%d"))
    last_month = date_start
    for total_month in range(total_months(date_start), total_months(date_end)):
        year, month = divmod(total_month, 12)
        month_wins = search_wins_by_player_in_time(player, last_month, datetime(year, month + 1, day)).count()
        total_wins = search_wins_by_player_in_time(player, date_start, datetime(year, month + 1, day)).count()
        total_games = search_games_by_player_in_time(player, date_start, datetime(year, month + 1, day)).count()
        month_ranks = average_ranks(search_ranks_by_player_in_time(player, date_start, datetime(year, month + 1, day)).values_list('rank', flat=True), return_zero_as_null=True)
        last_month = datetime(year, month + 1, 1)

        wins_log.append(month_wins)
        try:
            rate_log.append(round(total_wins/total_games*100, 2))
        except ZeroDivisionError:
            rate_log.append(0)
        ranks_log.append(month_ranks)
        date_log.append(last_month.strftime("%Y-%m-%d"))

    return [date_log, wins_log], [date_log, rate_log], [date_log, ranks_log]

def find_player_activity_log(player):
    """

    :param player:
    :return:
    """
    # Get the dates for this search
    date_start, date_end = generate_dates("recent_year")

    # Search for recent games and count them
    recent_games = search_games_by_player_in_time(player, date_start, date_end)

    activity_log = list()

    # Make sure all dates are filled out
    delta = timedelta(days=1)
    while date_start <= date_end:
        activity_log.append({"date": date_start.strftime("%Y-%m-%d"), "game_count": len(recent_games.filter(date__exact=date_start.strftime("%Y-%m-%d")))})
        date_start += delta

    return activity_log

def find_statistic(group, type, date_string="all"):
    """
    Search a group over a time range for a type of statistic. Here are the statistics you can search, which is set by
    setting the type to the following strings:
        - "wins": The number of wins per player
        - "percentage": The win percentage of a player over the time period
        - "heavy": Only heavy games (as set by the game's heavy flag)
        - "unique": Number of unique game wins

    :param group: The group object of interest
    :param type: A string to query for, see above for possibilities
    :param date_string: A string to represent a time range of interest (see generate_dates())
    :return: A sorted list of tuples, where the first value is the username, and the second is the result of the type
    """
    return_list = []

    # Get the dates for this search
    date_start, date_end = generate_dates(date_string)

    # Loop through all the players
    players = group.players.all()
    for player in players:
        query_result = 0
        if type == "wins":
            query_result = search_wins_by_player_in_time(player, date_start, date_end).count()
        elif type == "percentage":
            try:
                query_result = search_wins_by_player_in_time(player, date_start, date_end).count() / \
                               search_games_by_player_in_time(player, date_start, date_end).count() * 100
                query_result = '{0:.2f}'.format(query_result)
            except ZeroDivisionError:
                # This player hasn't played any games
                query_result = 0
        elif type == "heavy":
            query_result = search_wins_by_player_in_time_for_heavy(player, date_start, date_end).count()
        elif type == "unique":
            query_result = search_wins_by_player_in_time_that_are_unique(player, date_start, date_end).count()
        else:
            # This might be a game, lets try to find this
            if Game.objects.filter(name__exact=type):
                query_result = search_wins_by_player_in_time_for_game(player, date_start, date_end, type).count()
                # if query_result < 5:
                #     query_result = 0

        if float(query_result) > 0:
            return_list.append((player.user.username, query_result))

    return generate_trophies(sorted(return_list, key=itemgetter(1), reverse=True))


def find_tournaments(player):
    print("player", player)
    print(Tournament.objects.filter(group_id=player.primary_group_id).all())
    pass
