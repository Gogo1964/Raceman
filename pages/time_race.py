# Source - https://stackoverflow.com/a
# Posted by Bryan Oakley, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-11, License - CC BY-SA 4.0

import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3
from startseq import StartSeqPage

class TimeRacePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is the time race page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Back to Mode Selection",
                           command=lambda: controller.show_frame("ModeSelPage"))
        buttonStart = tk.Button(self, text="Start Race",
                           command=lambda: controller.show_frame("StartSeqPage"))
        button.pack()
        buttonStart.pack()

