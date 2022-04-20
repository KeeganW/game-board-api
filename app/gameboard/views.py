import json
from datetime import datetime

from django.contrib.auth import login, authenticate, logout
from django.core.cache import cache
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from rest_framework import generics
from rest_framework.decorators import permission_classes

from gameboard.forms import AddRoundForm, EditForm, AddGameForm
from gameboard.helpers.import_helper import ImportScores, ExportScores
from gameboard.models import Player, Round, Game, PlayerRank, Tournament
from gameboard.permissions import IsAuthenticatedOrCreate
from gameboard.queries.find import find_games, find_players_in_group, find_groups, find_player_activity_log, \
    find_player_monthly_log, find_statistic, find_favorite_game, find_win_percentage, find_average_placement, \
    find_player_status
from gameboard.queries.generate import favorite_games
from gameboard.queries.helpers import clear_cache, get_cache
from gameboard.queries.search import search_games_by_group, find_oldest_date
from gameboard.serializers import SignUpSerializer, GroupSerializer
from gameboard.utils import get_user_info, get_user_info_by_username
import datetime

""" Non login required functions """


def index(request):
    """
    The index page for the game board application. This is a landing page encouraging new users to sign up. If they are
    signed in, redirect them to their dashboard.

    :param request: The user's request.
    :return: A rendering of a web page for the user to interact with. Either a splash page or a redirect.
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(player))
    else:
        return render(request, "index.html")


def import_scores(request):
    """
    Imports a set of scores from a dataset in a standard format. See dataset.csv as an example.

    :param request: The user's request. Not uses in this function.
    :return: A redirect to the index page, once the import is complete.
    """
    ImportScores()

    return HttpResponseRedirect(reverse(index))


def export_scores(request):
    """
    Exports the data to a standard format that can be imported again later.

    :param request: The user's request. Not uses in this function.
    :return: Redirects to the index page, once the export is complete.
    """
    ExportScores()

    return HttpResponseRedirect(reverse(index))


@permission_classes([IsAuthenticatedOrCreate])
def player(request, player=None, message=None):
    """
    The player's main page, to be shown upon login. Also used to show sub tabs under the player including their
    statistics, trophies, and groups.

    :param request: A html request.
    :param player: A player's username (for looking at other players, not yourself)
    :param message: A message to display on the page in the case of an error.
    :return: A rendering of a web page for the user to interact with.
    """
    # Get game board user
    gb_user = get_user_info(request)

    # Setup dictionary with data to be returned with render
    data = dict()

    # Check if we are looking at another user, or ourselves
    if not player:
        player = gb_user
    else:
        player = get_user_info_by_username(player)
        if player is None:
            # Player provided isn't a real player, so 404
            raise Http404()

    # Create the objects in the data
    data["player"] = player
    data["groups"] = find_groups(gb_user)
    data["message"] = message

    # Add additional data based on the request.
    end_path = request.path_info.split('/')
    if len(end_path) > 1 and end_path[-2] == 'statistics':
        win_log, rate_log, ranks_log = find_player_monthly_log(player)
        data["win_time"] = win_log
        data["rate_time"] = rate_log
        data["rank_time"] = ranks_log
        favorites, game_rate_log = favorite_games(player)
        data["favorite"] = favorites
        data["win_game"] = game_rate_log
        data["activity"] = find_player_activity_log(player)
        return render(request, "player/statistics.html", data)
    elif len(end_path) > 1 and end_path[-2] == 'trophies':
        # Check the cache for the trophies for this group, so we don't have to run a long calculation.
        trophies = get_cache(player.primary_group, 'trophies')
        if trophies:
            # Cached, so return it
            data["trophies"] = trophies
        else:
            # Not cached, get the recent games first
            trophies = dict()
            trophies["recent"] = dict()
            trophies["recent"]["Most Unique Games"] = find_statistic(player.primary_group, "unique", "recent")
            trophies["recent"]["Most Wins"] = find_statistic(player.primary_group, "wins", "recent")
            trophies["recent"]["Most Heavy Wins"] = find_statistic(player.primary_group, "heavy", "recent")
            trophies["recent"]["Highest Win Percentage"] = find_statistic(player.primary_group, "percentage", "recent")
            for game in Game.objects.all():
                trophies["recent"]["Most {} Wins".format(game.name)] = find_statistic(player.primary_group, game.name, "recent")

            # Now get the data from past years
            year = datetime.now().date().year
            oldest = find_oldest_date().year
            while year >= oldest:
                year_str = str(year)
                trophies[year_str] = {}
                trophies[year_str]["Most Unique Games"] = find_statistic(player.primary_group, "unique", year_str)
                trophies[year_str]["Most Wins"] = find_statistic(player.primary_group, "wins", year_str)
                trophies[year_str]["Most Heavy Wins"] = find_statistic(player.primary_group, "heavy", year_str)
                trophies[year_str]["Highest Win Percentage"] = find_statistic(player.primary_group, "percentage", year_str)
                for game in Game.objects.all():
                    trophies[year_str]["Most {} Wins".format(game.name)] = find_statistic(player.primary_group, game.name, year_str)
                year -= 1

            # Store this info in a cache
            cache.set('trophies-{}'.format(player.primary_group.id), trophies, 86400)
            data["trophies"] = trophies
        return render(request, "player/trophies.html", data)
    elif len(end_path) > 1 and end_path[-2] == 'groups':
        # Get all the groups for this user
        data["groups"] = find_groups(player)

        # Get the status of all the players in each group
        status = {}
        for group in data["groups"]:
            for p in group.players.all():
                status[p.user.username] = find_player_status(p)
        data["status"] = status

        return render(request, "player/groups.html", data)
    else:
        # Get the various data points to fill out the profile page
        # primary_group = passed on via player object
        data['favorite_game'] = find_favorite_game(player)
        data['win_rate'] = find_win_percentage(player)
        data['average_placement'] = find_average_placement(player)
        # playing_since = passed on via player object

        return render(request, "player/profile.html", data)


@permission_classes([IsAuthenticatedOrCreate])
def group(request):
    """
    The group page, which contains statistics, graphs, and players within a group.

    :param request: A html request.
    :param message: A message to display on the page in the case of an error.
    :return:
    """
    gb_user = get_user_info(request)

    # Setup dictionary with data to be returned with render
    data = dict()

    # Get data for this group
    data["recent_games"] = search_games_by_group(gb_user.primary_group).order_by('-date')[0:10]  # Limit to the last 10.
    data['player'] = gb_user
    return render(request, "group.html", data)


@permission_classes([IsAuthenticatedOrCreate])
def edit_group(request):
    """
    Edit group information like what players and admins there are, as well as name.

    :param request:
    :return:
    """
    gb_user = get_user_info(request)

    data = dict()

    data['player'] = gb_user
    return render(request, "edit_group.html", data)


@permission_classes([IsAuthenticatedOrCreate])
def add_round(request):
    """
    A data entry page, which allows the user to enter a new game played, also known as a round.

    :param request: The user's request.
    :return: A rendering of a web page for the user to interact with.
    """
    # Get user
    gb_user = get_user_info(request)

    # Get ready with the data to send to the front end
    data = dict()

    add_round_form = AddRoundForm()
    # Only do things if the user has submitted data
    if request.method == "POST":
        # Create the form using the request
        add_round_form = AddRoundForm(request.POST)

        # Check if the data is valid
        if add_round_form.is_valid():
            group = find_groups(gb_user).first()
            game = add_round_form.cleaned_data.get('game')
            date = add_round_form.cleaned_data.get('date')
            players = add_round_form.cleaned_data.get('players').split(",")
            ranks = add_round_form.cleaned_data.get('ranks').split(",")
            scores = add_round_form.cleaned_data.get('scores').split(",")

            # Valid, so add the new game played object
            game_played = Round()
            game_played.game = Game.objects.get(name__exact=game)
            game_played.date = date
            game_played.group = group
            game_played.save()

            for player_index in range(len(players)):
                try:
                    rank = int(ranks[player_index])
                except ValueError:
                    rank = None
                try:
                    score = int(scores[player_index])
                except ValueError:
                    score = None
                player_rank = PlayerRank(player=Player.objects.get(user__username__exact=players[player_index]), rank=rank, score=score)
                player_rank.save()
                game_played.players.add(player_rank)

            clear_cache(gb_user.primary_group)

            response = JsonResponse({})
            response.status_code = 200
            return response
        else:
            # Non valid form, render it on the page
            response = JsonResponse({"error": add_round_form.errors})
            response.status_code = 400
            return response

    # Store the data and send to the view.
    data['add_round_form'] = add_round_form
    data['all_games'] = find_games()
    data['all_players'] = find_players_in_group(find_groups(gb_user).first())
    data['player'] = gb_user
    return render(request, "add_round.html", data)


@permission_classes([IsAuthenticatedOrCreate])
def add_game(request):
    """
    A data entry page, which allows the user to enter a new game played.

    :param request: The user's request.
    :return: A rendering of a web page for the user to interact with.
    """
    # Get user
    gb_user = get_user_info(request)

    # Get ready with the data to send to the front end
    data = dict()

    add_game_form = AddGameForm()
    # Only do things if the user has submitted data
    if request.method == "POST":
        # Create the form using the request
        add_game_form = AddGameForm(request.POST)

        # Check if the data is valid
        if add_game_form.is_valid():
            name = add_game_form.cleaned_data.get('name')
            description = add_game_form.cleaned_data.get('description')

            # Valid, so add the new game played object
            g = Game(name=name, description=description)
            g.save()

            return HttpResponseRedirect(reverse(add_round))

    # Store the data and send to the view.
    data['add_game_form'] = add_game_form
    data['all_games'] = find_games()
    data['player'] = gb_user
    return render(request, "add_game.html", data)


@permission_classes([IsAuthenticatedOrCreate])
def edit_player(request):
    """
    Edit player information, like username, name, password, and upload profile images.

    :param request: A html request, that needs a post request to submit data.
    :return: A rendering of the edit player page.
    """
    # Get user
    gb_user = get_user_info(request)

    # Get ready with the data to send to the front end
    data = dict()

    edit_form = EditForm(gb_user.user.username)
    # Only do things if the user has submitted data
    if request.method == "POST":
        # Create the form using the request
        edit_form = EditForm(gb_user.user.username, request.POST)

        profile_image = None
        if "photo" in request.FILES:
            profile_image = request.FILES['photo']
        # profile_image = request.FILES['profile_image']
        # Check if the data is valid
        if edit_form.is_valid():
            # Get the relevant cleaned data for creating a user
            username = edit_form.cleaned_data['username']
            first_name = edit_form.cleaned_data['first_name']
            last_name = edit_form.cleaned_data['last_name']
            favorite_game = edit_form.cleaned_data['favorite_game']
            password = edit_form.cleaned_data['password']

            # print("profile image is ",username, profile_image)

            if username:
                gb_user.user.username = username
            if first_name:
                gb_user.user.first_name = first_name
            if last_name:
                gb_user.user.last_name = last_name
            if favorite_game:
                gb_user.favorite_game = Game.objects.filter(name=favorite_game).first()
                gb_user.save()
            if password:
                gb_user.user.set_password(password)
            if profile_image:
                gb_user.profile_image = profile_image
                gb_user.save()
            gb_user.user.save()

            login(request, gb_user.user)
            return HttpResponseRedirect(reverse(index))

    data['edit_player_form'] = edit_form
    data['player'] = gb_user
    return render(request, "edit_player.html", data)


class SignUp(generics.CreateAPIView):
    queryset = Player.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [IsAuthenticatedOrCreate]

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
        print(request.user)
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
