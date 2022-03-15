import os
from collections import defaultdict
from typing import TypedDict, List, Dict, Tuple

import coloredlogs
import discord
import logging
from decouple import config

from cardsAPI import Deck

coloredlogs.install(level=logging.INFO)

bot = discord.Bot(debug_guilds=config(
    'DEBUG_GUILDS',
    cast=lambda v: [int(s.strip()) for s in v.split(',')]
))
# a dict of the form {userId: deckId}
users: Dict[int, str] = defaultdict(lambda: "")


class Game(TypedDict):
    gameType: str
    deck: Deck
    turnCount: int
    players: List[int]
    lastTurn: Tuple[int, int]  # value, count
    thisTurn: Tuple[int, int]  # value, count
    passCounter: int
    winners: List[int]


games: Dict[str, Game] = {}

# loading all the extensions
dir_name = os.path.dirname(__file__)
for filename in os.listdir(os.path.join(dir_name, './cogs')):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(config('TOKEN'))
