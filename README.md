
WORK IN PROGRESS

# Card Game Bot


 A discord bot that allows you to play a variety of card games with friends


<!--
## Features

 - Interactive button based gameplay
 - created with mobile in mind

### Available Games
 - President (Work in progress)

-->

## Screen Shots

#### Game lobby:

<img src="https://user-images.githubusercontent.com/34604972/166860070-5aae2327-26ef-4ce2-ac5f-302740dd5822.png" width="500" alt="Game lobby for a game of president">


## Installation

I'll have a public bot at some point, but for now you'll need to host the bot yourself.

1. Clone the repo
2. create a virtual environment with `python3 -m venv .venv`
3. activate the virtual environment with `source .venv/bin/activate` for linux (check out the [venv](https://docs.python.org/3/library/venv.html) docs for more info)
4. Install the dependencies with `pip install -r requirements.txt`
5. create a functioning environmental variable file using `cp .env_template .env`
6. edit the environmental variable file to include your bot token and the id of the servers you want the bot to work in
7. Run the bot with `python -m src.main.py`

## Testing

run `pytest test` in the terminal

