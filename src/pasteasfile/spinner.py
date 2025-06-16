# spinner.py

import threading, tkinter as tk, sys, os
from PIL import Image, ImageTk

# SPINNER_PATH = "spinner.gif"
if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
SPINNER_PATH = os.path.join(base_path, "spinner.gif")
DURATION_MS  = 1000            # how long to keep it on-screen
ARC_MS       = 40             # frame delay

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
    try:
        while True:
            frame = gif.copy().resize((w, h), Image.LANCZOS)
            frames.append(ImageTk.PhotoImage(frame))
            gif.seek(len(frames))
    except EOFError:
        pass
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
