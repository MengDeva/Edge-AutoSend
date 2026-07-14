import os
import sys
import time
import requests  # pyright: ignore[reportMissingModuleSource]
from pathlib import Path
from dotenv import load_dotenv

# ================== CONFIGURE THESE ==================
if getattr(sys, "frozen", False):
    if sys.platform == "darwin" and ".app/Contents/MacOS" in sys.executable:
        BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(sys.executable),
                         "..", "..", "..", "..")
        )
    else:
        BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(sys.executable), "..")
        )
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

BOT_TOKEN = os.getenv("AOW_BOT_TOKEN")
CHAT_ID = os.getenv("AOW_CHAT_ID")

WATCH_FOLDER = os.path.join(BASE_DIR, "AOW Screenshots")
POLL_SECONDS = 5
# ===================================================

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"


def parse_filename(file_path):
    filename = Path(file_path).stem
    parts = filename.split('_')
    supervisor = parts[0]
    rest = '_'.join(parts[1:]) if len(parts) > 1 else ""
    dayoff = 0
    dt_part = rest
    if '_Check-In=' in rest:
        dt_part, dayoff_str = rest.split('_Check-In=')
        try:
            dayoff = int(dayoff_str)
        except:
            dayoff = 0
    dt_list = dt_part.replace('-', ', ')
    return supervisor, dt_list, dayoff


def build_caption(supervisor, dt_list, dayoff):
    return f"{supervisor} ({dt_list})"


def send_file(file_path, log):
    supervisor, dt_list, dayoff = parse_filename(file_path)
    caption = build_caption(supervisor, dt_list, dayoff)
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID, 'caption': caption}
            response = requests.post(TELEGRAM_API_URL, files=files, data=data)
            if response.status_code == 200:
                log(f"✅ Sent (as file): {os.path.basename(file_path)}")
                return True
            else:
                log(f"❌ Failed: {os.path.basename(file_path)}")
                log(f"   Response: {response.text}")
                return False
    except Exception as e:
        log(f"❌ Error: {e}")
        return False


def get_creation_time(file_path):
    try:
        return os.stat(file_path).st_birthtime
    except AttributeError:
        return os.path.getmtime(file_path)


def _scan(folder):
    files = list(folder.glob("*.png")) + list(folder.glob("*.PNG"))
    return list(set(files))


def run(log_callback=None, stop_event=None):
    """Sends existing PNGs, then keeps watching the folder for new ones
    every POLL_SECONDS until stop_event is set (or the app closes).
    log_callback(msg) receives status lines; falls back to print()."""
    log = log_callback if log_callback else print

    log(f"📁 Checking folder: {WATCH_FOLDER}")
    folder = Path(WATCH_FOLDER)
    if not folder.exists():
        log("❌ ERROR: Folder does not exist! Please check the path.")
        return

    png_files = _scan(folder)
    log(f"📄 Found {len(png_files)} PNG files.")

    sent_files = set()
    if png_files:
        png_files.sort(key=get_creation_time)
        log("📸 Sending existing files as documents...")
        for file_path in png_files:
            send_file(file_path, log)
            sent_files.add(file_path.name)
    else:
        log("ℹ️  No PNG files found in this folder.")

    if stop_event is None:
        return  # one-shot mode, no watching

    log("⏳ Watching for new screenshots... (click the button again to stop)")
    while not stop_event.is_set():
        time.sleep(POLL_SECONDS)
        if stop_event.is_set():
            break
        current = _scan(folder)
        new = [f for f in current if f.name not in sent_files]
        if new:
            new.sort(key=get_creation_time)
            for file_path in new:
                log(f"📸 New file detected: {file_path.name}")
                send_file(file_path, log)
                sent_files.add(file_path.name)

    log("🛑 Stopped watching.")


if __name__ == "__main__":
    run()
