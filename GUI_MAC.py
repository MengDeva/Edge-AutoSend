import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

# =========================================================
# EDIT THIS SECTION — set up your own buttons here
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("LANG", "en_US.UTF-8")

BUTTONS = [
    {
        "label": "Send Timelines",
        "command": [sys.executable, os.path.join(BASE_DIR, "timelines.py")],
    },
    {
        "label": "Send CheckInMe",
        "command": [sys.executable, os.path.join(BASE_DIR, "CheckinMe.py")],
    },
    {
        "label": "Send AOW Reports",
        "command": [sys.executable, os.path.join(BASE_DIR, "aow.py")],
    },
]

WINDOW_TITLE = "Deva Tools"

# =========================================================
# You shouldn't need to touch anything below this line
# =========================================================


def log(msg):
    log_box.configure(state="normal")
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    log_box.configure(state="disabled")


def run_command(cmd, label):
    log(f"Running: {label} ...")

    def worker():
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.stdout:
                log(result.stdout)
            if result.stderr:
                log(result.stderr)
            if result.returncode == 0:
                log(f"'{label}' finished successfully.\n")
            else:
                log(f"'{label}' exited with error code {result.returncode}\n")
                messagebox.showerror(
                    "Error", f"'{label}' hit an error. Check the log.")
        except Exception as e:
            log(f"Failed to run '{label}': {e}\n")
            messagebox.showerror("Error", str(e))

    threading.Thread(target=worker, daemon=True).start()


def quit_app():
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
root.geometry("560x500")
center_window(root)
root.resizable(False, False)

tk.Label(root, text="Hello, Guys", font=(
    "Helvetica", 16, "bold")).pack(pady=(15, 10))

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

for btn in BUTTONS:
    tk.Button(
        btn_frame,
        text=btn["label"],
        width=25,
        height=2,
        bd=0,
        highlightbackground="#7DC9E7",
        highlightthickness=3,
        command=lambda c=btn["command"], l=btn["label"]: run_command(c, l),
    ).pack(pady=5)

tk.Label(root, text="Log:", anchor="w").pack(fill="x", padx=15, pady=(15, 0))
log_box = scrolledtext.ScrolledText(
    root, height=10, state="disabled", wrap="word")
log_box.pack(fill="both", padx=15, pady=5, expand=True)

tk.Button(root, text="Quit", width=15, bg="#d9534f",
          fg="black", command=quit_app).pack(pady=10)

root.mainloop()
