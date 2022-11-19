import tkinter as tk
from tkinter import ttk

from gui.styles import *

import sv_ttk



class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sv_ttk.set_theme('dark') 
        self.withdraw() # Hide the root window, only show subsequent windowse 'light') 

        style = ttk.Style(self)
        style.configure('TButton', font=BUTTON_FONT)
        style.configure('TLabel', font=LABEL_FONT)
        style.configure('Title.TLabel', font=TITLE_FONT)
