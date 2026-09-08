<p align="center">
  <img
    src="https://readme-typing-svg.herokuapp.com?font=Poppins&weight=600&size=24&pause=1000&color=00C2FF&center=true&vCenter=true&width=850&lines=🤖+JARVIS+Desktop+Voice+Assistant;🎙️+Hey+Jarvis+%7C+Wake+Word+Activated;🖥️+Windows+Desktop+Automation;⚡+Python+%7C+Voice+Control+%7C+AI;🚀+Iron-Man+Style+Desktop+Assistant"
    alt="Typing Header"
  />
</p>

<p align="center">
  <img src="https://giffiles.alphacoders.com/212/212508.gif" alt="Jarvis HUD" width="100%">
</p>

<p align="center">
  <strong>ASSISTANT – Jarvis Desktop Voice Assistant</strong>
</p>

<p align="center">
  A powerful Windows voice-controlled desktop assistant built with Python,
  featuring wake-word detection, real-time animated HUD, application control,
  system automation, and voice feedback — all packed into a single EXE.
</p>

---

## About JARVIS PRO

JARVIS PRO is a Windows-focused desktop voice assistant. It listens for a
command, determines the intent, routes the request to the appropriate skill,
and returns feedback through speech and the desktop HUD. The project combines a
Python automation and voice runtime with a Next.js/Three.js visual interface,
a native `pywebview` window, and an optional remote dashboard.

The assistant supports two voice modes:

| Mode | When it is selected | What it does |
| --- | --- | --- |
| Online | An internet connection is available | Starts the full JARVIS runtime: skills, memory, automation, desktop HUD, remote dashboard, and the online voice engine. |
| Offline | No internet connection is available | Runs an isolated local conversation loop using Faster-Whisper for speech-to-text, Ollama for AI, and Piper for text-to-speech. |

The configured wake words are `jarvis`, `hey jarvis`, and `hello jarvis`.

## Main Features

- Wake-word and microphone-based voice control.
- Online and offline voice modes.
- Native desktop HUD powered by Next.js, React, Three.js, and `pywebview`.
- Windows automation for applications, volume, brightness, battery, processes,
  task management, Wi-Fi, Bluetooth, files, and browser navigation.
- Browser, Google, YouTube, Spotify, maps, translation, news, weather, camera,
  screen, communication, notes, reminders, and personal-memory skills.
- Natural follow-up handling and conversation context.
- AI/developer-intent routing for programming and project-related requests.
- Optional mobile-friendly remote dashboard with pairing, command history, file
  transfer, microphone queue, and live-conversation controls.

## How It Works

```text
Microphone / remote dashboard
             |
             v
Voice listener or dashboard server
             |
             v
core.dispatcher.dispatch(command)
             |
             +--> Fast routers for direct command plans
             |
             +--> Conversation and follow-up resolution
             |
             +--> Developer / chat / planner intent routing
             |
             v
core.registry.execute(action, data)
             |
             v
skills.<category>.<module>
             |
             +--> Windows, browser, web, media, camera, memory, or service API
             |
             v
Voice response + HUD event + dashboard update
```

### Startup Sequence

1. `main.py` checks network availability and selects online or offline mode.
2. In online mode, it loads the configured modules in `skills/loader.py`,
   initializes memory, and marks the core as ready.
3. It starts the HUD runtime and Python-to-web HUD bridge.
4. It launches the Next.js HUD from `hud/web` on `http://127.0.0.1:3000` and
   opens it in a native `pywebview` desktop window.
5. It starts the remote dashboard server and the online voice engine in the
   background.
6. Commands are routed to registered skills. Closing the native HUD requests a
   complete JARVIS shutdown and stops the HUD server process tree.

### Command Routing

The voice listener sends recognized text to `core.dispatcher`. Fast routers
handle common actionable commands first. Requests that need context, planning,
or conversation are resolved by the brain and planner modules. Individual
skills register named actions with `core.registry`; the planner invokes those
actions with the extracted command data.

Natural wording is supported, so the examples below are representative phrases
rather than a strict command grammar. Some actions require a configured account,
browser session, Windows permission, network connection, or optional dependency.

## Skills and Commands

