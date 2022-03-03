import discord
import os
from decouple import config
from collections import defaultdict
import coloredlogs, logging
from typing import TypedDict, List, Dict
from cardsAPI import Deck


coloredlogs.install(level=logging.INFO)

bot = discord.Bot(debug_guilds=[config('DEBUG_GUILD', cast=int)])
# a dict of the form {userId: deckId}
players: Dict[int, str] = defaultdict(lambda: None) 

class Game(TypedDict):
    gameType: str
    deck: Deck
    turnCount: int
    players: List[int]

games: Dict[str, Game] = {}


# loading all the extensions
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(config('TOKEN'))