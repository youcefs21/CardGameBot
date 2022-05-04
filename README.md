 # Card Game Bot


 A discord bot that allows you to play a variety of card games with friends


<!--
## Features

 - Interactive button based gameplay
 - created with mobile in mind

### Available Games
 - President (Work in progress)

-->

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

0. if you haven't already, complete the [installation](#installation) section
1. install [geckodriver](https://github.com/mozilla/geckodriver/releases) (needed for selenium)
2. place the login information of 6 discord accounts you want to use for testing in the `.env` file from earlier.
3. visit the channel you want to use for testing in the [web version of discord](https://discord.com/login) and place the url in the `TEST_CHANNEL` variable in the `.env` file.
4. Make sure all the accounts have access to the channel you want to test in.
5. run `pytest test` in the terminal
