# PasteAsFile

A tiny Windows utility that instantly turns your clipboard text into a temporary file, ready to be pasted or attached anywhere.

[**➡️ Download the Latest Release**](https://github.com/yoloyash/PasteAsFile/releases/latest)

<!-- You can add a GIF here later -->

## How It Works

1. Run the `PasteAsFile.exe` application. An icon will appear in your system tray.
2. Copy any text to your clipboard.
3. Press **`Ctrl`+`Alt`+`V`**.
4. The text is saved as a temporary file with the configured extension (``.py`` by default).
5. That file is copied to your clipboard, ready to be pasted (e.g., into an email attachment, Slack, Discord, etc.).

Right-click the tray icon to quickly switch the default extension. The tray menu displays the current choice, and a modern dialog lets you pick from common options like `.py`, `.txt`, or `.md`, or enter any custom extension.

## A Note on Security

When you run the executable for the first time, Windows Defender SmartScreen may show a warning. This is normal for new applications from independent developers that are not digitally signed.

The application is safe. If you are cautious, you are welcome to inspect the source code and build it yourself.

**For building instructions, see [BUILDING.md](BUILDING.md).**
