# JARVIS Desktop AI

A desktop voice assistant built with Python and PyQt. This branch adds an optional compact floating companion so you can keep JARVIS accessible without leaving the full HUD open.

> This is a community contribution based on the upstream project by AFLAHAFI. It is not an official upstream release.

## Highlights

- Existing desktop assistant and HUD features from the upstream project.
- **Mini Assistant HUD:** click **▣ MINI** to hide the main window and show a compact floating companion.
- **Keyboard shortcut:** press **Ctrl+M** while the main window is focused.
- **OPEN HUD:** restore the main window to its previous size and position.
- **Draggable, always-on-top mini window.**
- Refreshed window title and HUD subtitle branding.
- Setup and branding notes in [SETUP_GUIDE.md](SETUP_GUIDE.md) and [BRANDING.md](BRANDING.md).

## Requirements

- Windows 10/11 or another OS supported by the upstream project
- Python version supported by the project's dependencies
- A working microphone/audio setup for voice features
- API credentials only for services you choose to configure

## Windows quick start

1. Install Python and Git if they are not already installed.
2. Download or clone this repository.
3. Open the project folder in Command Prompt.
4. Create a virtual environment and install the project's dependencies:

   ```bat
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install --upgrade pip
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

5. Review the upstream setup instructions in [SETUP_GUIDE.md](SETUP_GUIDE.md).
6. Configure API keys locally using the example configuration where required. **Never commit API keys, tokens, or personal memory files.**
7. Start the assistant with `run.bat` or run `python main.py` inside the activated environment.

## Using Mini Mode

1. Launch JARVIS and wait for the main HUD.
2. Click **▣ MINI**, or press **Ctrl+M** while the main HUD has focus.
3. Drag the mini window to move it.
4. Click **OPEN HUD** to return to the full interface. Closing the mini window also restores the HUD.

## Security

- Keep API credentials and tokens local.
- Do not commit `config/api_keys.json`, `.env` files, personal memory databases, or other private data.
- Rotate any credential that has accidentally been published.

## Verification status

Python syntax compilation was checked for the prepared local source package. The GUI has **not** been runtime-tested on a real desktop in this environment; please test the Mini button, Ctrl+M, drag behavior, and OPEN HUD on your system before relying on it.

## Contribution

This is a proposed contribution for maintainer review. See [CHANGELOG_LOCAL.md](CHANGELOG_LOCAL.md) for the changes in this branch. Please report platform-specific issues with the OS, Python version, and relevant traceback, with secrets removed.

## Upstream

Original project: https://github.com/AFLAHAFI/ai-agent_jarvis
