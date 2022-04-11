from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
# For static routing for random files that need to be served
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token

from gameboard import views
from gameboard.models import Player
from gameboard.views import index, import_scores, group, add_round, player, gb_logout, edit_player, edit_group, \
    export_scores, gb_login, gb_register, add_game, remove_round, test
from gameboard.pages.tournament import tournament, all_tournaments, add_tournament, add_team, add_bracket_round

# Routers for getting all values from db (developer only) TODO remove this, testing only
router = routers.DefaultRouter()
router.register(r'player', views.PlayerViewSet)
router.register(r'game', views.GameViewSet)
router.register(r'group', views.GroupViewSet)
router.register(r'player_rank', views.PlayerRankViewSet)
router.register(r'round', views.RoundViewSet)
router.register(r'bracket_round', views.BracketRoundViewSet)
router.register(r'team', views.TeamViewSet)
router.register(r'bracket', views.BracketViewSet)
router.register(r'tournament', views.TournamentViewSet)

urlpatterns = [
    # TODO remove this
    path('', include(router.urls)),

    # Main page reference
    path('', index, name="index"),

    # Sets up database
    path('import/', import_scores, name="import"),
    path('export/', export_scores, name="export"),


    path('game/', views.game_detail),
    path('game/<int:pk>/', views.game_detail),

    # # Player specific pages
    # path('player/', player, name="player"),
    # path('player/add/', None, name="player.add"),
    # path('player/edit/', edit_player, name="player.edit"),
    # path('player/remove/', None, name="player.remove"),
    # path('player/<slug:player>/', player, name="player.specific"),
    # path('player/<slug:player>/profile/', player, name="player.specific.profile"),
    # path('player/<slug:player>/statistics/', player, name="player.specific.statistics"),
    # path('player/<slug:player>/trophies/', player, name="player.specific.trophies"),
    # path('player/<slug:player>/groups/', player, name="player.specific.groups"),
    #
    # # Group
    # path('group/', group, name="group"),
    # path('group/add/', None, name="group.add"),
    # path('group/edit/', edit_group, name="group.edit"),
    # path('group/remove/', None, name="group.remove"),
    # path('group/<slug:group>/', None, name="group.specific"),
    #
    # # Round
    # path('round/', None, name="round"),
    # path('round/add/', add_round, name="round.add"),
    # path('round/edit/', None, name="round.edit"),
    # path('round/remove/', remove_round, name="round.remove"),
    # path('round/<slug:round>/', None, name="round.specific"),
    #
    # # Game Pages
    # path('game/', None, name="game"),
    # path('game/add/', add_game, name="game.add"),
    # path('game/edit/', None, name="game.edit"),
    # path('game/remove/', None, name="game.remove"),
    # path('game/<slug:game>/', None, name="game.specific"),
    #
    # # Tournament Pages
    # path('tournament/', all_tournaments, name="tournament"),
    # path('tournament/add/', add_tournament, name="tournament.add"),
    # path('tournament/edit/', None, name="tournament.edit"),
    # path('tournament/remove/', None, name="tournament.remove"),
    # path('tournament/<slug:tournament>/', tournament, name="tournament.specific"),
    #
    # # Bracket
    # path('bracket/', None, name="bracket"),
    # path('bracket/add/', add_bracket_round, name="bracket.add"),
    # path('bracket/edit/', None, name="bracket.edit"),
    # path('bracket/remove/', None, name="bracket.remove"),
    # path('bracket/<slug:bracket>/', None, name="bracket.specific"),
    #
    # # Team Pages
    # path('team/', None, name="team"),
    # path('team/add/', add_team, name="team.add"),
    # path('team/edit/', None, name="team.edit"),
    # path('team/remove/', None, name="team.remove"),
    # path('team/<slug:team>/', None, name="team.specific"),
    #
    # # Site functionality
    # path('logout/', gb_logout, name="logout"),
    # path('login/', gb_login, name="login"),
    # path('register/', gb_register, name="register"),

    path('test/', test, name='test'),
] + static(settings.STATIC_ROOT, document_root=settings.STATIC_ROOT)
