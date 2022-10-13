#!/usr/bin/python
# app/services/webdriver.py


"""
@author: Maxime Dréan.

Github: https://github.com/maximedrn
Telegram: https://t.me/maximedrn

Copyright © 2022 Maxime Dréan. All rights reserved.
Any distribution, modification or commercial use is strictly prohibited.
"""


# Selenium module imports: pip install selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as SC
from selenium.webdriver.firefox.service import Service as SG
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Webdriver Manager module: pip install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager as CDM
from webdriver_manager.firefox import GeckoDriverManager as GDM

# Python internal imports.
from ..utils.func import exit
from ..utils.colors import GREEN, RED, RESET

# Python default imports.
from datetime import datetime as dt
from os.path import abspath, exists
from os import name as osname


class Webdriver:
    """Webdriver class and methods to prevent exceptions."""

    def __init__(self, browser: int, browser_path: str,
                 wallet_name: str, wallet: object, solver: int) -> None:
        """Contains the file paths of the webdriver and the extension."""
        self.metamask_extension_path = abspath(  # MetaMask extension path.
            'assets/MetaMask.crx' if browser == 0 else 'assets/MetaMask.xpi')
        self.coinbase_wallet_extension_path = abspath(
            'assets/CoinbaseWallet.crx')  # Coinbase Wallet extension path.
        self.wallet_name = wallet_name.lower().replace(' ', '_')
        self.browser_path = browser_path  # Get the browser path.
        self.solver = solver  # reCAPTCHA solver number.
        self.wallet = wallet  # Instance of the Wallet class.
        # Start a Chrome (not headless) or Firefox (headless mode) webdriver.
        self.driver = self.chrome() if browser == 0 else self.firefox()
        self.window = browser  # Window handle value.

    def chrome(self) -> webdriver:
        """Start a Chrome webdriver and return its state."""
        options = webdriver.ChromeOptions()  # Configure options for Chrome.
        # Add wallet extension according to user choice
        options.add_extension(eval(f'self.{self.wallet_name}_extension_path'))
        options.add_argument('log-level=3')  # No logs is printed.
        options.add_argument('--mute-audio')  # Audio is muted.
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--lang=en-US')  # Set webdriver language
        options.add_experimental_option(  # to English. - 2 methods.
            'prefs', {'intl.accept_languages': 'en,en_US'})
        options.add_experimental_option('excludeSwitches', [
            'enable-logging', 'enable-automation'])
        driver = webdriver.Chrome(service=SC(  # DeprecationWarning using
            self.browser_path), options=options)  # executable_path.
        driver.maximize_window()  # Maximize window to reach all elements.
        return driver

    def firefox(self) -> webdriver:
        """Start a Firefox webdriver and return its state."""
        options = webdriver.FirefoxOptions()  # Configure options for Firefox.
        if self.solver != 1 and self.wallet.recovery_phrase != '' and \
                self.wallet.password != '':  # Not manual solver.
            options.add_argument('--headless')  # Headless mode.
        options.add_argument('--log-level=3')  # No logs is printed.
        options.add_argument('--mute-audio')  # Audio is muted.
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-dev-shm-usage')
        options.set_preference('intl.accept_languages', 'en,en-US')
        driver = webdriver.Firefox(service=SG(  # DeprecationWarning using
            self.browser_path), options=options)  # executable_path.
        driver.install_addon(self.metamask_extension_path)  # Add extension.
        driver.maximize_window()  # Maximize window to reach all elements.
        return driver

    def quit(self) -> None:
        """Stop the webdriver."""
        try:  # Try to close the webdriver.
            self.driver.quit()
        except Exception:  # The webdriver is closed
            pass  # or no webdriver is started.

    def clickable(self, element: str) -> None:
        """Click on an element if it's clickable using Selenium."""
        try:
            WDW(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH, element))).click()
        except Exception:  # Some buttons need to be visible to be clickable,
            self.driver.execute_script(  # so JavaScript can bypass this.
                'arguments[0].click();', self.visible(element))

    def visible(self, element: str):
        """Check if an element is visible using Selenium."""
        return WDW(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, element)))

    def send_keys(self, element: str, keys: str) -> None:
        """Send keys to an element if it's visible using Selenium."""
        try:
            self.visible(element).send_keys(keys)
        except Exception:  # Some elements are not visible but are present.
            WDW(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, element))).send_keys(keys)

    def send_date(self, element: str, keys: str) -> None:
        """Send a date (DD-MM-YYYY HH:MM) to a date input by clicking on it."""
        if self.window == 1:  # GeckoDriver (Mozilla Firefox).
            self.send_keys(element, '-'.join(
                reversed(keys.split('-'))) if '-' in keys else keys)
            return  # Quit the method.
        keys = keys.split('-') if '-' in keys else [keys]
        keys = [keys[1], keys[0], keys[2]] if len(keys) > 1 else keys
        for part in range(len(keys) - 1 if keys[len(keys) - 1] == str(
                          dt.now().year) else len(keys)):  # Number of clicks.
            self.clickable(element)  # Click first on the element.
            self.send_keys(element, keys[part])  # Then send it the date.

    def clear_text(self, element) -> None:
        """Clear text from an input."""
        self.clickable(element)  # Click on the element then clear its text.
        # Note: change with 'darwin' if it's not working on MacOS.
        control = Keys.COMMAND if osname == 'posix' else Keys.CONTROL
        if self.window == 0:  # ChromeDriver (Google Chrome).
            webdriver.ActionChains(self.driver).key_down(control).send_keys(
                'a').key_up(control).perform()
        elif self.window == 1:  # GeckoDriver (Mozilla Firefox).
            self.send_keys(element, (control, 'a'))

    def is_empty(self, element: str, data: str, value: str = '') -> bool:
        """Check if data is empty and input its value."""
        if data != value:  # Check if the data is not an empty string
            self.send_keys(element, data)  # or a default value, and send it.
            return False
        return True

    def window_handles(self, window_number: int) -> None:
        """Check for window handles and wait until a specific tab is opened."""
        window_number = {1: 0, 0: 1, 2: 2}[window_number] \
            if self.window == 1 else window_number
        WDW(self.driver, 10).until(lambda _: len(
            self.driver.window_handles) > window_number)
        self.driver.switch_to.window(  # Switch to the asked tab.
            self.driver.window_handles[window_number])


