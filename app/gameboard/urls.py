from django.urls import path, include
from rest_framework import routers

from gameboard import views, viewsets
from gameboard.views import import_scores, export_scores


router = routers.DefaultRouter()
router.register(r'player', viewsets.PlayerViewSet)
router.register(r'game', viewsets.GameViewSet)
router.register(r'group', viewsets.GroupViewSet)
router.register(r'player_rank', viewsets.PlayerRankViewSet)
router.register(r'round', viewsets.RoundViewSet)
router.register(r'bracket_match', viewsets.BracketMatchViewSet)
router.register(r'team', viewsets.TeamViewSet)
router.register(r'bracket', viewsets.BracketViewSet)
router.register(r'tournament', viewsets.TournamentViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Import/Export
    path('import/', import_scores, name="import"),
    path('export/', export_scores, name="export"),

    # Info gathering for
    path('player_info/', views.player_info, name='Player Info'),
    path('add_round_info/', views.add_round_info, name='Add Round Info'),
    path('tournament_info/<slug:pk>/', views.tournament_info, name='Tournament Info'),
    path('tournament_stats/<slug:pk>/', views.tournament_stats, name='Tournament Stats'),

    # Post routes
    path('add_round/', views.add_round, name='Add Round'),
    path('add_match/', views.add_match, name='Add Round'),

    # Signing in and registering urls
    path('set-csrf/', views.set_csrf_token, name='Set-CSRF'),
    path('login/', views.login_view, name='Login'),
    path('logout/', views.logout_view, name='Logout'),
]
