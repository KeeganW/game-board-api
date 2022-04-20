import json

from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET

from gameboard.helpers.import_helper import ImportScores, ExportScores
from gameboard.models import Player, Round, Game, PlayerRank, Tournament, Group, BracketRound
from gameboard.serializers import GroupSerializer


def import_scores(request):
    """
    Imports a set of scores from a dataset in a standard format. See dataset.csv as an example.

    :param request: The user's request. Not uses in this function.
    :return: A redirect to the index page, once the import is complete.
    """
    ImportScores()

    return 'Imported'


def export_scores(request):
    """
    Exports the data to a standard format that can be imported again later.

    :param request: The user's request. Not uses in this function.
    :return: Redirects to the index page, once the export is complete.
    """
    ExportScores()

    return 'Exported'


@require_GET
def tournament_stats(request, pk):
    # TODO check that we can access this stuff
    tournament_query = Tournament.objects.filter(pk=pk)
    if len(tournament_query) > 0:
        tournament = tournament_query.first()
        # Get all the stats associated with this tournament.
        # Get current scores
        # This can be calculated by assigning point values to every 1, 2, 3, and 4 placement
        # TODO make scoring customizable. For now go 9, 7, 5, 3 respectively
        scoring = {
            1: 9,
            2: 7,
            3: 5,
            4: 3,
        }
        scores_by_team = {}  # key: team pk, value: cumulative score
        team_by_players = {}  # key: player pk, value: team pk
        # For each team, get all players.
        for team in tournament.bracket.teams.all():
            team_name = team.name
            scores_by_team[team_name] = 0
            for team_player in team.players.all():
                team_by_players[team_player.pk] = team_name

        # Go through all matches in bracket, find each player that played, find their associated team, and add ranking
        for match in tournament.bracket.rounds.all():
            for player_rank in match.round.players.all():
                players_team = team_by_players[player_rank.player.pk]
                if players_team is not None and player_rank.rank is not None:
                    scores_by_team[players_team] += scoring[player_rank.rank]

        # Get current weighted scores
        # TODO ask kevin how this is calculated
        return JsonResponse({
            "detail": "Success",
            "scoring": scores_by_team,
        })
    return JsonResponse(
        {"detail": "Invalid identifier"},
        status=401,
    )

@require_POST
def add_match(request):
    data = json.loads(request.body)
    print(data)
    round_pk = data.get('round')[0]
    match = data.get('match')
    tournament_pk = data.get('tournament')
    if round_pk is None or match is None or tournament_pk is None:
        return JsonResponse({
            "errors": {
                "__all__": "Please enter match, round, and tournament"
            }
        }, status=400)

    round = Round.objects.filter(pk=round_pk).first()
    match = BracketRound(match=match, round=round)
    match.save()
    tournament = Tournament.objects.filter(pk=tournament_pk).first()
    tournament.bracket.rounds.add(match)

    return JsonResponse({
        "detail": "Success",
        "pk": tournament_pk,
    })


@require_POST
def add_round(request):
    data = json.loads(request.body)
    # TODO make sure this has length
    game = data.get('game')[0]
    date = data.get('playedOn')
    players = data.get('players')
    # TODO Check that players, ranks, and scores are all the same length.
    if game is None or date is None or players is None:
        return JsonResponse({
            "errors": {
                "__all__": "Please enter game, date, and players"
            }
        }, status=400)

    scores = []
    ranks = []
    for player in players:
        scores.append(data.get('score-' + player))
        ranks.append(data.get('rank-' + player))

    game = Game.objects.filter(name=game).first()
    round = Round(game=game, date=date, group=request.user.primary_group)
    round.save()

    for i in range(len(players)):
        this_player = Player.objects.filter(username=players[i]).first()
        player_rank = PlayerRank(player=this_player, rank=ranks[i], score=scores[i])
        player_rank.save()
        round.players.add(player_rank)

    # TODO create all player ranks
    return JsonResponse({
        "detail": "Success",
        "pk": round.pk,
    })