| Skill module | Registered actions / capability | Example voice commands |
| --- | --- | --- |
| `skills/assistant/greetings.py` | `greet`, `how_are_you`, `welcome`, `goodbye` | "Hello Jarvis", "How are you?", "Goodbye" |
| `skills/ai/clarify.py` | `clarify` | Used when JARVIS needs a missing detail before acting. |
| `skills/automation/home_automation.py` | `home_automation` | "Turn on the [device]", "Turn off the [device]" |
| `skills/browser/browser_ai.py` | `open`, `google_search`, `browser_open_result` | "Open Spotify", "Search Google for Python tutorials" |
| `skills/browser/youtube.py` | `youtube_search`, playback actions | "Search YouTube for lofi music", "Pause YouTube" |
| `skills/browser_control/browser_controls.py` | `refresh`, `back`, `forward`, `new_tab`, `close_tab`, `scroll_down`, `scroll_up` | "Refresh the page", "Go back", "Open a new tab", "Scroll down" |
| `skills/camera/camera.py` | `camera_status`, `capture`, `camera_preview`, `camera_close`, `start_recording`, `stop_recording` | "Open camera", "Take a photo", "Start recording" |
| `skills/camera/vision_skill.py` | camera-vision analysis actions | "What can you see?", "Analyze the camera scene" |
| `skills/communication/whatsapp.py` | WhatsApp open/close, message, file, photo, screenshot, scheduled-message, call, and video-call actions | "Send WhatsApp message to Alex", "Send the latest screenshot on WhatsApp" |
| `skills/communication/email.py` | `send_email`, email-contact actions | "Send an email to Alex", "Show email contacts" |
| `skills/communication/contact.py` | `remember_contact`, `forget_contact`, `show_contacts` | "Remember Alex's number", "Show my contacts" |
| `skills/communication/github.py` | `github_search` | "Search GitHub for FastAPI examples" |
| `skills/communication/chatgpt.py` | `chatgpt_search` | "Search ChatGPT for this topic" |
| `skills/files/files.py` | `open_file`, `open_folder`, `create_file`, `create_folder`, `copy`, `move`, `rename`, `delete` | "Create a folder called Reports", "Open Downloads", "Rename this file" |
| `skills/files/file_info.py`, `recent.py` | `file_info`, `recent_files` | "Show file information", "Show recent files" |
| `skills/files/recycle.py`, `zip_manager.py` | `recycle`, `zip`, `extract` | "Open recycle bin", "Zip this folder", "Extract this archive" |
| `skills/media/media.py` | `play` | "Play some music" |
| `skills/media/spotify.py` | Spotify open/close/play/pause/next/previous/song/volume actions | "Open Spotify", "Play Blinding Lights on Spotify", "Next song" |
| `skills/memory/memory.py` | remember, recall, and forget-memory handling | "Remember that my favorite color is blue", "What is my favorite color?" |
| `skills/memory/notes.py` | `create_note`, `list_notes`, `clear_notes` | "Take a note: call Sam", "List my notes" |
| `skills/memory/reminders.py` | `create_reminder`, `list_reminders`, `cancel_reminder` | "Remind me at 6 PM", "Show my reminders" |
| `skills/navigation/maps.py` | `maps_open`, `maps_directions` | "Open maps", "Get directions to the airport" |
| `skills/navigation/translate.py` | `translate_open`, `translate_text` | "Translate hello to Hindi", "Open Google Translate" |
| `skills/network/weather.py` | `weather` | "What's the weather in Chennai?" |
| `skills/network/wifi.py` | `wifi_on`, `wifi_off`, `wifi_status`, `wifi_list` | "Turn Wi-Fi on", "Show available Wi-Fi networks" |
| `skills/network/bluetooth.py` | `bluetooth_status`, `bluetooth_devices` | "Is Bluetooth on?", "Show Bluetooth devices" |
| `skills/news/news.py` | `get_news` | "Give me the latest news" |
| `skills/screen/screenshot.py` | `screenshot` | "Take a screenshot" |
| `skills/screen/screenshot_ai.py`, `screen_vision_skill.py` | AI screenshot and screen-vision actions | "Analyze my screen", "What is on the screen?" |
| `skills/screen/clipboard.py` | `clipboard` | "Read the clipboard" |
| `skills/system/system.py` | `shutdown`, `restart`, `sleep`, `lock` | "Shut down the PC", "Restart the computer", "Lock the screen" |
| `skills/system/volume.py` | volume control | "Increase volume", "Mute the sound" |
| `skills/system/brightness.py` | brightness control | "Increase brightness", "Set brightness to 50" |
| `skills/system/battery.py` | `battery` | "Show battery status" |
| `skills/system/process.py`, `taskmanager.py` | `running_apps`, `close_process`, task-manager action | "Show running apps", "Close Chrome", "Open Task Manager" |
| `skills/utilities/search.py` | `search_file` | "Find my report file" |
| `skills/utilities/time_skill.py` | `time` | "What time is it?" |
| `skills/web/personal_links.py` | `open_personal_link` | "Open my portfolio" after configuring a personal link. |

