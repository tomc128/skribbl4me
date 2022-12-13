import tkinter as tk
from tkinter import ttk
from gui.styles import *

from skribbler import Skribbler

class SkribblerWindow(tk.Toplevel):

    
    UI_UPDATE_INTERVAL = 100


    def __init__(self, skribbler: Skribbler, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry('1200x800')
        
        self.skribbler = skribbler

        self.protocol('WM_DELETE_WINDOW', self.master.destroy)

        self.title('skribbl4me : Skribbler')

        self._create_widgets()

        self.after(0, self._update_ui)
    

    def _on_close(self):
        self.skribbler.stop_skribbling()
        self.master.destroy()


    def _create_widgets(self):
        self._create_wrapper()

        style = ttk.Style(self.wrapper)
        # For debugging:
        # style.configure('GameInfo.TFrame', background='red')
        # style.configure('PlayerInfo.TFrame', background='green')
        # style.configure('PossibleWords.TFrame', background='blue')
        # style.configure('Guesses.TFrame', background='yellow')
        # style.configure('Actions.TFrame', background='pink')
        style.configure('GameInfo.TFrame')
        style.configure('PlayerInfo.TFrame')
        style.configure('PossibleWords.TFrame')
        style.configure('Guesses.TFrame')
        style.configure('Actions.TFrame')

        style.configure('TLabel', font=LABEL_FONT)


        # split wrapper into 2 rows, the first containing a frame containing game information, the second
        # split into 3 columns, the first containg a frame containing player information, the second
        # containing a frame containing possible words, and the third containing a frame containing
        # a label with all previous guesses, and a text field for the user to enter their guess

        self._create_game_info_frame()
        self._create_player_info_frame()
        self._create_possible_words_frame()
        self._create_guesses_frame()
        self._create_actions_frame()

        # make wrapper fill the entire window
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
    
    
    def _create_wrapper(self):
        
        self.wrapper = ttk.Frame(self)
        self.wrapper.grid(row=0, column=0, sticky=tk.NSEW, **WRAPPER_PADDING)
        
        self.wrapper.columnconfigure(0, minsize=200)
        self.wrapper.columnconfigure(1, weight=1)
        self.wrapper.columnconfigure(2, weight=1)

        self.wrapper.rowconfigure(0, minsize=20)
        self.wrapper.rowconfigure(1, weight=1)
        self.wrapper.rowconfigure(2, minsize=20)

        
    def _create_game_info_frame(self):
        self.game_info_frame = ttk.Frame(self.wrapper, style='GameInfo.TFrame')
        self.game_info_frame.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.game_info_frame.columnconfigure(0, weight=1)
        self.game_info_frame.rowconfigure(0, weight=1)

        self.game_info_label = ttk.Label(self.game_info_frame, text='Game Info:')
        self.game_info_label.grid(row=0, column=0, sticky=tk.NSEW, **ELEMENT_PADDING)


    def _create_player_info_frame(self):
        self.player_info_frame = ttk.Frame(self.wrapper, style='PlayerInfo.TFrame')
        self.player_info_frame.grid(row=1, column=0, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.player_info_frame.columnconfigure(0, weight=1)
        self.player_info_frame.rowconfigure(0, weight=1)

        self.player_info_label = ttk.Label(self.player_info_frame, text='Player Info:')
        self.player_info_label.grid(row=0, column=0, sticky=tk.NSEW, **ELEMENT_PADDING)


    def _create_possible_words_frame(self):
        self.possible_words_frame = ttk.Frame(self.wrapper, style='PossibleWords.TFrame')
        self.possible_words_frame.grid(row=1, column=1, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.possible_words_frame.columnconfigure(0, weight=1)
        self.possible_words_frame.rowconfigure(0, weight=1)

        self.possible_words_label = ttk.Label(self.possible_words_frame, text='Possible Words:')
        self.possible_words_label.grid(row=0, column=0, sticky=tk.NSEW, **ELEMENT_PADDING)

    
    def _create_guesses_frame(self):
        self.guesses_frame = ttk.Frame(self.wrapper, style='Guesses.TFrame')
        self.guesses_frame.grid(row=1, column=2, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.guesses_frame.columnconfigure(0, weight=1)
        
        self.guesses_frame.rowconfigure(0)
        self.guesses_frame.rowconfigure(1, weight=1)
        self.guesses_frame.rowconfigure(2)

        self.guesses_label = ttk.Label(self.guesses_frame, text='Guesses:')
        self.guesses_label.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.guesses_text = ttk.Entry(self.guesses_frame, width=30, state='readonly')
        self.guesses_text.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.guesses_entry = ttk.Entry(self.guesses_frame)
        self.guesses_entry.grid(row=2, column=0, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.guesses_guess_button = ttk.Button(self.guesses_frame, text='Guess', command=self._on_guesses_guess_button_click)
        self.guesses_guess_button.grid(row=2, column=1, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.guesses_entry.bind('<Return>', self._on_guesses_entry_return)
    

    def _create_actions_frame(self):
        self.actions_frame = ttk.Frame(self.wrapper, style='Actions.TFrame')
        self.actions_frame.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.actions_frame.columnconfigure(0, weight=1)
        self.actions_frame.rowconfigure(0, weight=1)

        self.start_button = ttk.Button(self.actions_frame, text='Start', command=self._on_start_button_click)
        self.start_button.grid(row=0, column=0, sticky=tk.NSEW, **ELEMENT_PADDING)

        self.stop_button = ttk.Button(self.actions_frame, text='Stop', command=self._on_stop_button_click)
        self.stop_button.grid(row=0, column=1, sticky=tk.NSEW, **ELEMENT_PADDING)


    def _on_guesses_entry_return(self, _):
        self.skribbler.make_guess(self.guesses_entry.get())
        self.guesses_entry.delete(0, tk.END)
    
    def _on_guesses_guess_button_click(self):
        self.skribbler.make_guess(self.guesses_entry.get())
        self.guesses_entry.delete(0, tk.END)

    def _on_start_button_click(self):
        self.skribbler.start_skribbling()

    def _on_stop_button_click(self):
        self.skribbler.stop_skribbling()
    

    def _update_ui(self):
        if self.skribbler.skribbling_is_enabled:
            self.start_button['state'] = 'disabled'
            self.stop_button['state'] = 'normal'
        else:
            self.start_button['state'] = 'normal'
            self.stop_button['state'] = 'disabled'

        self.after(self.UI_UPDATE_INTERVAL, self._update_ui)

