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
    GUESS_DELAY_RANGES = {
        0: (4, 8),
        1: (3, 6),
        2: (1, 2),
    }


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

        self.driver.set_window_size(1200, 800)
        self.driver.set_window_position(0, 0)

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
        print('Starting skribbling loop...')

        previous_website_state: str = 'unknown'
        previous_game_state: str = 'unknown'

        while self.skribbling_is_enabled:
            sleep(self.LOOP_DELAY)
                
            website_state = self.get_website_state()

            match website_state:
                case 'home':
                    if previous_website_state == 'home':
                        continue
                    previous_website_state = 'home'

                    print('On home screen. Waiting for game to start...')
                
                case 'lobby':
                    if previous_website_state == 'lobby':
                        continue
                    previous_website_state = 'lobby'

                    print('In lobby. Waiting for game to start...')
                
                case 'loading':
                    if previous_website_state == 'loading':
                        continue
                    previous_website_state = 'loading'
                    
                    print('In loading screen...')
                
                case 'game':
                    # Do not break if previous state was game, as the game requires multiple checks to be done
                    if previous_website_state != 'game':
                        print('In game.')

                    previous_website_state = 'game'

                    game_state = self.get_game_state()
                    
                    match game_state:
                        case 'drawing':
                            if previous_game_state == 'drawing':
                                continue
                            previous_game_state = 'drawing'

                            print('Drawing!')
                        
                        case 'waiting_for_round':
                            if previous_game_state == 'waiting_for_round':
                                continue
                            previous_game_state = 'waiting_for_round'

                            print('Skribbler: Waiting for round / Waiting for the next round to start...')
                        
                        case 'guessed':
                            if previous_game_state == 'guessed':
                                continue
                            previous_game_state = 'guessed'

                            print('Skribbler: Guessed / Waiting for the next round...')
                        
                        case 'guessing':
                            # Do not break if previous state was guessing, as guessing requires multiple checks to be done
                            if previous_game_state != 'guessing':
                                print('Guessing!')
                            previous_game_state = 'guessing'

                            print('Skribbler: Guessing / TODO: do something here...')

        print('Stopping skribbling loop...')


    def get_website_state(self) -> str:
        """Detects the current website state."""
        displayed: list[str] = []

        try:
            if self.driver.find_element(By.ID, 'home').is_displayed():
                displayed.append('home')
            
            if 'show' in self.driver.find_element(By.CSS_SELECTOR, '.room').get_attribute('class'):
                displayed.append('lobby')
            
            if self.driver.find_element(By.ID, 'load').is_displayed():
                displayed.append('loading')
            
            if self.driver.find_element(By.ID, 'game').is_displayed() and ('show' not in self.driver.find_element(By.CSS_SELECTOR, '.room').get_attribute('class')):
                displayed.append('game')

            match len(displayed):
                case 1:
                    return displayed[0]
                case 2:
                    return 'multiple'
                case 0 | _:
                    return 'unknown'
        
        except NoSuchElementException:
            return 'unknown'


    def get_game_state(self) -> str:
        """Detects the current game state."""

        try:
            game_toolbar = self.driver.find_element(By.ID, 'game-toolbar')
            if game_toolbar.is_displayed():
                return 'drawing'
        except NoSuchElementException:
            pass

        try:
            # #game-canvas > .overlay-content. but it is never hidden - its hidden when "top: -100%" and shown when "top: 0%"
            overlay = self.driver.find_element(By.ID, 'game-canvas').find_element(By.CLASS_NAME, 'overlay-content')
            if 'top: 0' in overlay.get_attribute('style'):
                return 'waiting_for_round'
        except NoSuchElementException:
            pass

        try:
            # #game-players > .players-list > .player [.guessed] > .player-info > .player-name [.me]
            my_player = self.driver.find_element(By.ID, 'game-players').find_element(By.CLASS_NAME, 'players-list').find_element(By.CLASS_NAME, 'me')

            if 'guessed' in my_player.find_element(By.XPATH, '..').find_element(By.XPATH, '..').get_attribute('class'):
                return 'guessed'
        except NoSuchElementException:
            pass

        return 'guessing'


    def extract_word_hint(self) -> str:
        """Extracts the word hint from the website."""
        word_hint = ''

        parent = self.driver.find_element(By.ID, 'game-word')
        hint_container = parent.find_element(By.CLASS_NAME, 'hints').find_element(By.CLASS_NAME, 'container')
        hints = hint_container.find_elements(By.CLASS_NAME, 'hint')

        for hint in hints:
            word_hint += ' ' if hint.text == '' else hint.text

        return word_hint.strip()


    def generate_hint_regex(self, word_hint: str) -> str:
        """Generates a regex pattern from the word hint."""
        return '^' + ''.join(['\\w' if char == '_' else '\\W' if char == ' ' else char for char in word_hint]) + '$'














