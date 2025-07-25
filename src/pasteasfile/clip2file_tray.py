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
    
    root = tk.Toplevel()
    root.title("Choose Extension")
    root.resizable(False, False)
    root.configure(bg='#f0f0f0')
    
    # Center the window
    root.update_idletasks()
    width = 300
    height = 200
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Main frame with modern styling
    main_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title label
    title_label = tk.Label(main_frame, text="Choose file extension", 
                          font=('Segoe UI', 12, 'bold'), 
                          bg='#f0f0f0', fg='#333333')
    title_label.pack(pady=(0, 15))
    
    # Text entry field
    ext_var = tk.StringVar(value=DEFAULT_EXT)
    entry_frame = tk.Frame(main_frame, bg='white', highlightbackground='#cccccc', 
                          highlightthickness=1, bd=0)
    entry_frame.pack(fill='x', pady=(0, 15))
    
    entry = tk.Entry(entry_frame, textvariable=ext_var, font=('Segoe UI', 11), 
                    bd=0, highlightthickness=0)
    entry.pack(padx=8, pady=8)
    
    # Common extensions frame
    extensions_frame = tk.Frame(main_frame, bg='#f0f0f0')
    extensions_frame.pack(fill='x', pady=(0, 15))
    
    common_exts = ['.md', '.py', '.txt']
    buttons = []
    
    def select_extension(ext):
        ext_var.set(ext)
        update_button_states()
        entry.focus_set()
    
    def update_button_states():
        current_ext = ext_var.get()
        for btn, ext in zip(buttons, common_exts):
            if current_ext == ext:
                btn.configure(bg='#0078d4', fg='white', 
                            activebackground='#106ebe', activeforeground='white')
            else:
                btn.configure(bg='white', fg='#333333', 
                            activebackground='#e0e0e0', activeforeground='#333333')
    
    # Create buttons for common extensions
    for i, ext in enumerate(common_exts):
        btn = tk.Button(extensions_frame, text=ext, font=('Segoe UI', 10),
                       bd=0, padx=20, pady=8, cursor='hand2',
                       command=lambda e=ext: select_extension(e))
        btn.grid(row=0, column=i, padx=5)
        buttons.append(btn)
    
    # Monitor entry changes
    def on_entry_change(*args):
        update_button_states()
    
    ext_var.trace_add("write", on_entry_change)
    
    # Confirm button
    def confirm():
        global DEFAULT_EXT
        ext = ext_var.get().strip()
        if ext and not ext.startswith("."):
            ext = "." + ext
        if ext:
            DEFAULT_EXT = ext
            icon.update_menu()
        root.destroy()
    
    confirm_btn = tk.Button(main_frame, text="OK", font=('Segoe UI', 10, 'bold'),
                           bg='#0078d4', fg='white', bd=0, padx=30, pady=8,
                           cursor='hand2', command=confirm,
                           activebackground='#106ebe', activeforeground='white')
    confirm_btn.pack()
    
    # Bind Enter key to confirm
    root.bind('<Return>', lambda e: confirm())
    
    # Initial button state update
    update_button_states()
    
    # Focus on entry
    entry.focus_set()
    entry.select_range(0, tk.END)
    
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