import discord
import os
from decouple import config
from collections import defaultdict
import coloredlogs, logging


logging.basicConfig(level=logging.INFO)
coloredlogs.install()

bot = discord.Bot(debug_guilds=[config('DEBUG_GUILD', cast=int)])
players = defaultdict(lambda: None) # a dict of the form {userId: gameId}
games = {} # a dict of the form {gameId: (deckId, turnCount, [list of players], {gameSpecificArgs})}
nextGameID = 0

# loading all the extensions
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(config('TOKEN'))