# 🛠️ JARVIS (MARK LVI) — Complete Setup Guide

Welcome to the complete installation and setup guide for **JARVIS (MARK LVI)** by **AFLAHAFI**.
This guide covers setting up and running your personal AI desktop assistant across Windows 10/11, macOS, and Linux.

---

## 📋 System Requirements

| Component | Minimum Specification | Recommended |
|---|---|---|
| **Operating System** | Windows 10/11 (64-bit), macOS 12+, Ubuntu 22.04+ (X11) | Windows 11 / macOS Sonoma / Linux X11 |
| **Python** | Python 3.11 – 3.13 | Python 3.12 or 3.13 |
| **API Key** | Google Gemini API Key (Free tier from [Google AI Studio](https://aistudio.google.com/app/apikey)) | Gemini API Key or Local LLM (Ollama) |
| **Microphone & Speaker** | Standard laptop mic and speakers | USB headset or clean array mic |
| **Webcam** | Any 720p/1080p RGB webcam (for Hand Tracking & Vision) | 1080p 30/60fps Webcam |
| **Disk Space** | ~2 GB free disk space | 4 GB |

---

## 🪟 Windows Setup Guide (One-Click)

### 1. Install Prerequisites
1. Download and install **Python 3.12 or 3.13** from [python.org](https://www.python.org/downloads/).
   > ⚠️ **CRITICAL:** Ensure you check the box **"Add python.exe to PATH"** during installation!
2. Install [Git for Windows](https://git-scm.com/download/win) if not already installed.

### 2. Clone the Repository
Open PowerShell or Command Prompt:
```bash
git clone https://github.com/AFLAHAFI/ai-agent_jarvis.git
cd ai-agent_jarvis
```

### 3. Automatic Environment Setup
Run the automated setup script:
```bash
python setup.py
```
This script will:
* Create an isolated virtual environment (`.venv/`)
* Install all required dependencies (`requirements.txt`)
* Download Playwright browsers for web automation
* Verify audio, vision, and system libraries

### 4. Configure Your API Key
Copy the template configuration file:
```bash
copy config\api_keys.json.example config\api_keys.json
```
Edit `config\api_keys.json` with your preferred editor and enter your Gemini API key:
```json
{
  "gemini_api_key": "YOUR_ACTUAL_GEMINI_API_KEY",
  "os_system": "windows",
  "assistant_name": "JARVIS",
  "user_name": "Sir",
  "ui_color": "#00f0ff",
  "camera_index": 0,
  "hud_style": "hybrid"
}
```

### 5. Launch JARVIS
Simply run:
```bash
run.bat
```
or run with Python:
```bash
.venv\Scripts\python.exe main.py
```

---

## 🍎 macOS Setup Guide

### 1. Prerequisites
1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python 3.12 and portaudio:
   ```bash
   brew install python@3.12 portaudio git
   ```

### 2. Clone & Setup
Clone into a local folder (outside iCloud-synced Documents):
```bash
cd ~
git clone https://github.com/AFLAHAFI/ai-agent_jarvis.git
cd ai-agent_jarvis
python3.12 setup.py
```

### 3. Permissions
Grant macOS permissions in **System Settings → Privacy & Security**:
* **Microphone** (Terminal / Python)
* **Camera** (Terminal / Python)
* **Accessibility** (for keyboard and mouse automation)

### 4. Run
```bash
source .venv/bin/activate
python main.py
```

---

## 🐧 Linux Setup Guide (Ubuntu / Debian / Arch)

### 1. Install System Dependencies
On Ubuntu / Debian:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv portaudio19-dev libasound2-dev git libgl1-mesa-glx
```

### 2. Clone & Setup
```bash
git clone https://github.com/AFLAHAFI/ai-agent_jarvis.git
cd ai-agent_jarvis
python3 setup.py
```

### 3. Run
```bash
source .venv/bin/activate
python main.py
```

---

## ⚙️ Voice & Gesture Controls Quick Reference

* **Wake Word:** Say *"Hey Jarvis"* anytime to bring the HUD forward and activate.
* **Hand Tracking:** Say *"Enable hand tracking"* to steer cursor with your index finger and pinch thumb + index to click. Say *"Disable hand tracking"* to stop.
* **Visual Click:** Say *"Click on [element/button name]"* to visually locate and click any UI item on screen.
* **Autonomous Drawing:** Say *"Draw a cat in Paint"* or *"Draw a human figure"*.
* **Media & Music:** Say *"Play music"*, *"Pause"*, *"Next track"*, *"Volume up"*.
* **System Clean:** Say *"Clean system temp files"* to empty recycle bin and flush RAM caches.
