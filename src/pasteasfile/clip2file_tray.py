# clip2file_tray.py

import sys
import tempfile, subprocess, keyboard, pyperclip, atexit, os, threading, re
from PIL import Image
import pystray
import tkinter as tk
from tkinter import ttk

from .spinner import show_spinner
from .utils import get_asset_path

TMP_FILES = []
DEFAULT_EXT = ".py"

def copy_text_as_file():
    data = pyperclip.paste()
    if not data.strip():
        return
    lines = data.splitlines()
    first = next((l for l in lines if l.strip()), '')
    words = re.findall(r'\w+', first)
    name = '_'.join(words[:5]).lower() or 'clipboard'
    filename = f"{name}{DEFAULT_EXT}"
    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, filename)
    count = 1
    while os.path.exists(path):
        path = os.path.join(temp_dir, f"{name}_{count}{DEFAULT_EXT}")
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

def set_default_extension(icon, _item):
    """Show a tiny dialog to choose the default file extension."""
    global DEFAULT_EXT

    root = tk.Tk()
    root.title("Default Extension")
    root.resizable(False, False)

    frm = ttk.Frame(root, padding=10)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Choose extension").pack(anchor="w")

    common = [".py", ".txt", ".md", "Other..."]
    choice = tk.StringVar(value=DEFAULT_EXT if DEFAULT_EXT in common else "Other...")
    combo = ttk.Combobox(frm, values=common, textvariable=choice, state="readonly")
    combo.pack(fill="x", pady=5)

    custom_var = tk.StringVar(value=DEFAULT_EXT if DEFAULT_EXT not in common else "")
    entry = ttk.Entry(frm, textvariable=custom_var)
    entry.pack(fill="x")

    def update_state(*_):
        if choice.get() == "Other...":
            entry.configure(state="normal")
            entry.focus()
        else:
            entry.configure(state="disabled")
            custom_var.set(choice.get())

    choice.trace_add("write", update_state)
    update_state()

    def confirm():
        ext = custom_var.get() if choice.get() == "Other..." else choice.get()
        ext = ext.strip()
        if ext and not ext.startswith("."):
            ext = "." + ext
        if ext:
            DEFAULT_EXT = ext
        root.destroy()

    btn = ttk.Button(frm, text="OK", command=confirm)
    btn.pack(pady=8)

    root.mainloop()

def on_exit(icon, _item):
    # clean up files & hooks, stop tray, then fully exit
    for f in TMP_FILES:
        try: os.unlink(f)
        except: pass
    keyboard.unhook_all()
    icon.stop()
    os._exit(0)      # ← kill the whole process immediately

def setup_tray():
    image = Image.open(get_asset_path("icon.ico"))
    menu  = pystray.Menu(
        pystray.MenuItem(lambda: f"Set Extension ({DEFAULT_EXT})", set_default_extension),
        pystray.MenuItem("Exit", on_exit)
    )
    icon  = pystray.Icon("Paste as File", image, "Paste as File", menu)
    threading.Thread(target=icon.run, daemon=True).start()
    return icon

def main():
    atexit.register(lambda: [os.unlink(f) for f in TMP_FILES if os.path.exists(f)])
    icon = setup_tray()
    keyboard.add_hotkey("ctrl+alt+v", copy_text_as_file, suppress=False)
    keyboard.wait()          # still blocks, but on_exit will now kill this too

if __name__ == "__main__":
    main()