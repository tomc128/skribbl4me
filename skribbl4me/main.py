import json
from gui.app import App
from gui.main_window import MainWindow
from gui.skribbler_window import SkribblerWindow

from skribbler import Skribbler

if __name__ == '__main__':

    word_data_json = '../scrape4me/word_data.json'

    with open(word_data_json, 'r', encoding='utf-8') as file:
        word_data = json.load(file)
    
    word_list = [word['word'] for word in word_data['words']]

    print(f'Loaded {len(word_list)} unique words!')

    skribbler = Skribbler('../lib/webdriver/msedgedriver.exe', '../lib/autodraw/autodraw.crx', word_list)

    app = App()
    app.withdraw()

    main_window = MainWindow(skribbler, app)
    # skribbler_window = SkribblerWindow(skribbler, app) # testing only - no functionality

    app.mainloop()

    skribbler.stop_skribbling()