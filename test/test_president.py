import asyncio
import threading
import time

import discord
import pytest
from decouple import config
from src.cogs.GameService import GameService
from src.main import main


@pytest.fixture(scope="module")
def bot():
    """
    initialize the bot for testing. This bot will be used to send messages to the test channel
    :return: a discord.Bot object
    """
    bt: discord.Bot = main()

    def botThread(b: discord.Bot):
        b.run()

    bot_thread = threading.Thread(
        target=botThread,
        args=(bt,)
    )
    bot_thread.start()

    time.sleep(2)  # wait for bot to start
    yield bt

    asyncio.run(bt.close())


def test_command(bot):
    """
    this is how you would simulate a slash command,
    #TODO currently doesn't work because fake ctx is not complete
    :param bot:
    :return:
    """
    service = GameService(bot)
    ctx = FakeCTX(bot)

    result = asyncio.run(service.president.callback(service, ctx))


class FakeUser:
    id = 1


class FakeInteraction:
    data = {}


class FakeCTX:
    def __init__(self, bt):
        self.user = FakeUser
        self.bot: discord.Bot = bt
        self.interaction = FakeInteraction()

    async def send(self, msg="", ephemeral=False, embed=None, view=None, delete_after=10):
        channel = await self.bot.fetch_channel(config("TEST_CHANNEL"))
        return await channel.send(msg, embed=embed, view=view, delete_after=delete_after)

    async def respond(self, msg="", ephemeral=False, embed=None, view=None, delete_after=10):
        return await self.send(msg, embed, view, delete_after)

    async def send_response(self, msg="", embed=None, view=None, delete_after=10):
        return await self.send(msg, embed, view, delete_after)
