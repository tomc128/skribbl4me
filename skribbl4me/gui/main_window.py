import tkinter as tk
from tkinter import ttk

class MainWindow(tk.Toplevel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.protocol('WM_DELETE_WINDOW', self.master.destroy)

        self.title('Welcome to Skribbl4Me')
        self.resizable(False, False)

        self._create_widgets()
        self._place_widgets()


    def _create_widgets(self):
        self._create_heading()
        self._create_description()
        self._create_buttons()


    def _create_heading(self):
        self.heading = ttk.Label(self, text='Welcome to Skribbl4Me', style='Title.TLabel')


    def _create_description(self):
        self.description = ttk.Label(self, text='Description goes here')


    def _create_buttons(self):
        self.buttons = ttk.Frame(self)
        self.new_game_button = ttk.Button(self.buttons, text='New Game')
        self.load_game_button = ttk.Button(self.buttons, text='Load Game')
        self.settings_button = ttk.Button(self.buttons, text='Settings')
        self.exit_button = ttk.Button(self.buttons, text='Exit')


    def _place_widgets(self):
        self.heading.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, pady=10)
        self.description.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=10)
        self.buttons.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=10)
        self.new_game_button.grid(row=0, column=0, sticky=tk.NSEW, padx=10)
        self.load_game_button.grid(row=0, column=1, sticky=tk.NSEW, padx=10)
        self.settings_button.grid(row=0, column=2, sticky=tk.NSEW, padx=10)
        self.exit_button.grid(row=0, column=3, sticky=tk.NSEW, padx=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.buttons.columnconfigure(0, weight=1)
        self.buttons.columnconfigure(1, weight=1)
        self.buttons.columnconfigure(2, weight=1)
        self.buttons.columnconfigure(3, weight=1)