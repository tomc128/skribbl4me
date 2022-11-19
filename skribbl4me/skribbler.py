"""Contains the Skribbler class."""

from threading import Thread
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class Skribbler:
    """Handles all website interactions and game state logic."""

    PAGE_LOAD_TIMEOUT = 10
    COOKIE_CONSENT_TIMEOUT = 3

    LOOP_DELAY = 0.1

    
    def __init__(self, driver_executable: str, autodraw_extension: str, word_list: list[str]) -> None:
        """Initializes the Skribbler class."""
        self.word_list = word_list
        self.driver_is_initialised = False
        self.website_is_loaded = False
        self.skribbling_is_enabled = False
        self.driver_executable = driver_executable
        self.autodraw_extension = autodraw_extension

        self.loop_thread = Thread(target=self.loop)


    def init_driver(self) -> None:
        """Initializes the Selenium driver."""
        browser = 'edge' if 'edgedriver' in self.driver_executable else 'chrome'

        if browser == 'edge':
            options = EdgeOptions()
            options.add_extension(self.autodraw_extension)
            service = EdgeService(executable_path=self.driver_executable)
            self.driver = webdriver.Edge(service=service, options=options)
        
        else:
            options = ChromeOptions()
            options.add_extension(self.autodraw_extension)
            service = ChromeService(executable_path=self.driver_executable)
            self.driver = webdriver.Chrome(service=service, options=options)
        
        self.driver_is_initialised = True
            

    def load_website(self) -> None:
        """Loads the skribbl.io website and accepts cookies."""
        self.driver.get('https://skribbl.io')
        WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(EC.presence_of_element_located((By.ID, 'home')))
        assert 'skribbl' in self.driver.title

        try:
            WebDriverWait(self.driver, self.COOKIE_CONSENT_TIMEOUT).until(EC.presence_of_element_located((By.ID, 'cmpwelcomebtnyes')))
            consent_button = self.driver.find_element(By.ID, 'cmpwelcomebtnyes')
            consent_button.click()
        except (NoSuchElementException, TimeoutException):
            pass
            
        self.website_is_loaded = True
    

    def start_skribbling(self) -> None:
        """Starts the skribbling loop."""
        self.skribbling_is_enabled = True
        self.loop_thread.start()


    def stop_skribbling(self) -> None:
        """Stops the skribbling loop."""
        if self.skribbling_is_enabled:
            self.skribbling_is_enabled = False
            self.loop_thread.join()


    def loop(self) -> None:
        """The main loop."""
        while self.skribbling_is_enabled:
            print('loop')
            sleep(self.LOOP_DELAY)
