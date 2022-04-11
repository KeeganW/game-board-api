from django.urls import path, include
from rest_framework import generics, permissions, serializers, routers

from gameboard import views, viewsets
from gameboard.models import Player
from gameboard.views import import_scores, export_scores


class SignUpSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = Player.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            # TODO: Other values?
        )
        user.save()  # TODO: Is this needed?
        return user

    class Meta:
        model = Player
        fields = ['username', 'password']
        write_only_fields = ['password']
        extra_kwargs = {
            'username': {'required': True},
            'password': {'required': True},
        }


class IsAuthenticatedOrCreate(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return super(IsAuthenticatedOrCreate, self).has_permission(request, view)


class SignUp(generics.CreateAPIView):
    queryset = Player.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [IsAuthenticatedOrCreate]


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
    path("register/", SignUp.as_view()),
    path("token/", include('gameboard.urls_authentication')),
]
