import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from main import players, games, nextGameID
import asyncio
import requests


class president(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    president = SlashCommandGroup("president", "start a game of president!")

    # @president.command(description="only users listed can join this game!")
    # async def private(self, ctx):
    #     await ctx.respond("error: not implemented")

    @president.command(description="anyone in the server can join this game!")
    async def play(self, ctx):
        global nextGameID

        # check that the person using the command is not already in a game
        UserID = int(ctx.author.id)
        if (players[UserID] != None):
            await ctx.respond("error: you're already in a game!", ephemeral=True)
            return


        # initialize player 
        players[UserID] = nextGameID
        nextGameID+=1
        currentGameID = players[UserID]

        # initialize game 
        games[currentGameID] = {
            "deckId": None,
            "turnCount": 1,
            "players": [UserID]
            }

        # initialize lobby components
        lobbyEmbed = discord.Embed(title="A game of President!",description="awaiting players...")
        lobbyEmbed.add_field(name="President", value=str(ctx.author))
        view = mainGameMenu(currentGameID, ["Scum", "High-Scum", "Citizen", "Vice-President"], lobbyEmbed)

        # send lobby
        lobbyMessage = await ctx.respond(view=view, embed=lobbyEmbed)

        # send a secret start game button to president
        startView = startGameButton(currentGameID, lobbyMessage)
        await ctx.respond("Press the `Start Game!` button to start the game",view=startView, ephemeral=True)

        await startView.wait()

        # deal the cards:
        deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1").json()
        games[currentGameID]["deckId"] = deck['deck_id']

        # tell users cards are being drawn
        m = await ctx.send("drawing each player their cards... This will take about 15 seconds")


        done = True
        while done:
            for playerID in games[currentGameID]["players"]:
                print(deck["remaining"])
                if deck["remaining"] == 0:
                    done = False
                    break
                card = requests.get(f"https://deckofcardsapi.com/api/deck/{games[currentGameID]['deckId']}/draw/?count=1").json()
                deck["remaining"] -= 1
                requests.get(f"https://deckofcardsapi.com/api/deck/{games[currentGameID]['deckId']}/pile/{playerID}/add/?cards={card['cards'][0]['code']}")

        await m.delete()
        await ctx.send("The cards have been drawn! Use `/president hand` to see your hand (don't worry, only you can see the message sent)")


        await ctx.send("if you are the president, use `/president givelow <cardCode>` to give the lowest ranking player a card")
        await ctx.send("if you are the lowest ranking player, use `/president givehigh <cardCode>` to give the president your best card")
        await ctx.send("once everyone is ready, the president must use `/president start` to start the game")




    @president.command(description="give the president a card")
    async def givehigh(self, ctx, cardcode):
        # check if player is in a game
        UserID = int(ctx.author.id)
        if (players[UserID] == None):
            await ctx.respond("error: you're not in a game!", ephemeral=True)
            return
        gameID = players[UserID]

        # check if the person using is the lowest player
        if int(games[gameID]["players"][-1]) != UserID:
            await ctx.respond("you are not the lowest ranking player", ephemeral=True)
            return

        # take away cardcode from UserID
        checkSuccess = requests.get(f"https://deckofcardsapi.com/api/deck/{games[gameID]['deckId']}/pile/{UserID}/draw/?cards={cardcode}").json()
        if checkSuccess["success"] != True:
            await ctx.respond("card error", ephemeral=True)
            return



        # give cardcode to int(games[gameID]["players"][0]) instead
        presID = int(games[gameID]["players"][0])
        requests.get(f"https://deckofcardsapi.com/api/deck/{games[gameID]['deckId']}/pile/{presID}/add/?cards={cardcode}")



        await ctx.respond("nice", ephemeral=True)



    @president.command(description="give the lowest ranking player a card")
    async def givelow(self, ctx, cardcode):
        # check if player is in a game
        UserID = int(ctx.author.id)
        if (players[UserID] == None):
            await ctx.respond("error: you're not in a game!", ephemeral=True)
            return
        
        gameID = players[UserID]



        # check if the person using is the highest player
        if int(games[gameID]["players"][0]) != UserID:
            await ctx.respond("you are not the lowest ranking player", ephemeral=True)
            return

        # take away cardcode from UserID
        checkSuccess = requests.get(f"https://deckofcardsapi.com/api/deck/{games[gameID]['deckId']}/pile/{UserID}/draw/?cards={cardcode}").json()

        if checkSuccess["success"] != True:
            await ctx.respond("card error", ephemeral=True)
            return


        # give cardcode to int(games[gameID]["players"][-1]) instead
        lowID = int(games[gameID]["players"][0])
        requests.get(f"https://deckofcardsapi.com/api/deck/{games[gameID]['deckId']}/pile/{lowID}/add/?cards={cardcode}")



        await ctx.respond("nice", ephemeral=True)



    @president.command(description="start the gameplay")
    async def start(self, ctx):
        pass









    @president.command(description="what cards do you have in your hand?")
    async def hand(self, ctx):
        # check if player is in a game
        UserID = int(ctx.author.id)
        if (players[UserID] == None):
            await ctx.respond("error: you're not in a game!", ephemeral=True)
            return
        
        currentGameID = players[UserID]

        # show hand
        hand = requests.get(f"https://deckofcardsapi.com/api/deck/{games[currentGameID]['deckId']}/pile/{UserID}/list/").json()
        cardCodes = [x["code"] for x in hand["piles"][str(UserID)]["cards"]]

        await ctx.respond("Your hand is: ```"+str(cardCodes)+"```", ephemeral=True)




    @commands.Cog.listener()
    async def on_ready(self):
        print("President module ready!")


class startGameButton(discord.ui.View):
    def __init__(self, gameID, lobbyMessage):
        self.gameID = gameID
        self.lobbyMessage = lobbyMessage
        super().__init__()

    @discord.ui.button(label="Start Game!", style=discord.ButtonStyle.green)
    async def start(self, button, interaction):
        self.stop()



# game lobby
class mainGameMenu(discord.ui.View):
    def __init__(self, gameID, roles, embed):
        self.gameID = gameID
        self.embed = embed
        self.roles = roles
        super().__init__(timeout=None)


    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
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
            self.embed.description = "Game Full! Awaiting for president to start..."









def setup(bot):
    bot.add_cog(president(bot))