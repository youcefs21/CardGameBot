from discord.ext import commands
from discord.commands import SlashCommandGroup
import games.PlayPresident as PlayPresident


class GameService(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    play = SlashCommandGroup("play", "play a card game!")

    @play.command(description="a game of president")
    async def president(self, ctx):
        await PlayPresident.president(ctx, self.bot)


def setup(bot):
    bot.add_cog(GameService(bot))
