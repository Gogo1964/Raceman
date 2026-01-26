# Source - https://stackoverflow.com/a
# Posted by Bryan Oakley, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-11, License - CC BY-SA 4.0
import sys
sys.path.append('./pages')

import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3
from mode_sel import ModeSelPage
from startseq import StartSeqPage
from config import ConfigPage 
from lap_race import LapRacePage
from time_race import TimeRacePage
from training import TrainingPage

class RacerBoyApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("800x480")
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.title("RacerBoy")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ModeSelPage, TrainingPage, StartSeqPage, ConfigPage, LapRacePage, TimeRacePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ModeSelPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.start_sequence() if page_name == "StartSeqPage" else None
        frame.tkraise()

if __name__ == "__main__":
    app = RacerBoyApp()
    app.mainloop()
