from django.contrib.auth.models import User
from django.test import TestCase, LiveServerTestCase, Client
from gameboard.models import Player, Round, Game, Group, PlayerRank, Team, Bracket, Tournament, BracketRound, \
    BracketType
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class TestGameBoardModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Create 3 users (James, John, and Jane), 3 games (Catan, Bananagram, and Uno), and a group (Testing Group)

        Create 3 plays
        Play catan, P1 in first, P2 in second
        Play Bananagram, same result plus P3 didn't finish
        Play Uno (single player) who didn't finish
        :return:
        """
        u1 = User(first_name="James", last_name="Doe", email="gameboard@gmail.com", username="james", password="password")
        u1.save()
        u2 = User(first_name="John", last_name="Doe", email="gameboard@gmail.com", username="john", password="password")
        u2.save()
        u3 = User(first_name="Jane", last_name="Doe", email="gameboard@gmail.com", username="jane", password="password")
        u3.save()
        dob = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date()  # Don't break due to Y2K
        player1 = Player(user=u1, date_of_birth=dob)
        player1.save()
        player2 = Player(user=u2, date_of_birth=dob)
        player2.save()
        player3 = Player(user=u3, date_of_birth=dob)
        player3.save()

        game1 = Game(name="Catan", description="A first time board game players game!")
        game1.save()
        game2 = Game(name="Bananagram", description="Spell words!")
        game2.save()
        game3 = Game(name="Uno", description="Reverse!")
        game3.save()

        group = Group(name="TestingGroup")
        group.save()
        group.players.add(player1)
        group.players.add(player2)
        group.admins.add(player3)

        game_date = datetime.datetime.strptime("2019-12-01", "%Y-%m-%d").date()
        # Play catan, P1 in first, P2 in second
        played1 = Round(game=game1, date=game_date, group=group)
        played1.save()
        rank1 = PlayerRank(player=player1, rank=1)
        rank1.save()
        rank2 = PlayerRank(player=player2, rank=2)
        rank2.save()
        played1.players.add(rank1)
        played1.players.add(rank2)

        # Play Bananagram, same result plus P3 didn't finish
        played2 = Round(game=game2, date=game_date, group=group)
        played2.save()
        rank3 = PlayerRank(player=player3)
        rank3.save()
        played2.players.add(rank1)
        played2.players.add(rank2)
        played2.players.add(rank3)

        # Play Uno (single player) who didn't finish
        played3 = Round(game=game3, date=game_date, group=group)
        played3.save()
        played3.players.add(rank3)

    def test_player(self):
        """
        Test the player object works by getting James, and testing various information about them.
        :return: None
        """
        player = Player.objects.get(user__username="james")
        dob1 = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date()
        dob2 = datetime.datetime.strptime("2000-01-02", "%Y-%m-%d").date()

        self.assertEquals(player.user.first_name, "James")
        self.assertEquals(player.user.password, "password")
        self.assertNotEqual(player.user.last_name, "Bond")
        self.assertNotEqual(player.user.email, "email")
        self.assertEquals(player.date_of_birth, dob1)
        self.assertNotEqual(player.date_of_birth, dob2)

    def test_game(self):
        """
        Test the game object works by getting various games and testing them.
        :return: None
        """
        game1 = Game.objects.get(name="Uno")
        game2 = Game.objects.get(name="Bananagram")
        game3 = Game.objects.get(description="Reverse!")

        self.assertNotEqual(game1, game2)
        self.assertEqual(game1, game3)
        self.assertEqual(game1.description, "Reverse!")

    def test_playergroup(self):
        """
        Test the group object works by getting group and players and testing them.
        :return: None
        """
        group = Group.objects.get(name="TestingGroup")
        player1 = Player.objects.get(user__username="james")
        player2 = Player.objects.get(user__username="john")
        player3 = Player.objects.get(user__username="jane")
        player4 = group.admins.first()

        self.assertEquals(player3, player4)
        self.assertIn(player1, group.players.all())
        self.assertIn(player2, group.players.all())
        self.assertNotIn(player1, group.admins.all())
        self.assertNotIn(player3, group.players.all())

    def test_game_played(self):
        """
        Test the round object works by getting group and players and testing them.
        :return: None
        """
        player1 = Player.objects.get(user__username="james")
        player2 = Player.objects.get(user__username="john")
        player3 = Player.objects.get(user__username="jane")
        played1 = Round.objects.filter(players__player__user__username__exact=player1.user.username)
        played2 = Round.objects.filter(players__player__user__username__exact=player2.user.username)
        played3 = Round.objects.filter(players__player__user__username__exact=player3.user.username)

        self.assertEqual(len(played1), 2)
        self.assertEqual(len(played2), 2)
        self.assertEqual(len(played3), 2)

        game_played1 = Round.objects.get(game__name__exact="Catan")
        game_played2 = Round.objects.get(game__name__exact="Bananagram")
        game_played3 = Round.objects.get(game__name__exact="Uno")

        winners1 = game_played1.winners()
        placed_players1 = game_played1.placed_players()
        all_players1 = game_played1.all_players()
        self.assertEquals(len(winners1), 1)
        self.assertEquals(len(placed_players1), 2)
        self.assertEquals(len(all_players1), 2)
        self.assertIn(player1, winners1)
        self.assertNotIn(player2, winners1)
        self.assertNotIn(player3, winners1)
        self.assertIn(player1, placed_players1)
        self.assertIn(player2, placed_players1)
        self.assertNotIn(player3, placed_players1)
        self.assertIn(player1, all_players1)
        self.assertIn(player2, all_players1)
        self.assertNotIn(player3, all_players1)

        winners2 = game_played2.winners()
        placed_players2 = game_played2.placed_players()
        all_players2 = game_played2.all_players()
        self.assertEquals(len(winners2), 1)
        self.assertEquals(len(placed_players2), 2)
        self.assertEquals(len(all_players2), 3)
        self.assertIn(player1, winners2)
        self.assertNotIn(player2, winners2)
        self.assertNotIn(player3, winners2)
        self.assertIn(player1, placed_players2)
        self.assertIn(player2, placed_players2)
        self.assertNotIn(player3, placed_players2)
        self.assertIn(player1, all_players2)
        self.assertIn(player2, all_players2)
        self.assertIn(player3, all_players2)

        winners3 = game_played3.winners()
        placed_players3 = game_played3.placed_players()
        all_players3 = game_played3.all_players()
        self.assertEquals(len(winners3), 0)
        self.assertEquals(len(placed_players3), 0)
        self.assertEquals(len(all_players3), 1)
        self.assertNotIn(player1, winners3)
        self.assertNotIn(player2, winners3)
        self.assertNotIn(player3, winners3)
        self.assertNotIn(player1, placed_players3)
        self.assertNotIn(player2, placed_players3)
        self.assertNotIn(player3, placed_players3)
        self.assertNotIn(player1, all_players3)
        self.assertNotIn(player2, all_players3)
        self.assertIn(player3, all_players3)

    def test_tournament(self):
        """
        Test that a tournament works as expected
        :return: None
        """
        player1 = Player.objects.get(user__username="james")
        player2 = Player.objects.get(user__username="john")
        player3 = Player.objects.get(user__username="jane")
        game1 = Game.objects.get(name="Uno")
        game_date = datetime.datetime.strptime("2019-12-01", "%Y-%m-%d").date()
        group = Group.objects.get(name="TestingGroup")

        # Create two teams, one from player1, one from player2
        t1 = Team(name="Player 1's Team", color="FFFFFF")
        t1.save()
        t1.players.add(player1)

        t2 = Team(name="Player 2's Team", color="000000")
        t2.save()
        t2.players.add(player2)

        # Create a new bracket, and add the two teams
        b1 = Bracket(type=BracketType.ROUND_ROBIN)
        b1.save()
        b1.teams.add(t1)
        b1.teams.add(t2)

        # Create a new tournament
        tour1 = Tournament(name="Test Tournament", bracket=b1, group=group)
        tour1.save()

        # Add a single match between teams
        played1 = Round(game=game1, date=game_date, group=group)
        played1.save()
        rank1 = PlayerRank(player=player1, rank=1)
        rank1.save()
        rank2 = PlayerRank(player=player2, rank=2)
        rank2.save()
        played1.players.add(rank1)
        played1.players.add(rank2)
        # Make it a bracket round
        br1 = BracketRound(match=1, round=played1)
        br1.save()
        # Add it to bracket
        b1.rounds.add(br1)

        # TODO(keegan): write actual tests

# class TestMenuServeFunctions(StaticLiveServerTestCase):
#     """
#
#     """
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.selenium = WebDriver()
#         cls.selenium.implicitly_wait(10)
#         cls.selenium.get('%s%s' % (cls.live_server_url, '/import'))
#         try:
#             element = WebDriverWait(cls.selenium, 20).until(
#                 EC.presence_of_element_located((By.ID, "register-btn"))
#             )
#         finally:
#             pass
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super().tearDownClass()
#
#     def test_all(self):
#         # Test the index page
#         self.selenium.get('%s%s' % (self.live_server_url, '/'))
#         try:
#             element = WebDriverWait(self.selenium, 2).until(
#                 EC.presence_of_element_located((By.ID, "register-btn"))
#             )
#         finally:
#             pass
#         self.assertTrue(self.selenium.find_element_by_id('register-btn').is_displayed())
#
#         # register new user
#         self.selenium.get('%s%s' % (self.live_server_url, '/register'))
#         self.assertTrue(self.selenium.find_element_by_id('register-submit').is_displayed())
#         username_input = self.selenium.find_element_by_name("register-username")
#         username_input.send_keys('tester')
#         first_input = self.selenium.find_element_by_name("register-first_name")
#         first_input.send_keys('Test')
#         last_input = self.selenium.find_element_by_name("register-last_name")
#         last_input.send_keys('User')
#         password_input = self.selenium.find_element_by_name("register-password")
#         password_input.send_keys('WebAppsIsTheBestCourse')
#         confirm_password_input = self.selenium.find_element_by_name("register-password_confirm")
#         confirm_password_input.send_keys('WebAppsIsTheBestCourse')
#         self.selenium.find_element_by_id('register-submit').click()
#         self.assertTrue(self.selenium.find_element_by_id('logout-btn').is_displayed())
#
#         # logout
#         self.selenium.get('%s%s' % (self.live_server_url, '/logout'))
#
#         # Login to user
#         self.selenium.get('%s%s' % (self.live_server_url, '/login'))
#         username_input = self.selenium.find_element_by_name("login-username")
#         username_input.send_keys('Keegan')
#         password_input = self.selenium.find_element_by_name("login-password")
#         password_input.send_keys('WebAppsIsTheBestCourse')
#         self.selenium.find_element_by_id('login-submit').click()
#         self.assertTrue(self.selenium.find_element_by_id('logout-btn').is_displayed())
#
#         # Try to edit name
#         self.selenium.find_element_by_id('edit-profile-btn').click()
#         self.assertTrue(self.selenium.find_element_by_id('id_last_name').is_displayed())
#         last_input = self.selenium.find_element_by_id('id_last_name')
#         last_input.send_keys('Williams')
#         self.selenium.find_element_by_id('edit-submit').click()
#         self.assertEqual(self.selenium.find_element_by_id('user-full-name').text, 'KEEGAN WILLIAMS')
#
#         # Try to add game data
#         self.selenium.get('%s%s' % (self.live_server_url, '/group'))
#         self.assertEqual(self.selenium.find_element_by_id('group-name').text, 'TAS and Friends')
#         self.selenium.find_element_by_id('add-round-btn').click()
#         game_input = self.selenium.find_element_by_name("game")
#         game_input.send_keys('Carcassone')
#         player_input = self.selenium.find_element_by_name("player")
#         player_input.send_keys('Keegan')
#         player_input.send_keys(Keys.RETURN)
#         player_input.send_keys(Keys.RETURN)
#         self.selenium.find_element_by_id('li-1').click()
#         self.selenium.find_element_by_name('submit').click()
#         self.selenium.get('%s%s' % (self.live_server_url, '/group'))




