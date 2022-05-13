import os

import coloredlogs
import discord
import logging
from decouple import config


def main(proxy=None):
    bot = discord.Bot(
        debug_guilds=config(
            'DEBUG_GUILDS',
            cast=lambda v: [int(s.strip()) for s in v.split(',')]
        ),
        proxy=proxy
    )

    # loading all the extensions
    dir_name = os.path.dirname(__file__)
    for filename in os.listdir(os.path.join(dir_name, 'cogs')):
        if filename.endswith('.py'):
            bot.load_extension(f'src.cogs.{filename[:-3]}')

    return bot


if __name__ == '__main__':
    coloredlogs.install(level=logging.INFO)
    bt = main()
    bt.run(config('TOKEN'))


