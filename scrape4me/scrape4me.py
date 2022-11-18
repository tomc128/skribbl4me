# A bot that plays games against another version of itself. Based on code in ./skribbl4me.py, it should spin up two webdriver instances,
# create a private game and play against each other. It should collect data about which words are used. It should repeat this process 
# for ever. Write for me copilot


from os import path
from typing import Literal
from time import sleep

from threading import Thread

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException)
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




LOOP_DELAY = 2
RAW_WORD_ENCOUNTERS_FILE = './word_encounters.txt'



def log_word(word: str) -> None:
    if not word.strip():
        return
        
    print(f'Logging word: {word}')
    with open(RAW_WORD_ENCOUNTERS_FILE, 'a', encoding='utf-8') as file:
        file.write(f'{word}\n')




class Scraper:

    def __init__(self, role: Literal['host', 'player'], executable_name: str):
        self.role = role
        self.executable_name = executable_name

        self.__init_driver()
    
    def __init_driver(self):
        driver_executable = path.join(path.dirname(path.abspath(__file__)), '../', 'lib', 'webdriver', self.executable_name)

        browser = 'edge' if 'edgedriver' in driver_executable else 'chrome'

        if browser == 'edge':
            options = EdgeOptions()
            service = EdgeService(executable_path=driver_executable)
            self.driver = webdriver.Edge(service=service, options=options)
        else:
            options = ChromeOptions()
            service = ChromeService(executable_path=driver_executable)
            self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.get('https://skribbl.io/')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'home')))
        assert 'skribbl' in self.driver.title

        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'cmpwelcomebtnyes')))
        try:
            consent_button = self.driver.find_element(By.ID, 'cmpwelcomebtnyes')
            consent_button.click()
        except NoSuchElementException:
            pass
    
    def host__host_game(self) -> str:
        create_room_button = self.driver.find_element(By.ID, 'home').find_element(By.CLASS_NAME, 'button-create')
        create_room_button.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'game-canvas')))
        sleep(3)

        ## Draw time
        draw_time_dropdown = Select(self.driver.find_element(By.ID, 'item-settings-drawtime'))
        draw_time_dropdown.select_by_visible_text('15')

        ## Number of rounds
        number_of_rounds_dropdown = Select(self.driver.find_element(By.ID, 'item-settings-rounds'))
        number_of_rounds_dropdown.select_by_visible_text('10')

        ## Get invite link
        invite_field = self.driver.find_element(By.ID, 'input-invite')
        invite_link = invite_field.get_attribute('value')

        if not invite_link:
            invite_link = invite_field.text
        
        return invite_link

    def player__join_game(self, link: str):
        self.driver.get(link)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'home')))
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
        screens : dict[str, WebElement] = {}
        screens['login'] = self.driver.find_element(By.ID, 'home') # initial login screen
        screens['lobby'] = self.driver.find_element(By.ID, 'start-game') # custom lobby screen ('start-game' is a button with that ID which only displays when you're in the lobby - there is no dedicated lobby screen)
        screens['loading'] = self.driver.find_element(By.ID, 'load') # loading screen
        screens['game'] = self.driver.find_element(By.ID, 'game') # game screen
        displayed = []

        for screen_id, screen in screens.items():
            try:
                if screen.is_displayed():
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

        while True:
            state = self.detect_state()
            print(f'{self.role}: {state}')
            
            match state:
                case 'game':
                    game_state = self.detect_game_state()
                    print(f'{self.role}: {state}/{game_state}')
                
                    if game_state == 'drawing__word_select':
                        if game_state != last_game_state:
                            last_game_state = game_state
                            word_select = self.driver.find_element(By.ID, 'game-canvas').find_element(By.CLASS_NAME, 'overlay-content').find_element(By.CLASS_NAME, 'words')
                            word_select_buttons = word_select.find_elements(By.CLASS_NAME, 'word')

                            for button in word_select_buttons:
                                log_word(button.text)

                            try:
                                word_select_buttons[0].click()
                            except (ElementNotInteractableException, NoSuchElementException):
                                pass
                        else:
                            # already logged these words, so just wait for the round to start
                            pass

                    elif game_state == 'drawing':
                        if game_state != last_game_state:
                            last_game_state = game_state
                    
                    elif game_state == 'waiting_for_round':
                        if game_state != last_game_state:
                            last_game_state = game_state
                    
                    elif game_state == 'guessed':
                        if game_state != last_game_state:
                            last_game_state = game_state

            sleep(LOOP_DELAY)
            continue
            

if __name__ == '__main__':
    host = Scraper('host', 'msedgedriver.exe')
    player = Scraper('player', 'msedgedriver.exe')

    host_link = host.host__host_game()

    print(f'Host link: "{host_link}"')

    player.player__join_game(host_link)

    host.host__start_game()

    player_thread = Thread(target=player.loop)
    host_thread = Thread(target=host.loop)

    player_thread.start()
    host_thread.start()

    print('Threads started')
    input()