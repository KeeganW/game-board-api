"""
Search

Searchers are simple filters written over the top of the django ORM in order to provide more specific results
for commonly repeated searches.
"""
from gameboard.models import Round, PlayerRank, Tournament, Player, Group
from gameboard.queries.helpers import get_heavy_game_list


def find_oldest_date():
    return Round.objects.all().order_by('-date').last().date


def search_groups_by_player(player):
    return Group.objects.filter(player__user=player.user)


def search_wins_by_player(player):
    return Round.objects.filter(players__player__user=player.user, players__rank__exact=1)


def search_wins_by_player_in_time(player, date_start, date_end):
    return search_wins_by_player(player).filter(date__range=(date_start, date_end))


def search_ranks_by_player(player):
    return PlayerRank.objects.filter(player__user=player.user)


def search_ranks_by_player_in_time(player, date_start, date_end):
    return search_ranks_by_player(player).filter(game_players__date__range=(date_start, date_end))


def search_games_by_player(player):
    return Round.objects.filter(players__player__user=player.user)


def search_games_by_player_in_time(player, date_start, date_end):
    return search_games_by_player(player).filter(date__range=(date_start, date_end))


def search_games_by_group(group):
    return Round.objects.filter(group=group)


def search_games_by_group_in_time(group, date_start, date_end):
    return search_games_by_group(group).filter(date__range=(date_start, date_end))


def search_wins_by_player_in_time_for_heavy(player, date_start, date_end):
    return search_wins_by_player_in_time(player, date_start, date_end).filter(game__name__in=get_heavy_game_list())


def search_wins_by_player_in_time_that_are_unique(player, date_start, date_end):
    return search_wins_by_player_in_time(player, date_start, date_end).order_by().values_list("game__name").distinct()


def search_wins_by_player_in_time_for_game(player, date_start, date_end, game):
    return search_wins_by_player_in_time(player, date_start, date_end).filter(game__name__exact=game)


def search_round_by_id(round_id):
    return Round.objects.filter(id=round_id).first()


def search_tournament_by_id(tournament_id):
    return Tournament.objects.filter(id=tournament_id).first()


def search_player_by_id(player_id):
    return Player.objects.filter(id=player_id).first()
