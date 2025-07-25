# spinner.py

import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from .utils import get_asset_path

SPINNER_PATH = get_asset_path("spinner.gif")
DURATION_MS  = 1000            # how long to keep it on-screen
ARC_MS       = 40             # frame delay

class SpinnerManager:
    """Manages spinner overlay windows in the main thread."""
    
    def __init__(self, parent_root):
        self.parent = parent_root
        self.frames = []
        self._load_frames()
    
    def _load_frames(self):
        """Load and prepare GIF frames."""
        try:
            gif = Image.open(SPINNER_PATH)
            w, h = 80, 80
            
            for frame in ImageSequence.Iterator(gif):
                resized_frame = frame.copy().resize((w, h), Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(resized_frame))
        except Exception as e:
            print(f"Failed to load spinner: {e}")
    
    def show(self):
        """Show the spinner overlay."""
        if not self.frames:
            return
        
        # Create overlay window
        overlay = tk.Toplevel(self.parent)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        
        # Configure transparency
        key = "#123456"
        overlay.configure(bg=key)
        overlay.wm_attributes("-transparentcolor", key)
        
        # Position at center-bottom of screen
        w, h = 80, 80
        sw = overlay.winfo_screenwidth()
        sh = overlay.winfo_screenheight()
        overlay.geometry(f"{w}x{h}+{(sw-w)//2}+{sh-h-60}")
        
        # Create label for animation
        lbl = tk.Label(overlay, bg=key)
        lbl.pack(expand=True, fill="both")
        
        # Start animation
        self._animate(overlay, lbl, 0, 0)
    
    def _animate(self, overlay, label, frame_idx, elapsed):
        """Animate the spinner."""
        if elapsed >= DURATION_MS:
            overlay.destroy()
            return
        
        # Update frame
        label.configure(image=self.frames[frame_idx])
        
        # Schedule next frame
        next_idx = (frame_idx + 1) % len(self.frames)
        overlay.after(ARC_MS, self._animate, overlay, label, next_idx, elapsed + ARC_MS)

# Legacy function for compatibility
def show_spinner():
    """Legacy function - should not be used directly."""
    print("Warning: show_spinner() called directly. Use SpinnerManager instead.")