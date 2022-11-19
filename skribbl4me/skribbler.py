"""Contains the Skribbler class."""

import random
import re
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
from selenium.webdriver.common.keys import Keys



def clamp(value, min_value, max_value):
    """Clamps a value to a min and max value."""
    return max(min(value, max_value), min_value)


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
        self.current_round_guessed_words = []

        self.loop_thread: Thread


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
        if self.skribbling_is_enabled:
            return

        self.loop_thread = Thread(target=self.loop)

        self.skribbling_is_enabled = True
        self.loop_thread.start()


    def stop_skribbling(self) -> None:
        """Stops the skribbling loop."""
        if not self.skribbling_is_enabled:
            return

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
                case w_state if w_state in ['home', 'lobby', 'loading']:
                    if previous_website_state == w_state:
                        continue
                    previous_website_state = w_state

                    print(f'Website state: {w_state}')
                
                case 'game':
                    # Do not break if previous state was game, as the game requires multiple checks to be done
                    if previous_website_state != 'game':
                        print('Website state: game')

                    previous_website_state = 'game'

                    game_state = self.get_game_state()
                    
                    match game_state:
                        case g_state if g_state in ['drawing', 'waiting_for_round', 'guessed']:
                            if previous_game_state == g_state:
                                continue
                            previous_game_state = g_state

                            print(f'Game state: {g_state}')
                            self.current_round_guessed_words = []
                        
                        case 'guessing':
                            # Do not break if previous state was guessing, as guessing requires multiple checks to be done
                            if previous_game_state != 'guessing':
                                print('Guessing!')
                            previous_game_state = 'guessing'

                            word_hint = self.extract_word_hint()
                            hint_regex = self.generate_hint_regex(word_hint)

                            number_of_hints = self.get_number_of_hints_given(word_hint)

                            possible_words = self.get_possible_words(hint_regex)
                            possible_words = list(set(possible_words) - set(self.current_round_guessed_words))
                            word_to_guess = self.choose_word_to_guess(possible_words)

                            if word_to_guess:
                                print(f'Guessing "{word_to_guess}". One of {len(possible_words)} possible words from the hint "{word_hint}".')
                                self.make_guess(word_to_guess)

                                # Wait a random amount of time before guessing again
                                guess_delay = random.randint(*self.GUESS_DELAY_RANGES[clamp(number_of_hints, 0, len(self.GUESS_DELAY_RANGES) - 1)])
                                print(f'Waiting {guess_delay} seconds before guessing again...')
                                sleep(guess_delay)
                            
                            print('Done')




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
            # if 'top: 0' in overlay.get_attribute('style'):
            #     return 'waiting_for_round'
            if 'top: -100%' not in overlay.get_attribute('style'):
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


        # TODO: Sometimes the app thinks we are guessing when in reality the round is over (but the overlay hasn't quite been hidden yet)
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


    def get_number_of_hints_given(self, word_hint: str) -> int:
        """Returns the number of hints given."""
        # the number of hints is the number of letters in the word hint (not spaces or _)
        return len([letter for letter in word_hint if letter != ' ' and letter != '_'])


    def generate_hint_regex(self, word_hint: str) -> str:
        """Generates a regex pattern from the word hint."""
        return '^' + ''.join(['\\w' if char == '_' else '\\W' if char == ' ' else char for char in word_hint]) + '$'


    def get_possible_words(self, hint_regex: str) -> list[str]:
        """Returns a list of possible words that match the hint regex."""
        return [word for word in self.word_list if re.match(hint_regex, word)]


    def choose_word_to_guess(self, possible_words: list[str]) -> str:
        """Chooses a word to guess from the list of possible words."""
        return random.choice(possible_words) if possible_words else ''


    def make_guess(self, word: str) -> None:
        """Makes a guess."""
        # #game > #game-wrapper #game-chat > .chat-container > form > input
        guess_input = self.driver.find_element(By.ID, 'game-wrapper').find_element(By.ID, 'game-chat').find_element(By.CLASS_NAME, 'chat-container').find_element(By.TAG_NAME, 'form').find_element(By.TAG_NAME, 'input')

        if guess_input.get_attribute('value'):
            # user is typing, wait for them to finish
            return
        
        try:
            guess_input.send_keys(word)
            guess_input.send_keys(Keys.RETURN)
            self.current_round_guessed_words.append(word)
        except ElementNotInteractableException:
            pass












