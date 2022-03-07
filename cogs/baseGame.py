import discord
from discord.ext import commands
from discord.commands import slash_command
from main import players, games
import asyncio
import requests
import logging


class baseGame(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @slash_command(description="what cards do you have in your hand?")
    async def hand(self, ctx):
        # check if player is in a game
        UserID = int(ctx.author.id)
        if (players[UserID] == None):
            await ctx.respond("error: you're not in a game!", ephemeral=True)
            return
        
        gameID = players[UserID]
        hand = games[gameID]["deck"].piles[UserID]

        await ctx.respond("Your hand is: ```"+str(hand)+"```", ephemeral=True)

    @slash_command(description="quit the game you are currently in")
    async def quit(self, ctx):
        UserID = int(ctx.author.id)
        if (players[UserID] == None):
            await ctx.respond("nothing to quit from", ephemeral=True)
            return

        gameID = players[UserID]
        players[UserID] = None

        games[gameID]["players"].remove(UserID)
        await ctx.respond(f"you have been removed from game #{gameID} of type {games[gameID]['gameType']}", ephemeral=True)

        logging.info(f"removed {UserID} from game {gameID}, users left are {games[gameID]['players']}")

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Base Game module ready!")




# game lobby
class mainGameMenu(discord.ui.View):
    def __init__(self, gameID, roles, embed):
        self.gameID = gameID
        self.embed = embed
        self.roles = roles
        super().__init__(timeout=None)


    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green)
    async def joinGameButton(self, button, interaction):
        global games
        if len(self.roles) == 0:
            await interaction.response.send_message("`the game is full`", ephemeral=True)
            return

        # check that user is not already in a game
        UserID = int(interaction.user.id)
        if (players[UserID] != None):
            await interaction.response.send_message("error: you're already in a game!", ephemeral=True)
            return


        players[UserID] = self.gameID            
        self.embed.add_field(name=self.roles.pop(), value=str(interaction.user))


        games[self.gameID]["players"].append(UserID)


        await interaction.message.edit(embed=self.embed)
        await interaction.response.send_message("you're now part of the game!", ephemeral=True)

        if len(self.roles)==0:
            self.embed.description = "Game Full! Awaiting for host to start..."


class startGameButton(discord.ui.View):
    def __init__(self):
        self.started = False
        super().__init__()

    @discord.ui.button(label="Start Game!", style=discord.ButtonStyle.green)
    async def start(self, button, interaction):
        # check that user is in a game
        UserID = int(interaction.user.id)
        gameID = players[UserID]
        if (gameID == None):
            await interaction.response.send_message("error: you're not in a game", ephemeral=True)
            return

        # check that user is in the game host
        game = games[gameID]
        if (game["players"][0] != UserID):
            await interaction.response.send_message("error: you're not the game host", ephemeral=True)
            return


        self.started = True
        self.stop()
        
class nextButton(discord.ui.View):
    def __init__(self):
        self.started = False
        super().__init__()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def start(self, button, interaction):
        # check that user is in a game
        UserID = int(interaction.user.id)
        gameID = players[UserID]
        if (gameID == None):
            await interaction.response.send_message("error: you're not in a game", ephemeral=True)
            return

        # check that user is in the game host
        game = games[gameID]
        if (game["players"][0] != UserID):
            await interaction.response.send_message("error: you're not the game host", ephemeral=True)
            return
        self.started = True
        self.stop()


class CardButton(discord.ui.Button):
    def __init__(self, card):
        self.card = card
        super().__init__(
            label=str(card),
            style=discord.enums.ButtonStyle.primary,
            custom_id=str(card)
        )

    async def callback(self, interaction):
        logging.info(f"{self.card} button has been clicked")
        UserID = int(interaction.user.id)
        gameID = players[UserID]
        games[gameID]["deck"].piles[UserID].pick(self.card) # remove card
        deck = games[gameID]["deck"]

        view = discord.ui.View()
        cards = deck.piles[UserID].toList()

        for card in cards[:24]:
            view.add_item(CardButton(card))

        view.add_item(passButton())

        await interaction.response.edit_message(view=view)


class passButton(discord.ui.Button):
    def __init__(self):
        
        super().__init__(
            label="pass",
            style=discord.enums.ButtonStyle.secondary,
            custom_id="pass"
        )

    async def callback(self, interaction):
        logging.info(f"pass button has been clicked")

def setup(bot):
    bot.add_cog(baseGame(bot))