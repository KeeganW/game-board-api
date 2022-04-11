from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework import generics, permissions, serializers
from gameboard.models import Player


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


urlpatterns = [
    path("register/", SignUp.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
