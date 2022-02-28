import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, slash_command
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


        everyPlayerGets = 52//len(games[currentGameID]["players"])
        extra = 52%len(games[currentGameID]["players"])
        for playerID in games[currentGameID]["players"]:
            if extra > 0:
                card = requests.get(f"https://deckofcardsapi.com/api/deck/{games[currentGameID]['deckId']}/draw/?count={everyPlayerGets+1}").json()
                extra-=1
            else:
                card = requests.get(f"https://deckofcardsapi.com/api/deck/{games[currentGameID]['deckId']}/draw/?count={everyPlayerGets}").json()

            cards = card['cards'][0]['code']
            for i in range(1,everyPlayerGets): cards += "," + card['cards'][i]['code'] 

            requests.get(f"https://deckofcardsapi.com/api/deck/{games[currentGameID]['deckId']}/pile/{playerID}/add/?cards={cards}")

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

        # check if the person using is the lowest player
        if int(games[gameID]["players"][-1]) == UserID:
            presID = int(games[gameID]["players"][0])

        elif int(games[gameID]["players"][0]) == UserID:
            presID = int(games[gameID]["players"][-1])
    
        else:
            await ctx.respond("you are not the president, nor the lowest ranking player", ephemeral=True)
            return



        # take away cardcode from UserID
        checkSuccess = requests.get(f"https://deckofcardsapi.com/api/deck/{games[gameID]['deckId']}/pile/{UserID}/draw/?cards={cardcode}").json()
        if checkSuccess["success"] != True:
            await ctx.respond("card error", ephemeral=True)
            return


        # give cardcode to other player
        requests.get(f"https://deckofcardsapi.com/api/deck/{games[gameID]['deckId']}/pile/{presID}/add/?cards={cardcode}")



        await ctx.respond("nice", ephemeral=True)



    @slash_command(description="start the gameplay")
    async def start(self, ctx):
        pass



    @slash_command(description="what cards do you have in your hand?")
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