# Source - https://stackoverflow.com/a
# Posted by Bryan Oakley, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-11, License - CC BY-SA 4.0

import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3

class ConfigPage(tk.Frame):

    def __init__(self, parent, controller, return_to="ModeSelPage"):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is the config page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Back to prev page",
                           command=lambda: controller.show_frame(return_to))
        button.pack()