### Live Conversation Commands

These commands are handled directly by the dispatcher after startup:

| Command | Action |
| --- | --- |
| `start live conversation`, `start live mode`, `enter live conversation` | Starts live conversation mode. |
| `stop live conversation`, `stop live mode`, `exit live conversation`, `end live conversation` | Stops live conversation mode. |
| `live conversation status`, `live mode status` | Reports live conversation status. |

### Developer Requests

The intent engine recognizes programming-related words such as `create`,
`build`, `make`, `fix`, `edit`, `update`, `refactor`, and `generate` when they
are paired with code terms, technologies, file extensions, or project objects.
Examples include "Create a Python calculator", "Fix this JavaScript file", or
"Build a React website". These requests are routed to the developer branch of
the brain instead of the normal desktop-automation planner.

## Run the Project

### Prerequisites

- Windows 10 or later for the Windows automation features.
- Python 3 and Node.js with npm available in `PATH`.
- A working microphone for voice input.
- Ollama and the configured local model for offline mode. The default setting is
  `qwen2.5:3b` at `http://localhost:11434/api/generate`.
- Browser logins and service credentials where a skill requires them, such as
  Spotify, WhatsApp, email, or personal links.

### Installation

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Set-Location hud\web
npm install
Set-Location ..\..
```

`requirements.txt` is currently empty, so it does not yet pin the Python
runtime dependencies. Install the Python packages required by the runtime and
the optional skills you plan to use before starting JARVIS. The HUD dependencies
are declared in `hud/web/package.json` and are installed by `npm install`.

### Start JARVIS

```powershell
python main.py
```

The application starts the Next.js HUD itself, opens the native JARVIS desktop
window, and prints the dashboard URL and pairing PIN to the terminal when the
dashboard server is available. To work on the HUD alone:

```powershell
Set-Location hud\web
npm run dev
```

### Build the HUD

```powershell
Set-Location hud\web
npm run build
npm run start
```

## Configuration

The main application settings live in `config/settings.py`:

| Setting | Default | Purpose |
| --- | --- | --- |
| `APP_NAME` | `JARVIS` | Application display name. |
| `VERSION` | `1.0` | Application version. |
| `VOICE` | `male` | Preferred voice profile. |
| `LANGUAGE` | `en` | Assistant language. |
| `WAKE_WORDS` | `jarvis`, `hey jarvis`, `hello jarvis` | Words that activate the assistant. |
| `AI_PROVIDER` | `ollama` | Selected AI provider. |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Default local Ollama model. |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Local Ollama generation endpoint. |

Other configuration modules in `config/` contain browser, Spotify, WhatsApp,
YouTube, HUD, personal-link, and project-path settings.

## Project Structure

```text
JARVIS-PRO/
├── main.py                 # Application entry point and lifecycle management
├── requirements.txt        # Python dependency manifest (currently unpinned)
├── ai/                     # AI provider, memory, intent, and profile modules
├── brain/                  # Intent engine, planning, reasoning, and follow-ups
├── config/                 # App, service, path, browser, and HUD settings
├── core/                   # Dispatcher, registry, queues, workers, routers, state
├── dashboard/              # Remote dashboard server and static web pages
│   └── static/             # Login and dashboard client assets
├── data/                   # Runtime-created data: captures, notes, memories, logs
├── hud/                    # Python HUD bridge, events, native desktop window
│   └── web/                # Next.js/React/Three.js HUD application
│       ├── app/            # Next.js pages, layout, and global styles
│       ├── components/     # HUD and orb React components
│       ├── lib/            # Three.js scenes, avatars, bridge, hand tracking
│       ├── public/models/  # GLB 3D assets
│       └── package.json    # HUD scripts and Node dependencies
├── services/               # External-service and Windows integration adapters
├── skills/                 # Feature modules registered as executable actions
│   ├── assistant/          # Greetings and assistant responses
│   ├── automation/         # Home automation
│   ├── browser/            # Browser, Google, and YouTube actions
│   ├── browser_control/    # In-browser navigation controls
│   ├── camera/             # Camera capture, recording, and vision
│   ├── communication/      # WhatsApp, email, contacts, GitHub, ChatGPT
│   ├── files/              # File, folder, archive, recent-file, recycle actions
│   ├── media/              # General media and Spotify controls
│   ├── memory/             # Memory, notes, and reminders
│   ├── navigation/         # Maps and translation
│   ├── network/            # Weather, Wi-Fi, and Bluetooth
│   ├── news/               # News retrieval
│   ├── screen/             # Screenshots, clipboard, and screen vision
│   ├── system/             # Windows power, display, process, and audio controls
│   ├── utilities/          # Time and file search
│   ├── web/                # Personal web links
│   └── loader.py           # Configured skill import list and diagnostics
├── tools/                  # Supporting Windows and database utilities
├── voice/                  # Voice pipelines, TTS, STT, modes, and interruptions
│   └── offline/            # Isolated offline STT, AI, TTS, and voice loop
├── logs/                   # Runtime logs, including the HUD web-server log
└── workspace/              # Workspace/runtime support files
```

## Key Architecture Files

| File | Responsibility |
| --- | --- |
| `main.py` | Owns startup, mode selection, HUD process lifecycle, dashboard startup, voice startup, and shutdown. |
| `skills/loader.py` | Imports the configured skill modules and reports loaded or failed modules without stopping all startup on an optional-skill failure. |
| `core/dispatcher.py` | Central command entry point for voice and remote-dashboard input. |
| `core/fast_router.py` | Sends common commands to specialized direct routers before full planning. |
| `core/registry.py` | Stores actions registered by skills and executes the selected action. |
| `brain/intent_engine.py` | Classifies requests as planner, chat, or developer intent. |
| `voice/mode.py` | Selects online or offline mode using a network check. |
| `voice/offline/offline_runner.py` | Runs the isolated offline conversation loop. |
| `hud/web/` | Provides the visual HUD rendered by the native desktop window. |
| `dashboard/server.py` | Hosts the paired remote-control dashboard. |

## Data and Logs

`config/paths.py` creates the `data/` directory and its standard subfolders
when they are needed: `cache`, `captures`, `documents`, `downloads`, `exports`,
`faces`, `logs`, `memories`, `recordings`, `screenshots`, and `temp`.

The Next.js HUD output is written to `logs/hud_web.log` by the main application.
Use these locations when investigating skill failures, voice issues, or HUD
startup problems.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| HUD does not open | Confirm Node.js/npm is installed, run `npm install` in `hud/web`, then inspect `logs/hud_web.log`. |
| JARVIS reports a failed skill | Check the startup output from `skills/loader.py`; optional skill imports are allowed to fail independently. |
| Offline mode does not respond | Start Ollama, ensure the configured model is installed, and verify the Ollama URL in `config/settings.py`. |
| Microphone commands are not recognized | Check microphone permissions and the selected input device, then restart JARVIS so it can calibrate ambient noise. |
| A service command does not work | Verify its account/session/configuration and any required browser, Windows permission, or network connection. |
| Dashboard is unavailable | Check the console output for the generated pairing PIN and whether FastAPI-related dashboard dependencies are installed. |

## Notes for Contributors

- Add a new feature as a module under the appropriate `skills/` category.
- Register each executable action with `core.registry.register`.
- Add the import path to `SKILLS` in `skills/loader.py` so the module registers
  itself during startup.
- Add or update a router when the command needs deterministic parsing before the
  planner runs.
- Keep external integrations in `services/` and application configuration in
  `config/`.
- Preserve the main-thread requirement for `pywebview.start()`; the native HUD
  must be started from the main application thread.
