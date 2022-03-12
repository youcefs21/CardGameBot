import discord
from discord.ext import commands
from discord.commands import slash_command

from cardsAPI import Card
from main import users, games
import logging


class BaseGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="what cards do you have in your hand?")
    async def hand(self, ctx):
        # check if player is in a game
        user_id = int(ctx.author.id)
        if users[user_id] is None:
            await ctx.respond("error: you're not in a game!", ephemeral=True)
            return

        game_id = users[user_id]
        hand = games[game_id]['deck'].piles[user_id]

        await ctx.respond("Your hand is: ```" + str(hand) + "```", ephemeral=True)

    @slash_command(description="quit the game you are currently in")
    async def quit(self, ctx):
        user_id = int(ctx.author.id)
        if users[user_id] == "":
            await ctx.respond("nothing to quit from", ephemeral=True)
            return

        game_id = users[user_id]
        users[user_id] = ""
        players = games[game_id]['players']

        players.remove(user_id)
        await ctx.respond(f"you have been removed from a game of {games[game_id]['gameType']}",
                          ephemeral=True)

        logging.info(f"removed {user_id} from game {game_id}, users left are {players}")

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
        if users[user_id] != "":
            await interaction.response.send_message("error: you're already in a game!", ephemeral=True)
            return

        users[user_id] = self.gameID
        self.embed.add_field(name=self.roles.pop(), value=str(interaction.user))

        games[self.gameID]['players'].append(user_id)

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
        game_id = users[user_id]
        if game_id == "":
            await interaction.response.send_message("error: you're not in a game", ephemeral=True)
            return

        # check that user is in the game host
        players = games[game_id]['players']
        if players[0] != user_id:
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
        game_id = users[user_id]
        if game_id == "":
            await interaction.response.send_message("error: you're not in a game", ephemeral=True)
            return

        # check that user is in the game host
        players = games[game_id]['players']
        if players[0] != user_id:
            await interaction.response.send_message("error: you're not the game host", ephemeral=True)
            return
        self.started = True
        self.stop()


class CardButton(discord.ui.Button):
    def __init__(self, card: Card, origin, table_message: discord.Message):
        self.card = card
        self.origin = origin
        self.table_message = table_message
        super().__init__(
            label=str(card),
            style=discord.enums.ButtonStyle.primary,
            custom_id=str(card)
        )

    async def callback(self, interaction):
        user_id = int(interaction.user.id)
        game_id = users[user_id]
        game = games[game_id]
        game['thisTurn'] = (int(self.card), game['thisTurn'][1] + 1)
        deck = game['deck']
        deck.piles[user_id].pick(self.card)  # remove card
        deck.table_img.addCard(self.card)
        deck.piles['table'].add([self.card])

        cards_on_table = discord.File(deck.table_img.img_path)
        await self.table_message.edit(file=cards_on_table, embed=None)

        _, min_count = game['lastTurn']
        _, current_count = game['thisTurn']

        if min_count == current_count:
            await interaction.response.edit_message(
                content="you have played enough cards, turn passed",
                view=None
            )
            self.origin.stop()
            return

        view = discord.ui.View()
        cards = deck.piles[user_id].toList()
        # filter out all cards that don't match the card that has been played this turn
        # [:] notation is to filter in place rather than override the alias
        cards[:] = [x for x in cards if x == self.card]

        # auto passed after playing all cards that you can play
        if len(cards) == 0:
            await interaction.response.edit_message(
                content="you don't have any playable cards, turn passed",
                view=None
            )
            self.origin.stop()
            return

        for card in cards[:24]:
            view.add_item(CardButton(card, self.origin, self.table_message))

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
        user_id = int(interaction.user.id)
        game_id = users[user_id]
        game = games[game_id]
        if game['gameType'] == "President":
            min_val, min_count = game['lastTurn']
            _, current_count = game['thisTurn']
            logging.info(f"played count: {current_count}, pass count: {game['passCounter']}")
            if current_count == 0:
                game['passCounter'] += 1
                await interaction.response.edit_message(content="turn passed", view=None)
                self.origin.stop()
                return

            if min_count > current_count:
                await interaction.response.send_message(f"you need to play exactly {min_count} cards before passing")
                return

        await interaction.response.edit_message(content="turn passed", view=None)
        self.origin.stop()


class RoundView(discord.ui.View):
    def __init__(self, table_message: discord.Message):
        self.started = False
        self.table_message = table_message
        super().__init__()

    @discord.ui.button(label="Show Hand", style=discord.ButtonStyle.blurple)
    async def btn(self, _, interaction: discord.Interaction):
        # check that user is in a game
        user_id = int(interaction.user.id)
        game_id = users[user_id]
        if game_id == "":
            await interaction.response.send_message("error: you're not in a game", ephemeral=True)
            return

        game = games[game_id]
        turn_count = game['turnCount']
        players = game['players']
        n = len(players)

        # check that user is in the game host
        if players[turn_count % n] != user_id:
            await interaction.response.send_message("it's not your turn yet!", ephemeral=True)
            return

        # signal that the button was pressed
        self.started = True

        view = discord.ui.View()

        deck = game['deck']
        cards = deck.piles[user_id].toList()
        dist = deck.piles[user_id].distribution
        min_val, min_count = game['lastTurn']
        # filter out all cards that are lower than the card played last turn
        # [:] notation is to filter in place rather than override the alias
        cards[:] = [x for x in cards if (x >= min_val) and (dist[int(x)] >= min_count)]

        cards.sort()

        # if you can't play any cards, auto pass
        if len(cards) == 0:
            await interaction.response.edit_message(content="you don't have any playable cards, turn passed", view=None)
            game['passCounter'] += 1
            view.stop()
            self.stop()
            return

        for card in cards[:24]:
            view.add_item(CardButton(card, view, self.table_message))

        view.add_item(PassButton(view))

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )
        _, current_count = game['thisTurn']
        if current_count != 0:
            game['passCounter'] = 0

        await view.wait()
        self.stop()


def setup(bot):
    bot.add_cog(BaseGame(bot))
