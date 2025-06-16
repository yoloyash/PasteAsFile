# clip2file_tray.py

import sys
import tempfile, subprocess, pathlib, keyboard, pyperclip, atexit, os, threading
from PIL import Image
import pystray

from spinner import show_spinner

TMP_FILES = []

def copy_text_as_file():
    data = pyperclip.paste()
    if not data.strip():
        return
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp.write(data.encode()); tmp.close()
    TMP_FILES.append(tmp.name)
    subprocess.run(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden",
         "Set-Clipboard", "-Path", str(pathlib.Path(tmp.name))],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    show_spinner()  

def on_exit(icon, _item):
    # clean up files & hooks, stop tray, then fully exit
    for f in TMP_FILES:
        try: os.unlink(f)
        except: pass
    keyboard.unhook_all()
    icon.stop()
    os._exit(0)      # ← kill the whole process immediately

def setup_tray():
    base_path = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(__file__)
    icon_path = os.path.join(base_path, "icon.ico")
    image = Image.open(icon_path)
    menu  = pystray.Menu(pystray.MenuItem("Exit", on_exit))
    icon  = pystray.Icon("Paste as File", image, "Paste as File", menu)
    threading.Thread(target=icon.run, daemon=True).start()
    return icon

if __name__ == "__main__":
    atexit.register(lambda: [os.unlink(f) for f in TMP_FILES if os.path.exists(f)])
    icon = setup_tray()
    keyboard.add_hotkey("ctrl+alt+v", copy_text_as_file, suppress=False)
    keyboard.wait()          # still blocks, but on_exit will now kill this too

# pyinstaller clip2file_tray.py --onefile --noconsole --add-data "icon.ico;." --add-data "spinner.gif;."
# watchmedo auto-restart --patterns="*.py" --recursive -- python clip2file_tray.py