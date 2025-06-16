# Windows tool that converts clipboard text into a file and puts that file on the clipboard, so it can be pasted anywhere as if the user copied a file manually
import tempfile, subprocess, pathlib, keyboard, pyperclip, atexit, os

def clip_py():
    data = pyperclip.paste()
    if not data.strip():
        return
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp.write(data.encode()); tmp.close()
    subprocess.run(["powershell","-NoProfile",f'Set-Clipboard -Path \"{pathlib.Path(tmp.name)}\"'])
    atexit.register(lambda: os.unlink(tmp.name))

keyboard.add_hotkey('ctrl+alt+v', clip_py)
keyboard.wait()
