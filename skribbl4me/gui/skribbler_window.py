import tkinter as tk
from tkinter import ttk
from gui.styles import *

from skribbler import Skribbler

class SkribblerWindow(tk.Toplevel):

    def __init__(self, skribbler: Skribbler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.skribbler = skribbler

        self.protocol('WM_DELETE_WINDOW', self.master.destroy)

        self.title('skribbl4me : Skribbler')

        self._create_widgets()
        self._place_widgets()
    

    def _create_widgets(self):
        self._create_wrapper()
    
    
    def _create_wrapper(self):
        self.wrapper = ttk.Frame(self)
        self.wrapper.grid(row=0, column=0, sticky=tk.NSEW, **WRAPPER_PADDING)
        
        self.wrapper.columnconfigure(0, weight=1)
        self.wrapper.rowconfigure(0, weight=1)
    

    def _place_widgets(self):
        self.wrapper.columnconfigure(0, weight=1)
        self.wrapper.rowconfigure(0, weight=1)
        self.wrapper.rowconfigure(1, weight=1)
        self.wrapper.rowconfigure(2, weight=1)

