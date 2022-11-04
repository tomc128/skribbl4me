import argparse
import random
import re
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LOOP_UPDATE_DELAY = 0.5
GUESS_DELAY_RANGE = [(4, 8), (3, 6), (1, 2)]


def init_driver(driver_executable: str) -> None:
    global driver

    options = Options()
    options.add_extension('extension.crx')
    driver = webdriver.Edge(executable_path=f'./{driver_executable}', options=options)

    driver.get('https://skribbl.io/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'screenLogin')))
    assert 'skribbl' in driver.title

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'cmpbntyestxt')))
    try:
        consent_button = driver.find_element(By.ID, 'cmpbntyestxt')
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
    screens['login'] = driver.find_element(By.ID, 'screenLogin') # initial login screen
    screens['lobby'] = driver.find_element(By.ID, 'screenLobby') # custom lobby screen
    screens['loading']= driver.find_element(By.ID, 'screenLoading') # loading screen
    screens['browser'] = driver.find_element(By.ID, 'screenBrowser') # ? unknown screen
    screens['game'] = driver.find_element(By.ID, 'screenGame') # game screen
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
        toolbar = driver.find_element(By.CLASS_NAME, 'containerToolbar')
        if toolbar.is_displayed():
            return 'drawing'
    except NoSuchElementException:
        pass

    try:
        overlay = driver.find_element(By.ID, 'overlay')
        if overlay.is_displayed():
            return 'waiting_for_round'
    except NoSuchElementException:
        pass

    try:
        my_player = driver.find_element(By.ID, 'containerGamePlayers').find_element(By.XPATH, '//div[contains(text(), "(You)")]/../..')
        if 'guessedWord' in my_player.get_attribute('class'):
            return 'guessed'
    except NoSuchElementException:
        pass
    
    return 'guessing'


def generate_regex(word_hint) -> str:
    return '^' + ''.join(['\\w' if char == '_' else '\\W' if char == ' ' else char for char in word_hint]) + '$'


def get_word_hint() -> str:
    return driver.find_element(By.ID, 'currentWord').text


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def make_guess() -> None:
    word_hint = get_word_hint()

    if not word_hint:
        print('No word detected on page')
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

    guess_input = driver.find_element(By.ID, 'inputChat')
    guess_input.send_keys(guess)
    guess_input.send_keys('\n')
    
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
            case 'drawing':
                pass
            case 'waiting_for_round':
                pass
            case 'guessed':
                pass
            case 'guessing':
                make_guess()

        sleep(LOOP_UPDATE_DELAY)




def on_state_change(state: str) -> None:
    match state:
        case 'login':
            pass
        case 'lobby':
            pass
        case 'loading':
            pass
        case 'browser':
            pass
        case 'game':
            game_loop()
        case 'unknown':
            pass
        case 'multiple':
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
