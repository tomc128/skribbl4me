from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def init() -> None:
    global driver

    options = Options()
    options.add_extension('extension.crx')
    driver = webdriver.Edge(executable_path='./msedgedriver.exe', options=options)

    driver.get('https://skribbl.io/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'screenLogin')))
    assert 'skribbl' in driver.title

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'cmpbntyestxt')))
    try:
        consent_button = driver.find_element(By.ID, 'cmpbntyestxt')
        consent_button.click()
    except NoSuchElementException:
        pass


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
                pass

        sleep(0.5)




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

    current_state = 'uninitialised'
    init()

    while True:
        state = detect_state()

        if state != current_state:
            print(f'Changed state from {current_state} to {state}')
            current_state = state
            on_state_change(state)

        sleep(0.5)