@require_GET
def add_round_info(request):
    if request.user.is_authenticated:
        # Get all players in this group
        group = request.user.primary_group
        group_players = []
        for player in group.players.all():
            group_players.append({
                "pk": player.pk,
                "username": player.username,
            })

        # Gather all the games available
        games = []
        for game in Game.objects.all():
            games.append({
                "pk": game.pk,
                "name": game.name,
            })

        # Return accumulated data
        data = {
            "detail": "Success",
            "player": {
                "pk": request.user.pk,
                "username": request.user.username,
            },
            "group": {
                "pk": group.pk,
                "name": group.name,
                "players": group_players,
            },
            "games": games,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({
            "errors": {
                "__all__": "User is not authenticated"
            }
        }, status=401)


@require_GET
def tournament_info(request, pk):
    # TODO check that we can access this stuff
    tournament_query = Tournament.objects.filter(pk=pk)
    if len(tournament_query) > 0:
        # Get basic tournament info
        tournament = tournament_query.first()
        bracket = tournament.bracket

        # For every team, get their information
        bracket_teams = []
        for team in bracket.teams.all():
            # Gather all player info
            team_players = []
            for team_player in team.players.all():
                team_players.append({
                    'pk': team_player.pk,
                    'username': team_player.username,
                })

            bracket_teams.append({
                'pk': team.pk,
                'name': team.name,
                'color': team.color,
                'players': team_players,
            })

        # For every match, gather information
        bracket_rounds = []
        for match in bracket.rounds.all():
            game_round = match.round

            # Gather round info
            round_ranks = []
            for player_rank in game_round.players.all():
                round_ranks.append({
                    'pk': player_rank.pk,
                    'player': {
                        'pk': player_rank.player.pk,
                        'username': player_rank.player.username,
                    },
                    'rank': player_rank.rank,
                    'score': player_rank.score,
                })

            bracket_rounds.append({
                'pk': match.pk,
                'match': match.match,
                'round': {
                    'pk': game_round.pk,
                    'game': {
                        'pk': game_round.game.pk,
                        'name': game_round.game.name,
                    },
                    'date': game_round.date,
                    'players': round_ranks,
                }
            })

        # Append it all to the return object
        data = {
            'detail': 'Success',
            'tournament': {
                'pk': tournament.pk,
                'name': tournament.name,
                'group': tournament.group.pk,
                'bracket': {
                    'pk': bracket.pk,
                    'type': bracket.type,
                    'teams': bracket_teams,
                    'rounds': bracket_rounds,
                }
            }
        }
        return JsonResponse(data)
    return JsonResponse(
        {"detail": "Invalid identifier"},
        status=401,
    )


@require_GET
def player_info(request):
    if request.user.is_authenticated:
        group_serializer = GroupSerializer(request.user.primary_group, context={"request": request})
        data = {
            "detail": "Success",
            "playerPk": request.user.pk,
            "groupPk": group_serializer.data['pk'],
            "groupName": group_serializer.data['name'],
            "groupImageUrl": group_serializer.data['group_picture'],
        }
    else:
        data = {
            "detail": "Failure",
            "playerPk": -1,
            "groupPk": -1,
            "groupName": '',
            "groupImageUrl": '',
        }
    return JsonResponse(data)


@ensure_csrf_cookie
def set_csrf_token(request):
    """
    This will be `/api/set-csrf-cookie/` on `urls.py`
    """
    return JsonResponse({"details": "CSRF cookie set"})


@require_POST
def login_view(request):
    """
    This will be `/api/login/` on `urls.py`
    """
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        return JsonResponse({
            "errors": {
                "__all__": "Please enter both username and password"
            }
        }, status=400)
    gb_player = authenticate(username=username, password=password)
    if gb_player is not None:
        login(request, gb_player)
        group_serializer = GroupSerializer(gb_player.primary_group, context={"request": request})
        return JsonResponse({
            "detail": "Success",
            "playerPk": gb_player.pk,
            "groupPk": gb_player.primary_group.pk,
            "groupName": gb_player.primary_group.name,
            "groupImageUrl": group_serializer.data['group_picture'],
        })
    return JsonResponse(
        {"detail": "Invalid credentials"},
        status=401,
    )


def logout_view(request):
    """
    This will be `/api/login/` on `urls.py`
    """
    logout(request)
    return JsonResponse(
        {"detail": "Logged user out"},
        status=200,
    )
