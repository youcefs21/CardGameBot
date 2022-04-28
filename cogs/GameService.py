import asyncio

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
        await lobby.openLobby(user_id, ctx)

        # role choice and last chance to quit game

        # pre-game card trade and start of rounds
        await PlayPresident.president(ctx, self.bot)

        # game summary


class LobbyButtons(discord.ui.View):
    def __init__(self, host_id: int, users_in_game: Set[int]):
        self.done = False
        self.update = False
        self.users_in_game = users_in_game
        self.player_ids = [host_id]
        super().__init__()

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
    async def join_button(self, _, interaction: discord.Interaction):
        player_id = interaction.user.id
        if player_id in self.users_in_game:
            await interaction.response.send_message("you're already in a game", ephemeral=True)
            return

        self.users_in_game.add(player_id)
        self.player_ids.append(player_id)
        self.update = True

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
    async def leave_button(self, _, interaction: discord.Interaction):
        player_id = interaction.user.id
        if player_id not in self.player_ids:
            await interaction.response.send_message("you're not in this game", ephemeral=True)
            return

        self.users_in_game.discard(player_id)
        self.player_ids.remove(player_id)
        self.update = True

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_button(self, _, interaction: discord.Interaction):
        player_id = interaction.user.id
        if player_id != self.player_ids[0]:
            await interaction.response.send_message("you're not the game host", ephemeral=True)
            return

        self.done = True
        self.stop()


class Lobby:
    def __init__(self, game_service: GameService, game_name: str, max_count, min_count):
        self.game_service = game_service
        self.game_name = game_name
        self.max_count = max_count
        self.min_count = min_count

    async def openLobby(self, host_id: int, ctx: discord.ApplicationContext):

        lobby_view = LobbyButtons(host_id, self.game_service.users_in_game)
        embed = await self.createEmbed(lobby_view.player_ids)
        lobby_msg = await ctx.send_response(embed=embed, view=lobby_view)

        while not lobby_view.done:
            await asyncio.sleep(0.5)

            # check that there is at least 1 player in the lobby
            if len(lobby_view.player_ids) == 0:
                lobby_view.stop()
                await lobby_msg.delete_original_message()
                await ctx.send("Game cancelled, everyone left", delete_after=2)
                return []

            # check if the player list has been updated, then update embed
            if lobby_view.update:
                embed = await self.createEmbed(lobby_view.player_ids)
                await lobby_msg.edit_original_message(embed=embed)
                lobby_view.update = False

        # delete lobby and return list of participating players
        lobby_view.stop()
        await lobby_msg.delete_original_message()
        return lobby_view.player_ids

    async def createEmbed(self, player_ids: List[int]) -> discord.Embed:
        """
        :param player_ids: a list of user ids of the players participating in the game
        :return: lobby embed
        """

        host = await self.game_service.bot.fetch_user(player_ids[0])
        title = f"A game of {self.game_name}"
        description = f"{host} started a game of {self.game_name} \n\n" + \
                      f"use `/rules {self.game_name}` to learn how to play cardbot's version of {self.game_name}!"

        embed = discord.Embed(title=title, description=description)

        embed.add_field(name="Number of Players", value=f"{len(player_ids)}/6", inline=False)

        for i, player_id in enumerate(player_ids):
            player = await self.game_service.bot.fetch_user(player_id)
            embed.add_field(name=f"Player {i+1}", value=player)

        return embed


def setup(bot):
    bot.add_cog(GameService(bot))
