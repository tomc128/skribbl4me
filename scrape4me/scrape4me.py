# A bot that plays games against another version of itself. Based on code in ./skribbl4me.py, it should spin up two webdriver instances,
# create a private game and play against each other. It should collect data about which words are used. It should repeat this process 
# for ever. Write for me copilot


from os import path
from typing import Literal
from time import sleep

import clipboard

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
from selenium.webdriver.support.ui import Select




class Scraper:

    def __init__(self, role: Literal['host', 'player'], executable_name: str):
        self.role = role
        self.executable_name = executable_name

        self.__init_driver()
    
    def __init_driver(self):
        driver_executable = path.join(path.dirname(path.abspath(__file__)), 'lib', 'webdriver', self.executable_name)

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


if __name__ == '__main__':
    host = Scraper('host', 'msedgedriver.exe')
    player = Scraper('player', 'msedgedriver.exe')

    host_link = host.host__host_game()

    print(f'Host link: "{host_link}"')

    player.player__join_game(host_link)

    host.host__start_game()

    input()