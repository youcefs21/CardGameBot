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

    @president.command(description="only users listed can join this game!")
    async def private(self, ctx):
        await ctx.respond("error: not implemented")

    @president.command(description="anyone in the server can join this game!")
    async def public(self, ctx):
        global nextGameID

        # check that the person using the command is not already in a game
        UserID = int(ctx.author.id)
        if (players[UserID] != None):
            await ctx.respond("error: you're already in a game!")
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

        # dm a start game button to president
        startView = startGameButton(currentGameID, lobbyMessage)
        await ctx.author.send(embed=lobbyEmbed, view=startView)

        await startView.wait()

        # deal the cards:
        deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1").json()
        games[currentGameID]["deckId"] = deck['deck_id']

        # tell users cards are being drawn
        for playerID in games[currentGameID]["players"]:
            user = await self.bot.fetch_user(int(playerID))
            m = await user.send("drawing your cards... This will take about 15 seconds")
            await m.delete(delay=10)


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

        # show the players their hands
        handMessages = []
        for playerID in games[currentGameID]["players"]:
            user = await self.bot.fetch_user(int(playerID))
            hand = requests.get(f"https://deckofcardsapi.com/api/deck/{games[currentGameID]['deckId']}/pile/{playerID}/list/").json()
            cardCodes = [x["code"] for x in hand["piles"][str(playerID)]["cards"]]
            m = await user.send("Your hand is: ```"+str(cardCodes)+"```")
            handMessages.append(m)
        


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
        await self.lobbyMessage.delete_original_message()
        await asyncio.sleep(1)
        await interaction.message.delete()
        await asyncio.sleep(1)
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