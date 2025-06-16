# clip2file_tray.py

import sys
import tempfile, subprocess, pathlib, keyboard, pyperclip, atexit, os, threading, re
from PIL import Image
import pystray

from pasteasfile.spinner import show_spinner

TMP_FILES = []

def copy_text_as_file():
    data = pyperclip.paste()
    if not data.strip():
        return
    lines = data.splitlines()
    first = next((l for l in lines if l.strip()), '')
    words = re.findall(r'\w+', first)
    name = '_'.join(words[:5]).lower() or 'clipboard'
    filename = f"{name}.py"
    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, filename)
    count = 1
    while os.path.exists(path):
        path = os.path.join(temp_dir, f"{name}_{count}.py")
        count += 1
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
    TMP_FILES.append(path)
    subprocess.run(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden",
         "Set-Clipboard", "-Path", str(path)],
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
    if getattr(sys, "frozen", False):
        base_path = pathlib.Path(sys._MEIPASS)
    else:
        base_path = pathlib.Path(__file__).resolve().parents[2] / "assets"
    icon_path = base_path / "icon.ico"
    image = Image.open(str(icon_path))
    menu  = pystray.Menu(pystray.MenuItem("Exit", on_exit))
    icon  = pystray.Icon("Paste as File", image, "Paste as File", menu)
    threading.Thread(target=icon.run, daemon=True).start()
    return icon

if __name__ == "__main__":
    atexit.register(lambda: [os.unlink(f) for f in TMP_FILES if os.path.exists(f)])
    icon = setup_tray()
    keyboard.add_hotkey("ctrl+alt+v", copy_text_as_file, suppress=False)
    keyboard.wait()          # still blocks, but on_exit will now kill this too


# debug command (to be run from root)
# watchmedo auto-restart --patterns="*.py" --recursive -- python -m pasteasfile.clip2file_tray
# build (to be run from src/pasteasfile)
# pyinstaller clip2file_tray.py --onefile --noconsole --add-data "../../assets/icon.ico;." --add-data "../../assets/spinner.gif;."