def download_browser(browser: int) -> str:
    """Try to download the webdriver using the Driver Manager."""
    try:
        # Set the name of the webdriver according to browser choice.

        # If you have a mismatch with chromedriver use this.
        # https://chromedriver.storage.googleapis.com/index.html?path=107.0.5304.18/
        # browser_path = abspath('assets/chromedriver') # chromedriver_mac64_m1.zip
        # return browser_path

        webdriver = 'ChromeDriver' if browser == 0 else 'GeckoDriver'
        print(f'Downloading the {webdriver}.', end=' ')
        # Download the webdriver using the Driver Manager module.
        browser_path = CDM(log_level=0).install() if browser == 0 \
            else GDM(log_level=0).install()
        print(f'{GREEN}{webdriver} downloaded:{RESET} \n{browser_path}')
        return browser_path  # Return the path of the webdriver.
    except Exception:
        print(f'{RED}Browser download failed.{RESET}')
        # Set the browser path as "assets/" + browser + extension.
        browser_path = abspath('assets/' + (
            'chromedriver.' + 'exe' if osname == 'nt' else '') if browser == 0
            else ('geckodriver.' + 'exe' if osname == 'nt' else ''))
        # Check if an executable is already in this path, else exit.
        if not exists(browser_path):
            exit('Download the webdriver and place it in the assets/ folder.')
        print(f'Webdriver path set as {browser_path}')
