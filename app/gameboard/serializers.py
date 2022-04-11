from django.contrib.auth.models import User
from rest_framework import serializers

from gameboard.models import Player, Game, Group, PlayerRank, Round, BracketRound, Team, Bracket, Tournament


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['pk', 'name', 'description', 'game_picture']


class PlayerSerializer(serializers.ModelSerializer):
    favorite_game = GameSerializer()
    user = UserSerializer()
    class Meta:
        model = Player
        fields = ['user', 'date_of_birth', 'profile_image', 'favorite_game', 'primary_group']


class GroupSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)
    admins = PlayerSerializer(many=True)
    class Meta:
        model = Group
        fields = ['name', 'players', 'admins', 'group_picture']


class PlayerRankSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    class Meta:
        model = PlayerRank
        fields = ['player', 'rank', 'score']


class RoundSerializer(serializers.ModelSerializer):
    game = GameSerializer()
    players = PlayerRankSerializer(many=True)
    class Meta:
        model = Round
        fields = ['game', 'date', 'players', 'group']


class BracketRoundSerializer(serializers.ModelSerializer):
    round = RoundSerializer()
    class Meta:
        model = BracketRound
        fields = ['match', 'round']


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)
    class Meta:
        model = Team
        fields = ['name', 'color', 'players']


class BracketSerializer(serializers.ModelSerializer):
    rounds = RoundSerializer(many=True)
    teams = TeamSerializer(many=True)
    class Meta:
        model = Bracket
        fields = ['type', 'rounds', 'teams']


class TournamentSerializer(serializers.ModelSerializer):
    bracket = BracketSerializer()
    group = GroupSerializer()
    class Meta:
        model = Tournament
        fields = ['name', 'bracket', 'group']
