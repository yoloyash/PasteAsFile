# spinner.py

import threading
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from tkinterdnd2 import Tk, DND_FILES, COPY
from .utils import get_asset_path

SPINNER_PATH = get_asset_path("spinner.gif")
DURATION_MS  = 1000            # how long to keep it on-screen
ARC_MS       = 40             # frame delay
DRAG_DURATION_MS = 5000       # how long to keep drag icon visible

def _overlay():
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    key = "#123456"
    root.configure(bg=key)
    root.wm_attributes("-transparentcolor", key)
    w, h = 80, 80
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{sh-h-60}")
    gif = Image.open(SPINNER_PATH)
    frames = []

    for frame in ImageSequence.Iterator(gif):
        resized_frame = frame.copy().resize((w, h), Image.Resampling.LANCZOS)
        frames.append(ImageTk.PhotoImage(resized_frame))

    lbl = tk.Label(root, bg=key)
    lbl.pack(expand=True, fill="both")
    def animate(i=0, t=0):
        lbl.configure(image=frames[i])
        if t < DURATION_MS:
            root.after(ARC_MS, animate, (i + 1) % len(frames), t + ARC_MS)
        else:
            root.destroy()
    animate()
    root.mainloop()

def show_spinner():
    threading.Thread(target=_overlay, daemon=True).start()


def _drag_overlay(path: str):
    root = Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    key = "#123456"
    root.configure(bg=key)
    root.wm_attributes("-transparentcolor", key)
    w, h = 80, 80
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{sh-h-60}")

    img = Image.open(get_asset_path("icon.ico")).resize((w, h), Image.Resampling.LANCZOS)
    icon = ImageTk.PhotoImage(img)
    lbl = tk.Label(root, image=icon, bg=key)
    lbl.image = icon
    lbl.pack(expand=True, fill="both")

    lbl.drag_source_register(1, DND_FILES)

    def drag_init(event):
        return ((COPY,), (DND_FILES,), (path,))

    lbl.dnd_bind("<<DragInitCmd>>", drag_init)

    def close(_=None):
        root.destroy()

    root.bind("<FocusOut>", close)
    root.after(DRAG_DURATION_MS, close)
    root.mainloop()


def show_drag_icon(path: str):
    threading.Thread(target=_drag_overlay, args=(path,), daemon=True).start()
