import os

import coloredlogs
import discord
import logging
from decouple import config


coloredlogs.install(level=logging.INFO)


def main():
    bot = discord.Bot(debug_guilds=config(
        'DEBUG_GUILDS',
        cast=lambda v: [int(s.strip()) for s in v.split(',')]
    ))

    # loading all the extensions
    dir_name = os.path.dirname(__file__)
    for filename in os.listdir(os.path.join(dir_name, 'cogs')):
        if filename.endswith('.py'):
            bot.load_extension(f'src.cogs.{filename[:-3]}')

    bot.run(config('TOKEN'))

    return bot


if __name__ == '__main__':
    main()

