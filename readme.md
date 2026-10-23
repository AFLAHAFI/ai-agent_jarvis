# 🤖 JARVIS (MARK LVI) — Autonomous AI Desktop Agent







<div align="center">







![JARVIS Banner](https://img.shields.io/badge/JARVIS-MARK_LVI-00f0ff?style=for-the-badge&logo=probot&logoColor=black)



![Python 3.12+](https://img.shields.io/badge/Python-3.12%20%7C%203.13-blue?style=for-the-badge&logo=python&logoColor=white)



![Gemini Live API](https://img.shields.io/badge/Gemini_Live-Streaming_Audio-4285F4?style=for-the-badge&logo=google&logoColor=white)



![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand_Tracking-FF6F00?style=for-the-badge&logo=google&logoColor=white)



![Cross Platform](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-green?style=for-the-badge)



![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)







**Next-Generation Multi-modal AI Desktop Voice Assistant & Autonomous Agent by [AFLAHAFI](https://github.com/AFLAHAFI)**  



*Voice • Vision • MediaPipe Hand Gestures • MS Paint Speed-Drawing • Stark Arc Reactor HUD • Sub-Pixel UI Automation*







</div>







---







## 🌟 Overview







**JARVIS (MARK LVI)** is an advanced, fully autonomous personal AI assistant built for desktop operating systems (Windows 10/11, macOS, and Linux). Powered by Google's native bidirectional **Gemini Live API** streaming audio architecture, JARVIS delivers instant voice conversations with zero latency, accompanied by a dynamic Iron-Man-inspired **Stark Arc Reactor & 3D Holographic Lip-Synced Avatar HUD**.







Beyond conversation, MARK LVI acts as an autonomous digital agent capable of perceiving your screen, tracking hand gestures via optical computer vision, physically guiding the mouse to paint artwork live, automating browser tasks, and managing computer operations with zero subscriptions.







---







## 🚀 Key Features







### 1. ⚛️ Dynamic Stark Arc Reactor & 3D Holographic Avatar



* **Smart Hybrid State Machine:**



  * **Speaking / Answering:** Dynamically renders an animated **3D Holographic AI Core Avatar** with real-time formant and phonetic lip-sync visemes (~50 shapes/second).



  * **Listening / Thinking / Idle:** Seamlessly transitions into a pulsing, sound-reactive **10-Coil Electromagnetic Stark Arc Reactor**.



* **Authentic Tony Stark Hologram Rings:** Featuring concentric cybernetic telemetry arcs, counter-rotating precision calipers, and audio-reactive viseme expansion waves in vibrant Electric Stark Cyan (`#00f0ff`) and Stark Gold (`#ffd700`).



* **Audio-Reactive Waveforms:** Real-time software rendering with ambient halo glow and cybernetic telemetry HUD.







### 2. 📱 Mini Assistant Floating HUD Mode (Ctrl+M) & Instant Wakeup



* **Compact Multitasking Widget:** Click **▣ MINI** in the header or press **Ctrl+M** to collapse the full HUD into a sleek, frameless, draggable, always-on-top companion widget (320×110 px).



* **Live Status Telemetry:** Reflects current assistant state (● LISTENING in green, ● SPEAKING in cyan, ◈ THINKING in amber).



* **Instant One-Click Restoration:** Click **OPEN HUD ↗**, say *"Hey Jarvis"*, or press **Ctrl+M** anytime to instantly restore and repaint the full Stark Arc Reactor HUD to its exact previous window position and geometry (zero freeze/black screen).







### 3. 🖐️ Distance-Invariant Optical Hand Tracking & Floating Gesture HUD (`actions/hand_mouse.py`)



* Powered by **Google MediaPipe HandLandmarker** (21 3D joint landmarks) with **Palm-Scale Distance Normalization**.



* **Distance-Invariant Pinch-to-Click:** Pinch detection scales dynamically with palm geometry ($$Ratio = \frac{Distance}{PalmScale}$$), allowing left-clicks and drag operations to trigger reliably whether you are 30 cm or 2 meters away from the webcam.



* **Floating Stark Gesture Mini HUD:** A translucent neon status pill anchors to the top-right corner during active tracking, displaying real-time `[PINCH CLICK]` feedback with audio chirps.



* **Instant Camera Shutdown:** Clean, non-blocking camera release upon saying *"Disable hand tracking"* or *"ഹാൻഡ് ഓഫ് ചെയ്യൂ"*.



* **Jitter-Free Navigation:** Dynamic speed-adaptive smoothing with micro-movement deadband suppresses hand tremor completely. During active pinches, an anchor dampener locks the cursor in place so clicking never slips off target buttons.



* **Right-Click:** Pinch middle finger and thumb together at any distance.







### 4. 📜 Dynamic Contextual Scrolling & Dual-Pane Targeting (`actions/computer_control.py`)



* **Natural Malayalam & English Commands:** Interprets subtle magnitude instructions seamlessly (*"കുറച്ച് താഴോട്ട് ആക്ക്"*, *"ഇത്തിരി സ്ക്രോൾ ചെയ്യ്"*, *"ഫുൾ താഴോട്ട് പോ"*, *"scroll up a little"*, *"scroll all the way down"*).



* **Dual-Pane Awareness:** Distinguishes between split-screen containers (e.g., targeting the left chat conversation list vs. the right chat history pane in WhatsApp Desktop or browsers).



* **Zero-Refusal UI Authority:** Unrestricted operator permissions over desktop software — never refuses to click or interact with UI elements.



* **Sub-Pixel Precision Visual Screen Click:** Uses Gemini 2D normalized bounding box localization (`box_2d: [ymin, xmin, ymax, xmax]`) to visually locate and click ANY button, icon, menu, or chat on screen.



* **Context-Aware In-Place Replacement:** Edits and updates text in currently active fields (`Ctrl+A` ➔ `Backspace` ➔ `Type/Paste`) without duplicate tabs or windows.







### 5. ⏰ Quick Relative Reminders & Voice Notes (`actions/reminder.py`)



* **Instant Relative Delays:** Supports natural relative scheduling (*"Remind me in 5 minutes to check the oven"*, *"10 മിനിറ്റ് കഴിഞ്ഞ് ഓർമ്മിപ്പിക്കൂ"*) without needing full calendar dates.



* **System Scheduler Persistence:** Schedules tasks via native OS task schedulers (Windows Task Scheduler, macOS LaunchAgents, Linux systemd-run), triggering audio chimes and voice announcements even when the main assistant window is closed.







### 5. 💬 Native WhatsApp Desktop & Visual Chat Opener (`plugins/whatsapp_assistant.py`)



* **Native Desktop App Integration:** Opens chats and drafts messages directly inside the official Windows **WhatsApp Desktop** app via `whatsapp://` URI protocols.



* **Visual Chat & Unread Opener:** Visually navigates the WhatsApp interface to locate and click specific contact chats or green unread message badges on screen.



* **Unread Message Telemetry:** Scans active WhatsApp window headers to detect and announce unread conversations.







### 6. 🐕 Proactive Communication Watchdog (`main.py`)



* **Background Message Monitor:** Periodically monitors WhatsApp Desktop and alerts the user proactively with speech when new incoming messages arrive: *"Sir, you have received new message(s) on WhatsApp Desktop."*



* **Automatic Standby Wakeup:** Gently wakes from sleep to deliver urgent notifications and offers to open the message visually.







### 7. 📖 Smart Contact Book & Gmail Recipient Resolution (`plugins/gmail_assistant.py`)



* **Intelligent Recipient Mapping:** Automatically resolves contact names (e.g., "Amjad Ali") to verified email addresses stored in persistent memory.



* **Auto-Commit Contact Chips:** Commits recipient chips automatically in the Gmail compose interface.



* **In-Place Draft Editing:** Modifies active email drafts in-place without spawning duplicate browser tabs.







### 8. 🎙️ Strict Wake-Word Standby & Auto-Sleep (`core/wake_word.py` & `main.py`)



* **Strict "Hey Jarvis" Isolation:** Powered by local, offline ONNX **OpenWakeWord** models. The assistant stays silent in the background until explicitly invoked.



* **Automated Silence Timeout:** After executing user instructions, JARVIS automatically returns to a quiet standby state after a configured period of inactivity.







### 9. 🔒 Permanent User Identity Lock (`memory/memory_manager.py`)



* Enforces write-protection on primary user identity attributes configured in `config/api_keys.json`, ensuring the user's name is permanently locked and never overwritten by conversational context noise.







### 10. 🎨 Autonomous MS Paint Live Speed-Drawing (`actions/creative_agent.py`)



* Fully dynamic vector art synthesis for **ANY** subject requested by voice (humans, cats, cars, houses, landscapes, etc.) via Gemini FAST.



* **Physical Mouse Execution:** Opens MS Paint, maximizes it, and physically maneuvers the mouse across the canvas live on screen, rendering continuous bezier-like strokes in real-time.



* **Safe-Bounds Protection:** Ensures drawing is strictly contained inside the canvas sheet without touching toolbars or system controls.







### 11. 🔌 Modular Plug-and-Play Plugins Ecosystem (`plugins/`)



* **Gmail Assistant (`plugins/gmail_assistant.py`):** Open inbox, check unread emails, search messages, resolve contacts, and edit active drafts in-place.



* **Live Daily Briefing (`plugins/live_briefing.py`):** Live weather conditions and top world news headlines with time-aware greetings.



* **WhatsApp Desktop (`plugins/whatsapp_assistant.py`):** Native Windows messaging, unread checks, and visual chat clicking.



* **Spotify & Media Controller (`plugins/spotify_media.py`):** Control media playback (Play/Pause, Next Track, Mute, Volume Control).



* **System Deep Cleaner (`plugins/system_cleaner.py`):** Flush Windows `%TEMP%` cache files, empty Recycle Bin silently, and free RAM memory.







---







## 🏗️ Architecture







```mermaid



flowchart TD



    User([User Voice & Gestures]) <--> MicCam[Microphone & Webcam]



    MicCam --> AudioEngine[Audio Ingest & Wake-Word Detector]



    MicCam --> MediaPipe[MediaPipe Optical Hand Tracker]







    AudioEngine --> LiveSession[Gemini Live API Session]



    MediaPipe --> OSControl[PyAutoGUI Desktop Automation]







    LiveSession <--> ToolRouter{Tool & Action Dispatcher}







    ToolRouter --> CreativeAgent[MS Paint Speed-Drawing Agent]



    ToolRouter --> ScreenClick[Sub-Pixel Visual Screen Click]



    ToolRouter --> Plugins[Plugins Ecosystem: Spotify, WhatsApp, Cleaner]



    ToolRouter --> Reminders[HUD Smart Reminders]







    LiveSession --> UI[PyQt6 Stark HUD Canvas]



    UI --> Avatar3D[3D Lip-Synced Hologram]



    UI --> ArcReactor[10-Coil Arc Reactor Core]



```







---







## ⚡ Quick Start & Installation







### Step 1: Clone the Repository



```bash



git clone https://github.com/AFLAHAFI/ai-agent_jarvis.git



cd ai-agent_jarvis



```







### Step 2: Automatic One-Click Setup



Run the automated environment setup script:



```bash



python setup.py



```







### Step 3: Configure Your API Key



Copy the template configuration file:



```bash



# On Windows:



copy config\api_keys.json.example config\api_keys.json







# On macOS / Linux:



cp config/api_keys.json.example config/api_keys.json



```



Edit `config/api_keys.json` with your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey):



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







### Step 4: Run JARVIS



On Windows:



```bash



run.bat



```



On macOS / Linux:



```bash



source .venv/bin/activate



python main.py



```







For full platform-specific instructions, see the [📖 Detailed Setup Guide](SETUP_GUIDE.md).







---







## 🗣️ Common Voice Commands







| Action | Example Trigger Voice Phrase |



|---|---|



| **Wake Word** | *"Hey Jarvis"* (Arc Reactor Ignition Flare & Chime) |
| **Mini HUD Voice Switch** | *"Switch to mini HUD"* / *"മിനി ഹബ്ബിലോട്ട് മാറ്"* / *"Open full HUD"* |
| **24/7 Screen Vision** | *"Watch my screen"* / *"What am I looking at right now?"* / *"Read the error on screen"* |
| **PDF & Doc Summarizer** | *"Summarize this PDF on my desktop"* / *"Read document contract.pdf"* |
| **Workspace Presets** | *"Coding workspace"* / *"Snap WhatsApp to left"* / *"Focus VS Code"* |
| **Voice Notes & To-Dos** | *"കുറിച്ചു വെക്കൂ: മീറ്റിംഗ് ഉണ്ട്"* / *"Add to my to-do list: Project"* / *"Show my tasks"* |
| **System Diagnostics** | *"Jarvis, system status"* / *"How much battery is left?"* / *"ബാറ്ററി എത്രയുണ്ട്?"* |
| **Folder Organizer** | *"Clean up my Downloads folder"* / *"Undo folder organization"* |



| **Hand Tracking** | *"Enable hand tracking"* / *"Disable hand tracking"* |



| **Visual Click** | *"Click on the search bar"* / *"Click the mute button"* |



| **Live Drawing** | *"Draw a cat in Paint"* / *"Draw a red sports car"* |



| **Media Playback** | *"Play music"* / *"Pause music"* / *"Next track"* / *"Volume up"* |



| **Reminders** | *"Remind me to drink water in 10 minutes"* |



| **System Maintenance** | *"Clean temporary files"* / *"Empty recycle bin"* |



| **WhatsApp** | *"Send a WhatsApp message to [Contact/Number]"* / *"Check unread WhatsApp"* |



| **Gmail** | *"Check my unread emails"* / *"Open Gmail"* / *"Send an email"* / *"Edit draft"* |



| **Daily Briefing** | *"Good morning Jarvis"* / *"Give me today's briefing"* / *"What's the news today?"* |



| **Vision Analysis** | *"What's on my screen right now?"* / *"Look at this"* |







---







## 📂 Repository Structure







```



ai-agent_jarvis/



├── actions/                  # Auto-discovered capabilities & tools



│   ├── computer_control.py   # In-place text replacement & sub-pixel vision click



│   ├── creative_agent.py     # Live physical Paint drawing agent



│   ├── hand_mouse.py         # Distance-invariant MediaPipe hand tracking mouse



│   ├── reminder.py           # Audio-visual HUD reminder system



│   ├── screen_processor.py   # Display & webcam vision pipeline



│   └── ...                   # YouTube, weather, file controller, web search



├── config/                   # Configuration templates & models



│   ├── api_keys.json.example # Safe configuration template (API keys excluded)



│   ├── hand_landmarker.task  # MediaPipe hand tracking model



│   └── jarvis.ico            # Stark Industries HUD icon



├── core/                     # Internal subsystems (Gemini Live, audio, UI)



│   ├── avatar.py             # 3D holographic avatar mesh renderer



│   ├── gemini.py             # Resilient multi-tier model ladder



│   ├── plugin_loader.py      # Dynamic plugin discovery engine



│   ├── wake_word.py          # Local OpenWakeWord offline detector



│   └── ...



├── memory/                   # Assistant persistent memory



│   ├── long_term.json.example# Safe memory schema template



│   └── memory_manager.py     # Permanent user identity protection engine



├── plugins/                  # Modular plug-and-play user plugins



│   ├── gmail_assistant.py    # Gmail management & in-place draft editor



│   ├── live_briefing.py      # Real-time news & weather briefing



│   ├── spotify_media.py      # Multimedia & Spotify controller



│   ├── system_cleaner.py     # Cache, Temp & Recycle Bin cleaner



│   ├── whatsapp_assistant.py # Native Windows WhatsApp Desktop integration



│   └── _template.py          # Boilerplate for writing new plugins



├── .gitignore                # Strict security ignore rules



├── LICENSE                   # Open-source MIT License



├── main.py                   # Central daemon & Gemini Live loop



├── ui.py                     # PyQt6 Stark HUD & Arc Reactor engine



├── requirements.txt          # Python dependencies



├── setup.py                  # Automated virtualenv setup script



├── run.bat                   # One-click Windows launcher



├── README.md                 # Project documentation



└── SETUP_GUIDE.md            # Comprehensive setup walkthrough



```







---







## 🔒 Security & Privacy







* **Zero Secret Leakage:** `config/api_keys.json` and `memory/long_term.json` are excluded from version control via `.gitignore`.



* **Safe Local Operations:** All hand tracking and computer vision run 100% locally on your machine via CPU delegates. Audio is only streamed to Gemini Live during active sessions.



* **No Telemetry / No Tracking:** Your personal data, conversation history, and credentials remain solely on your local device.







---







## 🤝 Contributing







Contributions, issues, and feature requests are welcome!



1. Fork the Project: `https://github.com/AFLAHAFI/ai-agent_jarvis`



2. Create your Feature Branch: `git checkout -b feature/NewPlugin`



3. Commit your Changes: `git commit -m 'Add awesome new plugin'`



4. Push to the Branch: `git push origin feature/NewPlugin`



5. Open a Pull Request







---







## 📜 License







Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.







---







<div align="center">



Developed with ❤️ by <a href="https://github.com/AFLAHAFI">AFLAHAFI</a>



</div>



