"""
Deva Tools - Tkinter GUI
Buttons call checkinMe.run(), timelines.run(), aow.run() directly (no
subprocess), so this works correctly both bundled on Mac (py2app) and
Windows (PyInstaller).

Folder layout expected next to this script / the built app:
    Deva Tools.exe (or .app)
    checkinMe.py
    timelines.py
    aow.py
    CheckinMe Screenshots/
    Timelines Screenshots/
    AOW Screenshots/
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Folder the exe/app lives in when bundled, otherwise this script's folder
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# For PyInstaller onefile: bundled .py modules extract to sys._MEIPASS,
# so Python needs that on its import path to find checkinMe/timelines/aow.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, BASE_DIR)

import checkinMe   # noqa: E402
import timelines   # noqa: E402
import aow         # noqa: E402

WINDOW_TITLE = "Deva Tools"

BUTTONS = [
    {"label": "Send CheckInMe", "func": checkinMe.run},
    {"label": "Send Timelines", "func": timelines.run},
    {"label": "Send AOW", "func": aow.run},
]


def log(msg):
    log_box.configure(state="normal")
    log_box.insert(tk.END, str(msg) + "\n")
    log_box.see(tk.END)
    log_box.configure(state="disabled")


def run_task(func, label):
    log(f"Running: {label} ...")

    def worker():
        try:
            func(log_callback=log)
            log(f"'{label}' finished.\n")
        except Exception as e:
            log(f"Failed to run '{label}': {e}\n")
            messagebox.showerror("Error", str(e))

    threading.Thread(target=worker, daemon=True).start()


def quit_app():
    root.destroy()


# ---- UI ----
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry("460x400")
root.resizable(False, False)

tk.Label(root, text=WINDOW_TITLE, font=(
    "Helvetica", 16, "bold")).pack(pady=(15, 10))

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

for btn in BUTTONS:
    tk.Button(
        btn_frame,
        text=btn["label"],
        width=28,
        command=lambda f=btn["func"], l=btn["label"]: run_task(f, l),
    ).pack(pady=5)

tk.Label(root, text="Log:", anchor="w").pack(fill="x", padx=15, pady=(15, 0))
log_box = scrolledtext.ScrolledText(
    root, height=10, state="disabled", wrap="word")
log_box.pack(fill="both", padx=15, pady=5, expand=True)

tk.Button(root, text="Quit", width=15, bg="#d9534f",
          fg="white", command=quit_app).pack(pady=10)

root.mainloop()
