import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from decouple import config

from src.main import main


@pytest.fixture(scope="module")
def browsers():
    driver = webdriver.Firefox()
    test_channel = config("TEST_CHANNEL")
    driver.get(test_channel)
    print("\nstarting browsers...")
    for i in range(5):
        driver.execute_script(f"window.open('{test_channel}')")
        print(f"tab {i+2} is open")
        time.sleep(1)

    time.sleep(2)

    yield driver

    time.sleep(1)
    driver.quit()


@pytest.fixture(scope="module")
def bot():
    return main()


def test_login(browsers):
    for i, window in enumerate(browsers.window_handles):
        browsers.switch_to.window(window)
        email_box = browsers.find_element(by=By.NAME, value="email")
        email_box.send_keys(config(f"TEST_EMAIL_{i+1}"))

        pass_box = browsers.find_element(by=By.NAME, value="password")
        pass_box.send_keys(config(f"TEST_PASS_{i+1}"))

        browsers.find_element(by=By.CLASS_NAME, value="contents-3ca1mk").submit()
        time.sleep(2)

    time.sleep(4)
    for i, window in enumerate(browsers.window_handles):
        browsers.switch_to.window(window)
        time.sleep(0.5)
        assert browsers.find_element(by=By.CLASS_NAME, value="title-338goq").text == f"Tester{i+1}"

# class TestLobby:
#
#     @classmethod
#     def setup_class(cls):
#         pass
#
#     @classmethod
#     def teardown_class(cls):
#         pass
#
#     def test_mytest(self, browsers):
#         assert True
#
