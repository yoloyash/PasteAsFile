# PasteAsFile

This project is a Python-based Windows utility that runs in the system tray. Its core function is to convert text from the clipboard into a temporary file. Triggered by a Ctrl+Alt+V hotkey, it performs the conversion and copies the new file to the clipboard, ready for pasting, confirmed by a brief visual spinner.

## Setup

Install the required Python packages with:

```bash
pip install -r requirements.txt
```

## Development

During development you can automatically reload the tray application whenever
files change using [`watchmedo`](https://github.com/gorakhargosh/watchdog):

```bash
watchmedo auto-restart --patterns="*.py" --recursive -- \
    python -m pasteasfile.clip2file_tray
```

## Building

To generate a standalone executable run `pyinstaller` from the
`src/pasteasfile` directory:

```bash
pyinstaller clip2file_tray.py --onefile --noconsole \
    --add-data "../../assets/icon.ico;." \
    --add-data "../../assets/spinner.gif;."
```

You can download the latest release here.
