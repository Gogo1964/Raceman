#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rundenzähler für 2‑spurige Autorennbahn
Ziel: Raspberry Pi 3, Python3, RPi.GPIO, Tkinter
"""

import time
import threading
import json
import tkinter as tk
from tkinter import simpledialog, messagebox

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

# ---------------- GPIO Konfiguration ----------------
GPIO_LANE1_IN = 17
GPIO_LANE2_IN = 18
GPIO_LANE1_BWD = 23
GPIO_LANE1_FWD = 24
GPIO_LANE2_BWD = 22
GPIO_LANE2_FWD = 27

# ---------------- Einstellungen ----------------
DEBOUNCE_SECONDS = 1.0
CONFIG_FILE = "race_config.json"
DEFAULT_LAPS = 10
DEFAULT_TIME_SECS = 300
DEF_MINIMUM_LAP_TIME_MS = 6000
DEF_MAXIMUM_LAP_TIME_MS = 30000
COUNT_SAVED_LAPS = 5

# ---------------- Hilfsfunktionen ----------------
def current_millis():
    return int(time.time() * 1000)

# ---------------- Rennlogik ----------------
class RaceController:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
        self.reset()
        self.load_config()

    def reset_stats(self):
        self.reset()
        self.ui_callback("update")  

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
                self.mode = cfg.get("mode", "laps")
                self.target_laps = cfg.get("laps", DEFAULT_LAPS)
                self.target_time_secs = cfg.get("time", DEFAULT_TIME_SECS)
                self.target_heats = cfg.get("heats", 2)
                self.min_lap_time_ms = cfg.get("min_lap_time_ms", DEF_MINIMUM_LAP_TIME_MS)
                self.max_lap_time_ms = cfg.get("max_lap_time_ms", DEF_MAXIMUM_LAP_TIME_MS)
        except Exception:
            self.mode = "laps"
            self.target_laps = DEFAULT_LAPS
            self.target_time_secs = DEFAULT_TIME_SECS
            self.target_heats = 2
            self.min_lap_time_ms = DEF_MINIMUM_LAP_TIME_MS
            self.max_lap_time_ms = DEF_MAXIMUM_LAP_TIME_MS


    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "mode": self.mode,
                "laps": self.target_laps,
                "time_per_heat": self.target_time_secs,
                "heats": self.target_heats,
                "min_lap_time_ms": self.min_lap_time_ms,
                "max_lap_time_ms": self.max_lap_time_ms
            }, f)

    def reset(self):
        self.laps = [0, 0]
        self.trigger_events = [0, 0]
        self.last_trigger = [0, 0]
        self.lap_times = [[], []]
        self.last_lap_timestamp = [None, None]
        self.best_lap_times = [None, None]
        self.best_lap = [None, None]
        self.avg_lap_times = [None, None]
        self.stop_pending = [False, False]
        self.race_running = False
        self.remaining_heats = 0
        self.ignore_first_pass = [False, False]
        self.lane_io_in = [GPIO_LANE1_IN, GPIO_LANE2_IN]

    def start_heat(self):
        self.remaining_heats -= 1
        # Swap lanes for next heat
        self.laps = [self.laps[1], self.laps[0]]
        self.lap_times = [self.lap_times[1], self.lap_times[0]]
        self.best_lap_times = [self.best_lap_times[1], self.best_lap_times[0]]
        self.best_lap = [self.best_lap[1], self.best_lap[0]]
        self.avg_lap_times = [self.avg_lap_times[1], self.avg_lap_times[0]]
        self.ui_callback("update")
        if self.mode == "time":
            threading.Thread(target=self._time_race_monitor, daemon=True).start()

    def start_race(self):
        self.reset()
        self.race_running = True
        self.remaining_heats = self.target_heats
        self.laps = [0, 0]
        self.add_travel = [0, 0]
        self.lap_times = [[], []]
        self.best_lap_times = [None, None]
        self.best_lap = [None, None]
        self.avg_lap_times = [None, None]
        self.ignore_first_pass = [True, True]
        self.start_heat()

    def stop_heat(self):
        if self.race_running:
            print("Heat finished")
            self.ui_callback("power_off")
            if (self.remaining_heats > 0):
                messagebox.showinfo("Heat finished", f"Heat finished. SWAP LANES AND MOVE CARS TO START POSITION! Remaining heats: {self.remaining_heats}")
                self.start_heat()   
            else:
                self.race_running = False
                resulting_laps = [self.laps[0] + self.add_travel[0], 
                                  self.laps[1] + self.add_travel[1]]
                if (resulting_laps[0] > resulting_laps[1]):
                    winner = f"Lane 1 wins! {(resulting_laps[0] / 100):.2f} to {(resulting_laps[1] / 100):.2f}"
                elif resulting_laps[1] > resulting_laps[0]:
                    winner = f"Lane 2 wins! {(resulting_laps[1] / 100):.2f} to {(resulting_laps[0] / 100):.2f}"
                else:
                    winner = "It's a tie!"
                messagebox.showinfo("Race finished", f"All heats finished. {winner}")

    def stop_race(self):
        if self.race_running:
            self.race_running = False
            print("Race finished")
            self.ui_callback("power_off")

    def cancel_race(self):
        if self.race_running:
            self.race_running = False
            print("Race canceled")
            self.ui_callback("power_off")

    def _time_race_monitor(self):
        time.sleep(self.target_time_secs)
        if self.race_running:
            self.stop_pending[0] = True
            self.stop_pending[1] = True
            self.stop_pending_since = current_millis()

    def trigger_lane(self, lane):
        inputstate = None
        if GPIO_AVAILABLE:
            inputstate = GPIO.input(self.lane_io_in[lane])
            if inputstate == GPIO.HIGH:
                return  # Ignore if not LOW
        
        now = time.time()
        if now - self.last_trigger[lane] < DEBOUNCE_SECONDS:
            return
        self.last_trigger[lane] = now

        if self.ignore_first_pass[lane]:
            self.last_lap_timestamp[lane] = current_millis()
            self.ignore_first_pass[lane] = False
            return

        finished_lap = self.laps[lane] + 1
        print(f"Lane {lane + 1} triggered, state {inputstate}, laps {finished_lap}")

        now_ms = current_millis()

        if self.stop_pending[lane]:
            self.stop_pending[lane] = False
            if (self.last_lap_timestamp[lane] is not None
                and self.avg_lap_times[lane] is not None
                and self.stop_pending_since is not None):
                diff_ms = now_ms - self.stop_pending_since
                est_travel = (self.avg_lap_times[lane] - diff_ms) / self.avg_lap_times[lane]
                if est_travel < 0:
                    est_travel = 0
                self.add_travel[lane] += est_travel              
            else:
                self.add_travel[lane] += 0

            if lane == 0:
                self.ui_callback("power_off_1")
            elif lane == 1:
                self.ui_callback("power_off_2")
            if not any(self.stop_pending):
                if self.remaining_heats > 0:
                    self.stop_heat()
                else:
                    self.stop_race()
            return
        
        if self.last_lap_timestamp[lane] is not None:
            lap_time = now_ms - self.last_lap_timestamp[lane]
            if lap_time >= self.min_lap_time_ms and lap_time <= self.max_lap_time_ms:
                if self.best_lap_times[lane] is None or lap_time < self.best_lap_times[lane]:
                    self.best_lap_times[lane] = lap_time
                    self.best_lap[lane] = finished_lap
                if self.avg_lap_times[lane] is None:
                    self.avg_lap_times[lane] = lap_time
                else:
                    self.avg_lap_times[lane] = ((self.avg_lap_times[lane] * self.laps[lane]) 
                                                + lap_time) / finished_lap
                self.lap_times[lane].insert(0, lap_time)
                self.lap_times[lane] = self.lap_times[lane][:COUNT_SAVED_LAPS]
        self.last_lap_timestamp[lane] = now_ms
        self.laps[lane] = finished_lap
        self.ui_callback("update")

        if self.mode == "laps" and self.laps[lane] >= self.target_laps:
            self.stop_race()

# ---------------- Benutzeroberfläche ----------------
class RaceUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RaceMan")
        self.root.attributes('-fullscreen', True)
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry("%dx%d+0+0" % (w, h))

        self.controller = RaceController(self.handle_event)

        self.build_ui()
        self.bind_keys()

        if GPIO_AVAILABLE:
            self.setup_gpio()

    def build_ui(self):
        self.left = tk.Frame(self.root)
        self.right = tk.Frame(self.root)
        self.left.pack(side="left", expand=True, fill="both")
        self.right.pack(side="right", expand=True, fill="both")

        self.lap_labels = []
        self.time_labels = []
        self.extra_labels = []  # store the new labels if you need them later

        for frame in (self.left, self.right):
            # --- Top big lap label ---
            laps_big = tk.Label(frame, text="000", font=("Helvetica", 160, "bold"), fg="red")
            laps_big.pack(expand=True)
            self.lap_labels.append(laps_big)

            # --- Bottom container ---
            bottom = tk.Frame(frame)
            bottom.pack(fill="x", pady=10)

            # Configure grid so columns resize nicely
            bottom.columnconfigure(0, weight=1)
            bottom.columnconfigure(1, weight=1)

            # --- Left column: saved lap times ---
            times = []
            times_frame = tk.Frame(bottom)
            times_frame.grid(row=0, column=0, sticky="n")

            for _ in range(COUNT_SAVED_LAPS):
                lbl = tk.Label(times_frame, text="----- s", font=("Helvetica", 14))
                lbl.pack(anchor="w")
                times.append(lbl)

            self.time_labels.append(times)

            # --- Right column: two equal-sized labels ---
            extras = []
            extras_frame = tk.Frame(bottom)
            extras_frame.grid(row=0, column=1, sticky="n")

            lbl = tk.Label(
                extras_frame,
                text="----- s (---)",
                font=("Helvetica", 18, "bold"),
                width=12,   # ensures same size
                height=2,
                relief="solid",
                fg="green"
            )
            lbl.pack(pady=5)
            extras.append(lbl)

            lbl = tk.Label(
                extras_frame,
                text="Avg ----- s",
                font=("Helvetica", 18),
                width=12,   # ensures same size
                height=2,
                relief="solid",
                fg="orange"
            )
            lbl.pack(pady=5)
            extras.append(lbl)

            self.extra_labels.append(extras)


    def on_exit(self, event=None):
        """Close the Tkinter window."""
        self.root.destroy()
    
    def resize(self, event):
        print("New size is: {}x{}".format(event.width, event.height))

    def bind_keys(self):
        self.root.bind("<Shift-space>", lambda e: self.start_sequence())
        self.root.bind("<Control-r>", lambda e: self.controller.reset_stats())
        self.root.bind("R", lambda e: self.set_laps())
        self.root.bind("L", lambda e: self.set_laps())
        self.root.bind("T", lambda e: self.set_timed_race())
        self.root.bind("Z", lambda e: self.set_timed_race())
        self.root.bind("C", lambda e: self.set_lap_times())
        self.root.bind("p", lambda e: self.power_on())
        self.root.bind("P", lambda e: self.power_off())
        self.root.bind("M", lambda e: self.toggle_mode())
        self.root.bind("<Escape>", lambda e: self.controller.cancel_race())
        root.bind("<Shift-Escape>", self.on_exit)
        self.root.bind("<Configure>", self.resize)
        if not GPIO_AVAILABLE:
            self.root.bind("1", lambda e: self.controller.trigger_lane(0))
            self.root.bind("2", lambda e: self.controller.trigger_lane(1))

    def start_sequence(self):
        self.handle_event("power_off")
        def seq():
            self.show_overlay()
        threading.Thread(target=seq, daemon=True).start()

    def show_overlay(self):
        # Ensure geometry info is available
        self.root.update_idletasks()

        # Create overlay window
        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)   # No window decorations
        self.overlay.attributes("-topmost", True)

        # Match overlay position & size to root window
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.overlay.geometry(f"{w}x{h}+{x}+{y}")

        # Canvas for drawing circles
        self.canvas = tk.Canvas(self.overlay, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.cols = 5
        self.rows = 2
        self.radius = 20
        self.spacing_x = 80
        self.spacing_y = 60

        self.circles = []  # store (outline_id, fill_id)

        start_x = (w - (self.cols - 1) * self.spacing_x) // 2
        start_y = (h - (self.rows - 1) * self.spacing_y) // 2

        # Draw empty red circles
        for r in range(self.rows):
            for c in range(self.cols):
                cx = start_x + c * self.spacing_x
                cy = start_y + r * self.spacing_y

                outline = self.canvas.create_oval(
                    cx - self.radius, cy - self.radius,
                    cx + self.radius, cy + self.radius,
                    outline="red", width=2, fill=""
                )
                self.circles.append(outline)

        # Start fill animation
        self.current_col = 0
        self.overlay.after(1000, self.fill_next_column)

    def fill_next_column(self):
        if self.current_col < (self.cols - 1):
            for r in range(self.rows):
                index = r * self.cols + self.current_col
                self.canvas.itemconfig(self.circles[index], fill="red")

            self.current_col += 1
            self.overlay.after(1000, self.fill_next_column)
        else:
            for r in range(self.rows):
                index = r * self.cols + self.current_col
                self.canvas.itemconfig(self.circles[index], fill="red")
            # Close overlay after 200 ms
            self.handle_event("power_on")
            self.controller.ignore_first_pass = [True, True]
            self.controller.start_race()
            self.overlay.after(200, self.overlay.destroy)
            
    def set_laps(self):
        val = simpledialog.askinteger("Laps mode", "Count laps:", initialvalue=self.controller.target_laps)
        if val:
            self.controller.target_laps = val
            self.controller.mode = "laps"
            self.controller.save_config()

    def set_timed_race(self):
        valt = simpledialog.askinteger("Time mode", "Heat time (seconds):", initialvalue=self.controller.target_time_secs)
        valh = simpledialog.askinteger("Time mode", "Count heats:", initialvalue=self.controller.target_heats)
        if valt:
            self.controller.target_time_secs = valt
            self.controller.target_heats = valh
            self.controller.mode = "time"
            self.controller.save_config()

    def set_lap_times(self):
        val = simpledialog.askinteger("Minimum Lap Time", "Minimum lap time (milliseconds):", initialvalue=self.controller.min_lap_time_ms)
        if val:
            self.controller.min_lap_time_ms = val
            self.controller.save_config()
        val = simpledialog.askinteger("Maximum Lap Time", "Maximum lap time (milliseconds):", initialvalue=self.controller.max_lap_time_ms)
        if val:
            self.controller.max_lap_time_ms = val
            self.controller.save_config()

    def toggle_mode(self):
        self.controller.mode = "time" if self.controller.mode == "laps" else "laps"
        messagebox.showinfo("Modus", f"Current mode: {self.controller.mode}")

    def handle_event(self, event):
        if event == "update":
            for i in (0, 1):
                self.lap_labels[i].config(text=f"{(self.controller.laps[i] % 1000):03d}")
                for j in range(COUNT_SAVED_LAPS):
                    self.time_labels[i][j].config(text="----- s")
                for j, t in enumerate(self.controller.lap_times[i]):
                    self.time_labels[i][j].config(text=f"{t / 1000.0:.3f} s")
                if self.controller.best_lap_times[i] is not None:
                    self.extra_labels[i][0].config(text=f"{self.controller.best_lap_times[i] / 1000.0:.3f} s ({self.controller.best_lap[i]:03d})")
                else:
                    self.extra_labels[i][0].config(text="----- s (---)")
                if self.controller.avg_lap_times[i] is not None:
                    self.extra_labels[i][1].config(text=f"Avg {self.controller.avg_lap_times[i] / 1000.0:.3f} s")
                else:
                    self.extra_labels[i][1].config(text="Avg ----- s")
        elif event == "power_off" and GPIO_AVAILABLE:
            GPIO.output(GPIO_LANE1_FWD, GPIO.LOW)
            GPIO.output(GPIO_LANE1_BWD, GPIO.LOW)
            GPIO.output(GPIO_LANE2_FWD, GPIO.LOW)
            GPIO.output(GPIO_LANE2_BWD, GPIO.LOW)
        elif event == "power_off_1" and GPIO_AVAILABLE:
            GPIO.output(GPIO_LANE1_FWD, GPIO.LOW)
            GPIO.output(GPIO_LANE1_BWD, GPIO.LOW)
        elif event == "power_off_2" and GPIO_AVAILABLE:
            GPIO.output(GPIO_LANE2_FWD, GPIO.LOW)
            GPIO.output(GPIO_LANE2_BWD, GPIO.LOW)
        elif event == "power_on" and GPIO_AVAILABLE:
            GPIO.output(GPIO_LANE1_FWD, GPIO.HIGH)
            GPIO.output(GPIO_LANE2_FWD, GPIO.HIGH)
            GPIO.output(GPIO_LANE1_BWD, GPIO.LOW)
            GPIO.output(GPIO_LANE2_BWD, GPIO.LOW)

    def power_on(self):
        self.handle_event("power_on")

    def power_off(self):
        self.handle_event("power_off")

    # ---------------- GPIO ----------------
    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_LANE1_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(GPIO_LANE2_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(GPIO_LANE1_FWD, GPIO.OUT)
        GPIO.setup(GPIO_LANE1_BWD, GPIO.OUT)
        GPIO.setup(GPIO_LANE2_FWD, GPIO.OUT)
        GPIO.setup(GPIO_LANE2_BWD, GPIO.OUT)

        GPIO.add_event_detect(GPIO_LANE1_IN, GPIO.FALLING,
                              callback=lambda ch: self.controller.trigger_lane(0))
        GPIO.add_event_detect(GPIO_LANE2_IN, GPIO.FALLING,
                              callback=lambda ch: self.controller.trigger_lane(1))

# ---------------- Main ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = RaceUI(root)
    root.mainloop()
