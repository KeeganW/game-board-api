from enum import Enum

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.authtoken.models import Token

from gameboardapp.settings import AUTH_USER_MODEL


class Game(models.Model):
    """
    The game class is all of the information about individual games which are played by users. Games will be non-group
    specific. So if one group adds a game, it will then be available for all groups in the future.
    """
    name = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=400)
    game_picture = models.ImageField(upload_to='', blank=True)

    def __str__(self):
        return str(self.name)


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Player(AbstractUser):
    """
    The player class stores information about individual players.
    """
    date_of_birth = models.DateField(default=timezone.now().strftime("%Y-%m-%d"))
    profile_image = models.ImageField(upload_to='', blank=True)
    favorite_game = models.ForeignKey(Game, blank=True, null=True, on_delete=models.CASCADE)
    # Group is not an object, because we need to define one of these before the other will work
    primary_group = models.ForeignKey("Group", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.username)


class Group(models.Model):
    """
    A player group is a group which users/players can create and invite other players too. This allows users to keep all
    of the friends the play games with in separate groups, and keep track of scores with those other players.
    """
    name = models.CharField(max_length=150)
    players = models.ManyToManyField(AUTH_USER_MODEL, related_name='players')
    admins = models.ManyToManyField(AUTH_USER_MODEL, related_name='admins')
    group_picture = models.ImageField(upload_to='', blank=True)

    def __str__(self):
        return str(self.name)


def validate_rank_more_than_zero(value: int):
    """
    Ensure value is more than zero for ranking players.
    :param value: A positive integer > 0 or None
    :return: value
    """
    if value > 0 or value is None:
        return value
    else:
        raise ValidationError("This field must be > 0")


class PlayerRank(models.Model):
    """
    When a player is ranked in a game, their placement will be quantified by this class.

    A null rank means that the player either did not finish, or the game only supports winners and the others are not
    ranked.
    """
    player = models.ForeignKey(AUTH_USER_MODEL, related_name='game_player', on_delete=models.CASCADE)
    rank = models.IntegerField(null=True, validators=[validate_rank_more_than_zero])
    score = models.IntegerField(null=True)

    def __str__(self):
        if self.score:
            return str("{}={}({})".format(self.player, self.rank, self.score))
        return str("{}={}".format(self.player, self.rank if self.rank is not None else 'DNF'))


class Round(models.Model):
    """
    When a group plays a game, they will create a new instance of this class. This stores all the relevant
    information about who played the game, who won, and the game played.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now().strftime("%Y-%m-%d"))
    # TODO rename this to player_ranks?
    players = models.ManyToManyField(PlayerRank, related_name='game_players')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def winners(self):
        player_ids = self.players.filter(rank__exact=1).values_list('player_id', flat=True)
        return Player.objects.filter(id__in=list(player_ids))

    def placed_players(self):
        player_ids = self.players.filter(rank__gt=0).values_list('player_id', flat=True)
        return Player.objects.filter(id__in=list(player_ids))

    def all_players(self):
        player_ids = self.players.values_list('player_id', flat=True)
        return Player.objects.filter(id__in=list(player_ids))

    def __str__(self):
        return str("{}, {}: {}".format(self.game, self.date, self.players.all()))


class BracketRound(models.Model):
# class BracketMatch(models.Model):
    """
    When a bracket is played, its individual matches can be tracked by their corresponding match number.
    These matches correspond to a round, which tracks the actual outcome.
    """
    match = models.IntegerField(null=False)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    def __str__(self):
        return str("{}: {}".format(self.match, self.round))


class Team(models.Model):
    """
    A team is composed of a set of players who are playing for that team. Each team is identified by their name.
    Teams can be customized to have a hex color.
    """
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=6)
    players = models.ManyToManyField(AUTH_USER_MODEL, related_name='game_players')

    def __str__(self):
        return str("{}: {}".format(self.name, self.players.all()))


class BracketType(Enum):
    SINGLE_ELIMINATION = 'Single Elimination'
    DOUBLE_ELIMINATION = 'Double Elimination'
    ROUND_ROBIN = 'Round Robin'


class Bracket(models.Model):
    """
    A bracket is formed using a given bracket type. These brackets are composed of teams, and the rounds of games
    they play against each other.
    """
    type = models.CharField(BracketType, max_length=50)
    rounds = models.ManyToManyField(BracketRound, related_name='rounds')
    # matches = models.ManyToManyField(BracketMatch, related_name='rounds')
    teams = models.ManyToManyField(Team, related_name='teams')

    def __str__(self):
        return str("{}: {}".format(self.type, self.teams.all()))


class Tournament(models.Model):
    """
    Tournaments are where a group of players play against each other, trying to have their team win the overall
    tournament.
    """
    name = models.CharField(max_length=50)
    bracket = models.ForeignKey(Bracket, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return str("{}".format(self.name))


# TODO use db for statistics
class StatisticType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=50)


class StatisticInfo(models.Model):
    date = models.DateField()
    type = models.ForeignKey(StatisticType, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class Statistic(models.Model):
    player = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.DecimalField(decimal_places=2, max_digits=16)
    info = models.ForeignKey(StatisticInfo, on_delete=models.CASCADE)
