import discord
from discord.ext import commands
from discord.commands import slash_command
from main import players, games
import logging


class BaseGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="what cards do you have in your hand?")
    async def hand(self, ctx):
        # check if player is in a game
        user_id = int(ctx.author.id)
        if players[user_id] is None:
            await ctx.respond("error: you're not in a game!", ephemeral=True)
            return

        game_id = players[user_id]
        hand = games[game_id]["deck"].piles[user_id]

        await ctx.respond("Your hand is: ```" + str(hand) + "```", ephemeral=True)

    @slash_command(description="quit the game you are currently in")
    async def quit(self, ctx):
        user_id = int(ctx.author.id)
        if players[user_id] == "":
            await ctx.respond("nothing to quit from", ephemeral=True)
            return

        game_id = players[user_id]
        players[user_id] = ""

        games[game_id]["players"].remove(user_id)
        await ctx.respond(f"you have been removed from game #{game_id} of type {games[game_id]['gameType']}",
                          ephemeral=True)

        logging.info(f"removed {user_id} from game {game_id}, users left are {games[game_id]['players']}")

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Base Game module ready!")


# game lobby
class MainGameMenu(discord.ui.View):
    def __init__(self, game_id, roles, embed):
        self.gameID = game_id
        self.embed = embed
        self.roles = roles
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green)
    async def joinGameButton(self, _, interaction):
        if len(self.roles) == 0:
            await interaction.response.send_message("`the game is full`", ephemeral=True)
            return

        # check that user is not already in a game
        user_id = int(interaction.user.id)
        if players[user_id] != "":
            await interaction.response.send_message("error: you're already in a game!", ephemeral=True)
            return

        players[user_id] = self.gameID
        self.embed.add_field(name=self.roles.pop(), value=str(interaction.user))

        games[self.gameID]["players"].append(user_id)

        await interaction.message.edit(embed=self.embed)
        await interaction.response.send_message("you're now part of the game!", ephemeral=True)

        if len(self.roles) == 0:
            self.embed.description = "Game Full! Awaiting for host to start..."


class StartGameButton(discord.ui.View):
    def __init__(self):
        self.started = False
        super().__init__()

    @discord.ui.button(label="Start Game!", style=discord.ButtonStyle.green)
    async def start(self, _, interaction):
        # check that user is in a game
        user_id = int(interaction.user.id)
        game_id = players[user_id]
        if game_id == "":
            await interaction.response.send_message("error: you're not in a game", ephemeral=True)
            return

        # check that user is in the game host
        game = games[game_id]
        if game["players"][0] != user_id:
            await interaction.response.send_message("error: you're not the game host", ephemeral=True)
            return

        self.started = True
        self.stop()


class NextButton(discord.ui.View):
    def __init__(self):
        self.started = False
        super().__init__()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def start(self, _, interaction):
        # check that user is in a game
        user_id = int(interaction.user.id)
        game_id = players[user_id]
        if game_id == "":
            await interaction.response.send_message("error: you're not in a game", ephemeral=True)
            return

        # check that user is in the game host
        game = games[game_id]
        if game["players"][0] != user_id:
            await interaction.response.send_message("error: you're not the game host", ephemeral=True)
            return
        self.started = True
        self.stop()


class CardButton(discord.ui.Button):
    def __init__(self, card, origin):
        self.card = card
        self.origin = origin
        super().__init__(
            label=str(card),
            style=discord.enums.ButtonStyle.primary,
            custom_id=str(card)
        )

    async def callback(self, interaction):
        user_id = int(interaction.user.id)
        game_id = players[user_id]
        games[game_id]["deck"].piles[user_id].pick(self.card)  # remove card
        deck = games[game_id]["deck"]

        view = discord.ui.View()
        cards = deck.piles[user_id].toList()

        for card in cards[:24]:
            view.add_item(CardButton(card, self.origin))

        view.add_item(PassButton(self.origin))

        await interaction.response.edit_message(view=view)


class PassButton(discord.ui.Button):
    def __init__(self, origin):
        self.origin = origin
        super().__init__(
            label="pass",
            style=discord.enums.ButtonStyle.secondary,
            custom_id="pass"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="turn passed", view=None)
        self.origin.stop()


class RoundView(discord.ui.View):
    def __init__(self):
        self.started = False
        super().__init__()

    @discord.ui.button(label="Show Hand", style=discord.ButtonStyle.blurple)
    async def btn(self, _, interaction: discord.Interaction):
        # check that user is in a game
        user_id = int(interaction.user.id)
        game_id = players[user_id]
        if game_id == "":
            await interaction.response.send_message("error: you're not in a game", ephemeral=True)
            return

        # check that user is in the game host
        turn_count = games[game_id]["turnCount"]
        n = len(games[game_id]["players"])
        if games[game_id]["players"][turn_count % n] != user_id:
            await interaction.response.send_message("it's not your turn yet!", ephemeral=True)
            return

        # signal that the button was pressed
        self.started = True

        view = discord.ui.View()

        deck = games[game_id]['deck']
        cards = deck.piles[user_id].toList()

        for card in cards[:24]:
            view.add_item(CardButton(card, view))

        view.add_item(PassButton(view))

        await interaction.response.send_message(
            "pick a card or pass, no action for 5 seconds is an auto-pass",
            view=view,
            ephemeral=True
        )

        await view.wait()
        games[game_id]["turnCount"] += 1
        self.stop()


def setup(bot):
    bot.add_cog(BaseGame(bot))
