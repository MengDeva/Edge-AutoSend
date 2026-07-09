import time
import os
import requests  # pyright: ignore[reportMissingModuleSource]
from pathlib import Path
from datetime import datetime

# ================== CONFIGURE THESE ==================
# e.g., "123456:ABC-DEF1234ghIkl"
BOT_TOKEN = "8894808503:AAEnWdEUKr7m4hLUTFMIR9qivDR_nfUhSHk"
CHAT_ID = "745710033"              # e.g., "123456789"
# Your screenshot folder
WATCH_FOLDER = "/CheckinMe Screenshots"
DateTime = datetime.now()
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
    return f"Date: {DateTime.strftime("%d/%m/%Y")}\n=> ដេប៉ូ៖ {dt_list}\n-ចំនួននាក់ដែលបាន Check-In ថ្ងៃនេះ: {dayoff} នាក់"


def send_file(file_path):
    supervisor, dt_list, dayoff = parse_filename(file_path)
    caption = build_caption(supervisor, dt_list, dayoff)
    try:
        with open(file_path, 'rb') as f:
            # --- Send as document (file) instead of photo ---
            files = {'document': f}   # 'document' field, not 'photo'
            data = {'chat_id': CHAT_ID, 'caption': caption}
            response = requests.post(TELEGRAM_API_URL, files=files, data=data)
            if response.status_code == 200:
                print(f"✅ Sent (as file): {os.path.basename(file_path)}")
                return True
            else:
                print(f"❌ Failed: {os.path.basename(file_path)}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_creation_time(file_path):
    try:
        return os.stat(file_path).st_birthtime
    except AttributeError:
        return os.path.getmtime(file_path)


def main():
    print(f"📁 Checking folder: {WATCH_FOLDER}")

    # Check if folder exists
    folder = Path(WATCH_FOLDER)
    if not folder.exists():
        print(f"❌ ERROR: Folder does not exist! Please check the path.")
        return

    # Find all PNG files (case-insensitive)
    png_files = list(folder.glob("*.png")) + list(folder.glob("*.PNG"))
    png_files = list(set(png_files))

    print(f"📄 Found {len(png_files)} PNG files.")

    if png_files:
        png_files.sort(key=get_creation_time)
        print("📸 Sending existing files as documents...")
        for file_path in png_files:
            send_file(file_path)
    else:
        print("ℹ️  No PNG files found in this folder.")

    # --- Monitor for new files ---
    # sent_files = set(f.name for f in png_files)
    # print("⏳ Monitoring for new files...")
    # while True:
    #     time.sleep(5)
    #     current = set(f.name for f in folder.glob("*.png")
    #                   ) | set(f.name for f in folder.glob("*.PNG"))
    #     new = current - sent_files
    #     if new:
    #         new_paths = [folder / name for name in new]
    #         new_paths.sort(key=get_creation_time)
    #         for p in new_paths:
    #             print(f"📸 New file detected: {p.name}")
    #             send_file(p)
    #     sent_files = current


if __name__ == "__main__":
    main()
