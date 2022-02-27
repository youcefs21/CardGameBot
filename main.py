import discord
import os
from decouple import config

bot = discord.Bot(debug_guilds=[config('DEBUG_GUILD', cast=int)])

# loading all the extensions
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(config('TOKEN'))