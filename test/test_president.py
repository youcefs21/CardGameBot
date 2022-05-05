
###############################################################################
#            THE CODE BELLOW USES SELF-BOTS, WHICH ARE AGAINST                #
#       THE DISCORD TERMS OF SERVICE. THUS, IT HAS BEEN DEPRECATED            #
###############################################################################
#                                                                             #
# they were a pain to figure out,                                             #
#                                       and a joy to see finally working      #
#                                                                             #
#                                                                             #
#     Tester1                                                                 #
#                          Tester2                                            #
#                                           Tester3                           #
#                                                     Tester4                 #
#                              Tester5                                        #
#               Tester6                                                       #
#                                            Tester7                          #
#                                                                             #
#                         you will be missed o7                               #
###############################################################################


"""
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

    # login into all tabs
    for i, window in enumerate(driver.window_handles):
        driver.switch_to.window(window)
        email_box = driver.find_element(by=By.NAME, value="email")
        email_box.send_keys(config(f"TEST_EMAIL_{i+1}"))

        pass_box = driver.find_element(by=By.NAME, value="password")
        pass_box.send_keys(config(f"TEST_PASS_{i+1}"))

        driver.find_element(by=By.CLASS_NAME, value="contents-3ca1mk").submit()
        time.sleep(1.5)

    # check that all the tabs are logged in
    time.sleep(1)
    for i, window in enumerate(driver.window_handles):
        driver.switch_to.window(window)
        time.sleep(0.5)
        assert driver.find_element(by=By.CLASS_NAME, value="title-338goq").text == f"Tester{i + 1}"

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


class TestLobby:

    @pytest.fixture(scope="function")
    def min_lobby(self, browser, bot):
        # <start doc string>
        start a game of president with only 1 player, the host
        :param browser: Firefox webdriver with at least 1 logged in discord account
        :param bot: initialize the bot
        :return: bot
        # <end doc string>

        browser.switch_to.window(browser.window_handles[0])
        browser.find_element(by=By.CLASS_NAME, value="attachButton-1ijpt9").click()
        browser.find_element(by=By.ID, value="channel-attach-SLASH_COMMAND").click()
        ActionChains(browser).send_keys("play president" + Keys.ENTER + Keys.ENTER).perform()
        time.sleep(2)

        yield bot

        browser.switch_to.window(browser.window_handles[0])
        browser.find_elements(by=By.XPATH, value='//descendant::button[.="Leave"]')[-1].click()

        time.sleep(10)  # wait for leave event to trigger

    @pytest.fixture(scope="function")
    def full_lobby(self, browser, min_lobby):

        for i in range(1, 6):
            browser.switch_to.window(browser.window_handles[i])
            time.sleep(0.1)
            browser.find_elements(by=By.XPATH, value='//descendant::button[.="Join"]')[-1].click()
            time.sleep(0.4)

        yield min_lobby

        # cancel the game by making all players leave
        for i in range(1, 6):
            browser.switch_to.window(browser.window_handles[i])
            time.sleep(0.2)
            browser.find_elements(by=By.XPATH, value='//descendant::button[.="Leave"]')[-1].click()

    def test_no_double_host(self, browser, min_lobby):
        # <start doc string>
        test that the host can't join their own game
        :param browser: Firefox webdriver with at least 1 logged in discord account
        :param min_lobby: initialize the bot and start a game of president
        :return: assert that "You're already in a game!" was sent
        # <end doc string>


        ActionChains(browser).send_keys("/play president" + Keys.ENTER + Keys.ENTER).perform()
        time.sleep(2)

        msg = browser.find_elements(by=By.CLASS_NAME, value="messageListItem-ZZ7v6g")
        assert msg[-1].find_element(by=By.CLASS_NAME, value="messageContent-2t3eCI").text == "You're already in a game!"

    def test_min_player_count(self, browser, min_lobby):
        # <start doc string>
        test that the host can't start a game with less than 2 players
        :param browser: Firefox webdriver with at least 1 logged in discord account
        :param min_lobby: initialize the bot and start a game of president
        :return: assert that "There isn't enough players!" was sent
        # <end doc string>
        time.sleep(2)

        browser.find_elements(by=By.XPATH, value='//descendant::button[.="Next"]')[-1].click()
        time.sleep(1)
        msgs = browser.find_elements(by=By.CLASS_NAME, value="messageListItem-ZZ7v6g")
        msg = msgs[-1].find_element(by=By.CLASS_NAME, value="messageContent-2t3eCI")
        assert msg.text == "There isn't enough players!"

    def test_max_player_count(self, browser, full_lobby):
        # <start doc string>
        test that no more than 6 players can join a game
        :param browser: Firefox webdriver with at least 1 logged in discord account
        :param full_lobby: initialize the bot
        :return: assert that "sorry, this game is full" was sent to the 7th player
        # <end doc string>

        browser.switch_to.window(browser.window_handles[-1])
        time.sleep(1)
        browser.find_elements(by=By.XPATH, value='//descendant::button[.="Join"]')[-1].click()
        time.sleep(2)

        msgs = browser.find_elements(by=By.CLASS_NAME, value="messageListItem-ZZ7v6g")
        msg = msgs[-1].find_element(by=By.CLASS_NAME, value="messageContent-2t3eCI")
        assert msg.text == "sorry, this game is full"

        browser.switch_to.window(browser.window_handles[-1])
        browser.close()
"""
