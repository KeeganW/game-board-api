from django.urls import path, include, re_path
from django.contrib import admin
from rest_framework.authtoken import views

from gameboard.models import Group
from gameboard.views import ObtainExpiringAuthToken

admin.autodiscover()

from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import generics, permissions, serializers

# first we define the serializers
class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        print("Writing user")
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        user.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name", )

class SignUpSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        print("Writing user2")
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            # TODO: Other values?
        )
        user.save()  # TODO: Is this needed?
        return user

    class Meta:
        model = User
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

# Create the API views
class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [IsAuthenticatedOrCreate]

# Setup the URLs and include login URLs for the browsable API.
urlpatterns = [
    path("register/", SignUp.as_view()),
    # path('auth/', views.obtain_auth_token),
    path('auth/', ObtainExpiringAuthToken.as_view()),
    path("admin/", admin.site.urls),  # TODO: can we remove this? Replace by load from script?
]
