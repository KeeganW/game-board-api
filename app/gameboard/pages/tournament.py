import json
import random
from json import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from gameboard.models import Bracket, Tournament, BracketType, Team, BracketRound
from gameboard.queries.find import find_tournaments
from gameboard.queries.search import search_tournament_by_id, search_player_by_id, search_round_by_id, \
    search_groups_by_player
from gameboard.utils import get_user_info


@login_required
def all_tournaments(request):
    """
    The group page, which contains statistics, graphs, and players within a group.

    :param request: A html request.
    :param message: A message to display on the page in the case of an error.
    :return:
    """
    gb_user = get_user_info(request)

    # Setup dictionary with data to be returned with render
    data = dict()
    data['player'] = gb_user
    data['tournaments'] = find_tournaments(gb_user)
    # Get data for this tournament
    return render(request, "tournament.html", data)


@login_required
def tournament(request, tournament=None):
    """
    The group page, which contains statistics, graphs, and players within a group.

    :param request: A html request.
    :param message: A message to display on the page in the case of an error.
    :return:
    """
    gb_user = get_user_info(request)

    # Setup dictionary with data to be returned with render
    data = dict()
    data['player'] = gb_user

    # Get data for this tournament
    return render(request, "tournament.html", data)


@login_required
def add_tournament(request):
    """
    Adds a tournament to the user's group using a provided name and bracket type.

    :param HttpRequest request: A user request whose body contains name and bracketType
    :var str name: The name of the tournament to be created
    :var BracketType bracketType: The type of bracket this tournament will be following
    :return: A JSON response containing a message on failure, or the new tournament id on success
    """
    if request.method == "POST":
        gb_user = get_user_info(request)
        try:
            data = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse(data={"message": "No JSON provided"}, status=500)
        if gb_user and "name" in data and "bracketType" in data:
            # Check that bracket type is accepted
            try:
                bracket_type = BracketType[data["bracketType"]]
            except KeyError:
                return JsonResponse(data={"message": "This bracket type doesn't exist"}, status=500)
            # Everything looks good, let's add this tournament.
            try:
                # Create new bracket
                new_bracket = Bracket(type=bracket_type)
                new_bracket.save()

                try:
                    new_tournament = Tournament(name=data["name"], bracket=new_bracket, group=gb_user.primary_group)
                    new_tournament.save()
                except Exception as e:
                    new_bracket.delete()
                    return JsonResponse(data={"message": "Error creating tournament..." + repr(e)}, status=500)
                return JsonResponse(data={"tournament": new_tournament.id}, status=201)
            except Exception as e:
                return JsonResponse(data={"message": "An error occurred while adding the tournament..." + repr(e)}, status=500)
        return JsonResponse(data={"message": "Must have the following fields: 'name', 'bracketType'"}, status=500)
    else:
        return JsonResponse(data={"message": "This request is only supported by the following methods: ['POST']"}, status=500)


@login_required
def add_team(request):
    """
    Adds a team to a tournament the user controls.

    :param HttpRequest request: A user request whose body contains the following
    :var str name: The name of this team
    :var str tournamentId: The tournament we want to add this team to
    :var list playerIds: A list of player ids to add to this team
    :return: A JSON response containing a message on failure, or the new team id on success
    """
    if request.method == "POST":
        gb_user = get_user_info(request)
        try:
            data = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse(data={"message": "No JSON provided"}, status=500)
        if gb_user and "playerIds" in data and "name" in data and "tournamentId" in data:
            # TODO: Maybe, for each player, check that their id is in this group
            try:
                current_tournament = search_tournament_by_id(data["tournamentId"])
                teammates = data["playerIds"]

                # Check if user has access to add to this tournament
                if not player_can_add_to(gb_user, current_tournament):
                    return JsonResponse(data={"message": "User does not have access to this tournament"}, status=500)

                # Player can make this team, so make it
                team = Team(name=data["name"], color=data["color"] if "color" in data else ''.join([random.choice('ABCDEF0123456789') for color_place in range(6)]))
                team.save()

                # Add teammates to team
                try:
                    for player_id in teammates:
                        print("Player", player_id, "id", search_player_by_id(player_id))
                        team.players.add(search_player_by_id(player_id))
                except Exception as e:
                    team.delete()
                    return JsonResponse(data={"message": "An error occurred while adding all players to team..." + repr(e)}, status=500)

                # Team is finished, so add the team to the bracket
                current_tournament.bracket.teams.add(team)
                return JsonResponse(data={"team": team.id}, status=201)
            except Exception as e:
                return JsonResponse(data={"message": "An error occurred while adding the team..." + repr(e)}, status=500)
        return JsonResponse(data={"message": "Must have the following fields: 'name', 'tournamentId', and 'playerIds'"}, status=500)
    else:
        return JsonResponse(data={"message": "This request is only supported by the following methods: ['POST']"}, status=500)


@login_required
def add_bracket_round(request):
    """
    Adds a team to a tournament the user controls.

    :param HttpRequest request: A user request whose body contains the following
    :var list roundId: A round id for the game that was played
    :var str tournamentId: The tournament we want to add this team to
    :var str match: The name of this team
    :return: A JSON response containing a message on failure, or the new team id on success
    """
    if request.method == "POST":
        gb_user = get_user_info(request)
        try:
            data = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse(data={"message": "No JSON provided"}, status=500)
        if gb_user and "roundId" in data and "tournamentId" in data and "match" in data:
            try:
                round_id = data["roundId"]
                current_tournament = search_tournament_by_id(data["tournamentId"])
                match = data["match"]
                round = search_round_by_id(round_id)

                # Check if user has access to add to this tournament
                if not player_can_add_to(gb_user, current_tournament):
                    return JsonResponse(data={"message": "User does not have access to this tournament"}, status=500)

                # Check if user has access to add to this round
                if not player_can_add_to(gb_user, round):
                    return JsonResponse(data={"message": "User does not have access to this round"}, status=500)

                # Player can make this bracket round, so add it
                bracket_round = BracketRound(match=match, round=round)
                bracket_round.save()

                # Bracket round is created, so add the round to the bracket
                current_tournament.bracket.rounds.add(bracket_round)
                return JsonResponse(data={"bracketRound": bracket_round.id}, status=201)
            except Exception as e:
                return JsonResponse(data={"message": "An error occurred while adding the round to this tournament..." + repr(e)}, status=500)
        return JsonResponse(data={"message": "Must have the following fields: 'roundId', 'tournamentId', and 'match'"}, status=500)
    else:
        return JsonResponse(data={"message": "This request is only supported by the following methods: ['POST']"}, status=500)


def player_can_add_to(player, item_with_group):
    """
    Check if a player is part of the group that this item is in.

    :param player:
    :param item_with_group:
    :return:
    """
    return search_groups_by_player(player).filter(id=item_with_group.group.id).first() is not None
