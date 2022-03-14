# Game Board
Game board is an application for tracking games played with your friend groups, and viewing their results in interesting ways. 

# Running Game Board
In order to run this application, follow the following directions to run the game on your local machine. This assumes you have [docker](https://docs.docker.com/get-docker/) installed.

## First Time Setup
1. Clone the repository
    - `git clone https://github.com/KeeganW/game-board.git && cd game-board`
2. Run docker (note, you may need to run this twice after the database is made after initial run.)
   - `docker-compose up -d`
3. Create your database
    - `docker exec -it game-board-web-1 python manage.py makemigrations gameboard && docker exec -it game-board-web-1 python manage.py migrate --run-syncdb`

## Running the website
1. Run the web server.
    - `python manage.py runserver localhost:8080`
2. Open a browser to [localhost:8080](http://localhost:8080/).

## (Optional) Load Test Dataset
1. Just navigate to [the import page](http://localhost:8080/import).

For additional information, please see our [Wiki Page](https://github.com/KeeganW/game-board/wiki).