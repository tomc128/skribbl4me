import tkinter as tk
from threading import Thread
from tkinter import ttk
from tkinter.font import Font

from gui.skribbler_window import SkribblerWindow
from gui.styles import *
from skribbler import Skribbler


class MainWindow(tk.Toplevel):

    def __init__(self, skribbler: Skribbler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.skribbler = skribbler

        self.protocol('WM_DELETE_WINDOW', self.master.destroy)

        self.title('skribbl4me : Main')
        self.resizable(False, False)

        self._create_widgets()
        self._place_widgets()


    def _create_widgets(self):
        self._create_wrapper()

        self._create_heading()
        self._create_description()
        self._create_buttons()


    def _create_wrapper(self):
        self.wrapper = ttk.Frame(self)
        self.wrapper.grid(row=0, column=0, sticky=tk.NSEW, **WRAPPER_PADDING)

        self.wrapper.columnconfigure(0, weight=1)
        self.wrapper.rowconfigure(0, weight=1)


    def _create_heading(self):
        self.heading = ttk.Label(self.wrapper, text='Skribbl4Me', font=TITLE_FONT)


    def _create_description(self):
        self.description = ttk.Label(self.wrapper, text='A tool to help you play Skribbl.io')


    def _create_buttons(self):
        self.buttons = ttk.Frame(self.wrapper)
        
        self.launch_button = ttk.Button(self.buttons, text='Initialise & Launch', command=self._on_button_click)


    def _place_widgets(self):
        self.heading.grid(row=0, column=0, sticky=tk.NSEW)
        self.description.grid(row=1, column=0, **ELEMENT_PADDING, sticky=tk.NSEW)
        self.buttons.grid(row=2, column=0,  **ELEMENT_PADDING, sticky=tk.NSEW)
        
        self.launch_button.grid(row=0, column=0, sticky=tk.NSEW)

        self.buttons.columnconfigure(0, weight=1)
        self.buttons.columnconfigure(1, weight=1)
        self.buttons.columnconfigure(2, weight=1)
        self.buttons.columnconfigure(3, weight=1)

        self.wrapper.columnconfigure(0, weight=1)
        self.wrapper.rowconfigure(0, weight=1)
        self.wrapper.rowconfigure(1, weight=1)
        self.wrapper.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
    

    def _on_button_click(self):
        skribbler_launch_thread = Thread(target=self._launch_skribbler)
        skribbler_launch_thread.start()

        SkribblerWindow(self.skribbler, master=self.master)
        self.destroy()


    def _launch_skribbler(self):
        if not self.skribbler.driver_is_initialised:
            self.skribbler.init_driver()
        
        if not self.skribbler.website_is_loaded:
            self.skribbler.load_website()