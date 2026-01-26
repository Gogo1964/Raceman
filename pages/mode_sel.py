# Source - https://stackoverflow.com/a
# Posted by Bryan Oakley, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-11, License - CC BY-SA 4.0

import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3

class ModeSelPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Select Mode", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Training Mode",
                            command=lambda: controller.show_frame("TrainingPage"))
        button2 = tk.Button(self, text="Time Race Mode",
                            command=lambda: controller.show_frame("TimeRacePage"))
        button3 = tk.Button(self, text="Lap Race Mode",
                            command=lambda: controller.show_frame("LapRacePage"))
        button1.pack()
        button2.pack()
        button3.pack()

