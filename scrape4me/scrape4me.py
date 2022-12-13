# A bot that plays games against another version of itself. Based on code in ./skribbl4me.py, it should spin up two webdriver instances,
# create a private game and play against each other. It should collect data about which words are used. It should repeat this process
# for ever. Write for me copilot

import argparse
from os import path
from typing import Literal
from time import sleep

from threading import Thread

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, TimeoutException, ElementClickInterceptedException)
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys




LOOP_DELAY = 0.4
WORD_SELECT_DELAY = 0.25
OVERLAY_WAIT_DELAY = 0.25

# Normal values are 10 and 3. For a slow PC (like a raspberry pi) use 20 and 10
PAGE_LOAD_TIMEOUT = 10
ELEMENT_SEARCH_TIMEOUT = 3

RAW_WORD_ENCOUNTERS_FILE_NAME = 'word_encounters.txt'
RAW_WORD_ENCOUNTERS_FILE_PATH = path.join(path.dirname(path.abspath(__file__)), RAW_WORD_ENCOUNTERS_FILE_NAME)

# between 2 and 10 (inclusive) - 10 is most efficient
ROUND_COUNT = 10

global_stop_flag = False


def log_words(words: list[str]) -> None:
    words = [word.strip() for word in words if word.strip()] # Remove empty strings

    print(f'Logging {len(words)} words: {words}')

    with open(RAW_WORD_ENCOUNTERS_FILE_PATH, 'a', encoding='utf-8') as file:
        file.write('\n'.join(words))
        file.write('\n')




