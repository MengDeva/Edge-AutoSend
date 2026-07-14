import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, BASE_DIR)

import checkinMe   # noqa: E402
import timelines   # noqa: E402
import aow         # noqa: E402

WINDOW_TITLE = "Deva Tools"

TASKS = [
    {"label": "CheckInMe", "func": checkinMe.run},
    {"label": "Timelines", "func": timelines.run},
    {"label": "AOW", "func": aow.run},
]

# Runtime state per task: stop_event + button widget
for t in TASKS:
    t["stop_event"] = None
    t["button"] = None


def log(msg):
    log_box.configure(state="normal")
    log_box.insert(tk.END, str(msg) + "\n")
    log_box.see(tk.END)
    log_box.configure(state="disabled")


def toggle_task(task):
    if task["stop_event"] is not None:
        # Currently running -> stop it
        task["stop_event"].set()
        task["stop_event"] = None
        task["button"].config(text=f"Send {task['label']}")
        log(f"Stopping '{task['label']}' watcher...")
        return

    # Not running -> start it
    stop_event = threading.Event()
    task["stop_event"] = stop_event
    task["button"].config(text=f"Stop {task['label']}")
    log(f"Starting '{task['label']}' ...")

    def worker():
        try:
            task["func"](log_callback=log, stop_event=stop_event)
        except Exception as e:
            log(f"Failed to run '{task['label']}': {e}\n")
            messagebox.showerror("Error", str(e))
        finally:
            # If loop ended on its own (shouldn't normally happen), reset UI
            if task["stop_event"] is stop_event:
                task["stop_event"] = None
                task["button"].config(text=f"Send {task['label']}")

    threading.Thread(target=worker, daemon=True).start()


def quit_app():
    for t in TASKS:
        if t["stop_event"] is not None:
            t["stop_event"].set()
    root.destroy()


def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


# ---- UI ----
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry("600x760")
center_window(root)
root.resizable(False, False)

tk.Label(root, text="Hey There,", font=(
    "Helvetica", 16, "bold")).pack(pady=(15, 10))

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

for task in TASKS:
    b = tk.Button(
        btn_frame,
        text=f"Send {task['label']}",
        height=2,
        width=28,
        command=lambda t=task: toggle_task(t),
    )
    b.pack(pady=5)
    task["button"] = b

tk.Label(root, text="Log:", anchor="w").pack(fill="x", padx=15, pady=(15, 0))
log_box = scrolledtext.ScrolledText(
    root, height=10, state="disabled", wrap="word")
log_box.pack(fill="both", padx=15, pady=5, expand=True)

tk.Button(root, text="Quit", width=15, bg="#d9534f",
          fg="black", command=quit_app).pack(pady=10)

root.protocol("WM_DELETE_WINDOW", quit_app)
root.mainloop()
