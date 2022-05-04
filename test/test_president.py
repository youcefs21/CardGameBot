import time

import discord
import pytest
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from decouple import config
import threading

from src.main import main


@pytest.fixture(scope="module")
def browser():
    driver = webdriver.Firefox()
    test_channel = config("TEST_CHANNEL")
    driver.get(test_channel)
    print("\nstarting browsers...")
    for i in range(6):
        driver.execute_script(f"window.open('{test_channel}')")
        print(f"tab {i+2} is open")
        time.sleep(1)

    time.sleep(2)

    yield driver

    time.sleep(1)
    driver.quit()


@pytest.fixture(scope="module")
def bot():
    bt: discord.Bot = main()
    bot_thread = threading.Thread(
        target=lambda b: b.run(config('TOKEN')),
        args=(bt,),
        daemon=True
    )
    bot_thread.start()

    time.sleep(2)  # wait for bot to start
    yield bt

    bt.close()


def test_login(browser):
    for i, window in enumerate(browser.window_handles):
        browser.switch_to.window(window)
        email_box = browser.find_element(by=By.NAME, value="email")
        email_box.send_keys(config(f"TEST_EMAIL_{i+1}"))

        pass_box = browser.find_element(by=By.NAME, value="password")
        pass_box.send_keys(config(f"TEST_PASS_{i+1}"))

        browser.find_element(by=By.CLASS_NAME, value="contents-3ca1mk").submit()
        time.sleep(1)

    time.sleep(1)
    for i, window in enumerate(browser.window_handles):
        browser.switch_to.window(window)
        time.sleep(0.5)
        assert browser.find_element(by=By.CLASS_NAME, value="title-338goq").text == f"Tester{i + 1}"


class TestLobby:

    def test_already_in_game(self, browser, bot):
        """
        test that the host can't join their own game
        :param browser: Firefox webdriver with at least 1 logged in discord account
        :param bot: initialize the bot
        :return: assert that "You're already in a game!" was sent
        """

        browser.switch_to.window(browser.window_handles[0])

        text_box = browser.find_element(by=By.CLASS_NAME, value="markup-eYLPri")

        for i in range(2):
            ActionChains(browser).send_keys("/play president" + Keys.ENTER + Keys.ENTER).perform()
            time.sleep(2)

        msg = browser.find_elements(by=By.CLASS_NAME, value="messageListItem-ZZ7v6g")
        assert msg[-1].find_element(by=By.CLASS_NAME, value="messageContent-2t3eCI").text == "You're already in a game!"

    def test_min_player_count(self, browser, bot):
        """
        test that the host can't start a game with less than 2 players
        :param browser: Firefox webdriver with at least 1 logged in discord account
        :param bot: initialize the bot
        :return: assert that "You need at least 2 players to start a game!" was sent
        """

        browser.find_elements(by=By.XPATH, value='//descendant::button[.="Next"]')[-1].click()
        time.sleep(1)
        msgs = browser.find_elements(by=By.CLASS_NAME, value="messageListItem-ZZ7v6g")
        msg = msgs[-1].find_element(by=By.CLASS_NAME, value="messageContent-2t3eCI")
        assert msg.text == "There isn't enough players!"
