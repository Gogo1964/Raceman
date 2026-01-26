# Source - https://stackoverflow.com/a
# Posted by Bryan Oakley, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-11, License - CC BY-SA 4.0

import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3

class StartSeqPage(tk.Frame):

    def __init__(self, parent, controller, return_to="ModeSelPage"):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.return_to = return_to
        # Canvas for drawing circles
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.cols = 5
        self.rows = 2
        self.radius = 60
        self.spacing_x = 160
        self.spacing_y = 160


    def start_sequence(self):
        self.start_x = (self.winfo_width() - (self.cols - 1) * self.spacing_x) // 2
        self.start_y = (self.winfo_height() - (self.rows - 1) * self.spacing_y) // 2
        self.circles = []  # store (outline_id, fill_id)
        # Draw empty red circles
        for r in range(self.rows):
            for c in range(self.cols):
                cx = self.start_x + c * self.spacing_x
                cy = self.start_y + r * self.spacing_y

                outline = self.canvas.create_oval(
                    cx - self.radius, cy - self.radius,
                    cx + self.radius, cy + self.radius,
                    outline="red", width=2, fill=""
                )
                self.circles.append(outline)

        # Start fill animation
        self.current_col = 0
        self.after(1000, self.fill_next_column)

    def fill_next_column(self):
        if self.current_col < self.cols:
            for r in range(self.rows):
                index = r * self.cols + self.current_col
                self.canvas.itemconfig(self.circles[index], fill="red")

            self.current_col += 1
            self.after(1000, self.fill_next_column)
        else:
            self.canvas.delete("all")
            self.controller.show_frame(self.return_to)

