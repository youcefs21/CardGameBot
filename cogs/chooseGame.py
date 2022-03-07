import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, slash_command


class chooseGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    play = SlashCommandGroup("play", "play a card game!")


    @play.command(description="a game of president")
    async def president(self, ctx):
        president = self.bot.get_cog('president')

        await president.president(ctx)



def setup(bot):
    bot.add_cog(chooseGame(bot))