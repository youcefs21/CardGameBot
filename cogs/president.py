import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, slash_command
from main import players, games
from cogs.baseGame import mainGameMenu, startGameButton
import asyncio
import requests
import logging
from cardsAPI import Deck

class president(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    president = SlashCommandGroup("president", "start a game of president!")

    # @president.command(description="only users listed can join this game!")
    # async def private(self, ctx):
    #     await ctx.respond("error: not implemented")

    @president.command(description="anyone in the server can join this game!")
    async def play(self, ctx):

        # check that the person using the command is not already in a game
        UserID = int(ctx.author.id)
        if (players[UserID] != None):
            await ctx.respond("error: you're already in a game!", ephemeral=True)
            return


        # initialize deck
        deck = Deck()
        gameID = deck.id

        # initialize game 
        games[gameID] = {
            "gameType": "President",
            "deck": None,
            "turnCount": 0,
            "players": [UserID]
            }

        # initialize player
        games[gameID]["deck"] = deck
        players[UserID] = gameID



        # initialize lobby components
        lobbyEmbed = discord.Embed(title="A game of President!",description="awaiting players...")
        lobbyEmbed.add_field(name="President", value=str(ctx.author))
        view = mainGameMenu(gameID, ["Scum", "High-Scum", "Citizen", "Vice-President"], lobbyEmbed)

        # send lobby
        lobbyMessage = await ctx.respond(view=view, embed=lobbyEmbed)

        # send a secret start game button to president
        startView = startGameButton()
        await ctx.respond("Press the `Start Game!` button to start the game",view=startView, ephemeral=True)

        await startView.wait()
        if not startView.started:
            logging.info("game cancelled")
            for playerID in games[gameID]["players"]:
                players[playerID] = None
            del games[gameID]
            ctx.send("game cancelled")
            return

        view.stop()
        await lobbyMessage.delete_original_message()

        
        # divide the deck evenly between the players
        deck / games[gameID]["players"]

        await ctx.send("The cards have been drawn!\nUse `/hand` to see your hand")

        await ctx.send("```1.) if you are the president:\n" +
                        "   - use `/give <cardCode>` to give the lowest ranking player a card\n" +
                        "   - once everyone is ready, use `/start` to start the game\n" +
                        "2.) if you are the lowest ranking player:\n" +
                        "   - use `/give <cardCode>` to give the president your best card\n```"
                        )





    @slash_command(description="give the president a card")
    async def give(self, ctx, cardcode):
        # check if player is in a game
        UserID = int(ctx.author.id)
        if (players[UserID] == None):
            await ctx.respond("error: you're not in a game!", ephemeral=True)
            return
        gameID = players[UserID]
        piles = games[gameID]["deck"].piles

        # check if the person using is the lowest player
        if int(games[gameID]["players"][-1]) == UserID:
            presID = int(games[gameID]["players"][0])

        elif int(games[gameID]["players"][0]) == UserID:
            presID = int(games[gameID]["players"][-1])
    
        else:
            await ctx.respond("you are not the president, nor the lowest ranking player", ephemeral=True)
            return

        # take away cardcode from UserID
        if (piles[presID] + [piles[UserID].pick(cardcode)]) == False:
            await ctx.respond("card not found", ephemeral=True)
            return

        await ctx.respond("card sent successfully", ephemeral=True)



    @slash_command(description="start the gameplay")
    async def start(self, ctx):
        pass




    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("President module ready!")












def setup(bot):
    bot.add_cog(president(bot))