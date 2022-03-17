import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
import games.PlayPresident as PlayPresident
from typing import Set


class GameService(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.users_in_game: Set[int] = set()

    play = SlashCommandGroup("play", "play a card game!")

    @play.command(description="a game of president")
    async def president(self, ctx: discord.ApplicationContext):

        user_id = ctx.user.id
        if user_id in self.users_in_game:
            await ctx.respond("You're already in a game", ephemeral=True)
            return

        self.users_in_game.add(user_id)

        # lobby

        # role choice and last chance to quit game

        # pre-game card trade and start of rounds
        await PlayPresident.president(ctx, self.bot)

        # game summary


def setup(bot):
    bot.add_cog(GameService(bot))