class Scraper:

    def __init__(self, role: Literal['host', 'player'], executable_name: str, webdriver_is_on_path: bool = False, headless: bool = False):
        self.other = None
        self.role = role
        self.executable_name = executable_name
        self.webdriver_is_on_path = webdriver_is_on_path

        self.__init_driver(headless=headless)

    def set_other(self, other: 'Scraper'):
        self.other = other

    def __init_driver(self, headless: bool = False):
        driver_executable = path.join(path.dirname(path.abspath(__file__)), '../', 'lib', 'webdriver', self.executable_name)

        browser = 'edge' if 'edgedriver' in driver_executable else 'chrome'

        if browser == 'edge':
            options = EdgeOptions()
            options.headless = headless
            options.add_argument('--mute-audio')

            if self.webdriver_is_on_path:
                self.driver = webdriver.Edge(options=options)
            else:
                service = EdgeService(executable_path=driver_executable)
                self.driver = webdriver.Edge(service=service, options=options)
        else:
            options = ChromeOptions()
            options.headless = headless
            options.add_argument('--mute-audio')

            if self.webdriver_is_on_path:
                self.driver = webdriver.Chrome(options=options)
            else:
                service = ChromeService(executable_path=driver_executable)
                self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.set_window_size(1200, 800)
        if self.role == 'host':
            self.driver.set_window_position(0, 0)
        else:
            self.driver.set_window_position(1200, 0)

        self.driver.get('https://skribbl.io/')
        WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(EC.presence_of_element_located((By.ID, 'home')))
        assert 'skribbl' in self.driver.title

        # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.SUBTRACT).key_up(Keys.CONTROL).perform()
        self.driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.CONTROL, Keys.SUBTRACT)
        self.driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.CONTROL, Keys.SUBTRACT)

        try:
            WebDriverWait(self.driver, ELEMENT_SEARCH_TIMEOUT).until(EC.presence_of_element_located((By.ID, 'cmpwelcomebtnyes')))
            consent_button = self.driver.find_element(By.ID, 'cmpwelcomebtnyes')
            consent_button.click()
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

    def host__host_game(self) -> str:
        create_room_button = self.driver.find_element(By.ID, 'home').find_element(By.CLASS_NAME, 'button-create')
        create_room_button.click()

        WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(EC.presence_of_element_located((By.ID, 'game-canvas')))
        sleep(3)

        ## Draw time
        draw_time_dropdown = Select(self.driver.find_element(By.ID, 'item-settings-drawtime'))
        draw_time_dropdown.select_by_visible_text('15')

        ## Number of rounds
        number_of_rounds_dropdown = Select(self.driver.find_element(By.ID, 'item-settings-rounds'))
        number_of_rounds_dropdown.select_by_visible_text(str(ROUND_COUNT))

        ## Number of words to choose from
        number_of_words_dropdown = Select(self.driver.find_element(By.ID, 'item-settings-wordcount'))
        number_of_words_dropdown.select_by_visible_text('5')

        ## Word mode
        # Choose 'combination' as this allows us to select two words out of two sets of number_of_words. i.e. 10 instead of 5 per drawing
        word_mode_dropdown = Select(self.driver.find_element(By.ID, 'item-settings-mode'))
        word_mode_dropdown.select_by_visible_text('Combination')

        ## Get invite link
        invite_field = self.driver.find_element(By.ID, 'input-invite')
        invite_link = invite_field.get_attribute('value')

        if not invite_link:
            invite_link = invite_field.text

        return invite_link

    def player__join_game(self, link: str):
        self.driver.get(link)
        WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(EC.presence_of_element_located((By.ID, 'home')))
        assert 'skribbl' in self.driver.title

        sleep(1) # additional time just in case, as previous page also had #home element

        join_button = self.driver.find_element(By.ID, 'home').find_element(By.CLASS_NAME, 'button-play')
        join_button.click()

    def host__start_game(self):

        player_list = self.driver.find_element(By.ID, 'game-players').find_element(By.CLASS_NAME, 'players-list')
        player_list_items = player_list.find_elements(By.CLASS_NAME, 'player')

        while len(player_list_items) < 2:
            sleep(1)
            print('Waiting for players to join...')
            player_list_items = player_list.find_elements(By.CLASS_NAME, 'player')

        start_game_button = self.driver.find_element(By.ID, 'start-game')
        start_game_button.click()

    # from skribbl4me.py
    def detect_state(self):
        screens : dict[str, WebElement | None] = {}

        screens['login'] = self.driver.find_element(By.ID, 'home') # initial login screen

        screens['loading'] = self.driver.find_element(By.ID, 'load') # loading screen
        screens['game'] = self.driver.find_element(By.ID, 'game') # game screen

        # must be after game screen
        try:
            screens['lobby'] = self.driver.find_element(By.CSS_SELECTOR, '.room.show') # custom lobby screen ('start-game' is a button with that ID which only displays when you're in the lobby - there is no dedicated lobby screen)
        except NoSuchElementException:
            screens['lobby'] = None

        displayed = []

        for screen_id, screen in screens.items():
            try:
                if screen:
                    if screen.is_displayed():
                        if screen_id == 'lobby':
                            displayed.remove('game')
                        displayed.append(screen_id)
            except StaleElementReferenceException:
                pass



        if len(displayed) == 0:
            return 'unknown'
        elif len(displayed) == 1:
            return displayed[0]
        else:
            return 'multiple'

    # adapted from skribbl4me.py
    def detect_game_state(self) -> str:
        try:
            toolbar = self.driver.find_element(By.ID, 'game-toolbar')
            if toolbar.is_displayed():
                return 'drawing'
        except NoSuchElementException:
            pass

        try:
            overlay = self.driver.find_element(By.ID, 'game-canvas').find_element(By.CLASS_NAME, 'overlay-content')
            if 'top: 0' in overlay.get_attribute('style'):
                word_select = self.driver.find_element(By.ID, 'game-canvas').find_element(By.CLASS_NAME, 'overlay-content').find_element(By.CLASS_NAME, 'words')
                if 'show' in word_select.get_attribute('class'):
                    return 'drawing__word_select'
                else:
                    return 'waiting_for_round'
        except NoSuchElementException:
            pass

        try:
            my_player = self.driver.find_element(By.ID, 'game-players').find_element(By.CLASS_NAME, 'players-list').find_element(By.CLASS_NAME, 'me')

            if 'guessed' in my_player.find_element(By.XPATH, '..').find_element(By.XPATH, '..').get_attribute('class'):
                return 'guessed'
        except NoSuchElementException:
            pass

        return 'guessing'

    def loop(self):

        last_game_state = None
        last_chosen_words = []

        while True:

            if global_stop_flag:
                break

            state = self.detect_state()
            # print(f'{self.role}: {state}')

            match state:
                case 'lobby':
                    if self.role == 'host':
                        try:
                            self.host__start_game()
                        except (ElementClickInterceptedException, ElementNotInteractableException):
                            print('Couldn\'t start game, button is covered by overlay. Retrying...')
                            pass


                    sleep(LOOP_DELAY)
                    continue

                case 'game':
                    game_state = self.detect_game_state()
                    # print(f'{self.role}: {state}/{game_state}')

                    if game_state == 'drawing__word_select':
                        if game_state != last_game_state:
                            last_game_state = game_state

                            word_select = self.driver.find_element(By.ID, 'game-canvas').find_element(By.CLASS_NAME, 'overlay-content').find_element(By.CLASS_NAME, 'words')
                            word_select_buttons = word_select.find_elements(By.CLASS_NAME, 'word')

                            # For combination word mode, there are two sets of words to choose from. They are both in the word_select element.
                            # They are interlaced, i.e. WS1-1, WS2-1, WS1-2, WS2-2, etc.
                            # We need to log all words, then choose one from the first set, wait, then choose one from the second set.

                            last_chosen_words = []
                            words_to_log = set()

                            counter = 0
                            while counter < 10:
                                if len(last_chosen_words) == 2:
                                    break

                                counter += 1
                                sleep(WORD_SELECT_DELAY)

                                visible_word_select_buttons = [button for button in word_select_buttons if button.is_displayed() and button.text.strip()]
                                if not visible_word_select_buttons:
                                    continue

                                for button in visible_word_select_buttons:
                                    words_to_log.add(button.text)

                                try:
                                    chosen_word = visible_word_select_buttons[0]
                                    chosen_word_text = chosen_word.text.strip()

                                    if not chosen_word_text:
                                        continue
                                    if chosen_word_text in last_chosen_words:
                                        continue

                                    chosen_word.click()
                                    last_chosen_words.append(chosen_word_text)
                                except (ElementNotInteractableException, NoSuchElementException):
                                    pass

                            log_words(list(words_to_log))

                            if counter == 10:
                                print('Error: Could not select word from word select screen. This round will take longer than usual.')
                        else:
                            # already logged these words, so just wait for the round to start
                            pass

                    elif game_state == 'drawing':
                        if game_state != last_game_state:
                            last_game_state = game_state

                            sleep(OVERLAY_WAIT_DELAY) # ensure overlay is gone

                            self.other.guess('+'.join(last_chosen_words))



                    elif game_state == 'waiting_for_round':
                        if game_state != last_game_state:
                            last_game_state = game_state

                    elif game_state == 'guessed':
                        if game_state != last_game_state:
                            last_game_state = game_state

            sleep(LOOP_DELAY)
            continue

    def guess(self, word):
        # #game > #game-wrapper #game-chat > .chat-container > form > input
        guess_input = self.driver.find_element(By.ID, 'game-wrapper').find_element(By.ID, 'game-chat').find_element(By.CLASS_NAME, 'chat-container').find_element(By.TAG_NAME, 'form').find_element(By.TAG_NAME, 'input')

        try:
            guess_input.send_keys(word)
            guess_input.send_keys('\n')
        except ElementNotInteractableException:
            print('Guess input field is not interactable')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Skribbl.io bot')
    parser.add_argument('-d', '--driver', required=True, help='Name of the webdriver executable (in ../lib or PATH)')
    parser.add_argument('-p', '--path-enable', action='store_true', help='Enable PATH search for webdriver executable (instead of searching ../lib)')
    parser.add_argument('--headless', action='store_true', help='Run webdriver in headless mode')
    args = parser.parse_args()

    print('Starting drivers and logging in... (this may take a while)')
    print('Once the threads start, you can exit the program by pressing enter in the terminal.')

    host = Scraper('host', args.driver, webdriver_is_on_path=args.path_enable, headless=args.headless)
    player = Scraper('player', args.driver, webdriver_is_on_path=args.path_enable, headless=args.headless)

    host.set_other(player)
    player.set_other(host)

    host_link = host.host__host_game()

    print(f'Host link: "{host_link}"')

    player.player__join_game(host_link)

    host.host__start_game()

    player_thread = Thread(target=player.loop)
    host_thread = Thread(target=host.loop)

    player_thread.start()
    host_thread.start()

    print('Threads started!')
    input('>> Press enter at any time to exit <<')
    print('Exiting, please wait...')

    global_stop_flag = True

    player.driver.quit()
    host.driver.quit()

    player_thread.join()
    host_thread.join()