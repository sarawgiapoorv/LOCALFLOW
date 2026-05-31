# ⚡ LocalFlow

An advanced, privacy-first desktop voice dictation engine built to provide a powerful, open-source replacement for tools like **Flow** and **Whisper**. LocalFlow captures raw microphone streams, executes real-time cloud transcriptions, and passes them through a resilient multi-model LLM pool to strip filler words, fix grammar, and process spoken self-corrections instantly before injecting the text directly at your cursor.

---

## ✨ Core Features

* **Two-Stage Core AI Pipeline:**
    * **Stage 1 (Transcription):** Blazing fast audio-to-text decoding via Groq's `whisper-large-v3` cloud endpoint.
    * **Stage 2 (Polishing):** Context-aware text refinement utilizing deep LLM instructions to eliminate conversational stutter, remove filler phrases (`um`, `uh`, `basically`), and resolve complex verbal backtracking on-the-fly.
* **Resilient Model Failover Pool:** Implements a multi-model fallback safety system. If the default `llama-3.3-70b-versatile` endpoint fails or times out, the application sequentially hot-swaps to `llama-3.1-70b-versatile`, `llama3-70b-8192`, or `mixtral-8x7b-32768` to guarantee zero dictation dropouts.
* **Dual-Mode Recording Controls:**
    * **Hold-to-Record:** Hold down the `Right Alt` key to capture audio, and release it to instantly process and type your text.
    * **Hands-Free Continuous Mode:** Press `Ctrl + Shift + A` to toggle a long-form session. Speak completely hands-free and press the shortcut again to process blocks of narrative dictation.
* **Seamless Cursor Injection:** Automatically pushes finalized, polished prose into whatever text editor, IDE, or browser field you are currently focused on.
* **Persistent SQLite History Vault:** Locally logs every text generation with accurate timestamps into `localflow_history.db` so you never lose an optimized thought.
* **Production-Grade UI/UX:** Built on a sleek, Tailwind-inspired custom dark theme featuring live color-pulsing record animations and minimized close-to-tray system integration via `pystray`.

---

## 🏗️ Architecture & Technical Stack

```text
[Microphone] ──> SoundDevice Stream (16kHz Mono PCM)
                     └──> Stage 1: Groq Whisper API (Raw Text)
                              └──> Stage 2: Resilient LLM Pool (Pristine Text)
                                       ├──> Auto-Inject at Active Cursor
                                       └──> Local SQLite History Logging

GUI Framework: customtkinter (Modernized dark-mode engine).

Audio Pipeline: sounddevice + wavio + numpy (High-performance callback streaming tracking 16-bit PCM).

Global Inputs: keyboard hook engine capturing asynchronous desktop hotkeys flawlessly.

Local Storage: sqlite3 for local transactional application history caching

📂 Repository Layout
main.py: The main entry point that initializes and launches the desktop application GUI.

gui_app.py: Houses the CustomTkinter dark-mode user interface, status animation routines, settings panel management, and background threads.

ai_brain.py: Manages the two-stage cloud translation pipeline and resilience logic across the fallback Groq model configurations.

audio_recorder.py: Handles high-fidelity microphone input capture streaming utilizing hardware-specific audio device indexing.

history_vault.py: Establishes connections to the local SQLite storage engine to manage chronological transcript histories.

Launch_LocalFlow.bat: A silent launcher script that auto-elevates privileges to run the application headless using Windows pythonw.

requirements.txt: Outlines the clear upstream package dependencies required to set up the execution environment.

⚙️ Installation & Usage
Prerequisites
Python 3.10 or higher installed.

An active Groq API Key (Secure one at the Groq Console).

Setup Steps
Clone the repository to your local computer path:
git clone [https://github.com/sarawgiapoorv/LocalFlow.git](https://github.com/sarawgiapoorv/LocalFlow.git)
cd LocalFlow
Install the necessary system dependencies:
pip install -r requirements.txt
Run the Application:
To launch via a standard interactive terminal:
python main.py
To run silently in the background with no terminal window active:
Launch_LocalFlow.bat
Configure your credentials:
Expand the UI Settings panel, supply your preferred microphone input device index, input your Groq API Key (gsk_...), and press Apply Settings.

⌨️ Shortcuts Reference Guide
1) Hold Right Alt  ---->>Active Dictation---->>Turns status bar indicator red and runs active microphone capture stream.
2)Release Right Alt	---->>Stop & Transmit---->>Halts capture stream, packs the audio payload, triggers the AI pipeline, and types at the active cursor.
3)Ctrl + Shift + A---->>Continuous Toggle---->>Switches the application engine into an active, hands-free continuous dictation loop.

🔒 Security & Privacy Commitments
Your private API access credentials are saved locally onto your physical storage drive inside an automated local config.txt file.

The bundled .gitignore file is explicitly pre-configured to ensure your private configuration keys (config.txt) and transactional database caches (*.db) are never committed or exposed upstream to public version control.

🧑‍💻 Developer
Developed with ⚡ by Apoorv Sarawgi

Role: Aspiring AI/ML Engineer & Generative AI Developer

LinkedIn: apoorv-sarawgi

Medium Articles: Read Tech Articles


