from gui.app import App
from gui.main_window import MainWindow

if __name__ == '__main__':
    app = App()
    app.withdraw()

    main_window = MainWindow(app)

    app.mainloop()