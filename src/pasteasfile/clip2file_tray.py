# clip2file_tray.py

import sys
import tempfile, subprocess, keyboard, pyperclip, atexit, os, threading, re
import queue
import tkinter as tk
from tkinter import ttk
from PIL import Image
import pystray

from .spinner import SpinnerManager
from .utils import get_asset_path

TMP_FILES = []
DEFAULT_EXT = ".py"

# Queue for thread communication
ui_queue = queue.Queue()

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
    # Queue spinner request instead of direct call
    ui_queue.put(('show_spinner', None))

def set_default_extension(icon, _item):
    """Show a tiny dialog to choose the default file extension."""
    # Queue the extension dialog request
    ui_queue.put(('show_extension_dialog', icon))

def _show_extension_dialog(icon):
    """Actually show the extension dialog - runs in main thread."""
    global DEFAULT_EXT
    
    root = tk.Toplevel()  # Use Toplevel instead of Tk()
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
        global DEFAULT_EXT
        ext = custom_var.get() if choice.get() == "Other..." else choice.get()
        ext = ext.strip()
        if ext and not ext.startswith("."):
            ext = "." + ext
        if ext:
            DEFAULT_EXT = ext
            icon.update_menu()
        root.destroy()
    
    btn = ttk.Button(frm, text="OK", command=confirm)
    btn.pack(pady=8)
    
    # Make dialog modal
    root.transient()
    root.grab_set()
    root.wait_window()

def on_exit(icon, _item):
    # clean up files & hooks, stop tray, then fully exit
    for f in TMP_FILES:
        try: os.unlink(f)
        except: pass
    keyboard.unhook_all()
    icon.stop()
    ui_queue.put(('quit', None))

def setup_tray():
    image = Image.open(get_asset_path("icon.ico"))
    menu  = pystray.Menu(
        pystray.MenuItem(lambda item: f"Set Extension ({DEFAULT_EXT})", set_default_extension),
        pystray.MenuItem("Exit", on_exit)
    )
    icon  = pystray.Icon("Paste as File", image, "Paste as File", menu)
    threading.Thread(target=icon.run, daemon=True).start()
    return icon

def process_ui_queue(root, spinner_manager, icon):
    """Process UI events from the queue - runs in main thread."""
    try:
        while True:
            try:
                action, data = ui_queue.get_nowait()
                if action == 'show_spinner':
                    spinner_manager.show()
                elif action == 'show_extension_dialog':
                    _show_extension_dialog(data)
                elif action == 'quit':
                    root.quit()
                    return
            except queue.Empty:
                break
    finally:
        # Schedule next check
        root.after(50, lambda: process_ui_queue(root, spinner_manager, icon))

def main():
    atexit.register(lambda: [os.unlink(f) for f in TMP_FILES if os.path.exists(f)])
    
    # Create hidden root window for Tkinter
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Create spinner manager
    spinner_manager = SpinnerManager(root)
    
    # Setup tray icon
    icon = setup_tray()
    
    # Setup hotkey
    keyboard.add_hotkey("ctrl+alt+v", copy_text_as_file, suppress=False)
    
    # Start processing UI queue
    root.after(50, lambda: process_ui_queue(root, spinner_manager, icon))
    
    # Run Tkinter main loop in main thread
    root.mainloop()

if __name__ == "__main__":
    main()