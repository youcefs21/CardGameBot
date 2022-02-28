import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from main import players, games, nextGameID
import asyncio


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

        # initialize game 
        games[players[UserID]] = (None, 1, [UserID], {"President": UserID})

        # initialize lobby components
        lobbyEmbed = discord.Embed(title="A game of President!",description="awaiting players...")
        lobbyEmbed.add_field(name="President", value=str(ctx.author))
        view = mainGameMenu(players[UserID], ["Scum", "High-Scum", "Citizen", "Vice-President"], lobbyEmbed)

        # send lobby
        lobbyMessage = await ctx.respond(view=view, embed=lobbyEmbed)

        # dm a start game button to president
        startView = startGameButton(players[UserID], lobbyMessage)
        await ctx.author.send(embed=lobbyEmbed, view=startView)

        await view.wait()

        


    @commands.Cog.listener()
    async def on_ready(self):
        print("President module ready!")


class startGameButton(discord.ui.View):
    def __init__(self, gameID, lobbyMessage):
        self.gameID = gameID
        self.lobbyMessage = lobbyMessage
        super().__init__(timeout=None)

    @discord.ui.button(label="Start Game!", style=discord.ButtonStyle.green)
    async def start(self, button, interaction):
        await self.lobbyMessage.delete_original_message()
        await asyncio.sleep(1)
        await interaction.message.delete()
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


        await interaction.message.edit(embed=self.embed)
        await interaction.response.send_message("you're now part of the game!", ephemeral=True)

        if len(self.roles)==0:
            self.embed.description = "Game Full! Awaiting for president to start..."
            await interaction.message.edit(embed=self.embed)
            await asyncio.sleep(5)
            await interaction.message.delete()
            self.stop()









def setup(bot):
    bot.add_cog(president(bot))