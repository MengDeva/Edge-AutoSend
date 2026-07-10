import os
import sys
import requests  # pyright: ignore[reportMissingModuleSource]
from pathlib import Path
from datetime import datetime

# ================== CONFIGURE THESE ==================
BOT_TOKEN = "8894808503:AAEnWdEUKr7m4hLUTFMIR9qivDR_nfUhSHk"
CHAT_ID = "745710033"

# Use the folder next to the .exe/.app when bundled, otherwise next to this script
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WATCH_FOLDER = os.path.join(BASE_DIR, "CheckinMe Screenshots")
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
    date_str = datetime.now().strftime('%d/%m/%Y')
    return (
        f"Date: {date_str}\n"
        f"=> ដេប៉ូ៖ {dt_list}\n"
        f"-ចំនួននាក់ដែលបាន Check-In ថ្ងៃនេះ: {dayoff} នាក់"
    )


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


def run(log_callback=None):
    """Main entry point called by the GUI. log_callback(msg) receives status
    lines; falls back to print() if this script is run standalone."""
    log = log_callback if log_callback else print

    log(f"📁 Checking folder: {WATCH_FOLDER}")

    folder = Path(WATCH_FOLDER)
    if not folder.exists():
        log("❌ ERROR: Folder does not exist! Please check the path.")
        return

    png_files = list(folder.glob("*.png")) + list(folder.glob("*.PNG"))
    png_files = list(set(png_files))

    log(f"📄 Found {len(png_files)} PNG files.")

    if png_files:
        png_files.sort(key=get_creation_time)
        log("📸 Sending existing files as documents...")
        for file_path in png_files:
            send_file(file_path, log)
    else:
        log("ℹ️  No PNG files found in this folder.")


if __name__ == "__main__":
    run()
