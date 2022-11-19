from gui.app import App
from gui.main_window import MainWindow

from skribbler import Skribbler

if __name__ == '__main__':
    skribbler = Skribbler('../lib/webdriver/msedgedriver.exe', '../lib/autodraw/autodraw.crx', ['hello', 'world'])

    app = App()
    app.withdraw()

    main_window = MainWindow(skribbler, app)

    app.mainloop()

    skribbler.stop_skribbling()