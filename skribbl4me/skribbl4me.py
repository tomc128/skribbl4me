import argparse
import random
import re
from time import sleep
from os import path

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

LOOP_UPDATE_DELAY = 0.5
GUESS_DELAY_RANGE = [(4, 8), (3, 6), (1, 2)]


def init_driver(driver_executable: str) -> None:
    global driver

    driver_executable = path.join(path.dirname(path.abspath(__file__)), 'lib', 'webdriver', driver_executable)
    autodraw_extension = path.join(path.dirname(path.abspath(__file__)), 'lib', 'autodraw', 'autodraw.crx')

    browser = 'edge' if 'edgedriver' in driver_executable else 'chrome'

    if browser == 'edge':
        options = EdgeOptions()
        options.add_extension(autodraw_extension)
        service = EdgeService(executable_path=driver_executable)
        driver = webdriver.Edge(service=service, options=options)
    else:
        options = ChromeOptions()
        options.add_extension(autodraw_extension)
        service = ChromeService(executable_path=driver_executable)
        driver = webdriver.Chrome(service=service, options=options)


    driver.get('https://skribbl.io/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'home')))
    assert 'skribbl' in driver.title

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'cmpwelcomebtnyes')))
    try:
        consent_button = driver.find_element(By.ID, 'cmpwelcomebtnyes')
        consent_button.click()
    except NoSuchElementException:
        pass


def init_word_list() -> None:
    global word_list

    with open('default_words.txt', 'r') as f:
        word_list = [line.strip() for line in f.readlines() if line.strip()]

    print(f'Loaded {len(word_list)} words')


def detect_state() -> str:
    screens : dict[str, WebElement] = {}
    screens['login'] = driver.find_element(By.ID, 'home') # initial login screen
    screens['lobby'] = driver.find_element(By.ID, 'start-game') # custom lobby screen ('start-game' is a button with that ID which only displays when you're in the lobby - there is no dedicated lobby screen)
    screens['loading'] = driver.find_element(By.ID, 'load') # loading screen
    screens['game'] = driver.find_element(By.ID, 'game') # game screen
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


def detect_game_state() -> str:
    try:
        toolbar = driver.find_element(By.CLASS_NAME, 'game-toolbar')
        if toolbar.is_displayed():
            return 'drawing'
    except NoSuchElementException:
        pass

    try:
        # #game-canvas > .overlay-content. but it is never hidden - its hidden when "top: -100%" and shown when "top: 0%"
        overlay = driver.find_element(By.ID, 'game-canvas').find_element(By.CLASS_NAME, 'overlay-content')
        if 'top: 0' in overlay.get_attribute('style'):
            return 'waiting_for_round'
    except NoSuchElementException:
        pass

    try:
        # #game-players > .players-list > .player [.guessed] > .player-info > .player-name [.me]
        # my_player if it has the class .me
        # guessed if the grandparent has the class .guessed
        my_player = driver.find_element(By.ID, 'game-players').find_element(By.CLASS_NAME, 'players-list').find_element(By.CLASS_NAME, 'me')

        if 'guessed' in my_player.find_element(By.XPATH, '..').find_element(By.XPATH, '..').get_attribute('class'):
            return 'guessed'
    except NoSuchElementException:
        pass
    
    return 'guessing'


def generate_regex(word_hint) -> str:
    return '^' + ''.join(['\\w' if char == '_' else '\\W' if char == ' ' else char for char in word_hint]) + '$'


def get_word_hint() -> str:
    # #game-word > .hints > .container > many .hint elements - the ones with the class 'uncover' are the ones that are uncovered
    word_hint = ''

    parent = driver.find_element(By.ID, 'game-word')
    hint_container = parent.find_element(By.CLASS_NAME, 'hints').find_element(By.CLASS_NAME, 'container')
    hints = hint_container.find_elements(By.CLASS_NAME, 'hint')

    for hint in hints:
        if hint.text == '':
            word_hint += ' '
        else:
            word_hint += hint.text

        print(f'Hint: `{hint.text}`')

    return word_hint


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def make_guess() -> None:
    word_hint = get_word_hint()

    if not word_hint:
        print('No word detected on page')
        return

    # #game > #game-wrapper #game-chat > .chat-container > form > input
    guess_input = driver.find_element(By.ID, 'game-wrapper').find_element(By.ID, 'game-chat').find_element(By.CLASS_NAME, 'chat-container').find_element(By.TAG_NAME, 'form').find_element(By.TAG_NAME, 'input')
    
    if guess_input.get_attribute('value'):
        print('User is typing, skipping guess')
        return


    num_hints = len(re.findall('[a-z]', word_hint, re.IGNORECASE))
    regex = generate_regex(word_hint)

    possible_words = [word for word in word_list if (re.match(regex, word, flags=re.IGNORECASE)) and (word not in guessed_words)]

    if len(possible_words) == 0:
        print('No possible words found')
        return
    
    guess = random.choice(possible_words)
    guessed_words.append(guess)

    print(f'{num_hints}/2 hints. Guessing {guess}, one of {len(possible_words)} possible words. Guessed {len(guessed_words)} words so far')

    try:
        guess_input.send_keys(guess)
        guess_input.send_keys('\n')
    except ElementNotInteractableException:
        print('Guess input field is not interactable')
    
    delay = random.uniform(*GUESS_DELAY_RANGE[clamp(num_hints, 0, 2)])
    print(f'Waiting {delay} seconds...')
    sleep(delay)


def game_loop() -> None:
    while True:
        state = detect_state()
        game_state = detect_game_state()

        if state != 'game':
            break

        match game_state:
            case 'drawing' | 'waiting_for_round' | 'guessed':
                print(f'Waiting until we can guess ({game_state})')
                pass
            case 'guessing':
                make_guess()

        sleep(LOOP_UPDATE_DELAY)




def on_state_change(state: str) -> None:
    match state:
        case 'login' | 'lobby' | 'loading':
            pass
        case 'game':
            game_loop()
        case 'unknown' | 'multiple':
            pass



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Skribbl.io bot')
    parser.add_argument('-d', '--driver', required=True, help='Name of the webdriver executable')
    args = parser.parse_args()

    current_state = 'uninitialised'
    guessed_words = []
    drawing_has_started = False

    init_driver(args.driver)
    init_word_list()

    while True:
        state = detect_state()

        if state != current_state:
            print(f'Changed state from {current_state} to {state}')
            current_state = state
            on_state_change(state)

        sleep(LOOP_UPDATE_DELAY)
