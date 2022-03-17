import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
import games.PlayPresident as PlayPresident
from typing import Set, List


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
        lobby = Lobby(game_service=self, game_name="President", max_count=2, min_count=6)
        lobby.openLobby(user_id, ctx)

        # role choice and last chance to quit game

        # pre-game card trade and start of rounds
        await PlayPresident.president(ctx, self.bot)

        # game summary


class Lobby:
    def __init__(self, game_service, game_name: str, max_count, min_count):
        self.game_service = game_service
        self.game_name = game_name
        self.max_count = max_count
        self.min_count = min_count

    def openLobby(self, host_id: int, ctx: discord.ApplicationContext):
        player_ids = [host_id]

        embed = self.createEmbed(player_ids)

        lobby_msg = await ctx.send(embed=embed)

    def createEmbed(self, player_ids: List[int]) -> discord.Embed:
        """
        :param player_ids: a list of user ids of the players participating in the game
        :return: lobby embed
        """

        host = await self.game_service.bot.fetch_user(player_ids[0])
        embed = discord.Embed(title=f"A game of {self.game_name}", description=f"{host}")
        embed.add_field(name="Player 1", value=host)

        for i in range(1, len(player_ids)):
            player = await self.game_service.bot.fetch_user(player_ids[i])
            embed.add_field(name=f"Player {i+1}", value=player)

        return embed


def setup(bot):
    bot.add_cog(GameService(bot))
