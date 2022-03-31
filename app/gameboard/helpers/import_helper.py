import csv
import os

from django.contrib.auth.models import User
from django.db.models import QuerySet

from gameboardapp.settings import STATIC_ROOT, PROJECT_ROOT, BASE_DIR, APP_ROOT, MEDIA_ROOT
from datetime import datetime
from django.db import IntegrityError
from gameboard.models import Game, Round, Player, Group, PlayerRank


class ImportScores:
    """
    Imports scores form a custom formatted csv (stored as a static file).
    """
    # The csv file to get data from
    # dataset_name = 'dataset2'
    dataset_name = 'dataset3'
    dataset = os.path.join(STATIC_ROOT, dataset_name + '.csv')

    version = int(dataset_name[-1])

    # Specific locations of columns within the csv
    date_loc = 0
    game_loc = 1
    coop = 2
    first_player_loc = 3

    # Storing the player information
    players = {}

    def __init__(self):
        """
        Wipes all past data (be careful to only use this in a testing environment!) and then adds data. Adding starts
        with players, then games, then individual games by the date they were played. Assumes the dataset contains all
        games played by a single group, which hasn't been created yet.
        """
        # Wipe the db
        self.wipe_db()

        if self.dataset_name[0:7] == 'dataset':
            # Add all players from dataset
            group = self.add_players()

            # Add all games from the dataset
            self.add_games()

            # Create the games played for this group
            self.add_game_played(group)
        else:
            self.import_special()

    def wipe_db(self):
        """
        WARNING: This function wipes all data in the database. Be careful with its use!

        :return: None
        """
        self.delete_helper(Player.objects.all())
        self.delete_helper(User.objects.all())
        self.delete_helper(Game.objects.all())
        self.delete_helper(Round.objects.all())
        self.delete_helper(PlayerRank.objects.all())
        self.delete_helper(Group.objects.all())

    @staticmethod
    def delete_helper(objects: QuerySet):
        for obj in objects:
            obj.delete()


    def import_special(self):
        all_data = []
        with open(self.dataset, newline='') as f:
            # Get the first line
            reader = csv.reader(f)
            for line in reader:
                all_data.append(line)

        export_location = os.path.join(STATIC_ROOT, 'backup.csv')
        players = []
        with open(export_location, mode='w') as f:
            f_write = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            headers = ['Date', 'Game', 'Coop']
            for line in all_data:
                headers.append(line[0])
                headers.append(line[0] + '_scores')
            players = headers[3:]
            f_write.writerow(headers)

        # calculate games and scores
        games = {}
        for line in all_data:
            player = line.pop(0)
            # remove real name
            line.pop(0)

            # Now in sets of 4, we want to continue to pop for game, place, score, date
            while len(line) > 0:
                date = line.pop()
                score = line.pop()
                rank = line.pop()
                game = line.pop()
                if game != '':
                    game_id = game + '|:|' + date
                    # Now add it to our games dictionary
                    try:
                        games[game_id].append([player, rank, score])
                    except KeyError:
                        games[game_id] = [[player, rank, score]]

        with open(export_location, mode='a+') as f:
            f_write = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for game_id, ranks in games.items():
                game, date = game_id.split('|:|')
                line = [''] * (len(players) + 1)  # +1 for the coop slot
                line.insert(0, game)
                line.insert(0, date)
                for [player, rank, score] in ranks:
                    line_index = players.index(player) + 3
                    line[line_index] = rank
                    line[line_index + 1] = score
                f_write.writerow(line)

    def add_players(self):
        """
        Adds all the players within the csv to the Player database table.

        Gets the first line of the csv. Loops over all the players in that line (marked by location marks). Adds those
        players as users, with a temporary password (password) and usernames/first names corresponding
        to the player name.

        :return: None
        """
        with open(self.dataset, newline='') as f:
            # Get the first line
            reader = csv.reader(f)
            people = next(reader)
            new_players = people[self.first_player_loc:]
            if self.version > 1:
                # Remove odd indexes (scores)
                new_players = [v for i, v in enumerate(new_players) if i % 2 == 0]
            group = Group(name="Sample Group")
            group.save()

            # Loop over those players
            for player in new_players:
                print(f"Adding player: {player}")
                # Set the user object
                username = player.replace(" ", "")
                u = User(first_name=player, last_name="", username=username)
                u.save()
                u.set_password("password")
                u.save()

                # Set the player object
                p = Player(user=u, date_of_birth=datetime.now(), primary_group=group)
                p.save()

                self.players[player] = p

                group.players.add(p)
                group.admins.add(p)
            return group

    def add_games(self):
        """
        Adds all the games within the csv for later relation with the Round object.

        Loops through all lines in the sheet, looking at a specific column and pulling all the unique names it finds
        in that column.

        :return: None
        """
        with open(self.dataset, newline='') as f:
            # Open the csv
            reader = csv.reader(f)
            for line in reader:
                # Get the game data
                game = line[self.game_loc]
                if len(game) > 0:
                    try:
                        # Add it if it is unique
                        g = Game(name=game)
                        g.save()
                    except IntegrityError:
                        pass

    def add_game_played(self, group):
        """
        Adds all games that were played which were recorded, as long as they are properly formatted.

        :return: None
        """
        with open(self.dataset, newline='') as f:
            # Open the csv, and read through every line (but the header)
            reader = csv.reader(f)
            people = next(reader)
            new_players = people[self.first_player_loc:]

            for line in reader:
                # Get the game (if it is not there, ignore this line)
                game = line[self.game_loc]
                if len(game) > 0:
                    # Set local variables
                    players = list()

                    # Get the date the game was played on
                    date = datetime.strptime(line[self.date_loc], "%m/%d/%y")

                    # Get the players placements (and their scores) that played in that round
                    player_stats = line[self.first_player_loc:]

                    # Loop through all the players who played
                    for player_index in range(len(player_stats)):
                        # We only want to process the names of the players
                        if player_index % 2 == 0:
                            # Get their names, and the wins they had
                            player_stat = player_stats[player_index]

                            # Check whether this player played. "" = didn't, anything else = did
                            if player_stat != "":
                                player_name = new_players[player_index]
                                player = self.players[player_name]

                                # Create a rank object, and get it setup to add
                                try:
                                    player_placement = None if player_stat == "0" else int(player_stat)
                                except ValueError:  # TODO(keegan): Is this correct for int conversion?
                                    player_placement = None

                                # TODO add in self.version check for scores
                                try:
                                    player_score = int(player_stats[player_index + 1])
                                except ValueError:  # TODO(keegan): Is this correct for int conversion?
                                    player_score = None
                                rank = PlayerRank(player=player, rank=player_placement, score=player_score)
                                players.append(rank)

                    self.enter_game_played(players, game, date, group)

    @staticmethod
    def enter_game_played(players, game, date, group):
        """
        Actually adds the game played to the database, linking to Player objects and Game objects.

        :param players: The names of the players
        :param game: The game that was played (string)
        :param date: A date object to use for when the game was played
        :param group: Which group this game was played with
        :return: None
        """
        try:
            game_played = Round()
            game_played.game = Game.objects.get(name__exact=game)
            game_played.date = date
            game_played.group = group
            game_played.save()

            for player in players:
                player.save()
                game_played.players.add(player)
        except:
            print("Error entering game", game)
            pass


class ExportScores:
    """
    This class is used to export the database into a re-importable format
    """
    export_location = os.path.join(STATIC_ROOT, 'backup.csv')
    players = []

    def __init__(self):
        group = Group.objects.all().first()
        # Put the header at the top of the file
        self.add_header(group)

        # Add all thr game data
        self.add_all_rounds(group)

        pass

    def add_header(self, group):
        with open(self.export_location, mode='w') as f:
            f_write = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            line = ['Date', 'Game', 'Coop']
            for player in group.players.all():
                print(player)
                line.append(player.user.username)
                self.players.append(player.user.username)
            f_write.writerow(line)

    def add_all_rounds(self, group):
        with open(self.export_location, mode='a+') as f:
            f_write = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for round in Round.objects.filter(group_id=group.id).order_by('-date'):
                # Add first part of line
                line = [round.date.strftime("%m/%d/%y"), round.game.name, '']

                # Add player information
                for player in self.players:
                    line.append("")

                for player in round.players.all():
                    line[self.players.index(player.user.username) + 3] = 0

                for player in round.winners.all():
                    line[self.players.index(player.user.username) + 3] = 1

                f_write.writerow(line)
