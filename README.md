# Game Board
Game board is an application for tracking games played with your friend groups, and viewing their results in interesting ways. 

# Running Game Board
In order to run this application, follow the following directions to run the game on your local machine. This assumes you have [docker](https://docs.docker.com/get-docker/) installed.

Run docker (note, you may need to run this twice after the database is made after initial run.)
- `docker-compose up -d`

## First Time Setup
Note, you will need to create the django migrations for the system to work
- `docker exec -it game-board-web-1 python manage.py makemigrations gameboard && docker exec -it game-board-web-1 python manage.py migrate --run-syncdb`

## Running the website
1. Run the web server.
    - `python manage.py runserver localhost:8080`
2. Open a browser to [localhost:8080](http://localhost:8080/).

## (Optional) Load Test Dataset
1. Just navigate to [the import page](http://localhost:8080/import).

For additional information, please see our [Wiki Page](https://github.com/KeeganW/game-board/wiki).

# Possible New Features
- Elo system
  - Based off of games won and lost against peers
  - Can we factor games elo/points by top placements similar to TFT?
- Cleaner score calculations
- Stats based off of placements not just first
- Start player (it's own github page?)
- Tournament page
  - Set teams or individual player brackets
  - Keeps track of scores of teams (allow entries for placements)

# How would DPG use this?
- Players turn round cards in after playing a game in the shop
- Round cards are entered into system at the end of the day (or by players?)
  - Need an admin only can enter rounds feature
  - Players who are not members would need to be ignored (best), or added as new players
  - Players get sent emails when rounds are entered with links to see stats
- Players can login and view their scores
  - Need to have a way to setup and account that they can login and use 
  - Maybe players just need to register with their password on site
  - Needs feature for password reset
  - Does django do salting and encrypting of passwords?
  - Maybe a hookup to a google account (oauth2 blech)?
  - Players can get trophies (most plays in a month, etc)
- Games have leaderboards for best players (based on win percentage or high placements?)
- Virtual score card
  - A score card (or a set of them) in the right format, but just for one set of people
- Scores for games


# AUTH config
`openssl genrsa -out oidc.key 4096` from app directory

