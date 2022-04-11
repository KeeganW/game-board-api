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
router.register(r'bracket_round', viewsets.BracketRoundViewSet)
router.register(r'team', viewsets.TeamViewSet)
router.register(r'bracket', viewsets.BracketViewSet)
router.register(r'tournament', viewsets.TournamentViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Import/Export
    path('import/', import_scores, name="import"),
    path('export/', export_scores, name="export"),

    # Signing in and registering urls
    path('register/', views.SignUp.as_view()),
    path('', include('gameboard.urls_authentication')),
]
