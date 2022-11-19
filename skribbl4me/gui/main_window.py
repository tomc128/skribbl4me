import tkinter as tk
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
        
        self.init_driver_button = ttk.Button(self.buttons, text='Initialize Driver', command=self._on_init_driver_button_click)
        self.launch_skribbler_button = ttk.Button(self.buttons, text='Launch Skribbler', state=tk.DISABLED, command=self._on_launch_skribbler_button_click)


    def _place_widgets(self):
        self.heading.grid(row=0, column=0, sticky=tk.NSEW)
        self.description.grid(row=1, column=0, **ELEMENT_PADDING, sticky=tk.NSEW)
        self.buttons.grid(row=2, column=0,  **ELEMENT_PADDING, sticky=tk.NSEW)
        
        self.init_driver_button.grid(row=0, column=0, **ELEMENT_PADDING, sticky=tk.NSEW)
        self.launch_skribbler_button.grid(row=0, column=1, **ELEMENT_PADDING, sticky=tk.NSEW)

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
    

    def _on_init_driver_button_click(self):
        if self.skribbler.driver_is_initialised and self.skribbler.website_is_loaded:
            return
        
        self.skribbler.init_driver()
        self.skribbler.load_website()

        self.launch_skribbler_button['state'] = tk.NORMAL


    def _on_launch_skribbler_button_click(self):
        SkribblerWindow(self.skribbler, master=self.master)
        self.destroy()

