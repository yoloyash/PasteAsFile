# Building and Development

## Setup (to be run from `root` directory)

Install the required Python packages with:

```bash
pip install -r requirements.txt
```

### Development

1. Install library

```bash
pip install -v -e .
```

2. Run dev:

```bash
watchmedo auto-restart --patterns="*.py" --recursive -- python -m pasteasfile.clip2file_tray
```

### Building

To generate a standalone executable use `pyinstaller` from the
`src/pasteasfile` directory:

```bash
pyinstaller run.py --onefile --noconsole \
    --name PasteAsFile \
    --add-data "assets/icon.ico;." \
    --add-data "assets/spinner.gif;."
```
