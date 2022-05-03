import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from decouple import config

from src.main import main


@pytest.fixture(scope="module")
def browsers():
    drivers = []
    for i in range(6):
        driver = webdriver.Chrome()
        driver.get("https://discord.com/channels/904807840236060732/970085634351964221")
        driver.set_window_rect(45 + (640 * (i % 3)), -10 + (540 * (i % 2)), 640, 540)
        driver.execute_script("document.body.style.zoom='50%'")
        drivers.append(driver)

    time.sleep(2)

    yield drivers

    time.sleep(20)
    for driver in drivers:
        driver.quit()


@pytest.fixture(scope="module")
def bot():
    return main()


def test_login(browsers):
    for i, browser in enumerate(browsers):
        email_box = browser.find_element(by=By.NAME, value="email")
        email_box.send_keys(config(f"TEST_EMAIL_{i+1}"))

        pass_box = browser.find_element(by=By.NAME, value="password")
        pass_box.send_keys(config(f"TEST_PASS_{i+1}"))

        browser.find_element(by=By.CLASS_NAME, value="contents-3ca1mk").submit()
        time.sleep(1)

    time.sleep(6)

    for browser in browsers:
        assert browser.current_url == "https://discord.com/channels/904807840236060732/970085634351964221"


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
