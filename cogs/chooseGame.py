import discord
from discord.ext import commands
import logging


class chooseGame(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Choose Game module ready!")

def setup(bot):
    bot.add_cog(chooseGame(bot))