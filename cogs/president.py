import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, slash_command
from main import players, games
from cogs.baseGame import mainGameMenu, startGameButton, CardButton
import asyncio
import requests
import logging
from cardsAPI import Deck

class president(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    play = SlashCommandGroup("play", "play a card game!")


    @play.command(description="a game of president")
    async def president(self, ctx):

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
            await ctx.send("game cancelled")
            return

        view.stop()
        await lobbyMessage.delete_original_message()

        
        # divide the deck evenly between the players
        deck / games[gameID]["players"]

        m = await ctx.send("The cards have been drawn!\nUse `/hand` to see your hand")
        await m.delete(delay=30)
        m = await ctx.send("```1.) if you are the president:\n" +
                        "   - use `/give <cardCode>` to give the lowest ranking player a card\n" +
                        "   - once everyone is ready, use `/start` to start the game\n" +
                        "2.) if you are the lowest ranking player:\n" +
                        "   - use `/give <cardCode>` to give the president your best card\n```"
                        )
        await m.delete(delay=30)

        view = discord.ui.View()

        cards = deck.piles[UserID].toList()

        for card in cards[:24]:
            view.add_item(CardButton(card))

        await ctx.respond("pick a card or pass, no action for 5 seconds is an auto-pass", view=view)



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







    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("President module ready!")












def setup(bot):
    bot.add_cog(president(bot))