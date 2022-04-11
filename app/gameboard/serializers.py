from rest_framework import serializers

from gameboard.models import Player, Game, Group, PlayerRank, Round, BracketRound, Team, Bracket, Tournament


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['pk', 'name', 'description', 'game_picture']
        read_only_fields = ['pk']


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['pk', 'username', 'date_of_birth', 'profile_image', 'favorite_game', 'primary_group']
        read_only_fields = ['pk', 'username']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['pk', 'name', 'players', 'admins', 'group_picture']
        read_only_fields = ['pk']


class PlayerRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerRank
        fields = ['pk', 'player', 'rank', 'score']
        read_only_fields = ['pk']


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ['pk', 'game', 'date', 'players', 'group']
        read_only_fields = ['pk']


class BracketRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = BracketRound
        fields = ['pk', 'match', 'round']
        read_only_fields = ['pk']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['pk', 'name', 'color', 'players']
        read_only_fields = ['pk']


class BracketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bracket
        fields = ['pk', 'type', 'rounds', 'teams']
        read_only_fields = ['pk']


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['pk', 'name', 'bracket', 'group']
        read_only_fields = ['pk']
