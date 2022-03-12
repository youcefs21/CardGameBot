import asyncio

import discord
import logging

from discord.commands import slash_command
from discord.ext import commands

import cogs.BaseGame as Base
from cardsAPI import Deck
from main import users, games


async def president(ctx: discord.ApplicationContext, bot: discord.Bot):
    # check that the person using the command is not already in a game
    user_id = int(ctx.user.id)
    if users[user_id] != "":
        await ctx.respond("error: you're already in a game!", ephemeral=True)
        return

    # initialize deck
    deck = Deck()
    game_id = deck.id

    # initialize game
    games[game_id] = {
        "gameType": "President",
        "deck": deck,
        "turnCount": 1,
        "players": [user_id],
        "lastTurn": (0, 0),
        "thisTurn": (0, 0),
        "passCounter": 0,
        "winners": []
    }
    game = games[game_id]

    # initialize user and players
    users[user_id] = game_id
    players = game['players']
    winners = game['winners']

    # initialize lobby components
    lobby_embed = discord.Embed(title="A game of President!", description="awaiting players...")
    lobby_embed.add_field(name="President", value=str(ctx.author))
    ranks = ["Scum", "High-Scum", "Citizen", "Vice-President", "President"]
    view = Base.MainGameMenu(game_id, ranks[:-1], lobby_embed)

    # send lobby
    lobby_message = await ctx.respond(view=view, embed=lobby_embed)

    # send a secret start game button to president
    start_view = Base.StartGameButton()
    start_message = await ctx.send("Press the `Start Game!` button to start the game", view=start_view)

    await start_view.wait()
    if not start_view.started:
        logging.info("game cancelled")
        for playerID in players:
            users[playerID] = ""
        await ctx.send("game cancelled")
        return

    view.stop()
    await lobby_message.delete_original_message()
    await start_message.delete()

    # divide the deck evenly between the players
    deck.div(players)

    next_view = Base.NextButton()
    instructions = await ctx.send("The cards have been drawn!\nUse `/hand` to see your hand\n" +
                                  "```1.) if you are the president:\n" +
                                  "   - use `/give <cardCode>` to give the lowest ranking player a card\n" +
                                  "   - once everyone is ready, press the `next` button to start round 1\n" +
                                  "2.) if you are the lowest ranking player:\n" +
                                  "   - use `/give <cardCode>` to give the president your best card\n```",
                                  view=next_view
                                  )

    await next_view.wait()
    if not next_view.started:
        logging.info("game cancelled")
        for playerID in players:
            users[playerID] = ""
        await ctx.send("game cancelled")
        return

    await instructions.delete()

    deck.createPile("table")
    deck.createPile("discard")

    cards_on_table = discord.File(deck.table_img.img_path, "table.png")
    pic_embed = discord.Embed()
    pic_embed.set_image(url="attachment://table.png")
    table_message = await ctx.send(
        "here are the cards that are currently on the table\n",
        file=cards_on_table,
        embed=pic_embed
    )
    cards_on_table = discord.File(deck.table_img.img_path)
    await table_message.edit(file=cards_on_table, embed=None)

    # Main game loop
    while len(players) > 1:
        turn_count = game['turnCount']
        n = len(players)
        next_player = players[turn_count % n]

        if game['passCounter'] >= n and game['lastTurn'] != (0, 0):
            game['passCounter'] = 0
            table_cards = deck.piles['table'].draw(deck.piles['table'].remaining)
            deck.piles['discard'].add(table_cards)
            game['lastTurn'] = (0, 0)
            game['thisTurn'] = (0, 0)
            deck.table_img.clearTable()

            picture = discord.File(deck.table_img.img_path)
            await table_message.edit(file=picture)

        round_view = Base.RoundView(table_message)

        m = await ctx.send(
            f"**Round {turn_count}!**\n\n" +
            f"<@{next_player}> it's your turn, click 'Show Hand' to proceed!\n" +
            "Will auto pass in 30 seconds",
            view=round_view
        )

        # wait 10 seconds, then check if the show hand button was pressed
        # if it was pressed, await round_view to stop
        for i in range(30):
            await asyncio.sleep(1)
            if round_view.started:
                break

        if round_view.started:
            await round_view.wait()
        else:
            game['passCounter'] += 1

        game['turnCount'] += 1
        if game['thisTurn'] != (0, 0):
            game['lastTurn'] = game['thisTurn']
            game['thisTurn'] = (0, 0)

        if deck.piles[next_player].remaining == 0:
            players.remove(next_player)
            await ctx.send(f"<@{next_player}> is the new {ranks[len(winners)]}!", delete_after=10)
            winners.append(next_player)
            users[next_player] = ""

        await m.delete()

    await ctx.send(f"<@{players[0]}> is the new Scum!", delete_after=10)
    users[players[0]] = ""

    game_summary_embed = discord.Embed(
        title="President Game Summary",
        description=f"the game lasted {game['turnCount']} rounds! The new rankings are:"
    )
    for i, winner_id in enumerate(winners):
        winner = await bot.fetch_user(int(winner_id))
        game_summary_embed.add_field(name=ranks[-(i+1)], value=str(winner))

    loser = await bot.fetch_user(int(players[0]))
    game_summary_embed.add_field(name="Scum", value=str(loser))

    await ctx.send(embed=game_summary_embed)


class President(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="give a card")
    async def give(self, ctx, card_code):
        # check if player is in a game
        user_id = int(ctx.author.id)
        if users[user_id] == "":
            await ctx.respond("error: you're not in a game!", ephemeral=True)
            return
        game_id = users[user_id]
        piles = games[game_id]['deck'].piles
        players = games[game_id]['players']

        # check if the person using is the lowest player
        if int(players[-1]) == user_id:
            pres_id = int(players[0])

        elif int(players[0]) == user_id:
            pres_id = int(players[-1])

        else:
            await ctx.respond("you are not the president, nor the lowest ranking player", ephemeral=True)
            return

        # take away card_code from user_id
        if not piles[pres_id].add([piles[user_id].pick(card_code)]):
            await ctx.respond("card not found", ephemeral=True)
            return

        await ctx.respond("card sent successfully", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("President module ready!")


def setup(bot):
    bot.add_cog(President(bot))
